"""Functions which are writing data
"""
import os
import numpy as np
from energy_demand.basic import basic_functions

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

def write_max_results(sim_yr, path_result, model_results, filename):
    """Store yearly model resul to txt

    Store numpy array to txt
    """
    # Create folder and subolder
    basic_functions.create_folder(path_result)
    basic_functions.create_folder(path_result, "tot_fuel_max")

    # Write to txt
    path_file = os.path.join(
        os.path.join(path_result, "tot_fuel_max"),
        "{}__{}__{}".format(filename, sim_yr, ".txt"))
    np.savetxt(path_file, model_results, delimiter=',')

    return
