"""Loading weather data (temp)
"""
import re
import csv
import numpy as np
import logging
from energy_demand.basic import date_handling
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def read_weather_station_script_data(path_to_csv):
    """Read in weather stations from script data
    """
    temp_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

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

        for row in read_lines:
            station_id = str(row[0])
            year = float(row[1])
            day = int(row[2])
            hour = int(row[3])
            temperature = float(row[4])

            try:
                temp_data[station_id]
            except KeyError:
                temp_data[station_id] = {}
            try:
                temp_data[station_id][year]
            except KeyError:
                temp_data[station_id][year] = np.zeros((365, 24))

            temp_data[station_id][year][day][hour] = temperature

    return temp_data

def read_changed_weather_data_script_data(path_to_csv, sim_period):
    """Read in weather data from script data
    """
    logging.debug("... read changed weather data")
    temp_data = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            station_id = str(row[0])
            year = int(row[1])
            day = float(row[2])
            hour = float(row[3])
            temperature = float(row[4])

            if year in sim_period:
                try:
                    temp_data[station_id][year][int(day)][int(hour)] = temperature

                except KeyError:

                    # Add station ID or year
                    try:
                        temp_data[station_id]
                    except KeyError:
                        temp_data[station_id] = {}
                    try:
                        temp_data[station_id][year]
                    except KeyError:
                        temp_data[station_id][year] = np.zeros((365, 24))

                    temp_data[station_id][year][int(day)][int(hour)] = temperature

    return temp_data
