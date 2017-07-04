"""Functions related to dates
"""
from datetime import date
from datetime import timedelta as td

def convert_date_to_yearday(year, month, day):
    """Gets the yearday (julian year day) of a year minus one to correct because of python iteration
    TESTED_PYTEST

    Parameters
    ----------
    date_base_yr : int
        Year
    date_base_yr : int
        Month
    day : int
        Day

    Example
    -------
    5. January 2015 --> Day nr 5 in year --> -1 because of python --> Out: 4
    """
    date_y = date(year, month, day)
    yearday = date_y.timetuple().tm_yday - 1 #: correct because of python iterations

    return yearday

def convert_yearday_to_date(year, yearday_python):
    """Gets the yearday of a year minus one to correct because of python iteration
    TESTED_PYTEST

    Parameters
    ----------
    year : int
        Year
    yearday_python : int
        Yearday - 1
    """
    date_first_jan = date(year, 1, 1)
    date_new = date_first_jan + td(yearday_python)

    return date_new

def get_weekday_type(date_from_yearday):
    """Gets the weekday of a date
    TESTED_PYTEST
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

    weekday = date_from_yearday.timetuple().tm_wday

    if weekday == 5 or weekday == 6:
        return 1 # Holiday
    else:
        return 0 # Working day

def fullyear_dates(start=None, end=None):
    """Calculates all dates between a star and end date.
    TESTED_PYTEST

    Parameters
    ----------
    start : date
        Start date
    end : date
        end date

    Returns
    -------
    list_dates : list
        A list with dates
    """
    list_dates = []
    span = end - start
    for day in range(span.days + 1):
        list_dates.append(start + td(days=day))

    return list(list_dates)

'''def timesteps_full_year(base_yr):
    """A list is generated from the first hour of the base year to the last hour of teh base year

    This function generates a single list from a list with
    containg start and end dates of the base year

    Parameters
    ----------
    base_yr : int
        Year used to generate timesteps.

    Returns
    -------
    timesteps : dict
        Contains every yearday and the start and end time_ID

    Note
    ----
    The base year must be identical to the input energy data

    """
    # List with all dates of the base year
    list_dates = fullyear_dates(start=date(base_yr, 1, 1), end=date(base_yr, 12, 31)) # List with every date in a year

    timesteps = {}

    #Add to list
    for day_date in list_dates:
        yearday = day_date.timetuple().tm_yday - 1 # -1 because in _info yearday 1: 1. Jan    ((tm_year=2015, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=-1))

        # Iterate hours
        for h_id in range(24):
            start_period = "P{}H".format(yearday * 24 + h_id) # Start intervall ID
            end_period = "P{}H".format(yearday * 24 + h_id + 1) # End intervall ID
            yearday_h_id = str(str(yearday) + str("_") + str(h_id)) # Timestep ID

            # Add to dict
            timesteps[yearday_h_id] = {'start': start_period, 'end': end_period}

    return timesteps

'''