from django.db import models
from django.contrib.auth.models import AbstractUser


# ============================================================
#  🗄️  DATABASE CUSTOMIZATION ZONE
#  Extend the default User model here or add new models below.
#  After any change:  python manage.py makemigrations && migrate
# ============================================================

class User(AbstractUser):
    """
    Custom User model — add extra fields here as your project grows.

    Example fields (uncomment / add what you need):
        barangay   = models.CharField(max_length=100, blank=True)
        role       = models.CharField(max_length=50,
                         choices=[('admin','Admin'),('staff','Staff')],
                         default='staff')
        contact_no = models.CharField(max_length=20, blank=True)
        profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    """

    # ── add your custom fields below this line ──────────────
    # barangay    = models.CharField(max_length=100, blank=True)
    # role        = models.CharField(max_length=50, default='staff')
    # ────────────────────────────────────────────────────────

    class Meta:
        verbose_name = 'Barangay User'
        verbose_name_plural = 'Barangay Users'

    def __str__(self):
        return self.username


# ── Add more models below (e.g. Resident, Blotter, Certificate) ──────────────

# ── Add more models below ──────────────────────────────────────────────────

class Resident(models.Model):
    # The actual data we want to save
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    
    # Adding gender so the dashboard can count them!
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    
    address    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"