"""Function which are used in multiple scripts
"""
import os
import csv
from datetime import date
from datetime import timedelta
import json
import numpy as np

def create_txt_shapes(
        end_use,
        path_txt_shapes,
        shape_peak_dh,
        shape_non_peak_y_dh,
        shape_peak_yd_factor,
        shape_non_peak_yd
    ):
    """Function collecting functions to write out txt files
    """

    def jason_shape_peak_dh(input_array, outfile_path):
        """Wrte to txt. Array with shape: (24,)
        """
        np_dict = dict(enumerate(input_array))
        with open(outfile_path, 'w') as outfile:
            json.dump(np_dict, outfile)

    def jason_shape_non_peak_y_dh(input_array, outfile_path):
        """Wrte to txt. Array with shape: (365, 24)
        """
        out_dict = {}
        for k, row in enumerate(input_array):
            out_dict[k] = dict(enumerate(row))
        with open(outfile_path, 'w') as outfile:
            json.dump(out_dict, outfile)

    def jason_shape_peak_yd_factor(input_array, outfile_path):
        """Wrte to txt. Array with shape: ()
        """
        with open(outfile_path, 'w') as outfile:
            json.dump(input_array, outfile)

    def jason_shape_non_peak_yd(input_array, outfile_path):
        """Wrte to txt. Array with shape: (365)"""
        out_dict = {}
        for k, row in enumerate(input_array):
            out_dict[k] = row
        with open(outfile_path, 'w') as outfile:
            json.dump(out_dict, outfile)

    # Main function
    jason_shape_peak_dh(
        shape_peak_dh,
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt'))
        )
    jason_shape_non_peak_y_dh(
        shape_non_peak_y_dh, os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
    jason_shape_peak_yd_factor(
        shape_peak_yd_factor, os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
    jason_shape_non_peak_yd(
        shape_non_peak_yd, os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')))

    return

def fullyear_dates(start, end):
    """Calculates all dates between a star and end date.

    Parameters
    ----------
    start : date
        Start date
    end : date
        End date

    Returns
    -------
    list_dates : list
        A list with all daily dates
    """
    list_dates = []
    span = end - start
    for day in range(span.days + 1):
        list_dates.append(start + timedelta(days=day))

    return list_dates

def read_assumption_sim_param(path_to_csv):
    """Read assumptions from dict

    Parameters
    ----------
    path_to_csv : str
        Path to csv file with info

    Return
    -----
    assumptions : dict
        Assumptions
    """
    assumptions = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(csvfile) # Skip headers

        for row in read_lines:
            try:
                assumptions[str(row[0])] = float(row[1])
            except ValueError:
                assumptions[str(row[0])] = None

    # Redefine sim_period_yrs
    assumptions['sim_period'] = range(
        int(assumptions['base_yr']),
        int(assumptions['end_yr']) + 1,
        int(assumptions['sim_years_intervall'])
        )

    # Redefine sim_period_yrs
    assumptions['list_dates'] = fullyear_dates(
        start=date(int(assumptions['base_yr']), 1, 1),
        end=date(int(assumptions['base_yr']), 12, 31))

    return assumptions

def abs_to_rel(absolute_array):
    """Convert absolute numbers in an array to relative

    Parameters
    ----------
    absolute_array : array
        Contains absolute numbers in it

    Returns
    -------
    relative_array : array
        Contains relative numbers

    Note
    ----
    - If the total sum is zero, return an array with zeros and raise a warning
    """
    try:
        relative_array = (1 / np.sum(absolute_array)) * absolute_array
        relative_array[np.isnan(relative_array)] = 0
    except ZeroDivisionError:
        # If the total sum is zero, return same array
        relative_array = absolute_array

    return relative_array

def get_weekday_type(date_to_test):
    """Gets the weekday of a date

    Parameters
    ----------
    date_to_test : date
        Date of a day in ayear

    Returns
    -------
    daytype : str
        holiday or working day

    Note
    ----
    Bank holidays are defined for the year 2002 - 2015. The whole week of christmas
    is defined as a bank holiday

    Info
    -----
    timetuple attributes:
        tm_year
        tm_mon
        tm_mday
        tm_hour
        tm_min
        tm_sec
        tm_wday
        tm_yday
        tm_isdst
    """
    weekday = date_to_test.timetuple().tm_wday
    year = date_to_test.timetuple().tm_year

    if year == 2015:
        bank_holidays = [
            date(2015, 1, 1),
            date(2015, 4, 3),
            date(2015, 4, 6),
            date(2015, 5, 4),
            date(2015, 5, 25),
            date(2015, 8, 31),
            date(2015, 12, 25),
            date(2015, 12, 28),
            date(2015, 12, 29),
            date(2015, 12, 30),
            date(2015, 12, 31)]
    elif year == 2014:
        bank_holidays = [
            date(2014, 1, 1),
            date(2014, 4, 18),
            date(2014, 4, 21),
            date(2014, 5, 5),
            date(2014, 5, 26),
            date(2014, 8, 25),
            date(2014, 12, 25),
            date(2014, 12, 26),
            date(2014, 12, 27),
            date(2014, 12, 28),
            date(2014, 12, 29),
            date(2014, 12, 30),
            date(2014, 12, 31)]
    elif year == 2013:
        bank_holidays = [
            date(2013, 1, 1),
            date(2013, 4, 29),
            date(2013, 4, 1),
            date(2013, 5, 6),
            date(2013, 5, 27),
            date(2013, 8, 26),
            date(2013, 12, 25),
            date(2013, 12, 26),
            date(2013, 12, 27),
            date(2013, 12, 28),
            date(2013, 12, 29),
            date(2013, 12, 30),
            date(2013, 12, 31)]
    elif year == 2012:
        bank_holidays = [
            date(2012, 1, 1),
            date(2012, 1, 2),
            date(2012, 4, 6),
            date(2012, 4, 9),
            date(2012, 5, 7),
            date(2012, 6, 4),
            date(2012, 6, 7),
            date(2012, 8, 27),
            date(2012, 12, 25),
            date(2012, 12, 26),
            date(2012, 12, 27),
            date(2012, 12, 28),
            date(2012, 12, 29),
            date(2012, 12, 30),
            date(2012, 12, 31)]
    elif year == 2011:
        bank_holidays = [
            date(2011, 1, 1),
            date(2011, 1, 2),
            date(2011, 1, 3),
            date(2011, 4, 22),
            date(2011, 4, 25),
            date(2011, 4, 29),
            date(2011, 5, 2),
            date(2011, 5, 30),
            date(2011, 8, 29),
            date(2011, 12, 25),
            date(2011, 12, 26),
            date(2011, 12, 27),
            date(2011, 12, 28),
            date(2011, 12, 29),
            date(2011, 12, 30),
            date(2011, 12, 31)]
    elif year == 2010:
        bank_holidays = [
            date(2010, 1, 1),
            date(2010, 4, 2),
            date(2010, 4, 5),
            date(2010, 5, 3),
            date(2010, 5, 31),
            date(2010, 8, 30),
            date(2010, 12, 25),
            date(2010, 12, 26),
            date(2010, 12, 27),
            date(2010, 12, 28),
            date(2010, 12, 29),
            date(2010, 12, 30),
            date(2010, 12, 31)]
    elif year == 2009:
        bank_holidays = [
            date(2009, 1, 1),
            date(2009, 4, 10),
            date(2009, 4, 13),
            date(2009, 5, 4),
            date(2009, 5, 25),
            date(2009, 8, 31),
            date(2009, 12, 25),
            date(2009, 12, 26),
            date(2009, 12, 27),
            date(2009, 12, 28),
            date(2009, 12, 29),
            date(2009, 12, 30)]
    elif year == 2008:
        bank_holidays = [
            date(2008, 1, 1),
            date(2008, 4, 21),
            date(2008, 4, 24),
            date(2008, 5, 5),
            date(2008, 5, 26),
            date(2008, 8, 25),
            date(2008, 12, 25),
            date(2008, 12, 26),
            date(2008, 12, 27),
            date(2008, 12, 28),
            date(2008, 12, 29),
            date(2008, 12, 30)]
    elif year == 2007:
        bank_holidays = [
            date(2007, 1, 1),
            date(2007, 4, 6),
            date(2007, 4, 9),
            date(2007, 5, 7),
            date(2007, 5, 28),
            date(2007, 8, 27),
            date(2007, 12, 25),
            date(2007, 12, 26),
            date(2007, 12, 27),
            date(2007, 12, 28),
            date(2007, 12, 29),
            date(2007, 12, 30)]
    elif year == 2006:
        bank_holidays = [
            date(2006, 1, 2),
            date(2006, 4, 14),
            date(2006, 4, 17),
            date(2006, 5, 1),
            date(2006, 5, 29),
            date(2006, 8, 28),
            date(2006, 12, 25),
            date(2006, 12, 26),
            date(2006, 12, 27),
            date(2006, 12, 28),
            date(2006, 12, 29),
            date(2006, 12, 30)]
    elif year == 2005:
        bank_holidays = [
            date(2005, 1, 1),
            date(2005, 1, 2),
            date(2005, 1, 3),
            date(2005, 3, 25),
            date(2005, 3, 28),
            date(2005, 5, 2),
            date(2005, 5, 30),
            date(2005, 8, 29),
            date(2005, 12, 25),
            date(2005, 12, 26),
            date(2005, 12, 27),
            date(2005, 12, 28),
            date(2005, 12, 29),
            date(2005, 12, 30)]
    elif year == 2004:
        bank_holidays = [
            date(2004, 1, 1),
            date(2004, 4, 9),
            date(2004, 4, 12),
            date(2004, 4, 25),
            date(2004, 5, 3),
            date(2004, 5, 31),
            date(2004, 8, 30),
            date(2004, 12, 25),
            date(2004, 12, 26),
            date(2004, 12, 27),
            date(2004, 12, 28),
            date(2004, 12, 29),
            date(2004, 12, 30)]
    elif year == 2003:
        bank_holidays = [
            date(2003, 1, 1),
            date(2003, 4, 21),
            date(2003, 5, 5),
            date(2003, 5, 26),
            date(2003, 8, 25),
            date(2003, 12, 25),
            date(2003, 12, 26),
            date(2003, 12, 27),
            date(2003, 12, 28),
            date(2003, 12, 29),
            date(2003, 12, 30)]
    elif year == 2002:
        bank_holidays = [
            date(2002, 1, 1),
            date(2002, 4, 1),
            date(2002, 5, 6),
            date(2002, 6, 3),
            date(2002, 6, 4),
            date(2002, 8, 26),
            date(2002, 12, 25),
            date(2002, 12, 26),
            date(2002, 12, 27),
            date(2002, 12, 28),
            date(2002, 12, 29),
            date(2002, 12, 30)]
    else:
        bank_holidays = []

    if weekday == 5 or weekday == 6:
        return 'holiday'
    else:
        if date_to_test in bank_holidays:
            return 'holiday'
        else:
            return 'working_day'
    