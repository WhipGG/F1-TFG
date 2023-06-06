import requests, zipfile, io
from selenium import webdriver
import pandas as pd
import numpy as np



def update_database(path_to_save='./f1db_csv'):
    r = requests.get('https://ergast.com/downloads/f1db_csv.zip')
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(path_to_save)
    
    # Get weather info
    date_parse_list = ['date', 'fp1_date', 'fp2_date', 'fp3_date', 'quali_date', 'sprint_date']
    races = pd.read_csv(path_to_save+'/races.csv', na_values=["\\N"], parse_dates=date_parse_list)
    weather = races.iloc[:,[0]]
    
    info = []
    # read wikipedia tables
    for link in races.url:
        try:
            df = pd.read_html(link)[0]
            if 'Weather' in list(df.iloc[:,0]):
                n = list(df.iloc[:,0]).index('Weather')
                info.append(df.iloc[n,1])
            else:
                df = pd.read_html(link)[1]
                if 'Weather' in list(df.iloc[:,0]):
                    n = list(df.iloc[:,0]).index('Weather')
                    info.append(df.iloc[n,1])
                else:
                    df = pd.read_html(link)[2]
                    if 'Weather' in list(df.iloc[:,0]):
                        n = list(df.iloc[:,0]).index('Weather')
                        info.append(df.iloc[n,1])
                    else:
                        df = pd.read_html(link)[3]
                        if 'Weather' in list(df.iloc[:,0]):
                            n = list(df.iloc[:,0]).index('Weather')
                            info.append(df.iloc[n,1])
                        else:
                            driver = webdriver.Chrome()
                            driver.get(link)
                            
                            # click language button
                            button = driver.find_element_by_link_text('Italiano')
                            button.click()
                            
                            # find weather in italian with selenium
                            
                            clima = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[9]/td').text
                            info.append(clima) 
                                
        except:
            info.append('not found')
            
    # append column with weather information to dataframe  
    info_ser = pd.Series(info)
    weather = weather.merge(info_ser.rename('weather'), left_index=True, right_index=True)
    # set up a dictionary to convert weather information into keywords
    weather_dict = {'weather_warm': ['soleggiato', 'clear', 'warm', 'hot', 'sunny', 'fine', 'mild', 'sereno'],
                    'weather_cold': ['cold', 'fresh', 'chilly', 'cool'],
                    'weather_dry': ['dry', 'asciutto'],
                    'weather_wet': ['showers', 'wet', 'rain', 'pioggia', 'damp', 'thunderstorms', 'rainy'],
                    'weather_cloudy': ['overcast', 'nuvoloso', 'clouds', 'cloudy', 'grey', 'coperto']}
    # map new df according to weather dictionary
    weather_df = pd.DataFrame(columns = weather_dict.keys())
    for col in weather_df:
        weather_df[col] = weather['weather'].map(lambda x: 1 if any(i in weather_dict[col] for i in x.lower().split()) else 0) 
    weather_info = pd.concat([weather, weather_df], axis = 1)
    weather_info = weather_info.replace('not found', np.nan)
    weather_info.to_csv(path_to_save+'/weather.csv', index=False)
    





    
def update_learning_dataset(data_path='./f1db_csv/', save_path='./data_ready/'):
    # Load data
    constructor_standings = pd.read_csv(data_path+'constructor_standings.csv', na_values=["\\N"])
    driver_standings = pd.read_csv(data_path+'driver_standings.csv', na_values=["\\N"])
    drivers = pd.read_csv(data_path+'drivers.csv', na_values=["\\N"], parse_dates=['dob'])
    drivers['number'] = drivers['number'].astype('Int64')
    date_parse_list = ['date', 'fp1_date', 'fp2_date', 'fp3_date', 'quali_date', 'sprint_date']
    races = pd.read_csv(data_path+'races.csv', na_values=["\\N"], parse_dates=date_parse_list)
    results = pd.read_csv(data_path+'results.csv', na_values=["\\N"])
    results['number'] = results['number'].astype('Int64')
    weather_info = pd.read_csv(data_path+'weather.csv')
    
    # Create dataset
    races_weather = races.merge(weather_info, how='inner', on='raceId')
    df1 = results.copy()
    df1 = df1.merge(races_weather, how='inner', on='raceId')
    drop_list_1 = ['url',
                   'fp1_date', 'fp1_time',
                   'fp2_date', 'fp2_time',
                   'fp3_date', 'fp3_time',
                   'quali_date', 'quali_time',
                   'sprint_date', 'sprint_time',
                   'fastestLap', 'rank',
                   'fastestLapTime', 'fastestLapSpeed',
                   'time_x', 'milliseconds',
                   'laps', 'statusId']
    df1 = df1.drop(drop_list_1, axis=1)
    df1 = df1.rename(columns={'time_y':'time'})
    
    drivers_frd = drivers.copy()
    first_race_dates = []
    results_sorted_date = df1.sort_values(by='date')
    for driver in drivers_frd.driverId:
        first_race_dates.append(results_sorted_date[results_sorted_date.driverId == driver].iloc[0].date)
    drivers_frd['firstRaceDate'] = first_race_dates
    
    df2 = df1.merge(drivers_frd, how='inner', on='driverId')
    drop_list_2 = ['url',
                   'number_x','number_y',
                   'nationality', 'code',
                   'forename', 'surname']
    df2 = df2.drop(drop_list_2, axis=1)
    df2['age'] = df2['date'] - df2['dob']
    df2['experience'] = df2['date'] - df2['firstRaceDate']
    
    driver_standings_mod = driver_standings.copy()
    drop_list_3 = ['driverStandingsId', 'position', 'positionText', 'wins']
    driver_standings_mod = driver_standings_mod.drop(drop_list_3, axis=1)
    driver_standings_mod = driver_standings_mod.rename(columns={'points':'pointsAfterRace'})
    
    df3 = df2.merge(driver_standings_mod, how='left', on=['raceId', 'driverId'])
    df3['driversPointsBeforeRace'] = df3['pointsAfterRace'] - df3['points']
    
    def calc_cons_points_bef_race(race, cons):
        return sum(df3.loc[(df3['raceId']==race) & (df3['constructorId']==cons)]['driversPointsBeforeRace'])
    constructor_standings_mod = constructor_standings.copy()
    constructor_standings_mod['constPointsBeforeRace'] = constructor_standings_mod.apply(
        lambda x: calc_cons_points_bef_race(x.raceId, x.constructorId), axis=1)
    constructor_standings_mod = constructor_standings_mod.fillna(0)
    drop_list_4 = ['constructorStandingsId', 'points', 'position', 'positionText', 'wins']
    constructor_standings_mod = constructor_standings_mod.drop(drop_list_4, axis=1)
    
    df4 = df3.merge(constructor_standings_mod, how='left', on=['raceId', 'constructorId'])
    
    drop_list_5 = ['resultId', 'name', 'date', 'time', 'weather', 'dob', 'firstRaceDate', 'driverRef', 'pointsAfterRace',
                   'position', 'positionText', 'points', 'raceId']
    df5 = df4.drop(drop_list_5, axis=1)
    df5 = df5.rename(columns={'positionOrder':'position'})
    df5['age'] = df5['age'].dt.days
    df5['experience'] = df5['experience'].dt.days
    df5['driversPointsBeforeRace'] = df5['driversPointsBeforeRace'].fillna(0)
    df5['constPointsBeforeRace'] = df5['constPointsBeforeRace'].fillna(0)
    df5['grid'] = df5['grid'].replace(0, 21)
    
    # Save
    df5.to_csv(save_path+'LEARNING_DF_NORMAL.csv', index=False)