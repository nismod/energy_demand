'''Main file containing the energy demand model main function
#
# Description: Energy Demand Model - Run one year
# Authors: Sven Eggimann, ... Aurthors: Pranab Baruah; Scott Thacker
#
# Abbreviations:
# -------------
# rs = Residential Sector
# ss = service Sector
# ts = transportation Sector #TODO
#
# bd = Base demand
# by = Base year
# cy = Current year
# dw = dwelling
# p  = Percent
# e  = electricitiy
# g  = gas
# lu = look up
# h = hour
# hp = heat pump
# tech = technology
# temp = temperature
# d = day
# y = year
# yearday = Day in a year ranging from 0 to 364

# Shapes
# ------
# yd = for every year the day
# yh = for every hour in a year
# dh = every hour in day

# y = for total year
# y_dh = for every day in a year, the dh is provided


Down the line
- data centres (ICT about %, 3/4 end-use devices, network and data centres 1/4 NIC 2017)

The docs can be found here: http://ed.readthedocs.io
'''
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

#!python3.6
import os
import sys
import random
import numpy as np
import energy_demand.main_functions as mf
import energy_demand.building_stock_generator as bg
import energy_demand.assumptions as assumpt
import energy_demand.technological_stock as ts
import energy_demand.plot_functions as pf
import energy_demand.national_dissaggregation as nd
import energy_demand.data_loader as dl

import energy_demand.residential_model as rm # Import sub modules
import energy_demand.service_model as sm # Import sub modules
import energy_demand.industry_model as im # Import sub modules
import energy_demand.transport_model as tm # Import sub modules




print("Start Energy Demand Model with python version: " + str(sys.version))

def energy_demand_model(data):
    """Main function of energy demand model to calculate yearly demand

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally

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
    resid_object_country = rm.residential_model_main_function(data)

    # Convert to dict for energy_supply_model
    result_dict = mf.convert_out_format_es(data, resid_object_country, data['ss_all_enduses'])

    # --------------------------
    # Service Model
    # --------------------------
    #service_object_country = sm.service_model_main_function(data)

    # --------------------------
    # Industry Model
    # --------------------------
    #industry_object_country = im.service_model_main_function(data)

    # --------------------------
    # Transportation Model
    # --------------------------

    # --- Write to csv and YAML
    # mf.write_final_result(data, result_dict, data['lu_reg'], False)

    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL timesteps*regions: " + str(len(result_dict['electricity'])))
    print("Finished energy demand model")

    # Plot Region 0 for half a year
    #pf.plot_x_days(result_dict[2], 0, 2)

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
    ey = 2020 #includes this year
    sim_years = range(by, ey + 1)

    # dummy coordinates
    coord_dummy = {}
    coord_dummy['Wales'] = {'longitude': 52.289288, 'latitude': -3.610933}
    coord_dummy['Scotland'] = {'longitude': 56.483100, 'latitude': -4.027093}
    coord_dummy['England'] = {'longitude': 52.874205, 'latitude': -0.871205}

    pop_dummy = {}

    '''ff = range(100, 102)

    a = {}
    for i in ff:
        a[str(i)] = i * 1000
        coord_dummy[str(i)] = {'longitude': 52.289288, 'latitude': -3.610933}
    print(a)
    '''
    a = {'Wales': 3000000} #, 'Scotland': 5300000, 'England': 5300000}

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
    # DUMMY DATA GENERATION----------------------


    # Reg Floor Area? Reg lookup?
    data_external = {
        'population': pop_dummy,
        'region_coordinates': coord_dummy,
        'glob_var' : {},
        'fuel_price': fuel_price_dummy,

        # Demand of other sectors
        'external_enduses_resid': {
            #'waste_water': {0: 0},  # Yearly fuel data
            #'ICT_model': {}
        }
    }
    data_external['end_yr'] = ey
    data_external['sim_period'] = range(by, ey + 1, 1) # Alywas including last simulation year
    data_external['base_yr'] = by
    # ------------------- DUMMY END


    # ----------------------------------------
    # Model calculations outside main function
    # ----------------------------------------
    base_data = {}

    # Copy external data into data container
    for dataset_name, external_data in data_external.items():
        base_data[str(dataset_name)] = external_data

    path_main = os.path.join(os.path.dirname(__file__), '..', 'data') # Main path

    # Path to local files (#Z:\01-Data_NISMOD\data_energy_demand\)
    #base_data['local_data_path'] = r'C:\01-Private\99-Dropbox\Dropbox\00-Office_oxford\07-Data'
    base_data['local_data_path'] = r'Z:\01-Data_NISMOD\data_energy_demand'

    # Load and generate general data
    base_data = dl.load_data(path_main, base_data)

    # Load assumptions
    base_data['assumptions'] = assumpt.load_assumptions(base_data)

    # Change temperature data according to simple assumptions about climate change
    base_data['temperature_data'] = mf.change_temp_data_climate_change(base_data)

    # RESIDENTIAL: Convert base year fuel input assumptions to energy service
    base_data['assumptions']['rs_service_tech_by_p'], base_data['assumptions']['rs_service_fueltype_tech_by_p'], base_data['assumptions']['rs_service_fueltype_by_p'] = mf.calc_service_fueltype_tech(
        base_data['assumptions'],
        base_data['lu_fueltype'],
        base_data['assumptions']['rs_fuel_enduse_tech_p_by'],
        base_data['rs_fuel_raw_data_enduses'],
        base_data['assumptions']['technologies']
        )

    # SERVICE Sector:
    fuels_aggregated_across_sectors = mf.ss_summarise_fuel_per_enduse_all_sectors(base_data['ss_fuel_raw_data_enduses'], base_data['ss_all_enduses'], base_data['nr_of_fueltypes'])

    # Calculate sigmoid for service sector
    base_data['assumptions']['ss_service_tech_by_p'], base_data['assumptions']['ss_service_fueltype_tech_by_p'], base_data['assumptions']['ss_service_fueltype_by_p'] = mf.calc_service_fueltype_tech(
        base_data['assumptions'],
        base_data['lu_fueltype'],
        base_data['assumptions']['ss_fuel_enduse_tech_p_by'],
        fuels_aggregated_across_sectors,
        base_data['assumptions']['technologies']
        )

    # Write out txt file with service shares for each technology per enduse
    mf.write_out_txt(base_data['path_dict']['path_txt_service_tech_by_p'], base_data['assumptions']['rs_service_tech_by_p'])
    print("... a file has been generated which shows the shares of each technology per enduse")

    # Calculate technologies with more, less and constant service based on service switch assumptions
    base_data['assumptions']['rs_tech_increased_service'], base_data['assumptions']['rs_tech_decreased_share'], base_data['assumptions']['rs_tech_constant_share'] = mf.get_technology_services_scenario(base_data['assumptions']['rs_service_tech_by_p'], base_data['assumptions']['rs_share_service_tech_ey_p'])
    base_data['assumptions']['ss_tech_increased_service'], base_data['assumptions']['ss_tech_decreased_share'], base_data['assumptions']['ss_tech_constant_share'] = mf.get_technology_services_scenario(base_data['assumptions']['ss_service_tech_by_p'], base_data['assumptions']['ss_share_service_tech_ey_p'])


    # Calculate sigmoid diffusion curves based on assumptions about fuel switches

    # Residential
    '''base_data['assumptions']['rs_installed_tech'], base_data['assumptions']['rs_sigm_parameters_tech'] = mf.generate_sig_diffusion(
        base_data,
        base_data['assumptions']['rs_service_switches'],
        base_data['assumptions']['rs_fuel_switches'],
        base_data['rs_all_enduses'],
        base_data['rs_fuel_raw_data_enduses'],
        base_data['assumptions']['rs_tech_increased_service'],
        base_data['assumptions']['rs_share_service_tech_ey_p'],
        base_data['assumptions']['rs_enduse_tech_maxL_by_p'],
        base_data['assumptions']['rs_service_fueltype_by_p'],
        base_data['assumptions']['rs_service_tech_by_p'],
        base_data['assumptions']['rs_fuel_enduse_tech_p_by']
        )
    '''

    # Service
    base_data['assumptions']['ss_installed_tech'], base_data['assumptions']['ss_sigm_parameters_tech'] = mf.generate_sig_diffusion(
        base_data,
        base_data['assumptions']['ss_service_switches'],
        base_data['assumptions']['ss_fuel_switches'],
        base_data['ss_all_enduses'],
        fuels_aggregated_across_sectors, #base_data['ss_fuel_raw_data_enduses'], #TODO: USE AGGREGATED FUEL across all sectors
        base_data['assumptions']['ss_tech_increased_service'],
        base_data['assumptions']['ss_share_service_tech_ey_p'],
        base_data['assumptions']['ss_enduse_tech_maxL_by_p'],
        base_data['assumptions']['ss_service_fueltype_by_p'],
        base_data['assumptions']['ss_service_tech_by_p'],
        base_data['assumptions']['ss_fuel_enduse_tech_p_by']
        )
    
    print("base_data['assumptions']['ss_sigm_parameters_tech']")
    print(base_data['assumptions']['ss_sigm_parameters_tech'])
    #prnt(".")

    # Disaggregate national data into regional data #TODO
    base_data = nd.disaggregate_base_demand_for_reg(base_data, 1)

    # Generate virtual residential building stock over whole simulatin period
    base_data['dw_stock_resid'] = bg.resid_build_stock(base_data)

    # Generate virtual service building stock
    #base_data['dw_stock_service']

    # If several years are run:
    results_every_year = []
    for sim_y in sim_years:
        base_data['curr_yr'] = sim_y
        print("                           ")
        print("-------------------------- ")
        print("SIM RUN:  " + str(sim_y))
        print("-------------------------- ")
        results, resid_object_country = energy_demand_model(base_data)

        results_every_year.append(resid_object_country)


    # ------------------------------
    # Plotting
    # ------------------------------
    # Plot load factors
    ##pf.plot_load_curves_fueltype(results_every_year, base_data)

    # Plot results for every year
    pf.plot_stacked_Country_end_use(results_every_year, base_data['rs_all_enduses'], 'rs_tot_country_fuel_enduse_specific_h')
    pf.plot_stacked_Country_end_use(results_every_year, base_data['ss_all_enduses'], 'ss_tot_country_fuel_enduse_specific_h')

    # Plot total fuel (y) per fueltype
    pf.plot_fuels_tot_all_enduses(results_every_year, base_data)

    # Plot peak demand (h) for every fueltype
    pf.plot_rs_fuels_peak_hour(results_every_year, base_data)

    # Plot a full week
    pf.plot_fuels_tot_all_enduses_week(results_every_year, base_data)

    # Run main function
    #results = energy_demand_model(base_data)

    print("Finished running Energy Demand Model")

    #-----------
    # Profiler
    #-----------
    """
    import cProfile
    import pstats
    cProfile.run('energy_demand_model(base_data)')

    stats = pstats.Stats('c://Users//cenv0553//GIT//data//model_output//resid_service_tech_by_p.txt')
    #base_data['path_dict']['path_out_stats_cProfile']

    stats.strip_dirs()
    stats.sort_stats(-1)
    stats.print_stats()

    # -------------
    # PyCallGraph
    # -------------

    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput

    print("Run profiler....")
    #with PyCallGraph(output=GraphvizOutput()):

    graphviz = GraphvizOutput()
    graphviz.output_file = r'C:\\Users\\cenv0553\\GIT\\data\\model_output\\basic.png'

    with PyCallGraph(output=graphviz):
        energy_demand_model(base_data)
    """
