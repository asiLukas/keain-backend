"""Seed Case + KeycapSet tables from JSON fixtures with images."""
import json
from pathlib import Path

from django.db import migrations

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_data"


def reseed(apps, schema_editor):
    Build = apps.get_model("build", "Build")
    Case = apps.get_model("build", "Case")
    KeycapSet = apps.get_model("build", "KeycapSet")

    Build.objects.update(case=None, keycap_set=None)
    Case.objects.all().delete()
    KeycapSet.objects.all().delete()

    cases = json.loads((SEED_DIR / "cases.json").read_text())
    Case.objects.bulk_create(
        [Case(**c) for c in cases],
        batch_size=500,
    )

    keycaps = json.loads((SEED_DIR / "keycaps.json").read_text())
    KeycapSet.objects.bulk_create(
        [KeycapSet(**k) for k in keycaps],
        batch_size=500,
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("build", "0019_case_keycapset_images")]
    operations = [migrations.RunPython(reseed, noop)]
