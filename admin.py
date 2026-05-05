from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, Household, Resident, Facility, Institution, MedicalStaff, OtherProfessional, Settings



class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'contact_number')}),
    )

admin.site.register(User, CustomUserAdmin)


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('household_code', 'head_of_family', 'number_of_members', 'created_at')
    search_fields = ('household_code', 'head_of_family')


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'civil_status', 'created_at')
    list_filter = ('gender', 'civil_status', 'citizenship', 'disability')
    search_fields = ('full_name',)


@admin.register(Settings)
class BarangaySettingsAdmin(admin.ModelAdmin):
    list_display = ('barangay_name', 'municipality', 'province', 'updated_at')


admin.site.register(Facility)
admin.site.register(Institution)
admin.site.register(MedicalStaff)
admin.site.register(OtherProfessional)