"""Function to create map plots of the results with help of
the geopanda library (http://geopandas.org)
"""
import os
import numpy as np
import geopandas as gpd
import pandas as pd
import palettable #https://jiffyclub.github.io/palettable/colorbrewer/sequential/
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from energy_demand.basic import basic_functions
from energy_demand.plotting import plotting_styles

def own_classification_work_round(bins, min_value, lad_geopanda_shp, field_name_to_plot, legend_title):
    """Generate plot with own classification of choropleth maps

    The vues for plotting are taken from `palette`
    Arguments
    ---------
    bins : list
        List with own borders for classification
    min_value : float
        Mininum data value
    lad_geopanda_shp : geopanda dataframe
        Figure pandaframe
    field_name_to_plot : str
        Name of figure to plot
    axes : axes
        Axis of figure

    Info
    ----
    Source: https://stackoverflow.com/questions/41783090/plotting-a-
    choropleth-map-with-geopandas-using-a-user-defined-classification-s

        [x for x in range(0, 1000000, 200000)]
    """
    def rgb2hex(r_color, g_color, b_color):
        """Convert RGB to HEX
        """
        return "#{:02x}{:02x}{:02x}".format(r_color, g_color, b_color)

    # --------------
    # Color paletts
    # --------------
    color_list_rgb = palettable.colorbrewer.qualitative.Dark2_7
    #color_list_rgb = palettable.colorbrewer.sequential.Greens_9

    color_list = []
    for color in color_list_rgb.colors[:len(bins)]:
        color_list.append(rgb2hex(color[0], color[1], color[2]))

    # Reclassify
    lad_geopanda_shp, cmap = hack_classification(
        lad_geopanda_shp,
        bins,
        color_list,
        field_name_to_plot)

    # ----------
    # Legend
    # ----------
    legend_handles = []
    for bin_nr, color in enumerate(color_list):

        # Legend label
        if bin_nr == 0: #first bin entry
            label_legend_patch = "< {} (min {})".format(bins[bin_nr], min_value)
        elif bin_nr == len(bins) - 1: #last bin entry
            label_legend_patch = "> {} ( max {})".format(bins[bin_nr - 1], bins[bin_nr])
        else:
            label_legend_patch = "{} - {}".format(bins[bin_nr - 1], bins[bin_nr])

        patch = mpatches.Patch(
            color=color,
            label=str(label_legend_patch))

        legend_handles.append(patch)

    plt.legend(
        handles=legend_handles,
        title=legend_title,
        prop={
            'family': 'arial',
            'size': 10},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False)

    return lad_geopanda_shp, cmap

def hack_classification(lad_geopanda_shp, bins, color_list, field_name_to_plot):
    """Remap according to user defined classification

    Arguments
    ----------
    lad_geopanda_shp : dataframe
        Shapefile geopanda dataframe
    bins : list
        Classification boders
    color_list : list
        List with colors for every category
    field_name_to_plot : str
        Name of figure to plot
    """
    def bin_mapping(value_to_classify):
        """Maps values to a bin.
        The mapped values must start at 0 and end at 1.
        """
        for idx, bound in enumerate(bins):
            if value_to_classify < bound:
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
        legend_unit,
        field_name_to_plot,
        fig_name_part,
        result_path,
        plotshow=False,
        user_classification=False,
        bins=[]
    ):
    """Create plot of LADs and store to map file (PDF)

    Arguments
    ---------
    lad_geopanda_shp : dataframe
        Geopanda dataframe
    legend_unit : str
        Unit of values
    field_name_to_plot : str
        Field name to plot in map
    fig_name_part : str
        Additional string naming variable
    result_path : str
        Path to figure to plot
    user_classification : bool
        Criteria if user classification or not
    bins : list
        Classification boders

        # Classification borders
        # Note:
        #   First bin entry must not be zero! (the first entry is alwys from zero to first entry)
        #   Last bin entry is always theretical maximum

    Info
    -----
        Map color:  https://matplotlib.org/users/colormaps.html

    http://darribas.org/gds_scipy16/ipynb_md/02_geovisualization.html
    https://stackoverflow.com/questions/41783090/plotting-a-choropleth
    -map-with-geopandas-using-a-user-defined-classification-s
    """
    fig_name = os.path.join(
        result_path,
        "{}.{}".format(field_name_to_plot, "pdf"))

    fig_map, axes = plt.subplots(
        1,
        figsize=(5, 8))

    legend_title = "unit [{}]".format(legend_unit)

    # -----------------------------
    # Own classification (work around)
    # -----------------------------
    if user_classification:

        # Get maximum and minum values
        max_value = lad_geopanda_shp[field_name_to_plot].max()
        min_value = lad_geopanda_shp[field_name_to_plot].min()

        bins.append(max_value)

        lad_geopanda_shp, cmap = own_classification_work_round(
            bins,
            min_value,
            lad_geopanda_shp,
            field_name_to_plot,
            legend_title)

        lad_geopanda_shp.plot(
            axes=axes,
            column='reclassified',
            legend=False,
            cmap=cmap,
            alpha=1,
            vmin=0,
            vmax=1)
    else:

        # -----------------------------
        # Plot map with all value hues
        # -----------------------------
        lad_geopanda_shp.plot(
            axes=axes,
            column=field_name_to_plot,
            cmap='OrRd',
            alpha=1,
            legend=True)

        plt.legend(
            title=legend_title,
            fontsize=8,
            fontfamily='arial')

    # -----------------------------
    # Plot map with all value hues
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

    #from pysal.esda.mapclassify import User_Defined
    #lad_geopanda_shp.User_Defined(lad_geopanda_shp, bins)
    '''lad_geopanda_shp.assign(cl=interval_data.yb).plot(
        column='cl',
        categorical=True,
        k=10,
        cmap='OrRd',
        linewidth=0.1,
        axes=axes,
        edgecolor='white',
        legend=True,
        scheme='User_Defined')'''

    # Title
    field_name_to_plot = os.path.join(
        field_name_to_plot,
        fig_name_part)

    fig_map.suptitle(field_name_to_plot)

    # Make that not distorted
    plt.axis('equal')

    # Tight layout
    plt.margins(x=0)

    # Add space for legend
    plt.subplots_adjust(bottom=0.2)

    # Save figure
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def merge_data_to_shp(shp_gdp, merge_data, unique_merge_id):
    """Merge data to geopanda dataframe which is read from shapefile

    Arguments
    ----------
    shp_gdp : dataframe
        Geopanda dataframe from shapefile
    merge_data : dict
        Data to merge
    unique_merge_id : str
        Unique ID to make attribute merge

    Returns
    --------
    shp_gdp_merged : dataframe
        Geopanda containing merged dataframe

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

    shp_gdp_merged = shp_gdp.merge(
        merge_dataframe,
        on=unique_merge_id)

    return shp_gdp_merged

def create_geopanda_files(data, results_container, paths, lu_reg, fueltypes_nr):
    """Create map related files (png) from results.

    Arguments
    ---------
    results_container : dict
        Data container
    paths : dict
        Paths
    lu_reg : list
        Region in a list with order how they are stored in result array
    fueltypes_nr : int
        Number of fueltypes
    """
    # --------
    # Read LAD shapefile and create geopanda
    # --------
    lad_geopanda_shp = gpd.read_file(paths['lad_shapefile'])

    # Attribute merge unique Key
    unique_merge_id = 'name' #'geo_code'

    # ---------
    # Population
    # ---------
    for year in results_container['results_every_year'].keys():

        field_name = 'pop_{}'.format(year)

        # Both need to be lists
        merge_data = {
            str(field_name): data['scenario_data']['population'][year].flatten().tolist(),
            str(unique_merge_id): list(lu_reg)}

        # Merge to shapefile
        lad_geopanda_shp = merge_data_to_shp(
            lad_geopanda_shp,
            merge_data,
            unique_merge_id)

        # If user classified, defined bins
        bins = [50000, 300000]

        plot_lad_national(
            lad_geopanda_shp=lad_geopanda_shp,
            legend_unit="people",
            field_name_to_plot=field_name,
            fig_name_part="pop_",
            result_path=paths['data_results_shapefiles'],
            user_classification=True,
            bins=bins)

    # ------------------------------------
    # Total fuel all enduses
    # ------------------------------------
    for year in results_container['results_every_year'].keys():
        for fueltype in range(fueltypes_nr):

            field_name = 'y_{}_{}'.format(year, fueltype)

            # Calculate yearly sum
            yearly_sum_gwh = np.sum(
                results_container['results_every_year'][year][fueltype],
                axis=1)

            fuel_data = basic_functions.array_to_dict(yearly_sum_gwh, lu_reg)

            # Both need to be lists
            merge_data = {
                str(field_name): list(fuel_data.values()),
                str(unique_merge_id): list(lu_reg)}

            # Merge to shapefile
            lad_geopanda_shp = merge_data_to_shp(
                lad_geopanda_shp,
                merge_data,
                unique_merge_id)

            # If user classified, defined bins
            #bins = [50000, 300000]
            plot_lad_national(
                lad_geopanda_shp=lad_geopanda_shp,
                legend_unit="GWh",
                field_name_to_plot=field_name,
                fig_name_part="tot_all_enduses_y_",
                result_path=paths['data_results_shapefiles'],
                user_classification=False) #,
                #bins=bins)

    # ------------------------------------
    # Create shapefile with load factors
    # ------------------------------------
    for year in results_container['load_factors_y'].keys():
        for fueltype in range(fueltypes_nr):

            field_name = 'lf_{}_{}'.format(year, fueltype)

            results = basic_functions.array_to_dict(
                results_container['load_factors_y'][year][fueltype], lu_reg)

            # Both need to be lists
            merge_data = {
                str(field_name): list(results.values()),
                str(unique_merge_id): list(lu_reg)}

            # Merge to shapefile
            lad_geopanda_shp = merge_data_to_shp(
                lad_geopanda_shp,
                merge_data,
                unique_merge_id)

            # If user classified, defined bins
            #bins = [50000, 300000]
            plot_lad_national(
                lad_geopanda_shp=lad_geopanda_shp,
                legend_unit="%",
                field_name_to_plot=field_name,
                fig_name_part="lf_max_y",
                result_path=paths['data_results_shapefiles'],
                user_classification=False) #True,
                #bins=bins)
