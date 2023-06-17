import fastf1
from datetime import datetime
import requests
import pandas as pd
from .models import Driver, Constructor, Circuit, Grid


data_directory='f1dataapp/f1db_csv/'

def transform_none(num):
    if type(num)==pd._libs.missing.NAType:
        return None
    else:
        return num

def populate_drivers():
    Driver.objects.all().delete()
    drivers = pd.read_csv(data_directory+'drivers.csv', na_values=["\\N"], parse_dates=['dob'])
    drivers['number'] = drivers['number'].astype('Int64')
    objs = [Driver(driverId=row['driverId'],
                   driverRef=row['driverRef'],
                   number=transform_none(row['number']),
                   code=row['code'], 
                   forename=row['forename'],
                   surname=row['surname'],
                   dob=row['dob'],
                   nationality=row['nationality'],
                   url=row['url'],
                   name=row['forename'] + ' ' + row['surname'] 
                   ) for index, row in drivers.iterrows()]
    Driver.objects.bulk_create(objs)



def populate_constructors():
    Constructor.objects.all().delete()
    constructors = pd.read_csv(data_directory+'constructors.csv', na_values=["\\N"])
    objs = [Constructor(constructorId=row['constructorId'],
                        constructorRef=row['constructorRef'],
                        name=row['name'], 
                        nationality=row['nationality'],
                        url=row['url']
                        ) for index, row in constructors.iterrows()]
    Constructor.objects.bulk_create(objs)



def populate_circuits():
    Circuit.objects.all().delete()
    circuits = pd.read_csv(data_directory+'circuits.csv', na_values=["\\N"])
    objs = [Circuit(circuitId=row['circuitId'],
                    circuitRef=row['circuitRef'],
                    name=row['name'], 
                    location=row['location'],
                    country=row['country'],
                    url=row['url']
                    ) for index, row in circuits.iterrows()]
    Circuit.objects.bulk_create(objs)



def fetch_old_race_data():
    fastf1.Cache.enable_cache('f1dataapp/f1cache')
    session_types = ["FP1", "FP2", "FP3", "Q", "R", "S", "SS"]
    for year in range(2022, datetime.now().year+1):
        for round_number in range(1, 25):
            for session_type in session_types:
                try:
                    session = fastf1.get_session(year, round_number, session_type)
                    session.load()
                except:
                    pass