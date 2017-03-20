"""This file stores all functions of main.py"""

import os
import csv
from datetime import date
from datetime import timedelta as td
import numpy as np
print("Loading main functions")
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def convert_result_to_final_total_format(data, all_regions):
    """Convert into nested citionary with fueltype, region, hour"""

    timesteps, _ = timesteps_full_year()                                 # Create timesteps for full year (wrapper-timesteps)
    result_dict = initialise_energy_supply_dict(data['fuel_type_lu'], data['reg_lu'], timesteps)

    for reg in all_regions:
        print("reg_id " + str(reg))
        region_name = reg.reg_id

        # Get total fuel fuel
        hourly_all_fuels = reg.tot_all_enduses_h()

        # Iterate fueltypes
        for fueltype in data['fuel_type_lu']:

            fuel_total_h_all_end_uses = hourly_all_fuels[fueltype]

            # Convert array into dict for out_read
            out_dict = dict(enumerate(fuel_total_h_all_end_uses))

            result_dict[fueltype][region_name] = out_dict

    return result_dict

def load_data(data, path_main):
    """All base data no provided externally are loaded

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------
    data : dict
        Dict with own data

    Returns
    -------
    data : list
        Returns a list where all datas are wrapped together.

    Notes
    -----

    """
    # As soon as old model is deleted, mode this to data_loader
    import energy_demand.data_loader as dl

    # ------Read in all data from csv files which have to be read in anyway
    data = read_data(data, path_main)

    # --- Execute data generatore
    run_data_collection = True # Otherwise already read out files are read in from txt files
    data = dl.generate_data(data, run_data_collection)


    # ---TESTS
    # Test if numer of fuel types is identical (Fuel lookup needs to have same dimension as end-use fuels)
    for end_use in data['data_residential_by_fuel_end_uses']:
        assert len(data['fuel_type_lu']) == len(data['data_residential_by_fuel_end_uses'][end_use]) # Fuel in fuel distionary does not correspond to len of input fuels

    # test if...
    return data

def initialise_energy_supply_dict(fuel_type_lu, reg_lu, timesteps):
    """Generates nested dictionary for providing results to smif

    Parameters
    ----------
    fuel_type_lu : array
        Contains all fuel types
    reg_pop : array
        Containes all population of different regions
    timesteps : ??
        Contaings all timesteps for the full year

    Returns
    -------
    result_dict : dict
        Returns a nested dictionary for energy supply model. (fueltype/region/timeID)

    Notes
    -----
    notes
    """
    result_dict = {}
    for i in range(len(fuel_type_lu)):
        result_dict[i] = {}
        for j in range(len(reg_lu)):
            result_dict[i][j] = {}
            for k in timesteps:
                result_dict[i][j][k] = {}
    return result_dict

def read_csv_float(path_to_csv):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    list_elements = []
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(row)

    # Convert list into array
    elements_array = np.array(list_elements, float)
    return elements_array

def read_csv(path_to_csv):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    list_elements = []
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(row)

    # Convert list into array
    elements_array = np.array(list_elements)
    return elements_array

def read_csv_base_data_resid(path_to_csv):
    """This function reads in base_data_CSV all fuel types (first row is fueltype, subkey), header is appliances

    Parameters
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
    # Quick and dirty
    """
    l = []
    end_uses_dict = {}

    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines: # select row
            l.append(row)

        for i in _headings[1:]: # skip first
            end_uses_dict[i] = np.zeros((len(l), 1)) # len fuel_ids

        cnt_fueltype = 0
        for row in l:
            cnt = 1 #skip first
            for i in row[1:]:
                end_use = _headings[cnt]
                end_uses_dict[end_use][cnt_fueltype] = i
                cnt += 1

            cnt_fueltype += 1

    return end_uses_dict

def datetime_range(start=None, end=None):
    """Calculates all dates between a star and end date.

    Parameters
    ----------
    start : date
        Start date
    end : date
        end date

    """
    span = end - start
    for i in range(span.days + 1):
        yield start + td(days=i)

def writeToEnergySupply(path_out_csv, fueltype, in_data):
    '''
    REads out results (which still need to be preared) to list of energy supply model.

    Input:
    -path_out_csv   Path to energy supply resulting table
    -in_data        Data input

    Output:
    -               Print results
    '''
    outData = []

    # NEW: Create ID

    # WRITE TO YAMAL FILE

    print("Data for energy supply model")

    for region_nr in range(len(in_data[fueltype])):
        supplyTimeStep = 0
        for timestep in range(len(in_data[fueltype][region_nr])): #Iterate over timesteps

            if timestep == (1 * 7 * 24) or timestep == (2 * 7 * 24) or timestep == (3 * 7 * 24) or timestep == (4 * 7 * 24):
                supplyTimeStep = 0

            outData.append([region_nr, timestep, supplyTimeStep, in_data[fueltype][region_nr][timestep].sum()]) # List with data out

            print(" Region: " + str(region_nr) + str("   Demand teimstep:  ") + str(timestep) + str("   supplyTimeStep: " + str(supplyTimeStep) + str("   Sum: " + str(in_data[fueltype][region_nr][timestep].sum()))))
            supplyTimeStep += 1

    '''# Read existing CSV
    existing_data = read_csv(path_dictpath_out_csv)
    print(existing_data)

    for i, j in zip(existing_data, new_data):
        i[5] = j[5]

    print("---")
    print(existing_data)
    '''
    with open(path_out_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for row in outData: #existing_data:
            writer.writerow(row)
    return

def conversion_ktoe_gwh(data_ktoe):
    """Conversion of ktoe to gwh

    Parameters
    ----------
    data_ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in GWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """

    data_gwh = data_ktoe * 11.6300000
    return data_gwh

def timesteps_full_year():
    """This function generates a single list from a list with start and end dates
    and adds the same date into the list according to the number of hours in a day.

    Parameters
    ----------

    Returns
    -------
    timestep : list
        List containing all dates according to number of hours
    """
    #TODO: improve

    full_year_date = [date(2015, 1, 1), date(2015, 12, 31)] # Base Year
    start_date, end_date = full_year_date[0], full_year_date[1]
    list_dates = list(datetime_range(start=start_date, end=end_date)) # List with every date in a year

    hours = 24
    yaml_list = [] ## l = [{'id': value, 'start': 'p', 'end': 'P2',   }
    timestep_full_year_dict = {} #  YEARDAY_H

    #Add to list
    #h_year_id = 0
    for day_date in list_dates:
        _info = day_date.timetuple() # Get date
        day_of_that_year = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

        # Interate hours
        for h_id in range(hours):
            #Create ID (yearday_hour of day)
            start_period = "P{}H".format(day_of_that_year * 24 + h_id)
            end_period = "P{}H".format(day_of_that_year * 24 + h_id + 1)

            yearday_h_id = str(str(day_of_that_year) + str("_") + str(h_id))

            #start_period = str("P" + str(h_year_id) + str("H"))
            #end_period = str("P" + str(h_year_id + 1) + str("H"))

            # Add to dict
            timestep_full_year_dict[yearday_h_id] = {'start': start_period, 'end': end_period}

            #Add to yaml listyaml
            yaml_list.append({'id': yearday_h_id, 'start': start_period, 'end': end_period})

    return timestep_full_year_dict, yaml_list

def get_weekday_type(date_from_yearday):
    """Gets the weekday of a date

    Parameters
    ----------
    date_from_yearday : date
        Date of a day in ayear

    Returns
    -------
    daytype : int
        If 1: holiday, if 0; working day

    Notes
    -----
    notes
    """
    _info = date_from_yearday.timetuple()
    weekday = _info[6]                # 0: Monday
    if weekday == 5 or weekday == 6:
        return 1 # Holiday
    else:
        return 0 # Working day

def read_csv_nested_dict(path_to_csv):
    """Read in csv file into nested dictionary with first row element as main key

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {float(1990): {str(Header1): float(Val1), str(Header2): Val2}}
    """

    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            out_dict[float(row[0])] = {}
            cnt = 1 # because skip first element
            for i in row[1:]:
                out_dict[float(row[0])][_headings[cnt]] = float(i)
                cnt += 1

    return out_dict

def read_csv_dict(path_to_csv):
    """Read in csv file into a dict (with header)

    The function tests if a value is a string or float
    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {{str(Year): float(1990), str(Header1): float(Val1), str(Header2): float(Val2)}}
    """

    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:

            # Iterate row entries
            for k, i in enumerate(row):

                # Test if float or string
                try:
                    out_dict[_headings[k]] = float(i)
                except ValueError:
                    out_dict[_headings[k]] = str(i)

    return out_dict

def read_csv_dict_no_header(path_to_csv):
    """Read in csv file into a dict (without header)

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {{str(Year): float(1990), str(Header1): float(Val1), str(Header2): float(Val2)}}
    """
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:

            # Iterate row entries
            try:
                out_dict[int(row[0])] = float(row[1])
            except ValueError:
                out_dict[int(row[0])] = str(row[1])

    return out_dict

def read_data(data, path_main):
    """Reads in all csv files and stores them in a dictionary

    Parameters
    ----------
    path_main : str
        Path to main model folder
    path_dict : dict
        Dictionary containing all path to individual files

    Returns
    -------
    data : dict
        Dictionary containing read in data from csv files


    #Todo: Iterate every row and test if string or float value and then only write one write in function
    """
    path_dict = {'path_pop_reg_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_nr_regions.csv'),
                 'path_dwtype_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),
                 'path_lookup_appliances':os.path.join(path_main, 'residential_model/lookup_appliances_HES.csv'),
                 'path_fuel_type_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_fuel_types.csv'),
                 'path_day_type_lu': os.path.join(path_main, 'residential_model/lookup_day_type.csv'),
                 'path_bd_e_load_profiles': os.path.join(path_main, 'residential_model/HES_base_appliances_eletricity_load_profiles.csv'),
                 'path_temp_2015': os.path.join(path_main, 'residential_model/CSV_YEAR_2015.csv'),
                 'path_hourly_gas_shape': os.path.join(path_main, 'residential_model/SANSOM_residential_gas_hourly_shape.csv'),
                 'path_dwtype_dist': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_distribution.csv'),
                 'path_dwtype_age': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_age.csv'),
                 'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_floorarea.csv'),
                 'path_reg_floorarea': os.path.join(path_main, 'residential_model/data_residential_model_floorarea.csv'),
                 'path_reg_dw_nr': os.path.join(path_main, 'residential_model/data_residential_model_nr_dwellings.csv'),

                 'path_data_residential_by_fuel_end_uses': os.path.join(path_main, 'residential_model/data_residential_by_fuel_end_uses.csv'),
                 'path_lu_appliances_HES_matched': os.path.join(path_main, 'residential_model/lookup_appliances_HES_matched.csv')

                }

    data['path_dict'] = path_dict

    # Lookup data
    data['reg_lu'] = read_csv_dict_no_header(path_dict['path_pop_reg_lu'])                # Region lookup table
    data['dwtype_lu'] = read_csv_dict_no_header(path_dict['path_dwtype_lu'])              # Dwelling types lookup table
    data['app_type_lu'] = read_csv(path_dict['path_lookup_appliances'])                   # Appliances types lookup table
    data['fuel_type_lu'] = read_csv_dict_no_header(path_dict['path_fuel_type_lu'])        # Fuel type lookup
    data['day_type_lu'] = read_csv(path_dict['path_day_type_lu'])                         # Day type lookup

    #fuel_bd_data = read_csv_float(path_dict['path_base_data_fuel'])               # All disaggregated fuels for different regions
    data['csv_temp_2015'] = read_csv(path_dict['path_temp_2015'])                         # csv_temp_2015 #TODO: Delete because loaded in shape_residential_heating_gas
    data['hourly_gas_shape'] = read_csv_float(path_dict['path_hourly_gas_shape'])         # Load hourly shape for gas from Robert Sansom #TODO: REmove because in shape_residential_heating_gas

    #path_dwtype_age = read_csv_float(['path_dwtype_age'])
    data['dwtype_distr'] = read_csv_nested_dict(path_dict['path_dwtype_dist'])
    data['dwtype_age_distr'] = read_csv_nested_dict(path_dict['path_dwtype_age'])
    data['dwtype_floorarea']  = read_csv_dict(path_dict['path_dwtype_floorarea_dw_type'])

    data['reg_floorarea'] = read_csv_dict_no_header(path_dict['path_reg_floorarea'])
    data['reg_dw_nr'] = read_csv_dict_no_header(path_dict['path_reg_dw_nr'])

    # load shapes
    data['dict_shapes_end_use_h'] = {}
    data['dict_shapes_end_use_d'] = {}


    # Data new approach
    data_residential_by_fuel_end_uses = read_csv_base_data_resid(path_dict['path_data_residential_by_fuel_end_uses']) # Yearly end use data


    data['lu_appliances_HES_matched'] = read_csv(path_dict['path_lu_appliances_HES_matched'])


    # --------------------------
    # Convert loaded data into correct units
    # --------------------------
    for enduse in data_residential_by_fuel_end_uses:
        data_residential_by_fuel_end_uses[enduse] = conversion_ktoe_gwh(data_residential_by_fuel_end_uses[enduse]) # TODO: Check if ktoe

    data['data_residential_by_fuel_end_uses'] = data_residential_by_fuel_end_uses


    return data

def disaggregate_base_demand_for_reg(data, reg_data_assump_disaggreg, data_external):
    """This function disaggregates fuel demand based on region specific parameters
    for the base year
    """

    #TODO: So far simple disaggregation by population

    regions = data['reg_lu']
    national_fuel = data['data_residential_by_fuel_end_uses'] # residential data
    dict_with_reg_fuel_data = {}
    reg_data_assump_disaggreg = reg_data_assump_disaggreg
    base_year = data_external['glob_var']['base_year']
    # Iterate regions
    for region in regions:

        #Scrap improve
        reg_pop = data_external['population'][base_year][region]         # Regional popluation
        total_pop = sum(data_external['population'][base_year].values()) # Total population

        # Disaggregate fuel depending on end_use
        intermediate_dict = {}

        for enduse in national_fuel:

            # So far simply pop
            reg_disaggregate_factor_per_enduse_and_reg = reg_pop / total_pop  #TODO: create dict with disaggregation factors

            #TODO: Get enduse_specific disaggreagtion reg_disaggregate_factor_per_enduse_and_reg
            intermediate_dict[enduse] = national_fuel[enduse] * reg_disaggregate_factor_per_enduse_and_reg

        dict_with_reg_fuel_data[region] = intermediate_dict

    data['fueldata_disagg'] = dict_with_reg_fuel_data

    return data

def write_YAML(yaml_write, path_YAML):
    """Creates a YAML file with the timesteps IDs

    Parameters
    ----------
    yaml_write : int
        Whether a yaml file should be written or not (1 or 0)
    path_YAML : str
        Path to write out YAML file

    """
    if yaml_write:
        import yaml
        _, yaml_list = timesteps_full_year()  # Create timesteps for full year (wrapper-timesteps)

        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)
    return

def write_to_csv_will(data, reesult_dict, reg_lu):
    """ Write reults for energy supply model
    e.g.

    england, P0H, P1H, 139.42, 123.49

    """

    for fueltype in data['fuel_type_lu']:

        #TODO: Give relative path stored in data[pathdict]
        path = 'C:/Users/cenv0553/GIT/NISMODII/model_output/_fueltype_{}_hourly_results'.format(fueltype)

        yaml_list = []
        with open(path, 'w', newline='') as fp:
            a = csv.writer(fp, delimiter=',')
            data = []

            for reg in reesult_dict[fueltype]:
                region_name = reg_lu[reg]


                for _day in reesult_dict[fueltype][reg]:
                    for _hour in range(24):

                        start_id = "P{}H".format(_day * 24 + _hour)
                        end_id = "P{}H".format(_day * 24 + _hour + 1)
                        
                        yaml_list.append({'region': region_name, 'start': start_id, 'end': end_id, 'value': reesult_dict[fueltype][reg][_day][_hour], 'units': 'CHECK GWH', 'year': 'XXXX'})

                        data.append([region_name, start_id, end_id, reesult_dict[fueltype][reg][_day][_hour]])

            a.writerows(data)

        #with open(path, 'w') as outfile:
        #    yaml.dump(yaml_list, outfile, default_flow_style=False)

def convert_to_array(fuel_type_p_ey):
    """Convert dictionary to array"""
    for i in fuel_type_p_ey:
        a = fuel_type_p_ey[i].items()
        a = list(a)
        fuel_type_p_ey[i] = np.array(a, dtype=float)
    return fuel_type_p_ey


def get_elasticity(demand_base, elasticity, price_base, price_curr):
    """Price Elasticity = (% Change in Quantity) / (% Change in Price)

    elasticity = (Q_base - Q_curr) / (P_base - P_curr)

    reformulate

    OK

    Q_curr = -1 * (elasticity * (P_base - P_curr) - Q_base)
    """
    pricediff = price_base - price_curr                     # Absolute price difference (e.g. 20 - 15 --> 5)
    #pricediff_p = -1 * (pricediff / demand_base)            # Price diff in percent (e.g. -1 * (5/20) --> -0.25)
    #demand_diff_in_p = elasticity * pricediff_p             # Demand difference in percent of base demand
    #demand_diff_absolute = demand_diff_in_p * demand_base   # Demand diff in absolute
    #current_demand = demand_base + demand_diff_absolute     # new demand

    # New current demand
    current_demand = -1 * ((elasticity * pricediff) - demand_base)

    return current_demand



"""A one-line summary that does not use variable names or the
    function name.
    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    long_var_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).
    This can have multiple paragraphs.
    You may include some math:

"""
