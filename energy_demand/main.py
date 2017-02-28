"""Main file
#
# Description: Energy Demand Model - Run one year
# Authors: Sven Eggimann, ...
#
# Abbreviations:
# -------------
# bd = Base demand
# by = Base year
# p  = Percent
# e  = electricitiy
# g  = gas
# lu = look up

# The docs can be found here: http://ed.readthedocs.io

#"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

#!python3.6

# NOCHT TUN ata Different appliances for cold/hot extremes, data Heating fro min_max climate

import sys
from datetime import date
import energy_demand.main_functions as mf
import building_stock_generator as bg
import assumptions as assumpt

from energy_demand import residential_model
import numpy as np

print("Start Energy Demand Model with python version: " + str(sys.version))

def load_data():
    """All base data no provided externally are loaded

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------

    Returns
    -------
    data : list
        Returns a list where all datas are wrapped together.

    Notes
    -----

    """
    #path_main = '../data'
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' # Remove

    # ------Read in all data from csv files-------------------
    data, path_dict = mf.read_data(path_main)

    # Global variables
    global_variables = {'base_year': 2015, 'current_year': 2015, 'end_year': 2050}
    data['global_variables'] = global_variables # add to data dict

    #print(isinstance(reg_floor_area[0], int))
    #print(isinstance(reg_floor_area[0], float))


    # ------Generate generic load profiles (shapes) [in %]-------------------
    shape_app_elec, shape_hd_gas = mf.get_load_curve_shapes(path_dict['path_bd_e_load_profiles'], data['day_type_lu'], data['app_type_lu'], global_variables, data['csv_temp_2015'], data['hourly_gas_shape'])
    data['shape_app_elec'] = shape_app_elec # add to data dict

    # ------Base demand for the base year for all modelled elements-------------------

    # Base demand of appliances over a full year (electricity)
    bd_app_elec = mf.get_bd_appliances(shape_app_elec, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])
    data['bd_app_elec'] = bd_app_elec # add to data dict

    # Base demand of heating demand (gas)
    bd_hd_gas = mf.get_bd_hd_gas(shape_hd_gas, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])
    data['bd_hd_gas'] = bd_hd_gas # add to data dict

    print("---Summary Base Demand")
    print("Base Fuel elec appliances total per year (uk):             " + str(data['fuel_bd_data'][:, 1].sum()))
    print("Base Fuel elec appliances total per year (region, hourly): " + str(bd_app_elec.sum()))
    print("  ")
    print("Base gas hd appliances total per year (uk):                " + str(data['fuel_bd_data'][:, 2].sum()))
    print("Base gas hd appliancestotal per year (region, hourly):     " + str(bd_hd_gas.sum()))

    # ---------------------------------------------------------------
    # Generate simulation timesteps and assing base demand (e.g. 1 week in each season, 24 hours)
    # ---------------------------------------------------------------
    timesteps_own_selection = (
        [date(global_variables['base_year'], 1, 12), date(global_variables['base_year'], 1, 18)],     # Week Spring (Jan) Week 03  range(334 : 364) and 0:58
        [date(global_variables['base_year'], 4, 13), date(global_variables['base_year'], 4, 19)],     # Week Summer (April) Week 16  range(59:150)
        [date(global_variables['base_year'], 7, 13), date(global_variables['base_year'], 7, 19)],     # Week Fall (July) Week 25 range(151:242)
        [date(global_variables['base_year'], 10, 12), date(global_variables['base_year'], 10, 18)],   # Week Winter (October) Week 42 range(243:333)
        )
    data['timesteps_own_selection'] = timesteps_own_selection # add to data dict

    # Create own timesteps
    own_timesteps = mf.own_timesteps(timesteps_own_selection)

    # Populate timesteps base year data (appliances, electricity)
    timesteps_app_bd = mf.create_timesteps_app(0, timesteps_own_selection, bd_app_elec, data['reg_lu'], data['fuel_type_lu'], data['app_type_lu'], own_timesteps) # [GWh]
    data['timesteps_app_bd'] = timesteps_app_bd # add to data dict

    # Populate timesteps base year data (heating demand, ga)
    timesteps_hd_bd = mf.create_timesteps_hd(1, timesteps_own_selection, bd_hd_gas, data['reg_lu'], data['fuel_type_lu'], own_timesteps) # [GWh]
    data['timesteps_hd_bd'] = timesteps_hd_bd # add to data dict

    print("----------------------Statistics--------------------")
    print("Number of timesteps appliances:          " + str(len(timesteps_app_bd[0][0])))
    print("Number of timestpes heating demand:      " + str(len(timesteps_hd_bd[1][0])))
    print(" ")
    print("Sum Appliances simulation period:        " + str(timesteps_app_bd.sum()))
    print("Sum heating emand simulation period:     " + str(timesteps_hd_bd.sum()))
    print(" ")

    return data




# ---------------------------------------------------------------
# Run Model
# ---------------------------------------------------------------
def energy_demand_model(data, assumptions, data_ext):
    """Main function to run energy demand module

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally
    assumptions : dict
        Contains all assumptions
    data_ext : dict
        All data provided externally

    Returns
    -------
    result_dict : nested dict
        A nested dictionary containing all data for energy
        supply model with timesteps for every hour in a year.
        fuel_type
            region
                timestep

    Notes
    -----
    All messy now...needs cleaning
    """
    # Add external data to data dictionary
    # ----

    # Conert population data int array
    data_ext = mf.add_to_data(data_ext, data_ext['population']) # Convert to array, store in data

    #print ("Energy Demand Model - Main funtion simulation parameter: " + str(global_variables))


    # Build base year building stock

    # Build virtual residential building stock
    old_dwellings, new_dwellings = bg.virtual_building_stock(data, assumptions, data_ext)


    # Run different sub-models (sector models)
    # -- Residential model
    e_app_bd, g_hd_bd = residential_model.run(data['global_variables'], data['shape_app_elec'], data['reg_pop_array'], data_ext['reg_pop_external_array'], data['timesteps_app_bd'], data['timesteps_hd_bd'])
    #print(e_app_bd[0][0])

    '''
    transportation_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Industry_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Service_sector_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    '''

    # ---------------------------------------------------------------------------
    # Generate the wrapper timesteps and add instert data (from own timeperiod to full year)
    print("Generate resutls for wrapper (read into nested dictionary")
    # ---------------------------------------------------------------------------
    timesteps, _ = mf.timesteps_full_year()                                 # Create timesteps for full year (wrapper-timesteps)

    # Initialise nested Dicionatry for wrapper (Fuel type, region, hour)
    result_dict = mf.init_dict_energy_supply(data['fuel_type_lu'], data['reg_pop_array'], timesteps)

    # Add electricity data to result dict for wrapper
    result_dict = mf.add_demand_result_dict(0, e_app_bd, data['fuel_type_lu'], data['reg_pop_array'], timesteps, result_dict, data['timesteps_own_selection'])
    #print(result_dict[0][0])
    #prnt("..")
    # Add gas data
    result_dict = mf.add_demand_result_dict(1, g_hd_bd, data['fuel_type_lu'], data['reg_pop_array'], timesteps, result_dict, data['timesteps_own_selection'])

    # Write YAML File
    #mf.write_YAML(False, 'C:/Users/cenv0553/GIT/NISMODII/TESTYAML.yaml')

    # --- Write out functions....scrap to improve
    #mf.write_to_csv_will(result_dict, data['reg_lu'])
    #rint("..")


    # Write function to also write out results
    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL region:    " + str(len(result_dict[0])))
    print("FINAL timesteps: " + str(len(result_dict[0][0])))
    print("Finished energy demand model")
    print(result_dict[0][0])
    return result_dict

# Run
if __name__ == "__main__":
    # New function to load data
    data_external = {'population': {0: 3000001, 1: 5300001, 2: 53000001}}

    base_data = load_data()     # Get own data
    assumptions = assumpt.load_assumptions() # Get all assumptions

    energy_demand_model(base_data, assumptions, data_external)
    print("Finished everything")
