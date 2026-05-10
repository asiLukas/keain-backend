from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("build", "0018_alter_keycapset_profile")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="images",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="keycapset",
            name="images",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
