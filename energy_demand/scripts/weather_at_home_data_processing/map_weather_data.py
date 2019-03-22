"""
Get a the closest weather@home grid cell data for an input list of coordinates
"""
import os
import pandas as pd
import numpy as np
import haversine

from energy_demand.scripts.weather_scripts import weather_scenario
from energy_demand.geography import weather_station_location

def spatially_map_data(
        path_results,
        path_weather_at_home_stations,
        path_input_coordinates
    ):

    # Read in weather@home grid cells
    stations_grid_cells = pd.read_csv(path_weather_at_home_stations)

    # Read in input stations and coordinages to map 
    stations_to_map_to = pd.read_csv(path_input_coordinates)

    # Get all weather@home stations to get data
    mapped_stations = []

    # Iterate marius grid stations
    for station in enumerate(stations_to_map_to):

        # Marius weather station
        station_lat = row[1]
        station_lon = row[2]

        # Get closest Met Office weather station
        closest_uk_2015_met_office_station = get_closest_station_met_office(
            latitude_reg=station_lat,
            longitude_reg=station_lon,
            weather_stations=stations_grid_cells)
        
        # Add station
        mapped_stations[station_array_nr] = uk_met_office_stations_t_min[closest_uk_2015_met_office_station]



    # Filter data

    # Write out data
    # scenario_nr, year, day, parameter, value

    # Read wind and solar data
    uk_met_office_stations_t_min_array = np.load(os.path.join(path_2015_uk_data, "2015_t_min.npy"))
    
    # Convert data into dict with uk met office station ID
    nr_of_uk_met_office_stations = uk_met_office_stations_t_min_array.shape[0]
    
    stations = pd.read_csv(os.path.join(path_2015_uk_data, "2015_stations.csv"))
    df_stations = stations.set_index(('station_id'))
    stations_2015_met_office = df_stations.to_dict('index')

    uk_met_office_stations_t_min = {}
    uk_met_office_stations_t_max = {}
    for station_array_nr in range(nr_of_uk_met_office_stations):
        station_id = stations.get_value(station_array_nr,'station_id')
        uk_met_office_stations_t_min[station_id] = uk_met_office_stations_t_min_array[station_array_nr]

    # ------------------------------------------------------------
    # Read in MARIUS grid weather stations
    # ------------------------------------------------------------
    data_list = weather_scenario.get_temp_data_from_nc(path_example_grid_min_datafile_MARIUS, 'tasmin')

    # Coordinates and station id
    stations_marius = []
    print("NUMBE OF ROWS " + str(len(data_list)))
    cnt = 0
    station_id_cnt = 0
    for i  in data_list.index:
        if cnt == 359: #Originally only 360 days
            # Weather station metadata
            station_lon = data_list.get_value(i,'lon')
            station_lat = data_list.get_value(i,'lat')
            station_id = "station_id_{}".format(station_id_cnt)
            stations_marius.append([station_id, station_lat, station_lon]) #ID, latitude, longitude

            # Reset
            station_id_cnt += 1
            cnt = -1
        cnt += 1
    print("... finished read in marius weather stations")

    nr_of_marius_stations = len(stations_marius)

    

    # ----------------------------------------------------------
    # Write out data
    # ----------------------------------------------------------

    # Weather stations
    df = pd.DataFrame(stations_marius, columns=['station_id', 'latitude', 'longitude'])
    df.to_csv(os.path.join(path_2015_uk_data_remaped, "stations_2015.csv"), index=False)

    # Data
    np.save(os.path.join(path_2015_uk_data_remaped, "t_min.npy"), mapped_marius_station_data_t_min)
    np.save(os.path.join(path_2015_uk_data_remaped, "t_max.npy"), mapped_marius_station_data_t_max)


def calc_distance_two_points(lat_from, long_from, lat_to, long_to):
    """Calculate distance between two points

    https://pypi.org/project/haversine/#description

    Arguments
    ----------
    long_from : float
        Longitute coordinate from point
    lat_from : float
        Latitute coordinate from point
    long_to : float
        Longitute coordinate to point
    lat_to : float
        Latitue coordinate to point

    Return
    ------
    distance : float
        Distance
    """
    distance_in_km = haversine(
        (lat_from, long_from),
        (lat_to, long_to),
        unit='km')

    return distance_in_km

def get_closest_station_met_office(
        latitude_reg,
        longitude_reg,
        weather_stations
    ):
    """
    """
    closest_dist = 99999999999

    for station_id in weather_stations:

        lat_to = weather_stations[station_id]["latitude"]
        long_to = weather_stations[station_id]["longitude"]

        dist_to_station = calc_distance_two_points(
            lat_from=latitude_reg,
            long_from=longitude_reg,
            lat_to=lat_to,
            long_to=long_to)

        if dist_to_station < closest_dist:
            closest_dist = dist_to_station
            closest_id = station_id

    return closest_id
