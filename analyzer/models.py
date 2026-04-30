from django.conf import settings
from django.db import models


class Analysis(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    build = models.ForeignKey(
        "build.Build",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyses",
    )
    audio = models.FileField(upload_to="analyses/", blank=True, null=True)

    message = models.TextField(blank=True, default="")
    thock = models.IntegerField(null=True, blank=True)
    clack = models.IntegerField(null=True, blank=True)
    creaminess = models.IntegerField(null=True, blank=True)
    pitch = models.IntegerField(null=True, blank=True)
    consistency = models.IntegerField(null=True, blank=True)
    tonal_balance = models.IntegerField(null=True, blank=True)
    peak_resonance = models.IntegerField(null=True, blank=True)
    purity = models.IntegerField(null=True, blank=True)
    peak_loudness = models.IntegerField(null=True, blank=True)
    metallic_resonance = models.IntegerField(null=True, blank=True)
    variance = models.IntegerField(null=True, blank=True)
    frequency_response = models.JSONField(null=True, blank=True)
    verdict = models.TextField(blank=True, null=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "analyses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["build"]),
        ]

    def __str__(self) -> str:
        return f"Analysis #{self.pk}"
