"""Loading weather data (temp)
"""
import os
import numpy as np

def read_weather_data_script_data(path_to_csv, temp_year_scenario):
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

        if year != temp_year_scenario:
            pass
        else:
            temp_data[station_id] = np.loadtxt(path_file_to_read, delimiter=',')

    return dict(temp_data)
