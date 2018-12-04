"""Clean original temperature data
"""
import os
import csv
from collections import defaultdict
import logging
import numpy as np
import pandas as pd

from energy_demand.basic import date_prop
from energy_demand.basic import basic_functions
from energy_demand.read_write import data_loader

def count_sequence_of_zeros(sequence):
    cnt = 0
    max_cnt_zeros = 0
    for hour_val in sequence:
        if hour_val == 0:
            cnt += 1
        else:
            if cnt > max_cnt_zeros:
                max_cnt_zeros = cnt
            cnt = 0 #reset to zero again

    return max_cnt_zeros

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

def run(
        path_files,
        path_out_files,
        path_weather_stations,
        crit_min_max=False
    ):
    """Iterate weather data from MIDAS and
    generate annual hourly temperatre data files
    for every weather station by interpolating missing values
    http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/

    The data are obtained from the Centre for Environmental Data Analysis

    [Download link]http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/ ()

    http://badc.nerc.ac.uk/artefacts/badc_datadocs/ukmo-midas/WH_Table.html (metadata)

    Weather Stations information: http://badc.nerc.ac.uk/search/midas_stations/
    http://badc.nerc.ac.uk/cgi-bin/midas_stations/search_by_name.cgi.py?name=&minyear=&maxyear=

    The values are then written to a created folder as follows:

        year__stationname.txt

    Arguments
    ---------
    path_files : str
        Path to folder with original weather data files
    path_out_files : str
        Path to folder where the cleaned data are stored

    crit_missing_values : int
        Criteria of how many missing values there mus bet until
        a weather station is discarded
    crit_nr_of_zeros : int
        Criteria of how many zeros there must be per year until
        weather station is discarde
    nr_daily_zeros : int
        How many zero values there can be maxmum in a day in the
        year until the station is discarded

    Note
    -----
        - In case of a leap year the 29 of February is ignored
    """
    logging.info("... starting to clean original weather files")

    # Load coordinates of weather stations
    weather_stations = data_loader.read_weather_stations_raw(path_weather_stations)

    # Stations which are outisde of the uk and are ignored
    stations_outside_UK = [
        1605, # St. Helena
        1585, # Gibraltar
        1609] # Falkland Islands

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

    # Sort according to year
    all_annual_raw_files.sort()

    # Annual temperature file
    for file_name in all_annual_raw_files:
        print("... reading in file: " + str(file_name), flush=True)

        path_to_csv = os.path.join(path_files, file_name)
        temp_stations = {}
        temp_stations_min_max = defaultdict(dict)

        with open(path_to_csv, 'r') as csvfile:
            read_lines = csv.reader(csvfile, delimiter=',')

            for row in read_lines:
                date_measurement = row[0].split(" ")
                year = int(date_measurement[0].split("-")[0])
                month = int(date_measurement[0].split("-")[1])
                day = int(date_measurement[0].split("-")[2])
                hour = int(date_measurement[1][:2])

                yearday = date_prop.date_to_yearday(year, month, day)

                if date_prop.is_leap_year(year):
                    yearday = yearday - 1 # Substract because 29. of Feb is later ignored
                else:
                    pass

                year_hour = (yearday * 24) + hour

                # Weather station id
                station_id = int(row[5])

                # If station is outside uk or leap year day
                if (station_id in stations_outside_UK) or (month == 2 and day == 29):
                    pass
                else:
                    # Air temperature in Degrees Celcius
                    if row[35] == ' ' or row[35] == '': # If no data point
                        air_temp = placeholder_value
                    else:
                        air_temp = float(row[35])

                    # Add weather station if not already added to dict
                    if station_id not in temp_stations:
                        if crit_min_max:
                            temp_stations_min_max[station_id]['t_min'] = np.zeros((365), dtype="float")
                            temp_stations_min_max[station_id]['t_max'] = np.zeros((365), dtype="float")
                            temp_stations[station_id] = []
                    else:
                        pass

                    if air_temp is not placeholder_value:

                        if yearday not in temp_stations[station_id]:
                            temp_stations_min_max[station_id]['t_min'][yearday] = air_temp
                            temp_stations_min_max[station_id]['t_max'][yearday] = air_temp
                            temp_stations[station_id].append(yearday)

                        if crit_min_max:
                            # Update min and max daily temperature
                            if air_temp < temp_stations_min_max[station_id]['t_min'][yearday]:
                                temp_stations_min_max[station_id]['t_min'][yearday] = air_temp
                            if air_temp > temp_stations_min_max[station_id]['t_max'][yearday]:
                                temp_stations_min_max[station_id]['t_max'][yearday] = air_temp

        # ------------------------
        # Delete weather stations with missing daily data inputs
        # ------------------------
        stations_to_delete = []
        for station_id in temp_stations_min_max.keys():

            nans, x = nan_helper(temp_stations_min_max[station_id]['t_min'])
            nr_of_nans_t_min = list(nans).count(True)

            nans, x = nan_helper(temp_stations_min_max[station_id]['t_max'])
            nr_of_nans_t_max = list(nans).count(True)

            if nr_of_nans_t_min > 0 or nr_of_nans_t_max > 0:
                print("Station '{}' contains {} {} .nan values and is deleted".format(station_id, nr_of_nans_t_min, nr_of_nans_t_max))
                stations_to_delete.append(station_id)
        
        print("Number of stations to delete: {}".format(len(stations_to_delete)))
        for i in stations_to_delete:
            del temp_stations_min_max[i]

        # --------------------
        # Write out files
        # --------------------
        path_out_stations = os.path.join(path_out_files, '{}_stations.csv'.format(str(year)))
        path_out_t_min = os.path.join(path_out_files, "{}_t_min.npy".format(str(year)))
        path_out_t_max = os.path.join(path_out_files, "{}_t_max.npy".format(str(year)))

        # Check if weather station is defined
        stations_to_delete = []
        for name in temp_stations_min_max.keys():
            try:
               _ = weather_stations[name]['latitude']
               _ = weather_stations[name]['longitude']
            except KeyError:
                print("... no coordinates are available for weather station '{}'".format(name))
                stations_to_delete.append(name)

        print("... number of stations to delete: {}".format(len(stations_to_delete)))
        for name in stations_to_delete:
            del temp_stations_min_max[name]

        stations = list(temp_stations_min_max.keys())
        out_list = []
        for station_name in stations:
            out_list.append([station_name, weather_stations[station_name]['latitude'], weather_stations[station_name]['longitude']])

        # Write
        df = pd.DataFrame(np.array(out_list), columns=['station_id', 'latitude', 'longitude'])
        df.to_csv(path_out_stations, index=False)

        stations_t_min = list(i['t_min'] for i in temp_stations_min_max.values())
        stations_t_max = list(i['t_max'] for i in temp_stations_min_max.values())
        stations_t_min = np.array(stations_t_min)
        stations_t_max = np.array(stations_t_max)

        np.save(path_out_t_min, stations_t_min)
        np.save(path_out_t_max, stations_t_max)

    logging.info("... finished cleaning weather data")

run(
    path_files="//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/H-Met_office_weather_data/_meteo_data_2015",
    path_out_files="//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/H-Met_office_weather_data/_complete_meteo_data_all_yrs_cleaned_min_max",
    path_weather_stations="//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/H-Met_office_weather_data/cleaned_weather_stations.csv",
    crit_min_max=True)
