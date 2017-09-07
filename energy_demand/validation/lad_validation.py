"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import os
import sys
import operator
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions

def compare_lad_regions(fig_name, data, lad_infos_shapefile, model_run_object, nr_of_fueltypes, lu_fueltypes, lu_reg):
    """Compare gas/elec demand for LADs

    Parameters
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    model_run_object : object
        Model run results

    Note
    -----
    SOURCE OF LADS:
    """
    print("..Validation of spatial disaggregation")
    result_dict = {}
    result_dict['REAL_electricity_demand'] = {}
    result_dict['modelled_electricity_demand'] = {}

    # Match ECUK sub-regional demand with geocode
    for region_name in lu_reg:

        # Iterate loaded data
        for reg_csv_geocode in lad_infos_shapefile:
            if reg_csv_geocode == region_name:

                # --Sub Regional Electricity
                #value_gwh = conversions.convert_ktoe_gwh(lad_infos_shapefile[reg_csv_geocode]['elec_tot15']) # Add data (CHECK UNIT: TODO)TODO
                result_dict['REAL_electricity_demand'][region_name] = lad_infos_shapefile[reg_csv_geocode]['elec_tot15'] #TODO: CHECK UNIT

                all_fueltypes_reg_demand = model_run_object.get_regional_yh(nr_of_fueltypes, reg_csv_geocode)
                result_dict['modelled_electricity_demand'][region_name] = np.sum(all_fueltypes_reg_demand[lu_fueltypes['electricity']])

    # -----------------
    # Sort results according to size
    # -----------------
    result_dict['modelled_electricity_demand_sorted'] = {}

    # --Sorted sub regional electricity demand
    sorted_dict_REAL_elec_demand = sorted(result_dict['REAL_electricity_demand'].items(), key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    nr_of_labels = len(sorted_dict_REAL_elec_demand)

    x_values = []
    for i in range(nr_of_labels):
        x_values.append(0 + i*0.2)

    y_values_REAL_electricity_demand = []
    y_values_modelled_electricity_demand = []

    labels = []
    for sorted_region in sorted_dict_REAL_elec_demand:
        y_values_REAL_electricity_demand.append(result_dict['REAL_electricity_demand'][sorted_region[0]])
        y_values_modelled_electricity_demand.append(result_dict['modelled_electricity_demand'][sorted_region[0]])
        labels.append(sorted_region)

    # RMSE calculations
    rmse_value = basic_functions.rmse(np.array(y_values_modelled_electricity_demand), np.array(y_values_REAL_electricity_demand))

    # ----------------------------------------------
    # Plot
    # ----------------------------------------------
    plt.figure(figsize=plotting_program.cm2inch(17, 10))
    plt.margins(x=0) #remove white space

    plt.plot(x_values, y_values_REAL_electricity_demand, 'ro', markersize=1, color='green', label='Sub-regional demand (real)')
    plt.plot(x_values, y_values_modelled_electricity_demand, 'ro', markersize=1, color='red', label='Disaggregated demand (modelled)')

    #plt.xticks(x_values, labels, rotation=90)
    plt.ylim(0, 6000)

    title_left = ('Comparison of sub-regional electricity demand (RMSE: {}, number of areas= {})'.format(rmse_value, len(y_values_REAL_electricity_demand)))
    plt.title(title_left, loc='left')
    plt.xlabel("Regions")
    plt.ylabel("Sub-regional yearly electricity demand [GW]")
    plt.legend()

    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))
    #plt.show()
