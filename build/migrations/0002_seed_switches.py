import json
from pathlib import Path

from django.db import migrations

SEED_FILE = Path(__file__).resolve().parent.parent / "seed_data" / "switches.json"

TYPE_MAP = {
    "Linear": "linear",
    "Tactile": "tactile",
    "Clicky": "clicky",
    "Hall Effect": "hall_effect",
}

MOUNT_MAP = {
    "PCB (5-pin)": "pcb_5pin",
    "Plate (3-pin)": "plate_3pin",
}

MATERIAL_MAP = {
    "ABS": "abs",
    "Dupont TC308": "dupont_tc308",
    "E1": "e1",
    "G1": "g1",
    "Gateron KS3 Mold": "gateron_ks3_mold",
    "H1": "h1",
    "H7": "h7",
    "HPE": "hpe",
    "INK": "ink",
    "LY": "ly",
    "M1": "m1",
    "M3": "m3",
    "MPE": "mpe",
    "Metal": "metal",
    "Modified PC & UPE Blend": "modified_pc_upe_blend",
    "Mystery Material": "mystery",
    "NPI": "npi",
    "NY": "ny",
    "Nylon": "nylon",
    "P1": "p1",
    "P2": "p2",
    "P3": "p3",
    "P3+": "p3_plus",
    "P4": "p4",
    "PBT": "pbt",
    "PC": "pc",
    "PME": "pme",
    "POK": "pok",
    "POM": "pom",
    "Polymer Nylon & UHMWPE Blend": "polymer_nylon_uhmwpe_amp",
    "Polymer Nylon and UHMWPE Blend": "polymer_nylon_uhmwpe_and",
    "Proprietary": "proprietary",
    "Proprietary Gazzew Blend": "proprietary_gazzew_blend",
    "Proprietary INK Blend": "proprietary_ink_blend",
    "Proprietary KTT Blend": "proprietary_ktt_blend",
    "Proprietary Milky Blend": "proprietary_milky_blend",
    "Proprietary Nixdork Blend": "proprietary_nixdork_blend",
    "Proprietary POM Blend": "proprietary_pom_blend",
    "Q1": "q1",
    "R1": "r1",
    "T1": "t1",
    "T2": "t2",
    "T3": "t3",
    "T4": "t4",
    "T5": "t5",
    "TPS": "tps",
    "Teflon": "teflon",
    "UHMWPE": "uhmwpe",
    "UPE": "upe",
    "Y1": "y1",
    "Y3": "y3",
}


def _opt(value, mapping):
    if not value:
        return None
    return mapping[value]


def seed(apps, schema_editor):
    Switch = apps.get_model("build", "Switch")
    raw = json.loads(SEED_FILE.read_text())
    objs = [
        Switch(
            name=row["name"],
            type=_opt(row["type"], TYPE_MAP),
            mount_type=_opt(row["mount_type"], MOUNT_MAP),
            top_housing_material=_opt(row["top_housing_material"], MATERIAL_MAP),
            bottom_housing_material=_opt(row["bottom_housing_material"], MATERIAL_MAP),
            stem_material=_opt(row["stem_material"], MATERIAL_MAP),
            spring=row["spring"] or "",
            actuation_force_g=row["actuation_force_g"],
            bottom_out_force_g=row["bottom_out_force_g"],
            pre_travel_mm=row["pre_travel_mm"],
            total_travel_mm=row["total_travel_mm"],
        )
        for row in raw
    ]
    Switch.objects.bulk_create(objs, batch_size=500, ignore_conflicts=True)


def unseed(apps, schema_editor):
    apps.get_model("build", "Switch").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("build", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
