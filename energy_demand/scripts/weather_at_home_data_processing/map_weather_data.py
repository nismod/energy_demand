"""
Get a the closest weather@home grid cell data for an input list of coordinates
"""
import os
import pandas as pd
from haversine import haversine

def create_folder(path_folder, name_subfolder=None):
    """Creates folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str, default=None
        Name of subfolder to create
    """
    if not name_subfolder:
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
    else:
        path_result_subolder = os.path.join(path_folder, name_subfolder)
        if not os.path.exists(path_result_subolder):
            os.makedirs(path_result_subolder)

def spatially_map_data(
        path_results,
        result_out_path,
        path_weather_at_home_stations,
        path_input_coordinates,
        attributes,
        scenarios
    ):
    scenario_names = ["NF{}".format(i) for i in range(1, 101)]

    # Path to scenarios
    path_to_scenario_data = os.path.join(path_results, '_realizations')
    create_folder(result_out_path)
    result_out_path = "C:/AAA"
    # Read in input stations and coordinages to map
    stations_to_map_to = pd.read_csv(path_input_coordinates)

    # Read in MARIUS grid weather stations
    print("... read in weather stations per attribute", flush=True)

    weather_stations_per_attribute = {}
    for attribute in attributes:
        path_station = os.path.join(path_weather_at_home_stations, "stations_{}.csv".format(attribute))
        stations_grid_cells = pd.read_csv(path_station)
        stations_grid_cells = stations_grid_cells.set_index('station_id')

        # Convert into dict
        stations_grid_cells_dict = {}
        for index in stations_grid_cells.index:
            stations_grid_cells_dict[index] = {
                'longitude': stations_grid_cells.loc[index, 'longitude'],
                'latitude': stations_grid_cells.loc[index, 'latitude']}

        weather_stations_per_attribute[attribute] = stations_grid_cells_dict

    # Iterate geography and assign closest weather station data
    print("... Find closest stations")
    closest_weather_ids = {}
    for index in stations_to_map_to.index:
        closest_weather_ids[index] = {}
        station_lat = stations_to_map_to.loc[index, 'latitude']
        station_lon = stations_to_map_to.loc[index, 'longitude']

        for attribute in attributes:

            # Get closest weather station
            closest_marius_station = get_closest_weather_station(
                latitude_reg=station_lat,
                longitude_reg=station_lon,
                weather_stations=weather_stations_per_attribute[attribute])

            closest_weather_ids[index][attribute] = closest_marius_station

    # ----------------------------------------
    # Get data
    # ----------------------------------------
    for scenario_nr in scenarios:
        scenario_name = scenario_names[scenario_nr]
        for attribute in attributes:
            print("... create {} {}".format(scenario_name, attribute))
            stations_to_map_to_list = []
            path_data = os.path.join(path_to_scenario_data, "weather_data_{}__{}.csv".format(scenario_name, attribute))
            data = pd.read_csv(path_data)
            data = data.set_index("station_id")

            columns = list(data.columns)
            for cnt, column_entry in enumerate(columns):
                if column_entry == 'yearday':
                    position_yearday = cnt
                if column_entry == attribute:
                    position_attribute = cnt

            for year in range(2015, 2051):
                print("        ... {}".format(year), flush=True)
                data_yr = data.loc[data['timestep'] == year]

                for index in stations_to_map_to.index:
                    region_name = stations_to_map_to.loc[index, 'region_id']
                    closest_weather_station_id = closest_weather_ids[index][attribute]
                    closest_data = data_yr.loc[closest_weather_station_id]
                    closest_data_list = list(closest_data.values)

                    for row in closest_data_list:
                        stations_to_map_to_list.append([
                            region_name,
                            #attribute,
                            row[position_attribute],
                            year,
                            int(row[position_yearday])])

            # ----------------------------------------------------------
            # Write out data
            # ----------------------------------------------------------
            stations_to_map_to_out = pd.DataFrame(
                stations_to_map_to_list,
                columns=['region', attribute, 'timestep', 'yearday'])

            result_file = os.path.join(result_out_path, "{}__{}.csv".format(attribute, scenario_name))
            stations_to_map_to_out.to_csv(result_file, index=False)

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

def get_closest_weather_station(
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
