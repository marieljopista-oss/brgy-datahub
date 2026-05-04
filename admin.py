from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Resident

# Register the User model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

# Register the Resident model ONCE
@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    # This combines all the features you wanted
    list_display = ('first_name', 'last_name', 'gender', 'created_at')
    list_filter = ('gender',) 
    search_fields = ('first_name', 'last_name')