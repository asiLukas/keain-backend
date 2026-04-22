from django.contrib import admin

from user.models import KeainUser


# Register your models here.
class KeainUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "theme", "is_staff", "is_active")
    list_filter = ("theme", "is_staff", "is_active")
    search_fields = ("username", "email")


admin.site.register(KeainUser, KeainUserAdmin)
