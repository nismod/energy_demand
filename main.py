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

print("Start Energy Demand Model")
print("Python Version: " + str(sys.version))

path_python = os.getcwd()                           # Get python path
sys.path.append(path_python)                        # Append path
sys.path.append(r'C:\Users\cenv0553\GIT\NISMODII')  # Append path to python files

from main_functions import *                        # Functions main module
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

path_base_elec_load_profiles = path_main + r'\residential_model\base_appliances_eletricity_load_profiles.csv'  # Path to base population
path_base_data_fuel = path_main + r'\scenario_and_base_data\base_data_fuel.csv'  # Path to base population

# Global variables
p0_year_curr = 0                                    # [int] Current year in current simulatiod
P1_year_base = 2015                                 # [int] First year of the simulation period
p2_year_end = 2050                                  # [int] Last year of the simulation period
P3_sim_period = range(p2_year_end - P1_year_base)   # List with simulation years

# Store all parameters in one list
sim_param = [p0_year_curr, P1_year_base, p2_year_end, P3_sim_period]

# Lookup tables
reg_lu = read_csv(path_pop_reg_lu)                      # Region lookup table
dwelling_type_lu = read_csv(path_dwelling_type_lu)      # Dwelling types lookup table
app_type_lu = read_csv(path_lookup_appliances)    # Appliances types lookup table
fuel_type_lu = read_csv(path_fuel_type_lu)              # Fuel type lookup
day_type_lu = read_csv(path_day_type_lu)                # Day type lookup
season_lookup = read_csv(path_seasons_lookup)           # Season lookup
print(reg_lu)
print(dwelling_type_lu)
print(app_type_lu)
print(fuel_type_lu)

# Read in data
# ------------------
pop_region = read_csv(path_pop_reg_base, float)         # Population data
bd_fuel_data = read_csv(path_base_data_fuel, float)      # All disaggregated fuels for different regions
# Read in population, floor area, nr of households etc...for current year (depending on scenario) # TODO

print(pop_region)
print(bd_fuel_data)
print("-----------------------Start calculations----------------------------")

# ---------------------------------------------------------------
# Shape initialisation. Generate generic load profiles [in %]
# ---------------------------------------------------------------

# Shape appliances electricity for base year derived from HES data [%]
shape_app_elec = shape_bd_app(path_base_elec_load_profiles, day_type_lu, app_type_lu, sim_param[1])

# Shape heating demand for base year derived from XX [%]

# Load more base demand

# ---------------------------------------------------------------
# Base demands. Calculate base demand per region and fuel type
# ---------------------------------------------------------------

# Base demand of appliances over a full year
bd_app_elec = bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, bd_fuel_data)

# Base demand of heating
'''for reg in range(len(bd_app_elec[0])):
    cntd = 0
    ydaycnt = 0
    for yday in bd_app_elec[reg][0]:
        print("REGA " + str(ydaycnt) + ("   ") + str(yday.sum()))
        ydaycnt += 1
        cntd +=1
        if cntd == 7:
            cntd = 0
            break
prnt("..")
'''

print("--------")
print("Base Fuel sum total per year (uk):             " + str(bd_fuel_data[:, 1].sum()))
print("Base Fuel sum total per year (region, hourly): " + str(bd_app_elec.sum()))
print("ll: " + str(len(bd_app_elec[0][0])))

# ---------------------------------------------------------------
# Generate simulation timesteps and assing base demand (e.g. 1 week in each season, 24 hours)
# ---------------------------------------------------------------
# Now for 2015...tood: write generically
timesteps_selection = (
    [date(2015, 1, 12), date(2015, 1, 18)], # Week Spring (Jan) Week 03
    [date(2015, 4, 13), date(2015, 4, 19)], # Week Summer (April) Week 16
    [date(2015, 7, 13), date(2015, 7, 19)], # Week Fall (July) Week 25
    [date(2015, 10, 12), date(2015, 10, 18)], # Week Winter (October) WEek 42
    )
#timesteps_selection = ([date(2015, 1, 12), date(2015, 12, 31)]) # whole year#

# Appliances timesteps base demand
timesteps_app_bd = create_timesteps_app(timesteps_selection, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu) # [GWh]

print("Base fuel electrictiy appliances timsteps: " + str(timesteps_app_bd.sum()))
# Heating demand timesteps

# Yearly estimate (# Todo if necessary)

def energy_demand_model(sim_param, pop_region, dwelling_type_lu, timesteps_app_bd):
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
    ed_ts_residential = residential_model.run(sim_param, shape_app_elec, pop_region, dwelling_type_lu, timesteps_app_bd)

    '''
    transportation_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Industry_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Service_sector_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    '''

    # Convert results to a format which can be transferred to energy supply model
    print("Write model results to energy supply")
    print("ed_residential: " + str(ed_ts_residential.sum()))

    path_out_energy_supply_gas = r'C:\Users\cenv0553\GIT\NISMODII\model_output\to_energy_supply_gas.csv'
    path_out_energy_supply_elec = r'C:\Users\cenv0553\GIT\NISMODII\model_output\to_energy_supply_elec.csv'

    writeToEnergySupply(path_out_energy_supply_elec, ed_ts_residential)
    #writeToEnergySupply(path_out_energy_supply_gas)

    return

# Run
energy_demand_model(sim_param, pop_region, dwelling_type_lu, timesteps_app_bd)
