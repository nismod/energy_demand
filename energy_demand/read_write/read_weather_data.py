"""Loading weather data (temp)
"""
import os
import numpy as np
from collections import defaultdict

def get_all_weather_yrs(path_to_csvs):
    """Get all weather yrs
    TODO
    """
    weather_yrs = set([])

    all_txt_files_in_folder = os.listdir(path_to_csvs)

    for file_path in all_txt_files_in_folder:
        year = int(file_path.split("__")[0])
        weather_yrs.add(year)

    return list(weather_yrs)

def get_all_station_per_weather_yr(path_to_csvs):
    """
    """
    out_dict = {}

    all_txt_files_in_folder = os.listdir(path_to_csvs)

    for file_path in all_txt_files_in_folder:
        year = int(file_path.split("__")[0])
        weather_station_nr = int(file_path.split("__")[1][:-4])

        try:
            out_dict[year].append(weather_station_nr)
        except KeyError:
            out_dict[year] = [weather_station_nr]

    return out_dict

def read_weather_data_script_data(path_to_csv, weather_yrs_scenario):
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

        year = int(file_path.split("__")[0])
        station_id = int(file_path.split("__")[1][:-4]) #remove .txt

        if year == weather_yrs_scenario:
            temp_data[station_id] = np.loadtxt(path_file_to_read, delimiter=',')
        else:
            pass

    return temp_data
