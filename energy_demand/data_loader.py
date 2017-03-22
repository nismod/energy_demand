""" new load profile generator """

import os
import csv
import unittest
from datetime import date
#import main_functions as mf


import matplotlib.pyplot as plt
import data_loader_functions as df
import numpy as np

def generate_data(data, run_data_collection):
    """ This function loads all that which does not neet to be run every time"""
    base_year_load_data = 2015

    if run_data_collection is False:
        # TODO
        # Read in individual CSV files of load shapes
        return data

    # --------------
    # HES data
    # --------------
    # Generate generic load profiles (shapes) for all electricity appliances from HES data [ % ]
    hes_data, hes_y_peak, _ = df.read_hes_data(data)
    year_raw_values_hes = df.assign_hes_data_to_year(data, hes_data, base_year_load_data)

    # Load shape for all end_uses
    for end_use in data['data_residential_by_fuel_end_uses']:
        #print("ENDUSE: " + str(i))
        #end_use = i # End use read from avaialble fuels...
        data = df.get_hes_end_uses_shape(data, hes_data, year_raw_values_hes, hes_y_peak, _, end_use)
    #prnt("oklo")
    # Dump created end_use_dictionaries into txt files #TODO



    # ----------------------------
    # Residential Gas demand ()
    # Daily shapes taken from Robert Sansom
    # Yearly peak from CSWV
    # ----------------------------
    # CSV Residential
    data = df.read_shp_heating_gas(data, 'heating', 'dict_shp_enduse_h_resid', 'dict_shp_enduse_d_resid', 'path_temp_2015')

    #CSV Service
    #data = df.read_shp_heating_gas(data, 'heating', 'dict_shp_enduse_h_service', 'dict_shp_enduse_d_service', 'path_temp_2015_service')


    # ---------------------
    # Load Carbon Trust data
    # - electricity for non-residential
    # -
    # ---------------------
    
    # ENDUSE XY
    folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\__OWN_SEWAGE' #Community _OWN_SEWAGE
    out_dict_av, out_dict_not_av, hourly_shape_of_maximum_days = df.read_raw_carbon_trust_data(data, folder_path)

    # Read in CWV for non-residential

    # Get yearly profiles
    enduse = 'WHATEVERENDUSE'
    year_data = df.assign_carbon_trust_data_to_year(data, enduse, out_dict_av, base_year_load_data)

    '''import matplotlib.pyplot as plt
    import numpy as np

    x_values = range(365 * 24)
    y_values = []
    #y_values = all_hours_year[region].values()

    for day, daily_values in enumerate(year_data):

        # ONLY PLOT HALF A YEAR
        if day < 365:
            for hour in daily_values:
                y_values.append(hour)

    plt.plot(x_values, y_values)

    plt.legend()
    plt.show()
    print("")
    '''
    #out_dict_av [daytype, month, ...] ---> Calculate yearly profile with averaged monthly profiles

    # ENDUSE XY
    folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\__OWN_SEWAGE' #Community _OWN_SEWAGE


    # ADD DICTS TO data


    return data
