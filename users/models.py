import uuid
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone
from rest_framework.authtoken.models import Token

# Create your models here.

class UserManager(BaseUserManager):

    def _create_user(self, id, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not id:
            raise ValueError('The given id must be set')

        user = self.model(id=id, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, id, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(id, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, **extra_fields)


class AnonUser(models.Model):
    id = models.IntegerField(primary_key=True)
    last_login = models.DateTimeField('last login', blank=True, null=True)
    USERNAME_FIELD = "id"
    objects = UserManager()


class CustomToken(Token):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey("AnonUser", on_delete=models.CASCADE)

    def is_fresh(self):
        return self.created + timedelta(days=3) > timezone.now()

    def __str__(self):
        return f"Token of {self.user.id}"
