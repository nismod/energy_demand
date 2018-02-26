#http://darribas.org/gds15/content/labs/lab_03.html
#https://stackoverflow.com/questions/31755886/choropleth-map-from-geopandas-geodatafame
# http://geopandas.org
import os
import geopandas as gpd
import pandas as pd
import palettable #https://jiffyclub.github.io/palettable/colorbrewer/sequential/
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from energy_demand.basic import basic_functions
from energy_demand.plotting import plotting_styles

def own_classification_work_round(bins, min_value, lad_geopanda_shp, field_name_to_plot):
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
    def rgb2hex(r, g, b):
        """Convert RGB to HEX
        """
        return "#{:02x}{:02x}{:02x}".format(r,g,b)
    
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
    # TODO: REPLACE 0 WITH SAMMELS NUMBER
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
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)

    return lad_geopanda_shp, cmap

def hack_classification(lad_geopanda_shp, bins, color_list, field_name_to_plot):
    """Remap according to user defined classification
    """
    def bin_mapping(x):
        """Maps values to a bin.
        The mapped values must start at 0 and end at 1.
        """
        for idx, bound in enumerate(bins):

            # TODO CHCANGED
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
    lad_geopanda_shp : dataframe
        Geopanda dataframe
    field_name_to_plot : str
        Field name to plot in map
    result_path : str
        Path to figure to plot

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
    '''lad_geopanda_shp.plot(
        axes=axes,
        column=field_name_to_plot,
        cmap='OrRd',
        legend=True)'''

    # -----------------------------
    # Own classification (work around)
    # -----------------------------

    # Get maximum and minum values
    max_value = lad_geopanda_shp[field_name_to_plot].max()
    min_value = lad_geopanda_shp[field_name_to_plot].min()

    # Classification borders
    # Note: 
    #   First bin entry must not be zero! (the first entry is alwys from zero to first entry)
    #   Last bin entry is always theretical maximum
    bins = [50000, 300000, max_value]

    # Hack
    lad_geopanda_shp, cmap = own_classification_work_round(
        bins,
        min_value,
        lad_geopanda_shp,
        field_name_to_plot)

    lad_geopanda_shp.plot(
        axes=axes,
        column='reclassified',
        legend=False,
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

    #from pysal.esda.mapclassify import User_Defined
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

def create_geopanda_files(data, results_container, paths, lu_reg):
    """Create map related files from results

    Arguments
    ---------
    results_container : dict
        Data container
    paths : dict
        Paths
    lu_reg : list
        Region in a list with order how they are stored in result array
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

        for reg_nr, i in enumerate(list(lu_reg)):
            print("REG: {}  {}".format(i, data['scenario_data']['population'][year][reg_nr]))


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