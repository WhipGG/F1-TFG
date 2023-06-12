from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import RedirectView

import requests
import datetime

from .update_ergast import update_database, update_learning_dataset
from .populateDB import populate_drivers, populate_constructors, populate_circuits
from .forms import Prediction, process_prediction_form
from .predictions import predict
from .models import Driver, Circuit
from .charts import ChartFactory


def index(request):
    response = requests.get('http://ergast.com/api/f1/current/next.json')
    data = response.json()
    next_race = data['MRData']['RaceTable']['Races'][0]
    race_name = next_race['raceName']
    circuit = Circuit.objects.filter(circuitRef=next_race['Circuit']['circuitId'])[0]
    circuit_layout = circuit.layout.url
    start_date = datetime.datetime.strptime(next_race['FirstPractice']['date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(next_race['date'], '%Y-%m-%d')
    if start_date.month==end_date.month:
        dates = str(start_date.day) + ' - ' + str(end_date.day) + ' ' + end_date.strftime('%b').lower()
    else:
        dates = str(start_date.day) + ' ' + start_date.strftime('%b').lower() + ' - ' + str(end_date.day) + ' ' + end_date.strftime('%b').lower()
    return render(request, 'f1dataapp/index.html', {'raceName':race_name, 'layout':circuit_layout, 'dates':dates})


def predictions(request):
    if request.method == "POST":
        form = Prediction(request.POST)
        if form.is_valid():
            driverIds, strating_pos = process_prediction_form(form)
            if strating_pos==False:
                return render(request, 'f1dataapp/predictions.html', {'form': form, 'error':driverIds})
            
            weather={'weather_warm':int(form.cleaned_data['warm']),
                     'weather_cold':int(form.cleaned_data['cold']),
                     'weather_dry':int(form.cleaned_data['dry']),
                     'weather_wet':int(form.cleaned_data['wet']),
                     'weather_cloudy':int(form.cleaned_data['cloudy'])}
            grid = {'driverId':driverIds, 'grid':strating_pos}
            pred_results = list(predict(grid, weather=weather)['driverId'])
            driver_results = [Driver.objects.filter(driverId=pred)[0] for pred in pred_results]
            return render(request, 'f1dataapp/predictions.html', {'form': form, 'prediction':driver_results})
    form = Prediction()
    return render(request, 'f1dataapp/predictions.html', {'form': form})


def latest_results(request):
    chart_q = ChartFactory.generate_times('Q')
    chart_r = ChartFactory.generate_times('R')
    table_data = ChartFactory.generate_table()
    return render(request, 'f1dataapp/latest_results.html', {'chart_q': chart_q, 'chart_r': chart_r, 'table': table_data})





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