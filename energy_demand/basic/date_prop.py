"""
Contains funtions related to handeling date and
time related functionality
"""
import numpy as np
from datetime import date
from datetime import timedelta
from energy_demand.basic import basic_functions

def convert_h_to_day_year_and_h(hour):
    """Convert a 8760 hour in a year
    to the yearday and hour of that day

    Input
    -----
    hour : int
        Hour of 8760 hours in a year

    Outputs
    -------
    day : int
        Pthon day of a year (0 == 1 day)
    day_h : int
        Python hour of day (0 == 1 hour)
    """
    day = basic_functions.round_down(int(hour / 24), 1)

    total_hours = day * 24

    day_h = hour - total_hours

    return day, day_h

def get_seasonal_weeks():
    """
    """
    '''winter_week = list(range(
        date_prop.date_to_yearday(year_to_model, 1, 12),
        date_prop.date_to_yearday(year_to_model, 1, 26))) #Jan
    spring_week = list(range(
        date_prop.date_to_yearday(year_to_model, 5, 11),
        date_prop.date_to_yearday(year_to_model, 5, 25))) #May
    summer_week = list(range(
        date_prop.date_to_yearday(year_to_model, 7, 13),
        date_prop.date_to_yearday(year_to_model, 7, 27))) #Jul
    autumn_week = list(range(
        date_prop.date_to_yearday(year_to_model, 10, 12),
        date_prop.date_to_yearday(year_to_model, 10, 26))) #Oct'''

    winter_week = list(range(
        date_to_yearday(2015, 1, 12), date_to_yearday(2015, 1, 19))) #Jan
    spring_week = list(range(
        date_to_yearday(2015, 5, 11), date_to_yearday(2015, 5, 18))) #May
    summer_week = list(range(
        date_to_yearday(2015, 7, 13), date_to_yearday(2015, 7, 20))) #Jul
    autumn_week = list(range(
        date_to_yearday(2015, 10, 12), date_to_yearday(2015, 10, 19))) #Oct

    return winter_week, spring_week, summer_week, autumn_week

def get_yeardays_daytype(year_to_model):
    """For yearday, daytype and date related
    properties

    Arguments
    ---------
    year_to_model : int
        Year to get daytpes

    Returns
    -------
    model_yeardays_daytype : dict
        Dict with description for every day if working or holiday
    yeardays_month : dict
        For every month the yeardays (as int) are provided
    yeardays_month_days : dict
        For every month, all dates are provided as date objects
    
    Note
    ----
    Only works with years with 365 days so far
    """
    # --------------------------------------
    # Calculate for all yeardays the daytype of base year
    # --------------------------------------
    list_dates = fullyear_dates(
        start=date(year_to_model, 1, 1),
        end=date(year_to_model, 12, 31))

    model_yeardays_daytype = np.array(['workday']*365)

    # Take respectve daily fuel curve depending on weekday or weekend
    for array_day, date_yearday in enumerate(list_dates):
        daytype = get_weekday_type(date_yearday)
        if daytype == 'holiday':
            model_yeardays_daytype[array_day] = 'holiday'

    # Calculate month of dates
    yeardays_month_days = {}
    for i in range(12):
        yeardays_month_days[i] = []

    # Get month type of yearday for every day
    yeardays_month = []
    for yearday, date_object in enumerate(list_dates):
        month_yearday = date_object.timetuple().tm_mon - 1
        yeardays_month.append(month_yearday)
        yeardays_month_days[month_yearday].append(yearday)

    return model_yeardays_daytype, yeardays_month, yeardays_month_days

def get_season(year_to_model):
    """

    Arguments
    ---------
    year_to_model : int
        Year which is modelled
    """
    # Full meteorological seasons
    seasons = {}
    seasons['winter'] = list(
        range(
            date_to_yearday(year_to_model, 12, 1),
            date_to_yearday(year_to_model, 12, 31))) + list(
                range(
                    date_to_yearday(year_to_model, 1, 1),
                    date_to_yearday(year_to_model, 2, 28)))
    seasons['spring'] = list(range(
        date_to_yearday(year_to_model, 3, 1),
        date_to_yearday(year_to_model, 5, 31)))
    seasons['summer'] = list(range(
        date_to_yearday(year_to_model, 6, 1),
        date_to_yearday(year_to_model, 8, 31)))
    seasons['autumn'] = list(range(
        date_to_yearday(year_to_model, 9, 1),
        date_to_yearday(year_to_model, 11, 30)))

    return seasons

def get_month_from_yeraday(year, yearday):
    """Get python month from yearday

    Arguments
    ----------
    year : int
        year
    yearday : int
        yearday

    Return
    ------
    python_month : int
        Python month (0 == 1)
    """
    date_year = yearday_to_date(int(year), int(yearday))
    python_month = date_year.timetuple().tm_mon - 1

    return python_month

def is_leap_year(year):
    """Determine whether a year is a leap year"""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def date_to_yearday(year, month, day):
    """Gets the yearday (julian year day) of a year minus one to correct because of python iteration

    Arguments
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

def yearday_to_date(year, yearday_python):
    """Gets the yearday of a year minus one to correct
    because of python iteration

    Arguments
    ----------
    year : int
        Year
    yearday_python : int
        Yearday - 1

    Returns
    -------
    date_new : date
        Date
    """
    date_new = date(year, 1, 1) + timedelta(yearday_python)

    return date_new

def get_weekday_type(date_to_test):
    """Gets the weekday of a date

    Arguments
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

    if weekday == 5 or weekday == 6:
        return 'holiday'
    else:
        year = date_to_test.timetuple().tm_year
        if year == 2015:
            bank_holidays = [
                date(2015, 1, 1),
                date(2015, 1, 2),
                date(2015, 4, 3),
                date(2015, 4, 6),
                date(2015, 5, 4),
                date(2015, 5, 25),
                date(2015, 8, 31),
                date(2015, 12, 24),
                date(2015, 12, 25),
                date(2015, 12, 26),
                date(2015, 12, 27),
                date(2015, 12, 28),
                date(2015, 12, 29),
                date(2015, 12, 30),
                date(2015, 12, 31)]
        elif year == 2014:
            bank_holidays = [
                date(2014, 1, 1),
                date(2014, 1, 2),
                date(2014, 4, 18),
                date(2014, 4, 21),
                date(2014, 5, 5),
                date(2014, 5, 26),
                date(2014, 8, 25),
                date(2014, 12, 24),
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
                date(2013, 1, 2),
                date(2013, 4, 29),
                date(2013, 4, 1),
                date(2013, 5, 6),
                date(2013, 5, 27),
                date(2013, 8, 26),
                date(2013, 12, 24),
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
                date(2012, 12, 24),
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
                date(2011, 12, 24),
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
                date(2010, 12, 24),
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
                date(2009, 12, 24),
                date(2009, 12, 25),
                date(2009, 12, 26),
                date(2009, 12, 27),
                date(2009, 12, 28),
                date(2009, 12, 29),
                date(2009, 12, 30),
                date(2009, 12, 31)]
        elif year == 2008:
            bank_holidays = [
                date(2008, 1, 1),
                date(2008, 4, 21),
                date(2008, 4, 24),
                date(2008, 5, 5),
                date(2008, 5, 26),
                date(2008, 8, 25),
                date(2008, 12, 24),
                date(2008, 12, 25),
                date(2008, 12, 26),
                date(2008, 12, 27),
                date(2008, 12, 28),
                date(2008, 12, 29),
                date(2008, 12, 30),
                date(2008, 12, 31)]
        elif year == 2007:
            bank_holidays = [
                date(2007, 1, 1),
                date(2007, 4, 6),
                date(2007, 4, 9),
                date(2007, 5, 7),
                date(2007, 5, 28),
                date(2007, 8, 27),
                date(2007, 12, 24),
                date(2007, 12, 25),
                date(2007, 12, 26),
                date(2007, 12, 27),
                date(2007, 12, 28),
                date(2007, 12, 29),
                date(2007, 12, 30),
                date(2007, 12, 31)]
        elif year == 2006:
            bank_holidays = [
                date(2006, 1, 2),
                date(2006, 4, 14),
                date(2006, 4, 17),
                date(2006, 5, 1),
                date(2006, 5, 29),
                date(2006, 8, 28),
                date(2006, 12, 24),
                date(2006, 12, 25),
                date(2006, 12, 26),
                date(2006, 12, 27),
                date(2006, 12, 28),
                date(2006, 12, 29),
                date(2006, 12, 30),
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
                date(2005, 12, 24),
                date(2005, 12, 25),
                date(2005, 12, 26),
                date(2005, 12, 27),
                date(2005, 12, 28),
                date(2005, 12, 29),
                date(2005, 12, 30),
                date(2005, 12, 31)]
        elif year == 2004:
            bank_holidays = [
                date(2004, 1, 1),
                date(2004, 4, 9),
                date(2004, 4, 12),
                date(2004, 4, 25),
                date(2004, 5, 3),
                date(2004, 5, 31),
                date(2004, 8, 30),
                date(2004, 12, 24),
                date(2004, 12, 25),
                date(2004, 12, 26),
                date(2004, 12, 27),
                date(2004, 12, 28),
                date(2004, 12, 29),
                date(2004, 12, 30),
                date(2004, 12, 31)]
        elif year == 2003:
            bank_holidays = [
                date(2003, 1, 1),
                date(2003, 4, 21),
                date(2003, 5, 5),
                date(2003, 5, 26),
                date(2003, 8, 25),
                date(2003, 12, 24),
                date(2003, 12, 25),
                date(2003, 12, 26),
                date(2003, 12, 27),
                date(2003, 12, 28),
                date(2003, 12, 29),
                date(2003, 12, 30),
                date(2003, 12, 31)]
        elif year == 2002:
            bank_holidays = [
                date(2002, 1, 1),
                date(2002, 4, 1),
                date(2002, 5, 6),
                date(2002, 6, 3),
                date(2002, 6, 4),
                date(2002, 8, 26),
                date(2002, 12, 24),
                date(2002, 12, 25),
                date(2002, 12, 26),
                date(2002, 12, 27),
                date(2002, 12, 28),
                date(2002, 12, 29),
                date(2002, 12, 30),
                date(2002, 12, 31)]
        else:
            bank_holidays = []

        if date_to_test in bank_holidays:
            return 'holiday'
        else:
            return 'working_day'

def fullyear_dates(start, end):
    """Calculates all dates between a star and end date.
    The star and end date are included in the list.

    Arguments
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
 