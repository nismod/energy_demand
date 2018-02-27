"""Function to create map plots of the results with help of
the geopanda library (http://geopandas.org)
"""
import os
import logging
import copy
import numpy as np
import geopandas as gpd
import pandas as pd
import palettable
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from energy_demand.basic import basic_functions
from energy_demand.technologies import tech_related

def user_defined_classification(
        bins,
        min_value,
        max_value,
        lad_geopanda_shp,
        field_to_plot,
        legend_title,
        color_palette,
        color_prop,
        color_zero=False,
        color_list=False
    ):
    """Generate plot with own classification of choropleth maps

    Arguments
    ---------
    bins : list
        List with own borders for classification
    min_value : float
        Mininum data value
    lad_geopanda_shp : geopanda dataframe
        Figure pandaframe
    field_to_plot : str
        Name of figure to plot
    axes : axes
        Axis of figure
    color_palette : list
        List name of color scheme
    color_prop : str
        If wither sequential or qualitative colors

    Info
    ----
    Source: https://stackoverflow.com/questions/41783090/plotting-a-
    choropleth-map-with-geopandas-using-a-user-defined-classification-s
    """
    # --------------
    # Color paletts
    # --------------
    if color_prop == 'sequential':
        color_list = getattr(palettable.colorbrewer.sequential, color_palette).hex_colors
    elif color_prop == 'qualitative':
        color_list = getattr(palettable.colorbrewer.qualitative, color_palette).hex_colors
    elif color_prop == 'user_defined':
        color_list = color_list

    # Shorten color list
    color_list = color_list[:len(bins)]

    # Reclassify
    reclass_lad_geopanda_shp, cmap = re_classification(
        lad_geopanda_shp,
        bins,
        color_list,
        field_to_plot,
        color_zero)

    # ----------
    # Legend
    # ----------
    legend_handles = []

    # Small number for plotting corrrect charts
    small_number = 0.01

    for bin_nr, bin_entry in enumerate(bins):

        # Legend labels
        if bin_nr == 0: #first bin entry
            if bins[bin_nr] < 0:
                label_patch = "> {} (min {})".format(bin_entry, min_value)

                if min_value > bin_entry:
                    print("Classification boundry is not clever for low values")
            else:
                label_patch = "< {} (min {})".format(bin_entry, min_value)
        elif bin_nr == len(bins) - 1: #last bin entry
            label_patch = "> {} (max {})".format(bin_entry - small_number, max_value)

            if max_value < bin_entry:
                print("Classification boundry is not clever for low values")
        else:

            # Add zero label if it exists
            if bins[bin_nr - 1] == 0:
                label_patch = "0"
                patch = mpatches.Patch(
                    color=color_zero,
                    label=str(label_patch))

                legend_handles.append(patch)

            if bin_entry < 0:
                label_patch = "{}  ―  {}".format(bins[bin_nr - 1], bin_entry - small_number)
            else:
                if bins[bin_nr - 1] == 0:
                    label_patch = "{}  ―  {}".format(bins[bin_nr - 1] + small_number, bin_entry - small_number)
                else:
                    label_patch = "{}  ―  {}".format(bins[bin_nr - 1], bin_entry - small_number)

        patch = mpatches.Patch(
            color=color_list[bin_nr],
            label=str(label_patch))

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

    return reclass_lad_geopanda_shp, cmap

def bin_mapping(value_to_classify, class_bins, dummy_small_nr_for_zero_color):
    """Maps values to a bin.
    The mapped values must start at 0 and end at 1.
    """
    round_digits = 4

    value_to_classify = round(value_to_classify, round_digits)

    # Treat -0 and 0 the same
    if value_to_classify == 0 or value_to_classify == -0:
        value_to_classify = 0

        # get position of zero value
        '''for idx, bound in enumerate(class_bins):
            if value_to_classify == bound:
                return idx / (len(class_bins) - 1.0)'''
        return dummy_small_nr_for_zero_color

    for idx, bound in enumerate(class_bins):
        if value_to_classify < bound:
            return idx / (len(class_bins) - 1.0)
        
def re_classification(lad_geopanda_shp, bins, color_list, field_to_plot, color_zero):
    """Reclassify according to user defined classification

    Arguments
    ----------
    lad_geopanda_shp : dataframe
        Shapefile geopanda dataframe
    bins : list
        Classification boders
    color_list : list
        List with colors for every category
    field_to_plot : str
        Name of figure to plot
    """
    dummy_small_nr_for_zero_color = 0.001

    # Create the list of bin labels and the list of colors corresponding to each bin
    bin_labels = []
    for idx in range(len(bins)):
        val_bin = idx / (len(bins) - 1.0)
        bin_labels.append(val_bin)

    # ----------------------
    # Add white bin and color
    # ----------------------
    print("=''00000000")
    print(color_list)
    print(bin_labels)
    color_list_copy = copy.copy(color_list)
    bin_labels_copy = copy.copy(bin_labels)

    # Add zero color in color list if a min_plus map
    if color_zero != False:
        insert_pos = 1
        color_list_copy.insert(insert_pos, color_zero)
        bin_labels_copy.insert(insert_pos, float(dummy_small_nr_for_zero_color))
    else:
        pass

    # Create the custom color map
    color_bin_match_list = []
    for lbl, color in zip(bin_labels_copy, color_list_copy):
        color_bin_match_list.append((lbl, color))

    cmap = LinearSegmentedColormap.from_list(
        'mycmap',
        color_bin_match_list)

    # Reclassify
    print(cmap._segmentdata)
    print(lad_geopanda_shp[field_to_plot])
    print("----")
    lad_geopanda_shp['reclassified'] = lad_geopanda_shp[field_to_plot].apply(
        func=bin_mapping,
        class_bins=bins,
        dummy_small_nr_for_zero_color=dummy_small_nr_for_zero_color)
    print(lad_geopanda_shp['reclassified'])
    return lad_geopanda_shp, cmap

def plot_lad_national(
        lad_geopanda_shp,
        legend_unit,
        field_to_plot,
        fig_name_part,
        result_path,
        color_palette,
        color_prop,
        user_classification=False,
        color_list=False,
        color_zero=False,
        bins=[],
        file_type="png", #"png" pdf
        plotshow=False
    ):
    """Create plot of LADs and store to map file (PDF)

    Arguments
    ---------
    lad_geopanda_shp : dataframe
        Geopanda dataframe
    legend_unit : str
        Unit of values
    field_to_plot : str
        Field name to plot in map
    fig_name_part : str
        Additional string naming variable
    result_path : str
        Path to figure to plot
    user_classification : bool
        Criteria if user classification or not
    bins : list
        Classification boders
    color_palette : list
        List name of color scheme
    color_list : list
        User defined color scheme
    color_prop : str
        If whether sequential or qualitative colors

    Info
    ----

        color_palette

            Colorbrewer defined color schemes can be found here:
            https://jiffyclub.github.io/palettable/colorbrewer/sequential/

        bins (Classification borders)

            If only positive numbers are to classify, the first entry must not be zero.
            If positive and negative numbers, a user defined  color schmene `color_list`
            generated with `colors_plus_minus_map` must be provided as an input and
            user_classification set to `user_classification`.

        Geopanda info:
        http://darribas.org/gds_scipy16/ipynb_md/02_geovisualization.html
        https://stackoverflow.com/questions/41783090/plotting-a-choropleth
        -map-with-geopandas-using-a-user-defined-classification-s
    """
    fig_name = os.path.join(
        result_path,
        "{}.{}".format(field_to_plot, file_type))

    fig_map, axes = plt.subplots(1, figsize=(5, 8))

    legend_title = "unit [{}]".format(legend_unit)

    # --------------------
    # Plot polygon borders and set per default to white
    # --------------------
    lad_geopanda_shp.plot(
        ax=axes,
        linewidth=0.6,
        color=None, #or white
        edgecolor='black')

    # -----------------------------
    # Own classification (work around)
    # -----------------------------
    if user_classification:

        # Get maximum and minum values
        rounding_digits = 10
        min_value = round(lad_geopanda_shp[field_to_plot].min(), rounding_digits)
        max_value = round(lad_geopanda_shp[field_to_plot].max(), rounding_digits)

        # Add maximum value
        bins.append(max_value)

        lad_geopanda_shp_reclass, cmap = user_defined_classification(
            bins,
            min_value,
            max_value,
            lad_geopanda_shp,
            field_to_plot,
            legend_title,
            color_palette=color_palette,
            color_prop=color_prop,
            color_zero=color_zero,
            color_list=color_list)

        lad_geopanda_shp_reclass.plot(
            ax=axes,
            column='reclassified',
            legend=False,
            cmap=cmap,
            alpha=1,
            vmin=0,
            vmax=1)

        # ---------
        # Aelect all polygons with value 0 of attribute to plot and set to zero color
        # ---------
        all_zero_polygons = getattr(lad_geopanda_shp, field_to_plot)
        lad_geopanda_shp = lad_geopanda_shp[(all_zero_polygons==0)]
        lad_geopanda_shp.plot(
            ax=axes,
            linewidth=0.6,
            color="#8a2be2", #or white
            edgecolor='black')
        #plt.show()

    else:

        # -----------------------------
        # Plot map with all value hues
        # -----------------------------
        lad_geopanda_shp.plot(
            ax=axes,
            column=field_to_plot,
            cmap='OrRd',
            legend=True,
            alpha=1)

        plt.legend(
            title=legend_title,
            prop={
                'family': 'arial',
                'size': 10},
            loc='upper center',
            bbox_to_anchor=(0.5, -0.05),
            frameon=False)

    # -----------------------------
    # Plot map with all value hues
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_to_plot,
        cmap='OrRd',
        legend=True)'''

    # -----------------------------
    # Plot map wtih quantiles
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_to_plot,
        scheme='QUANTILES',
        k=5,
        cmap='OrRd',
        legend=True)'''

    # -----------------------------
    # Plot map wtih quantiles
    # -----------------------------
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_to_plot,
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
    field_to_plot = field_to_plot + fig_name_part

    fig_map.suptitle(field_to_plot)

    # Make that not distorted
    plt.axis('equal')

    # Tight layout
    plt.margins(x=0)

    # Add space for legend
    plt.subplots_adjust(
        bottom=0.4) #0.2 the charts

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

def create_geopanda_files(
        data,
        results_container,
        paths,
        lu_reg,
        fueltypes_nr,
        fueltypes,
        path_shapefile_input
    ):
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
    logging.info("... create spatial maps of results")
    # --------
    # Read LAD shapefile and create geopanda
    # --------
    try:
        # Single scenario run
        lad_geopanda_shp = gpd.read_file(paths['lad_shapefile'])
    except IOError:
        # Multiple scenario runs
        lad_geopanda_shp = gpd.read_file(path_shapefile_input)
  
    # Attribute merge unique Key
    unique_merge_id = 'name' #'geo_code'

    # ======================================
    # Spatial maps of difference in load factors
    # ======================================
    simulated_yrs = list(results_container['load_factors_y'].keys())

    final_yr = simulated_yrs[-1]
    base_yr = simulated_yrs[0]

    for fueltype in range(fueltypes_nr):
        print("FUELTYPEL " + str(fueltype))

        fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype)
        field_name = 'lf_diff_{}_{}_'.format(final_yr, fueltype_str)
        if fueltype_str == 'hydrogen':
            print("..")

        lf_end_yr = basic_functions.array_to_dict(
            results_container['load_factors_y'][final_yr][fueltype],
            lu_reg)

        lf_base_yr = basic_functions.array_to_dict(
            results_container['load_factors_y'][base_yr][fueltype],
            lu_reg)

        # Calculate load factor difference base and final year (100 = 100%)
        diff_lf = {}
        for reg in lu_reg:
            diff_lf[reg] = lf_end_yr[reg] - lf_base_yr[reg]

        # Both need to be lists
        merge_data = {
            str(field_name): list(diff_lf.values()),
            str(unique_merge_id): list(lu_reg)}

        # Merge to shapefile
        lad_geopanda_shp = merge_data_to_shp(
            lad_geopanda_shp,
            merge_data,
            unique_merge_id)

        # If user classified, defined bins  [x for x in range(0, 1000000, 200000)]
        bins = [-4, -2, 0, 2, 4] # must be of uneven length containing zero

        color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
            bins=bins,
            color_prop='qualitative',
            color_order=True,
            color_zero='#8a2be2') #"#8a2be2" ffffff

        plot_lad_national(
            lad_geopanda_shp=lad_geopanda_shp,
            legend_unit="%",
            field_to_plot=field_name,
            fig_name_part="lf_max_y",
            result_path=paths['data_results_shapefiles'],
            color_palette='Purples_9',
            color_prop=color_prop,
            user_classification=user_classification,
            color_list=color_list,
            color_zero=color_zero,
            bins=bins)

    # ======================================
    # Population
    # ======================================
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
            field_to_plot=field_name,
            fig_name_part="pop_",
            result_path=paths['data_results_shapefiles'],
            color_palette='Dark2_7',
            color_prop='qualitative',
            user_classification=True,
            bins=bins)

    # ======================================
    # Total fuel all enduses
    # ======================================
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
            plot_lad_national(
                lad_geopanda_shp=lad_geopanda_shp,
                legend_unit="GWh",
                field_to_plot=field_name,
                fig_name_part="tot_all_enduses_y_",
                result_path=paths['data_results_shapefiles'],
                color_palette='Dark2_7',
                color_prop='qualitative',
                user_classification=False)

    # ======================================
    # Load factors
    # ======================================
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
            plot_lad_national(
                lad_geopanda_shp=lad_geopanda_shp,
                legend_unit="%",
                field_to_plot=field_name,
                fig_name_part="lf_max_y",
                result_path=paths['data_results_shapefiles'],
                color_palette='Dark2_7',
                color_prop='qualitative',
                user_classification=False)

def colors_plus_minus_map(
        bins,
        color_prop,
        color_order=True,
        color_zero='#ffffff'
    ):
    """Create color scheme in case plus and minus classes
    are defined (i.e. negative and positive values to
    classify)

    Arguments
    ---------
    bins : list
        List with borders
    color_prop : str
        Type of color is not plus_minus map
    color_order : bool
        Criteria to switch colors
    user_classification : bool
        Criteria whether used classification or not
    color_zero : str, default=white hex color
        Color of zero values

    Returns
    -------
    color_list : list
        List with colors
    color_prop : str
        Type of colors
    user_classification : bool
        Wheter user defined color scheme or not
    color_zero : hex_color string
        Color of zero values
    """
    if min(bins) < 0:

        # Colors pos and neg
        if color_order:
            color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors
            color_list_neg = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors
        else:
            color_list_neg = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors
            color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors

        # Select correct number of colors or addapt colors
        color_list_pos = color_list_pos[1:]

        # Invert negative colors
        color_list_neg = color_list_neg[::-1]

        nr_of_cat_pos_neg = int((len(bins) -1) / 2)

        color_list = []
        for i in range(nr_of_cat_pos_neg + 1): #add one to get class up to zero
            color_list.append(color_list_neg[i])

        for i in range(nr_of_cat_pos_neg + 1): # add one to get class beyond last bin
            color_list.append(color_list_pos[i])

        return color_list, 'user_defined', True, color_zero

    else:
        # regular classification
        return [], color_prop, False, False
