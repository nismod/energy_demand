"""
"""
import os
import csv
from collections import defaultdict
import numpy as np

from energy_demand.basic import date_prop
from energy_demand.basic import basic_functions

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])

    Taken from: https://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array
    """
    return np.isnan(y), lambda z: z.nonzero()[0]

def run(path_files, path_out_files, write_to_csv=True):
    """Iterate weather data from MIDAS and
    generate annual hourly temperatre data files
    for every weather station by interpolating missing values
    http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/
    """

    # Number of missing values until weather station quality
    # is considered as not good enough and ignored
    crit_missing_values = 100

    # Stations which are outisde of the uk and are ignored
    stations_outside_UK = [
        1605, # St. Helena
        1585, # Gibraltar
        1609  # Falkland Islands
        ]

    # Create out folder to store station specific csv
    if os.path.isdir(path_out_files):
        basic_functions.delete_folder(path_out_files)
        os.mkdir(path_out_files)
    else:
        os.mkdir(path_out_files)

    # Placeholder value for missing entry
    placeholder_value = np.nan

    # Read all files
    all_annual_raw_files = os.listdir(path_files)

    # Annual temperature file
    for file_name in all_annual_raw_files:
        print("   ...reading csv file: " + str(file_name))

        path_to_csv = os.path.join(path_files, file_name)

        temp_stations = {}

        with open(path_to_csv, 'r') as csvfile:
            read_lines = csv.reader(csvfile, delimiter=',')

            for row in read_lines:
                date_measurement = row[0].split(" ")
                year = int(date_measurement[0].split("-")[0])
                month = int(date_measurement[0].split("-")[1])
                day = int(date_measurement[0].split("-")[2])
                hour = int(date_measurement[1][:2])

                # Get yearday
                yearday = date_prop.date_to_yearday(year, month, day)

                year_hour = (yearday * 24) + hour

                # Weather station id
                station_id = int(row[5])

                if station_id in stations_outside_UK:
                    pass
                else:
                    # Air temperature in Degrees Celcius
                    if row[35] == ' ' or row[35] == '': # If no data point
                        air_temp = placeholder_value
                    else:
                        air_temp = float(row[35])

                    # Add weather station if not already added to dict
                    if station_id not in temp_stations:
                        temp_stations[station_id] = np.zeros((8760), dtype="float")
                    else:
                        pass
                    temp_stations[station_id][year_hour] = air_temp

        # ---------------------
        # Interpolate missing values (np.nan)
        # ---------------------
        temp_stations_cleaned_reshaped = {}

        for station in list(temp_stations.keys()):


            nans, x= nan_helper(temp_stations[station])
            nr_of_nans = list(nans).count(True)

            if nr_of_nans > crit_missing_values:
                print("Info - ignored station for year: {}  {} nr_of_nans: {}".format(station, year, nr_of_nans))
            else:

                # Interpolate missing np.nan values
                temp_stations[station][nans] = np.interp(
                    x(nans),
                    x(~nans),
                    temp_stations[station][~nans])

                # test if still np.nan value
                list_with_all_nan_args = list(np.argwhere(np.isnan(temp_stations[station])))

                if list_with_all_nan_args:
                    raise Exception("Still has np.nan entries")

                # Replace with day, hour array
                interpolated_values_reshaped = temp_stations[station].reshape(365, 24)
                temp_stations_cleaned_reshaped[station] = interpolated_values_reshaped

        # Write temperature data out to csv file
        if write_to_csv:
            for station_name, temp_values in temp_stations_cleaned_reshaped.items():

                file_name = "{}__{}.{}".format(year, station_name, "txt")

                path_out = os.path.join(path_out_files, file_name)

                np.savetxt(
                    path_out,
                    temp_values,
                    delimiter=",")

    '''final_files = read_weather_station_temp(
        path_files=path_out_files,
        years_to_load=[1966, 1987])
    print("======================================")
    print("Stations in all year")
    print(final_files.keys())
    print(len(list(final_files.keys())))'''

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

    for file_name in all_files:
        year = int(file_name.split("__")[0])                # year
        station_name = str(file_name.split("__")[1][:-4])   # station_name

        # temperature data
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

# -------------
run(path_files= "C:/Users/cenv0553/ED/data/_raw_data/_test_raw_weather_data",
    path_out_files ="C:/Users/cenv0553/ED/data/_raw_data/_test_raw_weather_data_cleaned")