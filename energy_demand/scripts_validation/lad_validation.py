"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import numpy as np
def compare_lad_regions(lad_infos_shapefile, model_run_object):
    """Compare gas/elec demand for LADs

    Parameters
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    model_run_object : object
        Model run results

    """
    result_dict = {}

    # Match ECUK sub-regional demand with geocode
    for reg_object in model_run_object.regions:
        result_dict[reg_object.region_name] = {}

        # Iterate loaded data
        for reg_csv_geocode in lad_infos_shapefile:
            if reg_csv_geocode == reg_object.region_name:
                result_dict[reg_object.region_name]['ECUK_electricity_demand'] = lad_infos_shapefile[reg_csv_geocode]['elec_ns_15']
                result_dict[reg_object.region_name]['modelled_electricity_demand'] = np.sum(model_run_object.get_regional_yh(reg_csv_geocode)) #Yearly value
                #TODO:result_dict[region_name]['ECUK_gas_demand'] = lad_infos_shapefile[reg_csv_geocode]['elec_ns_15']
                continue

        # print
    # plot
    prnt(".")


    pass