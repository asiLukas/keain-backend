from django.contrib import admin

from build.models import (
    Build,
    Case,
    KeycapSet,
    PCB,
    Plate,
    Stabilizer,
    Switch,
)


@admin.register(Switch)
class SwitchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "mount_type",
        "top_housing_material",
        "bottom_housing_material",
        "stem_material",
        "actuation_force_g",
        "bottom_out_force_g",
        "created_by",
    )
    list_filter = (
        "type",
        "mount_type",
        "top_housing_material",
        "bottom_housing_material",
        "stem_material",
        "created_by",
    )
    search_fields = ("name", "spring")
    autocomplete_fields = ("created_by",)
    list_per_page = 50


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "manufacturer",
        "layout",
        "material",
        "mount_style",
        "created_by",
    )
    list_filter = ("layout", "material", "mount_style", "created_by")
    search_fields = ("name", "manufacturer")
    autocomplete_fields = ("created_by",)


@admin.register(Plate)
class PlateAdmin(admin.ModelAdmin):
    list_display = ("material", "flex_cuts", "half_plate")
    list_filter = ("material", "flex_cuts", "half_plate")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PCB)
class PCBAdmin(admin.ModelAdmin):
    list_display = ("rgb", "hotswap", "wireless")
    list_filter = ("rgb", "hotswap", "wireless")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(KeycapSet)
class KeycapSetAdmin(admin.ModelAdmin):
    list_display = (
        "manufacturer",
        "colorway",
        "profile",
        "created_by",
    )
    list_filter = ("profile", "created_by")
    search_fields = ("manufacturer", "colorway")
    autocomplete_fields = ("created_by",)


@admin.register(Stabilizer)
class StabilizerAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "mount_type")
    list_filter = ("mount_type",)
    search_fields = ("manufacturer",)


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "switch",
        "case",
        "plate",
        "pcb",
        "keycap_set",
        "stabilizer",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "owner__username", "notes")
    autocomplete_fields = (
        "owner",
        "case",
        "keycap_set",
        "stabilizer",
        "switch",
    )
    readonly_fields = ("created_at", "updated_at")
