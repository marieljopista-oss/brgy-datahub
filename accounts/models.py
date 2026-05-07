from django.db import models
from django.contrib.auth.models import AbstractUser




# ============================================================
# USER MODEL
# ============================================================
class User(AbstractUser):
    ROLES = [
        ('Captain',       'Captain'),
        ('Secretary',     'Secretary'),
        ('Health Worker', 'Health Worker'),
    ]
    role           = models.CharField(max_length=50, choices=ROLES, default='Captain')
    contact_number = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        verbose_name        = 'Barangay User'
        verbose_name_plural = 'Barangay Users'

    def __str__(self):
        return self.username


# ============================================================
# HOUSEHOLD MODEL
# ============================================================
class Household(models.Model):
    MATERIAL_CHOICES = [
        ('Concrete', 'Concrete'),
        ('Wood',     'Wood'),
        ('Mixed',    'Mixed'),
    ]
    OWNERSHIP_CHOICES = [
        ('Owned',  'Owned'),
        ('Rented', 'Rented'),
    ]
    household_code    = models.CharField(max_length=20, unique=True)
    house_material    = models.CharField(max_length=20, choices=MATERIAL_CHOICES,
                                         default='Concrete')
    ownership_status  = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES,
                                         default='Owned')
    head_of_family    = models.CharField(max_length=100, blank=True, default='')
    number_of_members = models.IntegerField(default=0)
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.household_code


# ============================================================
# RESIDENT MODEL
# ============================================================
class Resident(models.Model):
    GENDER_CHOICES = [
        ('Male',   'Male'),
        ('Female', 'Female'),
    ]
    CIVIL_CHOICES = [
        ('',          'None'),
        ('Single',    'Single'),
        ('Married',   'Married'),
        ('Widowed',   'Widowed'),
        ('Separated', 'Separated'),
    ]
    CITIZENSHIP_CHOICES = [
        ('Filipino',  'Filipino'),
        ('Foreigner', 'Foreigner'),
    ]
    LGBTQ_CHOICES = [
        ('',            'None'),
        ('Gay',         'Gay'),
        ('Lesbian',     'Lesbian'),
        ('Bisexual',    'Bisexual'),
        ('Transgender', 'Transgender'),
    ]

    household        = models.ForeignKey(Household, on_delete=models.SET_NULL,
                                          null=True, blank=True)
    full_name        = models.CharField(max_length=100)
    birth_date       = models.DateField(null=True, blank=True)
    age              = models.IntegerField(default=0)
    gender           = models.CharField(max_length=10, choices=GENDER_CHOICES,
                                         default='Male')
    civil_status     = models.CharField(max_length=20, choices=CIVIL_CHOICES,
                                         blank=True, default='')
    citizenship      = models.CharField(max_length=20, choices=CITIZENSHIP_CHOICES,
                                         default='Filipino')
    livelihood       = models.CharField(max_length=100, blank=True, default='')
    house_material   = models.CharField(max_length=20, blank=True, default='')
    ownership_status = models.CharField(max_length=20, blank=True, default='')
    disability       = models.BooleanField(default=False)
    lgbtq_type       = models.CharField(max_length=20, choices=LGBTQ_CHOICES,
                                         blank=True, default='')
    is_labor_force   = models.BooleanField(default=False)
    is_unemployed    = models.BooleanField(default=False)
    is_ofw           = models.BooleanField(default=False)
    is_solo_parent   = models.BooleanField(default=False)
    is_indigenous    = models.BooleanField(default=False)
    is_osc           = models.BooleanField(default=False)
    is_osy           = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


# ============================================================
# FACILITY MODEL
# ============================================================
class Facility(models.Model):
    CATEGORY_CHOICES = [
        ('Land',     'Land'),
        ('Water',    'Water'),
        ('Utility',  'Utility'),
        ('Building', 'Building'),
        ('Facility', 'Facility'),
        ('Road',     'Road'),
    ]
    category           = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    name               = models.CharField(max_length=100)
    type               = models.CharField(max_length=50)
    area               = models.DecimalField(max_digits=10, decimal_places=2,
                                              null=True, blank=True)
    description        = models.TextField(blank=True, default='')
    status             = models.CharField(max_length=20, blank=True, default='')
    quantity           = models.IntegerField(null=True, blank=True)
    length_km          = models.DecimalField(max_digits=5, decimal_places=2,
                                              null=True, blank=True)
    maintenance_status = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.name


# ============================================================
# INSTITUTION MODEL
# ============================================================
class Institution(models.Model):
    STATUS_CHOICES = [
        ('Active',   'Active'),
        ('Inactive', 'Inactive'),
    ]
    name      = models.CharField(max_length=150)
    president = models.CharField(max_length=100, blank=True, default='')
    members   = models.IntegerField(default=0)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    programs  = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


# ============================================================
# MEDICAL STAFF MODEL
# ============================================================
class MedicalStaff(models.Model):
    POSITION_CHOICES = [
        ('Health Worker', 'Health Worker'),
        ('Nurse',         'Nurse'),
        ('Midwife',       'Midwife'),
        ('Doctor',        'Doctor'),
        ('Dentist',       'Dentist'),
    ]
    name           = models.CharField(max_length=100)
    position       = models.CharField(max_length=50, choices=POSITION_CHOICES,
                                       default='Health Worker')
    contact_number = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.name


# ============================================================
# OTHER PROFESSIONALS MODEL
# ============================================================
class OtherProfessional(models.Model):
    PROFESSION_CHOICES = [
        ('Teacher',     'Teacher'),
        ('Carpenter',   'Carpenter'),
        ('Electrician', 'Electrician'),
        ('Plumber',     'Plumber'),
        ('Farmer',      'Farmer'),
        ('Engineer',    'Engineer'),
        ('Other',       'Other'),
    ]
    name           = models.CharField(max_length=100)
    profession     = models.CharField(max_length=50, choices=PROFESSION_CHOICES,
                                       default='Teacher')
    contact_number = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.name


# ============================================================
# BARANGAY SETTINGS MODEL
# ============================================================
class Settings(models.Model):
    barangay_name = models.CharField(max_length=100, default='Cogon')
    municipality  = models.CharField(max_length=100, blank=True, default='')
    province      = models.CharField(max_length=100, blank=True, default='')
    region        = models.CharField(max_length=100, blank=True, default='')
    vision        = models.TextField(blank=True, default='')
    mission       = models.TextField(blank=True, default='')
    goals         = models.TextField(blank=True, default='')
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.barangay_name

