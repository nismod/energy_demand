"""Function to create map plots of the results with help of
the geopanda library (http://geopandas.org)
"""
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
from matplotlib.colors import LinearSegmentedColormap
from energy_demand.basic import basic_functions
from energy_demand.technologies import tech_related
from energy_demand.read_write import write_data
#matplotlib.use('Agg') # Used to make it work in linux

def get_reasonable_bin_values(
        data_to_plot,
        increments=10
    ):
    """Get reasonable bin values
    """
    def round_down(num, divisor):
        return num - (num%divisor)

    max_val = max(data_to_plot)
    min_val = min(data_to_plot)

    # Positive values
    if min_val >= 0:

        # Calculate number of classes
        classes = max_val / increments

        # Round down and add one class for larger values
        nr_classes = round_down(classes, increments) + 1

        if nr_classes > 9:
            raise Exception("Nr of classes is too big")

        # Classes
        min_class = round_down(min_val, increments)                              # Minimum class
        max_class = round_down(max_val, increments) + increments + increments    # Maximum class

        if min_class == 0:
            min_class = increments

        # Bin with classes
        #logging.info("vv {}  {}".format(max_val, min_val))
        #logging.info("pos {}  {} {}".format(min_class, max_class, increments))
        bins = list(range(int(min_class), int(max_class), int(increments)))
    else:
        logging.info("Neg")
        #lager negative values

        # must be of uneven length containing zero
        largest_min = abs(min_val)
        largest_max = abs(max_val)

        nr_min_class = round_down(abs(min_val), increments) / increments

        if max_val < 0:
            nr_pos_classes = 0
        else:
            nr_pos_classes = round_down(max_val, increments) / increments + 1

        # Number of classes
        #symetric_value = nr_of_classes_symetric * increments
        min_class_value = int(nr_min_class * -1) * increments
        max_class_value = int(nr_pos_classes) * increments

        # Negative classes
        if min_class_value / increments == 0:
            neg_classes = [increments * -1]
        elif min_class_value / increments == 1:
            neg_classes = [increments * -1]
        else:
            neg_classes = list(range(min_class_value, 0, increments))

        if max_class_value == 0:
            pos_classes = []
        elif max_class_value / increments == 0:
            pos_classes = [increments]
        elif max_class_value / increments == 1:
            pos_classes = [increments] #only one class
        else:
            pos_classes = list(range(increments, max_class_value + increments, increments))

        bins = neg_classes + [0] + pos_classes

    # ---
    # Test that maximum 9 classes
    # ---
    if len(bins) > 8:
        raise Exception("Too many bin classes defined " + str(len(bins)))

    return bins

def user_defined_classification(
        bins,
        min_value,
        max_value,
        lad_geopanda_shp,
        field_to_plot,
        legend_title,
        color_palette,
        color_prop,
        placeholder_zero_color,
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
    if min(bins) > 0:
        #bins.append(999)
        #color_list = color_list[:len(bins)]
        color_list = color_list[:len(bins)+1]
    else:
        color_list = color_list


    logging.info(" ")
    logging.info("BEFORE RECLASSIFICAOTN")
    logging.info("---")
    logging.info(bins)
    logging.info(color_list)

    # ------------------------------------------------------
    # Reclassify
    # ------------------------------------------------------
    reclass_lad_geopanda_shp, cmap = re_classification(
        lad_geopanda_shp,
        bins,
        color_list,
        field_to_plot,
        color_zero,
        placeholder_zero_color)

    # ------------------------------------------------------
    # Legend and legend labels
    # ------------------------------------------------------
    logging.info("bins fff")
    logging.info(bins)
    logging.info(color_list)

    legend_handles = []
    small_number = 0.01 # Small number for plotting corrrect charts

    if max(bins) >= 0:
        bins.append(999) # Append dummy last element for last class
    else:
        pass

    for bin_nr, bin_entry in enumerate(bins):
        if bin_nr == 0: #first bin entry

            if bin_entry < 0:
                label_patch = "> {} (min {})".format(bin_entry, min_value)

                if min_value > bin_entry:
                    print("Classification boundry is not clever for low values")
            else:
                label_patch = "< {} (min {})".format(bin_entry, min_value)
        elif bin_nr == len(bins)- 1: # -1 means that last bin entry
            ###label_patch = "> {} (max {})".format(bins[-2], max_value)
            label_patch = "> {} (max {})".format(bins[-2], max_value)

            if max_value < bin_entry:
                print("Classification boundry is not clever for low values")
        else:
            # ----------------------------
            # Add zero label if it exists
            # ----------------------------
            if bins[bin_nr - 1] == 0:
                patch = mpatches.Patch(
                    color=color_zero,
                    label=str("0"))
                legend_handles.append(patch)
            else:
                pass

            # ----------------------------
            # Other other labels
            # ----------------------------
            if bin_entry < 0:
                label_patch = "{}  ―  {}".format(bins[bin_nr - 1], bin_entry - small_number)
            else:
                if bins[bin_nr - 1] == 0:
                    label_patch = "{}  ―  {}".format(bins[bin_nr - 1] + small_number, bin_entry - small_number)
                else:
                    label_patch = "{}  ―  {}".format(bins[bin_nr - 1], bin_entry - small_number)

        logging.info("------label_patch: {}  {}  {}  {}".format(label_patch, bin_entry, bins, color_list))

        patch = mpatches.Patch(
            color=color_list[bin_nr],
            label=str(label_patch))

        legend_handles.append(patch)

    plt.legend(
        handles=legend_handles,
        title=legend_title,
        prop={'size': 5},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False)

    return reclass_lad_geopanda_shp, cmap

def bin_mapping(
        value_to_classify,
        nr_of_classes,
        class_bins,
        placeholder_zero_color
    ):
    """Maps values to a bin.
    The mapped values must start at 0 and end at 1.

    Arguments
    ---------
    value_to_classify : float
        Value to classify
    class_bins : list
        Bins to use for classification

    Returns
    -------
    classified value
    """
    round_digits = 4

    value_to_classify = round(value_to_classify, round_digits)

    # Treat -0 and 0 the same
    if value_to_classify == 0 or value_to_classify == -0:
        #value_to_classify = 0

        # get position of zero value
        '''for idx, bound in enumerate(class_bins):
            if value_to_classify == bound:
                return idx / (len(class_bins) - 1.0)'''
        return placeholder_zero_color

    for idx, bound in enumerate(class_bins):
        if value_to_classify < bound:
            #return idx / (len(class_bins) - 1.0)
            #logging.info("TT " + str(idx / nr_of_classes - 1.0))
            return idx / (nr_of_classes - 1.0)

def re_classification(
        lad_geopanda_shp,
        bins,
        color_list,
        field_to_plot,
        color_zero,
        placeholder_zero_color
    ):
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
    color_zero : str
        Color for zeros
    placeholder_zero_color : float
        Number to assign for zero values
    """
    # Create the list of bin labels and the
    # list of colors corresponding to each bin
    if max(bins) <=0:
        nr_of_classes = int(len(bins)) + 1 #only negative classes
    elif min(bins) >= 0:
        nr_of_classes = int(len(bins)) + 1 #only negative classes
    else:
        nr_of_classes = int(len(bins) -1) + 2 #class on top and bottom and get rid of 0

    bin_labels = []

    for idx in range(nr_of_classes):
        val_bin = idx / (nr_of_classes - 1.0)
        bin_labels.append(val_bin)

    # ----------------------
    # Add white bin and color
    # ----------------------
    color_list_copy = copy.copy(color_list)
    bin_labels_copy = copy.copy(bin_labels)

    #logging.info("KUH " + str(color_zero))
    #logging.info(color_list_copy)
    #logging.info(bin_labels_copy)
    # Add zero color in color list if a min_plus map
    if color_zero != False:
        insert_pos = 1
        #insert_pos = int(len(bin_labels)/2) #Middle position where 0 is positioned in bins
        #insert_pos = 0
        color_list_copy.insert(insert_pos, color_zero)
        bin_labels_copy.insert(insert_pos, float(placeholder_zero_color))
    else:
        pass
    #logging.info("KUH 2")
    #logging.info(color_list_copy)
    #logging.info(bin_labels_copy)

    # Create the custom color map
    color_bin_match_list = []
    for lbl, color in zip(bin_labels_copy, color_list_copy):
        color_bin_match_list.append((lbl, color))
    ##logging.info("color_bin_match_list: " + str(color_bin_match_list))
    ##logging.info(bins)
    ##logging.info(bin_labels_copy)

    if 0 in bins:
        pass
    elif min(bins) > 0:
        logging.info("TT")
    else:
        bins.insert(len(bins), 0) # Add zero at the end

    cmap = LinearSegmentedColormap.from_list(
        'mycmap',
        color_bin_match_list)

    #logging.info("cmap " + str(cmap))

    # Reclassify
    lad_geopanda_shp['reclassified'] = lad_geopanda_shp[field_to_plot].apply(
        func=bin_mapping,
        nr_of_classes=nr_of_classes,
        class_bins=bins,
        placeholder_zero_color=float(placeholder_zero_color))

    return lad_geopanda_shp, cmap

def plot_lad_national(
        lad_geopanda_shp,
        legend_unit,
        field_to_plot,
        fig_name_part,
        result_path,
        color_palette,
        color_prop=False,
        user_classification=False,
        color_list=False,
        color_zero=False,
        bins=[],
        file_type="pdf", #"png" pdf
        plotshow=False
    ):
    """Create plot of LADs and store to map file (PDF) and csv file

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
    # ---------------------
    # Write results to csv
    # ---------------------
    out_data_path = os.path.join(
        result_path,
        "{}_{}.{}".format(fig_name_part, field_to_plot, 'csv'))

    write_data.write_result_txt(
        out_data_path,
        lad_geopanda_shp['name'],
        lad_geopanda_shp[field_to_plot])

    # ---------------------
    # Create figure
    # ---------------------
    fig_name = os.path.join(
        result_path,
        "{}_{}.{}".format(
            fig_name_part, field_to_plot, file_type))

    fig_map, axes = plt.subplots(
        1, figsize=(5, 8))

    legend_title = "unit [{}]".format(legend_unit)

    # --------------------
    # Plot polygon borders and set per default to white
    # --------------------
    lad_geopanda_shp.plot(
        ax=axes,
        linewidth=0.6,
        color=None,
        edgecolor='black')

    # -----------------------------
    # Own classification (work around)
    # -----------------------------
    if user_classification:
        logging.info("User classification")

        # Color to assing zero values
        placeholder_zero_color = 0.00001

        # Get maximum and minum values
        rounding_digits = 10
        min_value = round(lad_geopanda_shp[field_to_plot].min(), rounding_digits)
        max_value = round(lad_geopanda_shp[field_to_plot].max(), rounding_digits)

        # Add maximum value
        logging.info(" {} {}".format(min_value, max_value))
        logging.info("FINAL BIN before" + str(bins))
        ###bins.append(max_value)

        ###logging.info("FINAL BIN " + str(bins))
        lad_geopanda_shp_reclass, cmap = user_defined_classification(
            bins,
            min_value,
            max_value,
            lad_geopanda_shp,
            field_to_plot,
            legend_title,
            color_palette=color_palette,
            color_prop=color_prop,
            placeholder_zero_color=placeholder_zero_color,
            color_zero=color_zero,
            color_list=color_list)

        # Plot reclassified
        lad_geopanda_shp_reclass.plot(
            ax=axes,
            column='reclassified',
            legend=False,
            cmap=cmap,
            alpha=1,
            vmin=0,
            vmax=1)

        # ---------
        # Select all polygons with value 0 of attribute to plot
        # ---------
        all_zero_polygons = getattr(lad_geopanda_shp_reclass, 'reclassified')
        lad_geopanda_shp_zeros = lad_geopanda_shp_reclass[(all_zero_polygons == placeholder_zero_color)]

        # If more than 0 polygons are selected with classified number of zero, plot them
        if lad_geopanda_shp_zeros.shape[0] > 0:
            lad_geopanda_shp_zeros.plot(
                ax=axes,
                color=color_zero)
    else:
        logging.info("not user classification")

        # ----------------------------
        # Plot map with all value hues
        # -----------------------------
        # Creates hues values
        lad_geopanda_shp.plot(
            ax=axes,
            column=field_to_plot,
            legend=True)
        '''
        lad_geopanda_shp.plot(
            ax=axes,
            column=field_to_plot,
            cmap='OrRd',
            legend=True)
        '''

        # -----------------------------
        # Plot map with quantiles
        # -----------------------------
        '''
        lad_geopanda_shp.plot(
            axes=axes,
            column=field_to_plot,
            scheme='equal_interval', #quantiles'
            k=10,
            cmap='OrRd',
            legend=True)
        '''

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

        # Legend taken form axis
        '''
        legend = axes.get_legend()
        legend.set_title(legend_title, prop={
            'family': 'arial',
            'size': 10})
        legend.set_frame_on(False)
        legend.set_bbox_to_anchor((0.5, -0.05))
        '''

    # Title
    fig_map.suptitle(field_to_plot + fig_name_part)

    # Make that not distorted
    plt.axis('equal')

    # Tight layout
    plt.margins(x=0)

    # Add space for legend
    plt.subplots_adjust(bottom=0.4)

    # Save figure
    plt.savefig(fig_name)

    # Show figure
    if plotshow:
        plt.show()
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

def plot_spatial_mapping_example(
        diffusion_vals,
        global_value,
        paths,
        regions,
        path_shapefile_input,
        plotshow=False
    ):
    """Figure plot

    Plot a map which distributes a global parameter to
    regional parameters based on diffusion values.

    """
    # Read LAD shapefile and create geopanda
    lad_geopanda_shp = gpd.read_file(path_shapefile_input)

    # Attribute merge unique Key
    unique_merge_id = 'name' #'geo_code'

    field_name = 'Fig_XX_spatial_diffusion_vals'

    # Calculate regional values
    regional_vals = {}
    for region in regions:
        regional_vals[region] = global_value * diffusion_vals[region]

    # Both need to be lists
    merge_data = {
        str(field_name): list(regional_vals.values()),
        str(unique_merge_id): list(regions)}

    # Merge to shapefile
    lad_geopanda_shp = merge_data_to_shp(
        lad_geopanda_shp,
        merge_data,
        unique_merge_id)

    # If user classified, defined bins  [x for x in range(0, 1000000, 200000)]
    #bins = [-4, -2, 0, 2, 4] # must be of uneven length containing zero if minus values
    #bins = [-15, -10, -5, 0, 5, 10, 15] 
    bins = [20, 30, 40, 50, 60, 70, 80, 90]

    if max(bins) < max(list(regional_vals.values())):
        raise Exception("Wrong bin definition: max_val: {}  min_val: {}".format(
            max(list(regional_vals.values())), min(list(regional_vals.values()))))

    color_palette = 'YlGn_9'# YlGn_9
    color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
        bins=bins,
        color_prop='qualitative',
        color_order=True,
        color_zero='#ffffff',
        color_palette=color_palette)

    plot_lad_national(
        lad_geopanda_shp=lad_geopanda_shp,
        legend_unit="%",
        field_to_plot=field_name,
        fig_name_part="lf_max_y",
        result_path=paths['data_results_PDF'],
        color_palette=color_palette,
        color_prop=color_prop,
        user_classification=user_classification,
        color_list=color_list,
        color_zero=color_zero,
        bins=bins,
        plotshow=plotshow)

    return

def create_geopanda_files(
        data,
        results_container,
        path_data_results_shapefiles,
        regions,
        fueltypes_nr,
        fueltypes,
        path_shapefile_input,
        plot_crit_dict,
        base_yr
    ):
    """Create map related files (png) from results.

    Arguments
    ---------
    results_container : dict
        Data container
    paths : dict
        Paths
    regions : list
        Region in a list with order how they are stored in result array
    fueltypes_nr : int
        Number of fueltypes
    """
    logging.info("... create spatial maps of results")

    #base_yr = 2015
    # --------
    # Read LAD shapefile and create geopanda
    # --------

    # Single scenario run
    lad_geopanda_shp = gpd.read_file(path_shapefile_input)

    # Attribute merge unique Key
    unique_merge_id = 'name' #'geo_code'

    # ======================================
    # Peak max h all enduses (abs)
    # ======================================
    if plot_crit_dict['plot_abs_peak_h']:
        for year in results_container['results_every_year'].keys():
            for fueltype in range(fueltypes_nr):

                fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype)

                # Calculate peak h across all regions
                field_name = 'peak_abs_h_{}_{}'.format(year, fueltype_str)


                # Get maxium demand of 8760h for every region
                h_max_gwh_regs = np.max(results_container['results_every_year'][year][fueltype], axis=1)
                print("TOTAL peak fuel across all regs {} {} ".format(np.sum(h_max_gwh_regs), fueltype_str))

                data_to_plot = basic_functions.array_to_dict(h_max_gwh_regs, regions)

                # Both need to be lists
                merge_data = {
                    str(field_name): list(data_to_plot.values()),
                    str(unique_merge_id): list(regions)}

                # Merge to shapefile
                lad_geopanda_shp = merge_data_to_shp(
                    lad_geopanda_shp,
                    merge_data,
                    unique_merge_id)

                bins = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2]

                color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
                    bins=bins,
                    color_prop='qualitative',
                    color_order=True,
                    color_zero='#ffffff',
                    color_palette='YlGnBu_7') #YlGnBu_9 #8a2be2 'YlGnBu_9'  'PuBu_8'

                # If user classified, defined bins
                plot_lad_national(
                    lad_geopanda_shp=lad_geopanda_shp,
                    legend_unit="GWh",
                    field_to_plot=field_name,
                    fig_name_part=field_name,
                    result_path=path_data_results_shapefiles,
                    color_palette='Dark2_7',
                    color_prop=color_prop,
                    user_classification=user_classification,
                    color_list=color_list,
                    bins=bins,
                    color_zero=color_zero)

    # ======================================
    # Peak max h all enduses (diff p)
    # ======================================
    if plot_crit_dict['plot_diff_peak_h']:
        for year in results_container['results_every_year'].keys():
            if year == base_yr:
                pass
            else:
                for fueltype in range(fueltypes_nr):
                    
                    # If total sum is zero, skip
                    if np.sum(results_container['results_every_year'][base_yr][fueltype]) == 0:
                        continue

                    ##if np.isnan(np.sum(results_container['results_every_year'][base_yr][fueltype])):
                    #    logging.info("Error: Contains nan entry {} {}".format(year, fueltype))
                    #    continue
                    #logging.info("============ {}  {}".format(fueltype, np.isnan(np.sum(results_container['results_every_year'][base_yr][fueltype]))))
                    #logging.info(results_container['results_every_year'][base_yr][fueltype])
                    fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype)

                    # Calculate peak h across all regions
                    field_name = 'peak_diff_p_peak_h_{}_{}'.format(year, fueltype_str)

                    # Get maxium demand of 8760h for every region for base year
                    h_max_gwh_regs_by = np.max(results_container['results_every_year'][base_yr][fueltype], axis=1)

                    # Get maxium demand of 8760h for every region for current year
                    h_max_gwh_regs_cy = np.max(results_container['results_every_year'][year][fueltype], axis=1)
                    print("TOTAL peak fuel across all regs {} {} ".format(np.sum(h_max_gwh_regs_cy), fueltype_str))

                    # Calculate difference in decimal
                    diff_p_h_max_regs = ((100 / h_max_gwh_regs_by) * h_max_gwh_regs_cy) - 100

                    data_to_plot = basic_functions.array_to_dict(diff_p_h_max_regs, regions)

                    # Both need to be lists
                    merge_data = {
                        str(field_name): list(data_to_plot.values()),
                        str(unique_merge_id): list(regions)}

                    # Merge to shapefile
                    lad_geopanda_shp = merge_data_to_shp(
                        lad_geopanda_shp,
                        merge_data,
                        unique_merge_id)

                    bins_increments = 20 #10
                    bins = get_reasonable_bin_values(
                        data_to_plot=list(data_to_plot.values()),
                        increments=bins_increments)

                    color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
                        bins=bins,
                        color_prop='qualitative',
                        color_order=True,
                        color_zero='#ffffff',
                        color_palette='YlGnBu_7') #YlGnBu_9 #8a2be2 'PuBu_8'
   
                    # Plot
                    plot_lad_national(
                        lad_geopanda_shp=lad_geopanda_shp,
                        legend_unit="GWh",
                        field_to_plot=field_name,
                        fig_name_part=field_name,
                        result_path=path_data_results_shapefiles,
                        color_palette='Dark2_7',
                        color_prop=color_prop,
                        user_classification=user_classification,
                        color_list=color_list,
                        bins=bins,
                        color_zero=color_zero)

    # ======================================
    # Load factors (absolute)
    # ======================================
    if plot_crit_dict['plot_load_factors']:
        for year in results_container['reg_load_factor_y'].keys():
            for fueltype in range(fueltypes_nr):

                fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype)
                field_name = 'lf_{}_{}'.format(year, fueltype_str)

                results = basic_functions.array_to_dict(
                    results_container['reg_load_factor_y'][year][fueltype], regions)

                # Both need to be lists
                merge_data = {
                    str(field_name): list(results.values()),
                    str(unique_merge_id): list(regions)}

                # Merge to shapefile
                lad_geopanda_shp = merge_data_to_shp(
                    lad_geopanda_shp,
                    merge_data,
                    unique_merge_id)

                # ABSOLUTE
                bins = [40, 45, 50, 55, 60, 75, 80]
                #bins = [55, 60, 65, 70] # must be of uneven length containing zero
                color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
                    bins=bins,
                    color_prop='qualitative',
                    color_order=True,
                    color_zero='#ffffff',
                    color_palette='YlGnBu_9') #8a2be2 'YlGnBu_9'  'PuBu_8'

                # If user classified, defined bins
                plot_lad_national(
                    lad_geopanda_shp=lad_geopanda_shp,
                    legend_unit="%",
                    field_to_plot=field_name,
                    fig_name_part="lf_max_y",
                    result_path=path_data_results_shapefiles,
                    color_palette='Dark2_7',
                    color_prop=color_prop,
                    user_classification=user_classification,
                    color_list=color_list,
                    bins=bins,
                    color_zero=color_zero)

    # ======================================
    # Load factors (difference p)
    # ======================================
    if plot_crit_dict['plot_load_factors_p']:
        simulated_yrs = list(results_container['reg_load_factor_y'].keys())

        final_yr = simulated_yrs[-1]
        base_yr = simulated_yrs[0]

        for fueltype in range(fueltypes_nr):
            logging.info("progress.. {}".format(fueltype))
            fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype)
            field_name = 'lf_diff_{}-{}_{}_'.format(base_yr, final_yr, fueltype_str)

            lf_end_yr = basic_functions.array_to_dict(
                results_container['reg_load_factor_y'][final_yr][fueltype],
                regions)

            lf_base_yr = basic_functions.array_to_dict(
                results_container['reg_load_factor_y'][base_yr][fueltype],
                regions)

            # Calculate load factor difference base and final year (100 = 100%)
            diff_lf = {}
            for reg in regions:
                diff_lf[reg] = lf_end_yr[reg] - lf_base_yr[reg]

            # Both need to be lists
            merge_data = {
                str(field_name): list(diff_lf.values()),
                str(unique_merge_id): list(regions)}

            # Merge to shapefile
            lad_geopanda_shp = merge_data_to_shp(
                lad_geopanda_shp,
                merge_data,
                unique_merge_id)

            # If user classified, defined bins  [x for x in range(0, 1000000, 200000)]
            #bins = [-4, -2, 0, 2, 4] # must be of uneven length containing zero
            bins = [-15, -10, -5, 0, 5, 10, 15] # must be of uneven length containing zero

            color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
                bins=bins,
                color_prop='qualitative',
                color_order=True,
                color_zero='#ffffff',
                color_palette='Purples_9')

            plot_lad_national(
                lad_geopanda_shp=lad_geopanda_shp,
                legend_unit="%",
                field_to_plot=field_name,
                fig_name_part="lf_max_y",
                result_path=path_data_results_shapefiles,
                color_palette='Purples_9',
                color_prop=color_prop,
                user_classification=user_classification,
                color_list=color_list,
                color_zero=color_zero,
                bins=bins)

    # ======================================
    # Population
    # ======================================
    if plot_crit_dict['plot_population']:
        for year in results_container['results_every_year'].keys():

            field_name = 'pop_{}'.format(year)

            # Both need to be lists
            merge_data = {
                str(field_name): data['scenario_data']['population'][year].flatten().tolist(),
                str(unique_merge_id): list(regions)}

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
                result_path=path_data_results_shapefiles,
                color_palette='Dark2_7',
                color_prop='qualitative',
                user_classification=True,
                bins=bins)

    # ======================================
    # Total fuel (y) all enduses
    # ======================================
    for year in results_container['results_every_year'].keys():
        for fueltype in range(fueltypes_nr):

            fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype)

            if plot_crit_dict['plot_total_demand_fueltype']:
                logging.info(" progress.. {}".format(fueltype))

                # ---------
                # Sum per enduse and year (y)
                # ---------
                field_name = 'y_{}_{}'.format(year, fueltype_str)

                # Calculate yearly sum across all regions
                yearly_sum_gwh = np.sum(
                    results_container['results_every_year'][year][fueltype],
                    axis=1)

                data_to_plot = basic_functions.array_to_dict(yearly_sum_gwh, regions)

                # Both need to be lists
                merge_data = {
                    str(field_name): list(data_to_plot.values()),
                    str(unique_merge_id): list(regions)}

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
                    fig_name_part="_tot_all_enduses_y",
                    result_path=path_data_results_shapefiles,
                    color_palette='Dark2_7',
                    color_prop='qualitative',
                    user_classification=False)

            # ===============================================
            # Differences in percent per enduse and year (y)
            # ===============================================
            if plot_crit_dict['plot_differences_p'] and year > base_yr:

                field_name = 'y_diff_p_{}-{}_{}'.format(
                    base_yr, year, fueltype_str)

                # Calculate yearly sums
                yearly_sum_gwh_by = np.sum(
                    results_container['results_every_year'][base_yr][fueltype],
                    axis=1)

                yearly_sum_gwh_cy = np.sum(
                    results_container['results_every_year'][year][fueltype],
                    axis=1)

                # Calculate percentual difference
                p_diff = ((yearly_sum_gwh_cy / yearly_sum_gwh_by) * 100) - 100

                data_to_plot = basic_functions.array_to_dict(p_diff, regions)

                # Both need to be lists
                merge_data = {
                    str(field_name): list(data_to_plot.values()),
                    str(unique_merge_id): list(regions)}

                # Merge to shapefile
                lad_geopanda_shp = merge_data_to_shp(
                    lad_geopanda_shp,
                    merge_data,
                    unique_merge_id)

                # Test if nan vlaue in list and if yes, skipt this
                nan_entry = False
                nan_value = float('nan')
                for entry in list(data_to_plot.values()):
                    if math.isnan(entry):
                        nan_entry = True
                if nan_entry:
                    continue

                # ----
                # CAlculate classes for manual classification
                # ----                
                #logging.info("Min {}  Max {}".format(
                #    min(list(data_to_plot.values())),
                #     max(list(data_to_plot.values()))))
                bins_increments = 10 #MAYBE NEEDS TO BE ADOPTED

                bins = get_reasonable_bin_values(
                    data_to_plot=list(data_to_plot.values()),
                    increments=bins_increments)

                color_list, color_prop, user_classification, color_zero = colors_plus_minus_map(
                    bins=bins,
                    color_prop='qualitative',
                    color_order=True)

                # Plot difference in % per fueltype of total fuel (y)
                plot_lad_national(
                    lad_geopanda_shp=lad_geopanda_shp,
                    legend_unit="GWh",
                    field_to_plot=field_name,
                    fig_name_part="tot_all_enduses_y_",
                    result_path=path_data_results_shapefiles,
                    color_palette='Purples_9',
                    color_prop=color_prop,
                    user_classification=user_classification,
                    color_list=color_list,
                    color_zero=color_zero,
                    bins=bins)

                # PLot not user classificaiton
                plot_lad_national(
                    lad_geopanda_shp=lad_geopanda_shp,
                    legend_unit="GWh",
                    field_to_plot=field_name,
                    fig_name_part="_huevalues_",
                    result_path=path_data_results_shapefiles,
                    color_palette='Purples_9',
                    color_prop=color_prop,
                    user_classification=False,
                    color_list=color_list,
                    color_zero=color_zero,
                    bins=bins)

def colors_plus_minus_map(
        bins,
        color_prop,
        color_order=True,
        color_zero='#ffffff',
        color_palette='Purples_9'
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
    if bins == []:
        # regular classification
        return [], color_prop, False, False

    elif min(bins) < 0:
        logging.info("negative bins" + str(bins))

        if len(bins) > 10:
            raise Exception("Too many bins defined: Change interval criteria")
        if len(bins) == 10 or len(bins) == 9: # add extra color to reach 10 colors

            if color_order:
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors
                color_list_pos.append('#330808')
                color_list_neg = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors
                color_list_neg.append('#0e2814')
            else:
                color_list_neg = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
                color_list_pos.append('#330808')
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9'
                color_list_pos.append('#0e2814')
        #elif len(bins) == 9:
        #    if color_order:
        #        color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors
        #        color_list_neg = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors
        #    else:
        #        color_list_neg = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
        #        color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9'
        elif len(bins) == 8:
            if color_order:
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors
                color_list_neg = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors
            else:
                color_list_neg = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9'
        else:
            # Colors pos and neg
            if color_order:
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
                color_list_neg = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9'
            else:
                color_list_neg = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9'

        # Number of categories
        #nr_of_cat_pos_neg = int((len(bins) -1) / 2)

        # Invert negative colors
        color_list_neg = color_list_neg[::-1]
        #logging.info("nr_of_cat_pos_neg " + str(nr_of_cat_pos_neg))

        color_list = []

        if max(bins) == 0:
            nr_of_cat_neg = int(len(bins)-1)
            for i in range(nr_of_cat_neg + 1): #add one to get class up to zero
                color_list.append(color_list_neg[i])
        if max(bins) <= 0:
            nr_of_cat_neg = int(len(bins))
            for i in range(nr_of_cat_neg + 1): #add one to get class up to zero
                color_list.append(color_list_neg[i])

            color_list.append(color_zero) # Add 0 color
        elif min(bins) >= 0:
            nr_of_cat_pos = int(len(bins))
            for i in range(nr_of_cat_pos + 1): #add one to get class up to zero
                color_list.append(color_list_neg[i])
            
            color_list.insert(0, color_zero) # Add 0 color
        else:
            nr_of_cat_neg = 0
            nr_of_cat_pos = 0
        
            for i in bins:
                if i < 0:
                    nr_of_cat_neg += 1
                elif i > 0:
                    nr_of_cat_pos += 1
                else:
                    pass
    
            for i in range(nr_of_cat_neg + 1): #add one to get class before first bin
                color_list.append(color_list_neg[i])

            for i in range(nr_of_cat_pos + 1): # add one to get class beyond last bin
                color_list.append(color_list_pos[i])

        return color_list, 'user_defined', True, color_zero

    elif min(bins) > 0:
        print("positive bins " + str(bins))
        color_list = []

        if len(bins) == 10 or len(bins) == 9: # add extra color to reach 10 colors

            if color_order:
                if max(bins) < 0:
                    color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_8').hex_colors
                    color_list_pos.append('#0e2814')
                else:
                    color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_8').hex_colors
                    color_list_pos.append('#330808')
            else:
                if max(bins) < 0:
                    color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9
                    color_list_pos.append('#0e2814')
                else:
                    color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
                    color_list_pos.append('#330808')
        else:
            if color_order:
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Reds_9').hex_colors   # 'Reds_9'
            else:
                color_list_pos = getattr(palettable.colorbrewer.sequential, 'Greens_9').hex_colors # 'Greens_9'
        #color_list_pos = getattr(palettable.colorbrewer.sequential, color_palette).hex_colors

        # Number of categories
        nr_of_cat_pos_neg = int((len(bins)))

        for i in range(nr_of_cat_pos_neg + 1): # add one to get class beyond last bin
            color_list.append(color_list_pos[i])

        return color_list, 'user_defined', True, color_zero

    else:
        # regular classification
        return [], color_prop, False, False
