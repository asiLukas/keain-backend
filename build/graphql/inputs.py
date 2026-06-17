import strawberry
import strawberry_django

from build.graphql.enums import (
    CaseMaterialEnum,
    CaseMountStyleEnum,
    KeycapProfileEnum,
    LayoutEnum,
    StabilizerMountEnum,
    SwitchMaterialEnum,
    SwitchMountEnum,
    SwitchTypeEnum,
)
from build.models import (
    Build,
    Case,
    KeycapSet,
    Stabilizer,
    Switch,
)


# Switch (Ownable)
@strawberry_django.input(Switch, exclude=["created_by", "id"])
class SwitchCreateInput:
    type: SwitchTypeEnum | None = strawberry.UNSET
    mount_type: SwitchMountEnum | None = strawberry.UNSET
    top_housing_material: SwitchMaterialEnum | None = strawberry.UNSET
    bottom_housing_material: SwitchMaterialEnum | None = strawberry.UNSET
    stem_material: SwitchMaterialEnum | None = strawberry.UNSET


@strawberry_django.partial(Switch, exclude=["created_by"])
class SwitchUpdateInput:
    id: strawberry.ID
    type: SwitchTypeEnum | None = strawberry.UNSET
    mount_type: SwitchMountEnum | None = strawberry.UNSET
    top_housing_material: SwitchMaterialEnum | None = strawberry.UNSET
    bottom_housing_material: SwitchMaterialEnum | None = strawberry.UNSET
    stem_material: SwitchMaterialEnum | None = strawberry.UNSET


# Case (Ownable)
@strawberry_django.input(Case, exclude=["created_by", "id"])
class CaseCreateInput:
    material: CaseMaterialEnum | None = strawberry.UNSET
    mount_style: CaseMountStyleEnum | None = strawberry.UNSET
    layout: LayoutEnum | None = strawberry.UNSET


@strawberry_django.partial(Case, exclude=["created_by"])
class CaseUpdateInput:
    id: strawberry.ID
    material: CaseMaterialEnum | None = strawberry.UNSET
    mount_style: CaseMountStyleEnum | None = strawberry.UNSET
    layout: LayoutEnum | None = strawberry.UNSET


# KeycapSet (Ownable)
@strawberry_django.input(KeycapSet, exclude=["created_by", "id"])
class KeycapSetCreateInput:
    profile: KeycapProfileEnum | None = strawberry.UNSET


@strawberry_django.partial(KeycapSet, exclude=["created_by"])
class KeycapSetUpdateInput:
    id: strawberry.ID
    profile: KeycapProfileEnum | None = strawberry.UNSET


# Stabilizer (Ownable)
@strawberry_django.input(Stabilizer, exclude=["created_by", "id"])
class StabilizerCreateInput:
    mount_type: StabilizerMountEnum | None = strawberry.UNSET


@strawberry_django.partial(Stabilizer, exclude=["created_by"])
class StabilizerUpdateInput:
    id: strawberry.ID
    mount_type: StabilizerMountEnum | None = strawberry.UNSET


# Build (owner, not created_by)
@strawberry_django.input(
    Build,
    exclude=["owner", "id", "case", "plate", "pcb", "keycap_set", "stabilizer", "switch"],
)
class BuildCreateInput:
    case_id: strawberry.ID | None = strawberry.UNSET
    plate_id: strawberry.ID | None = strawberry.UNSET
    pcb_id: strawberry.ID | None = strawberry.UNSET
    keycap_set_id: strawberry.ID | None = strawberry.UNSET
    stabilizer_id: strawberry.ID | None = strawberry.UNSET
    switch_id: strawberry.ID
    layout: LayoutEnum | None = strawberry.UNSET


@strawberry_django.partial(
    Build,
    exclude=["owner", "case", "plate", "pcb", "keycap_set", "stabilizer", "switch"],
)
class BuildUpdateInput:
    id: strawberry.ID
    case_id: strawberry.ID | None = strawberry.UNSET
    plate_id: strawberry.ID | None = strawberry.UNSET
    pcb_id: strawberry.ID | None = strawberry.UNSET
    keycap_set_id: strawberry.ID | None = strawberry.UNSET
    stabilizer_id: strawberry.ID | None = strawberry.UNSET
    switch_id: strawberry.ID | None = strawberry.UNSET
    layout: LayoutEnum | None = strawberry.UNSET
