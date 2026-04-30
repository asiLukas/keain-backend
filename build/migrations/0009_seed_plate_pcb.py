from itertools import product

from django.db import migrations

PLATE_MATERIALS = [
    "fr4",
    "brass",
    "aluminum",
    "polycarbonate",
    "pom",
    "carbon_fiber",
    "petg",
    "copper",
    "steel",
    "titanium",
    "acrylic",
]

PCB_RGB = ["none", "underglow", "per_key", "both"]


def seed(apps, schema_editor):
    Plate = apps.get_model("build", "Plate")
    PCB = apps.get_model("build", "PCB")

    plates = [
        Plate(material=m, flex_cuts=fc, half_plate=hp)
        for m, fc, hp in product(PLATE_MATERIALS, [False, True], [False, True])
    ]
    Plate.objects.bulk_create(plates, ignore_conflicts=True)

    pcbs = [
        PCB(rgb=r, hotswap=hs, wireless=w)
        for r, hs, w in product(PCB_RGB, [False, True], [False, True])
    ]
    PCB.objects.bulk_create(pcbs, ignore_conflicts=True)


def unseed(apps, schema_editor):
    apps.get_model("build", "Plate").objects.all().delete()
    apps.get_model("build", "PCB").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("build", "0008_alter_stabilizer_options_and_more")]
    operations = [migrations.RunPython(seed, unseed)]
