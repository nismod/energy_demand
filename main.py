# ----------------------------------------------------------------
# Description: Energy Demand Model - Run one year
# Authors: Sven Eggimann, ...
# ----------------------------------------------------------------
import sys, os

print ("Start Energy Demand Model")
print ("Python Version: " + str(sys.version))

path_python = os.getcwd()                           # Get python path
sys.path.append(path_python)                        # Append path
sys.path.append(r'C:\Users\cenv0553\GIT\NISMODII')  # Append path to python files

from main_functions import *                        # Functions main module
import residential_model                            # Residential sub-module
import pdb
#import transition_module                           # Module containing different technology diffusion methods
# ...

# Local paths
path_main = r'C:\Users\cenv0553\GIT\NISMODII\data'
path_pop_reg_lookup = path_main + r'\scenario_and_base_data\lookup_nr_regions.csv'  
path_pop_reg_base = path_main + r'\scenario_and_base_data\population_regions.csv'  
path_dwelling_type_lu = path_main + r'\residential_model\lookup_dwelling_type.csv'
path_lookup_appliances = path_main + r'\residential_model\lookup_appliances.csv'
path_fuel_type_lookup = path_main + r'\scenario_and_base_data\lookup_fuel_types.csv'
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
reg_lookup = read_csv(path_pop_reg_lookup)               # Region lookup table
dwelling_type_lu = read_csv(path_dwelling_type_lu) # Dwelling types lookup table
appliance_type_lu = read_csv(path_lookup_appliances)  # Appliances types lookup table
fuel_type_lookup = read_csv(path_fuel_type_lookup)         # Fuel type lookup
day_type_lu = read_csv(path_day_type_lu)           # Day type lookup
season_lookup = read_csv(path_seasons_lookup)            # Season lookup

print (reg_lookup)
print (dwelling_type_lu)
print (appliance_type_lu)
print (fuel_type_lookup)

# Read in data
pop_region = read_csv(path_pop_reg_base)                 # [float] Population data

print ("Population of regions")
print (pop_region)



# Shape initialisation
# ---------------
shape_appliances_elec = shape_base_resid_appliances(path_base_elec_load_profiles, day_type_lu, appliance_type_lu, sim_param[1]) # HES electricity shape (load profiles for base year given in %)

# Load residential model hourly heating shape

# Load more base demand


# Generate base demand per region and fuel type
# ---------------------
bd_appliances_elec = calc_base_demand_appliances(shape_appliances_elec, reg_lookup, fuel_type_lookup, )




# Generate simulation period
# --------------------------
# Now for 2015...could be written generically
date_list = (
    [date(2015, 1, 12), date(2015, 12, 18)], # Week Spring (Jan) Week 03
    [date(2015, 4, 13), date(2015, 4, 19)], # Week Summer (April) Week 16
    [date(2015, 7, 5), date(2015, 7, 21)], # Week Fall (July) Week 25
    [date(2015, 10, 12), date(2015, 10, 18)], # Week Winter (October) WEek 42
    )

all_different_demands = []

time_steps_base_demand = generate_sim_period(date_list, date_list, reg_lookup, fuel_type_lookup, appliance_type_lu, )


#pdb.set_trace()



# Initialise array to store final energy demands (Region, fule types....)
#print ("Loaded electricity base profiles")
#print(load_profiles[0][35])

def energy_demand_model(sim_param, load_profiles_shape, pop_region, dwelling_type_lu):
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
    ed_h_residential = residential_model.run(sim_param, shape_appliances_elec, pop_region, dwelling_type_lu)

    '''
    transportation_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Industry_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    Service_sector_model.run(modelrun_id, year, year_base, year_curr, total_yr, cur_yr)

    '''
    # Convert results to a format which can be transferred to energy supply model
    #writeToEnergySupply()
    return


# Run 
energy_demand_model(sim_param)

