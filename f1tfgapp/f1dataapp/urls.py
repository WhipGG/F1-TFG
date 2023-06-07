from django.urls import path

from . import views


app_name = "f1dataapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("predictions", views.predictions, name="predictions"),
    # Admin form management
    path("update_ergast", views.update_ergast, name="update_ergast"),
    path("update_dataset", views.update_dataset, name="update_dataset"),
]