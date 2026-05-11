from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Household, Resident, Facility,
    Institution, MedicalStaff, Professional,
    LandBody, WaterBody, Utility, Building,
    RoadNetwork, BarangayProfile,
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


# ─────────────────────────────────────────
#  FACILITIES
# ─────────────────────────────────────────
@admin.register(LandBody)
class LandBodyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'land_type', 'area_ha']
    list_filter   = ['land_type']
    search_fields = ['name']

@admin.register(WaterBody)
class WaterBodyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'water_type', 'description']
    list_filter   = ['water_type']
    search_fields = ['name']

@admin.register(Utility)
class UtilityAdmin(admin.ModelAdmin):
    list_display = ['electricity', 'water_supply', 'waste_management',
                    'toilet_count', 'bath_count']

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display  = ['name', 'building_type', 'status']
    list_filter   = ['building_type', 'status']
    search_fields = ['name']

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display  = ['name', 'facility_type', 'quantity']
    list_filter   = ['facility_type']
    search_fields = ['name']

@admin.register(RoadNetwork)
class RoadNetworkAdmin(admin.ModelAdmin):
    list_display = ['road_type', 'length_km', 'status']
    list_filter  = ['road_type', 'status']


# ─────────────────────────────────────────
#  INSTITUTIONS
# ─────────────────────────────────────────
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display  = ['name', 'president', 'members', 'status', 'programs']
    list_filter   = ['status']
    search_fields = ['name', 'president']

@admin.register(MedicalStaff)
class MedicalStaffAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'position', 'contact']
    list_filter   = ['position']
    search_fields = ['full_name']

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'profession', 'contact']
    list_filter   = ['profession']
    search_fields = ['full_name']