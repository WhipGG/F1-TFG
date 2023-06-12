from django import forms
from django.forms import ModelForm
from django.db.models import Q
from datetime import datetime

from .models import Driver, Constructor, Circuit, Grid


class Prediction(forms.Form):
    warm = forms.BooleanField(label='Warm',required=False)
    cold = forms.BooleanField(label='Cold',required=False)
    dry = forms.BooleanField(label='Dry',required=False)
    wet = forms.BooleanField(label='Wet',required=False)
    cloudy = forms.BooleanField(label='Cloudy',required=False)
    
    max_verstappen = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Max Verstappen")
    hamilton = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Lewis Hamilton")
    alonso = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Fernando Alonso")
    leclerc = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Charles Leclerc")
    sainz = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Carlos Sainz")
    perez = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Sergio Pérez")
    norris = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Lando Norris")
    piastri = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Oscar Piastri")
    russell = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="George Russell")
    ocon = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Esteban Ocon")
    gasly = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Pierre Gasly")
    stroll = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Lance Stroll")
    bottas = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Valtteri Bottas")
    zhou = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Guanyu Zhou")
    tsunoda = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Yuki Tsunoda")
    de_vries = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Nyck de Vries")
    kevin_magnussen = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Kevin Magnussen")
    hulkenberg = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Nico Hülkenberg")
    albon = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Alexander Albon")
    sargeant = forms.ChoiceField(choices=((x,x) for x in range(1,22)), required=True, label="Logan Sargeant")

def process_prediction_form(form):
    driverIds = []
    strating_pos = []
    for gridObj in Grid.objects.all():
        driver = gridObj.driver
        driverIds.append(int(driver.driverId))
        strating_pos.append(int(form.cleaned_data[driver.driverRef]))
    strating_pos_check = strating_pos.copy()
    strating_pos_check = [i for i in strating_pos_check if i != 21]
    if len(strating_pos_check) != len(set(strating_pos_check)):
        return "Error: Two or more drivers cannot have the same starting position", False
    return driverIds, strating_pos

