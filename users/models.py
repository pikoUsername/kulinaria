from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    objects = CustomUserManager()

    def __str__(self):
        return self.email
