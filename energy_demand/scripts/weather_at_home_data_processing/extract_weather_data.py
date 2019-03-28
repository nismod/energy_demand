"""Read original files into csv
"""
import os
import pytemperature
import xarray as xr
import numpy as np
import pandas as pd

def convert_to_celcius(df, attribute_to_convert):
    """# Convert Kelvin to Celsius (# Kelvin to Celsius)
    """
    df[attribute_to_convert] = df[attribute_to_convert].apply(pytemperature.k2c)
    return df

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
            station_lat = row[0]
            station_lon = row[1]

            station_id = "station_id_{}".format(station_id_cnt)

            #ID, latitude, longitude
            station_coordinates.append([station_id, station_lat, station_lon])

            # Reset
            station_data = np.zeros((365))
            station_id_cnt += 1
            cnt = -1
        cnt += 1

    return station_coordinates, stations_data

def create_folder(path_folder, name_subfolder=None):
    """Creates folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str, default=None
        Name of subfolder to create
    """
    if not name_subfolder:
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
    else:
        path_result_subolder = os.path.join(path_folder, name_subfolder)
        if not os.path.exists(path_result_subolder):
            os.makedirs(path_result_subolder)

def weather_dat_prepare(
        path_extracted_files,
        path_results,
        years=range(2020, 2050)
    ):
    """
    """
    folder_results = os.path.join(path_results, "_cleaned_csv")
    create_folder(folder_results)

    for year in years:
        path_year = os.path.join(folder_results, str(year))
        path_realizations = os.path.join(path_extracted_files, str(year))
        realization_names = os.listdir(path_realizations)

        for realization_name in realization_names:
            path_realization = os.path.join(path_year, realization_name)

            if os.path.exists(path_realization):
                pass #already extracted
            else:
                print("... processing {}  {}".format(str(year), str(realization_name)), flush=True)
                create_folder(path_realization)

                # ------------------------
                # Original data to extract
                # ------------------------
                path_wind = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_wss_daily_g2_{}.nc'.format(realization_name, year))
                path_rsds = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_rsds_daily_g2_{}.nc'.format(realization_name, year))
                path_tasmin = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_tasmin_daily_g2_{}.nc'.format(realization_name, year))
                path_tasmax = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_tasmax_daily_g2_{}.nc'.format(realization_name, year))

                wss = get_temp_data_from_nc(path_wind, 'wss')
                rsds = get_temp_data_from_nc(path_rsds, 'rsds')
                df_min = get_temp_data_from_nc(path_tasmin, 'tasmin')
                df_max = get_temp_data_from_nc(path_tasmax, 'tasmax')

                # Write out weather stations
                station_coordinates_wss = write_weather_stations(wss)
                station_coordinates_rsrds = write_weather_stations(rsds)
                station_coordinates_tmin = write_weather_stations(df_min)
                station_coordinates_tmax = write_weather_stations(df_max)

                # Write weather coordinates
                path_station_coordinates_wss = os.path.join(folder_results, "stations_wss.csv")
                if os.path.exists(path_station_coordinates_wss):
                    pass
                else:
                    df = pd.DataFrame(station_coordinates_wss, columns=['station_id', 'latitude', 'longitude'])
                    df.to_csv(os.path.join(folder_results, "stations_wss.csv"), index=False)

                path_station_coordinates_rsrds = os.path.join(folder_results, "stations_rsds.csv")
                if os.path.exists(path_station_coordinates_rsrds):
                    pass
                else:
                    df = pd.DataFrame(station_coordinates_rsrds, columns=['station_id', 'latitude', 'longitude'])
                    df.to_csv(path_station_coordinates_rsrds, index=False)

                path_station_coordinates_t_min = os.path.join(folder_results, "stations_t_min.csv")
                if os.path.exists(path_station_coordinates_t_min):
                    pass
                else:
                    df = pd.DataFrame(station_coordinates_tmin, columns=['station_id', 'latitude', 'longitude'])
                    df.to_csv(path_station_coordinates_t_min, index=False)

                path_station_coordinates_t_max = os.path.join(folder_results, "stations_t_max.csv")
                if os.path.exists(path_station_coordinates_t_max):
                    pass
                else:
                    df = pd.DataFrame(station_coordinates_tmax, columns=['station_id', 'latitude', 'longitude'])
                    df.to_csv(path_station_coordinates_t_max, index=False)

                # Convert Kelvin to Celsius (# Kelvin to Celsius)
                df_min = convert_to_celcius(df_min, 'tasmin')
                df_max = convert_to_celcius(df_max, 'tasmax')

                # Convert 360 day to 365 days
                print("     ..extend day", flush=True)
                list_wss = extend_360_day_to_365(wss, 'wss')
                list_rsds = extend_360_day_to_365(rsds, 'rsds')
                list_min = extend_360_day_to_365(df_min, 'tasmin')
                list_max = extend_360_day_to_365(df_max, 'tasmax')

                # Write out single weather stations as numpy array
                print("     ..write out", flush=True)
                data_wss = write_weather_data(list_wss)
                data_rsds = write_weather_data(list_rsds)
                t_min = write_weather_data(list_min)
                t_max = write_weather_data(list_max)
            
                # Write to csv
                np.save(os.path.join(path_realization, "wss.npy"), data_wss)
                np.save(os.path.join(path_realization, "rsds.npy"), data_rsds)
                np.save(os.path.join(path_realization, "t_min.npy"), t_min)
                np.save(os.path.join(path_realization, "t_max.npy"), t_max)

    print("... finished cleaning weather data")


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

            # Reset
            station_data = np.zeros((365))
            station_id_cnt += 1
            cnt = -1
        cnt += 1

    return stations_data

def write_weather_stations(data_list):
    """Write weather data to array
    data_list : list
        [[lat, long, yearday365, value]]
    """
    station_coordinates = []

    assert not len(data_list.values) % 360 #Check if dividable by 365
    nr_stations = int(len(data_list.values) / 360)

    station_id_cnt = 0
    cnt = 0

    for index in data_list.index:
        if cnt == 359:

            # Weather station metadata
            station_lon = data_list.loc[index, 'lon']
            station_lat = data_list.loc[index, 'lat']

            station_id = "station_id_{}".format(station_id_cnt)

            #ID, latitude, longitude
            station_coordinates.append([station_id, station_lat, station_lon])

            # Reset
            station_id_cnt += 1
            cnt = -1
        cnt += 1

    return station_coordinates
