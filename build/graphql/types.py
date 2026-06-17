import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from analyzer.graphql.filters import AnalysisFilter
from analyzer.graphql.orders import AnalysisOrder
from analyzer.graphql.types import AnalysisType
from build.graphql.enums import (
    CaseMaterialEnum,
    CaseMountStyleEnum,
    KeycapProfileEnum,
    LayoutEnum,
    PCBRgbEnum,
    PlateMaterialEnum,
    StabilizerMountEnum,
    SwitchMaterialEnum,
    SwitchMountEnum,
    SwitchTypeEnum,
)
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
    type: SwitchTypeEnum | None
    mount_type: SwitchMountEnum | None
    top_housing_material: SwitchMaterialEnum | None
    bottom_housing_material: SwitchMaterialEnum | None
    stem_material: SwitchMaterialEnum | None
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
    material: CaseMaterialEnum | None
    mount_style: CaseMountStyleEnum | None
    layout: LayoutEnum | None


@strawberry_django.type(Plate)
class PlateType:
    id: strawberry.auto
    material: PlateMaterialEnum | None
    flex_cuts: strawberry.auto
    half_plate: strawberry.auto


@strawberry_django.type(PCB)
class PCBType:
    id: strawberry.auto
    rgb: PCBRgbEnum
    hotswap: strawberry.auto
    wireless: strawberry.auto


@strawberry_django.type(KeycapSet)
class KeycapSetType:
    id: strawberry.auto
    manufacturer: strawberry.auto
    colorway: strawberry.auto
    profile: KeycapProfileEnum | None


@strawberry_django.type(Stabilizer)
class StabilizerType:
    id: strawberry.auto
    name: strawberry.auto
    mount_type: StabilizerMountEnum | None


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
    layout: LayoutEnum | None

    version: strawberry.auto

    analyses: OffsetPaginated[AnalysisType] = strawberry_django.offset_paginated(
        filters=AnalysisFilter, order=AnalysisOrder
    )

    @strawberry_django.field
    def analyses_count(self) -> int:
        return getattr(self, "_analyses_count", None) or 0

    @strawberry_django.field
    def best_primary(self) -> int:
        return int(getattr(self, "_best_primary", None) or 0)

    @strawberry_django.field
    def best_secondary(self) -> int:
        return int(getattr(self, "_best_secondary", None) or 0)
