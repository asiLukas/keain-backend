from django.db import migrations

STABILIZERS = [
    ("Cherry", "pcb_snap_in"),
    ("Cherry", "plate_mount"),
    ("Costar", "plate_mount"),
    ("Durock V1", "pcb_screw_in"),
    ("Durock V2", "pcb_screw_in"),
    ("C³ Equalz", "pcb_screw_in"),
    ("Everglide Panda", "pcb_screw_in"),
    ("Everglide EV", "pcb_screw_in"),
    ("Everglide AV4", "pcb_screw_in"),
    ("GMK Screw-In", "pcb_screw_in"),
    ("Owlstabs V1", "pcb_screw_in"),
    ("Owlstabs V2", "pcb_screw_in"),
    ("TX AP", "pcb_screw_in"),
    ("TX Rev3", "pcb_screw_in"),
    ("TX Rev4", "pcb_screw_in"),
    ("Gateron", "pcb_screw_in"),
    ("Gateron", "pcb_snap_in"),
    ("ZealPC", "pcb_screw_in"),
    ("KTT", "pcb_screw_in"),
    ("Staebies V2", "pcb_screw_in"),
    ("Wuque WS", "pcb_screw_in"),
    ("Cannonkeys C³", "pcb_screw_in"),
]


def seed(apps, schema_editor):
    Stabilizer = apps.get_model("build", "Stabilizer")
    Stabilizer.objects.bulk_create(
        [Stabilizer(manufacturer=m, mount_type=mt) for m, mt in STABILIZERS],
        ignore_conflicts=True,
    )


def unseed(apps, schema_editor):
    apps.get_model("build", "Stabilizer").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("build", "0009_seed_plate_pcb")]
    operations = [migrations.RunPython(seed, unseed)]
