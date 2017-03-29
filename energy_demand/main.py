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

# TODO: technologies: when on market? (diffusion-advanced )

The docs can be found here: http://ed.readthedocs.io
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
#!python3.6

import os
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
        A nested dictionary containing all data for energy supply model with
        timesteps for every hour in a year.
        [fuel_type : region : timestep]

    """
    # Initialisation

    # SCENARIO UNCERTAINTY
    # TODO: Implement weather generator (multiply fuel with different scenarios)
    # data = wheater_generator(data) # Read in CWV data and calcul difference
    # between average and min and max of year 2015

    # Change demand depending on climate variables

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
    print("FINAL timesteps: " + str(len(result_dict[1]['Wales'])))
    print("Finished energy demand model")

    # Plot Region 0 for half a year
    # pf.plot_x_days(result_dict[2], 0, 2)
    return result_dict


# Run
if __name__ == "__main__":
    # ------------------------------------------------------------------
    # Execute only once before executing energy demand module for a year
    # ------------------------------------------------------------------
    # Weather generater (change base_demand data)
    # { 'population': [ obs, obs ]  }
    # obs.value == 3000000
    # obs.region == 1
    # obs.interval == 2
    # obs.units == 'count'
    # External data provided from wrapper

    # Reg Floor Area? Reg lookup?
    data_external = {
        'population': {
            2015: {'Wales': 3000001, 'Scotland': 5300001},
            2016: {'Wales': 3000001, 'Scotland': 5300001}
        },
        'glob_var': {
            'base_year': 2015,
            'current_yr': 2016,
            'end_year': 2020
        },
        'fuel_price': {
            2015: {0: 10.0, 1: 10.0, 2: 10.0, 3: 10.0, 4: 10.0, 5: 10.0, 6: 10.0, 7: 10.0},
            2016: {0: 12.0, 1: 13.0, 2: 14.0, 3: 12.0, 4: 13.0, 5: 14.0, 6: 13.0, 7: 13.0}
        },
        # Demand of other sectors
        'external_enduses': {
            'waste_water': {0: 0},  # Yearly fuel data
            'ICT_model': {}
        }
    }

    # Model calculations outside main function
    path_main = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Load and generate data
    base_data = dl.load_data(path_main, data_external)

    # Load assumptions
    base_data = assumpt.load_assumptions(base_data)

    # Disaggregate national data into regional data
    base_data = nd.disaggregate_base_demand_for_reg(base_data, 1, data_external)

    # Generate virtual building stock over whole simulatin period
    base_data = bg.resid_build_stock(base_data, base_data['assumptions'], data_external)

    # Run main function
    results = energy_demand_model(base_data, data_external)
    print(results)
    print("Finished running Energy Demand Model")

