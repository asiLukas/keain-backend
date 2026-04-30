from django.db import models


class Switch(models.Model):
    """Mechanical keyboard switch reference data.

    Seeded from analyzer/seed_data/switches.json (~2.5k entries).
    Forces in grams, distances in mm.
    """

    class Type(models.TextChoices):
        LINEAR = "linear", "Linear"
        TACTILE = "tactile", "Tactile"
        CLICKY = "clicky", "Clicky"
        HALL_EFFECT = "hall_effect", "Hall Effect"

    class Mount(models.TextChoices):
        PCB_5_PIN = "pcb_5pin", "PCB (5-pin)"
        PLATE_3_PIN = "plate_3pin", "Plate (3-pin)"

    class Material(models.TextChoices):
        ABS = "abs", "ABS"
        DUPONT_TC308 = "dupont_tc308", "Dupont TC308"
        E1 = "e1", "E1"
        G1 = "g1", "G1"
        GATERON_KS3_MOLD = "gateron_ks3_mold", "Gateron KS3 Mold"
        H1 = "h1", "H1"
        H7 = "h7", "H7"
        HPE = "hpe", "HPE"
        INK = "ink", "INK"
        LY = "ly", "LY"
        M1 = "m1", "M1"
        M3 = "m3", "M3"
        MPE = "mpe", "MPE"
        METAL = "metal", "Metal"
        MODIFIED_PC_UPE_BLEND = "modified_pc_upe_blend", "Modified PC & UPE Blend"
        MYSTERY = "mystery", "Mystery Material"
        NPI = "npi", "NPI"
        NY = "ny", "NY"
        NYLON = "nylon", "Nylon"
        P1 = "p1", "P1"
        P2 = "p2", "P2"
        P3 = "p3", "P3"
        P3_PLUS = "p3_plus", "P3+"
        P4 = "p4", "P4"
        PBT = "pbt", "PBT"
        PC = "pc", "PC"
        PME = "pme", "PME"
        POK = "pok", "POK"
        POM = "pom", "POM"
        POLYMER_NYLON_UHMWPE_AMP = "polymer_nylon_uhmwpe_amp", "Polymer Nylon & UHMWPE Blend"
        POLYMER_NYLON_UHMWPE_AND = "polymer_nylon_uhmwpe_and", "Polymer Nylon and UHMWPE Blend"
        PROPRIETARY = "proprietary", "Proprietary"
        PROPRIETARY_GAZZEW_BLEND = "proprietary_gazzew_blend", "Proprietary Gazzew Blend"
        PROPRIETARY_INK_BLEND = "proprietary_ink_blend", "Proprietary INK Blend"
        PROPRIETARY_KTT_BLEND = "proprietary_ktt_blend", "Proprietary KTT Blend"
        PROPRIETARY_MILKY_BLEND = "proprietary_milky_blend", "Proprietary Milky Blend"
        PROPRIETARY_NIXDORK_BLEND = "proprietary_nixdork_blend", "Proprietary Nixdork Blend"
        PROPRIETARY_POM_BLEND = "proprietary_pom_blend", "Proprietary POM Blend"
        Q1 = "q1", "Q1"
        R1 = "r1", "R1"
        T1 = "t1", "T1"
        T2 = "t2", "T2"
        T3 = "t3", "T3"
        T4 = "t4", "T4"
        T5 = "t5", "T5"
        TPS = "tps", "TPS"
        TEFLON = "teflon", "Teflon"
        UHMWPE = "uhmwpe", "UHMWPE"
        UPE = "upe", "UPE"
        Y1 = "y1", "Y1"
        Y3 = "y3", "Y3"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=16, choices=Type.choices, null=True, blank=True)
    mount_type = models.CharField(max_length=16, choices=Mount.choices, null=True, blank=True)
    top_housing_material = models.CharField(
        max_length=32, choices=Material.choices, null=True, blank=True
    )
    bottom_housing_material = models.CharField(
        max_length=32, choices=Material.choices, null=True, blank=True
    )
    stem_material = models.CharField(max_length=32, choices=Material.choices, null=True, blank=True)
    spring = models.CharField(max_length=128, blank=True, default="")
    actuation_force_g = models.FloatField(null=True, blank=True)
    bottom_out_force_g = models.FloatField(null=True, blank=True)
    pre_travel_mm = models.FloatField(null=True, blank=True)
    total_travel_mm = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "type",
                    "top_housing_material",
                    "bottom_housing_material",
                    "stem_material",
                    "mount_type",
                    "spring",
                ],
                name="unique_switch_variant",
            ),
        ]

    def __str__(self) -> str:
        return self.name
