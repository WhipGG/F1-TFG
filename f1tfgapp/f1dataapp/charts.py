import base64
import io
import urllib.parse

import fastf1
import fastf1.plotting
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import requests
import datetime
from fastf1.core import Laps
from matplotlib.collections import LineCollection
from matplotlib import cm
from timple.timedelta import strftimedelta

from .models import Constructor

fastf1.plotting.setup_mpl()
mpl.use('Agg')

CACHE_DIR = 'f1dataapp/f1cache'
DATA_DIR = 'f1dataapp/f1db_csv/'

def load_circuit_ref():
    results = pd.read_csv(DATA_DIR+'results.csv', na_values=["\\N"])
    results['number'] = results['number'].astype('Int64')
    circuits = pd.read_csv(DATA_DIR+'circuits.csv', na_values=["\\N"])
    date_parse_list = ['date', 'fp1_date', 'fp2_date', 'fp3_date', 'quali_date', 'sprint_date']
    races = pd.read_csv(DATA_DIR+'races.csv', na_values=["\\N"], parse_dates=date_parse_list)
    df = results.merge(races, how='inner', on='raceId')
    df = df.rename(columns={"name": "gp_name"})
    df = df.merge(circuits, how='inner', on='circuitId')
    return df

circuit_ref = load_circuit_ref()

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

        plt.suptitle(f"{session.event['EventName']} {session.event.year} - {session.name}\n"
                     f"Fastest Lap: {pole_lap_time_string} ({pole_lap['Driver']})")

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    
    @staticmethod
    def generate_VS(year, driver1, driver2, circuit_name, session_ty):
        fastf1.Cache.enable_cache(CACHE_DIR)

        plt.rcParams["figure.figsize"] = (20, 20)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = session_ty

        session = fastf1.get_session(year, wknd, session_type)
        session.load()

        driver1_lap = session.laps.pick_driver(driver1).pick_fastest()
        driver2_lap = session.laps.pick_driver(driver2).pick_fastest()

        driver1_tel = driver1_lap.get_car_data().add_distance()
        driver2_tel = driver2_lap.get_car_data().add_distance()

        driver1_color = fastf1.plotting.driver_color(driver1)
        driver2_color = fastf1.plotting.driver_color(driver2)

        fig, (ax0, ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=6, sharex=True, layout='constrained')
        """
        ax0 = Speed
        ax1 = Throttle
        ax2 = Brake
        ax3 = Gear
        ax4 = RPM
        ax5 = DRS
        """
        ax0.plot(driver1_tel['Distance'], driver1_tel['Speed'], color=driver1_color, label=driver1)
        ax0.plot(driver2_tel['Distance'], driver2_tel['Speed'], color=driver2_color, label=driver2)
        ax0.set_ylabel('Speed in km/h', fontsize=18)
        ax0.legend()

        ax1.plot(driver1_tel['Distance'], driver1_tel['Throttle'], color=driver1_color, label=driver1)
        ax1.plot(driver2_tel['Distance'], driver2_tel['Throttle'], color=driver2_color, label=driver2)
        ax1.set_ylabel('Throttle %', fontsize=18)

        ax2.plot(driver1_tel['Distance'], driver1_tel['Brake'], color=driver1_color, label=driver1)
        ax2.plot(driver2_tel['Distance'], driver2_tel['Brake'], color=driver2_color, label=driver2)
        ax2.set_ylabel('Brake', fontsize=18)

        ax3.plot(driver1_tel['Distance'], driver1_tel['nGear'], color=driver1_color, label=driver1)
        ax3.plot(driver2_tel['Distance'], driver2_tel['nGear'], color=driver2_color, label=driver2)
        ax3.set_ylabel('Gear', fontsize=18)

        ax4.plot(driver1_tel['Distance'], driver1_tel['RPM'], color=driver1_color, label=driver1)
        ax4.plot(driver2_tel['Distance'], driver2_tel['RPM'], color=driver2_color, label=driver2)
        ax4.set_ylabel('RPM', fontsize=18)

        ax5.plot(driver1_tel['Distance'], driver1_tel['DRS'], color=driver1_color, label=driver1)
        ax5.plot(driver2_tel['Distance'], driver2_tel['DRS'], color=driver2_color, label=driver2)
        ax5.set_xlabel('Distance in m', fontsize=20)
        ax5.set_ylabel('DRS', fontsize=18)
        
        plt.suptitle(f"Fastest Lap Comparison \n "
                     f"{session.event['EventName']} {session.event.year} - {session.name}\n"
                     f"{driver1} vs {driver2}",
                     size='xx-large')


        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri

    @staticmethod
    def generate_speed_lap(year, driver, circuit_name, session_ty):
        fastf1.Cache.enable_cache(CACHE_DIR)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = session_ty
        driver_name = driver
        colormap = mpl.cm.plasma

        session = fastf1.get_session(year, wknd, session_type)
        weekend = session.event
        session.load()
        lap = session.laps.pick_driver(driver_name).pick_fastest()

        x = lap.telemetry['X']
        y = lap.telemetry['Y']
        color = lap.telemetry['Speed']
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
        fig.suptitle(f'{weekend.EventName} {year} - {session.name} - {driver_name} - Speed', size=24, y=0.97)

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
        ax.axis('off')

        ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)

        norm = plt.Normalize(color.min(), color.max())
        lc = mpl.collections.LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)

        lc.set_array(color)

        line = ax.add_collection(lc)

        cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
        normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
        legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    
    @staticmethod
    def generate_gears_lap(year, driver, circuit_name, session_ty):
        fastf1.Cache.enable_cache(CACHE_DIR)

        plt.rcParams["figure.figsize"] = (12, 6.75)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = session_ty
        driver_name = driver

        session = fastf1.get_session(year, wknd, session_type)
        weekend = session.event
        session.load()
        lap = session.laps.pick_driver(driver).pick_fastest()

        #plt.rcParams["figure.figsize"] = (10, 6)
        tel = lap.get_telemetry()

        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        gear = tel['nGear'].to_numpy().astype(float)

        cmap = cm.get_cmap('Paired')
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
        lc_comp.set_array(gear)
        lc_comp.set_linewidth(4)

        plt.gca().add_collection(lc_comp)
        plt.axis('equal')
        plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

        title = plt.suptitle(f'{weekend.EventName} {year} - {session.name} - {driver} - Gearshifts')

        cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))
        cbar.set_ticks(np.arange(1.5, 9.5))
        cbar.set_ticklabels(np.arange(1, 9))

        fig = plt

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def generate_tire_stints(year, circuit_name, session_ty):
        fastf1.Cache.enable_cache(CACHE_DIR)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = session_ty

        session = fastf1.get_session(year, wknd, session_type)
        session.load()
        laps = session.laps
        drivers = session.drivers
        drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"])
        stints = stints.count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})

        fig, ax = plt.subplots(figsize=(5, 10))
        
        for driver in drivers:
            driver_stints = stints.loc[stints["Driver"] == driver]

            previous_stint_end = 0
            for idx, row in driver_stints.iterrows():
                plt.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=fastf1.plotting.COMPOUND_COLORS[row["Compound"]],
                    edgecolor="black",
                    fill=True
                )

                previous_stint_end += row["StintLength"]

        plt.title(f'{year} {session.event.EventName} \n {session.name} \n Tire strategies')
        plt.xlabel("Lap Number")
        plt.grid(False)
        ax.invert_yaxis()

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def generate_position_changes(year, circuit_name):
        fastf1.Cache.enable_cache(CACHE_DIR)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = 'R'

        session = fastf1.get_session(year, wknd, session_type)
        session.load()

        fig, ax = plt.subplots(figsize=(12.0, 7.3))

        for drv in session.drivers:
            drv_laps = session.laps.pick_driver(drv)

            abb = drv_laps['Driver'].iloc[0]
            color = fastf1.plotting.driver_color(abb)

            ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                    label=abb, color=color)

        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel('Lap')
        ax.set_ylabel('Position')

        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.title(f'{year} {session.event.EventName} - Position changes')
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def generate_driver_lap_timings(year, circuit_name, driver):
        fastf1.Cache.enable_cache(CACHE_DIR)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = 'R'

        session = fastf1.get_session(year, wknd, session_type)
        session.load()

        driver_laps = session.laps.pick_driver(driver)
        """
        pits = driver_laps[pd.notna(driver_laps['PitInTime'])]
        driver_laps = driver_laps[pd.isna(driver_laps['PitOutTime'])]
        driver_laps = driver_laps[pd.isna(driver_laps['PitInTime'])]

        driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

        driver_laps = driver_laps.groupby('Stint')
        dfs = []
        for name, data in driver_laps:
            dfs.append(data)
        """
        driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
        driver_laps = driver_laps.groupby('Stint')
        dfs = []
        for name, data in driver_laps:
            dfs.append(data)
            
        for index in range(len(dfs)-1):
            next_row = dfs[index+1].iloc[0].copy()
            dfs[index].loc[len(dfs[index])] = next_row
            dfs[index] = dfs[index].sort_values(by="LapNumber")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        for df in dfs:
            ax.plot(df['LapNumber'], df['LapTime(s)'], color=fastf1.plotting.COMPOUND_COLORS[(df.iloc[0]['Compound'])])
        """
        for index, row in pits.iterrows():
            ax.axvspan(row['LapNumber']-1, row['LapNumber']+2, ymin = 0, ymax = 1)
            bot, top = ax.get_ylim()
            plt.text(row['LapNumber']-0.6, (bot+top)/2, 'PIT', rotation='90', fontsize='16', color='black')
        """
        ax.xaxis.set_label_text('Lap number')
        ax.yaxis.set_label_text('Lap time (s)')
        ax.set_title(f'{session.date.year} {session.event.EventName} - {driver} - Race pace')

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def driver_timing_comparison(year, circuit_name, drivers):
        fastf1.Cache.enable_cache(CACHE_DIR)

        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = 'R'

        session = fastf1.get_session(year, wknd, session_type)
        session.load()
        
        fig, ax = plt.subplots(figsize=(10, 5))

        for driver in drivers:
            driver_laps = session.laps.pick_driver(driver)
            driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
            ax.plot(driver_laps['LapNumber'], driver_laps['LapTime(s)'], color=fastf1.plotting.driver_color(driver), label=driver)

        ax.xaxis.set_label_text('Lap number')
        ax.yaxis.set_label_text('Lap time (s)')
        ax.set_title(f'{session.date.year} {session.event.EventName} - Race pace comparison')
        ax.legend()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def lap_time_distribution(year, circuit_name):
        wknd = int(circuit_ref.loc[(circuit_ref['year']==year) & (circuit_ref['name']==circuit_name)][0:1]['round'])
        session_type = 'R'

        session = fastf1.get_session(year, wknd, session_type)
        session.load()

        point_finishers = session.drivers[:10]
        driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps()
        driver_laps = driver_laps.reset_index()
        finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]
        driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
                        driver in fastf1.plotting.DRIVER_TRANSLATE.items()}

        fig, ax = plt.subplots(figsize=(10, 5))

        driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

        sns.violinplot(data=driver_laps,
                    x="Driver",
                    y="LapTime(s)",
                    inner=None,
                    scale="area",
                    order=finishing_order,
                    palette=driver_colors
                    )
        sns.swarmplot(data=driver_laps,
                    x="Driver",
                    y="LapTime(s)",
                    order=finishing_order,
                    hue="Compound",
                    palette=fastf1.plotting.COMPOUND_COLORS,
                    hue_order=["SOFT", "MEDIUM", "HARD"],
                    linewidth=0,
                    size=5,
                    )
        ax.set_xlabel("Driver")
        ax.set_ylabel("Lap Time (s)")
        plt.title(f"{session.date.year} {session.event.EventName} - Lap Time Distributions")
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def plot_driver_standings():
        request = requests.get('http://ergast.com/api/f1/current/driverStandings.json')
        data = request.json()
        standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        driver_standings = pd.DataFrame(columns=['name', 'position','points'])
        for position in standings:
            name = position['Driver']['code']
            pos = int(position['position'])
            points = int(position['points'])
            driver_standings.loc[len(driver_standings)] = [name, pos, points]
        
        fig, ax = plt.subplots(figsize=(6, 5))
        colors = [fastf1.plotting.driver_color(row['name'])  for index, row in driver_standings.iterrows()]
        bars = ax.barh(driver_standings['name'], driver_standings['points'], color=colors)
        ax.set_yticks(driver_standings['name'], labels=driver_standings['name'])
        ax.invert_yaxis()
        ax.set_title(f"{datetime.datetime.now().year} Season Driver Standings")
        ax.bar_label(bars)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri
    

    @staticmethod
    def plot_constructor_standings():
        request = requests.get('http://ergast.com/api/f1/current/constructorStandings.json')
        data = request.json()
        standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
        constructor_standings = pd.DataFrame(columns=['name', 'position','points'])
        for position in standings:
            name = position['Constructor']['name']
            pos = int(position['position'])
            points = int(position['points'])
            constructor_standings.loc[len(constructor_standings)] = [name, pos, points]
        
            fig, ax = plt.subplots(figsize=(6, 5))
            const_abv = {'Red Bull':'RBR',
                        'Mercedes':'MER',
                        'Aston Martin':'AMR',
                        'Ferrari':'FER',
                        'Alpine F1 Team':'APN',
                        'McLaren':'MCL',
                        'Haas F1 Team':'HAA',
                        'Alfa Romeo':'ARR',
                        'AlphaTauri':'APT',
                        'Williams':'WIL'}
            lab = [const_abv[row['name']]for index, row in constructor_standings.iterrows()]
            colors = [fastf1.plotting.team_color(row['name'])  for index, row in constructor_standings.iterrows()]
            bars = ax.barh(constructor_standings['name'], constructor_standings['points'], color=colors)
            ax.set_yticks(constructor_standings['name'], labels=lab)
            ax.invert_yaxis()
            ax.set_title(f"{datetime.datetime.now().year} Season Constructor Standings")
            ax.bar_label(bars)

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plt.close("all")

        return uri

