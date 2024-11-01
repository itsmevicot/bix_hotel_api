import re

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import EmailValidator
from django.db import models
from localflavor.br.models import BRCPFField

from users.enums import UserRole
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid email address.")],
        error_messages={'unique': "A user with this email already exists."}
    )
    cpf = BRCPFField(
        max_length=11,
        unique=True,
        error_messages={'unique': "A user with this CPF already exists."}
    )
    birth_date = models.DateField()
    role = models.CharField(max_length=20, choices=UserRole.choices(), default=UserRole.CLIENT.value)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cpf', 'birth_date']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    def clean(self):
        self.cpf = re.sub(r'[.-]', '', self.cpf)
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
