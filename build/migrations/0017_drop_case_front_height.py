from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("build", "0016_clear_cases_drop_front_height")]
    operations = [
        migrations.RemoveField(model_name="case", name="front_height_mm"),
    ]
