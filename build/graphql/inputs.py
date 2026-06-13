import strawberry
import strawberry_django

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
    pass


@strawberry_django.partial(Switch, exclude=["created_by"])
class SwitchUpdateInput:
    id: strawberry.ID


# Case (Ownable)
@strawberry_django.input(Case, exclude=["created_by", "id"])
class CaseCreateInput:
    pass


@strawberry_django.partial(Case, exclude=["created_by"])
class CaseUpdateInput:
    id: strawberry.ID


# KeycapSet (Ownable)
@strawberry_django.input(KeycapSet, exclude=["created_by", "id"])
class KeycapSetCreateInput:
    pass


@strawberry_django.partial(KeycapSet, exclude=["created_by"])
class KeycapSetUpdateInput:
    id: strawberry.ID


# Stabilizer (Ownable)
@strawberry_django.input(Stabilizer, exclude=["created_by", "id"])
class StabilizerCreateInput:
    pass


@strawberry_django.partial(Stabilizer, exclude=["created_by"])
class StabilizerUpdateInput:
    id: strawberry.ID


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
