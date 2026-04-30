from django.contrib import admin

from analyzer.models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "build", "verdict", "created_at")
    list_filter = ("created_at",)
    search_fields = ("owner__username", "verdict")
    autocomplete_fields = ("owner", "build")
    readonly_fields = ("created_at", "updated_at")
