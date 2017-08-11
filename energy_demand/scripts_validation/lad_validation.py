"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.scripts_basic import unit_conversions
import operator

def compare_lad_regions(lad_infos_shapefile, model_run_object, nr_of_fueltypes, lu_fueltypes):
    """Compare gas/elec demand for LADs

    Parameters
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    model_run_object : object
        Model run results
    
    INFO
    -----
    SOURCE OF LADS:
    """
    print("..Validation of spatial disaggregation")
    result_dict = {}
    result_dict['REAL_electricity_demand'] = {}
    result_dict['modelled_electricity_demand'] = {}

    # Match ECUK sub-regional demand with geocode
    for reg_object in model_run_object.regions:

        # Iterate loaded data
        for reg_csv_geocode in lad_infos_shapefile:
            if reg_csv_geocode == reg_object.region_name:

                # --Sub Regional Electricity
                #value_gwh = unit_conversions.convert_ktoe_gwh(lad_infos_shapefile[reg_csv_geocode]['elec_tot15']) # Add data (CHECK UNIT: TODO)TODO
                result_dict['REAL_electricity_demand'][reg_object.region_name] = lad_infos_shapefile[reg_csv_geocode]['elec_tot15'] #TODO: CHECK UNIT

                all_fueltypes_reg_demand = model_run_object.get_regional_yh(nr_of_fueltypes, reg_csv_geocode)
                result_dict['modelled_electricity_demand'][reg_object.region_name] = np.sum(all_fueltypes_reg_demand[lu_fueltypes['electricity']])

    # -----------------
    # Sort results according to size
    # -----------------
    result_dict['modelled_electricity_demand_sorted'] = {}

    # --Sorted sub regional electricity demand
    sorted_dict_REAL_elec_demand = sorted(result_dict['REAL_electricity_demand'].items(), key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    nr_of_labels = len(sorted_dict_REAL_elec_demand) #range(len(sorted_dict_REAL_elec_demand))
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

    plt.plot(x_values, y_values_REAL_electricity_demand, 'ro', markersize=1, color='green', label='Sub-regional demand (real)')
    plt.plot(x_values, y_values_modelled_electricity_demand, 'ro', markersize=1, color='red', label='Disaggregated demand (modelled)')

    plt.xticks(x_values, labels)

    plt.xlabel("Comparison of sub-regional electricity demand")
    plt.ylabel("Electricity demand [unit GWH?]")
    plt.legend()

    plt.show()
