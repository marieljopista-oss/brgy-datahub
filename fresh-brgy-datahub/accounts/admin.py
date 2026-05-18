from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Household, Resident, BarangayProfile,
)


# ─────────────────────────────────────────
#  USER
# ─────────────────────────────────────────
class CustomUserAdmin(UserAdmin):
    model = User
    list_display  = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter   = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'contact')}),
    )

admin.site.register(User, CustomUserAdmin)


# ─────────────────────────────────────────
#  BARANGAY PROFILE
# ─────────────────────────────────────────
@admin.register(BarangayProfile)
class BarangayProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'municipality', 'province', 'region', 'captain']


# ─────────────────────────────────────────
#  HOUSEHOLD
# ─────────────────────────────────────────
@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display  = ['household_id', 'ownership', 'house_material']
    search_fields = ['household_id']
    list_filter   = ['ownership', 'house_material']


# ─────────────────────────────────────────
#  RESIDENT
# ─────────────────────────────────────────
@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'age', 'gender', 'civil_status',
                     'citizenship', 'has_disability', 'created_at']
    list_filter   = ['gender', 'civil_status', 'citizenship',
                     'has_disability', 'in_labor_force', 'is_ofw',
                     'is_solo_parent', 'is_indigenous']
    search_fields = ['first_name', 'last_name']
    readonly_fields = ['age']

