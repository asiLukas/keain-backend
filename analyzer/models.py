from django.conf import settings
from django.db import models

from build.models import OwnableQuerySet


class MetricChoice(models.TextChoices):
    THOCK = "THOCK"
    CLACK = "CLACK"
    CREAMINESS = "CREAMINESS"
    PITCH = "PITCH"
    CONSISTENCY = "CONSISTENCY"
    TONAL_BALANCE = "TONAL_BALANCE"
    PEAK_RESONANCE = "PEAK_RESONANCE"
    PURITY = "PURITY"
    PEAK_LOUDNESS = "PEAK_LOUDNESS"
    METALLIC_RESONANCE = "METALLIC_RESONANCE"
    VARIANCE = "VARIANCE"


# Metrics where lower raw value = better.
INVERTED_METRICS = frozenset(
    {
        MetricChoice.PITCH,
        MetricChoice.PEAK_RESONANCE,
        MetricChoice.METALLIC_RESONANCE,
        MetricChoice.VARIANCE,
    }
)


def is_inverted(metric: MetricChoice) -> bool:
    return MetricChoice(metric) in INVERTED_METRICS


class Analysis(models.Model):
    created_by = models.ForeignKey(
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
    thock = models.IntegerField(default=0)
    clack = models.IntegerField(default=0)
    creaminess = models.IntegerField(default=0)
    pitch = models.IntegerField(default=0)
    consistency = models.IntegerField(default=0)
    tonal_balance = models.IntegerField(default=0)
    peak_resonance = models.IntegerField(default=0)
    purity = models.IntegerField(default=0)
    peak_loudness = models.IntegerField(default=0)
    metallic_resonance = models.IntegerField(default=0)
    variance = models.IntegerField(default=0)
    frequency_response = models.JSONField(null=True, blank=True)
    frequency_response_hz = models.JSONField(null=True, blank=True)
    verdict = models.TextField(blank=True, null=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OwnableQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "analyses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "-created_at"]),
            models.Index(fields=["build"]),
        ]

    def __str__(self) -> str:
        return f"Analysis #{self.pk}"
