
import os
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap
import argparse
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from collections import defaultdict

from energy_demand.plotting import fig_p2_weather_val, result_mapping
from energy_demand.basic import basic_functions
from energy_demand.technologies import tech_related
from energy_demand.read_write import write_data
from energy_demand.basic import conversions
from energy_demand.plotting import basic_plot_functions

def plot_4_cross_map(
        cmap_rgb_colors,
        reclassified,
        result_path,
        path_shapefile_input,
        threshold=None,
        seperate_legend=False
    ):
    """Plot classifed 4 cross map
    """
    # --------------
    # Use Cartopy to plot geometreis with reclassified faceolor
    # --------------
    plt.figure(figsize=basic_plot_functions.cm2inch(10, 10)) #, dpi=150)
    proj = ccrs.OSGB() #'epsg:27700'
    ax = plt.axes(projection=proj)
    ax.outline_patch.set_visible(False)

    # set up a dict to hold geometries keyed by our key
    geoms_by_key = defaultdict(list)

    # for each records, pick out our key's value from the record
    # and store the geometry in the relevant list under geoms_by_key
    for record in shpreader.Reader(path_shapefile_input).records():
        region_name = record.attributes['name']
        geoms_by_key[region_name].append(record.geometry)

    # now we have all the geometries in lists for each value of our key
    # add them to the axis, using the relevant color as facecolor
    for key, geoms in geoms_by_key.items():
        region_reclassified_value = reclassified.loc[key]['reclassified']
        facecolor = cmap_rgb_colors[region_reclassified_value]
        ax.add_geometries(geoms, crs=proj, edgecolor='black', facecolor=facecolor, linewidth=0.1)

    # --------------
    # Create Legend
    # --------------
    legend_handles = [
        mpatches.Patch(color=cmap_rgb_colors[0], label=str("+- threshold {}".format(threshold))),
        mpatches.Patch(color=cmap_rgb_colors[1], label=str("a")),
        mpatches.Patch(color=cmap_rgb_colors[2], label=str("b")),
        mpatches.Patch(color=cmap_rgb_colors[3], label=str("c")),
        mpatches.Patch(color=cmap_rgb_colors[4], label=str("d"))]

    legend = plt.legend(
        handles=legend_handles,
        #title="test",
        prop={'size': 8},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False)

    if seperate_legend:
        basic_plot_functions.export_legend(
            legend,
            os.path.join(result_path, "{}__legend.pdf".format(result_path)))
        legend.remove()

    # Remove coordinates from figure
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    legend.get_title().set_fontsize(8)

    # --------
    # Labeling
    # --------
    plt.tight_layout()
    plt.savefig(os.path.join(result_path))
    plt.close()

def plot_4_cross_map_OLD(
        cmap_rgb_colors,
        reclassified,
        result_path,
        path_shapefile_input,
        threshold=None,
        seperate_legend=False
    ):
    """Plot classifed 4 cross map
    """
    # Load uk shapefile
    uk_shapefile = gpd.read_file(path_shapefile_input)

    # Merge stats to geopanda
    shp_gdp_merged = uk_shapefile.merge(reclassified, on='name')

    # Assign projection
    crs = {'init': 'epsg:27700'} #27700: OSGB_1936_British_National_Grid
    uk_gdf = gpd.GeoDataFrame(shp_gdp_merged, crs=crs)
    ax = uk_gdf.plot()

    uk_gdf['facecolor'] = 'white'

    for region in uk_gdf.index:
        reclassified_value = uk_gdf.loc[region]['reclassified']
        uk_gdf.loc[region, 'facecolor'] = cmap_rgb_colors[reclassified_value]

    # plot with face color attribute
    uk_gdf.plot(ax=ax, facecolor=uk_gdf['facecolor'], edgecolor='black', linewidth=0.1)

    legend_handles = [
        mpatches.Patch(color=cmap_rgb_colors[0], label=str("+- thr {}".format(threshold))),
        mpatches.Patch(color=cmap_rgb_colors[1], label=str("a")),
        mpatches.Patch(color=cmap_rgb_colors[2], label=str("b")),
        mpatches.Patch(color=cmap_rgb_colors[3], label=str("c")),
        mpatches.Patch(color=cmap_rgb_colors[4], label=str("d"))]

    legend = plt.legend(
        handles=legend_handles,
        #title="test",
        prop={'size': 8},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False)

    if seperate_legend:
        basic_plot_functions.export_legend(
            legend,
            os.path.join(result_path, "{}__legend.pdf".format(result_path)))
        legend.remove()

    # Remove coordinates from figure
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    legend.get_title().set_fontsize(8)

    # --------
    # Labeling
    # --------
    plt.tight_layout()
    plt.savefig(os.path.join(result_path))
    plt.close()

def total_annual_demand(
        df_data_input,
        path_shapefile_input,
        regions,
        pop_data,
        simulation_yr_to_plot,
        result_path,
        fig_name,
        field_to_plot,
        unit='GW',
        seperate_legend=True,
        bins=False
    ):
    """
    """
    if unit == 'GW':
        conversion_factor = 1
    elif unit == 'kW':
        conversion_factor = conversions.gwh_to_kwh(gwh=1) #GW to KW
    elif unit == 'percentage':
        conversion_factor = 1
    else:
        raise Exception("Not defined unit")

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

    #print("---- Calculate average per person")
    tot_person = sum(pop_sim_yr)
    #print(df_data_input.iloc[0])
    tot_demand = sum(df_data_input.iloc[0])
    ##print("TOT PERSON: " + str(tot_person))
    #print("TOT PERSON: " + str(tot_demand))
    #print('AVERAGE KW per Person " '+ str(tot_demand / tot_person))

    #print(df_data_input)
    regional_statistics_columns = [
        'name',
        'mean',
        'mean_norm_pop',
        #'mean_norm_pop_std_dev',
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
            #mean_norm_pop_std_dev[region_name],
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
    shp_gdp_merged = uk_shapefile.merge(df_stats, on='name')

    # Assign projection
    crs = {'init': 'epsg:27700'} #27700: OSGB_1936_British_National_Grid
    uk_gdf = gpd.GeoDataFrame(shp_gdp_merged, crs=crs)
    ax = uk_gdf.plot()

    # Assign bin colors according to defined cmap and whether
    # plot with min_max values or only min/max values
    #bin_values = [0, 0.0025, 0.005, 0.0075, 0.01]
    nr_of_intervals = 6

    if bins:
        bin_values = bins
    else:
        bin_values = result_mapping.get_reasonable_bin_values_II(
            data_to_plot=list(uk_gdf[field_to_plot]),
            nr_of_intervals=nr_of_intervals)
    print("field_to_plot: {} BINS: {}".format(field_to_plot, bin_values))

    uk_gdf, cmap_rgb_colors, color_zero, min_value, max_value = fig_p2_weather_val.user_defined_bin_classification(
        uk_gdf,
        field_to_plot,
        bin_values=bin_values)

    # plot with face color attribute
    uk_gdf.plot(ax=ax, facecolor=uk_gdf['bin_color'], edgecolor='black', linewidth=0.1)

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

    if seperate_legend:
        basic_plot_functions.export_legend(
            legend,
            os.path.join(result_path, "{}__legend.pdf".format(fig_name)))
        legend.remove()

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
    #plt.title("Peak demand over time")
    plt.tight_layout()
    #plt.show()
    plt.savefig(os.path.join(result_path, fig_name))
    plt.close()
