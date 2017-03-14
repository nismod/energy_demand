""" new load profile generator """
import numpy as np
import os
import csv
import main_functions as mf
from datetime import date
import unittest
import matplotlib.pyplot as plt
import data_loader_functions as df

def generate_data(data, run_data_collection):
    """ This function loads all that which does not neet to be run every time"""
    base_year_load_data = 2015

    if run_data_collection == False:
        # TODO
        # Read in dumped csv files
        return data

    # --------------
    # HES data
    # --------------
    # Generate generic load profiles (shapes) for all electricity appliances from HES data [ % ]
    hes_data, hes_y_peak, _ = df.read_hes_data(data)
    year_raw_values_hes = df.assign_hes_data_to_year(data, hes_data, base_year_load_data)

    # Load shape for all end_uses
    for i in data['data_residential_by_fuel_end_uses']:
        end_use = i # End use read from avaialble fuels...
        data = df.get_hes_end_uses_shape(data, hes_data, year_raw_values_hes, hes_y_peak, _, end_use)

    # Dump created end_use_dictionaries into txt files #TODO

    # ----------------------------
    # Residential Gas demand ()
    # Daily shapes taken from Robert Sansom
    # Yearly peak from CSWV
    # ----------------------------
    end_use = 'heating'
    data = df.shape_residential_heating_gas(data, end_use)

    return data
