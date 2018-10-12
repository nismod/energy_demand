"""Loading weather data (temp)
"""
import os
import numpy as np

def get_all_station_per_weather_yr(path_to_csvs, min_nr_of_stations=10):
    """Get all weather years and stations

    Arguments
    -----------
    path_to_csvs : path
        Path to temperature data
    min_nr_of_stations : int,default=10
        Number of stations which are needed in a year
        in order that year is used

    Returns
    ---------
    cleaned_out_dict : dict
        All years and stations which fulfill minimum
        number of stations criteria
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

    # Remove all years with lower number of stations
    cleaned_out_dict = {}
    for year, stations in out_dict.items():
        if len(stations) >= min_nr_of_stations:
            cleaned_out_dict[year] = stations
        else:
            print("The year {} has not enough stations".format(year))

    print("Total number of years: " + str(len(cleaned_out_dict.keys())))
    return cleaned_out_dict

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
