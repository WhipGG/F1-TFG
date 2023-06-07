from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import RedirectView

from .update_ergast import update_database, update_learning_dataset
from .populateDB import populate_drivers, populate_constructors, populate_circuits


def index(request):
    return render(request, 'f1dataapp/index.html')


def predictions(request):
    return render(request, 'f1dataapp/predictions.html')





# Admin - data management views. These views manage update forms.
def update_ergast(request):
    update_database()
    return redirect("/admin")

def update_dataset(request):
    update_learning_dataset()
    return redirect("/admin")


# Admin - database management. These views reset the SQL database.
def reset_drivers(request):
    populate_drivers()
    return redirect("/admin")

def reset_constructors(request):
    populate_constructors()
    return redirect("/admin")

def reset_circuits(request):
    populate_circuits()
    return redirect("/admin")