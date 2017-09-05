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