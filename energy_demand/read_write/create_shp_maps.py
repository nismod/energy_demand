#http://darribas.org/gds15/content/labs/lab_03.html
#https://stackoverflow.com/questions/31755886/choropleth-map-from-geopandas-geodatafame
# http://geopandas.org
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import pysal as ps
from pysal.contrib.viz import mapping as maps
import numpy as np
from energy_demand.basic import basic_functions
from pysal.esda.mapclassify import User_Defined

def hack_classification(lad_geopanda_shp, bins, color_list, field_name_to_plot):
    """OWn classification with bins

    # https://automating-gis-processes.github.io/2016/Lesson5-interactive-map-bokeh.html
    # http://pysal.readthedocs.io/en/latest/library/esda/mapclassify.html 'User_defined' is not yet implemented

    Work arounde taken from
    Source: https://stackoverflow.com/questions/41783090/plotting-a-choropleth-map-with-geopandas-using-a-user-defined-classification-s
    """
    from matplotlib.colors import LinearSegmentedColormap

    # Maps values to a bin.
    # The mapped values must start at 0 and end at 1.
    def bin_mapping(x):
        for idx, bound in enumerate(bins):
            if x < bound:
                return idx / (len(bins) - 1.0)

    # Create the list of bin labels and the list of colors 
    # corresponding to each bin
    bin_labels = [idx / (len(bins) - 1.0) for idx in range(len(bins))]

    # Create the custom color map
    cmap = LinearSegmentedColormap.from_list(
        'mycmap', 
        [(lbl, color) for lbl, color in zip(bin_labels, color_list)])

    # Reclassify
    lad_geopanda_shp['reclassified'] = lad_geopanda_shp[field_name_to_plot].apply(bin_mapping)

    return lad_geopanda_shp, cmap

def plot_lad_national(
        lad_geopanda_shp,
        field_name_to_plot,
        result_path
    ):
    """Create plot of LADs and store to file

    Arguments
    ---------
    column : str
        Column to plot

    Info
    -----
        Map color:  https://matplotlib.org/users/colormaps.html

    http://darribas.org/gds_scipy16/ipynb_md/02_geovisualization.html
    https://stackoverflow.com/questions/41783090/plotting-a-choropleth-map-with-geopandas-using-a-user-defined-classification-s 
    """
    fig_name = os.path.join(
        result_path,
        field_name_to_plot)

    fig_map, axes = plt.subplots(
        1,
        figsize=(5, 8))


    # -----------------------------
    # Plot map wtih all value hues
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_name_to_plot,
        cmap='OrRd',
        legend=True)
    plt.show()'''

    # ------------
    # Own classification (work around)
    # ------------

    # Own classification bins
    bins = [x for x in range(0, 1000000, 200000)]

    # Own colors
    color_list = ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c'] # '#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']

    lad_geopanda_shp, cmap = hack_classification(lad_geopanda_shp, bins, color_list, field_name_to_plot)

    lad_geopanda_shp.plot(
        axes=axes,
        column='reclassified',
        cmap=cmap,
        alpha=1,
        vmin=0,
        vmax=1)
    
    # -----------------------------
    # Plot map wtih all value hues
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_name_to_plot,
        cmap='OrRd',
        legend=True)'''

    # -----------------------------
    # Plot map wtih quantiles
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_name_to_plot,
        scheme='QUANTILES',
        k=5,
        cmap='OrRd',
        legend=True)'''

    # -----------------------------
    # Plot map wtih quantiles
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_name_to_plot,
        scheme='equal_interval',
        k=5,
        cmap='OrRd',
        legend=True)'''

    #lad_geopanda_shp.User_Defined(lad_geopanda_shp, bins)
    '''lad_geopanda_shp.assign(cl=interval_data.yb).plot(
        column='cl',
        categorical=True,
        k=10,
        cmap='OrRd',
        linewidth=0.1,
        ax=axes,
        edgecolor='white',
        legend=True,
        scheme='User_Defined')'''


    # Title
    fig_map.suptitle(field_name_to_plot)

    # Make that not distorted
    lims = plt.axis('equal') 

    # Save figure
    plt.savefig(fig_name)
    plt.show()

def merge_data_to_shp(shp_gdp, merge_data, unique_merge_id):
    """Merge data to geopanda dataframe which is read
    from shapefile

    Steps
    - create dataframe from merge_data

    Arguments
    ----------
    merge_data : dict
        Data to merge
    unique_merge_id : str
        Unique ID to make attribute merge

    Example for merge_data
    ------------------------
        merge_data = {
            name_of_new_data_column: [9999, 9999],
            merge_unique_ID: ['W06000016', 'S12000013']}

    More info: http://geopandas.org/mergingdata.html
    """
    # Create a GeoDataFrame with joing attribute and values
    merge_dataframe = pd.DataFrame(
        data=merge_data)

    # Merge
    shp_gdp_merged = shp_gdp.merge(
        merge_dataframe,
        on=unique_merge_id)

    print("New fields: " + str(list(shp_gdp_merged)))

    return shp_gdp_merged

def test():
    """
    """
    shapefile_link = 'C:/Users/cenv0553/nismod/data_energy_demand/_raw_data/C_LAD_geography/lad_2016.shp'
    lads_shapes = gpd.read_file(shapefile_link)

    # Variables
    name_of_new_data_column = 'testdata'    # Name of merged data
    column_to_plot = 'y_2016_2'             # Name of column to plot data

    merge_data = {
        name_of_new_data_column: [9999, 9999],
        'geo_code': ['W06000016', 'S12000013']}

    # Merge
    lads_shapes = merge_data_to_shp(lads_shapes, merge_data, 'geo_code')

    # Get all data rows of dataframe
    print(list(lads_shapes))
    print("DATA")
    print(lads_shapes[column_to_plot])
    print("------------------")
    # ---------------------------
    # PLots
    # ---------------------------
    fig_map, axes = plt.subplots(1, figsize=(5, 10))

    '''ax = plot(
        lads_shapes[name_of_new_data_column],
        column=name_of_new_data_column,
        scheme='QUANTILES',
        k=3,
        colormap='OrRd',
        legend=True)'''
    lads_shapes.plot(
        axes=axes,
        column=column_to_plot,
        scheme='QUANTILES',
        k=5,
        colormap='OrRd',
        legend=True)

    fig_map.suptitle('testtile')
    lims = plt.axis('equal') #Make that not distorted
    plt.show()
    #ax = plot_dataframe(lads_shapes, column='CRIME', scheme='QUANTILES', k=3, colormap='OrRd', legend=True)
    print("finished")

#test()
def create_geopanda_files(data, results_container, paths, lookups, lu_reg):
    """Create map related files from results

    Arguments
    ---------
    results_container : dict
        Data container
    paths : dict
        Paths
    lookups : dict
        Lookups
    lu_reg : list
        Region in a list with order how they are stored in result array
    """

    # --------
    # Read LAD shapefile and create geopanda
    # --------
    lad_shapefile = paths['lad_shapefile']
    lad_geopanda_shp = gpd.read_file(lad_shapefile)

    # Attribute merge unique Key
    unique_merge_id = 'geo_code'

    # ---------
    # Population
    # ---------
    for year in results_container['results_every_year'].keys():

        field_name = 'pop_{}'.format(year)

        #print("A   ---------")
        #print(data['scenario_data']['population'][year])

        # Both need to be lists
        merge_data = {
            str(field_name): data['scenario_data']['population'][year].flatten().tolist(),
            str(unique_merge_id): list(lu_reg)}
        #print("B   ---------")
        #print(data['scenario_data']['population'][year][4])
        #prnt(".")
        # Merge to shapefile
        lad_geopanda_shp = merge_data_to_shp(
            lad_geopanda_shp,
            merge_data,
            unique_merge_id)

        # plot and save as fig
        plot_lad_national(
            lad_geopanda_shp=lad_geopanda_shp,
            field_name_to_plot=field_name,
            result_path=paths['data_results_shapefiles'])

    '''# ------------------------------------
    # Create shapefile with yearly total fuel all enduses
    # ------------------------------------

    # Iterate fueltpyes and years and add as attributes
    for year in results_container['results_every_year'].keys():
        for fueltype in range(lookups['fueltypes_nr']):

            # Calculate yearly sum
            yearly_sum = np.sum(results_container['results_every_year'][year][fueltype], axis=1)
            yearly_sum_gw = yearly_sum

            field_name = 'y_{}_{}'.format(year, fueltype)
            merge_data = basic_functions.array_to_dict(yearly_sum_gw, lu_reg)

    write_shp.write_result_shapefile(
        paths['lad_shapefile'],
        os.path.join(paths['data_results_shapefiles'], 'fuel_y'),
        field_names,
        csv_results)
    '''


    '''# ------------------------------------
    # Create shapefile with load factors
    # ------------------------------------
    field_names, csv_results = [], []
    # Iterate fueltpyes and years and add as attributes
    for year in results_container['load_factors_y'].keys():
        for fueltype in range(lookups['fueltypes_nr']):

            results = basic_functions.array_to_dict(
                results_container['load_factors_y'][year][fueltype], lu_reg)

            field_names.append('y_{}_{}'.format(year, fueltype))
            csv_results.append(results)

        # Add population
        field_names.append('pop_{}'.format(year))

        pop_dict = basic_functions.array_to_dict(
            data['scenario_data']['population'][year], lu_reg)

        csv_results.append(pop_dict)

    write_shp.write_result_shapefile(
        paths['lad_shapefile'],
        os.path.join(paths['data_results_shapefiles'], 'lf_max_y'),
        field_names,
        csv_results)

    '''