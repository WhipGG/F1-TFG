from django.contrib import admin
from .models import Driver, Constructor, Circuit, Grid

# Register your models here.

class DriverAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    readonly_fields = ['img_preview']

class ConstructorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    readonly_fields = ['img_preview']

class CircuitAdmin(admin.ModelAdmin):
    search_fields = ["name", "location", "country"]
    readonly_fields = ['img_preview']

class GridAdmin(admin.ModelAdmin):
    list_display = ["driver", "constructor", "driver_photo", "constructor_photo"]


admin.site.register(Driver, DriverAdmin)
admin.site.register(Constructor, ConstructorAdmin)
admin.site.register(Circuit, CircuitAdmin)
admin.site.register(Grid, GridAdmin)