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

# The docs can be found here: http://ed.readthedocs.io
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
#!python3.6

import sys

import energy_demand.main_functions as mf
import energy_demand.building_stock_generator as bg
import energy_demand.assumptions as assumpt
from energy_demand import residential_model
import energy_demand.technological_stock as ts
import numpy as np
#from datetime import date
print("Start Energy Demand Model with python version: " + str(sys.version))

def energy_demand_model(data, assumptions, data_ext):
    """Main function of energy demand model to calculate yearly demand

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

    # Convert population data int array
    data_ext = mf.add_to_data(data_ext, data_ext['population']) # Convert to array, store in data

    # Run different sub-models (sector models)

    # -- Residential model
    e_app_bd, g_hd_bd = residential_model.run(data_ext['glob_var'], data['shape_app_elec'], data['reg_pop_array'], data_ext['reg_pop_external_array'], data['timesteps_app_bd'], data['timesteps_hd_bd'])


    # new approach - OBJECT ORIENTED
    import energy_demand.main_object_approach as tttt
    tttt.test_run_new_model(data, data_ext, assumptions)



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

    # External data provided to wrapper
    data_external = {'population': {2015: {0: 3000001, 1: 5300001, 2: 53000001},
                                    2016: {0: 3001001, 1: 5301001, 2: 53001001}
                                   },

                     'glob_var': {'base_year': 2015,
                                  'current_year': 2016,
                                  'end_year': 2020
                                 },
                    }


    # ----------- Model calculations outside main function

    # DATA

    # Load data
    base_data = mf.load_data(data_external)
    #print(base_data)

    # Load assumptions
    assumptions_model_run = assumpt.load_assumptions(base_data)

    # Wheater generater (change base_demand data)


    # Generate virtual building stock over whole simulatin period
    #__building_stock = bg.resid_build_stock(base_data, assumptions_model_run, data_external)

    # Generate technological stock over whole simulation period
    #base_tech_stock_resid = ts.resid_tech_stock(2015, assumptions_model_run, data_external)

    #neu = ts.resid_tech_stock(2016, assumptions_model_run, data_external)


    '''print(base.__dict__)
    print("------")
    print(base_tech_stock_resid.NEWDEMAND_tech_A)
    print(base.p_new_tech_A)
    print(neu.driver_lighting())

    ORIG = 100 #kwh
    NEU = ORIG * base.driver_lighting() / neu.driver_lighting()
    print("NEU: " + str(NEU))
    prnt("..")
    '''




    # Run main function
    energy_demand_model(base_data, assumptions_model_run, data_external)
    print("Finished everything")
