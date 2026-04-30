from django.db import migrations


def forward(apps, schema_editor):
    apps.get_model("build", "KeycapSet").objects.filter(manufacturer="").delete()


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("build", "0011_seed_cases_keycaps")]
    operations = [migrations.RunPython(forward, reverse)]
