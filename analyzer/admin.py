from django.contrib import admin

from analyzer.models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "build", "verdict", "created_at")
    list_filter = ("created_at",)
    search_fields = ("created_by__username", "verdict")
    autocomplete_fields = ("created_by", "build")
    readonly_fields = ("created_at", "updated_at")
