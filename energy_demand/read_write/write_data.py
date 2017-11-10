"""Functions which are writing data
"""
import os
import numpy as np
import configparser
from energy_demand.basic import basic_functions

def write_simulation_inifile(path, sim_param, enduses, assumptions, reg_nrs):
    """Write .ini file with simulation parameters

    Arguments
    ---------
    path : str
        Path to result foder
    sim_param : dict
        Contains all information necessary to plot results
    """
    path_ini_file = os.path.join(path, 'model_run_sim_param.ini')

    config = configparser.ConfigParser()

    config.add_section('SIM_PARAM') 
    config['SIM_PARAM']['reg_nrs'] = str(reg_nrs)
    config['SIM_PARAM']['base_yr'] = str(sim_param['base_yr'])

    config['SIM_PARAM']['simulated_yrs'] = str(sim_param['simulated_yrs'])

    config['SIM_PARAM']['model_yearhours_nrs'] = str(assumptions['model_yearhours_nrs'])
    config['SIM_PARAM']['model_yeardays_nrs'] = str(assumptions['model_yeardays_nrs'])

    # ----------------------------
    # Other information to pass to plotting and summing function
    # ----------------------------
    config.add_section('ENDUSES')
    config['ENDUSES']['rs_all_enduses'] = str(enduses['rs_all_enduses']) #convert list to string
    config['ENDUSES']['ss_all_enduses'] = str(enduses['ss_all_enduses'])
    config['ENDUSES']['is_all_enduses'] = str(enduses['is_all_enduses'])




    with open(path_ini_file, 'w') as f:
        config.write(f)

    return

def write_lf(path_result_folder, path_new_folder, parameters, model_results, file_name):
    """Write numpy array to txt file

    """
    # Create folder and subolder
    basic_functions.create_folder(path_result_folder)
    path_result_sub_folder = os.path.join(path_result_folder, path_new_folder)
    basic_functions.create_folder(path_result_sub_folder)

    # Create full file_name
    for name_param in parameters:
        file_name += str("__") + str(name_param)

    # Generate full path
    path_file = os.path.join(path_result_sub_folder, file_name)

    # Write array to txt (only 2 dimensinal array possible)
    for fueltype_nr, fuel_fueltype in enumerate(model_results):
        path_file_fueltype = path_file + "__" + str(fueltype_nr) + "__" + ".txt"
        np.savetxt(path_file_fueltype, fuel_fueltype, delimiter=',')

    return

def write_supply_results(sim_yr, path_result, model_results, file_name):
    """Store yearly model resul to txt

    Store numpy array to txt

    Fueltype : Regions : Fuel
    """
    # Create folder for model simulation year
    basic_functions.create_folder(path_result)

    # Write to txt
    for fueltype_nr, fuel in enumerate(model_results):
        path_file = os.path.join(
            path_result,
            "{}__{}__{}__{}".format(file_name, sim_yr, fueltype_nr, ".txt"))

        np.savetxt(path_file, fuel, delimiter=',')

    # Read in with loadtxt
    return

def write_enduse_specific(sim_yr, path_result, model_results, filename):
    """Store

    Store numpy array to txt
    """
    # Create folder for model simulation year
    basic_functions.create_folder(path_result)
    basic_functions.create_folder(path_result, "enduse_specific_results")

     # Write to txt
    for enduse, fuel in model_results.items():
        for fueltype_nr, fuel_fueltype in enumerate(fuel):
            path_file = os.path.join(
                os.path.join(path_result, "enduse_specific_results"),
                "{}__{}__{}__{}__{}".format(filename, enduse, sim_yr, fueltype_nr, ".txt"))
            np.savetxt(path_file, fuel_fueltype, delimiter=',')

    return

def write_max_results(sim_yr, path_result, result_foldername, model_results, filename):
    """Store yearly model resuls to txt

    Store numpy array to txt
    """
    # Create folder and subolder
    basic_functions.create_folder(path_result)
    basic_functions.create_folder(path_result, result_foldername)

    # Write to txt
    path_file = os.path.join(
        os.path.join(path_result, result_foldername),
        "{}__{}__{}".format(filename, sim_yr, ".txt"))
    np.savetxt(path_file, model_results, delimiter=',')

    return
