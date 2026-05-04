from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date

# ============================================================
# USER MODEL
# ============================================================
class User(AbstractUser):
    ROLES = [
        ('Captain', 'Captain'),
        ('Secretary', 'Secretary'),
        ('Health Worker', 'Health Worker'),
    ]
    role = models.CharField(max_length=50, choices=ROLES, default='Captain')
    contact_number = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        verbose_name = 'Barangay User'
        verbose_name_plural = 'Barangay Users'

    def __str__(self):
        return f"{self.username} - {self.role}"


# ============================================================
# HOUSEHOLD MODEL
# ============================================================
class Household(models.Model):
    MATERIAL_CHOICES = [('Concrete', 'Concrete'), ('Wood', 'Wood'), ('Mixed', 'Mixed')]
    OWNERSHIP_CHOICES = [('Owned', 'Owned'), ('Rented', 'Rented')]

    household_code = models.CharField(max_length=20, unique=True)
    house_material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default='Concrete')
    ownership_status = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES, default='Owned')
    head_of_family = models.CharField(max_length=100, blank=True, default='')
    number_of_members = models.PositiveIntegerField(default=0, editable=False) # Auto-calculated
    created_at = models.DateTimeField(auto_now_add=True)

    def update_member_count(self):
        """Updates the count of residents linked to this household."""
        count = self.resident_set.count()
        self.number_of_members = count
        self.save()

    def __str__(self):
        return f"{self.household_code} ({self.head_of_family})"


# ============================================================
# RESIDENT MODEL
# ============================================================
class Resident(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    CIVIL_CHOICES = [
        ('Single', 'Single'), ('Married', 'Married'), 
        ('Widowed', 'Widowed'), ('Separated', 'Separated')
    ]
    LGBTQ_CHOICES = [
        ('None', 'None'), ('Gay', 'Gay'), ('Lesbian', 'Lesbian'), 
        ('Bisexual', 'Bisexual'), ('Transgender', 'Transgender')
    ]

    household = models.ForeignKey(Household, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    age = models.IntegerField(default=0, editable=False) # Auto-calculated
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    civil_status = models.CharField(max_length=20, choices=CIVIL_CHOICES, default='Single')
    citizenship = models.CharField(max_length=50, default='Filipino')
    livelihood = models.CharField(max_length=100, blank=True, default='')
    
    # Booleans for quick reporting
    disability = models.BooleanField(default=False)
    lgbtq_type = models.CharField(max_length=20, choices=LGBTQ_CHOICES, default='None')
    is_labor_force = models.BooleanField(default=False)
    is_unemployed = models.BooleanField(default=False)
    is_ofw = models.BooleanField(default=False)
    is_solo_parent = models.BooleanField(default=False)
    is_indigenous = models.BooleanField(default=False)
    is_osc = models.BooleanField("Out of School Child", default=False)
    is_osy = models.BooleanField("Out of School Youth", default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically calculate age based on birth_date before saving."""
        if self.birth_date:
            today = date.today()
            self.age = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


# ============================================================
# SIGNALS (To update Household counts)
# ============================================================
@receiver(post_save, sender=Resident)
@receiver(post_delete, sender=Resident)
def update_household_member_count(sender, instance, **kwargs):
    if instance.household:
        instance.household.update_member_count()


# ============================================================
# FACILITY & INFRASTRUCTURE
# ============================================================
class Facility(models.Model):
    CATEGORY_CHOICES = [
        ('Land', 'Land'), ('Water', 'Water'), ('Utility', 'Utility'),
        ('Building', 'Building'), ('Facility', 'Facility'), ('Road', 'Road'),
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    facility_type = models.CharField(max_length=50) # Changed from 'type'
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, default='Functional')
    length_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name

# ============================================================
# BARANGAY SETTINGS (Singleton Pattern recommended)
# ============================================================
class BarangaySettings(models.Model):
    barangay_name = models.CharField(max_length=100, default='Cogon')
    municipality = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Barangay Setting"
        verbose_name_plural = "Barangay Settings"

    def __str__(self):
        return self.barangay_name
