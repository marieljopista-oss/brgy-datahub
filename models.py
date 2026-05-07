from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


class User(AbstractUser):
    role = models.CharField(max_length=50, default='Captain')
    contact_number = models.CharField(max_length=20, blank=True, default='')


class Resident(models.Model):
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    age = models.IntegerField(default=0)

    gender = models.CharField(max_length=10)
    livelihood = models.CharField(max_length=100, blank=True, default='')
    disability = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.birth_date:
            today = date.today()
            self.age = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
