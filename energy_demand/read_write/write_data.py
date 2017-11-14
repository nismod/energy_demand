"""Functions which are writing data
"""
import os
import logging
import numpy as np
import configparser
from energy_demand.basic import basic_functions
from energy_demand.geography import write_shp
import yaml
from yaml import Loader, Dumper
import collections

def create_shp_results(results_container, paths, lookups, lu_reg):
    """Create csv file and merge with shape

    Arguments
    ---------
    results_container
    paths
    lookups
    lu_reg

    """
    logging.info("... create result shapefiles")

    # Paths
    path_out_shapefile = paths['data_results_shapefiles']

    # Create folder
    basic_functions.create_folder(path_out_shapefile)

    # Generate csv from resultfile
    field_names = []
    csv_results = []

    # ------------------------------------
    # Create shapefile with load factors
    # ------------------------------------

    # Iterate fueltpyes and years and add as attributes
    for fueltype in range(lookups['fueltypes_nr']):
        for year in results_container['load_factors_y'].keys():

            field_names.append('lp_max_y_{}_{}'.format(year, fueltype))
            csv_results.append(
                basic_functions.array_to_dict(
                    results_container['load_factors_y'][year][fueltype], lu_reg))

    write_shp.write_result_shapefile(
        paths['lad_shapefile_2011'],
        os.path.join(path_out_shapefile, 'lp_max_y'),
        field_names,
        csv_results)

    # ------------------------------------
    # Create shapefile with 
    # ------------------------------------

    # ------------------------------------
    # Create shapefile with 
    # ------------------------------------

    # ------------------------------------
    # Create shapefile with 
    # ------------------------------------

    logging.info("... finished generating shapefiles")

def dump(data, file_path):
    """Write plain data to a file as yaml

    Parameters
    ----------
    file_path : str
        The path of the configuration file to write
    data
        Data to write (should be lists, dicts and simple values)
    """
    with open(file_path, 'w') as file_handle:
        return yaml.dump(data, file_handle, Dumper=Dumper, default_flow_style=False)

def write_yaml_param_complete(path_yaml, dict_to_dump):
    """Write all assumption parameters to YAML
    #TODO :ORDER
    """
    list_to_dump_complete = []

    for dict_key, dict_values in dict_to_dump.items():
        try:
            parameter_infos = dict_values['param_infos']

            for paramter_info in parameter_infos:
                dict_to_dump_complete = {} #collections.OrderedDict()
                dict_to_dump_complete['suggested_range'] = paramter_info['suggested_range']
                dict_to_dump_complete['absolute_range'] = paramter_info['absolute_range']
                dict_to_dump_complete['description'] = paramter_info['description']
                dict_to_dump_complete['name'] = paramter_info['name']
                dict_to_dump_complete['default_value'] = paramter_info['default_value']
                dict_to_dump_complete['units'] = paramter_info['units']
                list_to_dump_complete.append(dict_to_dump_complete)
        except:
            pass #not correctly formated assumption

    # Dump list
    dump(list_to_dump_complete, path_yaml)
    return

def write_yaml_param(path_yaml, dict_to_dump):
    """Write all assumption parameters to YAML

    """
    with open(path_yaml, 'w') as file_handle:
        yaml.dump(dict_to_dump, file_handle)
    return

def write_simulation_inifile(path, sim_param, enduses, assumptions, reg_nrs, lu_reg):
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

    config.add_section('REGIONS')
    config['REGIONS']['lu_reg'] = str(lu_reg)

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
