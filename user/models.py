from django.contrib.auth.models import AbstractUser
from django.db import models


class KeainUser(AbstractUser):
    class AppTheme(models.TextChoices):
        LIGHT = "LIGHT"
        DARK = "DARK"

    theme = models.CharField(max_length=10, default=AppTheme.LIGHT, choices=AppTheme.choices)

    def __str__(self):
        return f"{self.username} ({self.email})"
