"""Reading raw data
"""
import sys
import os
import csv
import json
import logging
from collections import defaultdict
import yaml
import numpy as np
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_weather_data
from energy_demand.profiles import load_profile
from energy_demand.scripts import s_disaggregation
from energy_demand.read_write import data_loader
from energy_demand.technologies import fuel_service_switch
from energy_demand.scripts import init_scripts

class TechnologyData(object):
    """Class to store technology related
    data

    Arguments
    ---------
    fuel_type : str
        Fueltype of technology
    eff_by : str
        Efficiency of technology in base year
    eff_ey : str
        Efficiency of technology in future year
    year_eff_ey : int
        Future year when eff_ey is fully realised
    eff_achieved : float
        Factor of how much of the efficienc future
        efficiency is achieved
    diff_method : float
        Differentiation method
    market_entry : int,default=2015
        Year when technology comes on the market
    tech_list : list
        List where technology is part of
    tech_max_share : float
        Maximum theoretical fraction of how much
        this indivdual technology can contribute
        to total energy service of its enduse
    """
    def __init__(
            self,
            fuel_type=None,
            eff_by=None,
            eff_ey=None,
            year_eff_ey=None,
            eff_achieved=None,
            diff_method=None,
            market_entry=2015,
            tech_list=None,
            tech_max_share=None,
            fueltypes=None
        ):
        self.fuel_type_str = fuel_type
        self.fuel_type_int = tech_related.get_fueltype_int(fueltypes, fuel_type)
        self.eff_by = eff_by
        self.eff_ey = eff_ey
        self.year_eff_ey = year_eff_ey
        self.eff_achieved = eff_achieved
        self.diff_method = diff_method
        self.market_entry = market_entry
        self.tech_list = tech_list
        self.tech_max_share = tech_max_share

class CapacitySwitch(object):
    """Capacity switch class for storing
    switches

    Arguments
    ---------
    enduse : str
        Enduse of affected switch
    technology_install : str
        Installed technology
    switch_yr : int
        Year until capacity installation is fully realised
    installed_capacity : float
        Installed capacity in GWh
    """
    def __init__(
            self,
            enduse,
            technology_install,
            switch_yr,
            installed_capacity
        ):

        self.enduse = enduse
        self.technology_install = technology_install
        self.switch_yr = switch_yr
        self.installed_capacity = installed_capacity

class FuelSwitch(object):
    """Fuel switch class for storing
    switches

    Arguments
    ---------
    enduse : str
        Enduse of affected switch
    enduse_fueltype_replace : str
        Fueltype which is beeing switched from
    technology_install : str
        Installed technology
    switch_yr : int
        Year until switch is fully realised
    fuel_share_switched_ey : float
        Switched fuel share
    """
    def __init__(
            self,
            enduse=None,
            enduse_fueltype_replace=None,
            technology_install=None,
            switch_yr=None,
            fuel_share_switched_ey=None
        ):

        self.enduse = enduse
        self.enduse_fueltype_replace = enduse_fueltype_replace
        self.technology_install = technology_install
        self.switch_yr = switch_yr
        self.fuel_share_switched_ey = fuel_share_switched_ey

class ServiceSwitch(object):
    """Service switch class for storing
    switches

    Arguments
    ---------
    enduse : str
        Enduse of affected switch
    technology_install : str
        Installed technology
    service_share_ey : float
        Service share of installed technology in future year
    switch_yr : int
        Year until switch is fully realised
    """
    def __init__(
            self,
            enduse=None,
            technology_install=None,
            service_share_ey=None,
            switch_yr=None
        ):
        self.enduse = enduse
        self.technology_install = technology_install
        self.service_share_ey = service_share_ey
        self.switch_yr = switch_yr

'''def read_param_yaml(path):
    """Read yaml parameters
    """
    with open(path, 'r') as ymlfile:
        parameter_dict = yaml.load(ymlfile)

    return parameter_dict'''

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
        except KeyError:
            results[year][enduse] = np.zeros((fueltypes_nr, 365, 24), dtype=float)

        # Add year if not already exists
        results[year][enduse][fueltype_array_position] = txt_data

    return results

def load_script_data(data):
    """Load data generated by scripts
    #SCRAP REMOVE
    Arguments
    ---------
    data : dict
        Data container
    """
    fts_cont, sgs_cont, sd_cont, switches_cont = init_scripts.scenario_initalisation(
            data['paths']['path_main'], data)
    
    data['assumptions']['rs_service_tech_by_p'] = fts_cont['rs_service_tech_by_p']
    data['assumptions']['ss_service_tech_by_p'] = fts_cont['ss_service_tech_by_p']
    data['assumptions']['is_service_tech_by_p'] = fts_cont['is_service_tech_by_p']
    data['assumptions']['rs_service_fueltype_by_p'] = fts_cont['rs_service_fueltype_by_p']
    data['assumptions']['ss_service_fueltype_by_p'] = fts_cont['ss_service_fueltype_by_p']
    data['assumptions']['is_service_fueltype_by_p'] = fts_cont['is_service_fueltype_by_p']
    data['assumptions']['rs_service_fueltype_tech_by_p'] = fts_cont['rs_service_fueltype_tech_by_p']
    data['assumptions']['ss_service_fueltype_tech_by_p'] = fts_cont['ss_service_fueltype_tech_by_p']
    data['assumptions']['is_service_fueltype_tech_by_p'] = fts_cont['is_service_fueltype_tech_by_p']
    data['assumptions']['rs_tech_increased_service'] = sgs_cont['rs_tech_increased_service']
    data['assumptions']['ss_tech_increased_service'] = sgs_cont['ss_tech_increased_service']
    data['assumptions']['is_tech_increased_service'] = sgs_cont['is_tech_increased_service']
    data['assumptions']['rs_tech_decreased_share'] = sgs_cont['rs_tech_decreased_share']
    data['assumptions']['ss_tech_decreased_share'] = sgs_cont['ss_tech_decreased_share']
    data['assumptions']['is_tech_decreased_share'] = sgs_cont['is_tech_decreased_share']
    data['assumptions']['rs_tech_constant_share'] = sgs_cont['rs_tech_constant_share']
    data['assumptions']['ss_tech_constant_share'] = sgs_cont['ss_tech_constant_share']
    data['assumptions']['is_tech_constant_share'] = sgs_cont['is_tech_constant_share']
    data['assumptions']['rs_sig_param_tech'] = sgs_cont['rs_sig_param_tech']
    data['assumptions']['ss_sig_param_tech'] = sgs_cont['ss_sig_param_tech']
    data['assumptions']['is_sig_param_tech'] = sgs_cont['is_sig_param_tech']
    data['assumptions']['rs_installed_tech'] = sgs_cont['rs_installed_tech']
    data['assumptions']['ss_installed_tech'] = sgs_cont['ss_installed_tech']
    data['assumptions']['is_installed_tech'] = sgs_cont['is_installed_tech']
    data['rs_fuel_disagg'] = sd_cont['rs_fuel_disagg']
    data['ss_fuel_disagg'] = sd_cont['ss_fuel_disagg']
    data['is_fuel_disagg'] = sd_cont['is_fuel_disagg']

    data['assumptions']['rs_service_switches'] = switches_cont['rs_service_switches']
    data['assumptions']['ss_service_switches'] = switches_cont['ss_service_switches']
    data['assumptions']['is_service_switches'] = switches_cont['is_service_switches']

    data['assumptions']['rs_share_service_tech_ey_p'] = switches_cont['rs_share_service_tech_ey_p']
    data['assumptions']['ss_share_service_tech_ey_p'] = switches_cont['ss_share_service_tech_ey_p']
    data['assumptions']['is_share_service_tech_ey_p'] = switches_cont['is_share_service_tech_ey_p']
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
    service_switch_enduse_crit = {} #Store to list enduse specific switchcriteria (true or false)

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            try:
                service_switches.append(
                    ServiceSwitch(
                        enduse=str(row[0]),
                        technology_install=str(row[1]),
                        service_share_ey=float(row[2]),
                        switch_yr=float(row[3])
                    )
                )
            except (KeyError, ValueError):
                sys.exit("Check if provided data is complete (no empty csv entries)")

    # TODO: WRITE TEST AND TEST IF IN TECHNOLOGY DEFINITION CONTRADICTION
    # Test if more service is provided as input than possible to maximum switch
    '''for entry in service_switches:
        if entry['service_share_ey'] > entry['tech_max_share']:
            sys.exit("More service switch is provided for tech '{}' in enduse '{}' than max possible".format(entry['enduse'], entry['technology_install']))
    '''
    # Test if service of all provided technologies sums up to 100% in the end year
    '''for enduse in enduse_tech_ey_p:
        if round(sum(enduse_tech_ey_p[enduse].values()), 2) != 1.0:
            sys.exit("The provided ey service switch of enduse '{}' does not sum up to 1.0 (100%)".format(enduse))'''

    return service_switches

def read_fuel_switches(path_to_csv, enduses, lu_fueltypes):
    """This function reads in from CSV file defined fuel
    switch assumptions

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    enduses : dict
        Endues per submodel
    lu_fueltypes : dict
        Look-ups

    Returns
    -------
    dict_with_switches : dict
        All assumptions about fuel switches provided as input
    """
    service_switches = []

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines)

        for row in read_lines:
            try:
                service_switches.append(
                    FuelSwitch(
                        enduse=str(row[0]),
                        enduse_fueltype_replace=lu_fueltypes[str(row[1])],
                        technology_install=str(row[2]),
                        switch_yr=float(row[3]),
                        fuel_share_switched_ey=float(row[4]))
                )
            except (KeyError, ValueError):
                sys.exit("Check if provided data is complete (no emptly csv entries)")

    # -------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for obj in service_switches:
        #TODO: WRITE TEST FROM TECHNOLOGIES
        #if obj['fuel_share_switched_ey'] > obj['max_theoretical_switch']:
        #    sys.exit("More fuel is switched than theorically possible for enduse '{}' and fueltype '{}".format(obj['enduse'], obj['enduse_fueltype_replace']))

        if obj.fuel_share_switched_ey == 0:
            sys.exit("The share of switched fuel needs to be bigger than than 0 (otherwise delete as this is the standard input)")

    # Test if more than 100% per fueltype is switched
    for obj in service_switches:
        enduse = obj.enduse
        fuel_type = obj.enduse_fueltype_replace

        tot_share_fueltype_switched = 0
        # Do check for every entry
        for obj_iter in service_switches:
            if enduse == obj_iter.enduse and fuel_type == obj_iter.enduse_fueltype_replace:
                # Found same fueltypes which is switched
                tot_share_fueltype_switched += obj_iter.fuel_share_switched_ey

        if tot_share_fueltype_switched > 1.0:
            sys.exit("The defined fuel switches are larger than 1.0 for enduse {} and fueltype {}".format(enduse, fuel_type))

    # Test whether defined enduse exist
    for obj in service_switches:
        if obj.enduse in enduses['ss_all_enduses'] or obj.enduse in enduses['rs_all_enduses'] or obj.enduse in enduses['is_all_enduses']:
            pass
        else:
            sys.exit("The defined enduse '{}' to switch fuel from is not defined...".format(obj['enduse']))

    return service_switches

def read_technologies(path_to_csv, fueltypes):
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
                dict_technologies[technology] = TechnologyData(
                    fuel_type=str(row[1]),
                    eff_by=float(row[2]),
                    eff_ey=float(row[3]),
                    year_eff_ey=float(row[4]), #MAYBE: ADD DICT WITH INTERMEDIARY POINTS
                    eff_achieved=float(row[5]),
                    diff_method=str(row[6]),
                    market_entry=float(row[7]),
                    tech_list=str.strip(row[8]),
                    tech_max_share=float(str.strip(row[9])),
                    fueltypes=fueltypes)
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

            # If no tech
            if technology == "[]":
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

    return dict(results)

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

    return dict(results)

def read_capacity_installation(path_to_csv):
    """This function reads in service assumptions
    from csv file

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
                    CapacitySwitch(
                        enduse=str(row[0]),
                        technology_install=str(row[1]),
                        switch_yr=float(row[2]),
                        installed_capacity=float(row[3])))
            except (KeyError, ValueError):
                sys.exit("Error in loading service switch: Check if provided data is complete (no emptly csv entries)")

    return service_switches
