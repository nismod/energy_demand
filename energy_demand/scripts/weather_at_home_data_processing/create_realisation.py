"""Create weather realisation
"""
import os
import pandas as pd
import numpy as np

from energy_demand.read_write import write_data
from energy_demand.basic import basic_functions

def remap_year(year):
    """Remap year"""

    if year in range(2015, 2020):
        year_remapped = 2020
    elif year == 2050:
        year_remapped = 2049
    else:
        year_remapped = year

    return year_remapped

def generate_weather_at_home_realisation(
        path_results,
        path_stiching_table,
        years=range(2015, 2051)
    ):
    """
    Before running, generate 2015 remapped data
    """
    # Create result path
    result_path_realizations = os.path.join(path_results, "_realizations")
    basic_functions.create_folder(result_path_realizations)

    # Read in stiching table
    df_path_stiching_table = pd.read_table(path_stiching_table, sep=" ")

    # Set year as index
    df_path_stiching_table = df_path_stiching_table.set_index('year')

    # Realisations
    realisations = list(df_path_stiching_table.columns)

    columns = ['timestep', 'longitude', 'latitude', 'yearday', 'wss', 'rlds', 'rsds']

    for scenario_nr in range(100):
        realisation = realisations[scenario_nr]

        print("... creating weather data for realisation " + str(realisation), flush=True)
        realisation_out = []

        for sim_yr in simulation_yrs:
            print("   ... year: " + str(sim_yr), flush=True)

            year = remap_year(sim_yr)

            stiching_name = df_path_stiching_table[realisation][year]
            path_weather_data = os.path.join(result_path_realizations, str(year), stiching_name)
            path_wss = os.path.join(path_weather_data, "wss.npy")
            path_rsds = os.path.join(path_weather_data, "rsds.npy")
            path_stations = os.path.join(path_weather_data, "stations.csv")

            wss = np.load(path_wss)
            rsds = np.load(path_rsds)

            stations = pd.read_csv(path_stations)
            stations['timestep'] = sim_yr

            nr_stations_array = len(list(stations.values))

            for station_cnt in range(nr_stations_array):
                wss_station = wss[station_cnt]
                rsds_station = rsds[station_cnt]
                station_long = stations.loc[station_cnt]['longitude']
                station_lat = stations.loc[station_cnt]['latitude']
                for yearday in range(365):
                    realisation_out.append(
                        [sim_yr, station_long, station_lat, yearday, wss_station[yearday], rsds_station[yearday]])

        print("...writing out")
        # Write data to csv
        df = pd.DataFrame(realisation_out, columns=columns)
        path_out_csv = os.path.join(result_path_realizations, "weather_data_{}.csv".format(realisation))
        df.to_csv(path_out_csv, index=False)
