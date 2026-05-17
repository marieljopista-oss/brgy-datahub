from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


# ─────────────────────────────────────────
#  USER
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
        return self.username


# ─────────────────────────────────────────
#  BARANGAY PROFILE
# ─────────────────────────────────────────

class BarangayProfile(models.Model):
    name         = models.CharField(max_length=100, blank=True)
    municipality = models.CharField(max_length=100, blank=True)
    province     = models.CharField(max_length=100, blank=True)
    region       = models.CharField(max_length=100, blank=True)
    captain      = models.CharField(max_length=100, blank=True)
    contact      = models.CharField(max_length=20,  blank=True)
    vision       = models.TextField(blank=True)
    mission      = models.TextField(blank=True)
    goals        = models.TextField(blank=True)

    def __str__(self):
        return self.name or 'Barangay Profile'


# ─────────────────────────────────────────
#  HOUSEHOLD
# ─────────────────────────────────────────

class Household(models.Model):
    OWNERSHIP_CHOICES = [('Owned', 'Owned'), ('Rented', 'Rented'), ('Shared', 'Shared')]
    MATERIAL_CHOICES  = [
        ('Concrete',       'Concrete'),
        ('Wood',           'Wood'),
        ('Mixed',          'Mixed'),
        ('Light Materials','Light Materials'),
        ('Semi-Concrete',  'Semi-Concrete'),
    ]
    household_id   = models.CharField(max_length=20, unique=True)
    head           = models.CharField(max_length=100, blank=True)
    address        = models.CharField(max_length=200, blank=True)
    ownership      = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES, blank=True)
    house_material = models.CharField(max_length=20, choices=MATERIAL_CHOICES,  blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    @property
    def member_count(self):
        return self.residents.count()

    def __str__(self):
        return self.household_id


# ─────────────────────────────────────────
#  RESIDENT
# ─────────────────────────────────────────

class Resident(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    household      = models.ForeignKey(Household, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='residents')
    first_name     = models.CharField(max_length=50)
    middle_name    = models.CharField(max_length=50, blank=True)
    last_name      = models.CharField(max_length=50)
    birth_date     = models.DateField()
    gender         = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    civil_status   = models.CharField(max_length=20, blank=True)
    citizenship    = models.CharField(max_length=30, default='Filipino')
    livelihood     = models.CharField(max_length=50, blank=True)
    lgbtq_type     = models.CharField(max_length=30, blank=True)
    has_disability = models.BooleanField(default=False)
    in_labor_force = models.BooleanField(default=False)
    is_unemployed  = models.BooleanField(default=False)
    is_ofw         = models.BooleanField(default=False)
    is_solo_parent = models.BooleanField(default=False)
    is_indigenous  = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

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
#  FACILITIES & INFRASTRUCTURE
# ─────────────────────────────────────────

class LandBody(models.Model):
    LAND_TYPES = [
        ('Agricultural', 'Agricultural'), ('Residential', 'Residential'),
        ('Forest',       'Forest'),       ('Commercial',  'Commercial'),
        ('Industrial',   'Industrial'),
    ]
    name       = models.CharField(max_length=100)
    land_type  = models.CharField(max_length=20, choices=LAND_TYPES)
    area_ha    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WaterBody(models.Model):
    WATER_TYPES = [
        ('River',  'River'),  ('Creek', 'Creek'), ('Lake',   'Lake'),
        ('Spring', 'Spring'), ('Dam',   'Dam'),
    ]
    name        = models.CharField(max_length=100)
    water_type  = models.CharField(max_length=20, choices=WATER_TYPES)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    BUILDING_TYPES = [
        ('Health Facility', 'Health Facility'), ('Educational',  'Educational'),
        ('Emergency',       'Emergency'),       ('Government',   'Government'),
        ('Religious',       'Religious'),
    ]
    STATUS_CHOICES = [
        ('Operational', 'Operational'), ('Under Repair', 'Under Repair'),
        ('Closed',      'Closed'),
    ]
    name       = models.CharField(max_length=100)
    bldg_type  = models.CharField(max_length=30, choices=BUILDING_TYPES)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Operational')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Facility(models.Model):
    FACILITY_TYPES = [
        ('Community',  'Community'), ('Security',   'Security'),
        ('Transport',  'Transport'), ('Health',     'Health'),
        ('Education',  'Education'),
    ]
    name          = models.CharField(max_length=100)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    quantity      = models.PositiveIntegerField(default=1)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RoadNetwork(models.Model):
    ROAD_TYPES = [
        ('Concrete',  'Concrete'), ('Gravel', 'Gravel'),
        ('Asphalt',   'Asphalt'), ('Dirt Road', 'Dirt Road'),
    ]
    STATUS_CHOICES = [
        ('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor'),
    ]
    road_type  = models.CharField(max_length=20, choices=ROAD_TYPES)
    length_km  = models.DecimalField(max_digits=8, decimal_places=2)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Good')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.road_type} ({self.length_km} km)'


# ─────────────────────────────────────────
#  INSTITUTIONS & HUMAN RESOURCES
# ─────────────────────────────────────────

class Institution(models.Model):
    name       = models.CharField(max_length=100)
    president  = models.CharField(max_length=100, blank=True)
    members    = models.PositiveIntegerField(default=0)
    status     = models.CharField(max_length=10,
                                  choices=[('Active','Active'),('Inactive','Inactive')],
                                  default='Active')
    programs   = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MedicalStaff(models.Model):
    POSITIONS = [
        ('Doctor',        'Doctor'),       ('Health Worker', 'Health Worker'),
        ('Nurse',         'Nurse'),         ('Midwife',       'Midwife'),
        ('Dentist',       'Dentist'),
    ]
    name       = models.CharField(max_length=100)
    position   = models.CharField(max_length=20, choices=POSITIONS)
    contact    = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Professional(models.Model):
    PROFESSIONS = [
        ('Teacher',     'Teacher'),   ('Carpenter',   'Carpenter'),
        ('Electrician', 'Electrician'),('Plumber',    'Plumber'),
        ('Engineer',    'Engineer'),  ('Mechanic',    'Mechanic'),
        ('Farmer',      'Farmer'),
    ]
    name       = models.CharField(max_length=100)
    profession = models.CharField(max_length=20, choices=PROFESSIONS)
    contact    = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name