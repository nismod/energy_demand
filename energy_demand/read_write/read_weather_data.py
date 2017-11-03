"""Loading weather data (temp)
"""
import os
import re
import csv
import numpy as np
import logging
from energy_demand.basic import date_prop
from collections import defaultdict

def read_weather_station_script_data(path_to_csv):
    """Read in weather stations from script data
    """
    temp_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            station_id = str(row[0])
            latitude = float(row[1])
            longitude = float(row[2])
            try:
                temp_stations[station_id]['station_latitude'] = latitude
                temp_stations[station_id]['station_longitude'] = longitude
            except KeyError:
                # Add station
                temp_stations[station_id] = {}
                temp_stations[station_id]['station_latitude'] = latitude
                temp_stations[station_id]['station_longitude'] = longitude

    return temp_stations

def read_weather_data_script_data(path_to_csv):
    """Read in weather data from script data


    """
    temp_data = {}
    all_txt_files_in_folder = os.listdir(path_to_csv)
    
    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_to_csv, file_path)
        file_path_split = file_path.split("__")
        station_id = str(file_path_split[1]) #str_id

        txt_data = np.loadtxt(path_file_to_read, delimiter=',')

        temp_data[station_id] = txt_data

    return temp_data

def read_yearly_weather_data_script_data(path_to_csv):
    """Read in weather data from script data

    Read in weather data from script data
    """
    temp_data = defaultdict(dict)
    all_txt_files_in_folder = os.listdir(path_to_csv)

    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_to_csv, file_path)
        file_path_split = file_path.split("__")
        station_id = int(file_path_split[1])
        year = int(file_path_split[2])

        txt_data = np.loadtxt(path_file_to_read, delimiter=',')

        temp_data[station_id][year] = txt_data

    return temp_data
