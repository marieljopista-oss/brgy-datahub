from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Settings, User, Household, Resident, Facility, Institution, MedicalStaff, OtherProfessional
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_user(request):
    uid = request.session.get('user_id')
    if uid:
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            pass
    return None

def get_Settings():
    s = Settings.objects.first()
    if not s:
        s = Settings.objects.create(
            barangay_name='Cogon',
            vision='A progressive and resilient Barangay Cogon with empowered communities.',
            mission='To provide excellent public service and promote sustainable development for all residents.',
            goals='Improve infrastructure, enhance health services, promote education, and ensure disaster preparedness.',
        )
    return s

@login_required(login_url='login') # Add the login_url here
def home(request):
    settings = get_Settings()
    return render(request, 'accounts/settings.html', {'settings': settings})

# ============================================================
# LOGIN
# ============================================================

def login(request):
   from django.contrib.auth import authenticate, login as auth_login

def login(request):
    # If the user is already logged in, send them to home
    if request.user.is_authenticated:
        return redirect('home')
    
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            error = 'Invalid username or password.'
    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ============================================================
# MENU  (f3)
# ============================================================

@login_required
def home(request):
    user     = get_user(request)
    settings = get_Settings()
    return render(request, 'accounts/home.html', {'user': user, 'settings': settings})

@login_required
def profile(request):
    user = get_user(request)
    settings = get_Settings()
    return render(request, 'accounts/profile.html', {
        'user': user, 
        'settings': settings
    })
# ============================================================
# DASHBOARD  (f4)
# ============================================================

@login_required
def dashboard(request):
    user      = get_user(request)
    settings  = get_Settings()
    residents = Resident.objects.all()
    households = Household.objects.all()

    total_pop    = residents.count()
    total_male   = residents.filter(gender='Male').count()
    total_female = residents.filter(gender='Female').count()
    total_hh     = households.count()
    owned_hh     = households.filter(ownership_status='Owned').count()
    rented_hh    = households.filter(ownership_status='Rented').count()

    # Livelihood distribution
    livelihoods = {}
    for r in residents:
        l = r.livelihood.strip() if r.livelihood else 'None'
        livelihoods[l] = livelihoods.get(l, 0) + 1
    livelihoods_sorted = sorted(livelihoods.items(), key=lambda x: -x[1])

    # House materials
    house_materials = {}
    for h in households:
        m = h.house_material
        house_materials[m] = house_materials.get(m, 0) + 1

    # Infrastructure count
    infra_count = (
        Facility.objects.filter(category='Building').count() +
        Facility.objects.filter(category='Facility').count()
    )
    livelihood_types = len(livelihoods)

    # Age groups with disability
    age_groups = [
        ('0-6 months',          residents.filter(age=0)),
        ('7 months - 2 years',  residents.filter(age__gte=0, age__lte=2).exclude(age=0)),
        ('3-5 years old',       residents.filter(age__gte=3, age__lte=5)),
        ('6-12 years old',      residents.filter(age__gte=6, age__lte=12)),
        ('13-17 years old',     residents.filter(age__gte=13, age__lte=17)),
        ('18-59 years old',     residents.filter(age__gte=18, age__lte=59)),
        ('60 years and above',  residents.filter(age__gte=60)),
    ]
    age_group_data = []
    for label, qs in age_groups:
        total   = qs.count()
        with_d  = qs.filter(disability=True).count()
        without = total - with_d
        age_group_data.append((label, total, with_d, without))

    # LGBTQ
    lgbtq_total = residents.exclude(lgbtq_type='').count()
    lgbtq_gay   = residents.filter(lgbtq_type__iexact='Gay').count()
    lgbtq_les   = residents.filter(lgbtq_type__iexact='Lesbian').count()

    # Population by sector
    sectors = [
        ('Labor Force',             residents.filter(is_labor_force= True).count()),
        ('Unemployed',              residents.filter(is_unemployed= True).count()),
        ('Out of School Children',  residents.filter(is_osc= True).count()),
        ('Out of School Youth',     residents.filter(is_osy= True).count()),
        ('Persons with Disability', residents.filter(disability= True).count()),
        ('Overseas Filipino Workers', residents.filter(is_ofw= True).count()),
        ('Solo Parents',            residents.filter(is_solo_parent= True).count()),
        ('Indigenous People',       residents.filter(is_indigenous= True).count()),
    ]

    # Civil status
    civil_data = [
        ('Married',   residents.filter(civil_status='Married').count()),
        ('Single',    residents.filter(civil_status='Single').count()),
        ('Widowed',   residents.filter(civil_status='Widowed').count()),
        ('Separated', residents.filter(civil_status='Separated').count()),
    ]

    # Citizenship
    citizenship_data = [
        ('Filipino', residents.filter(citizenship='Filipino').count()),
        ('Foreign',  residents.filter(citizenship='Foreign').count()),
    ]

    context = {
        'user':              user,
        'settings':          settings,
        'total_pop':         total_pop,
        'total_male':        total_male,
        'total_female':      total_female,
        'total_hh':          total_hh,
        'owned_hh':          owned_hh,
        'rented_hh':         rented_hh,
        'livelihood_types':  livelihood_types,
        'infra_count':       infra_count,
        'livelihoods':       livelihoods_sorted,
        'house_materials':   house_materials.items(),
        'age_group_data':    age_group_data,
        'lgbtq_total':       lgbtq_total,
        'lgbtq_gay':         lgbtq_gay,
        'lgbtq_les':         lgbtq_les,
        'sectors':           sectors,
        'civil_data':        civil_data,
        'citizenship_data':  citizenship_data,
    }
    return render(request, 'accounts/dashboard.html', context)


# ============================================================
# RESIDENTS  (f5)
# ============================================================

@login_required
def residents(request):
    user       = get_user(request)
    settings   = get_Settings()
    search     = request.GET.get('search', '')
    residents  = Resident.objects.all().order_by('id')
    if search:
        residents = residents.filter(full_name__icontains=search)
    households = Household.objects.all()
    context = {
        'user':       user,
        'settings':   settings,
        'residents':  residents,
        'households': households,
        'search':     search,
        'total':      Resident.objects.count(),
    }
    return render(request, 'accounts/residents.html', context)


@login_required
def resident_add(request):
    if request.method == 'POST':
        settings = get_Settings()
        hh_id    = request.POST.get('household_id', '').strip()
        hh       = Household.objects.filter(household_id=hh_id).first() if hh_id else None
        Resident.objects.create(
            settings         = settings,
            household        = hh,
            full_name        = request.POST.get('full_name', ''),
            birth_date       = request.POST.get('birth_date') or None,
            age              = int(request.POST.get('age', 0)),
            gender           = request.POST.get('gender', 'Male'),
            civil_status     = request.POST.get('civil_status', 'Single'),
            livelihood       = request.POST.get('livelihood', ''),
            disability       = request.POST.get('disability', 'No'),
            lgbtq_type       = request.POST.get('lgbtq_type', ''),
            citizenship      = request.POST.get('citizenship', 'Filipino'),
            sector           = request.POST.get('sector', ''),
            is_osc           = request.POST.get('is_osc', 'No'),
            is_osy           = request.POST.get('is_osy', 'No'),
            is_labor_force   = request.POST.get('is_labor_force', 'No'),
            is_unemployed    = request.POST.get('is_unemployed', 'No'),
            is_ofw           = request.POST.get('is_ofw', 'No'),
            is_solo_parent   = request.POST.get('is_solo_parent', 'No'),
            is_indigenous    = request.POST.get('is_indigenous', 'No'),
        )
    return redirect('residents')


@login_required
def resident_edit(request, pk):
    r = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        hh_id = request.POST.get('household_id', '').strip()
        hh    = Household.objects.filter(household_id=hh_id).first() if hh_id else None
        r.household      = hh
        r.full_name      = request.POST.get('full_name', r.full_name)
        r.birth_date     = request.POST.get('birth_date') or None
        r.age            = int(request.POST.get('age', r.age))
        r.gender         = request.POST.get('gender', r.gender)
        r.civil_status   = request.POST.get('civil_status', r.civil_status)
        r.livelihood     = request.POST.get('livelihood', r.livelihood)
        r.disability     = request.POST.get('disability', r.disability)
        r.lgbtq_type     = request.POST.get('lgbtq_type', r.lgbtq_type)
        r.citizenship    = request.POST.get('citizenship', r.citizenship)
        r.sector         = request.POST.get('sector', r.sector)
        r.is_osc         = request.POST.get('is_osc', r.is_osc)
        r.is_osy         = request.POST.get('is_osy', r.is_osy)
        r.is_labor_force = request.POST.get('is_labor_force', r.is_labor_force)
        r.is_unemployed  = request.POST.get('is_unemployed', r.is_unemployed)
        r.is_ofw         = request.POST.get('is_ofw', r.is_ofw)
        r.is_solo_parent = request.POST.get('is_solo_parent', r.is_solo_parent)
        r.is_indigenous  = request.POST.get('is_indigenous', r.is_indigenous)
        r.save()
    return redirect('residents')


@login_required
def resident_delete(request, pk):
    r = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        r.delete()
    return redirect('residents')


# ============================================================
# FACILITIES  (f6, f7, f8, f9, f10)
# ============================================================

@login_required
def facilities(request):
    user     = get_user(request)
    settings = get_Settings()
    tab      = request.GET.get('tab', 'land')
    context = {
        'user':       user,
        'settings':   settings,
        'tab':        tab,
        'lands':      Facility.objects.filter(category='Land'),
        'waters':     Facility.objects.filter(category='Water'),
        'utilities':  Facility.objects.filter(category='Utility'),
        'buildings':  Facility.objects.filter(category='Building'),
        'facilities': Facility.objects.filter(category='Facility'),
        'roads':      Facility.objects.filter(category='Road'),
    }
    return render(request, 'accounts/facilities.html', context)


@login_required
def facility_add(request):
    if request.method == 'POST':
        settings = get_Settings()
        tab      = request.POST.get('tab', 'land')
        Facility.objects.create(
            settings           = settings,
            category           = request.POST.get('category', ''),
            name               = request.POST.get('name', ''),
            type               = request.POST.get('type', ''),
            area               = request.POST.get('area') or None,
            description        = request.POST.get('description', ''),
            status             = request.POST.get('status', ''),
            quantity           = request.POST.get('quantity') or None,
            length_km          = request.POST.get('length_km') or None,
            maintenance_status = request.POST.get('maintenance_status', ''),
        )
        return redirect('/facilities/?tab=' + tab)
    return redirect('facilities')


@login_required
def facility_delete(request, pk):
    f   = get_object_or_404(Facility, pk=pk)
    tab = request.POST.get('tab', 'land')
    if request.method == 'POST':
        f.delete()
    return redirect('/facilities/?tab=' + tab)


# ============================================================
# INSTITUTIONS  (f11, f12, f13)
# ============================================================

@login_required
def institution(request):
    user     = get_user(request)
    settings = get_Settings()
    tab      = request.GET.get('tab', 'institutions')
    context = {
        'user':          user,
        'settings':      settings,
        'tab':           tab,
        'institutions':  Institution.objects.all(),
        'medical':       MedicalStaff.objects.all(),
        'professionals': OtherProfessional.objects.all(),
    }
    return render(request, 'accounts/institution.html', context)


@login_required
def institution_add(request):
    if request.method == 'POST':
        settings = get_Settings()
        Institution.objects.create(
            settings  = settings,
            name      = request.POST.get('name', ''),
            president = request.POST.get('president', ''),
            members   = int(request.POST.get('members', 0)),
            status    = request.POST.get('status', 'Active'),
            programs  = request.POST.get('programs', ''),
        )
    return redirect('/institutions/?tab=institutions')


@login_required
def institution_delete(request, pk):
    i = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        i.delete()
    return redirect('/institutions/?tab=institutions')


@login_required
def medstaff_add(request):
    if request.method == 'POST':
        settings = get_Settings()
        MedicalStaff.objects.create(
            settings       = settings,
            name           = request.POST.get('name', ''),
            position       = request.POST.get('position', 'Health Worker'),
            contact_number = request.POST.get('contact_number', ''),
        )
    return redirect('/institutions/?tab=medical')


@login_required
def medstaff_delete(request, pk):
    m = get_object_or_404(MedicalStaff, pk=pk)
    if request.method == 'POST':
        m.delete()
    return redirect('/institutions/?tab=medical')


@login_required
def professional_add(request):
    if request.method == 'POST':
        settings = get_Settings()
        OtherProfessional.objects.create(
            settings       = settings,
            name           = request.POST.get('name', ''),
            profession     = request.POST.get('profession', 'Teacher'),
            contact_number = request.POST.get('contact_number', ''),
        )
    return redirect('/institutions/?tab=professionals')


@login_required
def professional_delete(request, pk):
    p = get_object_or_404(OtherProfessional, pk=pk)
    if request.method == 'POST':
        p.delete()
    return redirect('/institutions/?tab=professionals')


# ============================================================
# REPORTS  (f14, f15)
# ============================================================

@login_required
def reports(request):
    user       = get_user(request)
    settings   = get_Settings()
    residents  = Resident.objects.all()
    households = Household.objects.all()

    total_pop  = residents.count()
    total_hh   = households.count()
    disability = residents.filter(disability=True).count()
    infra      = (
        Facility.objects.filter(category='Building').count() +
        Facility.objects.filter(category='Facility').count()
    )
    avg_hh = round(total_pop / total_hh, 1) if total_hh else 0

    # Age groups for bar chart
    age_groups = [
        ('0-14',  residents.filter(age__lte=14).count()),
        ('15-19', residents.filter(age__gte=15, age__lte=19).count()),
        ('20-29', residents.filter(age__gte=20, age__lte=29).count()),
        ('30-39', residents.filter(age__gte=30, age__lte=39).count()),
        ('40-49', residents.filter(age__gte=40, age__lte=49).count()),
        ('50-59', residents.filter(age__gte=50, age__lte=59).count()),
        ('60+',   residents.filter(age__gte=60).count()),
    ]
    max_age = max([c for _, c in age_groups], default=1) or 1

    # Gender
    male   = residents.filter(gender='Male').count()
    female = residents.filter(gender='Female').count()
    male_pct   = round(male / total_pop * 100) if total_pop else 0
    female_pct = round(female / total_pop * 100) if total_pop else 0

    # Livelihood
    livelihoods = {}
    for r in residents:
        l = r.livelihood.strip() if r.livelihood else 'None'
        livelihoods[l] = livelihoods.get(l, 0) + 1
    livelihoods_sorted = sorted(livelihoods.items(), key=lambda x: -x[1])
    max_liv = max(livelihoods.values(), default=1) or 1

    # House ownership
    ownership = {}
    for h in households:
        o = h.ownership_status
        ownership[o] = ownership.get(o, 0) + 1

    # House materials
    house_mat = {}
    for h in households:
        m = h.house_material
        house_mat[m] = house_mat.get(m, 0) + 1
    max_mat = max(house_mat.values(), default=1) or 1

    # Buildings by type
    bldg_types = {}
    for f in Facility.objects.filter(category='Building'):
        bldg_types[f.type] = bldg_types.get(f.type, 0) + 1
    max_bldg = max(bldg_types.values(), default=1) or 1

    # Detailed age group with disability
    detail_ages = [
        ('0-6 months',         residents.filter(age=0)),
        ('7 months - 2 years', residents.filter(age__gte=0, age__lte=2).exclude(age=0)),
        ('3-5 years old',      residents.filter(age__gte=3, age__lte=5)),
        ('6-12 years old',     residents.filter(age__gte=6, age__lte=12)),
        ('13-17 years old',    residents.filter(age__gte=13, age__lte=17)),
        ('18-59 years old',    residents.filter(age__gte=18, age__lte=59)),
        ('60 years and above', residents.filter(age__gte=60)),
    ]
    detail_age_data = []
    max_detail = 1
    for label, qs in detail_ages:
        total  = qs.count()
        with_d = qs.filter(disability=True).count()
        without = total - with_d
        if total > max_detail:
            max_detail = total
        detail_age_data.append((label, total, with_d, without))

    # Disability by gender
    male_with_d    = residents.filter(gender='Male', disability=True).count()
    male_without_d = residents.filter(gender='Male', disability=False).count()
    female_with_d  = residents.filter(gender='Female', disability=True).count()
    female_without_d = residents.filter(gender='Female', disability=False).count()

    # Disaster preparedness
    evacuation  = Facility.objects.filter(category='Building', type='Emergency')
    vulnerable  = [
        ('Persons with Disability', disability),
        ('Children (0-14)',         residents.filter(age__lte=14).count()),
        ('Senior Citizens (60+)',   residents.filter(age__gte=60).count()),
    ]
    total_vulnerable = sum(v for _, v in vulnerable)

    context = {
        'user':               user,
        'settings':           settings,
        'total_pop':          total_pop,
        'total_hh':           total_hh,
        'infra':              infra,
        'disability':         disability,
        'avg_hh':             avg_hh,
        'age_groups':         age_groups,
        'max_age':            max_age,
        'male':               male,
        'female':             female,
        'male_pct':           male_pct,
        'female_pct':         female_pct,
        'livelihoods':        livelihoods_sorted,
        'max_liv':            max_liv,
        'ownership':          ownership.items(),
        'house_mat':          house_mat.items(),
        'max_mat':            max_mat,
        'bldg_types':         bldg_types.items(),
        'max_bldg':           max_bldg,
        'detail_age_data':    detail_age_data,
        'max_detail':         max_detail,
        'male_with_d':        male_with_d,
        'male_without_d':     male_without_d,
        'female_with_d':      female_with_d,
        'female_without_d':   female_without_d,
        'evacuation':         evacuation,
        'vulnerable':         vulnerable,
        'total_vulnerable':   total_vulnerable,
    }
    return render(request, 'accounts/reports.html', context)


# ============================================================
# SETTINGS  (f16, f17, f18)
# ============================================================

@login_required
def settings(request): # Match this name in urls.py
    user     = get_user(request)
    settings_obj = get_Settings()
    tab      = request.GET.get('tab', 'profile')
    users    = User.objects.all()
    context  = {
        'user':     user,
        'settings': settings_obj,
        'tab':      tab,
        'users':    users,
    }
    return render(request, 'accounts/settings.html', context)

@login_required
def settings_save(request):
    if request.method == 'POST':
        s = get_Settings()
        s.barangay_name = request.POST.get('barangay_name', s.barangay_name)
        s.municipality  = request.POST.get('municipality', s.municipality)
        s.province      = request.POST.get('province', s.province)
        s.region        = request.POST.get('region', s.region)
        s.vision        = request.POST.get('vision', s.vision)
        s.mission       = request.POST.get('mission', s.mission)
        s.goals         = request.POST.get('goals', s.goals)
        s.save()
    return redirect('/settings/?tab=profile')