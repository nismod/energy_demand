"""Loading weather data (temp)
"""
import os
import csv
from collections import defaultdict
import numpy as np

def read_weather_station_script_data(path_to_csv):
    """Read in weather stations from script data
    """
    temp_stations = defaultdict(dict)

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            station_id = str(row[0])
            latitude = float(row[1])
            longitude = float(row[2])

            temp_stations[station_id]['station_latitude'] = latitude
            temp_stations[station_id]['station_longitude'] = longitude

    return dict(temp_stations)

def read_weather_data_script_data(path_to_csv):
    """Read in weather data from script data

    Arguments
    ----------
    path_to_csv : str
        Path
    """
    temp_data = {}
    all_txt_files_in_folder = os.listdir(path_to_csv)

    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_to_csv, file_path)
        file_path_split = file_path.split("__")
        station_id = str(file_path_split[1]) #str_id

        temp_data[station_id] = np.loadtxt(path_file_to_read, delimiter=',')

    return temp_data
