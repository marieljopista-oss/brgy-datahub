urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.dashboard, name='dashboard'),

    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('facilities/', views.facilities, name='facilities'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('reports/', views.reports, name='reports'),

    path('residents/', views.residents, name='residents'),

    # FIX ADDED
    path('residents/add/', views.add_resident, name='add_resident'),

    path('institution/', views.institution, name='institution'),
]
