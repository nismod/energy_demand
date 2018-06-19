"""Functions which are writing data
"""
import os
import logging
import configparser
import csv
import yaml
import numpy as np
from energy_demand.basic import basic_functions
from energy_demand.geography import write_shp
from energy_demand.technologies import tech_related
from energy_demand.basic import conversions

class ExplicitDumper(yaml.Dumper):
    """
    A dumper that will never emit aliases.
    """
    def ignore_aliases(self, data):
        return True

def logg_info(modelrun, fuels_in, data):
    """Logg information
    """
    logging.info("================================================")
    logging.info("Simulation year:         %s", str(modelrun.curr_yr))
    logging.info("Nr of regions:           %s", str(data['reg_nrs']))
    logging.info("Total ktoe:              %s", str(conversions.gwh_to_ktoe(fuels_in["fuel_in"])))
    logging.info("-----------------")
    logging.info("[GWh] Total input:       %s", str(fuels_in["fuel_in"]))
    logging.info("[GWh] Total output:      %s", str(np.sum(modelrun.ed_fueltype_national_yh)))
    logging.info("[GWh] Total difference:  %s", str(round((np.sum(modelrun.ed_fueltype_national_yh) - fuels_in["fuel_in"]), 4)))
    logging.info("-----------")
    logging.info("[GWh] oil input:         %s", str(fuels_in["fuel_in_oil"]))
    logging.info("[GWh] oil output:        %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']])))
    logging.info("[GWh] oil diff:          %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']]) - fuels_in["fuel_in_oil"], 4)))
    logging.info("-----------")
    logging.info("[GWh] biomass output:    %s", str(fuels_in["fuel_in_biomass"]))
    logging.info("[GWh] biomass output:    %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']])))
    logging.info("[GWh] biomass diff:      %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']]) - fuels_in["fuel_in_biomass"], 4)))
    logging.info("-----------")
    logging.info("[GWh] solid_fuel output: %s", str(fuels_in["fuel_in_solid_fuel"]))
    logging.info("[GWh] solid_fuel output: %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']])))
    logging.info("[GWh] solid_fuel diff:   %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']]) - fuels_in["fuel_in_solid_fuel"], 4)))
    logging.info("-----------")
    logging.info("[GWh] elec output:       %s", str(fuels_in["fuel_in_elec"]))
    logging.info("[GWh] elec output:       %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']])))
    logging.info("[GWh] ele fuel diff:     %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']]) - fuels_in["fuel_in_elec"], 4)))
    logging.info("-----------")
    logging.info("[GWh] gas output:        %s", str(fuels_in["fuel_in_gas"]))
    logging.info("[GWh] gas output:        %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']])))
    logging.info("[GWh] gas diff:          %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']]) - fuels_in["fuel_in_gas"], 4)))
    logging.info("-----------")
    logging.info("[GWh] hydro output:      %s", str(fuels_in["fuel_in_hydrogen"]))
    logging.info("[GWh] hydro output:      %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']])))
    logging.info("[GWh] hydro diff:        %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']]) - fuels_in["fuel_in_hydrogen"], 4)))
    logging.info("-----------")
    logging.info("TOTAL HEATING            %s", str(fuels_in["tot_heating"]))
    logging.info("[GWh] heat input:        %s", str(fuels_in["fuel_in_heat"]))
    logging.info("[GWh] heat output:       %s", str(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['heat']])))
    logging.info("[GWh] heat diff:         %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['heat']]) - fuels_in["fuel_in_heat"], 4)))
    logging.info("-----------")
    logging.info("Diff elec p:             %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']])/ fuels_in["fuel_in_elec"]), 4)))
    logging.info("Diff gas p:              %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']])/ fuels_in["fuel_in_gas"]), 4)))
    logging.info("Diff oil p:              %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']])/ fuels_in["fuel_in_oil"]), 4)))
    logging.info("Diff solid_fuel p:       %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']])/ fuels_in["fuel_in_solid_fuel"]), 4)))
    logging.info("Diff hydrogen p:         %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']])/ fuels_in["fuel_in_hydrogen"]), 4)))
    logging.info("Diff biomass p:          %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']])/ fuels_in["fuel_in_biomass"]), 4)))
    logging.info("================================================")

    return

def tuple_representer(dumper, data):
    return dumper.represent_scalar(
        tag=u'tag:yaml.org,2002:str',
        value='({}, {})'.format(data[0], data[1]))

def write_array_to_txt(path_result, array):
    """Write scenario population for a year to txt file
    """
    np.savetxt(path_result, array, delimiter=',')

def write_list_to_txt(path_result, list_out):
    """Write scenario population for a year to txt file
    """
    file = open(path_result, "w")
    for entry in list_out:
        file.write(entry + "\n")

def write_scenaric_population_data(sim_yr, path_result, pop_y):
    """Write scenario population for a year to '.npy' file

    Parameters
    ----------
    sim_yr : int
        Simulation year
    path_result : str
        Path to resulting folder
    pop_y : array
        Population of simulation year
    """
    path_file = os.path.join(
        path_result,
        "pop__{}__{}".format(sim_yr, ".npy"))

    np.save(path_file, pop_y)
    logging.info("... finished saving population")

def create_shp_results(data, results_container, paths, lookups, regions):
    """Create csv file and merge with shape

    Arguments
    ---------
    results_container : dict
        Data container
    paths : dict
        Paths
    lookups : dict
        Lookups
    regions : list
        Region in a list with order how they are stored in result array
    """
    logging.info("... create result shapefiles")

    # ------------------------------------
    # Create shapefile with load factors
    # ------------------------------------
    field_names, csv_results = [], []
    # Iterate fueltpyes and years and add as attributes
    for year in results_container['reg_load_factor_y'].keys():
        for fueltype in range(lookups['fueltypes_nr']):

            results = basic_functions.array_to_dict(
                results_container['reg_load_factor_y'][year][fueltype], regions)

            field_names.append('y_{}_{}'.format(year, fueltype))
            csv_results.append(results)

        # Add population
        field_names.append('pop_{}'.format(year))

        pop_dict = basic_functions.array_to_dict(
            data['scenario_data']['population'][year], regions)

        csv_results.append(pop_dict)

    write_shp.write_result_shapefile(
        paths['lad_shapefile'],
        os.path.join(paths['data_results_shapefiles'], 'lf_max_y'),
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
            yearly_sum_gw = yearly_sum

            field_names.append('y_{}_{}'.format(year, fueltype))
            csv_results.append(
                basic_functions.array_to_dict(yearly_sum_gw, regions))

        # Add population
        field_names.append('pop_{}'.format(year))
        csv_results.append(
            basic_functions.array_to_dict(data['scenario_data']['population'][year], regions))

    write_shp.write_result_shapefile(
        paths['lad_shapefile'],
        os.path.join(paths['data_results_shapefiles'], 'fuel_y'),
        field_names,
        csv_results)

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
    yaml.add_representer(tuple, tuple_representer)
    with open(file_path, 'w') as file_handle:
        return yaml.dump(data, file_handle, Dumper=ExplicitDumper, default_flow_style=False)

def write_yaml_output_keynames(path_yaml, key_names):
    """Generate YAML file where the outputs
    for the sector model can be easily copied

    Arguments
    ----------
    path_yaml : str
        Path where yaml file is saved
    key_names : dict
        Names of keys of supply_out dict
    """
    list_to_dump = []

    for key_name in key_names:
        dict_to_dump = {
            'name': key_name,
            'spatial_resolution': 'lad_uk_2016',
            'temporal_resolution': 'hourly',
            'units': 'GWh'}

        list_to_dump.append(dict_to_dump)

    dump(list_to_dump, path_yaml)

def write_yaml_param_scenario(path_yaml, dict_to_dump):
    """Write all strategy variables to YAML file

    Arguments
    ----------
    path_yaml : str
        Path where yaml file is saved
    dict_to_dump : dict
        Dict which is written to YAML
    """
    list_to_dump = [dict_to_dump]
    dump(list_to_dump, path_yaml)

def write_yaml_param_complete(path_yaml, dict_to_dump):
    """Write all strategy variables to YAML file

    Arguments
    ----------
    path_yaml : str
        Path where yaml file is saved
    dict_to_dump : dict
        Dict which is written to YAML
    """
    list_to_dump = []

    for paramter_info in dict_to_dump:
        dump_dict = {}
        dump_dict['suggested_range'] = paramter_info['suggested_range']
        dump_dict['absolute_range'] = paramter_info['absolute_range']
        dump_dict['description'] = paramter_info['description']
        dump_dict['name'] = paramter_info['name']
        dump_dict['default_value'] = paramter_info['default_value']
        dump_dict['units'] = paramter_info['units']

        list_to_dump.append(dump_dict)

    # Dump list
    dump(list_to_dump, path_yaml)

def write_simulation_inifile(path, data):
    """Create .ini file with simulation parameters which ared
    used to read in correctly the simulation results

    Arguments
    ---------
    data : dict
        Data container
    """
    path_ini_file = os.path.join(
        path, 'model_run_sim_param.ini')

    config = configparser.ConfigParser()

    config.add_section('SIM_PARAM')
    config['SIM_PARAM']['reg_nrs'] = str(data['reg_nrs'])
    config['SIM_PARAM']['base_yr'] = str(data['assumptions'].base_yr)
    config['SIM_PARAM']['simulated_yrs'] = str(data['assumptions'].simulated_yrs)

    # ----------------------------
    # Other information to pass to plotting and summing function
    # ----------------------------
    config.add_section('ENDUSES')

    #convert list to strings
    config['ENDUSES']['rs_enduses'] = str(data['enduses']['rs_enduses'])
    config['ENDUSES']['ss_enduses'] = str(data['enduses']['ss_enduses'])
    config['ENDUSES']['is_enduses'] = str(data['enduses']['is_enduses'])

    config.add_section('REGIONS')
    config['REGIONS']['regions'] = str(data['regions'])

    with open(path_ini_file, 'w') as write_info:
        config.write(write_info)

def resilience_paper(
        path_result_folder,
        new_folder,
        file_name,
        results,
        submodels,
        regions,
        fueltypes,
        fueltype_str
    ):
    """Restuls for risk paper

    results : array 
        results_unconstrained (3, 391, 7, 365, 24)
    Get maximum and minimum h electricity for eversy submodel
    for base year
    """
    path_result_sub_folder = os.path.join(
        path_result_folder, new_folder)

    basic_functions.create_folder(path_result_sub_folder)

    # Create file path
    path_to_txt = os.path.join(
        path_result_sub_folder,
        "{}{}".format(file_name,".csv"))

    # Write csv
    file = open(path_to_txt, "w")

    file.write("{}, {}, {}".format(
        'lad_nr',
         #'submodel',
        'min_GW_elec',
        'max_GW_elec') + '\n')
        #'resid_min_GW_elec',
        #'resid_max_GW_elec',
        #'servi_min_GW_elec',
        #'servi_max_GW_elec',
        #'indus_min_GW_elec',
        #'indus_max_GW_elec') + '\n')

    fueltype_int = tech_related.get_fueltype_int(
        fueltypes, fueltype_str)

    for region_nr, region in enumerate(regions):

        min_GW_elec = 0
        max_GW_elec = 0

        for submodel_nr, submodel in enumerate(submodels):

            # Reshape
            reshape_8760h = results[submodel_nr][region_nr][fueltype_int].reshape(8760)

            min_GW_elec += np.min(reshape_8760h)
            max_GW_elec += np.max(reshape_8760h)

            # Min and max
            '''if submodel_nr == 0:
                resid_min_GW_elec = np.min(reshape_8760h)
                resid_max_GW_elec = np.max(reshape_8760h)
            elif submodel_nr == 1:
                service_min_GW_elec = np.min(reshape_8760h)
                service_max_GW_elec = np.max(reshape_8760h)
            else:
                industry_min_GW_elec = np.min(reshape_8760h)
                industry_max_GW_elec = np.max(reshape_8760h)'''
            
        file.write("{}, {}, {}".format(
            str.strip(region),
            float(min_GW_elec),
            float(max_GW_elec)) + '\n')

        '''file.write("{}, {}, {}, {}, {}, {}, {}".format(
            str.strip(region),
            float(resid_min_GW_elec),
            float(resid_max_GW_elec),
            float(service_min_GW_elec),
            float(service_max_GW_elec),
            float(industry_min_GW_elec),
            float(industry_max_GW_elec)
            ) + '\n')'''

    file.close()

    # ----------------------
    # Write out national average
    # ----------------------
    # Create file  path
    path_to_txt_flat = os.path.join(
        path_result_sub_folder,
        "{}{}".format(
            'averge_nr',
            ".csv"))

    file = open(path_to_txt_flat, "w")
    file.write("{}".format(
        'average_GW_UK') + '\n')

    uk_av_gw_elec = 0
    for submodel_nr, submodel in enumerate(submodels):
        for region_nr, region in enumerate(regions):
            reshape_8760h = results[submodel_nr][region_nr][fueltype_int].reshape(8760)
            uk_av_gw_elec += np.average(reshape_8760h)

    file.write("{}".format(uk_av_gw_elec))
    file.close()
    print("Finished writing out resilience .csv")
    return

def write_lf(
        path_result_folder,
        path_new_folder,
        parameters,
        model_results,
        file_name
    ):
    """Write numpy array to `.npy` file

    path_result_folder,
    path_new_folder,
    parameters,
    model_results,
    file_name
    """
    # Create folder and subolder
    basic_functions.create_folder(
        path_result_folder)

    path_result_sub_folder = os.path.join(
        path_result_folder, path_new_folder)

    basic_functions.create_folder(path_result_sub_folder)

    # Create full file_name
    for name_param in parameters:
        file_name += str("__") + str(name_param)

    # Generate full path
    path_file = os.path.join(path_result_sub_folder, file_name)

    path_file_fueltype = path_file + "__" + ".npy"

    np.save(path_file_fueltype, model_results)

def write_supply_results(
        sim_yr,
        name_new_folder,
        path_result,
        model_results,
        file_name
    ):
    """Write model results to numpy file as follows:

        name of file: name_year
        array in file:  np.array(region, fueltype, timesteps)

    Arguments
    ---------
    sim_yr : int
        Simulation year
    name_new_folder : str
        Name of folder to create
    path_result : str
        Paths
    model_results : array
        Results to store to txt
    file_name : str
        File name
    """
    # Create folder and subolder
    path_result_sub_folder = os.path.join(
        path_result, name_new_folder)

    basic_functions.create_folder(
        path_result_sub_folder)

    path_file = os.path.join(
        path_result_sub_folder,
        "{}__{}__{}".format(
            file_name,
            sim_yr,
            ".npy"))

    np.save(path_file, model_results)

def write_enduse_specific(sim_yr, path_result, model_results, filename):
    """Write out enduse specific results for every hour and store to
    `.npy` file

    Arguments
    -----------
    sim_yr : int
        Simulation year
    path_result : str
        Path
    model_results : dict
        Modelling results
    filename : str
        File name
    """
    # Create folder for model simulation year
    basic_functions.create_folder(path_result)

    basic_functions.create_folder(
        path_result, "enduse_specific_results")

    for enduse, fuel in model_results.items():

        path_file = os.path.join(
            os.path.join(path_result, "enduse_specific_results"),
            "{}__{}__{}__{}".format(
                filename,
                enduse,
                sim_yr,
                ".npy"))

        np.save(path_file, fuel)

def write_max_results(sim_yr, path_result, result_foldername, model_results, filename):
    """Store yearly model resuls to numpy array '.npy'

    Arguments
    ---------
    sim_yr : int
        Simulation year
    path_result : str
        Result path
    result_foldername : str
        Folder name
    model_results : np.array
        Model results
    filename : str
        File name

    """
    # Create folder and subolder
    basic_functions.create_folder(path_result)
    basic_functions.create_folder(path_result, result_foldername)

    # Write to txt
    path_file = os.path.join(
        os.path.join(path_result, result_foldername),
        "{}__{}__{}".format(filename, sim_yr, ".npy"))

    np.save(path_file, model_results)

    return

def create_txt_shapes(
        end_use,
        path_txt_shapes,
        shape_peak_dh,
        shape_non_peak_y_dh,
        shape_non_peak_yd
    ):
    """Function collecting functions to write out arrays
    to txt files
    """
    write_array_to_txt(
        os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_peak_dh') + str('.txt')),
        shape_peak_dh)

    write_array_to_txt(
        os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_non_peak_y_dh') + str('.txt')),
        shape_non_peak_y_dh)

    write_array_to_txt(
        os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')),
        shape_non_peak_yd)

    return

def create_csv_file(path, rows):
    """
    #filewriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
    """
    with open(path, 'w', newline='') as csvfile:

        filewriter = csv.writer(
            csvfile,
            delimiter=',',
            quotechar='|')

        for row in rows:
            filewriter.writerow(row)
