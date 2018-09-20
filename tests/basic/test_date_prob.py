"""Testing functions ``basic`` ``date_prop``
"""
from datetime import date
from energy_demand.basic import date_prop

'''def test_get_dates_week_nr():
    """testing function
    """
    import datetime
    from isoweek import Week
    in_year = 2017
    week_nr = 33
    expected = [
        datetime.date(2017, 8, 14),
        datetime.date(2017, 8, 15),
        datetime.date(2017, 8, 16),
        datetime.date(2017, 8, 17),
        datetime.date(2017, 8, 18),
        datetime.date(2017, 8, 19),
        datetime.date(2017, 8, 20)
    ]

    # call function
    out_value = date_prop.get_dates_week_nr(in_year, week_nr)

    assert out_value == expected
'''

def test_get_season():
    """testing
    """
    result = date_prop.get_season(year_to_model=2018)

    assert result['summer'][0] == 151 #2018 regular year, first of june julianday - 1 for python
    assert result['autumn'][0] == 243 #2018 regular year, first of june julianday - 1 for python
    assert result['winter'][0] == 334 #2018 regular year, first of june julianday - 1 for python
    assert result['spring'][0] == 59 #2018 regular year, first of june julianday - 1 for python

def test_get_yeardays_daytype():
    """testing
    """
    model_yeardays_daytype, yeardays_month, yeardays_month_days = date_prop.get_yeardays_daytype(
        year_to_model=2018)

    assert model_yeardays_daytype[0] == 'workday'
    assert model_yeardays_daytype[1] == 'workday'  
    assert model_yeardays_daytype[2] == 'workday'
    assert model_yeardays_daytype[3] == 'workday' 
    assert model_yeardays_daytype[4] == 'workday'
    assert model_yeardays_daytype[5] == 'holiday'
    assert model_yeardays_daytype[6] == 'holiday'

def test_get_month_from_yeraday():
    """testing
    """

    result = date_prop.get_month_from_yeraday(year=2015, yearday=37)
    expected = 1 #Feb
    assert result == expected

def test_date_to_yearday():
    """Testing
    """
    in_year = 2015
    in_month = 6
    in_day = 13
    expected = 164 - 1

    # call function
    out_value = date_prop.date_to_yearday(in_year, in_month, in_day)

    assert out_value == expected

def test_yearday_to_date():
    """Testing
    """
    in_year = 2015
    in_month = 6
    in_day = 13
    in_yearday = 163
    expected = date(2015, in_month, in_day)

    # call function
    out_value = date_prop.yearday_to_date(in_year, in_yearday)

    assert out_value == expected

def test_fullyear_dates():
    """Testing
    """
    start_date = date(2015, 1, 1)
    end_date = date(2015, 1, 4)
    expected = [
        date(2015, 1, 1),
        date(2015, 1, 2),
        date(2015, 1, 3),
        date(2015, 1, 4)]

    # call function
    out_value = date_prop.fullyear_dates(start_date, end_date)

    assert out_value == expected

def test_get_weekday_type():
    """Testing
    """
    date_to_test = date(2015, 4, 3)
    expected = 'holiday'

    # call function
    out_value = date_prop.get_weekday_type(date_to_test)

    assert out_value == expected

    date_to_test = date(2017, 9, 7)
    expected = 'working_day'

    # call function
    out_value = date_prop.get_weekday_type(date_to_test)

    assert out_value == expected

    date_to_test = date(2017, 9, 9)
    expected = 'holiday'

    # call function
    out_value = date_prop.get_weekday_type(date_to_test)

    assert out_value == expected

    # Test year
    date_to_test = date(2015, 4, 3)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2014, 4, 21)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected
    date_to_test = date(2013, 4, 1)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2012, 4, 9)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2011, 1, 2)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected
    
    date_to_test = date(2010, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected
    
    date_to_test = date(2009, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected
    
    date_to_test = date(2008, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected
    
    date_to_test = date(2007, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2006, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2005, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2004, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2003, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected

    date_to_test = date(2002, 12, 25)
    expected = 'holiday'
    out_value = date_prop.get_weekday_type(date_to_test)
    assert out_value == expected
