from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
import csv

from .models import (
    User, BarangayProfile,
    Household, Resident,
)


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def _age_group(birth_date):
    today  = date.today()
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
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login_view.html', {})


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

        if not all([first, last, role, username, email, password, confirm]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'accounts/login_view.html', {'show_signup': True})
        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/login_view.html', {'show_signup': True})
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/login_view.html', {'show_signup': True})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/login_view.html', {'show_signup': True})

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
    residents  = Resident.objects.select_related('household').all()
    households = Household.objects.all()
    total      = residents.count()

    # Age group breakdown with disability
    age_groups = []
    age_dis    = {g: {'without': 0, 'with': 0} for g in AGE_GROUP_ORDER}
    for r in residents:
        g = _age_group(r.birth_date)
        if r.has_disability:
            age_dis[g]['with']    += 1
        else:
            age_dis[g]['without'] += 1
    for g in AGE_GROUP_ORDER:
        w  = age_dis[g]['with']
        wo = age_dis[g]['without']
        age_groups.append({'label': g, 'without': wo, 'with': w, 'total': w + wo})

    # Livelihood distribution
    from django.db.models import Count
    livelihood_data = (
        residents.exclude(livelihood='')
        .values('livelihood')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # LGBTQ+
    lgbtq_data = (
        residents.exclude(lgbtq_type='')
        .values('lgbtq_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    stats = {
        'total_population':  total,
        'male':              residents.filter(gender='Male').count(),
        'female':            residents.filter(gender='Female').count(),
        'total_households':  households.count(),
        'owned':             households.filter(ownership='Owned').count(),
        'rented':            households.filter(ownership='Rented').count(),
        'livelihood_types':  residents.exclude(livelihood='').values('livelihood').distinct().count(),
        'with_disability':   residents.filter(has_disability=True).count(),
        'without_disability':residents.filter(has_disability=False).count(),
        'labor_force':       residents.filter(in_labor_force=True).count(),
        'unemployed':        residents.filter(is_unemployed=True).count(),
        'ofw':               residents.filter(is_ofw=True).count(),
        'solo_parents':      residents.filter(is_solo_parent=True).count(),
        'indigenous':        residents.filter(is_indigenous=True).count(),
        'filipino':          residents.filter(citizenship='Filipino').count(),
        'foreigner':         residents.filter(citizenship='Foreigner').count(),
        'married':           residents.filter(civil_status='Married').count(),
        'single':            residents.filter(civil_status='Single').count(),
        'widowed':           residents.filter(civil_status='Widowed').count(),
        'separated':         residents.filter(civil_status='Separated').count(),
        'osc': sum(1 for r in residents
                   if not r.in_labor_force and 6 <= r.age <= 14),
        'osy': sum(1 for r in residents
                   if r.is_unemployed and 15 <= r.age <= 24),
    }

    return render(request, 'dashboard.html', {
        'stats':          stats,
        'age_groups':     age_groups,
        'livelihood_data':livelihood_data,
        'lgbtq_data':     lgbtq_data,
        'barangay':       BarangayProfile.objects.first(),
    })


# ─────────────────────────────────────────
#  RESIDENTS
# ─────────────────────────────────────────

@login_required
def residents(request):
    residents_qs = Resident.objects.select_related('household').order_by('last_name', 'first_name')
    households   = Household.objects.all()
    return render(request, 'residents.html', {
        'residents':  residents_qs,
        'households': households,
    })


@login_required
def resident_add(request):
    if request.method == 'POST':
        p     = request.POST
        hh_id = p.get('household') or None
        Resident.objects.create(
            first_name     = p.get('first_name', ''),
            last_name      = p.get('last_name',  ''),
            birth_date     = p.get('birth_date'),
            gender         = p.get('gender', 'Male'),
            household_id   = hh_id,
            livelihood     = p.get('livelihood',  ''),
            civil_status   = p.get('civil_status',''),
            citizenship    = p.get('citizenship', 'Filipino'),
            lgbtq_type     = p.get('lgbtq_type',  ''),
            has_disability = bool(p.get('has_disability')),
            in_labor_force = bool(p.get('in_labor_force')),
            is_unemployed  = bool(p.get('is_unemployed')),
            is_ofw         = bool(p.get('is_ofw')),
            is_solo_parent = bool(p.get('is_solo_parent')),
            is_indigenous  = bool(p.get('is_indigenous')),
        )
    return redirect('residents')


@login_required
def resident_edit(request, pk):
    r = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        p = request.POST
        r.first_name     = p.get('first_name', '')
        r.last_name      = p.get('last_name',  '')
        r.birth_date     = p.get('birth_date')
        r.gender         = p.get('gender', 'Male')
        r.household_id   = p.get('household') or None
        r.livelihood     = p.get('livelihood',  '')
        r.civil_status   = p.get('civil_status','')
        r.citizenship    = p.get('citizenship', 'Filipino')
        r.lgbtq_type     = p.get('lgbtq_type',  '')
        r.has_disability = bool(p.get('has_disability'))
        r.in_labor_force = bool(p.get('in_labor_force'))
        r.is_unemployed  = bool(p.get('is_unemployed'))
        r.is_ofw         = bool(p.get('is_ofw'))
        r.is_solo_parent = bool(p.get('is_solo_parent'))
        r.is_indigenous  = bool(p.get('is_indigenous'))
        r.save()
    return redirect('residents')


@login_required
def resident_delete(request, pk):
    r = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        r.delete()
        messages.success(request, 'Resident deleted.')
    return redirect('residents')


@login_required
def resident_import(request):
    if request.method != 'POST':
        return redirect('residents')

    file = request.FILES.get('excel_file')

    # ── Validate file presence and extension ──
    if not file:
        messages.error(request, 'No file uploaded.')
        return redirect('residents')
    if not file.name.endswith(('.xlsx', '.xls')):
        messages.error(request, 'Invalid file type. Please upload an .xlsx or .xls file.')
        return redirect('residents')

    try:
        import openpyxl
        wb = openpyxl.load_workbook(file, data_only=True)
        ws = wb.active
    except Exception:
        messages.error(request, 'Could not read the Excel file. Make sure it is a valid .xlsx file.')
        return redirect('residents')

    created = 0
    skipped = 0
    errors  = []

    # Row 1 is the header — data starts at row 2 (min_row=2)
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):

        # Skip completely empty rows
        if not any(row):
            skipped += 1
            continue

        # Unpack the 14 expected columns
        try:
            (first_name, last_name, birth_date, gender, livelihood,
             has_disability, lgbtq_type, in_labor_force, is_unemployed,
             is_ofw, is_solo_parent, is_indigenous,
             civil_status, citizenship) = (list(row) + [None] * 14)[:14]
        except Exception:
            errors.append(f'Row {i}: Could not unpack columns.')
            continue

        # ── Required fields ──
        if not first_name or not last_name or not birth_date:
            errors.append(f'Row {i}: Skipped — First Name, Last Name, and Birth Date are required.')
            skipped += 1
            continue

        # ── Normalise birth_date ──
        if isinstance(birth_date, str):
            try:
                from datetime import datetime
                birth_date = datetime.strptime(birth_date.strip(), '%Y-%m-%d').date()
            except ValueError:
                errors.append(f'Row {i}: Invalid birth date format "{birth_date}". Use YYYY-MM-DD.')
                skipped += 1
                continue
        # openpyxl returns datetime objects for date cells
        elif hasattr(birth_date, 'date'):
            birth_date = birth_date.date()

        # ── Normalise boolean columns ──
        def to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return bool(val)
            if isinstance(val, str):
                return val.strip().upper() in ('TRUE', 'YES', '1')
            return False

        try:
            Resident.objects.create(
                first_name     = str(first_name).strip(),
                last_name      = str(last_name).strip(),
                birth_date     = birth_date,
                gender         = str(gender).strip()       if gender       else 'Male',
                livelihood     = str(livelihood).strip()   if livelihood   else '',
                has_disability = to_bool(has_disability),
                lgbtq_type     = str(lgbtq_type).strip()   if lgbtq_type   else '',
                in_labor_force = to_bool(in_labor_force),
                is_unemployed  = to_bool(is_unemployed),
                is_ofw         = to_bool(is_ofw),
                is_solo_parent = to_bool(is_solo_parent),
                is_indigenous  = to_bool(is_indigenous),
                civil_status   = str(civil_status).strip() if civil_status else '',
                citizenship    = str(citizenship).strip()  if citizenship  else 'Filipino',
            )
            created += 1
        except Exception as e:
            errors.append(f'Row {i}: {e}')
            skipped += 1

    # ── Flash summary messages ──
    if created:
        messages.success(request, f'Successfully imported {created} resident(s).')
    if skipped:
        messages.warning(request, f'{skipped} row(s) were skipped.')
    for err in errors:
        messages.warning(request, err)
    if not created and not errors:
        messages.info(request, 'No new residents were imported. The file may have been empty.')

    return redirect('residents')


# ─────────────────────────────────────────
#  REPORTS
# ─────────────────────────────────────────

@login_required
def reports(request):
    from django.db.models import Count
    residents_qs = Resident.objects.select_related('household').all()
    households   = Household.objects.all()
    total        = residents_qs.count()

    age_counts = {g: 0 for g in AGE_GROUP_ORDER}
    for r in residents_qs:
        age_counts[_age_group(r.birth_date)] += 1
    age_rows = [{'label': label, 'count': count} for label, count in age_counts.items()]

    dis_male   = residents_qs.filter(has_disability=True, gender='Male').count()
    dis_female = residents_qs.filter(has_disability=True, gender='Female').count()

    sectors = {
        'Labor Force':       residents_qs.filter(in_labor_force=True).count(),
        'Unemployed':        residents_qs.filter(is_unemployed=True).count(),
        'PWDs':              residents_qs.filter(has_disability=True).count(),
        'OFWs':              residents_qs.filter(is_ofw=True).count(),
        'Solo Parents':      residents_qs.filter(is_solo_parent=True).count(),
        'Indigenous (IPs)':  residents_qs.filter(is_indigenous=True).count(),
        'LGBTQ+':            residents_qs.exclude(lgbtq_type='').count(),
        'OSC (6–14)':        sum(1 for r in residents_qs if not r.in_labor_force and 6 <= r.age <= 14),
        'OSY (15–24)':       sum(1 for r in residents_qs if r.is_unemployed and 15 <= r.age <= 24),
    }

    context = {
        'stats': {
            'total_population': total,
            'total_with_dis':   residents_qs.filter(has_disability=True).count(),
            'total_households': households.count(),
            'avg_hh_members':   round(total / households.count(), 1) if households.count() else 0,
        },
        'age_labels':  list(age_counts.keys()),
        'age_values':  list(age_counts.values()),
        'age_rows':    age_rows,
        'gender_data': {
            'male':   residents_qs.filter(gender='Male').count(),
            'female': residents_qs.filter(gender='Female').count(),
        },
        'dis_male':   dis_male,
        'dis_female': dis_female,
        'sectors':    sectors,
        'vulnerable': {
            'pwds':     residents_qs.filter(has_disability=True).count(),
            'children': sum(v for k, v in age_counts.items()
                            if k in ['0 – 6 months', '7 months – 2 years old',
                                     '3 – 5 years old', '6 – 12 years old']),
            'seniors':  age_counts['60 years old and above'],
        },
        'barangay': BarangayProfile.objects.first(),
    }
    return render(request, 'reports.html', context)


@login_required
def export_csv(request, dtype):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{dtype}.csv"'
    writer = csv.writer(response)

    if dtype == 'residents':
        writer.writerow(['Name', 'Birth Date', 'Age', 'Gender', 'Household',
                         'Livelihood', 'Disability', 'Civil Status', 'Citizenship'])
        for r in Resident.objects.select_related('household').all():
            writer.writerow([
                r.full_name, r.birth_date, r.age, r.gender,
                r.household.household_id if r.household else '',
                r.livelihood, r.has_disability, r.civil_status, r.citizenship,
            ])

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
        b.vision  = request.POST.get('vision',  '')
        b.mission = request.POST.get('mission', '')
        b.goals   = request.POST.get('goals',   '')
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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role     = request.POST.get('role', '')
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
    return render(request, 'profile.html', {
        'user_profile': request.user,
    })


@login_required
def profile_save(request):
    if request.method == 'POST':
        u = request.user
        full_name = request.POST.get('full_name', '').strip().split(' ', 1)
        u.first_name = full_name[0]
        u.last_name  = full_name[1] if len(full_name) > 1 else ''
        u.email      = request.POST.get('email',   '').strip()
        u.contact    = request.POST.get('contact', '').strip()
        u.role       = request.POST.get('role',    '')

        new_pw  = request.POST.get('new_password',     '')
        confirm = request.POST.get('confirm_password', '')
        if new_pw:
            if new_pw == confirm and len(new_pw) >= 6:
                u.set_password(new_pw)
                messages.success(request, 'Password updated. Please log in again.')
            else:
                messages.error(request, 'Passwords do not match or too short.')
                return redirect('profile')

        if 'photo' in request.FILES:
            u.profile_photo = request.FILES['photo']

        u.save()
        messages.success(request, 'Profile saved.')
    return redirect('profile')
