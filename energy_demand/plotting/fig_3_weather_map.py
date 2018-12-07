
import os
import logging
import copy
import math
import numpy as np
import geopandas as gpd
import pandas as pd
import palettable
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

from energy_demand.plotting import fig_p2_weather_val, result_mapping
from energy_demand.basic import basic_functions
from energy_demand.technologies import tech_related
from energy_demand.read_write import write_data
from energy_demand.basic import conversions

def total_annual_demand(
        df_data_input,
        path_shapefile_input,
        regions,
        pop_data,
        simulation_yr_to_plot,
        result_path,
        fig_name,
        field_to_plot,
        unit='GW'
    ):
    """
    """
    if unit == 'GW':
        conversion_factor = 1
    if unit == 'kWh':
        conversion_factor = conversions.gwh_to_kwh(gwh=1) #GW to KW

    df_data_input = df_data_input * conversion_factor

    # Load uk shapefile
    uk_shapefile = gpd.read_file(path_shapefile_input)

    # Population of simulation year
    pop_sim_yr = pop_data[simulation_yr_to_plot]

    regions = list(df_data_input.columns)
    nr_of_regions = df_data_input.shape[1]
    nr_of_realisations = df_data_input.shape[0]

    # Mean over all realisations
    mean = df_data_input.mean(axis=0)

    # Mean normalized with population
    mean_norm_pop = df_data_input.mean(axis=0) / pop_sim_yr

    # Standard deviation over all realisations
    std_dev = df_data_input.std(axis=0)

    max_entry = df_data_input.max(axis=0) #maximum entry for every hour
    min_entry = df_data_input.min(axis=0) #maximum entry for every hour

    print("---- Calculate average per person")
    tot_person = sum(pop_sim_yr)
    print(df_data_input.iloc[0])
    tot_demand = sum(df_data_input.iloc[0])
    print("TOT PERSON: " + str(tot_person))
    print("TOT PERSON: " + str(tot_demand))
    print('AVERAGE KW per Person " '+ str(tot_demand / tot_person))

    print(df_data_input)
    regional_statistics_columns = [
        'name',
        'mean',
        'mean_norm_pop',
        'std_dev']#
        #'diff_av_max',
        #'mean_pp',
        #'diff_av_max_pp',
        #'std_dev_average_every_h',
        #'std_dev_peak_h_norm_pop']

    df_stats = pd.DataFrame(columns=regional_statistics_columns)

    for region_name in regions:

        line_entry = [[
            str(region_name),
            mean[region_name],
            mean_norm_pop[region_name],
            std_dev[region_name]
            #diff_av_max,
            #mean_peak_h_pp,
            #diff_av_max_pp,
            #std_dev_average_every_h,
            #std_dev_peak_h_norm_pop
            ]]

        line_df = pd.DataFrame(
            line_entry,
            columns=regional_statistics_columns)

        df_stats = df_stats.append(line_df)

    # ---------------
    # Create spatial maps
    # http://darribas.org/gds15/content/labs/lab_03.html
    # http://nbviewer.jupyter.org/gist/jorisvandenbossche/57d392c085901eb4981054402b37b6b1
    # ---------------
    # Merge stats to geopanda
    shp_gdp_merged = uk_shapefile.merge(
        df_stats,
        on='name')

    # Assign projection
    crs = {'init': 'epsg:27700'} #27700: OSGB_1936_British_National_Grid
    uk_gdf = gpd.GeoDataFrame(shp_gdp_merged, crs=crs)
    ax = uk_gdf.plot()

    # Assign bin colors according to defined cmap and whether
    # plot with min_max values or only min/max values
    #bin_values = [0, 0.0025, 0.005, 0.0075, 0.01]
    nr_of_intervals = 6

    bin_values = result_mapping.get_reasonable_bin_values_II(
        data_to_plot=list(uk_gdf[field_to_plot]),
        nr_of_intervals=nr_of_intervals)

    print("BINS " + str(bin_values))

    uk_gdf, cmap_rgb_colors, color_zero, min_value, max_value = fig_p2_weather_val.user_defined_bin_classification(
        uk_gdf,
        field_to_plot, 
        bin_values=bin_values)

    # plot with face color attribute
    uk_gdf.plot(ax=ax, facecolor=uk_gdf['bin_color'], edgecolor='black', linewidth=0.5)

    #shp_gdp_merged.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    #ax = uk_gdf.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    #uk_gdf[uk_gdf['name'] == 'E06000024'].plot(ax=ax, facecolor='green', edgecolor='black')
    #uk_gdf[uk_gdf['diff_av_max'] < 0.01].plot(ax=ax, facecolor='blue', edgecolor='black')

    # Get legend patches TODO IMPROVE
    # TODO IMRPVE: MAKE CORRECT ONE FOR NEW PROCESSING
    legend_handles = result_mapping.get_legend_handles(
        bin_values[1:-1],
        cmap_rgb_colors,
        color_zero,
        min_value,
        max_value)

    legend = plt.legend(
        handles=legend_handles,
        title="Unit: {} field: {}".format(unit, field_to_plot),
        prop={'size': 8},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False)

    # Remove coordinates from figure
    ax.set_yticklabels([])
    ax.set_xticklabels([])

    legend.get_title().set_fontsize(8)

    # PLot bins on plot
    '''plt.text(
        0,
        -20,
        bin_values[:-1],
        fontsize=8)'''

    # --------
    # Labeling
    # --------
    #plt.title("tttt")

    plt.tight_layout()
    #plt.show()

    plt.savefig(os.path.join(result_path, fig_name))
    plt.close()
