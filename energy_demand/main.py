"""Main file containing the energy demand model main function
#
# Description: Energy Demand Model - Run one year
# Authors: Sven Eggimann, ... Aurthors: Pranab Baruah; Scott Thacker
#
# Abbreviations:
# -------------
# bd = Base demand
# by = Base year
# dw = dwelling
# p  = Percent
# e  = electricitiy
# g  = gas
# lu = look up
# h = hour
# d = day

- Read out individal load shapes
- HEating Degree DAys
- efficiencies
- assumptions
- Overall total for every region...own class?


Down the line
- make sure that if a fuel type is added this correspoends to the fuel dict (do not read enfuse from fuel table but seperate tabel)

Open questions
- PEAK to ED
- Other Enduses from external wrapper?
- 
# TODO: Write function to convert array to list and dump it into txt file / or yaml file (np.asarray(a.tolist()))

The docs can be found here: http://ed.readthedocs.io
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
#!python3.6

import sys
import energy_demand.main_functions as mf
import energy_demand.building_stock_generator as bg
import energy_demand.assumptions as assumpt
import energy_demand.technological_stock as ts
import energy_demand.residential_model as rm
import energy_demand.plot_functions as pf
import energy_demand.national_dissaggregation as nd
import energy_demand.data_loader as dl
import numpy as np

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
    result_dict : dict
        A nested dictionary containing all data for energy supply model with timesteps for every hour in a year.
        [fuel_type : region : timestep]

    """
    # Initialisation

    # SCENARIO UNCERTAINTY
    # TODO: Implement wheater generator (multiply fuel with different scenarios)
    #data = wheater_generator(data) # Read in CWV data and calcul difference between average and min and max of year 2015

    # --------------------------
    # Residential model
    # --------------------------
    resid_object_country = rm.residential_model_main_function(data, data_ext)

    # --------------------------
    # Service Model
    # --------------------------

    # --------------------------
    # Industry Model
    # --------------------------

    # --------------------------
    # Transportation Model
    # --------------------------





    # Convert to dict for energy_supply_model
    result_dict = mf.convert_out_format_es(data, data_ext, resid_object_country)

    # --- Write to csv and YAML
    mf.write_final_result(data, result_dict, data['reg_lu'], False)

    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL region:    " + str(len(result_dict[1])))
    print("FINAL timesteps: " + str(len(result_dict[1][0])))
    print("Finished energy demand model")

    # Plot REgion 0 for half a year
    #pf.plot_x_days(result_dict[2], 0, 2)
    return result_dict

# Run
if __name__ == "__main__":

    # -------------------------------------------------------------------
    # Execute only once befure executing energy demand module for a year
    # ------------------------------------------------------------------_
    # Wheater generater (change base_demand data)

    # External data provided from wrapper
    data_external = {'population': {2015: {0: 3000001, 1: 5300001, 2: 53000001},
                                    2016: {0: 3000001, 1: 5300001, 2: 53000001}
                                   },

                     'glob_var': {'base_year': 2015,
                                  'current_year': 2016,
                                  'end_year': 2020
                                 },

                     'fuel_price': {2015: {0: 10.0, 1: 10.0, 2: 10.0, 3: 10.0, 4: 10.0, 5: 10.0, 6: 10.0, 7: 10.0},
                                    2016: {0: 12.0, 1: 13.0, 2: 14.0, 3: 12.0, 4: 13.0, 5: 14.0, 6: 13.0, 7: 13.0}
                                   },
                     # Demand of other sectors
                     'external_enduses': {'waste_water': {0: 0}, #Yearly fuel data
                                          'ICT_model': {}
                                         }
                    }

    # Data container
    base_data = {}

    # Model calculations outside main function
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' #path_main = '../data'
    base_data = dl.load_data(base_data, path_main, data_external) # Load and generate data

    # Load assumptions
    print("Load Assumptions")
    base_data = assumpt.load_assumptions(base_data)

    # Disaggregate national data into regional data
    base_data = nd.disaggregate_base_demand_for_reg(base_data, 1, data_external) 

    # Generate virtual building stock over whole simulatin period
    base_data = bg.resid_build_stock(base_data, base_data['assumptions'], data_external)

    # Generate technological stock for base year (Maybe for full simualtion period? TODO)
    base_data['tech_stock_by'] = ts.ResidTechStock(base_data, data_external, data_external['glob_var']['base_year'])

    # Run main function
    energy_demand_model(base_data, data_external)
    print("Finished running Energy Demand Model")
