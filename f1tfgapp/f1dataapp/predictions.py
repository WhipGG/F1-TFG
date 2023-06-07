import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
import joblib



model = tf.keras.models.load_model('models/nn_f1.h5')
scaler = joblib.load('models/minmaxscaler_f1.pkl')


def generate_new_race_start(grid_positions, 
                            weather={'weather_warm':0,
                                     'weather_cold':0,
                                     'weather_dry':0,
                                     'weather_wet':0,
                                     'weather_cloudy':0}, 
                            driver_data='data_ready/2023_grid_data.csv',
                            data_path = 'f1db_csv/'):
    # Load necessary data from csv
    date_parse_list = ['date', 'fp1_date', 'fp2_date', 'fp3_date', 'quali_date', 'sprint_date']
    races = pd.read_csv(data_path+'races.csv', na_values=["\\N"], parse_dates=date_parse_list)
    constructor_standings = pd.read_csv(data_path+'constructor_standings.csv', na_values=["\\N"])
    driver_standings = pd.read_csv(data_path+'driver_standings.csv', na_values=["\\N"])
    
    # Obtain current grid data
    grid = pd.read_csv(driver_data, parse_dates=['dob', 'firstRaceDate'])
    
    # Create df for next race
    next_race = races.loc[races['date']>=pd.Timestamp.today()][0:1]
    drop_list_1 = ['url', 'time', 'name',
                   'fp1_date', 'fp1_time',
                   'fp2_date', 'fp2_time',
                   'fp3_date', 'fp3_time',
                   'quali_date', 'quali_time',
                   'sprint_date', 'sprint_time']
    next_race = next_race.drop(drop_list_1, axis=1)
    next_race['weather_warm'] = weather['weather_warm']
    next_race['weather_cold'] = weather['weather_cold']
    next_race['weather_dry'] = weather['weather_dry']
    next_race['weather_wet'] = weather['weather_wet']
    next_race['weather_cloudy'] = weather['weather_cloudy']
    
    # Obtain current standings
    driver_standings_mod = driver_standings[driver_standings['raceId']==int(next_race[0:1]['raceId']-1)].copy()
    drop_list_2 = ['driverStandingsId', 'raceId', 'position', 'positionText', 'wins']
    driver_standings_mod = driver_standings_mod.drop(drop_list_2, axis=1)
    
    constructor_standings_mod = constructor_standings[constructor_standings['raceId']==int(next_race[0:1]['raceId']-1)].copy()
    drop_list_3 = ['constructorStandingsId', 'raceId', 'position', 'positionText', 'wins']
    constructor_standings_mod = constructor_standings_mod.drop(drop_list_3, axis=1)
    
    # Create df with starting grid
    starting_grid = pd.DataFrame.from_dict(grid_positions)
    
    # Create df for predict
    next_grid = grid.merge(starting_grid, how='inner', on='driverId')
    next_grid = next_grid.merge(next_race, how='cross')
    next_grid['age'] = next_grid['date'] - next_grid['dob']
    next_grid['experience'] = next_grid['date'] - next_grid['firstRaceDate']
    next_grid['age'] = next_grid['age'].dt.days
    next_grid['experience'] = next_grid['experience'].dt.days
    next_grid = next_grid.merge(driver_standings_mod, how='inner', on='driverId')
    next_grid = next_grid.rename(columns={'points':'driversPointsBeforeRace'})
    next_grid = next_grid.merge(constructor_standings_mod, how='inner', on='constructorId')
    next_grid = next_grid.rename(columns={'points':'constPointsBeforeRace'})
    drop_list_4 = ['driverRef', 'dob', 'firstRaceDate', 'raceId', 'date', 'forename', 'surname', 'fullname']
    next_grid = next_grid.drop(drop_list_4, axis=1)
    
    standings = driver_standings.loc[driver_standings['raceId']==int(next_race['raceId']-1)][['driverId', 'points']]
    return next_grid, standings




def predict(grid_positions, 
            weather={'weather_warm':0,
                     'weather_cold':0,
                     'weather_dry':0,
                     'weather_wet':0,
                     'weather_cloudy':0}):
    
    df, standings = generate_new_race_start(grid_positions, weather=weather)
    # Transform data
    df['grid'] = df['grid'].clip(upper=20)
    columns_to_scale = ['grid', 'year', 'round', 'age', 'experience', 'driversPointsBeforeRace', 'constPointsBeforeRace']
    df[columns_to_scale] = scaler.transform(df[columns_to_scale])
    drivers = df['driverId']
    constructors = df['constructorId']
    circuits = df['circuitId']
    X = df.drop(['driverId', 'constructorId', 'circuitId'], axis=1)
    
    # Predict and evaluate
    preds = model.predict([drivers, constructors, circuits, X], verbose = 0)
    df_preds = pd.DataFrame()
    df_preds['driverId'] = df['driverId']
    df_preds['prediction'] = np.argmax(preds, axis=1)+1
    df_preds = df_preds.merge(drivers, how='inner', on='driverId')
    df_preds = df_preds.merge(standings, how='inner', on='driverId')
    df_preds = df_preds.sort_values(by=['prediction', 'points'], ascending=[True, False])
    return df_preds