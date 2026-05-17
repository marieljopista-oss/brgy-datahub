from datetime import date
import csv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import (
    BarangayProfile,
    Building,
    Facility,
    Household,
    Institution,
    LandBody,
    MedicalStaff,
    Professional,
    Resident,
    RoadNetwork,
    User,
    Utility,
    WaterBody,
)


def _age_group(birth_date):
    today = date.today()
    months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    years = (today - birth_date).days // 365

    if months < 7:
        return "0 - 6 months"
    if months < 36:
        return "7 months - 2 years old"
    if years < 6:
        return "3 - 5 years old"
    if years < 13:
        return "6 - 12 years old"
    if years < 18:
        return "13 - 17 years old"
    if years < 60:
        return "18 - 59 years old"
    return "60 years old and above"


AGE_GROUP_ORDER = [
    "0 - 6 months",
    "7 months - 2 years old",
    "3 - 5 years old",
    "6 - 12 years old",
    "13 - 17 years old",
    "18 - 59 years old",
    "60 years old and above",
]


def _redirect_with_tab(route_name, tab_name):
    return redirect(f"{reverse(route_name)}?tab={tab_name}")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login_view.html", {})


def signup_view(request):
    if request.method == "POST":
        first = request.POST.get("first_name", "").strip()
        last = request.POST.get("last_name", "").strip()
        role = request.POST.get("role", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        contact = request.POST.get("contact", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if not all([first, last, role, username, email, password, confirm]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, "accounts/login_view.html", {"show_signup": True})
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/login_view.html", {"show_signup": True})
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "accounts/login_view.html", {"show_signup": True})
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "accounts/login_view.html", {"show_signup": True})

        User.objects.create_user(
            username=username,
            password=password,
            first_name=first,
            last_name=last,
            email=email,
            role=role,
            contact=contact,
        )
        messages.success(request, "Account created! You can now log in.")
        return redirect("login")

    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def home(request):
    return render(request, "accounts/home.html")


@login_required
def dashboard(request):
    residents = Resident.objects.select_related("household").all()
    households = Household.objects.all()
    buildings = Building.objects.all()
    facilities_qs = Facility.objects.all()
    roads = RoadNetwork.objects.all()
    institutions_qs = Institution.objects.all()
    medical_staff = MedicalStaff.objects.all()
    professionals = Professional.objects.all()
    utility = Utility.objects.first()
    total = residents.count()

    age_groups = []
    age_dis = {g: {"without": 0, "with_disability": 0} for g in AGE_GROUP_ORDER}
    for resident in residents:
        group = _age_group(resident.birth_date)
        if resident.has_disability:
            age_dis[group]["with_disability"] += 1
        else:
            age_dis[group]["without"] += 1
    for group in AGE_GROUP_ORDER:
        without_disability = age_dis[group]["without"]
        with_disability = age_dis[group]["with_disability"]
        age_groups.append(
            {
                "label": group,
                "without": without_disability,
                "with_disability": with_disability,
                "total": without_disability + with_disability,
            }
        )

    livelihood_data = (
        residents.exclude(livelihood="")
        .values("livelihood")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    lgbtq_data = (
        residents.exclude(lgbtq_type="")
        .values("lgbtq_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    material_data = (
        households.exclude(house_material="")
        .values("house_material")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    stats = {
        "total_population": total,
        "male": residents.filter(gender="Male").count(),
        "female": residents.filter(gender="Female").count(),
        "total_households": households.count(),
        "owned": households.filter(ownership="Owned").count(),
        "rented": households.filter(ownership="Rented").count(),
        "livelihood_types": residents.exclude(livelihood="").values("livelihood").distinct().count(),
        "infrastructure": buildings.count() + facilities_qs.count() + roads.count(),
        "buildings": buildings.count(),
        "facilities": facilities_qs.count(),
        "roads": roads.count(),
        "institutions": institutions_qs.count(),
        "medical_staff": medical_staff.count(),
        "professionals": professionals.count(),
        "with_disability": residents.filter(has_disability=True).count(),
        "without_disability": residents.filter(has_disability=False).count(),
        "labor_force": residents.filter(in_labor_force=True).count(),
        "unemployed": residents.filter(is_unemployed=True).count(),
        "ofw": residents.filter(is_ofw=True).count(),
        "solo_parents": residents.filter(is_solo_parent=True).count(),
        "indigenous": residents.filter(is_indigenous=True).count(),
        "filipino": residents.filter(citizenship="Filipino").count(),
        "foreigner": residents.filter(citizenship="Foreigner").count(),
        "married": residents.filter(civil_status="Married").count(),
        "single": residents.filter(civil_status="Single").count(),
        "widowed": residents.filter(civil_status="Widowed").count(),
        "separated": residents.filter(civil_status="Separated").count(),
        "osc": sum(1 for resident in residents if not resident.in_labor_force and 6 <= resident.age <= 14),
        "osy": sum(1 for resident in residents if resident.is_unemployed and 15 <= resident.age <= 24),
    }

    sectors = [
        ("Labor Force", stats["labor_force"]),
        ("Unemployed", stats["unemployed"]),
        ("Out of School Children (OSC) 6-14 yrs", stats["osc"]),
        ("Out of School Youth (OSY) 15-24 yrs", stats["osy"]),
        ("Persons with Disabilities (PWDs)", stats["with_disability"]),
        ("Overseas Filipino Workers (OFWs)", stats["ofw"]),
        ("Solo Parents", stats["solo_parents"]),
        ("Indigenous Peoples (IPs)", stats["indigenous"]),
        ("LGBTQ+ Members", residents.exclude(lgbtq_type="").count()),
    ]

    vulnerable = {
        "pwds": stats["with_disability"],
        "children": sum(
            item["total"]
            for item in age_groups
            if item["label"] in ["0 - 6 months", "7 months - 2 years old", "3 - 5 years old", "6 - 12 years old"]
        ),
        "seniors": next((item["total"] for item in age_groups if item["label"] == "60 years old and above"), 0),
    }

    infrastructure_updates = (
        [{"name": item.name, "category": "Building", "detail": item.building_type} for item in buildings.order_by("-id")[:5]]
        + [{"name": item.name, "category": "Facility", "detail": f"{item.facility_type} | Qty {item.quantity}"} for item in facilities_qs.order_by("-id")[:5]]
        + [{"name": f"{item.road_type} Road", "category": "Road", "detail": f"{item.length_km} km | {item.status}"} for item in roads.order_by("-id")[:5]]
    )[:8]

    institution_updates = (
        [{"name": item.name, "role": "Institution", "detail": f"{item.members} members | {item.status}"} for item in institutions_qs.order_by("-id")[:5]]
        + [{"name": item.full_name, "role": "Medical Staff", "detail": item.position} for item in medical_staff.order_by("-id")[:5]]
        + [{"name": item.full_name, "role": "Professional", "detail": item.profession} for item in professionals.order_by("-id")[:5]]
    )[:8]

    return render(
        request,
        "accounts/dashboard.html",
        {
            "stats": stats,
            "age_groups": age_groups,
            "livelihood_data": livelihood_data,
            "lgbtq_data": lgbtq_data,
            "material_data": material_data,
            "sectors": sectors,
            "vulnerable": vulnerable,
            "utility": utility,
            "recent_residents": residents.order_by("-updated_at")[:8],
            "infrastructure_updates": infrastructure_updates,
            "institution_updates": institution_updates,
            "land_bodies": LandBody.objects.order_by("-id")[:5],
            "water_bodies": WaterBody.objects.order_by("-id")[:5],
            "recent_buildings": buildings.order_by("-id")[:5],
            "recent_facilities": facilities_qs.order_by("-id")[:5],
            "recent_institutions": institutions_qs.order_by("-id")[:5],
            "recent_medical_staff": medical_staff.order_by("-id")[:5],
            "recent_professionals": professionals.order_by("-id")[:5],
            "barangay": BarangayProfile.objects.first(),
        },
    )


@login_required
def residents(request):
    q = request.GET.get("q", "").strip()
    residents_qs = Resident.objects.select_related("household").order_by("last_name", "first_name")
    if q:
        residents_qs = residents_qs.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(gender__icontains=q)
            | Q(livelihood__icontains=q)
            | Q(civil_status__icontains=q)
            | Q(citizenship__icontains=q)
        )
    households = Household.objects.all()
    return render(
        request,
        "accounts/residents.html",
        {
            "residents": residents_qs,
            "households": households,
        },
    )


@login_required
def resident_add(request):
    if request.method == "POST":
        p = request.POST
        hh_id = p.get("household") or None
        Resident.objects.create(
            first_name=p.get("first_name", ""),
            last_name=p.get("last_name", ""),
            birth_date=p.get("birth_date"),
            gender=p.get("gender", "Male"),
            household_id=hh_id,
            livelihood=p.get("livelihood", ""),
            civil_status=p.get("civil_status", ""),
            citizenship=p.get("citizenship", "Filipino"),
            lgbtq_type=p.get("lgbtq_type", ""),
            has_disability=bool(p.get("has_disability")),
            in_labor_force=bool(p.get("in_labor_force")),
            is_unemployed=bool(p.get("is_unemployed")),
            is_ofw=bool(p.get("is_ofw")),
            is_solo_parent=bool(p.get("is_solo_parent")),
            is_indigenous=bool(p.get("is_indigenous")),
        )
        messages.success(request, "Resident added.")
    return redirect("residents")


@login_required
def resident_edit(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == "POST":
        p = request.POST
        resident.first_name = p.get("first_name", "")
        resident.last_name = p.get("last_name", "")
        resident.birth_date = p.get("birth_date")
        resident.gender = p.get("gender", "Male")
        resident.household_id = p.get("household") or None
        resident.livelihood = p.get("livelihood", "")
        resident.civil_status = p.get("civil_status", "")
        resident.citizenship = p.get("citizenship", "Filipino")
        resident.lgbtq_type = p.get("lgbtq_type", "")
        resident.has_disability = bool(p.get("has_disability"))
        resident.in_labor_force = bool(p.get("in_labor_force"))
        resident.is_unemployed = bool(p.get("is_unemployed"))
        resident.is_ofw = bool(p.get("is_ofw"))
        resident.is_solo_parent = bool(p.get("is_solo_parent"))
        resident.is_indigenous = bool(p.get("is_indigenous"))
        resident.save()
        messages.success(request, "Resident updated.")
    return redirect("residents")


@login_required
def resident_delete(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == "POST":
        resident.delete()
        messages.success(request, "Resident deleted.")
    return redirect("residents")


@login_required
def resident_import(request):
    messages.info(request, "Resident import is not implemented yet.")
    return redirect("residents")


@login_required
def facilities(request):
    land_bodies = LandBody.objects.all()
    water_bodies = WaterBody.objects.all()
    buildings = Building.objects.all()
    facilities_qs = Facility.objects.all()
    roads = RoadNetwork.objects.all()
    return render(
        request,
        "accounts/facilities.html",
        {
            "land_bodies": land_bodies,
            "water_bodies": water_bodies,
            "utility": Utility.objects.first(),
            "buildings": buildings,
            "facilities": facilities_qs,
            "roads": roads,
            "land_water_total": land_bodies.count() + water_bodies.count(),
        },
    )


@login_required
def facility_add(request, ftype):
    if request.method == "POST":
        if ftype == "land":
            LandBody.objects.create(
                name=request.POST["name"],
                land_type=request.POST["land_type"],
                area_ha=request.POST.get("area_ha") or None,
            )
        elif ftype == "water":
            WaterBody.objects.create(
                name=request.POST["name"],
                water_type=request.POST["water_type"],
                description=request.POST.get("description", ""),
            )
        elif ftype == "building":
            Building.objects.create(
                name=request.POST["name"],
                building_type=request.POST["building_type"],
                status=request.POST.get("status", "Operational"),
            )
        elif ftype == "facility":
            Facility.objects.create(
                name=request.POST["name"],
                facility_type=request.POST["facility_type"],
                quantity=request.POST.get("quantity", 1),
            )
        elif ftype == "road":
            RoadNetwork.objects.create(
                road_type=request.POST["road_type"],
                length_km=request.POST["length_km"],
                status=request.POST.get("status", "Good"),
            )
        elif ftype == "utility":
            utility, _ = Utility.objects.get_or_create(pk=1)
            utility.electricity = request.POST.get("electricity", "Available")
            utility.water_supply = request.POST.get("water_supply", "Available")
            utility.waste_management = request.POST.get("waste_management", "Available")
            utility.toilet_count = request.POST.get("toilet_count", 0)
            utility.bath_count = request.POST.get("bath_count", 0)
            utility.save()
        messages.success(request, "Facility data saved.")

    tab_map = {
        "land": "landwater",
        "water": "landwater",
        "utility": "utilities",
        "building": "buildings",
        "facility": "facilities",
        "road": "roads",
    }
    return _redirect_with_tab("facilities", tab_map.get(ftype, "landwater"))


@login_required
def facility_delete(request, ftype, pk):
    model_map = {
        "land": LandBody,
        "water": WaterBody,
        "building": Building,
        "facility": Facility,
        "road": RoadNetwork,
    }
    model = model_map.get(ftype)
    if model and request.method == "POST":
        get_object_or_404(model, pk=pk).delete()
        messages.success(request, "Record deleted.")

    tab_map = {
        "land": "landwater",
        "water": "landwater",
        "building": "buildings",
        "facility": "facilities",
        "road": "roads",
    }
    return _redirect_with_tab("facilities", tab_map.get(ftype, "landwater"))


@login_required
def institutions(request):
    institutions_qs = Institution.objects.all()
    medical_staff = MedicalStaff.objects.all()
    professionals = Professional.objects.all()
    return render(
        request,
        "accounts/institutions.html",
        {
            "institutions": institutions_qs,
            "medical_staff": medical_staff,
            "professionals": professionals,
            "tracked_people_total": institutions_qs.count() + medical_staff.count() + professionals.count(),
        },
    )


@login_required
def institution_add(request, itype):
    if request.method == "POST":
        if itype == "institution":
            Institution.objects.create(
                name=request.POST["name"],
                president=request.POST.get("president", ""),
                members=request.POST.get("members", 0),
                status=request.POST.get("status", "Active"),
                programs=request.POST.get("programs", ""),
            )
        elif itype == "medical":
            MedicalStaff.objects.create(
                full_name=request.POST["full_name"],
                position=request.POST["position"],
                contact=request.POST.get("contact", ""),
            )
        elif itype == "professional":
            Professional.objects.create(
                full_name=request.POST["full_name"],
                profession=request.POST["profession"],
                contact=request.POST.get("contact", ""),
            )
        messages.success(request, "Institution data saved.")

    tab_map = {
        "institution": "institutions",
        "medical": "medical",
        "professional": "professionals",
    }
    return _redirect_with_tab("institutions", tab_map.get(itype, "institutions"))


@login_required
def institution_delete(request, itype, pk):
    model_map = {
        "institution": Institution,
        "medical": MedicalStaff,
        "professional": Professional,
    }
    model = model_map.get(itype)
    if model and request.method == "POST":
        get_object_or_404(model, pk=pk).delete()
        messages.success(request, "Record deleted.")

    tab_map = {
        "institution": "institutions",
        "medical": "medical",
        "professional": "professionals",
    }
    return _redirect_with_tab("institutions", tab_map.get(itype, "institutions"))


@login_required
def reports(request):
    return redirect(f"{reverse('dashboard')}#analytics")


@login_required
def export_csv(request, dtype):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{dtype}.csv"'
    writer = csv.writer(response)

    if dtype == "residents":
        writer.writerow(["Name", "Birth Date", "Age", "Gender", "Household", "Livelihood", "Disability", "Civil Status", "Citizenship"])
        for resident in Resident.objects.select_related("household").all():
            writer.writerow(
                [
                    resident.full_name,
                    resident.birth_date,
                    resident.age,
                    resident.gender,
                    resident.household.household_id if resident.household else "",
                    resident.livelihood,
                    resident.has_disability,
                    resident.civil_status,
                    resident.citizenship,
                ]
            )
    elif dtype == "facilities":
        writer.writerow(["Type", "Name", "Details", "Status"])
        for building in Building.objects.all():
            writer.writerow(["Building", building.name, building.building_type, building.status])
        for facility in Facility.objects.all():
            writer.writerow(["Facility", facility.name, facility.facility_type, facility.quantity])
        for road in RoadNetwork.objects.all():
            writer.writerow(["Road", road.road_type, f"{road.length_km} km", road.status])
    elif dtype == "institutions":
        writer.writerow(["Type", "Name", "Members or Role", "Status"])
        for institution in Institution.objects.all():
            writer.writerow(["Institution", institution.name, institution.members, institution.status])
        for staff in MedicalStaff.objects.all():
            writer.writerow(["Medical", staff.full_name, staff.position, ""])
        for professional in Professional.objects.all():
            writer.writerow(["Professional", professional.full_name, professional.profession, ""])

    return response


@login_required
def settings(request):
    barangay = BarangayProfile.objects.first()
    users = User.objects.all().order_by("username")
    return render(request, "accounts/settings.html", {"barangay": barangay, "users": users})


@login_required
def settings_save_profile(request):
    if request.method == "POST":
        barangay, _ = BarangayProfile.objects.get_or_create(pk=1)
        barangay.vision = request.POST.get("vision", "")
        barangay.mission = request.POST.get("mission", "")
        barangay.goals = request.POST.get("goals", "")
        barangay.save()
        messages.success(request, "Barangay profile saved.")
    return redirect("settings")


@login_required
def settings_save_barangay(request):
    if request.method == "POST":
        barangay, _ = BarangayProfile.objects.get_or_create(pk=1)
        barangay.name = request.POST.get("name", "")
        barangay.municipality = request.POST.get("municipality", "")
        barangay.province = request.POST.get("province", "")
        barangay.region = request.POST.get("region", "")
        barangay.captain = request.POST.get("captain", "")
        barangay.contact = request.POST.get("contact", "")
        barangay.save()
        messages.success(request, "Barangay information saved.")
    return redirect("settings")


@login_required
def settings_add_user(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "")
        if username and len(password) >= 8:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password, role=role)
                messages.success(request, f'User "{username}" added.')
            else:
                messages.error(request, "Username already exists.")
        else:
            messages.error(request, "Invalid username or password too short.")
    return redirect("settings")


@login_required
def settings_delete_user(request, pk):
    if request.method == "POST":
        user = get_object_or_404(User, pk=pk)
        if user != request.user:
            user.delete()
            messages.success(request, "User removed.")
    return redirect("settings")


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})


@login_required
def profile_save(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()
        user.contact = request.POST.get("contact", "").strip()
        user.role = request.POST.get("role", "")

        new_pw = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")
        if new_pw:
            if new_pw == confirm and len(new_pw) >= 6:
                user.set_password(new_pw)
                messages.success(request, "Password updated. Please log in again.")
            else:
                messages.error(request, "Passwords do not match or too short.")
                return redirect("profile")

        if "profile_photo" in request.FILES:
            user.profile_photo = request.FILES["profile_photo"]

        user.save()
        messages.success(request, "Profile saved.")
    return redirect("profile")
