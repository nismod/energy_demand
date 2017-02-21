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
# g  = gas5
# lu = look up
#
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

#TODO Switch applian5ces and hours
#TODO data Different appliances for cold/hot extremes
#TODO data Heating fro min_max climate 
import sys
import os
from datetime import date
import numpy as np

import main_functions as mf                         # Functions main module
import residential_model                            # Residential sub-module
print("Start Energy Demand Model")
print("Python Version: " + str(sys.version))

def load_data():
    """ This funciton loads all base data

    """
    path_python = os.getcwd()                           # Get python path
    sys.path.append(path_python)                        # Append path
    sys.path.append(r'C:\Users\cenv0553\GIT\NISMODII')  # Append path to python files


    #import transition_module                           # Module containing different technology diffusion methods
    # ... more imports

    # Local paths #TODO: Reade from database? Read on server?
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
    path_temp_2015 = path_main + r'\residential_model\CSV_YEAR_2015.csv'                                            # Path to temperature data
    path_hourly_gas_shape = path_main +  r'\residential_model\residential_gas_hourly_shape.csv'                     # Path to hourly gas shape

    # Global variables
    YEAR_SIMULATION = 2015                                                  # Provide year for which to run the simulation
    P1_YEAR_BASE = 2015                                                     # [int] First year of the simulation period
    P2_YEAR_END = 2050                                                      # [int] Last year of the simulation period
    P3_SIM_PERIOD = range(P2_YEAR_END - P1_YEAR_BASE)                       # List with simulation years
    P0_YEAR_CURR = YEAR_SIMULATION - P1_YEAR_BASE                           # [int] Current year in current simulation
    SIM_PARAM = [P0_YEAR_CURR, P1_YEAR_BASE, P2_YEAR_END, P3_SIM_PERIOD]    # Store all parameters in one list

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
    reg_pop = mf.read_csv(path_pop_reg_base, float)                  # Population data
    fuel_bd_data = mf.read_csv(path_base_data_fuel, float)          # All disaggregated fuels for different regions
    csv_temp_2015 = mf.read_csv(path_temp_2015)                     # csv_temp_2015
    hourly_gas_shape = mf.read_csv(path_hourly_gas_shape, float)   # Load hourly shape for gas from Robert Sansom
    # Read in more date such as floor area, nr of households etc. for base year # TODO

    #print("reg_pop:         " + str(reg_pop))
    #print("Fuel data:       " + str(fuel_bd_data))
    #print(hourly_gas_shape)  # Day, weekday, weekend
    
    print("-----------------------Start calculations----------------------------")
    # ---------------------------------------------------------------
    # Generate generic load profiles (shapes) [in %]
    # ---------------------------------------------------------------

    # Shape of base year for a full year for appliances (electricity) from HES data [%]
    shape_app_elec = mf.shape_bd_app(path_base_elec_load_profiles, day_type_lu, app_type_lu, SIM_PARAM[1])

    # Shape of base year for a full year for heating demand derived from XX [%]
    shape_hd_gas = mf.shape_bd_hd(csv_temp_2015, hourly_gas_shape)

    # Load more base demand
    # ...
    # ---------------------------------------------------------------
    # Base demand for the base year for all modelled elements
    # ---------------------------------------------------------------

    # Base demand of appliances over a full year (electricity)
    bd_app_elec = mf.bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, fuel_bd_data)

    # Base demand of heating demand (gas)
    bd_hd_gas = mf.bd_hd_gas(shape_hd_gas, reg_lu, fuel_type_lu, fuel_bd_data)

    print("---Summary Base Demand")
    print("Base Fuel elec appliances total per year (uk):             " + str(fuel_bd_data[:, 1].sum()))
    print("Base Fuel elec appliances total per year (region, hourly): " + str(bd_app_elec.sum()))
    print("  ")
    print("Base gas hd appliances total per year (uk):                " + str(fuel_bd_data[:, 2].sum()))
    print("Base gas hd appliancestotal per year (region, hourly):     " + str(bd_hd_gas.sum()))

    # ---------------------------------------------------------------
    # Generate simulation timesteps and assing base demand (e.g. 1 week in each season, 24 hours)
    # ---------------------------------------------------------------
    timesteps_selection = (
        [date(P1_YEAR_BASE, 1, 12), date(P1_YEAR_BASE, 1, 18)],     # Week Spring (Jan) Week 03
        [date(P1_YEAR_BASE, 4, 13), date(P1_YEAR_BASE, 4, 19)],     # Week Summer (April) Week 16
        [date(P1_YEAR_BASE, 7, 13), date(P1_YEAR_BASE, 7, 19)],     # Week Fall (July) Week 25
        [date(P1_YEAR_BASE, 10, 12), date(P1_YEAR_BASE, 10, 18)],   # Week Winter (October) Week 42
        )

    # Whole year
    #timesteps_selection = ([date(P1_YEAR_BASE, 1, 12), date(P1_YEAR_BASE, 12, 31)], []) # whole year

    # Populate timesteps base year data (appliances, electricity)
    timesteps_app_bd = mf.create_timesteps_app(timesteps_selection, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu) # [GWh]

    # Populate timesteps base year data (heating demand, ga)
    timesteps_hd_bd = mf.create_timesteps_hd(timesteps_selection, bd_hd_gas, reg_lu, fuel_type_lu) # [GWh]

    print("----------------------Statistics--------------------")
    print("Number of timesteps appliances:          " + str(len(timesteps_app_bd[0][0])))
    print("Number of timestpes heating demand:      " + str(len(timesteps_hd_bd[1][0])))
    print(" ")
    print("Sum Appliances simulation period:        " + str(timesteps_app_bd.sum()))
    print("Sum heating emand simulation period:     " + str(timesteps_hd_bd.sum()))
    print(" ")
    return SIM_PARAM, fuel_type_lu, dwelling_type_lu, reg_pop, fuel_bd_data, csv_temp_2015, hourly_gas_shape, shape_app_elec, shape_hd_gas, bd_app_elec, bd_hd_gas, timesteps_app_bd, timesteps_hd_bd

# ---------------------------------------------------------------
# Run Model
# ---------------------------------------------------------------
def energy_demand_model(SIM_PARAM, reg_pop, dwelling_type_lu, timesteps_app_bd, timesteps_hd_bd, fuel_type_lu):
    """
    This function runs the energy demand module

    Input:
    -SIM_PARAM
        SIM_PARAM[0]    year_curr:    [int] Current year in current simulation
        SIM_PARAM[1]    year_base:       [int] Base year (start of simulation period)
        SIM_PARAM[2]    year_end:        [int] Last year of the simulation period
        ...

    Output:

    """
    print ("Energy Demand Model - Main funtion simulation parameter: " + str(SIM_PARAM))

    # Run different sub-models (sector models)
    e_app_bd, g_hd_bd = residential_model.run(SIM_PARAM, shape_app_elec, reg_pop, timesteps_app_bd, timesteps_hd_bd)

    '''
    transportation_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Industry_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Service_sector_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    '''

    # ---------------------------------------------------------------------------
    # Write timestpes to energy demand model
    # ---------------------------------------------------------------------------
    #print("Write model results to energy supply")
    #print("ed_residential: " + str(e_app_bd.sum()))
    #path_out_energy_supply_elec = r'C:\Users\cenv0553\GIT\NISMODII\model_output\to_energy_supply_elec.csv'      # Out path to energy supply model
    #path_out_energy_supply_gas = r'C:\Users\cenv0553\GIT\NISMODII\model_output\to_energy_supply_gas.csv'        # Out path to energy supply model

    # Write timesteps to csv
    #mf.writeToEnergySupply(path_out_energy_supply_elec, 0, e_app_bd)
    #mf.writeToEnergySupply(path_out_energy_supply_gas, 1, g_hd_bd)

    # Create resutl file Hackathon
    # ----

    # Create timesteps
    timesteps = mf.timesteps_full_year()

    print(timesteps[str('99_1')])
    print("...")
    print("len: " + str(len(timesteps)))

    # Nested Dicionatry
    #result_array = np.zeros((len(fuel_type_lu), len(reg_pop), len(timesteps))) # Fuel Type, Region, Hour
    result_dict = {}
    for i in range(len(fuel_type_lu)):
        result_dict[i] = {}
        for j in range(len(reg_pop)):
            result_dict[i][j] = {}
            for k in range(len(timesteps)):
                result_dict[i][j][k] = {}

    #d['dict1'] = {}
    #d['dict1']['innerkey'] = 'value'

    # Fill timesteps with electrictiy data
    fuel_elec = 0

    for region_nr in range(len(reg_pop)):
        print("REGION: " + str(region_nr))
        year_hour = 0
        for timestep in timesteps: #Iterate over timesteps
            year_hour += 1
            timestep_id = str(timestep)
            #print(timestep_id)
            _yearday = int(timestep.split("_")[0])   # Yearday
            _h = int(timestep.split("_")[1])         # Hour

            start_period = timesteps[timestep][0]
            end_period = timesteps[timestep][1]
            #print("---------------------------")
            #print("timestep; " + str(timestep))
            '''print(timestep.split("_")[0])
            print(timestep.split("_")[1])
            print("..")
            print ("start_period:   " + str(start_period))
            print ("end_period:     " + str(end_period))
            print("reg_yeardayion_nr:       " + str(_yearday))
            print("_h:              "                + str(_h))'''
            #print("timestep_id:     " + str(timestep_id))

            #result_array[fuel_elec][region_nr][timestep_id] = e_app_bd[fuel_elec][region_nr][_h].sum() # List with data out
            result_dict[fuel_elec][region_nr][timestep_id] = e_app_bd[fuel_elec][region_nr][_h].sum()
            #print(" Region: " + str(region_nr) + str("  year_hour; " + str(year_hour)) + str("   Demand teimstep:  ") + str(timestep) + str("   Sum: " + str(e_app_bd[fuel_elec][region_nr][_h].sum())))


    # Write YAML file
    # ---------------
    '''
    - start: P0H
  end: P1H
  id: Whatever
- start: P1H
  end: P2H
  id: Whatever


    '''
    import yaml

    #for i in timesteps:
        
    path_YAML = r'C:\Users\cenv0553\GIT\NISMODII\TESTYAML.yaml'
    with open(path_YAML, 'w') as outfile:
        
        yaml.dump(timesteps, outfile, default_flow_style=False)

    print("Finished energy demand model")
    return result_dict

# Run
if __name__ == "__main__":
    # New function to load data
    SIM_PARAM, fuel_type_lu, dwelling_type_lu, reg_pop, fuel_bd_data, csv_temp_2015, hourly_gas_shape, shape_app_elec, shape_hd_gas, bd_app_elec, bd_hd_gas, timesteps_app_bd, timesteps_hd_bd = load_data()
    energy_demand_model(SIM_PARAM, reg_pop, dwelling_type_lu, timesteps_app_bd, timesteps_hd_bd, fuel_type_lu)
