from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Household, Resident, Facility, 
    Institution, MedicalStaff, OtherProfessional, Settings
)

# 1. Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'contact_number')}),
    )

admin.site.register(User, CustomUserAdmin)

# 2. Household Admin
@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('household_code', 'head_of_family', 'number_of_members', 'created_at')
    search_fields = ('household_code', 'head_of_family')

# 3. Resident Admin (Fixed E108 & E116 Errors)
@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    # 'full_name' exists in your model, but 'gender' and 'created_at' must match the field names exactly
    list_display = ('full_name', 'age', 'gender', 'civil_status', 'created_at')
    list_filter = ('gender', 'civil_status', 'citizenship', 'disability')
    search_fields = ('full_name',)

# 4. Settings Admin (Renamed to match your request)
@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('barangay_name', 'municipality', 'province', 'updated_at')

# 5. Other Models
admin.site.register(Facility)
admin.site.register(Institution)
admin.site.register(MedicalStaff)
admin.site.register(OtherProfessional)
