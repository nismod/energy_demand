"""
"""
import os
import sys
from datetime import date
from energy_demand.assumptions import assumptions
from energy_demand.read_write import data_loader
from energy_demand.basic import date_handling
import numpy as np
from energy_demand.initalisations import initialisations as init
from energy_demand.technologies import technologies_related
from energy_demand.read_write import read_data
from energy_demand.technologies import diffusion_technologies as diffusion
from energy_demand.technologies import fuel_service_switch
print("... start script {}".format(os.path.basename(__file__)))    

def write_installed_tech(path_to_txt, data):
    """Writ
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}".format(
        'enduse', 'technology') + '\n'
              )

    for enduse, technologies in data.items():
        for technology in technologies:
            file.write("{}, {}".format(
                str.strip(enduse), str.strip(technology) + '\n')
                )

    file.close()

    return

def write_sig_param_tech(path_to_txt, data):
    """Writ
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}, {}".format(
        'enduse', 'technology', 'midpoint', 'steepness', 'l_parameter') + '\n'
              )
    for enduse, technologies in data.items():
        for technology, parameters in technologies.items():
            midpoint = float(parameters['midpoint'])
            steepness = float(parameters['steepness'])
            l_parameter = float(parameters['l_parameter'])

            file.write("{}, {}, {}, {}, {}".format(
                enduse, str.strip(technology), midpoint, steepness, l_parameter) + '\n')

    file.close()

    return

base_data = {}
base_data['sim_param'] = {}
base_data['sim_param']['base_yr'] = 2015
base_data['sim_param']['end_yr'] = 2020
base_data['sim_param']['sim_years_intervall'] = 5 # Make calculation only every X year
base_data['sim_param']['sim_period'] = range(base_data['sim_param']['base_yr'], base_data['sim_param']['end_yr']  + 1, base_data['sim_param']['sim_years_intervall'])
base_data['sim_param']['sim_period_yrs'] = int(base_data['sim_param']['end_yr']  + 1 - base_data['sim_param']['base_yr'])
base_data['sim_param']['curr_yr'] = base_data['sim_param']['base_yr']
base_data['sim_param']['list_dates'] = date_handling.fullyear_dates(
    start=date(base_data['sim_param']['base_yr'], 1, 1),
    end=date(base_data['sim_param']['base_yr'], 12, 31))

# Paths
path_main = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-7])
local_data_path = r'Y:\01-Data_NISMOD\data_energy_demand'

# -----------------------------------------------------
# Load data and assumptions
# ------------------------------------------------------
base_data['path_dict'] = data_loader.load_paths(path_main, local_data_path)
base_data = data_loader.load_data_lookup_data(base_data)
base_data = data_loader.load_fuels(base_data)
base_data['assumptions'] = assumptions.load_assumptions(base_data)

CSV_rs_installed_tech = os.path.join(os.path.dirname(__file__), '..', r'data\data_scripts\rs_installed_tech.csv')
CSV_ss_installed_tech = os.path.join(os.path.dirname(__file__), '..', r'data\data_scripts\ss_installed_tech.csv')
CSV_is_installed_tech = os.path.join(os.path.dirname(__file__), '..', r'data\data_scripts\is_installed_tech.csv')

CSV_rs_sig_param_tech = os.path.join(os.path.dirname(__file__), '..', r'data\data_scripts\rs_sig_param_tech.csv')
CSV_ss_sig_param_tech = os.path.join(os.path.dirname(__file__), '..', r'data\data_scripts\ss_sig_param_tech.csv')
CSV_is_sig_param_tech = os.path.join(os.path.dirname(__file__), '..', r'data\data_scripts\is_sig_param_tech.csv')

if True:
    # Read in Services
    rs_service_tech_by_p = read_data.read_service_data_service_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'rs_service_tech_by_p.csv'))
    ss_service_tech_by_p = read_data.read_service_data_service_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'ss_service_tech_by_p.csv'))
    is_service_tech_by_p = read_data.read_service_data_service_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'is_service_tech_by_p.csv'))

    rs_service_fueltype_by_p = read_data.read_service_fueltype_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'rs_service_fueltype_by_p.csv'))
    ss_service_fueltype_by_p = read_data.read_service_fueltype_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'ss_service_fueltype_by_p.csv'))
    is_service_fueltype_by_p = read_data.read_service_fueltype_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'is_service_fueltype_by_p.csv'))
    
    rs_service_fueltype_tech_by_p = read_data.read_service_fueltype_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'rs_service_fueltype_tech_by_p.csv'))
    ss_service_fueltype_tech_by_p = read_data.read_service_fueltype_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'ss_service_fueltype_tech_by_p.csv'))
    is_service_fueltype_tech_by_p = read_data.read_service_fueltype_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'is_service_fueltype_tech_by_p.csv'))


    # Calculate technologies with more, less and constant service based on service switch assumptions (TWICE CALCULATION)
    base_data['assumptions']['rs_tech_increased_service'], base_data['assumptions']['rs_tech_decreased_share'], base_data['assumptions']['rs_tech_constant_share'] = fuel_service_switch.get_tech_future_service(
        rs_service_tech_by_p,
        base_data['assumptions']['rs_share_service_tech_ey_p'])
    base_data['assumptions']['ss_tech_increased_service'], base_data['assumptions']['ss_tech_decreased_share'], base_data['assumptions']['ss_tech_constant_share'] = fuel_service_switch.get_tech_future_service(
        ss_service_tech_by_p,
        base_data['assumptions']['ss_share_service_tech_ey_p'])
    base_data['assumptions']['is_tech_increased_service'], base_data['assumptions']['is_tech_decreased_share'], base_data['assumptions']['is_tech_constant_share'] = fuel_service_switch.get_tech_future_service(
        is_service_tech_by_p,
        base_data['assumptions']['is_share_service_tech_ey_p'])

    # Calculate sigmoid diffusion curves based on assumptions about fuel switches

    # --Residential
    base_data['assumptions']['rs_installed_tech'], base_data['assumptions']['rs_sig_param_tech'] = diffusion.get_sig_diffusion(
        base_data,
        base_data['assumptions']['rs_service_switches'],
        base_data['assumptions']['rs_fuel_switches'],
        base_data['rs_all_enduses'],
        base_data['assumptions']['rs_tech_increased_service'],
        base_data['assumptions']['rs_share_service_tech_ey_p'],
        base_data['assumptions']['rs_enduse_tech_maxL_by_p'],
        rs_service_fueltype_by_p,
        rs_service_tech_by_p,
        base_data['assumptions']['rs_fuel_tech_p_by']
        )

   # --Service
    base_data['assumptions']['ss_installed_tech'], base_data['assumptions']['ss_sig_param_tech'] = diffusion.get_sig_diffusion(
        base_data,
        base_data['assumptions']['ss_service_switches'],
        base_data['assumptions']['ss_fuel_switches'],
        base_data['ss_all_enduses'],
        base_data['assumptions']['ss_tech_increased_service'],
        base_data['assumptions']['ss_share_service_tech_ey_p'],
        base_data['assumptions']['ss_enduse_tech_maxL_by_p'],
        ss_service_fueltype_by_p,
        ss_service_tech_by_p,
        base_data['assumptions']['ss_fuel_tech_p_by']
        )

    # --Industry
    base_data['assumptions']['is_installed_tech'], base_data['assumptions']['is_sig_param_tech'] = diffusion.get_sig_diffusion(
        base_data,
        base_data['assumptions']['is_service_switches'],
        base_data['assumptions']['is_fuel_switches'],
        base_data['is_all_enduses'],
        base_data['assumptions']['is_tech_increased_service'],
        base_data['assumptions']['is_share_service_tech_ey_p'],
        base_data['assumptions']['is_enduse_tech_maxL_by_p'],
        is_service_fueltype_by_p,
        is_service_tech_by_p,
        base_data['assumptions']['is_fuel_tech_p_by']
        )
    

    write_installed_tech(CSV_rs_installed_tech, base_data['assumptions']['rs_installed_tech'])
    write_installed_tech(CSV_ss_installed_tech, base_data['assumptions']['ss_installed_tech'])
    write_installed_tech(CSV_is_installed_tech, base_data['assumptions']['is_installed_tech'])

    write_sig_param_tech(CSV_rs_sig_param_tech, base_data['assumptions']['rs_sig_param_tech'])
    write_sig_param_tech(CSV_ss_sig_param_tech, base_data['assumptions']['ss_sig_param_tech'])
    write_sig_param_tech(CSV_is_sig_param_tech, base_data['assumptions']['is_sig_param_tech'])

print("... finished script {}".format(os.path.basename(__file__)))
