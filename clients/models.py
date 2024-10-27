from django.db import models

from authentication.models import User


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Client: {self.user.username}"
