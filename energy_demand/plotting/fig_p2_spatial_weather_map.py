
"""
"""
import os
from collections import defaultdict
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

from energy_demand.plotting import result_mapping
from energy_demand.plotting import fig_p2_weather_val
from energy_demand.read_write import data_loader
from energy_demand.read_write import read_weather_data
from energy_demand.plotting import basic_plot_functions

def run(
        path_to_weather_data,
        folder_path_weater_stations,
        path_shapefile,
        fig_path
    ):
    """

    """
    # ----------------------------------------------------------
    # Iterate all calculated weather stations
    # ----------------------------------------------------------
    weather_yrs_stations = read_weather_data.get_all_station_per_weather_yr(path_to_weather_data)

    weather_station_coordinates = data_loader.read_weather_stations_raw(folder_path_weater_stations)
    # ----------------------------------------------------------
    # Station nr and how many times over simulation period
    # ----------------------------------------------------------
    station_counting_over_yr = {}

    for weather_yr, stations in weather_yrs_stations.items():
        for station in stations:
            try:
                station_counting_over_yr[station].append(weather_yr)
            except:
                station_counting_over_yr[station] = [weather_yr]

    # Count number of years
    for station in station_counting_over_yr:
        station_counting_over_yr[station] = len(station_counting_over_yr[station])

    # ----------------------------------------------------------
    # Create dataframe
    #{station_id: all_weather_stations[weather_yr][station_id]}
    #df = pd.DataFrame({'src_id': [...], 'longitude': [...], 'latitude': [...]})
    #  ----------------------------------------------------------
    stations_as_dict = {}
    for station_id in station_counting_over_yr:
        try:
            stations_as_dict[station_id] = {
                'longitude': weather_station_coordinates[station_id]['longitude'],
                'latitude': weather_station_coordinates[station_id]['latitude'],
                'nr_of_weather_yrs': station_counting_over_yr[station_id]}
        except:
            print("The station nr {} coul not be found".format(station_id))

    df = pd.DataFrame.from_dict(stations_as_dict, orient='index')

    df['Coordinates'] = list(zip(df.longitude, df.latitude))
    df['Coordinates'] = df['Coordinates'].apply(Point)

    # Load uk shapefile
    uk_shapefile = gpd.read_file(path_shapefile)

    # Assign correct projection
    crs = {'init': 'epsg:27700'} #27700 == OSGB_1936_British_National_Grid
    uk_gdf = gpd.GeoDataFrame(uk_shapefile, crs=crs)

    # Plot
    ax = uk_gdf.plot(
        linewidth=0.3,
        color='whitesmoke',
        edgecolor='black',
        figsize=basic_plot_functions.cm2inch(25, 20))
        
    # plot coordinates
    crs = {'init': 'epsg:4326'}
    gdf = gpd.GeoDataFrame(df, geometry='Coordinates', crs=crs)
    gdf = gdf.to_crs({'init' :'epsg:27700'})

    field_to_plot = 'nr_of_weather_yrs'
    nr_of_intervals = 6

    bin_values = result_mapping.get_reasonable_bin_values_II(
        data_to_plot=list(gdf[field_to_plot]),
        nr_of_intervals=nr_of_intervals)

    print("BINS " + str(bin_values))
    gdf, cmap_rgb_colors, color_zero, min_value, max_value = fig_p2_weather_val.user_defined_bin_classification(
        gdf,
        field_to_plot,
        bin_values=bin_values,
        cmap_sequential='PuRd') #'Reds')

    # plot with face color attribute
    gdf.plot(
        ax=ax,
        markersize=20,
        facecolor=gdf['bin_color'],
        edgecolor='black',
        linewidth=0.3)

    legend_handles = result_mapping.add_simple_legend(
        bin_values,
        cmap_rgb_colors,
        color_zero,
        patch_form='circle')

    plt.legend(
        handles=legend_handles,
        title=str(field_to_plot),
        prop={'size': 8},
        loc='center left', bbox_to_anchor=(1, 0.5),
        frameon=False)
    try:
        os.remove(fig_path)
    except:
        pass
    plt.savefig(fig_path)

#def plot_map_