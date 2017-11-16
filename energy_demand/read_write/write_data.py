"""Functions which are writing data
"""
import os
import logging
import numpy as np
import configparser
from energy_demand.basic import basic_functions, conversions
from energy_demand.geography import write_shp
import yaml
from yaml import Loader, Dumper
import collections

def write_pop(sim_yr, path_result, pop_y):
    """Write scenario population for a year
    """
    path_file = os.path.join(
        path_result,
        "model_run_pop", "pop__{}__{}".format(sim_yr, ".txt"))

    np.savetxt(path_file, pop_y, delimiter=',')

    pass

def create_shp_results(data, results_container, paths, lookups, lu_reg):
    """Create csv file and merge with shape

    Arguments
    ---------
    results_container : dict
        Data container
    paths : dict
        Paths
    lookups : dict
        Lookups
    lu_reg : list
        Region in a list with order how they are stored in result array
    """
    logging.info("... create result shapefiles")

    # ------------------------------------
    # Create shapefile with load factors
    # ------------------------------------
    field_names, csv_results = [], []
    # Iterate fueltpyes and years and add as attributes
    for year in results_container['load_factors_y'].keys():
        for fueltype in range(lookups['fueltypes_nr']):
            field_names.append('y_{}_{}'.format(year, fueltype))
            csv_results.append(
                basic_functions.array_to_dict(
                    results_container['load_factors_y'][year][fueltype], lu_reg))

        # Add population
        field_names.append('pop_{}'.format(year))
        csv_results.append(basic_functions.array_to_dict(data['scenario_data']['population'][year], lu_reg))

    write_shp.write_result_shapefile(
        paths['lad_shapefile'],
        os.path.join(paths['data_results_shapefiles'], 'lp_max_y'),
        field_names,
        csv_results)

    # ------------------------------------
    # Create shapefile with yearly total fuel all enduses
    # ------------------------------------
    field_names, csv_results = [], []

    # Iterate fueltpyes and years and add as attributes
    for year in results_container['results_every_year'].keys():
        for fueltype in range(lookups['fueltypes_nr']):

            # Calculate yearly sum
            yearly_sum = np.sum(results_container['results_every_year'][year][fueltype], axis=1)

            # Conversion: Convert gwh per years to gw
            yearly_sum_gw = conversions.gwhperyear_to_gw(yearly_sum)

            field_names.append('y_{}_{}'.format(year, fueltype))
            csv_results.append(
                basic_functions.array_to_dict(yearly_sum_gw, lu_reg))

        # Add population
        field_names.append('pop_{}'.format(year))
        csv_results.append(
            basic_functions.array_to_dict(data['scenario_data']['population'][year], lu_reg))

    write_shp.write_result_shapefile(
        paths['lad_shapefile'],
        os.path.join(paths['data_results_shapefiles'], 'fuel_y'),
        field_names,
        csv_results)

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

    Arguments
    ----------
    path_yaml : str
        Path where yaml file is saved
    dict_to_dump : dict
        Dict which is written to YAML

    Returns
    -------

    #
    #TODO :ORDER
    """
    list_to_dump = []

    for dict_key, dict_values in dict_to_dump.items():
        try:
            parameter_infos = dict_values['param_infos']

            for paramter_info in parameter_infos:
                dump_dict = {} #collections.OrderedDict()
                dump_dict['suggested_range'] = paramter_info['suggested_range']
                dump_dict['absolute_range'] = paramter_info['absolute_range']
                dump_dict['description'] = paramter_info['description']
                dump_dict['name'] = paramter_info['name']
                dump_dict['default_value'] = paramter_info['default_value']
                dump_dict['units'] = paramter_info['units']
                list_to_dump.append(dump_dict)
        except:
            pass #not correctly formated assumption

    # Dump list
    dump(list_to_dump, path_yaml)

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

    pass

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

    pass

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

    pass

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
