from typing import List, Optional

from django.db.models import Count, Max, Min
import strawberry
from graphql import GraphQLError
from strawberry.types.info import Info
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from analyzer.models import MetricChoice, is_inverted
from build.models import (
    Build,
    Case,
    KeycapSet,
    PCB,
    Plate,
    Stabilizer,
    Switch,
)
from core.error_codes import NOT_FOUND, err
from core.permissions import IsAuthenticated
from core.utils import get_user_from_info


def _builds_for(user):
    prim = MetricChoice(user.primary_metric)
    sec = MetricChoice(user.secondary_metric)
    prim_agg = Min if is_inverted(prim) else Max
    sec_agg = Min if is_inverted(sec) else Max
    return Build.objects.filter(owner=user).annotate(
        _analyses_count=Count("analyses", distinct=True),
        _best_primary=prim_agg(f"analyses__{prim.lower()}"),
        _best_secondary=sec_agg(f"analyses__{sec.lower()}"),
    )

from .types import (
    BuildType,
    CaseType,
    KeycapSetType,
    PCBType,
    PlateType,
    StabilizerType,
    SwitchType,
)


@strawberry.type
class BuildsPaginated(OffsetPaginated[BuildType]):
    @strawberry.field
    def parts_count(self) -> int:
        if self.queryset is None:
            return 0
        agg = self.queryset.aggregate(
            s=Count("switch", distinct=True),
            c=Count("case", distinct=True),
            p=Count("plate", distinct=True),
            pc=Count("pcb", distinct=True),
            k=Count("keycap_set", distinct=True),
            st=Count("stabilizer", distinct=True),
        )
        return sum(v or 0 for v in agg.values())


@strawberry.type
class BuildQuery:
    @strawberry.field
    def switches(self, info: Info) -> list[SwitchType]:
        return Switch.objects.visible_to(get_user_from_info(info))

    @strawberry.field
    def switch(self, info: Info, id: strawberry.ID) -> Optional[SwitchType]:
        return Switch.objects.visible_to(get_user_from_info(info)).filter(pk=id).first()

    @strawberry.field
    def cases(self, info: Info) -> list[CaseType]:
        return Case.objects.visible_to(get_user_from_info(info))

    @strawberry.field
    def case(self, info: Info, id: strawberry.ID) -> Optional[CaseType]:
        return Case.objects.visible_to(get_user_from_info(info)).filter(pk=id).first()

    @strawberry.field
    def keycap_sets(self, info: Info) -> list[KeycapSetType]:
        return KeycapSet.objects.visible_to(get_user_from_info(info))

    @strawberry.field
    def keycap_set(self, info: Info, id: strawberry.ID) -> Optional[KeycapSetType]:
        return KeycapSet.objects.visible_to(get_user_from_info(info)).filter(pk=id).first()

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

    @strawberry_django.offset_paginated(
        BuildsPaginated,
        permission_classes=[IsAuthenticated],
    )
    def builds(self, info: Info) -> List[BuildType]:
        return _builds_for(info.context["user"])

    @strawberry.field(permission_classes=[IsAuthenticated])
    def build(self, info: Info, id: strawberry.ID) -> BuildType:
        try:
            return _builds_for(info.context["user"]).get(pk=id)
        except Build.DoesNotExist:
            raise GraphQLError("Build not found.", extensions=err(NOT_FOUND))
