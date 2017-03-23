""" new load profile generator """

import os
import csv
import unittest
from datetime import date
import matplotlib.pyplot as plt
import energy_demand.data_loader_functions as df
import numpy as np
import main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325


#run_data_collection = False #Scrap
# ---------------------------------------------------
# All pre-processed load shapes are read in from .txt files
# ---------------------------------------------------
def collect_shapes_from_txts(data):

    # ----------------------------------------------------------------------
    # RESIDENTIAL MODEL .txt files
    # ----------------------------------------------------------------------
    # Iterate folders and get all enduse
    path_txt_shapes = data['path_dict']['path_txt_shapes_resid']
    all_csv_in_folder = os.listdir(path_txt_shapes)

    # Read all enduese from files
    enduses = []
    for file_name in all_csv_in_folder:
        enduse = file_name.split("__")[0] # two dashes because individual enduses may contain a single slash
        if enduse not in enduses:
            enduses.append(enduse)
    print("ENDUSES: " + str(enduses))
    # Read shapes from txt files
    for end_use in enduses:
        shape_h_peak = df.read_txt_shape_h_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_h_peak') + str('.txt')))
        shape_h_non_peak = df.read_txt_shape_h_non_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_h_non_peak') + str('.txt')))
        shape_d_peak = df.read_txt_shape_d_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_d_peak') + str('.txt')))
        shape_d_non_peak = df.read_txt_shape_d_non_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_d_non_peak') + str('.txt')))
        data['dict_shp_enduse_h_resid'][end_use] = {'shape_h_peak': shape_h_peak, 'shape_h_non_peak': shape_h_non_peak}
        data['dict_shp_enduse_d_resid'][end_use] = {'shape_d_peak': shape_d_peak, 'shape_d_non_peak': shape_d_non_peak}

    # ----------------------------------------------------------------------
    # SERVICE MODEL .txt files
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Industry MODEL .txt files
    # ----------------------------------------------------------------------

    return data


def generate_data(data):
    """This function loads all that which does not neet to be run every time"""

    base_year_load_data = 2015

    # ===========================================-
    # RESIDENTIAL MODEL
    # ===========================================
    path_txt_shapes = data['path_dict']['path_txt_shapes_resid']

    # HES data -- Generate generic load profiles (shapes) for all electricity appliances from HES data [ % ]
    hes_data, hes_y_peak, _ = df.read_hes_data(data)
    year_raw_values_hes = df.assign_hes_data_to_year(data, hes_data, base_year_load_data)

    # Load shape for all end_uses
    for end_use in data['data_residential_by_fuel_end_uses']:
        if end_use not in data['lu_appliances_HES_matched'][:, 1]:
            print("Enduse not HES data: " + str(end_use))
            continue

        data, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak = df.get_hes_end_uses_shape(data, hes_data, year_raw_values_hes, hes_y_peak, _, end_use)
        df.create_txt_shapes(end_use, path_txt_shapes, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak, "") # Write shapes to txt

    # Robert Sansom, Yearly peak from CSWV - Residential Gas demand, Daily shapes
    wheater_scenarios = ['actual', 'max_cold', 'min_warm'] # Different wheater scenarios to iterate #TODO: MAybe not necessary to read in indivdual shapes for different wheater scneario

    # Iterate wheater scenarios
    for wheater_scen in wheater_scenarios:
        shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak = df.read_shp_heating_gas(data, 'residential', wheater_scen) # Composite Wheater Variable for residential gas heating
        df.create_txt_shapes('heating', path_txt_shapes, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak, wheater_scen) # Write shapes to txt






    # ===========================================
    # SERVICE MODEL DATA GENERATION
    # ===========================================

    # ----------------------------
    # Service Gas demand, Daily shapes taken from Robert Sansom, Yearly peak from CSWV
    # ----------------------------
    #CSV Service
    #shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak = df.read_shp_heating_gas(data, 'service', 'actual') # Composite Wheater Variable for residential gas heating
    #df.create_txt_shapes('heating_service', path_txt_shapes, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak, _) # Write shapes to txt
    # ---------------------
    # Load Carbon Trust data - electricity for non-residential
    # ---------------------

    # ENDUSE XY
    folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\__OWN_SEWAGE' #Community _OWN_SEWAGE
    out_dict_av, out_dict_not_av, hourly_shape_of_maximum_days = df.read_raw_carbon_trust_data(data, folder_path)

    # Read in CWV for non-residential

    # Get yearly profiles
    enduse = 'WHATEVERENDUSE'
    year_data = df.assign_carbon_trust_data_to_year(data, enduse, out_dict_av, base_year_load_data)

    #out_dict_av [daytype, month, ...] ---> Calculate yearly profile with averaged monthly profiles

    # ENDUSE XY
    #folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\__OWN_SEWAGE' #Community _OWN_SEWAGE



    return data
