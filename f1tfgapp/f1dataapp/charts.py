import base64
import io
import urllib.parse

import fastf1
import fastf1.plotting
import fastf1.plotting
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from fastf1.core import Laps
from matplotlib.collections import LineCollection
from timple.timedelta import strftimedelta

from .models import Constructor

mpl.use('Agg')

CACHE_DIR = 'f1dataapp/f1cache'

class ChartFactory:
    @staticmethod
    def generate_table():
        fastf1.Cache.enable_cache(CACHE_DIR)
        request = requests.get('http://ergast.com/api/f1/current/last.json')
        data = request.json()
        ergast_race = data['MRData']['RaceTable']['Races'][0]
        session = fastf1.get_session(int(ergast_race['season']), ergast_race['raceName'], 'R')
        session.load()
        team_translate = {'Mercedes':'mercedes',
                          'Red Bull Racing':'red_bull',
                          'McLaren':'mclaren',
                          'Aston Martin':'aston_martin',
                          'Ferrari':'ferrari',
                          'Alpine':'alpine',
                          'Haas F1 Team':'haas',
                          'AlphaTauri':'alphatauri',
                          'Alfa Romeo':'alfa',
                          'Williams':'williams'}
        return [
            {
                'position': int(row['Position']),
                'name': row['FullName'],
                'team': row['TeamName'],
                'status': row['Status'],
                'points': int(row['Points']),
                'color': row['TeamColor'],
                'code': row['Abbreviation'],
                'logo': Constructor.objects.filter(constructorRef=team_translate[row['TeamName']])[0].logo.url
            }
            for index, row in session.results.iterrows()
        ]

    @staticmethod
    def generate_times(session_type):
        plt.rcParams["figure.figsize"] = (6, 5)
        fastf1.Cache.enable_cache(CACHE_DIR)
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)

        request = requests.get('http://ergast.com/api/f1/current/last.json')
        data = request.json()
        ergast_race = data['MRData']['RaceTable']['Races'][0]

        session = fastf1.get_session(int(ergast_race['season']), ergast_race['raceName'], session_type)
        session.load()

        drivers = pd.unique(session.laps['Driver'])

        list_fastest_laps = []
        for driver in drivers:
            driver_fastest_lap = session.laps.pick_driver(driver).pick_fastest()
            list_fastest_laps.append(driver_fastest_lap)

        fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)
        fastest_laps = fastest_laps.dropna(axis=0, how='all')

        pole_lap = fastest_laps.pick_fastest()
        fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

        team_colors = []
        for index, lap in fastest_laps.iterlaps():
            color = fastf1.plotting.team_color(str(lap['Team']))
            team_colors.append(color)

        fig, ax = plt.subplots()
        ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'], color=team_colors, edgecolor='grey')
        ax.set_yticks(fastest_laps.index)
        ax.set_yticklabels(fastest_laps['Driver'])
        ax.invert_yaxis()
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

        pole_lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

        plt.suptitle(f"{session.event['EventName']} {session.event.year}\n"
                     f"Fastest Lap: {pole_lap_time_string} ({pole_lap['Driver']})")

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri