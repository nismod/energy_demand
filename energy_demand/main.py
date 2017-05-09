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

Down the line
- make sure that if a fuel type is added this correspoends to the fuel dict (do not read enfuse from fuel table but seperate tabel)
- data centres (ICT about %, 3/4 end-use devices, network and data centres 1/4 NIC 2017)
Open questions
- PEAK to ED
- Other Enduses from external wrapper?

# TODO: technologies: when on market? (diffusion-advanced )

# Either calculate peak always speratly or assign peak shapes to day with most demand (for heating possible, for appliances other method??)
cleaning ttt
The docs can be found here: http://ed.readthedocs.io
5"""
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
import random

print("Start Energy Demand Model with python version: " + str(sys.version))

# Import sub modules
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
    sim_years = range(by, ey + 1) #TODO: TEST Everyhwere wher len(sim_years) is used

    pop_dummy = {}
    a = {'Wales': 3000000} #, 'Scotland': 5300000, 'England': 5300000}
    for i in sim_years:
        y_data = {}
        for reg in a:
            y_data[reg] = a[reg] # + (a[reg] * 1.04)
        pop_dummy[i] = y_data

    # dummy coordinates
    coord_dummy = {}
    coord_dummy['Wales'] = {'longitude': 52.289288, 'latitude': -3.610933}
    coord_dummy['Scotland'] = {'longitude': 56.483100, 'latitude': -4.027093}
    coord_dummy['England'] = {'longitude': 52.874205, 'latitude': -0.871205}

    fuel_price_dummy = {}
    a = {0: 10.0, 1: 10.0, 2: 10.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0}
    for i in sim_years:
        y_data = {}
        for reg in a:
            y_data[reg] = a[reg] + 0.3
        fuel_price_dummy[i] = y_data
        a = y_data
    # DUMMY DATA GENERATION----------------------


    # Reg Floor Area? Reg lookup?
    data_external = {

        'population': pop_dummy,
        'region_coordinates': coord_dummy,
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
    data_external['glob_var']['sim_period'] = range(by, ey + 1, 1) # Alywas including last simulation year
    data_external['glob_var']['base_yr'] = by # MUST ALWAYS BE MORE THAN ONE.  e.g. only simlulateds the year 2015: range(2015, 2016)
    # ------------------- DUMMY END



    # Model calculations outside main function
    # ----------------------------------------
    path_main = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Load and generate general data
    base_data = dl.load_data(path_main, data_external)

    # Load assumptions
    base_data['assumptions'] = assumpt.load_assumptions(base_data, data_external)

    # Change temperature data according to simple assumptions about climate change
    base_data['temperature_data'] = mf.change_temp_data_climate_change(base_data, data_external)

    # Calculate sigmoid diffusion curves based on assumptions about fuel switches
    base_data['assumptions'] = mf.generate_sig_diffusion(base_data, data_external)

    # Disaggregate national data into regional data #TODO
    base_data = nd.disaggregate_base_demand_for_reg(base_data, 1, data_external)

    # Generate virtual building stock over whole simulatin period
    base_data['dw_stock'] = bg.resid_build_stock(base_data, base_data['assumptions'], data_external)

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
