from django.db import models
from django.contrib.auth.models import AbstractUser


# ─────────────────────────────────────────
#  AUTH / USER
# ─────────────────────────────────────────

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Captain',      'Barangay Captain'),
        ('Secretary',    'Barangay Secretary'),
        ('Health Worker','Health Worker'),
        ('Treasurer',    'Barangay Treasurer'),
        ('Councilor',    'Barangay Councilor'),
    ]
    role          = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    contact       = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


# ─────────────────────────────────────────
#  BARANGAY PROFILE
# ─────────────────────────────────────────

class BarangayProfile(models.Model):
    name         = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100, blank=True)
    province     = models.CharField(max_length=100, blank=True)
    region       = models.CharField(max_length=100, blank=True)
    captain      = models.CharField(max_length=100, blank=True)
    contact      = models.CharField(max_length=20,  blank=True)
    vision       = models.TextField(blank=True)
    mission      = models.TextField(blank=True)
    goals        = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Barangay Profile'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────
#  HOUSEHOLD
# ─────────────────────────────────────────

class Household(models.Model):
    OWNERSHIP_CHOICES = [('Owned', 'Owned'), ('Rented', 'Rented')]
    MATERIAL_CHOICES  = [
        ('Concrete',       'Concrete'),
        ('Wood',           'Wood'),
        ('Mixed',          'Mixed'),
        ('Light Material', 'Light Material'),
    ]
    household_id   = models.CharField(max_length=20, unique=True, blank=True)
    head           = models.CharField(max_length=200, blank=True)
    ownership      = models.CharField(max_length=10, choices=OWNERSHIP_CHOICES, blank=True)
    house_material = models.CharField(max_length=20, choices=MATERIAL_CHOICES,  blank=True)

    def save(self, *args, **kwargs):
        if not self.household_id:
            last     = Household.objects.order_by('id').last()
            next_num = (last.id + 1) if last else 1
            self.household_id = f"HH-{next_num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.household_id} — {self.head}" if self.head else self.household_id


# ─────────────────────────────────────────
#  RESIDENT
# ─────────────────────────────────────────

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

    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    birth_date  = models.DateField(default='2000-01-01')
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES)

    household    = models.ForeignKey(Household, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='residents')
    livelihood   = models.CharField(max_length=30, choices=LIVELIHOOD_CHOICES, blank=True)
    civil_status = models.CharField(max_length=15, choices=CIVIL_CHOICES,      blank=True)
    citizenship  = models.CharField(max_length=15, choices=CITIZEN_CHOICES,    default='Filipino')
    lgbtq_type   = models.CharField(max_length=15, choices=LGBTQ_CHOICES,      blank=True)

    has_disability = models.BooleanField(default=False)
    in_labor_force = models.BooleanField(default=False)
    is_unemployed  = models.BooleanField(default=False)
    is_ofw         = models.BooleanField(default=False)
    is_solo_parent = models.BooleanField(default=False)
    is_indigenous  = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        b     = self.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def __str__(self):
        return self.full_name