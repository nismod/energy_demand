"""Script to prepare weather data
Load weather simulation data

1. Download yearly data from here: http://catalogue.ceda.ac.uk/uuid/0cea8d7aca57427fae92241348ae9b03

2. Extract data

3. Run this script to get only the relevant data

Links
------
http://data.ceda.ac.uk//badc//weather_at_home/data/marius_time_series/CEDA_MaRIUS_Climate_Data_Description.pdf
http://data.ceda.ac.uk/badc/weather_at_home/data/marius_time_series/near_future/data/
"""
import os
import pytemperature
import xarray as xr
import numpy as np
import pandas as pd

from energy_demand.basic import basic_functions
from energy_demand.read_write import write_data

path = "X:/nismod/data/energy_demand/J-MARIUS_data"
result_path = "X:/nismod/data/energy_demand/J-MARIUS_data"

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

    # Copy every sithieth day over the year and duplicate it. Do this five times --> get from 360 to 365 days
    day_cnt, day_cnt_365 = 0, 0

    for index, row in df.iterrows():
        day_cnt += 1

        # Copy extra day
        if day_cnt in days_to_duplicate:
            out_list.append([row['lat'], row['lon'], day_cnt_365, row[attribute]])
            day_cnt_365 += 1

        # Copy day
        day_cnt_365 += 1
        out_list.append([row['lat'], row['lon'], day_cnt_365, row[attribute]])

        # Reset counter if next weather station
        if day_cnt == 360:
            day_cnt = 0
            day_cnt_365 = 0

    return out_list

def write_wether_data(data_list):
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
            '''station_coordinates[station_id] = {
                'longitude':station_lat,
                'latitude': station_lon}'''
            station_coordinates.append([station_id, station_lat, station_lon]) #ID, latitude, longitude

            # Reset
            station_data = np.zeros((365))
            station_id_cnt += 1
            cnt = -1
        cnt += 1

    return station_coordinates, stations_data




def calc_HDD_from_min_max(t_min, t_max, base_temp):
    """Calculate hdd for every day and weather station

    The Meteorological Office equations


    """
    hdd_array = np.zeros((365))

    # Calculate hdd
    for yearday in range(365):
        case_met_equation = get_meterological_equation_case(t_min, t_max, base_temp)

    return hdd_array




# Load stiching table to create weather scenario
def weather_dat_prepare(data_path, result_path):
    """
    """
    # All folders
    '''
    all_files = os.listdir(path)
    folder_names = []
    for i in all_files:
        try:
            folder_names.append(int(i)) #get years
        except:
            pass
    '''
    folder_names = range(2020, 2049)
    folder_names = [2020, 2025, 2030, 2035, 2040, 2045, 2049]
    print("folder_name " + str(folder_names))

    # Create reulst folders
    result_folder = os.path.join(result_path, "_weather_data_cleaned")
    basic_functions.create_folder(result_folder)

    for folder_name in folder_names:

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
            path_tasmin = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_tasmin_daily_g2_{}.nc'.format(realization_name, year))
            path_tasmax = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_tasmax_daily_g2_{}.nc'.format(realization_name, year))
            
            # Load data
            print("     ..load data", flush=True)
            df_min = get_temp_data_from_nc(path_tasmin, 'tasmin')
            df_max = get_temp_data_from_nc(path_tasmax, 'tasmax')

            # Convert Kelvin to Celsius (# Kelvin to Celsius)
            print("     ..convert temp", flush=True)
            df_min = convert_to_celcius(df_min, 'tasmin')
            df_max = convert_to_celcius(df_max, 'tasmax')

            # Convert 360 day to 365 days
            print("     ..extend day", flush=True)
            list_min = extend_360_day_to_365(df_min, 'tasmin')
            list_max = extend_360_day_to_365(df_max, 'tasmax')

            # Write out single weather stations as numpy array
            print("     ..write out", flush=True)
            station_coordinates, stations_t_min = write_wether_data(list_min)
            station_coordinates, stations_t_max = write_wether_data(list_max)

            # Write to csv
            np.save(os.path.join(path_realization, "t_min.npy"), stations_t_min)
            np.save(os.path.join(path_realization, "t_max.npy"), stations_t_max)

            #write_data.write_yaml(station_coordinates, os.path.join(path_realization, "stations.yml"))
            columns = ['station_id', 'latitude', 'longitude']

            df = pd.DataFrame(station_coordinates, columns=columns)
            df.to_csv(os.path.join(path_realization, "stations.csv"), index=False)

    print("... finished cleaning weather data")

weather_dat_prepare(path, result_path)


'''
path_tasmax = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmax_daily_g2_2020.nc"
path_tasmin = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmin_daily_g2_2020.nc"

out_path = "C:/_scrap/test.csv"
out_path_station_names = "C:/_scrap/station_position.csv"

# Load data
df_max = get_temp_data_from_nc(path_tasmax, 'tasmax')
df_min = get_temp_data_from_nc(path_tasmin, 'tasmin')

# Convert Kelvin to Celsius (# Kelvin to Celsius)
df_max['tasmax'] = convert_to_celcius(df_max, 'tasmax')
df_min['tasmin'] = convert_to_celcius(df_min, 'tasmin')

# Convert 360 day to 365 days
list_max = extend_360_day_to_365(df_max, 'tasmax')
list_min = extend_360_day_to_365(df_min, 'tasmin')

# Write out single weather stations as numpy array
station_coordinates, stations_t_max = write_wether_data(list_max, list_max)
station_coordinates, stations_t_min = write_wether_data(list_max, list_min)

# Write out coordinates of weather data to csv
print(len(stations_t_max))
print(len(stations_t_min))
'''


# Convert weather station data to HDD days
'''for station_nr in enumerate(station_coordinates):

    t_min = stations_t_min[station_nr]
    t_max = stations_t_max[station_nr]

    calc_hdd_min_max(t_min, t_max)'''

