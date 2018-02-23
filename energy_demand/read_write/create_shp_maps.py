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
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

def hack_classification(lad_geopanda_shp, bins, color_list, field_name_to_plot):
    """OWn classification with bins

    # https://automating-gis-processes.github.io/2016/Lesson5-interactive-map-bokeh.html
    # http://pysal.readthedocs.io/en/latest/library/esda/mapclassify.html 'User_defined' is not yet implemented

    Work arounde taken from
    Source: https://stackoverflow.com/questions/41783090/plotting-a-choropleth-map-with-geopandas-using-a-user-defined-classification-s
    """
    def bin_mapping(x):
        """Maps values to a bin.
        The mapped values must start at 0 and end at 1.
        """
        for idx, bound in enumerate(bins):
            if x < bound:
                return idx / (len(bins) - 1.0)

    # Create the list of bin labels and the list of colors corresponding to each bin
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
    """Create plot of LADs and store to map file (PDF)

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
    # Plot map with all value hues
    # -----------------------------
    lad_geopanda_shp.plot(
        axes=axes,
        column=field_name_to_plot,
        cmap='OrRd',
        legend=True)
    plt.show()

    '''# ------------
    # Own classification (work around)
    # ------------
    from energy_demand.plotting import plotting_styles
    # Own classification bins
    bins = [x for x in range(0, 1000000, 200000)]
    bins = [0, 50000, 100000]


    #color_list = ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c'] # '#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']

    def rgb2hex(r,g,b):
        """Convert RGB to HEX
        """
        hex = "#{:02x}{:02x}{:02x}".format(r,g,b)
        return hex

    import palettable #https://jiffyclub.github.io/palettable/colorbrewer/sequential/
    color_list = []
    color_list_rgb = palettable.colorbrewer.qualitative.Dark2_7
    #color_list_rgb = palettable.colorbrewer.sequential.Greens_9

    for color in color_list_rgb.colors[:len(bins)]:
        color_list.append(rgb2hex(color[0], color[1], color[2]))

    lad_geopanda_shp, cmap = hack_classification(
        lad_geopanda_shp,
        bins,
        color_list,
        field_name_to_plot)

    # Legend
    legend_handles = []
    for bin_nr, color in enumerate(color_list):
        
        # Legend label
        if bin_nr == len(bins) -1:
            label_legend_patch = "{} {}".format(">", bins[bin_nr])
        else:
            label_legend_patch = "{} - {}".format(bins[bin_nr], bins[bin_nr + 1])

        patch = mpatches.Patch(
            color=color,
            label=str(label_legend_patch))

        legend_handles.append(patch)

    # Plot legend
    plt.legend(
        handles=legend_handles,
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)

    lad_geopanda_shp.plot(
        axes=axes,
        column='reclassified',
        legend=False,
        cmap=cmap,
        alpha=1,
        vmin=0,
        vmax=1)
    '''
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
    plt.axis('equal') 

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

    return shp_gdp_merged

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

        # Both need to be lists
        merge_data = {
            str(field_name): data['scenario_data']['population'][year].flatten().tolist(),
            str(unique_merge_id): list(lu_reg)}
        print("MERGE DATA")
        for reg_nr, reg in enumerate(lu_reg):
            print("reg: {}  {}".format(reg, data['scenario_data']['population'][year][reg_nr]))
        print(data['scenario_data']['population'][year].shape)
        prnt(":")
        print(merge_data)
        # TESTING WHY NOT FUNCTIONS IN TODO TODO
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