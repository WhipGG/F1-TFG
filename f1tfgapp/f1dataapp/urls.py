from django.urls import path

from . import views


app_name = "f1dataapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("predictions", views.predictions, name="predictions"),
    path("latest_results", views.latest_results, name="latest_results"),
    path("driver_vs_driver_lap", views.driver_vs_driver_lap, name="driver_vs_driver_lap"),
    path("driver_speed_lap", views.telemetry_speed, name="driver_speed_lap"),
    path("tire_stints", views.tyre_stints, name="tire_stints"),
    path("position_changes", views.position_changes, name="position_changes"),
    path("driver_lap_timing", views.driver_lap_timings, name="driver_lap_timing"),
    # Admin form management
    path("update_ergast", views.update_ergast, name="update_ergast"),
    path("update_dataset", views.update_dataset, name="update_dataset"),
    path("populate_drivers", views.reset_drivers, name="populate_drivers"),
    path("populate_constructors", views.reset_constructors, name="populate_constructors"),
    path("populate_circuits", views.reset_circuits, name="populate_circuits"),
]