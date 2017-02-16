"""
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
#
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import sys
import os
from datetime import date

print("Start Energy Demand Model")
print("Python Version: " + str(sys.version))

path_python = os.getcwd()                           # Get python path
sys.path.append(path_python)                        # Append path
sys.path.append(r'C:\Users\cenv0553\GIT\NISMODII')  # Append path to python files

import main_functions as mf                         # Functions main module
import residential_model                            # Residential sub-module
#import pdb
#import transition_module                           # Module containing different technology diffusion methods
# ...

# Local paths
path_main = r'C:\Users\cenv0553\GIT\NISMODII\data'
path_pop_reg_lu = path_main + r'\scenario_and_base_data\lookup_nr_regions.csv'
path_pop_reg_base = path_main + r'\scenario_and_base_data\population_regions.csv'
path_dwelling_type_lu = path_main + r'\residential_model\lookup_dwelling_type.csv'
path_lookup_appliances = path_main + r'\residential_model\lookup_appliances.csv'
path_fuel_type_lu = path_main + r'\scenario_and_base_data\lookup_fuel_types.csv'
path_day_type_lu = path_main + r'\residential_model\lookup_day_type.csv'
path_seasons_lookup = path_main + r'\scenario_and_base_data\lookup_season.csv'

path_base_elec_load_profiles = path_main + r'\residential_model\base_appliances_eletricity_load_profiles.csv'   # Path to base population
path_base_data_fuel = path_main + r'\scenario_and_base_data\base_data_fuel.csv'                                 # Path to base fuel data
path_csv_temp_2015 = path_main + r'\residential_model\CSV_YEAR_2015.csv'

# Global variables
P0_YEAR_CURR = 0                                            # [int] Current year in current simulatiod
P1_YEAR_BASE = 2015                                         # [int] First year of the simulation period
P2_YEAR_END = 2050                                          # [int] Last year of the simulation period
P3_SIM_PERIOD = range(P2_YEAR_END - P1_YEAR_BASE)           # List with simulation years

# Store all parameters in one list
sim_param = [P0_YEAR_CURR, P1_YEAR_BASE, P2_YEAR_END, P3_SIM_PERIOD]

# Lookup tables
reg_lu = mf.read_csv(path_pop_reg_lu)                      # Region lookup table
dwelling_type_lu = mf.read_csv(path_dwelling_type_lu)      # Dwelling types lookup table
app_type_lu = mf.read_csv(path_lookup_appliances)          # Appliances types lookup table
fuel_type_lu = mf.read_csv(path_fuel_type_lu)              # Fuel type lookup
day_type_lu = mf.read_csv(path_day_type_lu)                # Day type lookup
season_lookup = mf.read_csv(path_seasons_lookup)           # Season lookup

print(reg_lu)
print(dwelling_type_lu)
print(app_type_lu)
print(fuel_type_lu)

# Read in data
# ------------------
reg_pop = mf.read_csv(path_pop_reg_base, float)            # Population data
fuel_bd_data = mf.read_csv(path_base_data_fuel, float)     # All disaggregated fuels for different regions
csv_temp_2015 = mf.read_csv(path_csv_temp_2015)            # csv_temp_2015
# Read in population, floor area, nr of households etc...for current year (depending on scenario) # TODO


print("reg_pop:         " + str(reg_pop))
print("Fuel data:       " + str(fuel_bd_data))
#print("csv_temp_2015:   " + str(csv_temp_2015))

print("-----------------------Start calculations----------------------------")

# ---------------------------------------------------------------
# Generate generic load profiles (shapes) [in %]
# ---------------------------------------------------------------

# Shape of base year for a full year for appliances (electricity) from HES data [%]
shape_app_elec = mf.shape_bd_app(path_base_elec_load_profiles, day_type_lu, app_type_lu, sim_param[1]) # Sum must be one!

# Shape of base year for a full year for heating demand derived from XX [%]
shape_hd_gas = mf.shape_bd_hd(csv_temp_2015)  # Sum must be one!

# Load more base demand
# ...

print(" Shapes ")
print(" -------")
print("Shape appliances (must be one):      " + str(shape_app_elec.sum()))
print("Shape heating demand (must be one):  " + str(shape_hd_gas.sum()))
print(" ")


# ---------------------------------------------------------------
# Base demands. Calculate base demand per region and fuel type
# ---------------------------------------------------------------

# Base demand of appliances over a full year
bd_app_elec = mf.bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, fuel_bd_data)

# Base demand of heating
bd_hd_gas = mf.bd_hd_gas(shape_hd_gas, reg_lu, fuel_type_lu, fuel_bd_data)

print("--------Stat--before---")
print("Base Fuel elec appliances total per year (uk):             " + str(fuel_bd_data[:, 1].sum()))
print("Base Fuel elec appliances total per year (region, hourly): " + str(bd_app_elec.sum()))
print("  ")
print("Base gas hd appliances total per year (uk):                " + str(fuel_bd_data[:, 2].sum()))
print("Base gas hd appliancestotal per year (region, hourly):     " + str(bd_hd_gas.sum()))


# ---------------------------------------------------------------
# Generate simulation timesteps and assing base demand (e.g. 1 week in each season, 24 hours)
# ---------------------------------------------------------------
# Now for 2015...tood: write generically
timesteps_selection = (
    [date(2015, 1, 12), date(2015, 1, 18)],     # Week Spring (Jan) Week 03
    [date(2015, 4, 13), date(2015, 4, 19)],     # Week Summer (April) Week 16
    [date(2015, 7, 13), date(2015, 7, 19)],     # Week Fall (July) Week 25
    [date(2015, 10, 12), date(2015, 10, 18)],   # Week Winter (October) WEek 42
    )
#timesteps_selection = ([date(2015, 1, 12), date(2015, 12, 31)]) # whole year#

# Appliances timesteps base demand
timesteps_app_bd = mf.create_timesteps_app(timesteps_selection, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu) # [GWh]

# Heating timesteps base demand
timesteps_hd = mf.create_timesteps_hd(timesteps_selection, bd_hd_gas, reg_lu, fuel_type_lu) # [GWh]

print("----------------------Statistics--------------------")
print("Number of timesteps appliances:          " + str(len(timesteps_app_bd[0][0])))
print("Number of timestpes heating demand:      " + str(len(timesteps_hd[1][0])))
print(" ")
print("Sum Appliances simulation period:        " + str(timesteps_app_bd.sum()))
print("Sum heating emand simulation period:     " + str(timesteps_hd.sum()))
print(" ")


#for i in timesteps_hd[0][1]: # gas
#    print("--")
#    print(i)
#    #break

# Heating demand timesteps

# Yearly estimate (# Todo if necessary)

print("---run model---")


def energy_demand_model(sim_param, reg_pop, dwelling_type_lu, timesteps_app_bd, timesteps_hd):
    """
    This function runs the energy demand module

    Input:
    -sim_param
        sim_param[0]    year_curr:    [int] Current year in current simulation
        sim_param[1]    year_base:       [int] Base year (start of simulation period)
        sim_param[2]    year_end:        [int] Last year of the simulation period


    Output:
    - Hourly electrictiy demand
    - Hourly gas demand
    ...
    """
    print ("Energy Demand Model - Main funtion simulation parameter: " + str(sim_param))

    # Simulation parameters
    #year_curr = sim_param[0]
    #year_base = sim_param[1]
    #year_end = sim_param[2]
    #sim_period = sim_param[3]

    # Run different sub-models (sector models)
    ed_ts_residential = residential_model.run(sim_param, shape_app_elec, reg_pop, dwelling_type_lu, timesteps_app_bd)



    '''
    transportation_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Industry_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Service_sector_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    '''
    # ---------------------------------------------------------------------------
    # Convert results to a format which can be transferred to energy supply model
    # ---------------------------------------------------------------------------
    print("Write model results to energy supply")
    print("ed_residential: " + str(ed_ts_residential.sum()))

    path_out_energy_supply_elec = r'C:\Users\cenv0553\GIT\NISMODII\model_output\to_energy_supply_elec.csv'
    path_out_energy_supply_gas = r'C:\Users\cenv0553\GIT\NISMODII\model_output\to_energy_supply_gas.csv'

    mf.writeToEnergySupply(path_out_energy_supply_elec, 0, ed_ts_residential)
    print("-----------------------------------------------------------------------------------")
    mf.writeToEnergySupply(path_out_energy_supply_gas, 1, timesteps_hd)

    return

# Run
energy_demand_model(sim_param, reg_pop, dwelling_type_lu, timesteps_app_bd, timesteps_hd)
