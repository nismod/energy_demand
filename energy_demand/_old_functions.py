
def get_bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, fuel_bd_data):
    """
    This function uses the generic shapes of the load profiles to hourly disaggregate energy demand
    for all regions and fuel types

    # So far only eletricity appliances

    out:
    -fuel_type_per_region_hourly        Fueltype per region per appliance per hour
        fueltype
            region
                year_days
                    appliances
                        hours
    """
    fuelType_elec = 0 # Electrcitiy
    fuel_bd_data_electricity = fuel_bd_data[:, 1] # Base fuel per region

    dim_appliance = shape_app_elec.shape

    # Initialise array
    fuel_type_per_region = np.zeros((len(fuel_type_lu), len(reg_lu)), dtype=float) # To store absolute demand values
    fuel_type_per_region_hourly = np.zeros((len(fuel_type_lu), len(reg_lu), dim_appliance[0], dim_appliance[1], dim_appliance[2]), dtype=float) # To store absolute demand values of hourly appliances

    '''# Add electricity base data
    for region_nr in range(len(reg_lu)):
        fuel_type_per_region[fuelType_elec][region_nr] = fuel_bd_data_electricity[region_nr]

    # Appliances per region
    for region_nr in range(len(reg_lu)):
        reg_demand = fuel_type_per_region[fuelType_elec][region_nr]
        reg_elec_appliance = shape_app_elec * reg_demand # Shape elec appliance * regional demand in [GWh]
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance
    '''
    #'''
    # Add electricity base data per region
    for region_nr in range(len(reg_lu)):

        reg_demand = fuel_bd_data_electricity[region_nr]
        reg_elec_appliance = shape_app_elec * reg_demand # Shape elec appliance * regional demand in [GWh]
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance
    #'''

    # Test for errors
    try:
        _control = round(float(fuel_type_per_region_hourly.sum()), 4) # Sum of input energy data, rounded to 4 digits
        _control2 = round(float(fuel_bd_data_electricity.sum()), 4)   # Sum of output energy data, rounded to 4 digits

        if _control == _control2:
            print("Input total energy demand has been correctly disaggregated.")
        else:
            _err = "Error: Something with the disaggregation went wrong.. "
            raise Exception(_err)

    except _err:
        _val = sys.exc_info()
        _, _value, _tb = sys.exc_info()
        print("Errors from function db_appliances:")
        traceback.print_tb(_tb)
        print (_value)
        sys.exit()

    return fuel_type_per_region_hourly


'''
def shape_bd_app(path_bd_e_load_profiles, daytypee_lu, app_type_lu, base_year):
    
    This function reads in the HES eletricity load profiles
    of the base year and stores them in form of an array.
    First the absolute values are stored in a HES dictionary
    for the different month and day-types. Then the total
    demand of the year is calculated and all array entries
    calculated as percentage of the total demand.

    #TODO: expand for different regions, different dwelling types, fuels...

    Input:
    -path_bd_e_load_profiles   Path to .csv file with HSE data
    -season_lookup                  Lookup dictionary with seasons
    -daytypee_lu                    Lookup dictionary with type of days
    -app_type_lu              Looup dictionary containing all appliances
    -base_year                      Base year

    Output:
    -appliances_shape               [%] Array containing the shape of appliances
                                    for every day in the base year
                                    Within each month, the same load curves are
                                    used for every working/holiday day.
        year_days of base year
            hour
                appliance_typ
    '''
    # --------Read in HES data----------
    # Initilaise array to store all values for a year
    year_days, month_nr, hours = range(365), range(12), range(24)
    year_raw_values = np.zeros((len(year_days), len(hours), len(app_type_lu)), dtype=float)

    # Initialise HES dictionary with every month and day-type
    hes_data = np.zeros((len(daytypee_lu), len(month_nr), len(hours), len(app_type_lu)), dtype=float)

    # Read in energy profiles of base_year
    raw_elec_data = read_csv(path_bd_e_load_profiles)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month, daytype, appliance_typ = int(row[0]), int(row[1]), int(row[2])
        k_header = 3    # TODO: Check if in excel data starts here

        # iterate over hour
        for hour in hours:
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000)) # [kWH electric] Converts the summed watt into kWH
            hes_data[daytype][month][hour][appliance_typ] = _value
            k_header += 1

    # Create list with all dates of a whole year
    start_date, end_date = date(base_year, 1, 1), date(base_year, 12, 31)
    list_dates = list(datetime_range(start=start_date, end=end_date))

    # Error because of leap year
    if len(list_dates) != 365:
        a = "Error: Leap year has 366 day and not 365.... "
        raise Exception(a)

    # Assign every date to the place in the array of the year
    for date_in_year in list_dates:
        _info = date_in_year.timetuple()
        month_python = _info[1] - 1       # - 1 because in _info: Month 1 = Jan
        yearday_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        daytype = get_weekday_type(date_in_year)

        _data = hes_data[daytype][month_python] # Get day from HES raw data array

        # Add values to yearly array
        year_raw_values[yearday_python] = _data

    # Calculate yearly total demand over all day years and all appliances
    total_y_demand = year_raw_values.sum()

    # Calculate Shape of the eletrictiy distribution of the appliances by assigning percent values each
    appliances_shape = np.zeros((len(year_days), len(hours), len(app_type_lu)), dtype=float)
    appliances_shape = (1.0/total_y_demand) * year_raw_values

    # Test for errors
    # ---------------
    try:
        _control = float(appliances_shape.sum())
        _control = round(_control, 4) # round for 4 digits
        if _control == 1.0:
            print("Sum of shape is 100 % - good")
        else:
            _err = "Error: The shape calculation is not 100%. Something went wrong... "
            raise Exception(_err)
    except _err:
        _val = sys.exc_info()
        print (_val)
        sys.exit()

    return appliances_shape
    '''
'''def OLDMODEL_load_data(data, data_ext, path_main):
    

    # ----------below old model

    shape_app_elec, shape_hd_gas = get_load_curve_shapes(data['path_dict']['path_bd_e_load_profiles'], data['day_type_lu'], data['app_type_lu'], data_ext['glob_var'], data['csv_temp_2015'], data['hourly_gas_shape'])
    data['shape_app_elec'] = shape_app_elec # add to data dict

    # ------Base demand for the base year for all modelled elements-------------------

    # Base demand of appliances over a full year (electricity)
    bd_app_elec = get_bd_appliances(shape_app_elec, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])
    data['bd_app_elec'] = bd_app_elec # add to data dict

    # Base demand of heating demand (gas)
    bd_hd_gas = get_bd_hd_gas(shape_hd_gas, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])
    data['bd_hd_gas'] = bd_hd_gas # add to data dict

    print("---Summary Base Demand")
    print("Base Fuel elec appliances total per year (uk):             " + str(data['fuel_bd_data'][:, 1].sum()))
    print("Base Fuel elec appliances total per year (region, hourly): " + str(bd_app_elec.sum()))
    print("  ")
    print("Base gas hd appliances total per year (uk):                " + str(data['fuel_bd_data'][:, 2].sum()))
    print("Base gas hd appliancestotal per year (region, hourly):     " + str(bd_hd_gas.sum()))

    # ---------------------------------------------------------------
    # Generate simulation timesteps and assing base demand (e.g. 1 week in each season, 24 hours)
    # ---------------------------------------------------------------
    timesteps_own_selection = (
        [date(data_ext['glob_var']['base_year'], 1, 12), date(data_ext['glob_var']['base_year'], 1, 18)],     # Week Spring (Jan) Week 03  range(334 : 364) and 0:58
        [date(data_ext['glob_var']['base_year'], 4, 13), date(data_ext['glob_var']['base_year'], 4, 19)],     # Week Summer (April) Week 16  range(59:150)
        [date(data_ext['glob_var']['base_year'], 7, 13), date(data_ext['glob_var']['base_year'], 7, 19)],     # Week Fall (July) Week 25 range(151:242)
        [date(data_ext['glob_var']['base_year'], 10, 12), date(data_ext['glob_var']['base_year'], 10, 18)],   # Week Winter (October) Week 42 range(243:333)
        )
    data['timesteps_own_selection'] = timesteps_own_selection # add to data dict

    # Create own timesteps
    own_timesteps = get_own_timesteps(timesteps_own_selection)

    # Populate timesteps base year data (appliances, electricity)
    timesteps_app_bd = create_timesteps_app(0, timesteps_own_selection, bd_app_elec, data['reg_lu'], data['fuel_type_lu'], data['app_type_lu'], own_timesteps) # [GWh]
    data['timesteps_app_bd'] = timesteps_app_bd # add to data dict

    # Populate timesteps base year data (heating demand, ga)
    timesteps_hd_bd = create_timesteps_hd(1, timesteps_own_selection, bd_hd_gas, data['reg_lu'], data['fuel_type_lu'], own_timesteps) # [GWh]
    data['timesteps_hd_bd'] = timesteps_hd_bd # add to data dict

    print("----------------------Statistics--------------------")
    print("Number of timesteps appliances:          " + str(len(timesteps_app_bd[0][0])))
    print("Number of timestpes heating demand:      " + str(len(timesteps_hd_bd[1][0])))
    print(" ")
    print("Sum Appliances simulation period:        " + str(timesteps_app_bd.sum()))
    print("Sum heating emand simulation period:     " + str(timesteps_hd_bd.sum()))
    print(" ")

    return data
'''

'''
def calc_daily_load_factor(daily_loads):
    """Calculates load factor of a day

    Parameters
    ----------
    daily_loads : ??
        Load for every hours

    Returns
    -------
    load_factor : float
        Daily load factor
    """
    sum_load, max_load = 0, 0

    # Iterate hours to get max and average demand
    for i in daily_loads:
        h_load = ..
        sum_load += ..

        if h_load > max_load:
            max_load = h_load
    
    average_load = sum_load / len(daily_loads)

    load_factor = average_load / max_load
    

    return load_factor
'''

'''def add_to_data(data, pop_data_external): # Convert to array, store in data
    """ All all data received externally to main data dictionars. Convert also to array"""

    # Add population data
    reg_pop_array = {}
    for pop_year in pop_data_external:

        _t = pop_data_external[pop_year].items()
        l = []
        for i in _t:
            l.append(i)
        reg_pop_array[pop_year] = np.array(l, dtype=float)
    data['reg_pop_external_array'] = reg_pop_array
        #data['reg_pop_external'] = pop_data_external

        #print(data['reg_pop'][0])
        #print(isinstance(data['reg_pop'][0], int))
        #prin("kk")

    # Add other data
    return data
'''

'''
def get_load_curve_shapes(path_bd_e_load_profiles, day_type_lu, app_type_lu, glob_var, csv_temp_2015, hourly_gas_shape):
    """ Gets load curve shapes

    Parameters
    ----------
     : dict
        Dictionary containing paths

    Returns
    -------
    shape_app_elec : array
        Array with shape of electricity demand of appliances (full year)
    shape_hd_gas : array
        Array with shape of heating demand (full year)

    Info
    -------
    More Info
    """
    # Shape of base year for a full year for appliances (electricity) from HES data [%]
    shape_app_elec = shape_bd_app(path_bd_e_load_profiles, day_type_lu, app_type_lu, glob_var['base_year'])

    # Shape of base year for a full year for heating demand derived from XX [%]
    shape_hd_gas = shape_bd_hd(csv_temp_2015, hourly_gas_shape)

    return  shape_app_elec, shape_hd_gas
'''

'''def add_demand_result_dict(fuel_type, e_app_bd, fuel_type_lu, reg_pop, timesteps, result_dict, timesteps_own_selection):
    """Add data to wrapper timesteps

    """

    # Iteratue fuels
    for _ftyp in range(len(fuel_type_lu)):

        if _ftyp is not fuel_type: # IF other fueltype
            continue

        for region_nr in range(len(reg_pop)):
            year_hour = 0
            for timestep in timesteps: #Iterate over timesteps of full year
                timestep_id = str(timestep)
                _yearday = int(timestep.split("_")[0])   # Yearday
                _h = int(timestep.split("_")[1])         # Hour
                #start_period, end_period = timesteps[timestep]['start'], timesteps[timestep]['end']

                # Assign correct data from selection
                # Get season
                _season = get_season_yearday(_yearday)

                # Get daytype
                _yeardayReal = _yearday + 1 #Plus one from python
                date_from_yearday = datetime.datetime.strptime('2015 ' + str(_yeardayReal), '%Y %j')
                daytype = get_weekday_type(date_from_yearday)
                #daytype = 1

                # Get position in own timesteps
                hour_own_container = year_hour - _yearday * 24 #Hour of the day
                day_own_container_position = get_own_position(daytype, _season, hour_own_container, timesteps_own_selection) # AS input should
                #day_own_container_position = 1
                #print("day_own_container: " + str(day_own_container))

                #result_array[fuel_type][region_nr][timestep_id] = e_app_bd[fuel_elec][region_nr][_h].sum() # List with data out
                #result_dict[fuel_type][region_nr][timestep_id] = e_app_bd[fuel_elec][region_nr][_yearday][_h].sum()

                # DUMMY DATA
                #print("...---...")
                #print(fuel_type)
                #print(region_nr)
                #print(day_own_container)
                #print(_h) # Is missing!
                #print("EE:G " + str(e_app_bd[fuel_type][region_nr][day_own_container]))
                #print("---")
                result_dict[fuel_type][region_nr][timestep_id] = e_app_bd[fuel_type][region_nr][day_own_container_position].sum()  # Problem: Timesteps in are in fuel, region, TIMESTEP, appliances, hours
                year_hour += 1

    return result_dict
'''

'''def create_timesteps_app(fuel_type, date_list, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu, timestep_dates):
    """Creates the timesteps for which the energy demand of the appliances is calculated.
    Then base energy demand is added for each timestep read in from yearly demand aray.

    Parameters
    ----------
    fuel_type : int
        Fuel type
    date_list : list
        Contaings lists with start and end dates
    bd_app_elec : list
        Base demand applications (electricity)
    reg_lu : list
        Region look-up table
    fuel_type_lu : list
        Fuel type look-up table
        ...

    Returns
    -------
    data_timesteps_elec : array
        Timesteps containing appliances electricity data
            regions
                fuel_type
                    timesteps
                        hours
                            applications
    Notes
    -----

    """

    # Nuber of timesteps containing all days and hours
    timesteps = range(len(timestep_dates))

    # Initialise simulation array
    h_XX = 1 # BEcause for every timstep only one hozrs
    data_timesteps_elec = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), h_XX, len(app_type_lu)), dtype=float)
    #data_timesteps_elec = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), len(hours), len(app_type_lu)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lu)):
        cnt_h = 0

        for t_step in timesteps:

            # Get appliances demand of region for every date of timeperiod
            _info = timestep_dates[t_step].timetuple() # Get date
            yearday_python = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

            # Collect absolute data from
            #print("Add data to timstep container:    Timestep " + str(t_step) + str(" cnt_h: ") + str(cnt_h) + str("  Region_Nr") + str(reg_nr) + str("  Yearday") + str(yearday_python) + ("   ") + str(bd_app_elec[fuel_type][reg_nr][yearday_python][:,cnt_h].sum()))
            #data_timesteps_elec[fuel_type][reg_nr][t_step][:, cnt_h] = bd_app_elec[fuel_type][reg_nr][yearday_python][:, cnt_h] # Iterate over roew
            #print("A:  + " + str(data_timesteps_elec[fuel_type][reg_nr][t_step])) #[cnt_h]))
            #print("B:  + " + str(bd_app_elec[fuel_type][reg_nr][yearday_python][cnt_h]))

            #print(data_timesteps_elec[fuel_type][reg_nr][t_step].shape)
            #print(bd_app_elec[fuel_type][reg_nr][yearday_python][cnt_h].shape)
            data_timesteps_elec[fuel_type][reg_nr][t_step] = bd_app_elec[fuel_type][reg_nr][yearday_python][cnt_h] # Iterate over roew #TODO CHECK
            #print(data_timesteps_elec[fuel_type][reg_nr][t_step][cnt_h])
            #print(data_timesteps_elec[fuel_type][reg_nr][t_step])

            cnt_h += 1
            if cnt_h == 23:
                cnt_h = 0

    return data_timesteps_elec
'''
'''
def create_timesteps_hd(fuel_type, date_list, bd_hd_gas, reg_lu, fuel_type_lu, timestep_dates): # TODO: HIER GIBTS NOCH ERROR
    """This function creates the simulation time steps for which the heating energy is calculated.
    Then it selects energy demand from the yearl list for the simulation period.

    Parameters
    ----------
    date_list : list
        List containing selection of dates the simulation should run
    bd_hd_gas :
        Base demand heating (gas)
    reg_lu : array
        Region look-up table
    fuel_type_lu : array
        Fuel type look-up table

    Returns
    -------
    data_timesteps_hd_gas :
        Returns a nested dictionary for energy supply model. (fueltype/region/timeID)


        -data_timesteps_elec    Timesteps containing appliances electricity data
            regions
                fuel_type
                    timesteps
                        applications
                            hours
    Notes
    -----
    notes
    """
    # Region
    hours = range(24)

    # Number of timesteps
    timesteps = range(len(timestep_dates))

    # Initialise simulation array
    data_timesteps_hd_gas = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), len(hours)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lu)):

        cnt_h = 0
        for t_step in timesteps:

            # Get appliances demand of region for every date of timeperiod
            _info = timestep_dates[t_step].timetuple() # Get date
            yearday_python = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

            #print("DAY SN: " + str(yearday_python) + str("  ") + str(sum(bd_hd_gas[fuel_type][reg_nr][yearday_python])))

            # Get data and copy hour
            data_timesteps_hd_gas[fuel_type][reg_nr][t_step][cnt_h] = bd_hd_gas[fuel_type][reg_nr][yearday_python][cnt_h]

            cnt_h += 1
            if cnt_h == 23:
                cnt_h = 0

    return data_timesteps_hd_gas
'''