"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.scripts_basic import unit_conversions

def compare_lad_regions(lad_infos_shapefile, model_run_object, nr_of_fueltypes, lu_fueltypes):
    """Compare gas/elec demand for LADs

    Parameters
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    model_run_object : object
        Model run results

    """
    print("..Validation of spatial disaggregation")
    result_dict = {}

    # Match ECUK sub-regional demand with geocode
    for reg_object in model_run_object.regions:
        result_dict[reg_object.region_name] = {}

        # Iterate loaded data
        for reg_csv_geocode in lad_infos_shapefile:
            if reg_csv_geocode == reg_object.region_name:


                #value_gwh = unit_conversions.convert_ktoe_gwh(lad_infos_shapefile[reg_csv_geocode]['elec_tot15']) # Add data (CHECK UNIT: TODO)TODO
                value_gwh = lad_infos_shapefile[reg_csv_geocode]['elec_tot15'] #TODO: CHECK UNIT

                result_dict[reg_object.region_name]['ECUK_electricity_demand'] = value_gwh
                all_fueltypes_reg_demand = model_run_object.get_regional_yh(nr_of_fueltypes, reg_csv_geocode)

                result_dict[reg_object.region_name]['modelled_electricity_demand'] = np.sum(all_fueltypes_reg_demand[lu_fueltypes['electricity']])

                #TODO:result_dict[region_name]['ECUK_gas_demand'] = lad_infos_shapefile[reg_csv_geocode]['elec_ns_15']
    
    # -----------------
    # Sort results
    # -----------------

    # -------------------------------------
    # Plot
    # -------------------------------------
    x_values = range(len(result_dict))
    y_values_ECUK_electricity_demand = []
    y_values_modelled_electricity_demand = []

    labels = []
    for entry in result_dict:
        y_values_ECUK_electricity_demand.append(result_dict[entry]['ECUK_electricity_demand'])
        y_values_modelled_electricity_demand.append(result_dict[entry]['modelled_electricity_demand'])
        labels.append(entry)

    print("REAL " + str(y_values_ECUK_electricity_demand))
    print("MODELLE " + str(y_values_modelled_electricity_demand))
    plt.plot(x_values, y_values_ECUK_electricity_demand, 'ro', markersize=5, color='green')
    plt.plot(x_values, y_values_modelled_electricity_demand, 'ro', markersize=5, color='red')

    plt.xticks(x_values, labels)
    plt.xlabel("Comparison of energy demand in regions")
    #plt.legend()
    plt.show()
