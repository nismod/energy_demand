#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import energy_demand.main_functions as mf
from datetime import date
import numpy as np

# --------------Main_functions


def test_read_csv_dict():
    """Testing function"""

    # in test value
    in_value_1 = 'data/_test_data/test_csv.csv'

    expected = {15: {'test_value': 3}}

    # call function
    out_value = mf.read_csv_dict(in_value_1)

    assert out_value == expected

def test_read_csv_float():
    """Testing function"""

    # in test value
    in_value_1 = 'data/_test_data/test_csv.csv'

    expected = np.array([[float(15), float(3)]])

    # call function
    out_value = mf.read_csv_float(in_value_1)

    np.testing.assert_array_equal(out_value, expected)

def test_read_csv():
    """Testing function"""

    # in test value
    in_value_1 = 'data/_test_data/test_csv.csv'

    expected = np.array([[15, 3]])

    # call function
    out_value = mf.read_csv_float(in_value_1)

    # Raise assertion error if array are identical
    np.testing.assert_array_equal(out_value, expected)

def test_conversion_ktoe_gwh():
    """Testing function"""
    # in test value
    in_value = 10
    expected = in_value * 11.6300000

    # call function
    out_value = mf.conversion_ktoe_gwh(in_value)

    assert out_value == expected

def test_get_weekday_type():
    """Testing function"""
    # in test value

    in_value = date(2015, 1, 1)
    expected = 0

    # call function
    out_value = mf.get_weekday_type(in_value)

    assert out_value == expected


'''def test_timesteps_full_year():
    """Testing function"""

    # in test value
   
    expected = 0

    # call function
    out_value_1, out_value_1 = mf.timesteps_full_year(in_value)

    assert out_value == expected
'''
# ----
'''
def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
'''