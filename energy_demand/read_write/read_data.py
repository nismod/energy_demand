"""Reading raw data
"""
import os
import sys
import csv
import json
import logging
from collections import defaultdict
import yaml
import numpy as np
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_weather_data
from energy_demand.profiles import load_profile

def read_param_yaml(path):
    """Read yaml parameters
    """
    with open(path, 'r') as ymlfile:
        parameter_dict = yaml.load(ymlfile)

    return parameter_dict

def read_in_results(path_runs, lookups, seasons, model_yeardays_daytype):
    """Read and post calculate
    results from txt files
    and store into container
    """
    logging.info("... Reading in results")

    results_container = {}

    # -------------
    # Fuels
    # -------------
    logging.info("... Reading in fuels")

    results_container['results_every_year'] = read_results_yh(
        lookups['fueltypes_nr'], path_runs)

    results_container['results_enduse_every_year'] = read_enduse_specific_results_txt(
        lookups['fueltypes_nr'], path_runs)

    results_container['tot_peak_enduses_fueltype'] = read_max_results(
        os.path.join(path_runs, "result_tot_peak_enduses_fueltype"))

    # -------------
    # Load factors
    # -------------
    logging.info("... Reading in load factors")
    results_container['load_factors_y'] = read_lf_y(
        os.path.join(path_runs, "result_reg_load_factor_y"))
    results_container['load_factors_yh'] = read_lf_y(
        os.path.join(path_runs, "result_reg_load_factor_yd"))

    results_container['load_factor_seasons'] = {}
    results_container['load_factor_seasons']['winter'] = read_lf_y(
        os.path.join(path_runs, "result_reg_load_factor_winter"))
    results_container['load_factor_seasons']['spring'] = read_lf_y(
        os.path.join(path_runs, "result_reg_load_factor_spring"))
    results_container['load_factor_seasons']['summer'] = read_lf_y(
        os.path.join(path_runs, "result_reg_load_factor_summer"))
    results_container['load_factor_seasons']['autumn'] = read_lf_y(
        os.path.join(path_runs, "result_reg_load_factor_autumn"))

    # -------------
    # Post-calculations
    # -------------
    logging.info("... generating post calculations with read results")
    # Calculate average per season and fueltype for every fueltype
    av_season_daytype_cy = {}
    season_daytype_cy = {}
    for year, fueltypes_data in results_container['results_every_year'].items():
        av_season_daytype_cy[year] = {}
        season_daytype_cy[year] = {}

        for fueltype, reg_fuels in fueltypes_data.items():

            # Summarise across regions
            tot_all_reg_fueltype = np.sum(reg_fuels, axis=0)

            tot_all_reg_fueltype_reshape = tot_all_reg_fueltype.reshape((365, 24))

            calc_av, calc_lp = load_profile.calc_av_lp(
                tot_all_reg_fueltype_reshape,
                seasons,
                model_yeardays_daytype)

            av_season_daytype_cy[year][fueltype] = calc_av
            season_daytype_cy[year][fueltype] = calc_lp

    results_container['av_season_daytype_cy'] = av_season_daytype_cy
    results_container['season_daytype_cy'] = season_daytype_cy

    logging.info("... Reading in results finished")
    return results_container

def read_results_yh(fueltypes_nr, path_to_folder):
    """Read results

    Arguments
    ---------
    fueltypes_nr : int
        Number of fueltypes
    reg_nrs : int
        Number of regions
    path_to_folder : str
        Path to folder

    Returns
    -------
    results = dict
        Results
    """
    results = defaultdict(dict)

    all_txt_files_in_folder = os.listdir(path_to_folder)

    # ------------------
    # Get number of regions (search largest fueltype_array_position)
    # ------------------
    reg_nrs = 0
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_to_folder, file_path)
        file_path_split = file_path.split("__")
        try:
            fueltype_array_position = int(file_path_split[2])

            if fueltype_array_position > reg_nrs:
                reg_nrs = fueltype_array_position
        except IndexError:
            pass #path is a folder and not a file

    # Iterate files in folder
    for file_path in all_txt_files_in_folder:
        logging.info("... file_path: " + str(file_path))
        try:
            path_file_to_read = os.path.join(path_to_folder, file_path)
            file_path_split = file_path.split("__")
            year = int(file_path_split[1])
            fueltype_array_position = int(file_path_split[2])
            txt_data = np.loadtxt(path_file_to_read, delimiter=',')

            try:
                results[year]
            except KeyError:
                results[year] = np.zeros((fueltypes_nr, reg_nrs, 8760), dtype=float)

            results[year][fueltype_array_position] = txt_data
        except IndexError:
            pass #path is a folder and not a file

    return results

def read_max_results(path_enduse_specific_results):
    """Read max results

    Arguments
    ---------
    path_to_folder : str
        Path to folder
    """
    results = {}
    all_txt_files_in_folder = os.listdir(path_enduse_specific_results)

    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_enduse_specific_results, file_path)
        file_path_split = file_path.split("__")
        year = int(file_path_split[1])

        txt_data = np.loadtxt(path_file_to_read, delimiter=',')

        # Add year if not already exists
        results[year] = txt_data

    return results

def read_enduse_specific_results_txt(fueltypes_nr, path_to_folder):
    """Read restuls

    Arguments
    ---------
    fueltypes_nr : int
        Number of fueltypes
    path_to_folder : str
        Folder path
    """
    results = {}
    path_enduse_specific_results = os.path.join(path_to_folder, "enduse_specific_results")
    all_txt_files_in_folder = os.listdir(path_enduse_specific_results)

    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_enduse_specific_results, file_path)
        file_path_split = file_path.split("__")
        enduse = file_path_split[1]
        year = int(file_path_split[2])
        fueltype_array_position = int(file_path_split[3])

        txt_data = np.loadtxt(path_file_to_read, delimiter=',')

        # Create year if not existing
        try:
            results[year]
        except KeyError:
            results[year] = {}
        try:
            results[year][enduse]
        except:
            results[year][enduse] = np.zeros((fueltypes_nr, 365, 24), dtype=float)

        # Add year if not already exists
        results[year][enduse][fueltype_array_position] = txt_data

    return results

def load_script_data(data):
    """Load data generated by scripts

    Arguments
    ---------
    data : dict
        Data container
    """
    local_path = data['local_paths']['path_sigmoid_data']
    dir_services_path = data['local_paths']['dir_services']

    # Read in Services (from script data)
    data['assumptions']['rs_service_tech_by_p'] = read_service_tech_by_p(os.path.join(dir_services_path, 'rs_service_tech_by_p.csv'))
    data['assumptions']['ss_service_tech_by_p'] = read_service_tech_by_p(os.path.join(dir_services_path, 'ss_service_tech_by_p.csv'))
    data['assumptions']['is_service_tech_by_p'] = read_service_tech_by_p(os.path.join(dir_services_path, 'is_service_tech_by_p.csv'))
    data['assumptions']['rs_service_fueltype_by_p'] = read_service_fueltype_by_p(os.path.join(dir_services_path, 'rs_service_fueltype_by_p.csv'))
    data['assumptions']['ss_service_fueltype_by_p'] = read_service_fueltype_by_p(os.path.join(dir_services_path, 'ss_service_fueltype_by_p.csv'))
    data['assumptions']['is_service_fueltype_by_p'] = read_service_fueltype_by_p(os.path.join(dir_services_path, 'is_service_fueltype_by_p.csv'))
    data['assumptions']['rs_service_fueltype_tech_by_p'] = read_service_fueltype_tech_by_p(os.path.join(dir_services_path, 'rs_service_fueltype_tech_by_p.csv'))
    data['assumptions']['ss_service_fueltype_tech_by_p'] = read_service_fueltype_tech_by_p(os.path.join(dir_services_path, 'ss_service_fueltype_tech_by_p.csv'))
    data['assumptions']['is_service_fueltype_tech_by_p'] = read_service_fueltype_tech_by_p(os.path.join(dir_services_path, 'is_service_fueltype_tech_by_p.csv'))

    # Read technologies with more, less and constant service based on service switch assumptions (from script data)
    data['assumptions']['rs_tech_increased_service'] = read_installed_tech(os.path.join(local_path, 'rs_tech_increased_service.csv'))
    data['assumptions']['ss_tech_increased_service'] = read_installed_tech(os.path.join(local_path, 'ss_tech_increased_service.csv'))
    data['assumptions']['is_tech_increased_service'] = read_installed_tech(os.path.join(local_path, 'is_tech_increased_service.csv'))

    data['assumptions']['rs_tech_decreased_share'] = read_installed_tech(os.path.join(local_path, 'rs_tech_decreased_share.csv'))
    data['assumptions']['ss_tech_decreased_share'] = read_installed_tech(os.path.join(local_path, 'ss_tech_decreased_share.csv'))
    data['assumptions']['is_tech_decreased_share'] = read_installed_tech(os.path.join(local_path, 'is_tech_decreased_share.csv'))

    data['assumptions']['rs_tech_constant_share'] = read_installed_tech(os.path.join(local_path, 'rs_tech_constant_share.csv'))
    data['assumptions']['ss_tech_constant_share'] = read_installed_tech(os.path.join(local_path, 'ss_tech_constant_share.csv'))
    data['assumptions']['is_tech_constant_share'] = read_installed_tech(os.path.join(local_path, 'is_tech_constant_share.csv'))

    # Read in sigmoid technology diffusion parameters (from script data)
    data['assumptions']['rs_sig_param_tech'] = read_sig_param_tech(os.path.join(local_path, 'rs_sig_param_tech.csv'))
    data['assumptions']['ss_sig_param_tech'] = read_sig_param_tech(os.path.join(local_path, 'ss_sig_param_tech.csv'))
    data['assumptions']['is_sig_param_tech'] = read_sig_param_tech(os.path.join(local_path, 'is_sig_param_tech.csv'))

    # Read in installed technologies (from script data)
    data['assumptions']['rs_installed_tech'] = read_installed_tech(os.path.join(local_path, 'rs_installed_tech.csv'))
    data['assumptions']['ss_installed_tech'] = read_installed_tech(os.path.join(local_path, 'ss_installed_tech.csv'))
    data['assumptions']['is_installed_tech'] = read_installed_tech(os.path.join(local_path, 'is_installed_tech.csv'))

    # Read data after apply climate change (from script data)
    data['temp_data'] = read_weather_data.read_weather_data_script_data(
        data['local_paths']['dir_raw_weather_data'])

    # Disaggregation: Load disaggregated fuel per enduse and sector
    data['rs_fuel_disagg'] = read_disaggregated_fuel(
        os.path.join(data['local_paths']['data_processed_disaggregated'], 'rs_fuel_disagg.csv'),
        data['lookups']['fueltypes_nr'])
    data['ss_fuel_disagg'] = read_disaggregated_fuel_sector(
        os.path.join(data['local_paths']['data_processed_disaggregated'], 'ss_fuel_disagg.csv'),
        data['lookups']['fueltypes_nr'])
    data['is_fuel_disagg'] = read_disaggregated_fuel_sector(
        os.path.join(data['local_paths']['data_processed_disaggregated'], 'is_fuel_disagg.csv'),
        data['lookups']['fueltypes_nr'])

    return data

def read_csv_data_service(path_to_csv, fueltypes_nr):
    """This function reads in base_data_CSV all fuel types

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    fueltypes_nr : str
        Nr of fueltypes

    Returns
    -------
    elements_array : dict
        Returns an dict with arrays

    Notes
    -----
    the first row is the fuel_ID
    The header is the sub_key
    """
    lines = []
    end_uses_dict = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row
        _secondline = next(read_lines) # Skip first row

        # All sectors
        all_sectors = set([])
        for sector in _secondline[1:]: #skip fuel ID:
            all_sectors.add(sector)

        # All enduses
        all_enduses = set([])
        for enduse in _headings[1:]: #skip fuel ID:
            all_enduses.add(enduse)

        # Initialise dict
        for sector in all_sectors:
            end_uses_dict[sector] = {}
            for enduse in all_enduses:
                end_uses_dict[sector][enduse] = np.zeros((fueltypes_nr), dtype=float)

        for row in read_lines:
            lines.append(row)

        for cnt_fueltype, row in enumerate(lines):
            for cnt, entry in enumerate(row[1:], 1):
                enduse = _headings[cnt]
                sector = _secondline[cnt]
                end_uses_dict[sector][enduse][cnt_fueltype] += float(entry)

    return end_uses_dict, list(all_sectors), list(all_enduses)

def read_csv_float(path_to_csv):
    """This function reads in CSV files and skips header row.

    Arguments
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    service_switches = []

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            service_switches.append(row)

    return np.array(service_switches, float)

def read_load_shapes_tech(path_to_csv):
    """This function reads in csv technology shapes

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    """
    load_shapes_dh = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            dh_shape = np.zeros((24), dtype=float)
            for cnt, row_entry in enumerate(row[1:], 1):
                dh_shape[int(_headings[cnt])] = float(row_entry)

            load_shapes_dh[str(row[0])] = dh_shape

    return load_shapes_dh

def read_service_switch(path_to_csv, specified_tech_enduse_by):
    """This function reads in service assumptions from csv file

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    specified_tech_enduse_by : dict
        Technologiey per enduse for base year

    Returns
    -------
    enduse_tech_ey_p : dict
        Technologies per enduse for endyear in p
    tech_maxl_by_p : dict
        Maximum service per technology which can be switched
    service_switches : dict
        Service switches

    Notes
    -----
    The base year service shares are generated from technology stock definition
    - skips header row
    - It also test if plausible inputs
    While not only loading in all rows, this function as well tests if
    inputs are plausible (e.g. sum up to 100%)
    """
    service_switches = []
    enduse_tech_ey_p = {}
    tech_maxl_by_p = {}
    service_switch_enduse_crit = {} #Store to list enduse specific switchcriteria (true or false)

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            try:
                service_switches.append(
                    {
                        'enduse': str(row[0]),
                        'tech': str(row[1]),
                        'service_share_ey': float(row[2]),
                        'tech_assum_max_share': float(row[3]),
                        'year_switch_ey': float(row[4])
                    }
                )
            except (KeyError, ValueError):
                sys.exit("Check if provided data is complete (no empty csv entries)")

    # Group all entries according to enduse
    all_enduses = []
    for line in service_switches:
        enduse = line['enduse']
        if enduse not in all_enduses:
            all_enduses.append(enduse)
            enduse_tech_ey_p[enduse] = {}
            tech_maxl_by_p[enduse] = {}

    # Iterate all endusese and assign all lines
    for enduse in all_enduses:
        for line in service_switches:
            if line['enduse'] == enduse:
                tech = line['tech']
                enduse_tech_ey_p[enduse][tech] = line['service_share_ey']
                tech_maxl_by_p[enduse][tech] = line['tech_assum_max_share']

    # ------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for enduse in specified_tech_enduse_by:
        if enduse in service_switch_enduse_crit: #If switch is defined for this enduse
            for tech in specified_tech_enduse_by[enduse]:
                if tech not in enduse_tech_ey_p[enduse]:
                    sys.exit("No end year service share is defined for technology '{}' for the enduse '{}' ".format(tech, enduse))

    # Test if more service is provided as input than possible to maximum switch
    for entry in service_switches:
        if entry['service_share_ey'] > entry['tech_assum_max_share']:
            sys.exit("More service switch is provided for tech '{}' in enduse '{}' than max possible".format(entry['enduse'], entry['tech']))

    # Test if service of all provided technologies sums up to 100% in the end year
    for enduse in enduse_tech_ey_p:
        if round(sum(enduse_tech_ey_p[enduse].values()), 2) != 1.0:
            sys.exit("The provided ey service switch of enduse '{}' does not sum up to 1.0 (100%)".format(enduse))

    # ------------------------------------------------------
    # Add all other enduses for which no switch is defined
    # ------------------------------------------------------
    for enduse in specified_tech_enduse_by:
        if enduse not in enduse_tech_ey_p:
            enduse_tech_ey_p[enduse] = {}

    return enduse_tech_ey_p, tech_maxl_by_p, service_switches

def read_fuel_switches(path_to_csv, enduses, lookups):
    """This function reads in from CSV file defined fuel switch assumptions

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    enduses : dict
        Endues per submodel
    lookups : dict
        Look-ups

    Returns
    -------
    dict_with_switches : dict
        All assumptions about fuel switches provided as input
    """
    service_switches = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            try:
                service_switches.append(
                    {
                        'enduse': str(row[0]),
                        'enduse_fueltype_replace': lookups['fueltype'][str(row[1])],
                        'technology_install': str(row[2]),
                        'switch_yr': float(row[3]),
                        'share_fuel_consumption_switched': float(row[4]),
                        'max_theoretical_switch': float(row[5])
                    }
                )
            except (KeyError, ValueError):
                sys.exit("Check if provided data is complete (no emptly csv entries)")

    # -------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for element in service_switches:
        if element['share_fuel_consumption_switched'] > element['max_theoretical_switch']:
            sys.exit("More fuel is switched than theorically possible for enduse '{}' and fueltype '{}".format(element['enduse'], element['enduse_fueltype_replace']))

        if element['share_fuel_consumption_switched'] == 0:
            sys.exit("The share of switched fuel needs to be bigger than than 0 (otherwise delete as this is the standard input)")

    # Test if more than 100% per fueltype is switched
    for element in service_switches:
        enduse = element['enduse']
        fuel_type = element['enduse_fueltype_replace']

        tot_share_fueltype_switched = 0
        # Do check for every entry
        for element_iter in service_switches:
            if enduse == element_iter['enduse'] and fuel_type == element_iter['enduse_fueltype_replace']:
                # Found same fueltypes which is switched
                tot_share_fueltype_switched += element_iter['share_fuel_consumption_switched']

        if tot_share_fueltype_switched > 1.0:
            sys.exit("The defined fuel switches are larger than 1.0 for enduse {} and fueltype {}".format(enduse, fuel_type))

    # Test whether defined enduse exist
    for element in service_switches:
        if element['enduse'] in enduses['ss_all_enduses'] or element['enduse'] in enduses['rs_all_enduses'] or element['enduse'] in enduses['is_all_enduses']:
            pass
        else:
            sys.exit("The defined enduse '{}' to switch fuel from is not defined...".format(element['enduse']))

    return service_switches

def read_technologies(path_to_csv):
    """Read in technology definition csv file

    Arguments
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    dict_technologies : dict
        All technologies and their assumptions provided as input
    dict_tech_lists : dict
        List with technologies. The technology type
        is defined in the technology input file
    """
    dict_technologies = {}
    dict_tech_lists = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            technology = row[0]
            try:
                dict_technologies[technology] = {
                    'fuel_type': str(row[1]),
                    'eff_by': float(row[2]),
                    'eff_ey': float(row[3]),
                    'year_eff_ey': float(row[4]), #MAYBE: ADD DICT WITH INTERMEDIARY POINTS
                    'eff_achieved': float(row[5]),
                    'diff_method': str(row[6]),
                    'market_entry': float(row[7]),
                    'tech_list': str.strip(row[8]),
                    'tech_assum_max_share': float(str.strip(row[9]))
                }
                try:
                    dict_tech_lists[str.strip(row[8])].append(technology)
                except KeyError:
                    dict_tech_lists[str.strip(row[8])] = [technology]

            except Exception as e:
                logging.error(e)
                logging.error("Error in technology loading table. Check if e.g. empty field")
                sys.exit()

    return dict_technologies, dict_tech_lists

def read_base_data_resid(path_to_csv):
    """This function reads in base_data_CSV all fuel types

    (first row is fueltype, subkey), header is appliances

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : dict
        Returns an dict with arrays

    Notes
    -----
    the first row is the fuel_ID
    The header is the sub_key
    """
    try:
        lines = []
        end_uses_dict = {}

        with open(path_to_csv, 'r') as csvfile:
            read_lines = csv.reader(csvfile, delimiter=',')
            _headings = next(read_lines) # Skip first row

            for row in read_lines:
                lines.append(row)

            for i in _headings[1:]: # skip first
                end_uses_dict[i] = np.zeros((len(lines)), dtype=float)

            for cnt_fueltype, row in enumerate(lines):
                cnt = 1 #skip first
                for i in row[1:]:
                    end_use = _headings[cnt]
                    end_uses_dict[end_use][cnt_fueltype] = i
                    cnt += 1
    except (KeyError, ValueError):
        sys.exit("Check whether tehre any empty cells in the csv files for enduse '{}".format(end_use))

    # Create list with all rs enduses
    all_enduses = []
    for enduse in end_uses_dict:
        all_enduses.append(enduse)

    return end_uses_dict, all_enduses

def read_csv_base_data_industry(path_to_csv, fueltypes_nr, lu_fueltypes):
    """This function reads in base_data_CSV all fuel types

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : dict
        Returns an dict with arrays

    Notes
    -----
    the first row is the fuel_ID
    The header is the sub_key
    """
    lines = []
    end_uses_dict = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines)
        _secondline = next(read_lines)

        # All sectors
        all_enduses = set([])
        for enduse in _headings[1:]:
            if enduse is not '':
                all_enduses.add(enduse)

        # All enduses
        all_sectors = set([])
        for line in read_lines:
            lines.append(line)
            all_sectors.add(line[0])

        # Initialise dict
        for sector in all_sectors:
            end_uses_dict[sector] = {}
            for enduse in all_enduses:
                end_uses_dict[str(sector)][str(enduse)] = np.zeros((fueltypes_nr), dtype=float)

        for row in lines:
            sector = row[0]
            for position, entry in enumerate(row[1:], 1): # Start with position 1

                if entry != '':
                    enduse = str(_headings[position])
                    fueltype = _secondline[position]
                    fueltype_int = tech_related.get_fueltype_int(lu_fueltypes, fueltype)
                    end_uses_dict[sector][enduse][fueltype_int] += float(row[position])

    return end_uses_dict, list(all_sectors), list(all_enduses)

def read_installed_tech(path_to_csv):
    """Read

    Arguments
    --------
    path_to_csv : str
        Path
    """
    tech_installed = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            enduse = str.strip(row[0])
            technology = str.strip(row[1])

            try:
                tech_installed[enduse]
            except KeyError:
                tech_installed[enduse] = []

            if technology == "[]": # If no tech
                pass
            else:
                tech_installed[enduse].append(technology)

    return tech_installed

def read_sig_param_tech(path_to_csv):
    """Read 
    """
    logging.debug("... read in sig parameters: %s", path_to_csv)
    sig_param_tech = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            enduse = str.strip(row[0])
            technology = str.strip(row[1])
            midpoint = float(row[2])
            steepness = float(row[3])
            l_parameter = float(row[4])

            try:
                sig_param_tech[enduse]
            except KeyError:
                sig_param_tech[enduse] = {}
            
            sig_param_tech[enduse][technology] = {}
            sig_param_tech[enduse][technology] ['midpoint'] = midpoint
            sig_param_tech[enduse][technology] ['steepness'] = steepness
            sig_param_tech[enduse][technology] ['l_parameter'] = l_parameter

    return sig_param_tech

def read_service_fueltype_tech_by_p(path_to_csv):
    """Read in service data

    Arguments
    ----------
    path_to_csv : str
        Path to csv

    """
    service_fueltype_tech_by_p = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            service = str.strip(row[0])
            fueltype = int(row[1])
            tech = str.strip(row[2])
            service_p = float(row[3])

            try:
                service_fueltype_tech_by_p[service]
            except KeyError:
                service_fueltype_tech_by_p[service] = {}
            try:
                service_fueltype_tech_by_p[service][fueltype]
            except KeyError:
                service_fueltype_tech_by_p[service][fueltype] = {}

            if tech == 'None':
                service_fueltype_tech_by_p[service][fueltype] = {}
            else:
                try:
                    service_fueltype_tech_by_p[service][fueltype][tech]
                except KeyError:
                    service_fueltype_tech_by_p[service][fueltype][tech] = 0

                service_fueltype_tech_by_p[service][fueltype][tech] += service_p

    return service_fueltype_tech_by_p

def read_service_fueltype_by_p(path_to_csv):
    """Read
    """
    logging.debug("... read in service data: %s", path_to_csv)
    service_fueltype_by_p = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            service = str.strip(row[0])
            fueltype = int(row[1])
            service_p = float(row[2])

            try:
                service_fueltype_by_p[service]
            except KeyError:
                service_fueltype_by_p[service] = {}
            try:
                service_fueltype_by_p[service][fueltype]
            except KeyError:
                service_fueltype_by_p[service][fueltype] = 0

            service_fueltype_by_p[service][fueltype] += service_p

    return service_fueltype_by_p

def read_service_tech_by_p(path_to_csv):
    """Read
    """
    logging.debug("... read in service data: %s", path_to_csv)
    service_tech_by_p = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            service = str.strip(row[0])
            tech = str.strip(row[1])
            service_p = float(row[2])

            try:
                service_tech_by_p[service]
            except KeyError:
                service_tech_by_p[service] = {}
            try:
                service_tech_by_p[service][tech]
            except KeyError:
                service_tech_by_p[service][tech] = 0

            service_tech_by_p[service][tech] += service_p

    return service_tech_by_p

def read_disaggregated_fuel(path_to_csv, fueltypes_nr):
    """Read disaggregated fuel
    """
    fuel_sector_enduse = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            region = str.strip(row[0])
            enduse = str.strip(row[1])
            fueltype = int(row[2])
            fuel = float(row[3])
            try:
                fuel_sector_enduse[region]
            except KeyError:
                fuel_sector_enduse[region] = {}
            try:
                fuel_sector_enduse[region][enduse]
            except KeyError:
                fuel_sector_enduse[region][enduse] = np.zeros((fueltypes_nr), dtype=float)

            fuel_sector_enduse[region][enduse][fueltype] = fuel

    return fuel_sector_enduse

def read_disaggregated_fuel_sector(path_to_csv, fueltypes_nr):
    """Read disaggregated fuel
    """
    fuel_sector_enduse = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip headers

        for row in read_lines:
            region = str.strip(row[0])
            enduse = str.strip(row[1])
            sector = str.strip(row[2])
            fueltype = int(row[3])
            fuel = float(row[4])
            try:
                fuel_sector_enduse[region]
            except KeyError:
                fuel_sector_enduse[region] = {}
            try:
                fuel_sector_enduse[region][sector]
            except KeyError:
                fuel_sector_enduse[region][sector] = {}
            try:
                fuel_sector_enduse[region][sector][enduse]
            except KeyError:
                fuel_sector_enduse[region][sector][enduse] = np.zeros((fueltypes_nr), dtype=float)

            fuel_sector_enduse[region][sector][enduse][fueltype] = fuel

    return fuel_sector_enduse

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
    out_dict = np.zeros((365), dtype=float)
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(row, dtype=float)
    return out_dict

def read_lf_y(path_enduse_specific_results):
    """Read load factors from txt file
    """
    results = defaultdict(dict)

    all_txt_files_in_folder = os.listdir(path_enduse_specific_results)

    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_enduse_specific_results, file_path)
        file_path_split = file_path.split("__")
        txt_data = np.loadtxt(path_file_to_read, delimiter=',')

        year = int(file_path_split[1])
        fueltype_int = int(file_path_split[2])

        # Add year if not already exists
        results[year][fueltype_int] = txt_data

    return results

def read_pop(path_enduse_specific_results):
    """Read load factors from txt file
    """
    results = defaultdict(dict)

    all_txt_files_in_folder = os.listdir(path_enduse_specific_results)

    # Iterate files
    for file_path in all_txt_files_in_folder:
        path_file_to_read = os.path.join(path_enduse_specific_results, file_path)
        file_path_split = file_path.split("__")
        txt_data = np.loadtxt(path_file_to_read, delimiter=',')
        year = int(file_path_split[1])

        # Add year if not already exists
        results[year] = txt_data

    return results

def read_capacity_installation(path_to_csv):
    """This function reads in service assumptions from csv file

    Arguments
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    service_switches : dict
        Service switches which implement the defined capacity installation
    """
    service_switches = []

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            try:
                service_switches.append(
                    {
                        'enduse': str(row[0]),
                        'technology_install': str(row[1]),
                        'market_entry': float(row[2]),
                        'switch_yr': float(row[3]),
                        'installed_capacity':  float(row[4])
                    }
                )
            except (KeyError, ValueError):
                sys.exit("Error in loading service switch: Check if provided data is complete (no emptly csv entries)")

    return service_switches
