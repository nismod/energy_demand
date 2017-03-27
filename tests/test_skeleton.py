#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import pytest
import energy_demand.main_functions as mf
import energy_demand.building_stock_functions as bf
import energy_demand.building_stock_generator as bg
import energy_demand.national_dissaggregation as nd
from datetime import date
from datetime import timedelta as td
import numpy as np

from pytest import raises

# --------------Building STock generator
def test_raises_error_get_dwtype_dist():
    """ Test if the error is raised if wrong input data"""
    # in test value
    wrong_data = {'semi_detached': 20.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    in_value_2 = {'semi_detached': 20.0, 'terraced': 20, 'flat': 30, 'detached': 20, 'bungalow': 10}
    in_value_3 = {'base_year': 2015, 'current_year': 2016, 'end_year': 2050}

    with raises(AssertionError):
        bf.get_dwtype_dist(wrong_data, in_value_2, in_value_3)





# --------------Main_functions

def test_get_datetime_range():
    """Testing function"""
    start_date = date(2015, 1, 1)
    end_date = date(2015, 1, 2)

    expected = [date(2015, 1, 1), date(2015, 1, 2)]
    out = mf.get_datetime_range(start_date, end_date)

    assert out == expected



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


def test_apply_elasticity():
    """Calculate current demand based on demand elasticity"""

    in_value = np.array([[10.0], [20.0]])
    elasticity = -0.5
    price_base = 100
    price_curr = 80

    expected = -1 * (( -0.5 * ((100 - 80) / 100) * in_value) - in_value)

    # New current demand
    out_value = mf.apply_elasticity(in_value, elasticity, price_base, price_curr)

    np.testing.assert_array_equal(out_value, expected)



def test_convert_date_to_yearday():

    in_year = 2015
    in_month = 6
    in_day = 13
    expected = 164 - 1

    # call function
    out_value = mf.convert_date_to_yearday(in_year, in_month, in_day)

    assert out_value == expected


    
    

'''
def test_raises_error_disaggregate_base_demand_for_reg():
    """ Test if the error is raised"""

    data_ext = {'population': {2015: {0: 3000001, 1: 5300001, 2: 53000001}},
                     'glob_var': {'base_year': 2015,'end_year': 2020}}

    data = {'reg_lu': {0: 'WALES', 1: 'SCOTLAND', 2: 'ENGLAND'},'data_residential_by_fuel_end_uses': np.array([[0.],[0.],[ 1159.],[0.],[0.],[ 0.]])}

    reg_data_assump_disaggreg = {}

    # in test value
    wrong_data = {'semi_detached': 20.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    in_value_2 = {'semi_detached': 20.0, 'terraced': 20, 'flat': 30, 'detached': 20, 'bungalow': 10}
    in_value_3 = {'base_year': 2015, 'current_year': 2016, 'end_year': 2050}

    with raises(AssertionError):
        nd.disaggregate_base_demand_for_reg(data, reg_data_assump_disaggreg, data_ext)
'''

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
