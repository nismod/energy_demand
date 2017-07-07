"""Functions which are writing data
"""
import os
import unittest
import csv
import json
import yaml
import numpy as np
ASSERTIONS = unittest.TestCase('__init__')
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def create_txt_shapes(end_use, path_txt_shapes, shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd):
    """Function collecting functions to write out txt files"""
    jason_to_txt_shape_peak_dh(shape_peak_dh, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt')))
    jason_to_txt_shape_non_peak_dh(shape_non_peak_dh, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_non_peak_dh') + str('.txt')))
    jason_to_txt_shape_peak_yd_factor(shape_peak_yd_factor, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
    jason_to_txt_shape_non_peak_yd(shape_non_peak_yd, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')))

    return

def jason_to_txt_shape_peak_dh(input_array, outfile_path):
    """Wrte to txt. Array with shape: (24,)
    """
    np_dict = dict(enumerate(input_array))
    with open(outfile_path, 'w') as outfile:
        json.dump(np_dict, outfile)

def jason_to_txt_shape_non_peak_dh(input_array, outfile_path):
    """Wrte to txt. Array with shape: (365, 24)
    """
    out_dict = {}
    for k, row in enumerate(input_array):
        out_dict[k] = dict(enumerate(row))
    with open(outfile_path, 'w') as outfile:
        json.dump(out_dict, outfile)

def jason_to_txt_shape_peak_yd_factor(input_array, outfile_path):
    """Wrte to txt. Array with shape: ()
    """
    with open(outfile_path, 'w') as outfile:
        json.dump(input_array, outfile)

def jason_to_txt_shape_non_peak_yd(input_array, outfile_path):
    """Wrte to txt. Array with shape: (365)"""
    out_dict = {}
    for k, row in enumerate(input_array):
        out_dict[k] = row
    with open(outfile_path, 'w') as outfile:
        json.dump(out_dict, outfile)

def read_txt_shape_peak_dh(file_path):
    """Read to txt. Array with shape: (24,)
    """
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    out_dict = np.array(read_dict_list, dtype=float)
    return out_dict

def read_txt_shape_non_peak_yh(file_path):
    """Read to txt. Array with shape: (365, 24)"""
    out_dict = np.zeros((365, 24))
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(list(row.values()), dtype=float)
    return out_dict

def read_txt_shape_peak_yd_factor(file_path):
    """Read to txt. Array with shape: (365, 24)
    """
    out_dict = json.load(open(file_path))
    return out_dict

def read_txt_shape_non_peak_yd(file_path):
    """Read to txt. Array with shape: (365, 1)
    """
    out_dict = np.zeros((365))
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(row, dtype=float)
    return out_dict

def write_YAML(crit_write, path_YAML, yaml_list):
    """Creates a YAML file with the timesteps IDs

    Parameters
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

def write_final_result(data, result_dict, year, lu_reg, crit_YAML):
    """Write reults for energy supply model

    Parameters
    ----------
    data : dict
        Whether a yaml file should be written or not (1 or 0)
    result_dict : dict
        Dictionary which is stored to txt
    lu_reg : dict
        Look up dict for regions
    crit_YAML : bool
        Criteria if YAML files are generated

    Example
    -------
    The output in the textfile is as follows:

        england, P0H, P1H, 139.42, 123.49
    """
    print("...write data to YAML")
    # Remove data from path_main
    main_path = data['path_dict']['path_main'][:-5]

    for fueltype in data['lu_fueltype'].keys():

        # Path to create csv file
        path = os.path.join(main_path, 'model_output/_fueltype_{}_hourly_results.csv'.format(fueltype))

        with open(path, 'w', newline='') as fp:
            csv_writer = csv.writer(fp, delimiter=',')
            data = []
            yaml_list_fuel_type = []

            # Iterate fueltypes
            for reg, hour_day, obs_value, _ in result_dict[fueltype]:
                hour = int(hour_day.split("_")[0]) * 24 + int(hour_day.split("_")[1])

                start_id = "P{}H".format(hour)
                end_id = "P{}H".format(hour + 1)
                data.append((lu_reg[reg], start_id, end_id, obs_value))
                yaml_list_fuel_type.append({
                    'region': lu_reg[reg],
                    'start': start_id,
                    'end': end_id,
                    'value': float(obs_value),
                    'units': 'CHECK GWH',
                    'year': year
                    }
                )

            csv_writer.writerows(data)

            # Write YAML
            write_YAML(crit_YAML, os.path.join(main_path, 'model_output/YAML_  ----TIMESTEPS_{}.yml'.format(fueltype)), yaml_list_fuel_type)

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
