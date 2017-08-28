'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import energy_demand.energy_model as energy_model
from energy_demand.assumptions import assumptions
from energy_demand.read_write import data_loader
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data
from energy_demand.disaggregation import national_disaggregation
from energy_demand.building_stock import building_stock_generator
from energy_demand.technologies import diffusion_technologies as diffusion
from energy_demand.technologies import fuel_service_switch
from energy_demand.calculations import enduse_scenario
from energy_demand.basic import testing_functions as testing
from energy_demand.basic import unit_conversions
from energy_demand.basic import date_handling
from energy_demand.validation import lad_validation
from energy_demand.validation import elec_national_data
from energy_demand.plotting import plotting_results
from energy_demand.read_write import read_data
import datetime
from datetime import date
from datetime import timedelta as td
import numpy as np
from pytest import raises


# --------------------------
# date_handling
# -------------------------
from energy_demand.basic import date_handling

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
    in_yearday = 10
    expected = date(2015,1,11)

    # call function
    out_value = date_handling.convert_yearday_to_date(in_year, in_yearday)

    assert out_value == expected

def test_get_datetime_range():
    """Testing function"""
    start_date = date(2015, 1, 1)
    end_date = date(2015, 1, 2)

    expected = [date(2015, 1, 1), date(2015, 1, 2)]
    out = date_handling.get_datetime_range(start_date, end_date)

    assert out == expected


def test_get_weekday_type():
    """Testing function"""
    # in test value

    in_value = date(2015, 1, 1)
    expected = 0

    # call function
    out_value = date_handling.get_weekday_type(in_value)

    assert out_value == expected


# --------------Building STock generator
def test_raises_error_get_dwtype_distr_cy():
    """ Test if the error is raised if wrong input data"""
    # in test value
    wrong_data = {'semi_detached': 20.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    in_value_2 = {'semi_detached': 20.0, 'terraced': 20, 'flat': 30, 'detached': 20, 'bungalow': 10}
    in_value_3 = {'base_year': 2015, 'current_year': 2016, 'end_year': 2050}

    with raises(AssertionError):
        bf.get_dwtype_distr_cy(wrong_data, in_value_2, in_value_3)





# --------------------------
# Other
# --------------------------
def test_read_csv_dict():
    """Testing function"""

    # in test value
    in_value_1 = 'data/_test_data/test_csv.csv'

    expected = {15: {'test_value': 3}}

    # call function
    out_value = read_data.read_csv_dict(in_value_1)

    assert out_value == expected

def test_read_csv_float():
    """Testing function"""

    # in test value
    in_value_1 = 'data/_test_data/test_csv.csv'

    expected = np.array([[float(15), float(3)]])

    # call function
    out_value = read_data.read_csv_float(in_value_1)

    np.testing.assert_array_equal(out_value, expected)

def test_read_csv():
    """Testing function"""

    # in test value
    in_value_1 = 'data/_test_data/test_csv.csv'

    expected = np.array([[15, 3]])

    # call function
    out_value = read_data.read_csv_float(in_value_1)

    # Raise assertion error if array are identical
    np.testing.assert_array_equal(out_value, expected)

def test_conversion_ktoe_gwh():
    """Testing function"""
    # in test value
    in_value = 10
    expected = in_value * 11.6300000

    # call function
    out_value = unit_conversions.conversion_ktoe_gwh(in_value)

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

def test_timesteps_full_year():
    """Testing function"""

    # in test value
   
    expected = 0

    # call function
    out_value_1, out_value_1 = mf.timesteps_full_year(in_value)

    assert out_value == expected

def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)

'''