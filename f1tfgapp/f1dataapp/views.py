from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import RedirectView

import requests
import datetime

from .update_ergast import update_database, update_learning_dataset
from .populateDB import populate_drivers, populate_constructors, populate_circuits
from .forms import Prediction, process_prediction_form, Driver_vs_Driver_Lap, Driver_Speed_Lap, Tire_Stints, Race_Selector, Driver_Lap_Timing
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
    template = 'f1dataapp/predictions.html'
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
            return render(request, template, {'form': form, 'prediction':driver_results})
    form = Prediction()
    return render(request, template, {'form': form})


def latest_results(request):
    chart_q = ChartFactory.generate_times('Q')
    chart_r = ChartFactory.generate_times('R')
    table_data = ChartFactory.generate_table()
    return render(request, 'f1dataapp/latest_results.html', {'chart_q': chart_q, 'chart_r': chart_r, 'table': table_data})


def driver_vs_driver_lap(request):
    template = 'f1dataapp/driver_vs_driver_lap.html'
    if request.method == "POST":
        form = Driver_vs_Driver_Lap(request.POST)
        if form.is_valid():
            driver_1 = form.cleaned_data['driver_1']
            driver_2 = form.cleaned_data['driver_2']
            circuit = form.cleaned_data['circuit']
            year = int(form.cleaned_data['year'])
            session = form.cleaned_data['session']
            try:
                chart = ChartFactory.generate_VS(year, driver_1.code, driver_2.code, circuit.name, session)
            except:
                return render(request, template, {'form': form, 'error':"Error: Input data does not match any event."})
        return render(request, template, {'form': form, 'chart': chart})
    form = Driver_vs_Driver_Lap()
    return render(request, template, {'form': form})


def telemetry_speed(request):
    template = 'f1dataapp/driver_speed_lap.html'
    if request.method == "POST":
        form = Driver_Speed_Lap(request.POST)
        if form.is_valid():
            driver = form.cleaned_data['driver']
            circuit = form.cleaned_data['circuit']
            year = int(form.cleaned_data['year'])
            session = form.cleaned_data['session']
            try:
                chart_speed = ChartFactory.generate_speed_lap(year, driver.code, circuit.name, session)
                chart_gears = ChartFactory.generate_gears_lap(year, driver.code, circuit.name, session)
            except:
                return render(request, template, {'form': form, 'error':"Error: Input data does not match any event."})
        return render(request, template, {'form': form, 'chart_speed': chart_speed, 'chart_gears':chart_gears})
    form = Driver_Speed_Lap()
    return render(request, template, {'form': form})


def tyre_stints(request):
    template = 'f1dataapp/tire_stints.html'
    if request.method == "POST":
        form = Tire_Stints(request.POST)
        if form.is_valid():
            circuit = form.cleaned_data['circuit']
            year = int(form.cleaned_data['year'])
            session = form.cleaned_data['session']
            try:
                chart = ChartFactory.generate_tire_stints(year, circuit.name, session)
            except:
                return render(request, template, {'form': form, 'error':"Error: Input data does not match any event."})
        return render(request, template, {'form': form, 'chart': chart})
    form = Tire_Stints()
    return render(request, template, {'form': form})


def position_changes(request):
    template = 'f1dataapp/position_changes.html'
    if request.method == "POST":
        form = Race_Selector(request.POST)
        if form.is_valid():
            circuit = form.cleaned_data['circuit']
            year = int(form.cleaned_data['year'])
            try:
                chart = ChartFactory.generate_position_changes(year, circuit.name)
            except:
                return render(request, template, {'form': form, 'error':"Error: Input data does not match any event."})
        return render(request, template, {'form': form, 'chart': chart})
    form = Race_Selector()
    return render(request, template, {'form': form})


def driver_lap_timings(request):
    template = 'f1dataapp/driver_lap_timings.html'
    if request.method == "POST":
        form = Driver_Lap_Timing(request.POST)
        if form.is_valid():
            circuit = form.cleaned_data['circuit']
            year = int(form.cleaned_data['year'])
            driver = form.cleaned_data['driver']
            try:
                chart = ChartFactory.generate_driver_lap_timings(year, circuit.name, driver.code)
            except:
                return render(request, template, {'form': form, 'error':"Error: Input data does not match any event."})
        return render(request, template, {'form': form, 'chart': chart})
    form = Driver_Lap_Timing()
    return render(request, template, {'form': form})





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