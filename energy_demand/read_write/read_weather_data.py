"""Loading weather data (temp)
"""
import os
from collections import defaultdict
import numpy as np
import pandas as pd

def read_weather_station_script_data(path_to_csv):
    """Read in weather stations from script data

    Arguments
    ---------
    path_to_csv : str
        Path

    Returns
    -------
    temp_stations : dict
        Weather stations with coordinates
    """
    temp_stations = defaultdict(dict)

    raw_csv_file = pd.read_csv(path_to_csv)

    for index, row in raw_csv_file.iterrows():
        station_id = int(row['station_id'])
        temp_stations[station_id]['station_latitude'] = float(row['station_latitude'])
        temp_stations[station_id]['station_longitude'] = float(row['station_longitude'])

    return dict(temp_stations)

def read_weather_data_script_data(path_to_csv):
    """Read in weather data from script data

    Arguments
    ----------
    path_to_csv : str
        Path

    Returns
    -------
    temp_data : dict
        Temperature yh per weater station
    """
    temp_data = {}
    all_txt_files_in_folder = os.listdir(path_to_csv)

    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_to_csv, file_path)
        file_path_split = file_path.split("__")
        station_id = int(file_path_split[1])
        temp_data[station_id] = np.loadtxt(path_file_to_read, delimiter=',')

    return temp_data
