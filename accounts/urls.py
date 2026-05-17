from django.urls import path
from . import views

urlpatterns = [

    # ─────────────────────────────────────────
    #  AUTH
    # ─────────────────────────────────────────
    path('',        views.login_view,  name='login'),
    path('login/',  views.login_view,  name='login_alias'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # ─────────────────────────────────────────
    #  MAIN PAGES
    # ─────────────────────────────────────────
    path('home/',      views.home,      name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('residents/', views.residents, name='residents'),
    path('facilities/', views.facilities, name='facilities'),
    path('institutions/', views.institutions, name='institutions'),
    path('reports/',   views.reports,   name='reports'),
    path('settings/',  views.settings,  name='settings'),
    path('profile/',   views.profile,   name='profile'),

    # ─────────────────────────────────────────
    #  RESIDENTS CRUD
    # ─────────────────────────────────────────
    path('residents/add/',             views.resident_add,    name='resident_add'),
    path('residents/edit/<int:pk>/',   views.resident_edit,   name='resident_edit'),
    path('residents/delete/<int:pk>/', views.resident_delete, name='resident_delete'),
    path('residents/import/',          views.resident_import, name='resident_import'),

    path('facilities/add/<str:ftype>/',             views.facility_add,     name='facility_add'),
    path('facilities/delete/<str:ftype>/<int:pk>/', views.facility_delete,  name='facility_delete'),
    path('institutions/add/<str:itype>/',           views.institution_add,  name='institution_add'),
    path('institutions/delete/<str:itype>/<int:pk>/', views.institution_delete, name='institution_delete'),

    # ─────────────────────────────────────────
 # HOUSEHOLDS
    path('households/add/',             views.household_add,    name='household_add'),
    path('households/edit/<int:pk>/',   views.household_edit,   name='household_edit'),
    path('households/delete/<int:pk>/', views.household_delete, name='household_delete'),
    # ─────# HOUSEHOLDS
    path('reports/export/csv/<str:dtype>/', views.export_csv, name='export_csv'),

    # ─────────────────────────────────────────
    #  SETTINGS ACTIONS
    # ─────────────────────────────────────────
    path('settings/profile/save/',          views.settings_save_profile,  name='settings_save_profile'),
    path('settings/barangay/save/',         views.settings_save_barangay, name='settings_save_barangay'),
    path('settings/users/add/',             views.settings_add_user,      name='settings_add_user'),
    path('settings/backup/',                views.settings_backup,        name='settings_backup'),
    path('settings/users/delete/<int:pk>/', views.settings_delete_user,   name='settings_delete_user'),
    path("settings/restore/", views.settings_restore, name="settings_restore"),

    # ─────────────────────────────────────────
    #  PROFILE ACTIONS
    # ─────────────────────────────────────────
    path('profile/save/', views.profile_save, name='profile_save'),
]
