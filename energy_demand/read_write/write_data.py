"""Functions which are writing data
"""
import os
import logging
import configparser
import csv
import yaml
import numpy as np
from ruamel.yaml import YAML

from energy_demand.basic import lookup_tables, date_prop, basic_functions, conversions
from energy_demand import enduse_func

def write_yaml(data, file_path):
    """Write plain data to a file as yaml

    Parameters
    ----------
    data
        Data to write (should be lists, dicts and simple values)
    file_path : str
        The path of the configuration file to write
    """
    with open(file_path, 'w') as file_handle:
        yaml = YAML(typ='unsafe')
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        return yaml.dump(data, file_handle)

class ExplicitDumper(yaml.Dumper):
    """
    A dumper that will never emit aliases.
    """
    def ignore_aliases(self, data):
        return True

def logg_info(modelrun, fuels_in, data):
    """Logg information
    """
    lookups = lookup_tables.basic_lookups()
    logging.info("=====================================================")
    logging.info("Simulation year:         %s", str(modelrun.curr_yr))
    logging.info("Nr of regions:           %s", str(data['assumptions'].reg_nrs))
    logging.info("Total ktoe:              %s", str(conversions.gwh_to_ktoe(fuels_in["fuel_in"])))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] Total input:       %s", str(fuels_in["fuel_in"]))
    logging.info("[GWh] Total output:      %s", str(np.sum(modelrun.ed_fueltype_national_yh)))
    logging.info("[GWh] Total difference:  %s", str(round((np.sum(modelrun.ed_fueltype_national_yh) - fuels_in["fuel_in"]), 4)))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] oil input:         %s", str(fuels_in["fuel_in_oil"]))
    logging.info("[GWh] oil output:        %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['oil']])))
    logging.info("[GWh] oil diff:          %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['oil']]) - fuels_in["fuel_in_oil"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] biomass output:    %s", str(fuels_in["fuel_in_biomass"]))
    logging.info("[GWh] biomass output:    %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['biomass']])))
    logging.info("[GWh] biomass diff:      %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['biomass']]) - fuels_in["fuel_in_biomass"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] solid_fuel output: %s", str(fuels_in["fuel_in_solid_fuel"]))
    logging.info("[GWh] solid_fuel output: %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['solid_fuel']])))
    logging.info("[GWh] solid_fuel diff:   %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['solid_fuel']]) - fuels_in["fuel_in_solid_fuel"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] elec output:       %s", str(fuels_in["fuel_in_elec"]))
    logging.info("[GWh] elec output:       %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['electricity']])))
    logging.info("[GWh] ele fuel diff:     %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['electricity']]) - fuels_in["fuel_in_elec"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] gas output:        %s", str(fuels_in["fuel_in_gas"]))
    logging.info("[GWh] gas output:        %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['gas']])))
    logging.info("[GWh] gas diff:          %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['gas']]) - fuels_in["fuel_in_gas"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("[GWh] hydro output:      %s", str(fuels_in["fuel_in_hydrogen"]))
    logging.info("[GWh] hydro output:      %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['hydrogen']])))
    logging.info("[GWh] hydro diff:        %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['hydrogen']]) - fuels_in["fuel_in_hydrogen"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("TOTAL HEATING            %s", str(fuels_in["tot_heating"]))
    logging.info("[GWh] heat input:        %s", str(fuels_in["fuel_in_heat"]))
    logging.info("[GWh] heat output:       %s", str(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['heat']])))
    logging.info("[GWh] heat diff:         %s", str(round(np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['heat']]) - fuels_in["fuel_in_heat"], 4)))
    logging.info("-----------------------------------------------------")
    logging.info("Diff elec p:             %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['electricity']])/ fuels_in["fuel_in_elec"]), 4)))
    logging.info("Diff gas p:              %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['gas']])/ fuels_in["fuel_in_gas"]), 4)))
    logging.info("Diff oil p:              %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['oil']])/ fuels_in["fuel_in_oil"]), 4)))
    logging.info("Diff solid_fuel p:       %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['solid_fuel']])/ fuels_in["fuel_in_solid_fuel"]), 4)))
    logging.info("Diff hydrogen p:         %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['hydrogen']])/ fuels_in["fuel_in_hydrogen"]), 4)))
    logging.info("Diff biomass p:          %s", str(round((np.sum(modelrun.ed_fueltype_national_yh[lookups['fueltypes']['biomass']])/ fuels_in["fuel_in_biomass"]), 4)))
    logging.info("=====================================================")

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
    pop_y : array or list
        Population of simulation year
    """
    path_file = os.path.join(
        path_result,
        "pop__{}__{}".format(sim_yr, ".npy"))

    np.save(path_file, pop_y)
    assert type(pop_y) != dict #test that not a dict

    logging.debug("... finished saving population")

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

def write_simulation_inifile(path, data, simulated_regions):
    """Create .ini file with simulation parameters which are
    used to read in correctly the simulation results

    Arguments
    ---------
    paths: str
        Path
    data : dict
        Data container

    simulated_regions : list
        Simulated regions
    """
    path_ini_file = os.path.join(
        path, 'model_run_sim_param.ini')

    config = configparser.ConfigParser()

    config.add_section('SIM_PARAM')
    config['SIM_PARAM']['reg_nrs'] = str(data['assumptions'].reg_nrs)
    config['SIM_PARAM']['base_yr'] = str(data['assumptions'].base_yr)
    config['SIM_PARAM']['sim_yrs'] = str(data['assumptions'].sim_yrs)

    # ----------------------------
    # Other information to pass to plotting and summing function
    # ----------------------------
    config.add_section('ENDUSES')

    #convert list to strings
    config['ENDUSES']['residential'] = str(data['enduses']['residential'])
    config['ENDUSES']['service'] = str(data['enduses']['service'])
    config['ENDUSES']['industry'] = str(data['enduses']['industry'])

    config.add_section('REGIONS')
    config['REGIONS']['regions'] = str(simulated_regions)

    with open(path_ini_file, 'w') as write_info:
        config.write(write_info)

def write_min_max_result_to_txt(file_path, values, yearday, yearday_date):
    """Write min and max values including data information to csv file
    """
    file = open(file_path, "w")
    file.write("Yearday: {}".format(yearday) + '\n')
    file.write("date " + str(yearday_date) + '\n')
    for value in values:
        file.write("{}".format(value) + '\n') #Write list to values
    file.close()

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

    path_file_fueltype = os.path.join(path_result_sub_folder, file_name) + "__" + ".npy"

    np.save(path_file_fueltype, model_results)

def write_only_peak_total_regional(
        sim_yr,
        name_new_folder,
        path_result,
        model_results,
        file_name_annual_sum
        ):
    """Write only total regional demand for a region
    """
    path_result_sub_folder = os.path.join(
        path_result, name_new_folder)

    basic_functions.create_folder(
        path_result_sub_folder)

    path_file_annual_sum = os.path.join(
        path_result_sub_folder,
        "{}__{}__{}".format(file_name_annual_sum, sim_yr, ".npy"))

    # ------------------------------------
    # Sum annual fuel across all fueltypes
    # ------------------------------------
    # Sum across 8760 hours
    ed_fueltype_regs_y = np.sum(model_results, axis=2)
    np.save(path_file_annual_sum, ed_fueltype_regs_y)

def write_only_peak(
        sim_yr,
        name_new_folder,
        path_result,
        model_results,
        file_name_peak_day
    ):
    """Write only peak demand and total regional demand for a region
    """
    path_result_sub_folder = os.path.join(
        path_result, name_new_folder)

    basic_functions.create_folder(
        path_result_sub_folder)

    path_file_peak_day = os.path.join(
        path_result_sub_folder,
        "{}__{}__{}".format(file_name_peak_day, sim_yr, ".npy"))

    # ------------------------------------
    # Write out peak electricity day demands
    # ------------------------------------
    # Get peak day electricity
    lookups = lookup_tables.basic_lookups()
    fueltype_int = lookups['fueltypes']['electricity']

    national_hourly_demand = np.sum(model_results[fueltype_int], axis=0)
    peak_day_electricity, _ = enduse_func.get_peak_day_single_fueltype(national_hourly_demand)
    selected_hours = date_prop.convert_yearday_to_8760h_selection(peak_day_electricity)
    selected_demand = model_results[:, :, selected_hours]

    np.save(path_file_peak_day, selected_demand)

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
    path_result_sub_folder = os.path.join(
        path_result, name_new_folder)

    basic_functions.create_folder(
        path_result_sub_folder)

    path_file = os.path.join(
        path_result_sub_folder,
        "{}__{}__{}".format(file_name, sim_yr, ".npy"))

    np.save(path_file, model_results)

def write_full_results(
        sim_yr,
        path_result,
        full_results,
        filename
    ):
    """Write out enduse specific results for every hour and store to
    `.npy` file

    Arguments
    -----------
    sim_yr : int
        Simulation year
    path_result : str
        Path
    full_results : dict
        Modelling results per submodel, enduse, region, fueltype, 8760h
    filename : str
        File name
    """
    statistics_to_print = ["{}\t \t \t \t{}".format(
        "Enduse", "total_annual_GWh")]

    # Create folder for model simulation year
    basic_functions.create_folder(path_result)

    basic_functions.create_folder(
        path_result, "full_results")

    for sector_nr in full_results:

        for enduse, fuel in full_results[sector_nr].items():

            path_file = os.path.join(
                os.path.join(path_result, "full_results"),
                "{}__{}__{}__{}__{}".format(
                    filename,
                    enduse,
                    sim_yr,
                    sector_nr,
                    ".npy"))

            np.save(path_file, fuel)

            statistics_to_print.append("{}\t\t\t\t{}".format(
                enduse, np.sum(fuel)))

    # Create statistic files with sum of all end uses
    path_file = os.path.join(
        os.path.join(path_result, "full_results"),
        "{}__{}__{}".format("statistics_end_uses", sim_yr, ".txt"))

    write_list_to_txt(
        path_file,
        statistics_to_print)

def write_residential_tot_demands(
        sim_yr,
        path_result,
        tot_fuel_y_enduse_specific_yh,
        filename
    ):
    basic_functions.create_folder(path_result)
    basic_functions.create_folder(path_result, "residential_results")

    path_file = os.path.join(
        os.path.join(path_result, "residential_results"),
        "{}__{}__{}".format(
            filename,
            sim_yr,
            ".npy"))

    np.save(path_file, tot_fuel_y_enduse_specific_yh)

def write_enduse_specific(
        sim_yr,
        path_result,
        tot_fuel_y_enduse_specific_yh,
        filename
    ):
    """Write out enduse specific results for every hour and store to
    `.npy` file

    Arguments
    -----------
    sim_yr : int
        Simulation year
    path_result : str
        Path
    tot_fuel_y_enduse_specific_yh : dict
        Modelling results
    filename : str
        File name
    """
    statistics_to_print = []
    statistics_to_print.append("{}\t \t \t \t{}".format(
        "Enduse", "total_annual_GWh"))

    # Create folder for model simulation year
    basic_functions.create_folder(path_result)

    basic_functions.create_folder(
        path_result, "enduse_specific_results")

    for enduse, fuel in tot_fuel_y_enduse_specific_yh.items():
        logging.info("   ... Enduse specific writing to file: %s  Total demand: %s ", enduse, np.sum(fuel))

        path_file = os.path.join(
            os.path.join(path_result, "enduse_specific_results"),
            "{}__{}__{}__{}".format(
                filename,
                enduse,
                sim_yr,
                ".npy"))

        np.save(path_file, fuel)

        statistics_to_print.append("{}\t\t\t\t{}".format(
            enduse, np.sum(fuel)))

    # Create statistic files with sum of all end uses
    path_file = os.path.join(
        os.path.join(path_result, "enduse_specific_results"),
        "{}__{}__{}".format(
            "statistics_end_uses",
            sim_yr,
            ".txt"))

    write_list_to_txt(
        path_file,
        statistics_to_print)

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

def write_result_txt(path, regions, values):
    """Store values of spatial plot in csv file
    """
    myData = [["region", "value"]]

    for region, value in zip(regions, values):
        myData.append([region, value])

    myFile = open(path, 'w', newline='')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(myData)
