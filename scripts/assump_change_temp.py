"""This file changes temperatures for every year based on
assumptions about changing climte
"""
import os
import csv
from datetime import date
from datetime import timedelta
import numpy as np

# Functions for script
# --------------------
def fullyear_dates(start, end):
    """Calculates all dates between a star and end date.

    Parameters
    ----------
    start : date
        Start date
    end : date
        End date

    Returns
    -------
    list_dates : list
        A list with all daily dates
    """
    list_dates = []
    span = end - start
    for day in range(span.days + 1):
        list_dates.append(start + timedelta(days=day))

    return list_dates

def linear_diff(base_yr, curr_yr, value_start, value_end, sim_years):
    """This function assumes a linear fuel_enduse_switch diffusion.

    Parameters
    ----------
    base_yr : int
        The year of the current simulation.
    curr_yr : int
        The year of the current simulation.
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    sim_years : str
        Total number of simulated years.

    Returns
    -------
    fract_sy : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    # If current year is base year, return zero
    if curr_yr == base_yr or sim_years == 0:
        fract_sy = 0
    else:
        #-1 because in base year no change
        fract_sy = ((value_end - value_start) / (sim_years - 1)) * (curr_yr - base_yr)

    return fract_sy

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

def convert_yearday_to_date(year, yearday_python):
    """Gets the yearday of a year minus one to correct because of python iteration

    Parameters
    ----------
    year : int
        Year
    yearday_python : int
        Yearday - 1
    """
    date_new = date(year, 1, 1) + timedelta(yearday_python)

    return date_new

def read_assumption_sim_param(path_to_csv):
    assumptions = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(csvfile) # Skip headers

        for row in read_lines:
            try:
                assumptions[str(row[0])] = float(row[1])
            except:
                assumptions[str(row[0])] = None

    # Redefine sim_period_yrs
    assumptions['sim_period'] = range(
        int(assumptions['base_yr']),
        int(assumptions['end_yr']) + 1,
        5
        )

    # Redefine sim_period_yrs
    assumptions['list_dates'] = fullyear_dates(
        start=date(int(assumptions['base_yr']), 1, 1),
        end=date(int(assumptions['base_yr']), 12, 31))

    return assumptions


def read_assumption(path_to_csv):

    assumptions = []

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(csvfile) # Skip headers

        for row in read_lines:
            assumptions.append(float(row[1]))

    return assumptions

def change_temp_climate_change(temperature_data, assumptions_temp_change, sim_param):
    """Change temperature data for every year depending on simple climate change assumptions

    Parameters
    ---------
    data : dict
        Data

    Returns
    -------
    temp_climate_change : dict
        Adapted temperatures for all weather stations depending on climate change assumptions
    """
    temp_climate_change = {}

    # Change weather for all weater stations
    for station_id in temperature_data:
        temp_climate_change[station_id] = {}

        # Iterate over simulation period
        for curr_yr in sim_param['sim_period']:
            temp_climate_change[station_id][curr_yr] = np.zeros((365, 24))

            # Iterate every month and substract
            for yearday in range(365):

                # Create datetime object
                date_object = convert_yearday_to_date(
                    int(sim_param['base_yr']),
                    int(yearday)
                    )

                # Get month of yearday
                month_yearday = date_object.timetuple().tm_mon - 1

                # Get linear diffusion of current year
                temp_by = 0
                temp_ey = assumptions_temp_change[month_yearday]

                lin_diff_f = linear_diff(
                    sim_param['base_yr'],
                    curr_yr,
                    temp_by,
                    temp_ey,
                    sim_param['sim_period_yrs']
                )

                # Iterate hours of base year
                for hour, temp_old in enumerate(temperature_data[station_id][yearday]):
                    temp_climate_change[station_id][curr_yr][yearday][hour] = temp_old + lin_diff_f

    return temp_climate_change

def write_chanted_temp_data(path_to_txt, weather_data):
    """Write wheather data to csv file
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}".format(
        'station_id', 'day', 'hour', 'temp_in_celsius') + '\n'
              )

    for station_id in weather_data:
        for year in weather_data[station_id]:
            for day in range(365):
                for hour in range(24):
                    file.write("{}, {}, {}, {}, {}".format(
                        station_id, year, day, hour, weather_data[station_id][year][day][hour]) + '\n'
                          )
    file.close()

    print("...finished write_weather_data")
    return

# ----------------------
# Paths
# ----------------------
print("..start script {}".format(os.path.basename(__file__)))

CSV_PATH = os.path.join(
    os.path.dirname(__file__)[:-8], r'data\data_scripts\assumptions_from_db\assumptions_climate_change_temp.csv')
PATH_WEATHER_DATA = os.path.join(
    os.path.dirname(__file__)[:-8], r'data\data_scripts\weather_data.csv')
CSV_PATH_SIM_PARAM = os.path.join(
    os.path.dirname(__file__)[:-8], r'data\data_scripts\assumptions_from_db\assumptions_sim_param.csv')
CSV_PATH_OUT_TEMP_CLIMATE = os.path.join(
    os.path.dirname(__file__)[:-8], r'data\data_scripts\weather_data_changed_climate.csv')

# ----------------
# Load assumptions
# ----------------
TEMPERATURE_DATA = read_weather_data_script_data(PATH_WEATHER_DATA)
ASSUMPTIONS_TEMP_CHANGE = read_assumption(CSV_PATH)
SIM_PARAM = read_assumption_sim_param(CSV_PATH_SIM_PARAM)

TEMP_CLIMATE_CHANGE = change_temp_climate_change(
    TEMPERATURE_DATA, ASSUMPTIONS_TEMP_CHANGE, SIM_PARAM)

# Write out temp_climate_change
write_chanted_temp_data(CSV_PATH_OUT_TEMP_CLIMATE, TEMP_CLIMATE_CHANGE)

print("..finished script {}".format(os.path.basename(__file__)))
