import json
from pathlib import Path

from django.db import migrations

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_data"


def seed(apps, schema_editor):
    KeycapSet = apps.get_model("build", "KeycapSet")
    keycaps = json.loads((SEED_DIR / "keycaps.json").read_text())
    KeycapSet.objects.bulk_create(
        [KeycapSet(**k) for k in keycaps],
        ignore_conflicts=True,
        batch_size=500,
    )


def unseed(apps, schema_editor):
    apps.get_model("build", "KeycapSet").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("build", "0010_seed_stabilizers")]
    operations = [migrations.RunPython(seed, unseed)]
