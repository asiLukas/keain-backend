from django.db import migrations


def clear_cases(apps, schema_editor):
    apps.get_model("build", "Build").objects.update(case=None)
    apps.get_model("build", "Case").objects.all().delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("build", "0015_remove_case_typing_angle_deg_remove_case_weight_g")]
    operations = [migrations.RunPython(clear_cases, noop)]
