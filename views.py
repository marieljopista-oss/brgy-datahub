from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Resident  # This relative import works fine inside a standard Django app

# 1. AUTHENTICATION
def login_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_pass = request.POST.get('password')

        user = authenticate(request, username=user_name, password=user_pass)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            return render(request, 'accounts/login_view.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login_view.html')

def forgot_password(request):
    return render(request, 'accounts/forgot_password.html')

# 2. MAIN PAGES (Requires Login)
@login_required
def home(request):
    return render(request, 'accounts/home.html')

@login_required
def dashboard(request):
    # Counts real data from the database
    total = Resident.objects.count()
    males = Resident.objects.filter(gender='Male').count()
    females = Resident.objects.filter(gender='Female').count()

    context = {
        'total_pop': total,        
        'male_count': males,
        'female_count': females,
        'total_households': 0, 
    }
    return render(request, 'accounts/dashboard.html', context)

# 3. OTHER MODULES (Requires Login)
@login_required
def facilities(request):
    return render(request, 'accounts/facilities.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def settings(request):
    return render(request, 'accounts/settings.html')

@login_required
def reports(request):
    return render(request, 'accounts/reports.html') 

@login_required
def residents(request):
    # Fetch all resident records from PostgreSQL
    all_residents = Resident.objects.all() 
    
    context = {
        'residents': all_residents,
    }
    return render(request, 'accounts/residents.html', context)

@login_required
def add_resident(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        livelihood = request.POST.get('livelihood')

        Resident.objects.create(
            full_name=full_name,
            gender=gender,
            livelihood=livelihood
        )

        return redirect('residents')

    return redirect('residents')

@login_required
def institution(request):
    return render(request, 'accounts/institution.html')
