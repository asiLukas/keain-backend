from django.contrib.auth.models import AbstractUser
from django.db import models

from analyzer.models import MetricChoice


class KeainUser(AbstractUser):
    class AppTheme(models.TextChoices):
        LIGHT = "LIGHT"
        DARK = "DARK"

    theme = models.CharField(max_length=10, default=AppTheme.LIGHT, choices=AppTheme.choices)
    primary_metric = models.CharField(choices=MetricChoice.choices, default=MetricChoice.THOCK)
    secondary_metric = models.CharField(choices=MetricChoice.choices, default=MetricChoice.PURITY)

    def __str__(self):
        return f"{self.username} ({self.email})"
