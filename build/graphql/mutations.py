from graphql import GraphQLError
import strawberry
from strawberry.types.info import Info

from build.graphql.inputs import (
    BuildCreateInput,
    BuildUpdateInput,
    CaseCreateInput,
    CaseUpdateInput,
    KeycapSetCreateInput,
    KeycapSetUpdateInput,
    StabilizerCreateInput,
    StabilizerUpdateInput,
    SwitchCreateInput,
    SwitchUpdateInput,
)
from build.graphql.types import (
    BuildType,
    CaseType,
    KeycapSetType,
    StabilizerType,
    SwitchType,
)
from build.models import Build, Case, KeycapSet, Stabilizer, Switch
from core.error_codes import NOT_FOUND, err
from core.permissions import IsAuthenticated
from core.utils import get_user_from_info


def _clean(data):
    return {k: v for k, v in vars(data).items() if v is not strawberry.UNSET}


def _ownable_update(model, pk, user, data):
    obj = model.objects.filter(pk=pk, created_by=user).first()
    if not obj:
        raise GraphQLError("Not found", extensions=err(NOT_FOUND))
    for k, v in vars(data).items():
        if k != "id" and v is not strawberry.UNSET:
            setattr(obj, k, v)
    obj.save()
    return obj


def _ownable_delete(model, pk, user) -> bool:
    n, _ = model.objects.filter(pk=pk, created_by=user).delete()
    return n > 0


@strawberry.type
class BuildMutation:
    # Switch
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_switch(self, info: Info, input: SwitchCreateInput) -> SwitchType:
        return Switch.objects.create(created_by=get_user_from_info(info), **_clean(input))

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_switch(self, info: Info, input: SwitchUpdateInput) -> SwitchType:
        return _ownable_update(Switch, input.id, get_user_from_info(info), input)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_switch(self, info: Info, id: strawberry.ID) -> bool:
        return _ownable_delete(Switch, id, get_user_from_info(info))

    # Case
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_case(self, info: Info, input: CaseCreateInput) -> CaseType:
        return Case.objects.create(created_by=get_user_from_info(info), **_clean(input))

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_case(self, info: Info, input: CaseUpdateInput) -> CaseType:
        return _ownable_update(Case, input.id, get_user_from_info(info), input)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_case(self, info: Info, id: strawberry.ID) -> bool:
        return _ownable_delete(Case, id, get_user_from_info(info))

    # KeycapSet
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_keycap_set(self, info: Info, input: KeycapSetCreateInput) -> KeycapSetType:
        return KeycapSet.objects.create(created_by=get_user_from_info(info), **_clean(input))

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_keycap_set(self, info: Info, input: KeycapSetUpdateInput) -> KeycapSetType:
        return _ownable_update(KeycapSet, input.id, get_user_from_info(info), input)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_keycap_set(self, info: Info, id: strawberry.ID) -> bool:
        return _ownable_delete(KeycapSet, id, get_user_from_info(info))

    # Stabilizer
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_stabilizer(self, info: Info, input: StabilizerCreateInput) -> StabilizerType:
        return Stabilizer.objects.create(created_by=get_user_from_info(info), **_clean(input))

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_stabilizer(self, info: Info, input: StabilizerUpdateInput) -> StabilizerType:
        return _ownable_update(Stabilizer, input.id, get_user_from_info(info), input)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_stabilizer(self, info: Info, id: strawberry.ID) -> bool:
        return _ownable_delete(Stabilizer, id, get_user_from_info(info))

    # Build (owner, not created_by)
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_build(self, info: Info, input: BuildCreateInput) -> BuildType:
        return Build.objects.create(owner=get_user_from_info(info), **_clean(input))

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_build(self, info: Info, input: BuildUpdateInput) -> BuildType:
        user = get_user_from_info(info)
        obj = Build.objects.filter(pk=input.id, owner=user).first()
        if not obj:
            raise GraphQLError("Not found", extensions=err(NOT_FOUND))
        for k, v in vars(input).items():
            if k != "id" and v is not strawberry.UNSET:
                setattr(obj, k, v)
        obj.save()
        return obj

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_build(self, info: Info, id: strawberry.ID) -> bool:
        n, _ = Build.objects.filter(pk=id, owner=get_user_from_info(info)).delete()
        return n > 0
