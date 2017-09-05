#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------
# Testing file ``date_handling``
# -------------------------

import datetime
from datetime import date
from datetime import timedelta as td
import numpy as np
from pytest import raises
from energy_demand.basic import date_handling

'''
def test_get_dates_week_nr():
    """testing function
    """
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
    out_value = date_handling.get_dates_week_nr(in_year, week_nr)

    assert out_value == expected

'''

def test_convert_date_to_yearday():
    """Testing
    """
    in_year = 2015
    in_month = 6
    in_day = 13
    expected = 164 - 1

    # call function
    out_value = date_handling.convert_date_to_yearday(in_year, in_month, in_day)

    assert out_value == expected

def test_convert_yearday_to_date():
    """Testing
    """
    in_year = 2015
    in_month = 6
    in_day = 13
    in_yearday = 163
    expected = date(2015, in_month, in_day)

    # call function
    out_value = date_handling.convert_yearday_to_date(in_year, in_yearday)

    assert out_value == expected

def test_fullyear_dates():
    """Testing
    """
    start_date = date(2015, 1, 1)
    end_date =  date(2015, 1, 4)
    expected = [
        date(2015, 1, 1),
        date(2015, 1, 2),
        date(2015, 1, 3),
        date(2015, 1, 4)]

    # call function
    out_value = date_handling.fullyear_dates(start_date, end_date)

    assert out_value == expected
