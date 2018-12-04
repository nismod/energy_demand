"""
"""
import os
from collections import defaultdict
import numpy as np

def read_weather_station_temp(path_files, years_to_load=[]):
    """Get temperature values. Based on the defined
    years of which the temperature should be loaded,
    it is checked which weather stations occur
    in every year. Only these values are loaded

    Arguments
    ---------
    years_to_load : list
        Years to load temperature data

    Returns
    -------
    """
    container = {}

    all_files = os.listdir(path_files)

    # ----------------------------------------------------------
    #
    # ----------------------------------------------------------
    for file_name in all_files:
        year = int(file_name.split("__")[0])                # year
        station_name = str(file_name.split("__")[1][:-4])   # station_name
        try:
            container[station_name].append(year)
        except KeyError:
            container[station_name] = [year]

    # ---------------------------------------------------------
    # Test for which station names there is data for every year
    # ---------------------------------------------------------
    station_with_data_every_year = []
    for station_name, years in container.items():
        all_years_available = set(years_to_load).issubset(years)

        if all_years_available:
            station_with_data_every_year.append(station_name)

    print("Number of stations with every year")
    print(len(station_with_data_every_year))
    print("Stations with every year")
    print(station_with_data_every_year)
    #raise Exception
    # -------
    stations_in_all_y = defaultdict(dict)
    all_stations = defaultdict(dict)
    for station_name_to_load in station_with_data_every_year:

        for year_to_load in years_to_load:

            for file_name in all_files:
                year = int(file_name.split("__")[0])                # year
                station_name = str(file_name.split("__")[1][:-4])   # station_name

                if year_to_load == year and station_name_to_load == station_name:
                    file_path = os.path.join(path_files, file_name)
                    stations_in_all_y[station_name][year_to_load] = np.loadtxt(file_path, delimiter=',')
                else:
                    file_path = os.path.join(path_files, file_name)
                    all_stations[station_name][year_to_load] = np.loadtxt(file_path, delimiter=',')

    # print info
    print("Info----------------")
    for station_name, years in stations_in_all_y.items():
        print("Number of years in station {}: {}".format(len(list(years.keys())), station_name))
    
    print(" ")
    print("=======================")
    print(" ")
    for station_name, years in all_stations.items():
        print("Number of years in station {}: {}".format(len(list(years.keys())), station_name))
    return dict(stations_in_all_y)

read_weather_station_temp(
    path_files = "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/H-Met_office_weather_data/_year_selection_cleaned_2015_14_13",
    years_to_load=[2013,2014,2015]
)