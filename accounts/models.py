from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        PUBLIC='public','public user'
        RESCUER='rescuer', 'Rescuer'
        SHELTER='shelter','Shelter'
        ADMIN='admin','Admin'
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PUBLIC)
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)


# Create your models here.
