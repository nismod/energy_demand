"""This script changes temperatures for every year based on
assumptions about changing climte.
"""
import os
import csv
from datetime import date
from datetime import timedelta
import numpy as np
from energy_demand.scripts import s_shared_functions
from energy_demand.technologies import diffusion_technologies
from energy_demand.read_write import data_loader
from energy_demand.assumptions import assumptions

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

def read_assumption(path_to_csv):
    """
    Parameters
    ----------
    path_to_csv : str
        Path

    Return
    ------
    assumptions : dict
        Assumptions
    """
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
        print("... change climate for station_id {}".format(station_id))
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

                lin_diff_f = diffusion_technologies.linear_diff(
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
    file.write("{}, {}, {}, {}, {}".format(
        'station_id', 'year', 'day', 'hour', 'temp_in_celsius') + '\n'
              )

    for station_id in weather_data:
        print("... write temp data to csv for station_ID {}".format(station_id))
        for year in weather_data[station_id]:
            for day in range(365):
                for hour in range(24):
                    file.write("{}, {}, {}, {}, {}".format(
                        station_id,
                        year,
                        day,
                        hour,
                        weather_data[station_id][year][day][hour]) + '\n'
                              )
    file.close()

    print("... finished write_weather_data")
    return

def run(path_main, path_data_processed):
    """Function to run script
    """
    print("... start script {}".format(os.path.basename(__file__)))

    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(path_data_processed)

    data = data_loader.load_fuels(data)
    temperature_data = read_weather_data_script_data(
        data['local_paths']['path_processed_weather_data']
        )

    data['assumptions'] = assumptions.load_assumptions(data)
    assumptions_temp_change = data['assumptions']['climate_change_temp_diff_month']

    temp_climate_change = change_temp_climate_change(
        temperature_data, assumptions_temp_change, data['sim_param'])

    # Write out temp_climate_change
    write_chanted_temp_data(
        data['local_paths']['path_changed_weather_data'],
        temp_climate_change)

    print("... finished script {}".format(os.path.basename(__file__)))

    return
