"""Read raw weather data and weather stations
"""
import os
import re
import csv
from datetime import date
import collections
import numpy as np
import logging

def read_weather_data_raw(path_to_csv, placeholder_value=999):
    """Read in raw weather data

    Arguments
    ----------
    path_to_csv : string
        Path to weather data csv FileExistsError

    placeholder_value : int,default=999
        Placeholder number which is used
        in case no measurement exists for an hour

    Returns
    -------
    temp_stations : dict
        Contains temperature data in Degree Celsius
        (e.g. {'station_id: np.array((yeardays, 24))})

    Note
    ----
    The data are obtained from the Centre for Environmental Data Analysis

    [Download link]http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/ ()

    http://badc.nerc.ac.uk/artefacts/badc_datadocs/ukmo-midas/WH_Table.html (metadata)

    Weather Stations information: http://badc.nerc.ac.uk/search/midas_stations/
    http://badc.nerc.ac.uk/cgi-bin/midas_stations/search_by_name.cgi.py?name=&minyear=&maxyear=
    """
    temp_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')

        for row in read_lines: # select row
            date_measurement = row[0].split(" ")
            year = int(date_measurement[0].split("-")[0])
            month = int(date_measurement[0].split("-")[1])
            day = int(date_measurement[0].split("-")[2])
            hour = int(date_measurement[1][:2])

            # Weather station id
            station_id = int(row[5])

            # Air temperature in Degrees Celcius
            if row[35] == ' ': # If no data point
                air_temp = placeholder_value
            else:
                air_temp = float(row[35])

            # Get yearday
            yearday = date_to_yearday(year, month, day)

            # Add weather station if not already added to dict
            if station_id not in temp_stations:
                temp_stations[station_id] = np.zeros((365, 24), dtype=float)
            else:
                pass

            temp_stations[station_id][yearday][hour] = air_temp

    return temp_stations

def date_to_yearday(year, month, day):
    """Gets the yearday (julian year day) of a year minus one to correct because of python iteration

    Arguments
    ----------
    date_base_yr : int
        Year
    date_base_yr : int
        Month
    day : int
        Day

    Example
    -------
    5. January 2015 --> Day nr 5 in year --> -1 because of python --> Out: 4
    """
    date_y = date(year, month, day)
    yearday = date_y.timetuple().tm_yday - 1 #: correct because of python iterations

    return yearday

def clean_weather_data_raw(all_temp_stations, stations_outside_UK, placeholder_value=999):
    """Relace missing data measurement points and
    remove weater stations with no data

    Arguments
    ----------
    all_temp_stations : dict
        Raw data of temperature measurements
    stations_outside_UK : list
        Stations outside of UK
    placeholder_value : int
        Placeholder value for missing measurement point

    Returns
    -------
    temp_stations : dict
        Cleaned temp measurements

    Notes
    -----
    In the temperature mesaurements there are missing data
    points and for some stations, only 0 values are provided.

    From the raw dataset, all those stations are excluded where:
        - At least one day in a year has no measurement values
        - There is a day in the year with too many 0 values (zeros_day_crit criteria)
        - There is a day in a year with more than one missing measurement point
        - Are not located in UK

    In case only one measurement point is missing, this point gets interpolated.
    """
    zeros_day_crit = 10 # Number of 0 values there must be in a day in order to ignore weather station
    temp_stations = {}

    for station_id in all_temp_stations:
        if station_id in stations_outside_UK:
            pass
        else:
            # Iterate to see if data can be copyed
            copy_weater_station_data = True
            for day_nr, day in enumerate(all_temp_stations[station_id]):
                if np.sum(day) == 0:
                    copy_weater_station_data = False

                # Count number of zeroes in a day
                cnt_zeros = collections.Counter(day)[0]

                if cnt_zeros > zeros_day_crit:
                    copy_weater_station_data = False

            if copy_weater_station_data:
                temp_stations[station_id] = all_temp_stations[station_id]

                # Check if missing single temp measurements
                for day_nr, day in enumerate(all_temp_stations[station_id]):
                    if placeholder_value in day: # If day with missing data point

                        # check number of missing values
                        nr_of_missing_values = 0
                        for hour in day:
                            if hour == placeholder_value:
                                nr_of_missing_values += 1

                        # If only one placeholder
                        if nr_of_missing_values == 1:

                            # Interpolate depending on hour
                            for hour, temp in enumerate(day):
                                if temp == placeholder_value:

                                    if hour == 0: #If value of hours hour in day is missing
                                        # Replace with temperature of next hour
                                        all_temp_stations[station_id][day_nr][hour] = day[hour + 1]
                                    elif hour == 23:
                                        # Replace with temperature of previos hour
                                        all_temp_stations[station_id][day_nr][hour] = day[hour - 1]
                                    else:
                                        # Interpolate
                                        all_temp_stations[station_id][day_nr][hour] = (day[hour - 1] + day[hour + 1]) / 2

                        # if more than one temperture data point is missing in a day, remove weather station
                        if nr_of_missing_values > 1:
                            del temp_stations[station_id]
                            break

    return temp_stations

def read_weather_stations_raw(path_to_csv, stations_with_data):
    """Read in weather stations from csv
    file for which temp data are provided

    Parameter
    ---------
    path_to_csv : string
        Path to csv with stored weater station data

    Returns:
    --------
    weather_stations : dict
        Contains coordinates and station_id of weather stations

    Note
    ----
    Downloaded from MetOffice
    http://badc.nerc.ac.uk/cgi-bin/midas_stations/excel_list_station_details.cgi.py (09-05-2017)

    The weater station data was cleand manually to guarantee
    error-free loading (e.g. remove & or numbers in names)

    Not for all data a weather station ID is provided.
    More would be available here: https://badc.nerc.ac.uk/search/midas_stations/
    """
    weather_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        _headings = next(csvfile) # Skip first row
        _headings = next(csvfile) # Skip second row

        for row in csvfile:
            row_split = re.split('\s+', row)

            # Get only the float elements of each row
            all_float_values = []

            # Add station ID which is always first element
            all_float_values.append(float(row_split[0][1:]))

            for entry in row_split:
                try: # Test if can be converted to float
                    all_float_values.append(float(entry))
                except ValueError:
                    pass

            # Test if for weather station ID data is available
            if all_float_values[0] not in stations_with_data:
                continue
            else:
                station_id = int(all_float_values[0])
                weather_stations[station_id] = {
                    'station_latitude': float(all_float_values[1]),
                    'station_longitude': float(all_float_values[2])}

    return weather_stations

def write_weather_data(path_to_txt, weather_data):
    """Write wheather data to '.txt' file

    Arguments
    ----------
    path_to_txt : str
        Out path
    weather_data : dict
        Weather data
    """
    logging.info("... start write_weather_data")

    for station_id in weather_data:
        file_name = os.path.join(
            path_to_txt,
            "tempdata__{}__{}".format(str(station_id), ".txt"))

        np.savetxt(
            file_name,
            weather_data[station_id],
            delimiter=',')

    logging.info("... finished write_weather_data")
    return

def write_weather_stations(path_to_txt, weather_station):
    """Write wheather station data to csv file

    Arguments
    ----------
    path_to_txt : str
        Out path
    weather_station : dict
        Weater station data
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}".format('station_id', 'station_latitude', 'station_longitude') + '\n')
    for station_id in weather_station:
        file.write("{}, {}, {}".format(
            station_id, weather_station[station_id]['station_latitude'],
            weather_station[station_id]['station_longitude'])  + '\n')
    file.close()

    return

def run(local_paths):
    """Function to run script
    """
    print("... start script %s", os.path.basename(__file__))
    logging.info("... start script %s", os.path.basename(__file__))

    # Read in raw temperature data
    temp_data_raw = read_weather_data_raw(
        local_paths['folder_path_weater_data'])

    stations_outside_UK = [
        1605, # St. Helena
        1585,  # Gibraltar
        1609  # Falkland Islands
        ]

    # Clean raw temperature data
    temp_data = clean_weather_data_raw(
        temp_data_raw,
        stations_outside_UK)

    # Weather stations
    weather_stations = read_weather_stations_raw(
        local_paths['folder_path_weater_stations'],
        temp_data.keys())

    # Write out to csv files
    write_weather_stations(
        local_paths['changed_weather_station_data'],
        weather_stations)

    write_weather_data(
        local_paths['dir_raw_weather_data'],
        temp_data)

    logging.info("... finished script %s", os.path.basename(__file__))
    print("... finished script %s", os.path.basename(__file__))
    return
