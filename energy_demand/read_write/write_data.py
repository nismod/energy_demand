"""Functions which are writing data
"""
import logging
import json
import yaml
import numpy as np
import os
from energy_demand.basic import basic_functions

def read_txt_shape_peak_dh(file_path):
    """Read to txt. Array with shape: (24,)
    """
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    out_dict = np.array(read_dict_list, dtype=float)

    return out_dict

def read_txt_shape_non_peak_yh(file_path):
    """Read to txt. Array with shape: (model_yeardays_nrs, 24)
    """
    out_dict = np.zeros((365, 24), dtype=float)
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(list(row.values()), dtype=float)
    return out_dict

def read_txt_shape_peak_yd_factor(file_path):
    """Read to txt. Array with shape: (model_yeardays_nrs, 24)
    """
    out_dict = json.load(open(file_path))
    return out_dict

def read_txt_shape_non_peak_yd(file_path):
    """Read to txt. Array with shape
    """
    out_dict = np.zeros((365))
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(row, dtype=float)
    return out_dict

def write_YAML(crit_write, path_YAML, yaml_list):
    """Creates a YAML file with the timesteps IDs

    https://en.wikipedia.org/wiki/ISO_8601#Duration

    Arguments
    ----------
    crit_write : int
        Whether a yaml file should be written or not (1 or 0)
    path_YAML : str
        Path to write out YAML file
    yaml_list : list
        List containing YAML dictionaries for every region
    """
    if crit_write:
        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)

    return

def write_out_txt(path_to_txt, enduses_service):
    """Generate a txt file with base year service for each technology according to provided fuel split input
    """
    file = open(path_to_txt, "w")

    file.write("---------------------------------------------------------------" + '\n')
    file.write("Base year energy service (as share of total per enduse)" + '\n')
    file.write("---------------------------------------------------------------" + '\n')

    for enduse in enduses_service:
        file.write(" " + '\n')
        file.write("Enduse  "+ str(enduse) + '\n')
        file.write("----------" + '\n')

        for tech in enduses_service[enduse]:
            file.write(str(tech) + str("\t") + str("\t") + str("\t") + str(enduses_service[enduse][tech]) + '\n')

    file.close()
    return

def write_out_temp_assumptions(path_to_txt, temp_assumptions):
    """ # Write out assumptions
    """
    file = open(path_to_txt, "w")

    file.write("{}, {}".format(
        'month', 'temp_change_ey') + '\n'
              )
    for month, temp_change_ey in enumerate(temp_assumptions):
        file.write("{}, {}".format(
        month, temp_change_ey) + '\n'
                  )
    file.close()

    return

def write_out_sim_param(path_to_txt, temp_assumptions):
    """Write sim_param dictionary to csv
    """
    file = open(path_to_txt, "w")

    file.write("{}, {}".format(
        'month', 'temp_change_ey') + '\n'
              )
    for data in temp_assumptions:
        data_entry = data

        if str(data_entry) == 'list_dates':
            file.write("{}, {}".format(data_entry, 'None') + '\n')
        else:
            data_entry2 = str(temp_assumptions[data])
            file.write("{}, {}".format(data_entry, data_entry2) + '\n')
    file.close()

    return

def write_model_result_to_txt(sim_yr, path_result, model_results):
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
            "modelruns__{}__{}__{}".format(sim_yr, fueltype_nr, ".txt")
            )
        np.savetxt(path_file, fuel, delimiter=',')

    # Read in with loadtxt
    return

def write_model_result_to_txt_enduse(sim_yr, path_result, model_results):
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
                "modelruns__{}__{}__{}__{}".format(enduse, sim_yr, fueltype_nr, ".txt")
                )
            np.savetxt(path_file, fuel_fueltype, delimiter=',')

    # Read in with loadtxt
    return

def write_model_result_to_txt_maxresults(sim_yr, path_result, model_results):
    """Store yearly model resul to txt

    Store numpy array to txt
    """
    # Create folder and subolder
    basic_functions.create_folder(path_result)
    basic_functions.create_folder(path_result, "tot_fuel_max")

    # Write to txt
    path_file = os.path.join(
        os.path.join(path_result, "tot_fuel_max"),
        "peakfuels__{}__{}".format(sim_yr, ".txt")
        )
    np.savetxt(path_file, model_results, delimiter=',')

    return
