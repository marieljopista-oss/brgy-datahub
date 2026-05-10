from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from datetime import date
import json, csv

from .models import (
    User, BarangayProfile,
    Household, Resident,
    LandBody, WaterBody, Utility, Building, Facility, RoadNetwork,
    Institution, MedicalStaff, Professional,
)


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def _age_group(birth_date):
    """Return the age-group label for a resident."""
    today = date.today()
    months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    years  = (today - birth_date).days // 365

    if months < 7:   return '0 – 6 months'
    if months < 36:  return '7 months – 2 years old'
    if years  < 6:   return '3 – 5 years old'
    if years  < 13:  return '6 – 12 years old'
    if years  < 18:  return '13 – 17 years old'
    if years  < 60:  return '18 – 59 years old'
    return '60 years old and above'


AGE_GROUP_ORDER = [
    '0 – 6 months',
    '7 months – 2 years old',
    '3 – 5 years old',
    '6 – 12 years old',
    '13 – 17 years old',
    '18 – 59 years old',
    '60 years old and above',
]


# ─────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid username or password.')

    return render(request, 'login_view.html', {'show_error': bool(messages.get_messages(request))})


def signup_view(request):
    if request.method == 'POST':
        first    = request.POST.get('first_name', '').strip()
        last     = request.POST.get('last_name',  '').strip()
        role     = request.POST.get('role',       '').strip()
        username = request.POST.get('username',   '').strip()
        email    = request.POST.get('email',      '').strip()
        contact  = request.POST.get('contact',    '').strip()
        password = request.POST.get('password',   '')
        confirm  = request.POST.get('confirm_password', '')

        # Basic validation
        if not all([first, last, role, username, email, password, confirm]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('login')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('login')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('login')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('login')

        User.objects.create_user(
            username=username, password=password,
            first_name=first, last_name=last,
            email=email, role=role, contact=contact,
        )
        messages.success(request, 'Account created! You can now log in.')
        return redirect('login')

    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────

@login_required
def home(request):
    return render(request, 'home.html')


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────

@login_required
def dashboard(request):
    residents = Resident.objects.select_related('household').all()

    total       = residents.count()
    male_count  = residents.filter(gender='Male').count()
    female_count= residents.filter(gender='Female').count()

    households     = Household.objects.all()
    owned_count    = households.filter(ownership='Owned').count()
    rented_count   = households.filter(ownership='Rented').count()

    livelihood_count = residents.exclude(livelihood='').values('livelihood').distinct().count()
    infra_count      = Building.objects.count() + Facility.objects.count()

    # Livelihood distribution
    livelihood_data = (
        residents.exclude(livelihood='')
        .values('livelihood')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # House materials
    material_data = (
        households.exclude(house_material='')
        .values('house_material')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Age groups with disability status
    age_group_data = {g: {'without': 0, 'with': 0} for g in AGE_GROUP_ORDER}
    for r in residents:
        grp = _age_group(r.birth_date)
        key = 'with' if r.has_disability else 'without'
        age_group_data[grp][key] += 1

    age_groups = [
        {
            'label':    g,
            'without':  age_group_data[g]['without'],
            'with':     age_group_data[g]['with'],
            'total':    age_group_data[g]['without'] + age_group_data[g]['with'],
        }
        for g in AGE_GROUP_ORDER
    ]

    # Sector counts
    sectors = {
        'labor_force':  residents.filter(in_labor_force=True).count(),
        'unemployed':   residents.filter(is_unemployed=True).count(),
        'osc':          residents.filter(
                            birth_date__lte=date.today().replace(year=date.today().year - 6),
                            birth_date__gte=date.today().replace(year=date.today().year - 14),
                        ).count(),
        'osy':          residents.filter(
                            birth_date__lte=date.today().replace(year=date.today().year - 15),
                            birth_date__gte=date.today().replace(year=date.today().year - 24),
                        ).count(),
        'pwds':         residents.filter(has_disability=True).count(),
        'ofw':          residents.filter(is_ofw=True).count(),
        'solo_parent':  residents.filter(is_solo_parent=True).count(),
        'indigenous':   residents.filter(is_indigenous=True).count(),
    }

    # Civil status & citizenship
    civil = {s: residents.filter(civil_status=s).count() for s in ['Married','Single','Widowed','Separated']}
    citizenship = {c: residents.filter(citizenship=c).count() for c in ['Filipino','Foreigner']}

    # LGBTQ+
    lgbtq_data = (
        residents.exclude(lgbtq_type='')
        .values('lgbtq_type')
        .annotate(count=Count('id'))
    )

    barangay = BarangayProfile.objects.first()

    context = {
        'barangay':        barangay,
        'stats': {
            'total_population': total,
            'male':             male_count,
            'female':           female_count,
            'households':       households.count(),
            'owned':            owned_count,
            'rented':           rented_count,
            'livelihood_types': livelihood_count,
            'infrastructure':   infra_count,
        },
        'livelihood_data': livelihood_data,
        'material_data':   material_data,
        'age_groups':      age_groups,
        'total_no_dis':    sum(g['without'] for g in age_groups),
        'total_with_dis':  sum(g['with']    for g in age_groups),
        'sectors':         sectors,
        'civil':           civil,
        'citizenship':     citizenship,
        'lgbtq_data':      lgbtq_data,
    }
    return render(request, 'dashboard.html', context)


# ─────────────────────────────────────────
#  RESIDENTS
# ─────────────────────────────────────────

@login_required
def residents(request):
    residents  = Resident.objects.select_related('household').order_by('last_name', 'first_name')
    households = Household.objects.all()
    return render(request, 'residents.html', {'residents': residents, 'households': households})


@login_required
def resident_add(request):
    if request.method == 'POST':
        hh_id = request.POST.get('household')
        household = Household.objects.filter(pk=hh_id).first() if hh_id else None

        Resident.objects.create(
            first_name    = request.POST.get('first_name', '').strip(),
            last_name     = request.POST.get('last_name',  '').strip(),
            birth_date    = request.POST.get('birth_date'),
            gender        = request.POST.get('gender', 'Male'),
            household     = household,
            livelihood    = request.POST.get('livelihood',  ''),
            civil_status  = request.POST.get('civil_status',''),
            citizenship   = request.POST.get('citizenship', 'Filipino'),
            lgbtq_type    = request.POST.get('lgbtq_type',  ''),
            has_disability= request.POST.get('has_disability') == 'on',
            in_labor_force= request.POST.get('in_labor_force') == 'on',
            is_unemployed = request.POST.get('is_unemployed')  == 'on',
            is_ofw        = request.POST.get('is_ofw')         == 'on',
            is_solo_parent= request.POST.get('is_solo_parent') == 'on',
            is_indigenous = request.POST.get('is_indigenous')  == 'on',
        )
        messages.success(request, 'Resident added successfully.')
    return redirect('residents')


@login_required
def resident_edit(request, pk):
    r = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        hh_id = request.POST.get('household')
        r.first_name     = request.POST.get('first_name', '').strip()
        r.last_name      = request.POST.get('last_name',  '').strip()
        r.birth_date     = request.POST.get('birth_date')
        r.gender         = request.POST.get('gender', 'Male')
        r.household      = Household.objects.filter(pk=hh_id).first() if hh_id else None
        r.livelihood     = request.POST.get('livelihood',  '')
        r.civil_status   = request.POST.get('civil_status','')
        r.citizenship    = request.POST.get('citizenship', 'Filipino')
        r.lgbtq_type     = request.POST.get('lgbtq_type',  '')
        r.has_disability = request.POST.get('has_disability') == 'on'
        r.in_labor_force = request.POST.get('in_labor_force') == 'on'
        r.is_unemployed  = request.POST.get('is_unemployed')  == 'on'
        r.is_ofw         = request.POST.get('is_ofw')         == 'on'
        r.is_solo_parent = request.POST.get('is_solo_parent') == 'on'
        r.is_indigenous  = request.POST.get('is_indigenous')  == 'on'
        r.save()
        messages.success(request, f'{r.full_name} updated.')
    return redirect('residents')


@login_required
def resident_delete(request, pk):
    r = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        r.delete()
        messages.success(request, 'Resident deleted.')
    return redirect('residents')


# ─────────────────────────────────────────
#  FACILITIES
# ─────────────────────────────────────────

@login_required
def facilities(request):
    context = {
        'land_bodies':  LandBody.objects.all(),
        'water_bodies': WaterBody.objects.all(),
        'utility':      Utility.objects.first(),
        'buildings':    Building.objects.all(),
        'facilities':   Facility.objects.all(),
        'roads':        RoadNetwork.objects.all(),
    }
    return render(request, 'facilities.html', context)


@login_required
def facility_add(request, ftype):
    """Generic add for land/water/building/facility/road."""
    if request.method == 'POST':
        if ftype == 'land':
            LandBody.objects.create(
                name=request.POST['name'],
                land_type=request.POST['land_type'],
                area_ha=request.POST.get('area_ha') or None,
            )
        elif ftype == 'water':
            WaterBody.objects.create(
                name=request.POST['name'],
                water_type=request.POST['water_type'],
                description=request.POST.get('description',''),
            )
        elif ftype == 'building':
            Building.objects.create(
                name=request.POST['name'],
                building_type=request.POST['building_type'],
                status=request.POST.get('status','Operational'),
            )
        elif ftype == 'facility':
            Facility.objects.create(
                name=request.POST['name'],
                facility_type=request.POST['facility_type'],
                quantity=request.POST.get('quantity', 1),
            )
        elif ftype == 'road':
            RoadNetwork.objects.create(
                road_type=request.POST['road_type'],
                length_km=request.POST['length_km'],
                status=request.POST.get('status','Good'),
            )
        elif ftype == 'utility':
            util, _ = Utility.objects.get_or_create(pk=1)
            util.electricity      = request.POST.get('electricity',      'Available')
            util.water_supply     = request.POST.get('water_supply',     'Available')
            util.waste_management = request.POST.get('waste_management', 'Available')
            util.toilet_count     = request.POST.get('toilet_count', 0)
            util.bath_count       = request.POST.get('bath_count',   0)
            util.save()
        messages.success(request, 'Record saved.')
    return redirect('facilities')


@login_required
def facility_delete(request, ftype, pk):
    model_map = {
        'land':     LandBody,
        'water':    WaterBody,
        'building': Building,
        'facility': Facility,
        'road':     RoadNetwork,
    }
    model = model_map.get(ftype)
    if model and request.method == 'POST':
        get_object_or_404(model, pk=pk).delete()
        messages.success(request, 'Record deleted.')
    return redirect('facilities')


# ─────────────────────────────────────────
#  INSTITUTIONS
# ─────────────────────────────────────────

@login_required
def institutions(request):
    context = {
        'institutions': Institution.objects.all(),
        'medical_staff': MedicalStaff.objects.all(),
        'professionals': Professional.objects.all(),
    }
    return render(request, 'institutions.html', context)


@login_required
def institution_add(request, itype):
    if request.method == 'POST':
        if itype == 'institution':
            Institution.objects.create(
                name     = request.POST['name'],
                president= request.POST.get('president',''),
                members  = request.POST.get('members', 0),
                status   = request.POST.get('status','Active'),
                programs = request.POST.get('programs',''),
            )
        elif itype == 'medical':
            MedicalStaff.objects.create(
                full_name= request.POST['full_name'],
                position = request.POST['position'],
                contact  = request.POST.get('contact',''),
            )
        elif itype == 'professional':
            Professional.objects.create(
                full_name = request.POST['full_name'],
                profession= request.POST['profession'],
                contact   = request.POST.get('contact',''),
            )
        messages.success(request, 'Record added.')
    return redirect('institutions')


@login_required
def institution_delete(request, itype, pk):
    model_map = {
        'institution': Institution,
        'medical':     MedicalStaff,
        'professional':Professional,
    }
    model = model_map.get(itype)
    if model and request.method == 'POST':
        get_object_or_404(model, pk=pk).delete()
        messages.success(request, 'Record deleted.')
    return redirect('institutions')


# ─────────────────────────────────────────
#  REPORTS
# ─────────────────────────────────────────

@login_required
def reports(request):
    residents  = Resident.objects.select_related('household').all()
    households = Household.objects.all()
    total      = residents.count()

    # Age group counts for chart
    age_counts = {g: 0 for g in AGE_GROUP_ORDER}
    for r in residents:
        age_counts[_age_group(r.birth_date)] += 1

    # Disability by gender
    dis_male   = residents.filter(has_disability=True, gender='Male').count()
    dis_female = residents.filter(has_disability=True, gender='Female').count()

    # Sector summary
    sectors = {
        'Labor Force':    residents.filter(in_labor_force=True).count(),
        'Unemployed':     residents.filter(is_unemployed=True).count(),
        'OSC (6–14)':     residents.filter(in_labor_force=False).count(),  # simplified
        'OSY (15–24)':    residents.filter(is_unemployed=True).count(),    # simplified
        'PWDs':           residents.filter(has_disability=True).count(),
        'OFWs':           residents.filter(is_ofw=True).count(),
        'Solo Parents':   residents.filter(is_solo_parent=True).count(),
        'Indigenous (IPs)': residents.filter(is_indigenous=True).count(),
        'LGBTQ+':         residents.exclude(lgbtq_type='').count(),
    }

    context = {
        'stats': {
            'total_population': total,
            'total_with_dis':   residents.filter(has_disability=True).count(),
            'total_households': households.count(),
            'avg_hh_members':   round(total / households.count(), 1) if households.count() else 0,
            'infrastructure':   Building.objects.count() + Facility.objects.count(),
        },
        'age_labels':  list(age_counts.keys()),
        'age_values':  list(age_counts.values()),
        'gender_data': {
            'male':   residents.filter(gender='Male').count(),
            'female': residents.filter(gender='Female').count(),
        },
        'dis_male':   dis_male,
        'dis_female': dis_female,
        'sectors':    sectors,
        'vulnerable': {
            'pwds':     residents.filter(has_disability=True).count(),
            'children': sum(v for k, v in age_counts.items()
                            if k in ['0 – 6 months','7 months – 2 years old',
                                     '3 – 5 years old','6 – 12 years old']),
            'seniors':  age_counts['60 years old and above'],
        },
    }
    return render(request, 'reports.html', context)


@login_required
def export_csv(request, dtype):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{dtype}.csv"'
    writer = csv.writer(response)

    if dtype == 'residents':
        writer.writerow(['Name','Birth Date','Age','Gender','Household',
                         'Livelihood','Disability','Civil Status','Citizenship'])
        for r in Resident.objects.select_related('household').all():
            writer.writerow([r.full_name, r.birth_date, r.age, r.gender,
                             r.household.household_id if r.household else '',
                             r.livelihood, r.has_disability, r.civil_status, r.citizenship])
    elif dtype == 'facilities':
        writer.writerow(['Type','Name','Details','Status'])
        for b in Building.objects.all():
            writer.writerow(['Building', b.name, b.building_type, b.status])
        for f in Facility.objects.all():
            writer.writerow(['Facility', f.name, f.facility_type, f.quantity])
    elif dtype == 'institutions':
        writer.writerow(['Type','Name','Members','Status'])
        for i in Institution.objects.all():
            writer.writerow(['Institution', i.name, i.members, i.status])
        for m in MedicalStaff.objects.all():
            writer.writerow(['Medical', m.full_name, m.position, ''])
        for p in Professional.objects.all():
            writer.writerow(['Professional', p.full_name, p.profession, ''])

    return response


# ─────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────

@login_required
def settings(request):
    barangay = BarangayProfile.objects.first()
    users    = User.objects.all().order_by('username')
    return render(request, 'settings.html', {'barangay': barangay, 'users': users})


@login_required
def settings_save_profile(request):
    if request.method == 'POST':
        b, _ = BarangayProfile.objects.get_or_create(pk=1)
        b.vision   = request.POST.get('vision',  '')
        b.mission  = request.POST.get('mission', '')
        b.goals    = request.POST.get('goals',   '')
        b.save()
        messages.success(request, 'Barangay profile saved.')
    return redirect('settings')


@login_required
def settings_save_barangay(request):
    if request.method == 'POST':
        b, _ = BarangayProfile.objects.get_or_create(pk=1)
        b.name         = request.POST.get('name',         '')
        b.municipality = request.POST.get('municipality', '')
        b.province     = request.POST.get('province',     '')
        b.region       = request.POST.get('region',       '')
        b.captain      = request.POST.get('captain',      '')
        b.contact      = request.POST.get('contact',      '')
        b.save()
        messages.success(request, 'Barangay information saved.')
    return redirect('settings')


@login_required
def settings_add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        role     = request.POST.get('role','')
        if username and len(password) >= 8:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password, role=role)
                messages.success(request, f'User "{username}" added.')
            else:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Invalid username or password too short.')
    return redirect('settings')


@login_required
def settings_delete_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user != request.user:
            user.delete()
            messages.success(request, 'User removed.')
    return redirect('settings')


# ─────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def profile_save(request):
    if request.method == 'POST':
        u = request.user
        u.first_name = request.POST.get('first_name', '').strip()
        u.last_name  = request.POST.get('last_name',  '').strip()
        u.email      = request.POST.get('email',      '').strip()
        u.contact    = request.POST.get('contact',    '').strip()
        u.role       = request.POST.get('role',       '')

        new_pw  = request.POST.get('new_password',     '')
        confirm = request.POST.get('confirm_password', '')
        if new_pw:
            if new_pw == confirm and len(new_pw) >= 6:
                u.set_password(new_pw)
                messages.success(request, 'Password updated. Please log in again.')
            else:
                messages.error(request, 'Passwords do not match or too short.')
                return redirect('profile')

        if 'profile_photo' in request.FILES:
            u.profile_photo = request.FILES['profile_photo']

        u.save()
        messages.success(request, 'Profile saved.')
    return redirect('profile')