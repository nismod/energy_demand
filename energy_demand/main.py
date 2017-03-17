"""Main file containing the energy demand model main function
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
# h = hour
# d = day

# The docs can be found here: http://ed.readthedocs.io
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
#!python3.6

import sys
import energy_demand.main_functions as mf
import energy_demand.building_stock_generator as bg
import energy_demand.assumptions as assumpt
import energy_demand.technological_stock as ts
import energy_demand.residential_model as rm

print("Start Energy Demand Model with python version: " + str(sys.version))

def energy_demand_model(data, data_ext):
    """Main function of energy demand model to calculate yearly demand

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally
    data_ext : dict
        All data provided externally

    Returns
    -------
    result_dict : nested dict [fuel_type : region : timestep]
        A nested dictionary containing all data for energy
        supply model with timesteps for every hour in a year.

    Notes
    -----

    """
    all_Regions = []

    # Technological stock
    data['tech_stock'] = ts.resid_tech_stock(data, data_ext)

    # Iterate regions and generate objects
    timesteps, _ = mf.timesteps_full_year()                                 # Create timesteps for full year (wrapper-timesteps)
    result_dict = mf.init_dict_energy_supply(data['fuel_type_lu'], data['reg_pop_array'], timesteps)

    # Create regions for residential model
    for reg in data['reg_lu']:

        # Residential
        a = rm.Region(reg, data, data_ext)
        all_Regions.append(a)

    # Convert to dict for energy_supply_model
    result_dict = mf.convert_result_to_final_total_format(data, all_Regions)


    # Write YAML File
    #mf.write_YAML(False, 'C:/Users/cenv0553/GIT/NISMODII/TESTYAML.yaml')

    # --- Write out functions....scrap to improve
    mf.write_to_csv_will(data, result_dict, data['reg_lu']) #TODO IMprove

    # Write function to also write out results
    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL region:    " + str(len(result_dict[1])))
    print("FINAL timesteps: " + str(len(result_dict[1][0])))
    print("Finished energy demand model")
    return result_dict

# Run
if __name__ == "__main__":

    # Data container
    base_data = {}

    # External data provided to wrapper
    data_external = {'population': {2015: {0: 3000001, 1: 5300001, 2: 53000001},
                                    2016: {0: 3001001, 1: 5301001, 2: 53001001}
                                   },

                     'glob_var': {'base_year': 2015,
                                  'current_year': 2016,
                                  'end_year': 2020
                                 },
                    }

    # Model calculations outside main function
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/'             # #path_main = '../data'
    base_data = mf.load_data(base_data, path_main)                  # Load and generate data

    assumptions_model_run = assumpt.load_assumptions(base_data)     # Load assumptions
    base_data['assumptions'] = assumptions_model_run                # Add assumptions to data

    base_data = mf.disaggregate_base_demand_for_reg(base_data, 1) # Disaggregate national data into regional data

    # Generate virtual building stock over whole simulatin period
    base_data = bg.resid_build_stock(base_data, assumptions_model_run, data_external)

    # Generate technological stock over whole simulation period
    #base_tech_stock_resid = ts.resid_tech_stock(2015, assumptions_model_run, data_external)

    # -----------------
    # Run main function
    # -----------------
    energy_demand_model(base_data, data_external)

    # Wheater generater (change base_demand data)

    # Generate virtual building stock over whole simulatin period
    #__building_stock = bg.resid_build_stock(base_data, assumptions_model_run, data_external)

    # Generate technological stock over whole simulation period
    #base_tech_stock_resid = ts.resid_tech_stock(2015, assumptions_model_run, data_external)

    #neu = ts.resid_tech_stock(2016, assumptions_model_run, data_external)

    print("Finished everything")
