from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    ROLE_CLIENT = 'client'
    ROLE_STAFF = 'staff'
    ROLE_MANAGER = 'manager'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Client'),
        (ROLE_STAFF, 'Staff'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CLIENT)

    groups = models.ManyToManyField(
        Group,
        related_name="user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="user_permissions",
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
