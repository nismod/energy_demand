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
# hp = heat pump
# d = day


# Add Cooling

- Read out individal load shapes

# LOGGING?
    #log_path = os.path.join(data['path_dict']['path_main'][:-5], 'model_output/run_model_log.log')
    #print(log_path)
    #logging.basicConfig(filename=log_path, level=logging.DEBUG, filemode='w')
    #logging.debug('This message should go to the log file')
    #logging.info('So should this')
    #logging.warning('And this, too')

Down the line
- make sure that if a fuel type is added this correspoends to the fuel dict (do not read enfuse from fuel table but seperate tabel)
- data centres (ICT about %, 3/4 end-use devices, network and data centres 1/4 NIC 2017)
Open questions
- PEAK to ED
- Other Enduses from external wrapper?

# TODO: technologies: when on market? (diffusion-advanced )

# Either calculate peak always speratly or assign peak shapes to day with most demand (for heating possible, for appliances other method??)

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
import energy_demand.plot_functions as pf
import energy_demand.national_dissaggregation as nd
import energy_demand.data_loader as dl
import numpy as np
#import logging
print("Start Energy Demand Model with python version: " + str(sys.version))

# Sub modules
import energy_demand.residential_model as rm
import energy_demand.service_model as sm
import energy_demand.industry_model as im
import energy_demand.transport_model as tm

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

    # -------------------------
    # Residential model
    # --------------------------
    resid_object_country = rm.residential_model_main_function(data, data_ext)

    # Convert to dict for energy_supply_model
    result_dict = mf.convert_out_format_es(data, data_ext, resid_object_country)

    # --------------------------
    # Service Model
    # --------------------------
    #service_object_country = sm.service_model_main_function(data, data_ext)

    # --------------------------
    # Industry Model
    # --------------------------
    #industry_object_country = im.service_model_main_function(data, data_ext)

    # --------------------------
    # Transportation Model
    # --------------------------

    # --- Write to csv and YAML
    # mf.write_final_result(data, result_dict, data['lu_reg'], False)

    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL timesteps*regions: " + str(len(result_dict['electricity'])))
    print("Finished energy demand model")

    # Plot Region 0 for half a year
    # pf.plot_x_days(result_dict[2], 0, 2)

    #return result_dict
    return result_dict, resid_object_country #MULTIPLE YEARS

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


    # DUMMY DATA GENERATION----------------------
    by = 2015
    ey = 2020 #always includes this year
    sim_years = range(by, ey + 1)

    pop_dummy = {}
    a = {'Wales': 3000000} #, 'Scotland': 5300000, 'BERN': 5300000}
    for i in sim_years:
        y_data = {}
        for reg in a:
            y_data[reg] = a[reg] # + (a[reg] * 1.04)
        pop_dummy[i] = y_data


    fuel_price_dummy = {}
    a = {0: 10.0, 1: 10.0, 2: 10.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0}
    for i in sim_years:
        y_data = {}
        for reg in a:
            y_data[reg] = a[reg] + 0.3
        fuel_price_dummy[i] = y_data
        a = y_data

    # Scrap meteo
    import random
    meteo = {}
    a = [4, 4, 3, 4, 4, 5, 6, 6, 6, 7, 20, 22, 24, 9, 8, 7, 7, 7, 6, 5, 4, 3, 2, 1]

    for rise_fac, y in enumerate(sim_years, 1):
        new_year_value = []
        for ff in a: # New year value
            #new_year_value.append(ff + ff * (rise_fac/10)) #BECOME HOTTER
            new_year_value.append(ff) #Constant
        temp_y = np.zeros((365, 24))
        for i, d in enumerate(temp_y):
            b = []
            for ff in new_year_value:
                new_year_value_d = ff + ((i/365)*ff)
                b.append(new_year_value_d)
            temp_y[i] = b
        meteo[y] = temp_y
        '''temp_h_y2015[i] = [random.uniform(8.3, 3.7)]*24
        '''

    # DUMMY DATA GENERATION----------------------


    # Reg Floor Area? Reg lookup?
    data_external = {

        'population': pop_dummy,
        'temperature_data': meteo,
        'glob_var' : {},
        #'glob_var': {
        #    'base_yr': 2015,
        #    'curr_yr': 2016,
        #    'end_yr': 2017
        #},
        'fuel_price': fuel_price_dummy,

        # Demand of other sectors
        'external_enduses_resid': {
            #'waste_water': {0: 0},  # Yearly fuel data
            #'ICT_model': {}
        }
    }
    data_external['glob_var']['end_yr'] = ey
    data_external['glob_var']['sim_period'] = range(by, ey + 1, 1)
    data_external['glob_var']['base_yr'] = by # MUST ALWAYS BE MORE THAN ONE.  e.g. only simlulateds the year 2015: range(2015, 2016)
    # ------------------- DUMMY END



    # Model calculations outside main function
    # ----------------------------------------
    path_main = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Load and generate general data
    base_data = dl.load_data(path_main, data_external)

    # Load weather data
    base_data = mf.wheater_generator(base_data)

    # Load assumptions
    base_data = assumpt.load_assumptions(base_data, data_external)

    # Disaggregate national data into regional data
    base_data = nd.disaggregate_base_demand_for_reg(base_data, 1, data_external)

    # Generate virtual building stock over whole simulatin period
    base_data = bg.resid_build_stock(base_data, base_data['assumptions'], data_external)


    # If several years are run:
    results_every_year = []
    for sim_y in sim_years:
        data_external['glob_var']['curr_yr'] = sim_y

        print("-------------------------- ")
        print("SIM RUN:  " + str(sim_y))
        print(data_external['glob_var']['curr_yr'])
        print("-------------------------- ")
        results, resid_object_country = energy_demand_model(base_data, data_external)

        results_every_year.append(resid_object_country)



    # Plot results for every year
    pf.plot_stacked_Country_end_use(results_every_year, base_data)

    # Run main function
    results = energy_demand_model(base_data, data_external)

    print("Finished running Energy Demand Model")

