"""Loading weather data (temp)
"""
import os
import csv
import logging
from collections import defaultdict
import numpy as np

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

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            station_id = str(row[0])
            latitude = float(row[1])
            longitude = float(row[2])

            temp_stations[station_id]['station_latitude'] = latitude
            temp_stations[station_id]['station_longitude'] = longitude

            # Plot weather stations
            logging.debug("Station name: %s,  Longitude: %s, Latitude: %s",
                station_id,
                longitude,
                latitude)

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
        station_id = str(file_path_split[1])
        temp_data[station_id] = np.loadtxt(path_file_to_read, delimiter=',')

    return temp_data
