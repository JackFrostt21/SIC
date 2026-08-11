from django.contrib import admin

from unfold.admin import ModelAdmin

from apps.fleet.models import Geozone, Vehicle, VehicleMorningGeozone


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    list_display = (
        "plate_number",
        "name",
        "is_active",
        "is_subject_to_inspection",
        "omnicomm_vehicle_id",
        "terminal_id",
        "updated_at",
    )
    search_fields = ("plate_number", "name")
    list_filter = ("is_active", "is_subject_to_inspection")
    ordering = ("plate_number",)


@admin.register(Geozone)
class GeozoneAdmin(ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "is_used_in_matrix",
        "omnicomm_id",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("is_active", "is_used_in_matrix")
    ordering = ("name",)


@admin.register(VehicleMorningGeozone)
class VehicleMorningGeozoneAdmin(ModelAdmin):
    list_display = (
        "date",
        "vehicle",
        "geozone",
        "status",
        "duration_seconds",
        "source",
        "synced_at",
    )
    list_filter = ("date", "status", "geozone")
    search_fields = ("vehicle__plate_number", "geozone__name")
    autocomplete_fields = ("vehicle", "geozone")
    ordering = ("-date", "vehicle__plate_number")
