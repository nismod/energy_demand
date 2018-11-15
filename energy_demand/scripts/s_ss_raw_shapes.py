"""File to read in all service sector related data
"""
import os
import sys
import csv
from datetime import date
import numpy as np
from energy_demand.read_write import read_data
from energy_demand.read_write import write_data
from energy_demand.basic import date_prop
from energy_demand.profiles import load_profile

def dict_init_carbon_trust():
    """Helper function to initialise dict
    """
    carbon_trust_raw = {}
    for day in range(365):
        day_dict_h = {k: [] for k in range(24)}
        carbon_trust_raw[day] = day_dict_h

    return carbon_trust_raw

def read_raw_carbon_trust_data(folder_path):
    """Read in raw carbon trust dataset (used for service sector)

    Arguments
    ----------
    foder_path : string
        Path to folder with stored csv files

    Returns
    -------
    load_shape_y_dh : array
        Load shape for every day (tot sum 365) ((365, 24))
    load_peak_shape_dh : array
        Peak loadshape for peak day ((24))
    shape_non_peak_yd : array
        Yh load profile ((365))

    Note
    -----
    1. Get gas peak day load shape (the max daily demand can be taken from weather data,
       the daily shape however is not provided by samson)
    2. Iterate individual files which are about a year (even though gaps exist)
    3. Select those day with the maximum load
    4. Get the hourly shape of this day
    5. Calculate total demand of every day
    6. Assign percentag of total daily demand to each hour
    """
    def initialise_main_dict():
        """Helper function to initialise dict
        """
        out_dict_av = {'working_day': {}, 'holiday': {}}
        for dtype in out_dict_av:
            month_dict = {}
            for month in range(12):
                month_dict[month] = {k: [] for k in range(24)}
            out_dict_av[dtype] = month_dict
        return out_dict_av

    def initialise_out_dict_av():
        """Helper function to initialise dict"""
        out_dict_av = {'working_day': {}, 'holiday': {}}
        for dtype in out_dict_av:
            month_dict = {}
            for month in range(12):
                month_dict[month] = {k: 0 for k in range(24)}
            out_dict_av[dtype] = month_dict
        return out_dict_av

    # Get all files in folder
    all_csv_in_folder = os.listdir(folder_path)
    main_dict = initialise_main_dict()
    carbon_trust_raw = dict_init_carbon_trust()

    nr_of_line_entries = 0
    dict_max_dh_shape = {}

    # Itreatu folder with csv files
    for path_csv_file in all_csv_in_folder:
        path_csv_file = os.path.join(folder_path, path_csv_file)

        # Read csv file
        with open(path_csv_file, 'r') as csv_file:
            read_lines = csv.reader(csv_file, delimiter=',')
            _headings = next(read_lines)
            max_d_demand = 0 # Used for searching maximum

            # Count number of lines in CSV file
            row_data = []
            for count_row, row in enumerate(read_lines):
                row_data.append(row)
            #print("Number of lines in csv file: " + str(count_row))

            # Calc yearly demand based on one year data measurements
            if count_row > 365: # if more than one year is in csv file
                #print("FILE covers a full year---------------------------")

                # Test if file has correct form and not more entries than 48 half-hourly entries
                for day, row in enumerate(row_data):
                    if len(row) != 49:
                        continue # Skip row

                    # Use only data of one year
                    if day > 365:
                        continue

                    load_shape_dh = np.zeros((24), dtype="float")

                    row[1:] = map(float, row[1:]) # Convert all values except date into float values
                    daily_sum = sum(row[1:]) # Total daily sum
                    nr_of_line_entries += 1 # Nr of lines added
                    day = int(row[0].split("/")[0])
                    month = int(row[0].split("/")[1])
                    year = int(row[0].split("/")[2])

                    # Redefine yearday to another year and skip 28. of Feb.
                    if date_prop.is_leap_year(int(year)) is True:
                        year = year + 1 # Shift whole dataset to another year
                        if month == 2 and day == 29:
                            continue #skip leap day

                    date_row = date(year, month, day)
                    daytype = date_prop.get_weekday_type(date_row)

                    yearday_python = date_row.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
                    month_python = month - 1 # Month Python

                    h_day, cnt, control_sum = 0, 0, 0

                    # -----------------------------------------------
                    # Iterate half hour data and summarise to hourly
                    # -----------------------------------------------
                    for data_h in row[1:]:  # Skip first date row in csv file
                        cnt += 1
                        if cnt == 2:
                            demand_h = first_data_h + data_h
                            control_sum += abs(demand_h)

                            # Add demand
                            carbon_trust_raw[yearday_python][h_day].append(demand_h)

                            # Store demand according to daytype (aggregated by doing so)
                            main_dict[daytype][month_python][h_day].append(demand_h)

                            if daily_sum == 0: # Skip row if no demand of the day
                                load_shape_dh[h_day] = 0
                                continue
                            else:
                                load_shape_dh[h_day] = demand_h / daily_sum

                            cnt = 0
                            h_day += 1

                        # Value lagging behind one iteration
                        first_data_h = data_h

                    # Test if this is the day with maximum demand of this CSV file
                    if daily_sum >= max_d_demand:
                        max_d_demand = daily_sum
                        max_dh_shape = load_shape_dh

                    # Check if 100 %
                    np.testing.assert_almost_equal(control_sum, daily_sum, decimal=7, err_msg="")

                # Add load shape of maximum day in csv file
                dict_max_dh_shape[path_csv_file] = max_dh_shape

    # ---------------
    # Data processing
    # ---------------
    # --Average average maxium peak dh of every csv file
    load_peak_average_dh = np.zeros((24), dtype="float")
    for peak_shape_dh in dict_max_dh_shape.values():
        load_peak_average_dh += peak_shape_dh
    load_peak_shape_dh = load_peak_average_dh / len(dict_max_dh_shape)

    # -----------------------------------------------
    # Calculate average load shapes for every month
    # -----------------------------------------------
    out_dict_av = initialise_out_dict_av()

    for daytype in main_dict:
        for month in main_dict[daytype]:
            for hour in main_dict[daytype][month]:
                nr_of_entries = len(main_dict[daytype][month][hour])
                if nr_of_entries != 0:
                    out_dict_av[daytype][month][hour] = sum(main_dict[daytype][month][hour]) / nr_of_entries

    # ----------------------------------------------------------
    # Distribute raw data into base year depending on daytype
    # ----------------------------------------------------------
    year_data = assign_data_to_year(out_dict_av, 2015)

    # Calculate yearly sum
    yearly_demand = np.sum(year_data)

    # Create load_shape_dh
    load_shape_y_dh = np.zeros((365, 24), dtype="float")
    for day, dh_values in enumerate(year_data):
        load_shape_y_dh[day] = load_profile.abs_to_rel(dh_values) # daily shape

    np.testing.assert_almost_equal(np.sum(load_shape_y_dh), 365, decimal=2, err_msg="")

    # Calculate shape_non_peak_yd
    shape_non_peak_yd = np.zeros((365), dtype="float")
    for yearday, carbon_trust_d in enumerate(year_data):
        shape_non_peak_yd[yearday] = np.sum(carbon_trust_d)

    shape_non_peak_yd = shape_non_peak_yd / yearly_demand

    np.testing.assert_almost_equal(np.sum(shape_non_peak_yd), 1, decimal=2, err_msg="")

    return load_shape_y_dh, load_peak_shape_dh, shape_non_peak_yd

def assign_data_to_year(carbon_trust_data, base_yr):
    """Fill every base year day with correct data

    Arguments
    ----------
    carbon_trust_data : data
        Raw data
    base_yr : int
        Base Year
    """
    shape_non_peak_y_dh = np.zeros((365, 24), dtype="float")

    # Create list with all dates of a whole year
    list_dates = date_prop.fullyear_dates(
        start=date(base_yr, 1, 1),
        end=date(base_yr, 12, 31))

    # Assign every date to the place in the array of the year
    for yearday in list_dates:
        month_python = yearday.timetuple().tm_mon - 1 # - 1 because in _info: Month 1 = Jan
        yearday_python = yearday.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
        daytype = date_prop.get_weekday_type(yearday)

        # Get day from HES raw data array
        _data = carbon_trust_data[daytype][month_python]

        # Add values to yearly
        _data = np.array(list(_data.items()))
        shape_non_peak_y_dh[yearday_python] = np.array(_data[:, 1], dtype="float")

    return shape_non_peak_y_dh

def run(paths, local_paths, lookups):
    """Function to run script
    """
    print("... start script %s", os.path.basename(__file__))
    _, ss_sectors, ss_enduses = read_data.read_fuel_ss(
        paths['ss_fuel_raw'],
        lookups['fueltypes_nr'])

    # Iterate sectors and read in shape
    for sector in ss_sectors:
        # Match electricity shapes for every sector
        # to correct folder with load profiles
        if sector == 'community_arts_leisure':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "Community")
        elif sector == 'education':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "Education")
        elif sector == 'emergency_services':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "_all_elec")
        elif sector == 'health':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "Health")
        elif sector == 'hospitality':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "_all_elec")
        elif sector == 'military':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "_all_elec")
        elif sector == 'offices':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "Offices")
        elif sector == 'retail':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "Retail")
        elif sector == 'storage':
            sector_folder_path_elec = os.path.join(
                local_paths['folder_raw_carbon_trust'], "_all_elec")
        else:
            raise Exception("Error: The sector {} could not be assigned".format(sector))

        # ------------------------------------------------------
        # Assign shape across enduse for service sector
        # ------------------------------------------------------
        for enduse in ss_enduses:
            print("Enduse service: %s in sector %s", enduse, sector)

            # Enduses
            enduses_mainly_gas = ['ss_water_heating', 'ss_space_heating', 'ss_other_gas']

            # Select shape depending on enduse
            if enduse in enduses_mainly_gas:
                folder_path = os.path.join(
                    local_paths['folder_raw_carbon_trust'],
                    "_all_gas")
            else:
                folder_path = sector_folder_path_elec

            # Read in shape from carbon trust metering trial dataset
            shape_non_peak_y_dh, load_peak_shape_dh, shape_non_peak_yd = read_raw_carbon_trust_data(
                folder_path)

            # Write shapes to txt
            joint_string_name = str(sector) + "__" + str(enduse)

            write_data.create_txt_shapes(
                joint_string_name,
                local_paths['ss_load_profile_txt'],
                load_peak_shape_dh,
                shape_non_peak_y_dh,
                shape_non_peak_yd)

    print("... finished script %s", os.path.basename(__file__))
    return
