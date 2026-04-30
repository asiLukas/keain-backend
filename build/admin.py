from django.contrib import admin

from build.models import Switch

# Register your models here.


class BuildAdmin(admin.ModelAdmin):
    pass


admin.site.register(Switch, BuildAdmin)
