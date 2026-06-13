from django.conf import settings
from django.db import models


class OwnableQuerySet(models.QuerySet):
    """Visibility helper: public (created_by NULL) + own private entries."""

    def visible_to(self, user):
        if user is None or not user.is_authenticated:
            qs = self.filter(created_by__isnull=True)
        else:
            qs = self.filter(models.Q(created_by__isnull=True) | models.Q(created_by=user))
        return qs.alias(
            _owned=models.Case(
                models.When(created_by__isnull=False, then=1),
                default=0,
                output_field=models.IntegerField(),
            )
        ).order_by("-_owned", *(self.model._meta.ordering or []))


class Ownable(models.Model):
    """Mixin: NULL created_by = public/seeded. Non-NULL = private to that user."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )

    objects = OwnableQuerySet.as_manager()

    class Meta:
        abstract = True


class Layout(models.TextChoices):
    """Shared keyboard form-factor across Case/Plate/PCB."""

    LAYOUT_40 = "40", "40%"
    LAYOUT_60 = "60", "60%"
    LAYOUT_65 = "65", "65%"
    LAYOUT_75 = "75", "75%"
    TKL = "tkl", "TKL"
    LAYOUT_1800 = "1800", "1800"
    FULL = "full", "Full Size"
    HHKB = "hhkb", "HHKB"
    ALICE = "alice", "Alice"
    SOUTHPAW = "southpaw", "Southpaw"
    ERGO = "ergo", "Ergo / Split"
    NUMPAD = "numpad", "Numpad"
    MACROPAD = "macropad", "Macropad"


class Switch(Ownable):
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


class Case(Ownable):
    """Keyboard case reference data."""

    class Material(models.TextChoices):
        ALUMINUM = "aluminum", "Aluminum"
        POLYCARBONATE = "polycarbonate", "Polycarbonate"
        BRASS = "brass", "Brass"
        COPPER = "copper", "Copper"
        STEEL = "steel", "Steel"
        TITANIUM = "titanium", "Titanium"
        ACRYLIC = "acrylic", "Acrylic"
        WOOD = "wood", "Wood"
        FR4 = "fr4", "FR4"
        POM = "pom", "POM"
        ABS = "abs", "ABS"
        CARBON_FIBER = "carbon_fiber", "Carbon Fiber"

    class MountStyle(models.TextChoices):
        TRAY = "tray", "Tray Mount"
        TOP = "top", "Top Mount"
        BOTTOM = "bottom", "Bottom Mount"
        GASKET = "gasket", "Gasket Mount"
        INTEGRATED = "integrated", "Integrated Plate"
        SANDWICH = "sandwich", "Sandwich Mount"
        BURGER = "burger", "Burger Mount"
        LEAF_SPRING = "leaf_spring", "Leaf Spring"
        O_RING = "o_ring", "O-Ring Mount"
        PLATELESS = "plateless", "Plateless"
        FORCE_BREAK = "force_break", "Force Break"
        PCB_MOUNT = "pcb_mount", "PCB Mount"

    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=128, blank=True, default="")
    material = models.CharField(max_length=20, choices=Material.choices, null=True, blank=True)
    mount_style = models.CharField(max_length=20, choices=MountStyle.choices, null=True, blank=True)
    layout = models.CharField(max_length=12, choices=Layout.choices, null=True, blank=True)
    images = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["manufacturer", "name"]
        indexes = [
            models.Index(fields=["layout"]),
            models.Index(fields=["mount_style"]),
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["manufacturer", "name", "material", "mount_style", "layout"],
                name="unique_case_variant",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.name}".strip()


class Plate(models.Model):
    """Switch plate."""

    class Material(models.TextChoices):
        FR4 = "fr4", "FR4"
        BRASS = "brass", "Brass"
        ALUMINUM = "aluminum", "Aluminum"
        POLYCARBONATE = "polycarbonate", "Polycarbonate"
        POM = "pom", "POM"
        CARBON_FIBER = "carbon_fiber", "Carbon Fiber"
        PETG = "petg", "PETG"
        COPPER = "copper", "Copper"
        STEEL = "steel", "Steel"
        TITANIUM = "titanium", "Titanium"
        ACRYLIC = "acrylic", "Acrylic"

    material = models.CharField(max_length=20, choices=Material.choices, null=True, blank=True)
    flex_cuts = models.BooleanField(default=False)
    half_plate = models.BooleanField(default=False)

    class Meta:
        ordering = ["material"]
        constraints = [
            models.UniqueConstraint(
                fields=["material", "flex_cuts", "half_plate"],
                name="unique_plate_variant",
            ),
        ]

    def __str__(self) -> str:
        parts = [self.material or "Plate"]
        if self.flex_cuts:
            parts.append("flex-cut")
        if self.half_plate:
            parts.append("half")
        return " ".join(parts)


class PCB(models.Model):
    """Printed circuit board."""

    class RGB(models.TextChoices):
        NONE = "none", "None"
        UNDERGLOW = "underglow", "Underglow"
        PER_KEY = "per_key", "Per-Key"
        BOTH = "both", "Underglow + Per-Key"

    rgb = models.CharField(max_length=12, choices=RGB.choices, default=RGB.NONE)
    hotswap = models.BooleanField(default=False)
    wireless = models.BooleanField(default=False)

    class Meta:
        verbose_name = "PCB"
        verbose_name_plural = "PCBs"
        ordering = ["rgb"]
        constraints = [
            models.UniqueConstraint(
                fields=["rgb", "hotswap", "wireless"],
                name="unique_pcb_variant",
            ),
        ]

    def __str__(self) -> str:
        parts = [f"PCB ({self.rgb})"]
        if self.hotswap:
            parts.append("hotswap")
        if self.wireless:
            parts.append("wireless")
        return " ".join(parts)


class KeycapSet(Ownable):
    """Keycap set."""

    class Profile(models.TextChoices):
        CHERRY = "cherry", "Cherry"
        OEM = "oem", "OEM"
        SA = "sa", "SA"
        MT3 = "mt3", "MT3"
        KAT = "kat", "KAT"
        KAM = "kam", "KAM"
        XDA = "xda", "XDA"
        DSA = "dsa", "DSA"
        MDA = "mda", "MDA"
        DCX = "dcx", "DCX"
        MTNU = "mtnu", "MTNU"
        FLAT = "flat", "Flat"
        CHOC = "choc", "Choc"

    manufacturer = models.CharField(max_length=128, blank=True, default="")
    colorway = models.CharField(max_length=128, blank=True, default="")
    profile = models.CharField(max_length=12, choices=Profile.choices, null=True, blank=True)
    images = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["manufacturer", "colorway"]
        indexes = [
            models.Index(fields=["profile"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["manufacturer", "colorway", "profile"],
                name="unique_keycap_variant",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.colorway}".strip()


class Stabilizer(Ownable):
    """Stabilizer set."""

    class MountType(models.TextChoices):
        PCB_SCREW_IN = "pcb_screw_in", "PCB Screw-In"
        PCB_SNAP_IN = "pcb_snap_in", "PCB Snap-In"
        PLATE_MOUNT = "plate_mount", "Plate Mount"

    name = models.CharField(max_length=128, blank=True, default="")
    mount_type = models.CharField(max_length=20, choices=MountType.choices, null=True, blank=True)

    class Meta:
        ordering = ["name", "mount_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "mount_type"],
                name="unique_stabilizer_variant",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.mount_type or ''}".strip()


class Build(models.Model):
    """User keyboard build — links components."""

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="builds",
    )
    case = models.ForeignKey(
        Case, on_delete=models.PROTECT, null=True, blank=True, related_name="builds"
    )
    plate = models.ForeignKey(
        Plate, on_delete=models.PROTECT, null=True, blank=True, related_name="builds"
    )
    pcb = models.ForeignKey(
        PCB, on_delete=models.PROTECT, null=True, blank=True, related_name="builds"
    )
    keycap_set = models.ForeignKey(
        KeycapSet,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="builds",
    )
    stabilizer = models.ForeignKey(
        Stabilizer,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="builds",
    )
    switch = models.ForeignKey(Switch, on_delete=models.PROTECT, related_name="builds")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    version = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk:
            current = Build.objects.only("version").get(pk=self.pk).version
            self.version = current + 1
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["owner", "-updated_at"])]

    def __str__(self) -> str:
        return self.name
