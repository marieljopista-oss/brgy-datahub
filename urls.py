from django.urls import path
from . import views

urlpatterns = [
    # Clean up the names! No '.html' here.
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'), # Default route to home/dashboard
    path('dashboard/', views.dashboard, name='dashboard'), # Must match your view name
    
    path('facilities/', views.facilities, name='facilities'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('reports/', views.reports, name='reports'),
    path('residents/', views.residents, name='residents'), # Simplified for now
    path('institution/', views.institution, name='institution'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]