import strawberry

from build.models import (
    Case,
    KeycapSet,
    Layout,
    PCB,
    Plate,
    Stabilizer,
    Switch,
)


SwitchTypeEnum = strawberry.enum(Switch.Type, name="SwitchTypeEnum")
SwitchMountEnum = strawberry.enum(Switch.Mount, name="SwitchMountEnum")
SwitchMaterialEnum = strawberry.enum(Switch.Material, name="SwitchMaterialEnum")

CaseMaterialEnum = strawberry.enum(Case.Material, name="CaseMaterialEnum")
CaseMountStyleEnum = strawberry.enum(Case.MountStyle, name="CaseMountStyleEnum")

LayoutEnum = strawberry.enum(Layout, name="LayoutEnum")

KeycapProfileEnum = strawberry.enum(KeycapSet.Profile, name="KeycapProfileEnum")

PlateMaterialEnum = strawberry.enum(Plate.Material, name="PlateMaterialEnum")

PCBRgbEnum = strawberry.enum(PCB.RGB, name="PCBRgbEnum")

StabilizerMountEnum = strawberry.enum(Stabilizer.MountType, name="StabilizerMountEnum")
