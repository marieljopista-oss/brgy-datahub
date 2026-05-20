from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


# ─────────────────────────────────────────
#  AUTH / USER
# ─────────────────────────────────────────

class User(AbstractUser):
    ROLES = [
        ('Captain',      'Captain'),
        ('Secretary',    'Secretary'),
        ('Health Worker','Health Worker'),
        ('Treasurer',    'Treasurer'),
        ('Councilor',    'Councilor'),
    ]
    role          = models.CharField(max_length=50, choices=ROLES, blank=True)
    contact       = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username()}({self.role})"


class BarangayProfile(models.Model):
    name  = models.CharField(max_length=100, blank=True)
    municipality  = models.CharField(max_length=100, blank=True)
    province  = models.CharField(max_length=100, blank=True)
    region  = models.CharField(max_length=100, blank=True)
    captain  = models.CharField(max_length=100, blank=True)
    contact  = models.CharField(max_length=20, blank=True)
    vision  = models.TextField(blank=True)
    mission  = models.TextField(blank=True)
    goals  = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Barangay Profiles'

    def __str__(self):
        return self.name or 'Barangay Profile'


class Household(models.Model):
    OWNERSHIP_CHOICES = [('Owned', 'Owned'), ('Rented', 'Rented'), ('Shared', 'Shared')]
    MATERIAL_CHOICES = [
        ('Concrete','Concrete'),
       
        ('Wood',    'Wood'),
        ('Mixed',  'Mixed'),
       
        ('Light Materials','Light Materials'),
        ('Semi-Concrete',  'Semi-Concrete'),
    ]
    household_id = models.CharField(max_length=20, unique=True, blank=True)
    head = models.CharField(max_length=200, blank=True)
    ownership = models.CharField(max_length=10, choices=OWNERSHIP_CHOICES, blank=True)
    house_material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, blank=True)

    def save(self, *args, **kwargs):
        if not self.household_id:
            last = Household.objects.order_by('id').last()
            next_num = (last.id + 1) if last else 1
            self.household_id = f"HH-{next_num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.household_id} - {self.head}" if self.head else self.household_id


class Resident(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    CIVIL_CHOICES  = [
        ('Single',    'Single'),
        ('Married',   'Married'),
        ('Widowed',   'Widowed'),
        ('Separated', 'Separated'),
    ]
    CITIZEN_CHOICES = [('Filipino', 'Filipino'), ('Foreigner', 'Foreigner')]
    LGBTQ_CHOICES   = [
        ('',            'None'),
        ('Gay',         'Gay'),
        ('Lesbian',     'Lesbian'),
        ('Bisexual',    'Bisexual'),
        ('Transgender', 'Transgender'),
    ]
    LIVELIHOOD_CHOICES = [
        ('Farming',       'Farming'),
        ('Teaching',      'Teaching'),
        ('Student',       'Student'),
        ('Construction',  'Construction'),
        ('Small Business','Small Business'),
        ('Retail',        'Retail'),
        ('Healthcare',    'Healthcare'),
        ('Government',    'Government'),
    ]

    # Core fields
    first_name  = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name   = models.CharField(max_length=100)
    birth_date  = models.DateField(default='2000-01-01')
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES)

    # Optional links
    household   = models.ForeignKey(Household, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='residents')
    livelihood  = models.CharField(max_length=30, choices=LIVELIHOOD_CHOICES, blank=True)
    civil_status= models.CharField(max_length=15, choices=CIVIL_CHOICES,      blank=True)
    citizenship = models.CharField(max_length=15, choices=CITIZEN_CHOICES,    default='Filipino')
    lgbtq_type  = models.CharField(max_length=15, choices=LGBTQ_CHOICES,      blank=True)

    # Boolean flags
    has_disability = models.BooleanField(default=False)
    in_labor_force = models.BooleanField(default=False)
    is_unemployed = models.BooleanField(default=False)
    is_ofw = models.BooleanField(default=False)
    is_solo_parent = models.BooleanField(default=False)
    is_indigenous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)

    @property
    def age(self):
        today = date.today()
        return (today - self.birth_date).days // 365

    def __str__(self):
        return self.full_name


# ─────────────────────────────────────────
#  FACILITIES
# ─────────────────────────────────────────

class LandBody(models.Model):
    LAND_TYPE_CHOICES = [
        ('Agricultural', 'Agricultural'),
        ('Residential',  'Residential'),
        ('Forest',       'Forest'),
        ('Commercial',   'Commercial'),
        ('Industrial',   'Industrial'),
    ]
    name  = models.CharField(max_length=100)
    land_type  = models.CharField(max_length=20, choices=LAND_TYPE_CHOICES)
    area_ha  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WaterBody(models.Model):
    WATER_TYPE_CHOICES = [
        ('River',  'River'),
        ('Creek',  'Creek'),
        ('Lake',   'Lake'),
        ('Spring', 'Spring'),
        ('Dam',    'Dam'),
    ]
    name        = models.CharField(max_length=100)
    water_type  = models.CharField(max_length=15, choices=WATER_TYPE_CHOICES)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.water_type})"


class Utility(models.Model):
    AVAIL_CHOICES = [('Available', 'Available'), ('Not Available', 'Not Available')]
    electricity = models.CharField(max_length=15, choices=AVAIL_CHOICES, default='Available')
    water_supply = models.CharField(max_length=15, choices=AVAIL_CHOICES, default='Available')
    waste_management = models.CharField(max_length=15, choices=AVAIL_CHOICES, default='Available')
    toilet_count = models.PositiveIntegerField(default=0)
    bath_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Utilities'

    def __str__(self):
        return "Utility Settings"


class Building(models.Model):
    TYPE_CHOICES = [
        ('Health Facility', 'Health Facility'),
        ('Educational', 'Educational'),
        ('Emergency', 'Emergency'),
        ('Government', 'Government'),
        ('Religious', 'Religious'),
    ]
    STATUS_CHOICES = [
        ('Operational', 'Operational'),
        ('Under Repair', 'Under Repair'),
        ('Closed', 'Closed'),
    ]
    name = models.CharField(max_length=100)
    building_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Operational')
    created_at = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f"{self.name}({self.building_type})"


class Facility(models.Model):
    TYPE_CHOICES = [
        ('Community', 'Community'),
        ('Security', 'Security'),
        ('Transport', 'Transport'),
        ('Health', 'Health'),
        ('Education', 'Education'),
    ]
    name = models.CharField(max_length=100)
    facility_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Facilities'

    def __str__(self):
        return f"{self.name} (x{self.quantity})"


class RoadNetwork(models.Model):
    TYPE_CHOICES = [
        ('Concrete', 'Concrete'),
        ('Gravel', 'Gravel'),
        ('Asphalt', 'Asphalt'),
        ('Dirt Road', 'Dirt Road'),
    ]
    STATUS_CHOICES = [
        ('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor'),
    ]
    road_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    length_km = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Good')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.road_type} - {self.length_km} km ({self.status})"


# ─────────────────────────────────────────
#  INSTITUTIONS
# ─────────────────────────────────────────

class MedicalStaff(models.Model):
    POSITION_CHOICES = [
        ('Doctor', 'Doctor'),
        ('Health Worker', 'Health Worker'),
        ('Nurse', 'Nurse'),
        ('Midwife', 'Midwife'),
        ('Dentist', 'Dentist'),
    ]
    resident   = models.ForeignKey('Resident', on_delete=models.SET_NULL,   # ← ADD
                                    null=True, blank=True,                   # ← ADD
                                    related_name='medical_staff')            # ← ADD
    name       = models.CharField(max_length=100)
    position   = models.CharField(max_length=20, choices=POSITION_CHOICES)
    contact    = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return self.resident.full_name if self.resident else "No Resident Linked"


class Professional(models.Model):
    PROFESSION_CHOICES = [
        ('Teacher', 'Teacher'),
        ('Carpenter', 'Carpenter'),
        ('Electrician', 'Electrician'),
        ('Plumber', 'Plumber'),
        ('Engineer', 'Engineer'),
        ('Mechanic', 'Mechanic'),
        ('Farmer', 'Farmer'),
    ]
    resident   = models.ForeignKey('Resident', on_delete=models.SET_NULL,   # ← ADD
                                    null=True, blank=True,                   # ← ADD
                                    related_name='professionals')            # ← ADD
    name       = models.CharField(max_length=100)
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES)
    contact    = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.resident.full_name if self.resident else "No Resident Linked"