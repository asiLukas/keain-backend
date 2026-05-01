from typing import Optional

import strawberry
from graphql import GraphQLError
from strawberry.types.info import Info

from build.models import (
    Build,
    Case,
    KeycapSet,
    PCB,
    Plate,
    Stabilizer,
    Switch,
)
from core.permissions import IsAuthenticated

from .types import (
    BuildType,
    CaseType,
    KeycapSetType,
    PCBType,
    PlateType,
    StabilizerType,
    SwitchType,
)


# TODO move to project wide utils, or create some decorator idk
def _user(info: Info):
    return info.context.get("user")


@strawberry.type
class BuildQuery:
    @strawberry.field
    def switches(self, info: Info) -> list[SwitchType]:
        return Switch.objects.visible_to(_user(info))

    @strawberry.field
    def switch(self, info: Info, id: strawberry.ID) -> Optional[SwitchType]:
        return Switch.objects.visible_to(_user(info)).filter(pk=id).first()

    @strawberry.field
    def cases(self, info: Info) -> list[CaseType]:
        return Case.objects.visible_to(_user(info))

    @strawberry.field
    def case(self, info: Info, id: strawberry.ID) -> Optional[CaseType]:
        return Case.objects.visible_to(_user(info)).filter(pk=id).first()

    @strawberry.field
    def keycap_sets(self, info: Info) -> list[KeycapSetType]:
        return KeycapSet.objects.visible_to(_user(info))

    @strawberry.field
    def keycap_set(self, info: Info, id: strawberry.ID) -> Optional[KeycapSetType]:
        return KeycapSet.objects.visible_to(_user(info)).filter(pk=id).first()

    @strawberry.field
    def plates(self, info: Info) -> list[PlateType]:
        return Plate.objects.all()

    @strawberry.field
    def plate(self, info: Info, id: strawberry.ID) -> Optional[PlateType]:
        return Plate.objects.filter(pk=id).first()

    @strawberry.field
    def pcbs(self, info: Info) -> list[PCBType]:
        return PCB.objects.all()

    @strawberry.field
    def pcb(self, info: Info, id: strawberry.ID) -> Optional[PCBType]:
        return PCB.objects.filter(pk=id).first()

    @strawberry.field
    def stabilizers(self, info: Info) -> list[StabilizerType]:
        return Stabilizer.objects.all()

    @strawberry.field
    def stabilizer(self, info: Info, id: strawberry.ID) -> Optional[StabilizerType]:
        return Stabilizer.objects.filter(pk=id).first()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def builds(self, info: Info) -> list[BuildType]:
        return Build.objects.filter(owner=info.context["user"])

    @strawberry.field(permission_classes=[IsAuthenticated])
    def build(self, info: Info, id: strawberry.ID) -> BuildType:
        try:
            return Build.objects.get(pk=id, owner=info.context["user"])
        except Build.DoesNotExist:
            raise GraphQLError("Build not found.", extensions={"code": 404})
