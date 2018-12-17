"""Script to prepare weather data
Load weather simulation data

1. Download yearly data from here: http://catalogue.ceda.ac.uk/uuid/0cea8d7aca57427fae92241348ae9b03

2. Extract data

3. Run this script to get only the relevant data

Links
------
http://data.ceda.ac.uk//badc//weather_at_home/data/marius_time_series/CEDA_MaRIUS_Climate_Data_Description.pdf
http://data.ceda.ac.uk/badc/weather_at_home/data/marius_time_series/near_future/data/


https://medium.com/@rtjeannier/pandas-101-cont-9d061cb73bfc

"""
import logging
import os
import pytemperature
import xarray as xr
import numpy as np
import pandas as pd

from energy_demand.basic import basic_functions
from energy_demand.read_write import write_data

def create_realisation(
        base_yr_remapped_weather_path,
        realisation_list,
        realisation_path,
        realisation_out_path,
        path_stiching_table
    ):
    """
    Before running, generate 2015 remapped data
    """
    sim_yr_start = 2015
    sim_yr_end = 2050 + 1

    print("... writing data", flush=True)
    write_to_csv = True
    write_to_np = False
    write_to_parquet = False

    # Create result path
    basic_functions.create_folder(realisation_out_path)

    # Read in stiching table
    df_path_stiching_table = pd.read_table(path_stiching_table, sep=" ")

    # Set year as index
    df_path_stiching_table = df_path_stiching_table.set_index('year')

    # Realisations
    realisations = list(df_path_stiching_table.columns)

    columns = ['timestep', 'longitude', 'latitude', 'yearday', 'wss', 'rlds', 'rsds']

    for i in realisation_list:
        realisation = realisations[i]

        print("... creating weather data for realisation " + str(realisation), flush=True)
        realisation_out = []

        for sim_yr in range(sim_yr_start, sim_yr_end):

            print("   ... year: " + str(sim_yr), flush=True)
            # If year 2015 - 2019, take base year weather
            if sim_yr in range(2015, 2020):
                #print("... for year '{}' data from the year 2015 are used".format(sim_yr))
                year = 2020 #Select year 2020
                stiching_name = df_path_stiching_table[realisation][year]
                path_weather_data = os.path.join(realisation_path, str(year), stiching_name)
                path_wss = os.path.join(path_weather_data, "wss.npy")
                path_rlds = os.path.join(path_weather_data, "rlds.npy")
                path_rsds = os.path.join(path_weather_data, "rsds.npy")
                path_stations = os.path.join(path_weather_data, "stations.csv")

            elif sim_yr == 2050:
                #print("... for year '{}' data from the year 2049 are used".format(sim_yr))
                year = 2049
                stiching_name = df_path_stiching_table[realisation][year]
                path_weather_data = os.path.join(realisation_path, str(year), stiching_name)
                path_wss = os.path.join(path_weather_data, "wss.npy")
                path_rlds = os.path.join(path_weather_data, "rlds.npy")
                path_rsds = os.path.join(path_weather_data, "rsds.npy")
                path_stations = os.path.join(path_weather_data, "stations.csv")
            else:
                #print("normal")
                year = sim_yr
                stiching_name = df_path_stiching_table[realisation][year]
                path_weather_data = os.path.join(realisation_path, str(year), stiching_name)
                path_wss = os.path.join(path_weather_data, "wss.npy")
                path_rlds = os.path.join(path_weather_data, "rlds.npy")
                path_rsds = os.path.join(path_weather_data, "rsds.npy")
                path_stations = os.path.join(path_weather_data, "stations.csv")

            # Read t_min, t_max, stations)
            wss = np.load(path_wss)
            rlds = np.load(path_rlds)
            rsds = np.load(path_rsds)
            stations = pd.read_csv(path_stations)
            stations['timestep'] = sim_yr

            nr_stations_array = len(list(stations.values))

            for station_cnt in range(nr_stations_array):
                wss_station = wss[station_cnt]
                rlds_station = rlds[station_cnt]
                rsds_station = rsds[station_cnt]
                station_long = stations.loc[station_cnt]['longitude']
                station_lat = stations.loc[station_cnt]['latitude']
                for yearday in range(365):
                    realisation_out.append(
                        [sim_yr, station_long, station_lat, yearday, wss_station[yearday], rlds_station[yearday], rsds_station[yearday]])

        print("...writing out")
        # Write data to csv
        if write_to_csv:
            df = pd.DataFrame(realisation_out, columns=columns)
            path_out_csv = os.path.join(realisation_out_path, "weather_data_{}.csv".format(realisation))
            df.to_csv(path_out_csv, index=False)

        '''if write_to_parquet: 
            path_out_parquet = os.path.join(realisation_out_path, "weather_data_{}.parquet".format(realisation))
            df = pd.DataFrame(realisation_out, columns=columns)
            df.to_parquet(path_out_parquet, engine='pyarrow')

        if write_to_np:
            path_out_array = os.path.join(realisation_out_path, "weather_data_{}.npy".format(realisation))
            out_array = np.array(realisation_out)
            np.save(path_out_array, out_array)'''

        # Write stations to csv
        print("... writing stations to csv", flush=True)
        #stations_out.to_csv(os.path.join(realisation_out_path, "stations_{}.csv".format(realisation)), index=False)

def get_temp_data_from_nc(path_nc_file, attribute_to_keep):
    """Open c file, convert it into dataframe,
    clean it and extract attribute data
    """
    # Open as xarray
    x_array_data = xr.open_dataset(path_nc_file)

    # Convert to dataframe
    df = x_array_data.to_dataframe()

    # Add index as columns
    df = df.reset_index()

    # Drop unnecessary columns
    df = df.drop(['time_bnds', 'rotated_latitude_longitude', 'rlat', 'rlon', 'bnds', 'height'], axis=1)

    # Drop all missing value
    df = df.dropna(subset=[attribute_to_keep])

    return df

def convert_to_celcius(df, attribute_to_convert):
    """# Convert Kelvin to Celsius (# Kelvin to Celsius)
    """
    df[attribute_to_convert] = df[attribute_to_convert].apply(pytemperature.k2c)
    return df

def extend_360_day_to_365(df, attribute):
    """Add evenly distributed days across the 360 days

    Return
    ------
    out_list : list
        Returns list with days with the following attributes
        e.g. [[lat, long, yearday365, value]]
    """
    # Copy the following position of day in the 360 year
    days_to_duplicate = [60, 120, 180, 240, 300]
    out_list = []

    # Copy every 60th day over the year and duplicate it. Do this five times --> get from 360 to 365 days
    day_cnt, day_cnt_365 = 0, 0
    for i in df.index:
        day_cnt += 1

        latitude = df.get_value(i, 'lat')
        longitude = df.get_value(i, 'lon')
        value = df.get_value(i, attribute)

        # Copy extra day
        if day_cnt in days_to_duplicate:
            out_list.append([latitude, longitude, day_cnt_365, value])
            day_cnt_365 += 1

        # Copy day
        day_cnt_365 += 1
        out_list.append([latitude, longitude, day_cnt_365, value])

        # Reset counter if next weather station
        if day_cnt == 360:
            day_cnt = 0
            day_cnt_365 = 0

    return out_list

def write_weather_data(data_list):
    """Write weather data to array
    data_list : list
        [[lat, long, yearday365, value]]
    """
    station_coordinates = []

    assert not len(data_list) % 365 #Check if dividable by 365
    nr_stations = int(len(data_list) / 365)

    stations_data = np.zeros((nr_stations, 365))
    station_data = np.zeros((365))

    station_id_cnt = 0
    cnt = 0

    for row in data_list:
        station_data[cnt] = row[3]

        if cnt == 364:

            # 365 day data for weather station
            stations_data[station_id_cnt] = station_data

            # Weather station metadata
            station_lon = row[1]
            station_lat = row[0]

            station_id = "station_id_{}".format(station_id_cnt)

            #ID, latitude, longitude
            station_coordinates.append([station_id, station_lat, station_lon])

            # Reset
            station_data = np.zeros((365))
            station_id_cnt += 1
            cnt = -1
        cnt += 1

    return station_coordinates, stations_data

def weather_dat_prepare(data_path, result_path, years_to_clean=range(2020, 2049)):
    """
    """
    print("folder_name " + str(years_to_clean))

    # Create reulst folders
    result_folder = os.path.join(result_path, "_weather_data_cleaned_modassar")
    basic_functions.create_folder(result_folder)

    for folder_name in years_to_clean:

        year = folder_name

        # Create folder
        path_year = os.path.join(result_folder, str(year))
        basic_functions.create_folder(path_year)

        path_realizations = os.path.join(path, str(year))
        realization_names = os.listdir(path_realizations)

        for realization_name in realization_names:
            print("... processing {}  {}".format(str(year), str(realization_name)), flush=True)

            # Create folder
            path_realization = os.path.join(path_year, realization_name)
            basic_functions.create_folder(path_realization)
            
            # Data to extract
            path_wind = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_wss_daily_g2_{}.nc'.format(realization_name, year))
            path_rlds = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_rlds_daily_g2_{}.nc'.format(realization_name, year))
            path_rsds = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_rsds_daily_g2_{}.nc'.format(realization_name, year))
            
            # Load data
            print("     ..load data", flush=True)
            wss = get_temp_data_from_nc(path_wind, 'wss')
            rlds = get_temp_data_from_nc(path_rlds, 'rlds')
            rsds = get_temp_data_from_nc(path_rsds, 'rsds')

            # Convert 360 day to 365 days
            print("     ..extend day", flush=True)
            list_wss = extend_360_day_to_365(wss, 'wss')
            list_rlds = extend_360_day_to_365(rlds, 'rlds')
            list_rsds = extend_360_day_to_365(rsds, 'rsds')

            # Write out single weather stations as numpy array
            print("     ..write out", flush=True)
            station_coordinates, stations_wss = write_weather_data(list_wss)
            station_coordinates, stations_rlds = write_weather_data(list_rlds)
            station_coordinates, stations_rsds = write_weather_data(list_rsds)

            # Write to csv
            np.save(os.path.join(path_realization, "wss.npy"), stations_wss)
            np.save(os.path.join(path_realization, "rlds.npy"), stations_rlds)
            np.save(os.path.join(path_realization, "rsds.npy"), stations_rsds)

            #write_data.write_yaml(station_coordinates, os.path.join(path_realization, "stations.yml"))
            df = pd.DataFrame(station_coordinates, columns=['station_id', 'latitude', 'longitude'])
            df.to_csv(os.path.join(path_realization, "stations.csv"), index=False)

    print("... finished cleaning weather data")

clean_original_files = False
stich_weather_scenario = True

if clean_original_files:
    # ------------------------
    # Clean scenario data
    # ------------------------
    path = "X:/nismod/data/energy_demand/J-MARIUS_data"
    result_path = "X:/nismod/data/energy_demand/J-MARIUS_data"
    
    #years_to_clean = range(2020, 2026, 1)
    #years_to_clean = range(2026, 2031, 1)
    #years_to_clean = range(2031, 2041, 1)
    years_to_clean = range(2041, 2051, 1)

    weather_dat_prepare(path, result_path, years_to_clean)

if stich_weather_scenario:
    # ------------------------
    # Create realisation
    # ------------------------
    base_yr_remapped_weather_path = "X:/nismod/data/energy_demand/J-MARIUS_data/_weather_data_cleaned_modassar/2020"
    path = "X:/nismod/data/energy_demand/J-MARIUS_data"
    result_path = "X:/nismod/data/energy_demand/J-MARIUS_data"
    realisation_path = "X:/nismod/data/energy_demand/J-MARIUS_data/_weather_data_cleaned_modassar"
    realisation_out_path = "X:/nismod/data/energy_demand/J-MARIUS_data/_weather_realisation_modassar"
    path_stiching_table = "X:/nismod/data/energy_demand/J-MARIUS_data/stitching_table/stitching_table_nf.dat"

    realisation_list = range(100)
    #realisation_list = range(19, 100)

    create_realisation(
        base_yr_remapped_weather_path=base_yr_remapped_weather_path,
        realisation_list=realisation_list,
        realisation_path=realisation_path,
        realisation_out_path=realisation_out_path,
        path_stiching_table=path_stiching_table)
