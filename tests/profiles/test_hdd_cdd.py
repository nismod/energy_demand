"""testing
"""
from energy_demand.profiles import hdd_cdd
import numpy as np

def test_calc_hdd():
    """testing
    """
    t_base = 15 #degree
    temp_yh = np.zeros((365, 24))
    
    for day in range(365):
        for hour in range(24):
            temp_yh[day][hour] = np.random.randint(-4, 30)

    result = hdd_cdd.calc_hdd(t_base, temp_yh)

    temp_yh[temp_yh > t_base] = t_base

    expected = np.sum(t_base - temp_yh) / 24

    # positive values
    assert round(np.sum(result), 3) == round(expected, 3)

def test_sigm_temp():
    assumptions = {}
    assumptions['smart_meter_diff_params'] = {}
    assumptions['smart_meter_diff_params']['sig_midpoint'] = 0
    assumptions['smart_meter_diff_params']['sig_steeppness'] = 1

    end_yr_t_base = 13
    assumptions['rs_t_base_heating'] = {}
    assumptions['rs_t_base_heating']['base_yr'] = 15
    assumptions['rs_t_base_heating']['end_yr'] = end_yr_t_base

    base_sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'end_yr': 2020}

    result = hdd_cdd.sigm_temp(base_sim_param, assumptions, 'rs_t_base_heating')

    expected = end_yr_t_base
    assert result == expected
