import strawberry
import strawberry_django

from build.models import (
    Build,
    Case,
    KeycapSet,
    PCB,
    Plate,
    Stabilizer,
    Switch,
)


@strawberry_django.type(Switch)
class SwitchType:
    id: strawberry.auto
    name: strawberry.auto
    type: strawberry.auto
    mount_type: strawberry.auto
    top_housing_material: strawberry.auto
    bottom_housing_material: strawberry.auto
    stem_material: strawberry.auto
    spring: strawberry.auto
    actuation_force_g: strawberry.auto
    bottom_out_force_g: strawberry.auto
    pre_travel_mm: strawberry.auto
    total_travel_mm: strawberry.auto


@strawberry_django.type(Case)
class CaseType:
    id: strawberry.auto
    name: strawberry.auto
    manufacturer: strawberry.auto
    material: strawberry.auto
    mount_style: strawberry.auto
    layout: strawberry.auto


@strawberry_django.type(Plate)
class PlateType:
    id: strawberry.auto
    material: strawberry.auto
    flex_cuts: strawberry.auto
    half_plate: strawberry.auto


@strawberry_django.type(PCB)
class PCBType:
    id: strawberry.auto
    rgb: strawberry.auto
    hotswap: strawberry.auto
    wireless: strawberry.auto


@strawberry_django.type(KeycapSet)
class KeycapSetType:
    id: strawberry.auto
    manufacturer: strawberry.auto
    colorway: strawberry.auto
    profile: strawberry.auto


@strawberry_django.type(Stabilizer)
class StabilizerType:
    id: strawberry.auto
    manufacturer: strawberry.auto
    mount_type: strawberry.auto


@strawberry_django.type(Build)
class BuildType:
    id: strawberry.auto
    name: strawberry.auto
    notes: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    case: CaseType | None
    plate: PlateType | None
    pcb: PCBType | None
    keycap_set: KeycapSetType | None
    stabilizer: StabilizerType | None
    switch: SwitchType
