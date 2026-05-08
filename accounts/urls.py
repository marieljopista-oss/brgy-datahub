from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    
    # Navigation & Dashboards
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'), # Changed to lowercase
    path('settings/save/', views.settings_save, name='settings_save'),

    # Residents
    path('residents/', views.residents, name='residents'),
    path('residents/add/', views.resident_add, name='resident_add'),
    path('residents/edit/<int:pk>/', views.resident_edit, name='resident_edit'),
    path('residents/delete/<int:pk>/', views.resident_delete, name='resident_delete'),

    # Facilities
    path('facilities/', views.facilities, name='facilities'),
    path('facilities/add/', views.facility_add, name='facility_add'),
    path('facilities/delete/<int:pk>/', views.facility_delete, name='facility_delete'),

    # Institutions
    path('institutions/', views.institution, name='institution'),
    path('institutions/add/', views.institution_add, name='institution_add'),
    path('institutions/delete/<int:pk>/', views.institution_delete, name='institution_delete'),
    
    # Medical & Professionals
    path('medical/add/', views.medstaff_add, name='medstaff_add'),
    path('medical/delete/<int:pk>/', views.medstaff_delete, name='medstaff_delete'),
    path('professional/add/', views.professional_add, name='professional_add'),
    path('professional/delete/<int:pk>/', views.professional_delete, name='professional_delete'),
]