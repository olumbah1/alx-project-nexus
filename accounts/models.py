import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=False, blank=False)
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    def __str__(self):
        return self.email