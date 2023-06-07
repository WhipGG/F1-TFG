from django.contrib import admin
from .models import Driver, Constructor, Circuit, Grid

# Register your models here.

class DriverAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class ConstructorAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class CircuitAdmin(admin.ModelAdmin):
    search_fields = ["name", "location", "country"]

admin.site.register(Driver, DriverAdmin)
admin.site.register(Constructor, ConstructorAdmin)
admin.site.register(Circuit, CircuitAdmin)
admin.site.register(Grid)