"""Loading weather data (temp)
"""
import re
import csv
import numpy as np
from energy_demand.basic import date_handling
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def read_weather_station_script_data(path_to_csv):
    """Read in weather stations from script data
    """
    temp_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        # Iterate rows
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

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        # Iterate rows
        for row in read_lines:
            station_id = str(row[0])
            day = float(row[1])
            hour = float(row[2])
            temperature = float(row[3])

            try:
                temp_data[station_id][int(day)][int(hour)] = temperature
            except KeyError:
                temp_data[station_id] = np.zeros((365, 24))
                temp_data[station_id][int(day)][int(hour)] = temperature

    return temp_data
#'''

def read_weather_data_raw(path_to_csv, placeholder_value):
    """Read in raw weather data

    Parameters
    ----------
    path_to_csv : string
        Path to weather data csv FileExistsError

    placeholder_value : int
        Placeholder number which is used in case no measurment exists for an hour

    Returns
    -------
    temp_stations : dict
        Contains temperature data (e.g. {'station_id: np.array((yeardays, 24))})

    Note
    ----
    The data are obtained from the Centre for Environmental Data Analysis

    http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/ (Download link)

    http://badc.nerc.ac.uk/artefacts/badc_datadocs/ukmo-midas/WH_Table.html (metadata)
    """
    temp_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')

        # Iterate rows
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
            yearday = date_handling.convert_date_to_yearday(year, month, day)

            # Add weather station if not already added to dict
            if station_id not in temp_stations:
                temp_stations[station_id] = np.zeros((365, 24))

            # Add data
            temp_stations[station_id][yearday][hour] = air_temp

    return temp_stations

def clean_weather_data_raw(temp_stations, placeholder_value):
    """Relace missing data measurement points and remove weater stations with no data

    Parameters
    ----------
    temp_stations : dict
        Raw data of temperature measurements
    placeholder_value : int
        Placeholder value for missing measurement point

    Returns
    -------
    temp_stations_cleaned : dict
        Cleaned temp measurements

    Notes
    -----
    In the temperature mesaurements there are missing data points and for some stations, only 0 values are provided.
    From the raw dataset, all those stations are excluded where:
        - At least one day in a year has no measurement values
        - There is a day in the year with too many 0 values (zeros_day_crit criteria)
        - There is a day in a year with more than one missing measurement point

    In case only one measurement point is missing, this point gets interpolated.
    """
    zeros_day_crit = 10 # How many 0 values there must be in a day in order to ignore weater station
    temp_stations_cleaned = {}

    for station_id in temp_stations:

        # Iterate to see if data can be copyied or not
        copy_weater_station_data = True
        for day_nr, day in enumerate(temp_stations[station_id]):
            if np.sum(day) == 0:
                copy_weater_station_data = False

            # Count number of zeros in a day
            cnt_zeros = 0
            for hour in day:
                if hour == 0:
                    cnt_zeros += 1

            if cnt_zeros > zeros_day_crit:
                copy_weater_station_data = False

        if copy_weater_station_data:
            temp_stations_cleaned[station_id] = temp_stations[station_id]
        else: # Do not add data
            continue # Continue iteration

        # Check if missing single temp measurements
        for day_nr, day in enumerate(temp_stations[station_id]):
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
                            if hour == 0 or hour == 23:
                                if hour == 0: #If value of hours hour in day is missing
                                    temp_stations_cleaned[station_id][day_nr][hour] = day[hour + 1] #Replace with temperature of next hour
                                if hour == 23:
                                    temp_stations_cleaned[station_id][day_nr][hour] = day[hour - 1] # Replace with temperature of previos hour
                            else:
                                temp_stations_cleaned[station_id][day_nr][hour] = (day[hour - 1] + day[hour + 1]) / 2 # Interpolate

                # if more than one temperture data point is missing in a day, remove weather station
                if nr_of_missing_values > 1:
                    del temp_stations_cleaned[station_id]
                    break

    return temp_stations_cleaned

def read_weather_stations_raw(path_to_csv, stations_with_data):
    """Read in weather stations from csv file for which temp data are provided

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

    The weater station data was cleand manually to guarantee error-free loading (e.g. remove & or numbers in names)

    Not for all data a weather station ID is provided. More would be available here: https://badc.nerc.ac.uk/search/midas_stations/
    """
    weather_stations = {}

    with open(path_to_csv, 'r') as csvfile: # Read CSV file
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
                    'station_longitude': float(all_float_values[2])
                    }

    return weather_stations
#'''