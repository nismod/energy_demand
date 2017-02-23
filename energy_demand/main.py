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

#TODOs data Different appliances for cold/hot extremes, data Heating fro min_max climate

import sys
import os
from datetime import date
import energy_demand.main_functions as mf
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
    # Global variables
    YEAR_SIMULATION = 2015                                                  # Provide year for which to run the simulation
    P1_YEAR_BASE = 2015                                                     # [int] First year of the simulation period
    P2_YEAR_END = 2050                                                      # [int] Last year of the simulation period
    P3_SIM_PERIOD = range(P2_YEAR_END - P1_YEAR_BASE)                       # List with simulation years
    P0_YEAR_CURR = YEAR_SIMULATION - P1_YEAR_BASE                           # [int] Current year in current simulation
    SIM_PARAM = [P0_YEAR_CURR, P1_YEAR_BASE, P2_YEAR_END, P3_SIM_PERIOD]    # Store all parameters in one list



    #------Store all paths to data in dict-------------------
    #path_main = '../data'
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' # Remove
    paths_dict = {'path_pop_reg_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_nr_regions.csv'),
                  'path_pop_reg_base': os.path.join(path_main, 'scenario_and_base_data/population_regions.csv'),
                  'path_dwelling_type_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),
                  'path_lookup_appliances':os.path.join(path_main, 'residential_model/lookup_appliances.csv'),
                  'path_fuel_type_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_fuel_types.csv'),
                  'path_day_type_lu': os.path.join(path_main, 'residential_model/lookup_day_type.csv'),
                  'path_bd_e_load_profiles': os.path.join(path_main, 'residential_model/base_appliances_eletricity_load_profiles.csv'),
                  'path_base_data_fuel': os.path.join(path_main, 'scenario_and_base_data/base_data_fuel.csv'),
                  'path_temp_2015': os.path.join(path_main, 'residential_model/CSV_YEAR_2015.csv'),
                  'path_hourly_gas_shape': os.path.join(path_main, 'residential_model/residential_gas_hourly_shape.csv')
                                           #path_seasons_lookup = os.path.join(path_main, 'scenario_and_base_data/lookup_season.csv')
                 }

    # ------Read in all data from csv files-------------------
    data = mf.read_data(paths_dict)

    # ------Generate generic load profiles (shapes) [in %]-------------------
    shape_app_elec, shape_hd_gas = mf.get_load_curve_shapes(paths_dict['path_bd_e_load_profiles'], data['day_type_lu'], data['app_type_lu'], SIM_PARAM, data['csv_temp_2015'], data['hourly_gas_shape'])

    # ------Base demand for the base year for all modelled elements-------------------

    # Base demand of appliances over a full year (electricity)
    bd_app_elec = mf.get_bd_appliances(shape_app_elec, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])

    # Base demand of heating demand (gas)
    bd_hd_gas = mf.get_bd_hd_gas(shape_hd_gas, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])

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
        [date(P1_YEAR_BASE, 1, 12), date(P1_YEAR_BASE, 1, 18)],     # Week Spring (Jan) Week 03  range(334 : 364) and 0:58
        [date(P1_YEAR_BASE, 4, 13), date(P1_YEAR_BASE, 4, 19)],     # Week Summer (April) Week 16  range(59:150)
        [date(P1_YEAR_BASE, 7, 13), date(P1_YEAR_BASE, 7, 19)],     # Week Fall (July) Week 25 range(151:242)
        [date(P1_YEAR_BASE, 10, 12), date(P1_YEAR_BASE, 10, 18)],   # Week Winter (October) Week 42 range(243:333)
        )

    # Create own timesteps
    own_timesteps = mf.own_timesteps(timesteps_own_selection)

    # Populate timesteps base year data (appliances, electricity)
    fuel_type = 0 # elec
    timesteps_app_bd = mf.create_timesteps_app(timesteps_own_selection, fuel_type, bd_app_elec, data['reg_lu'], data['fuel_type_lu'], data['app_type_lu'], own_timesteps) # [GWh]

    # Populate timesteps base year data (heating demand, ga)
    fuel_type = 1 #gas
    timesteps_hd_bd = mf.create_timesteps_hd(timesteps_own_selection, fuel_type, bd_hd_gas, data['reg_lu'], data['fuel_type_lu'], own_timesteps) # [GWh]

    print("----------------------Statistics--------------------")
    print("Number of timesteps appliances:          " + str(len(timesteps_app_bd[0][0])))
    print("Number of timestpes heating demand:      " + str(len(timesteps_hd_bd[1][0])))
    print(" ")
    print("Sum Appliances simulation period:        " + str(timesteps_app_bd.sum()))
    print("Sum heating emand simulation period:     " + str(timesteps_hd_bd.sum()))
    print(" ")

    data_dict = {'SIM_PARAM': SIM_PARAM,
                 'fuel_type_lu': data['fuel_type_lu'],
                 'dwelling_type_lu': ['dwelling_type_lu'],
                 'reg_pop': ['reg_pop'],
                 'fuel_bd_data': ['fuel_bd_data'],
                 'csv_temp_2015': ['csv_temp_2015'],
                 'hourly_gas_shape': ['hourly_gas_shape'],
                 'shape_app_elec': shape_app_elec,
                 'shape_hd_gas': shape_hd_gas,
                 'bd_app_elec': bd_app_elec,
                 'bd_hd_gas': bd_hd_gas,
                 'timesteps_app_bd': timesteps_app_bd,
                 'timesteps_hd_bd': timesteps_hd_bd,
                 'timesteps_own_selection': timesteps_own_selection}

    #todo: reduce variables
    return data_dict

# ---------------------------------------------------------------
# Run Model
# ---------------------------------------------------------------
def energy_demand_model(data, pop_data_external):
    """Main function to run energy demand module

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        A list containing all data not provided externally

    pop_data_external : dict
        Population data from wrapper

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

    """

    # Get input and convert into necessary formats
    # -------------------------------------------------

    # population data
    _t = pop_data_external.items()
    l = []
    for i in _t:
        l.append(i)
    reg_pop = np.array(l, dtype=float)

    #print ("Energy Demand Model - Main funtion simulation parameter: " + str(SIM_PARAM))

    # ---------------------------------------------------------------------------
    # Run sub modules
    print(" Start executing sub models of energy demand module")
    # ---------------------------------------------------------------------------

    # Run different sub-models (sector models)
    e_app_bd, g_hd_bd = residential_model.run(data['SIM_PARAM'], data['shape_app_elec'], reg_pop, data['timesteps_app_bd'], data['timesteps_hd_bd'])

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
    result_dict = mf.init_dict_energy_supply(data['fuel_type_lu'], reg_pop, timesteps)

    # Add electricity data to result dict for wrapper
    result_dict = mf.add_demand_result_dict(0, e_app_bd, data['fuel_type_lu'], reg_pop, timesteps, result_dict, data['timesteps_own_selection'])

    # Add gas data
    result_dict = mf.add_demand_result_dict(1, g_hd_bd, data['fuel_type_lu'], reg_pop, timesteps, result_dict, data['timesteps_own_selection'])

    # Write YAML file
    yaml_write = False
    if yaml_write: # == True:
        import yaml
        _, yaml_list = mf.timesteps_full_year()                                 # Create timesteps for full year (wrapper-timesteps)
        path_YAML = 'C:/Users/cenv0553/GIT/NISMODII/TESTYAML.yaml'     # l = [{'id': value, 'start': 'p', 'end': 'P2',   }
        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)

    # Write function to also write out results

    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL region:    " + str(len(result_dict[0])))
    print("FINAL timesteps: " + str(len(result_dict[0][0])))
    print("Finished energy demand model")
    return result_dict

# Run
if __name__ == "__main__":
    # New function to load data
    pop_data = {'population': {0: 3000000, 1: 5300000, 2: 53000000}}
    base_data = load_data()
    energy_demand_model(base_data, pop_data["population"])
    print("Finished everything")
