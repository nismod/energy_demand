"""Testing
"""
import numpy as np
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_data

'''def test_get_tech_type():
    """Testing
    """
    tech_list = {
        'heating_non_const': ['heat_p'],
        'heating_const': ['boilerA'],
        'storage_heating_electricity': ['boilerC'],
        'secondary_heating_electricity': []}

    assert tech_related.get_tech_type('placeholder_tech', tech_list) == 'placeholder_tech'
    assert tech_related.get_tech_type('heat_p', tech_list) == 'heat_pump'
    assert tech_related.get_tech_type('test_tech', tech_list) == 'other_tech'''

def test_calc_eff_cy():
    """Testing
    """
    out_value = tech_related.calc_eff_cy(
        base_yr=2015,
        curr_yr=2020,
        eff_by=1.0,
        eff_ey=2.0,
        yr_until_changed=2020,
        f_eff_achieved=1.0,
        diff_method='linear')

    assert out_value == 2.0

    out_value = tech_related.calc_eff_cy(
        base_yr=2015,
        curr_yr=2020,
        eff_by=1.0,
        eff_ey=2.0,
        yr_until_changed=2020,
        f_eff_achieved=1.0,
        diff_method='sigmoid')

    assert out_value == 2.0

def test_calc_hp_eff():
    """Testing function
    """
    temp_yh = np.zeros((365, 24)) + 10

    efficiency_intersect = 10
    t_base_heating = 15.5

    # call function
    out_value = tech_related.calc_hp_eff(
        temp_yh,
        efficiency_intersect,
        t_base_heating)

    float_value = 1.0
    expected = type(float_value)
    assert type(out_value) == expected

def test_eff_heat_pump():
    """Testing
    """
    t_base = 15.5
    temp_yh = np.zeros((365, 24)) + 5 #make diff 10 degrees
    temp_diff = t_base - temp_yh

    efficiency_intersect = 6 #Efficiency of hp at temp diff of 10 degrees

    out_value = tech_related.eff_heat_pump(temp_diff, efficiency_intersect)

    values_every_h = -0.08 * temp_diff + (efficiency_intersect - (-0.8))
    expected = np.average(values_every_h)

    assert out_value == expected

def test_get_fueltype_str():
    """Testing function
    """
    fueltypes = {'gas': 1}
    in_value = 1
    expected = 'gas'

    # call function
    out_value = tech_related.get_fueltype_str(fueltypes, in_value)

    assert out_value == expected

def test_get_fueltype_int():
    """Testing function
    """
    fueltypes = {'gas': 1}
    in_value = 'gas'
    expected = 1

    # call function
    out_value = tech_related.get_fueltype_int(in_value)

    assert out_value == expected

def test_calc_av_heat_pump_eff_ey():
    """testing
    """
    technologies = {
        'heat_pump_ASHP_electricity': read_data.TechnologyData(),
        'heat_pump_GSHP_electricity': read_data.TechnologyData(),
        'heat_pumps_electricity': read_data.TechnologyData()
        }
    technologies['heat_pump_ASHP_electricity'].fueltype_str = 'electricity'
    technologies['heat_pump_ASHP_electricity'].eff_achieved = 1.0
    technologies['heat_pump_ASHP_electricity'].diff_method = 'linear'
    technologies['heat_pump_ASHP_electricity'].eff_by = 0.5
    technologies['heat_pump_ASHP_electricity'].eff_ey = 0.5
    technologies['heat_pump_ASHP_electricity'].year_eff_ey = 2020

    technologies['heat_pump_GSHP_electricity'].fueltype_str = 'electricity'
    technologies['heat_pump_GSHP_electricity'].eff_achieved = 1.0
    technologies['heat_pump_GSHP_electricity'].diff_method = 'linear'
    technologies['heat_pump_GSHP_electricity'].eff_by = 1.0
    technologies['heat_pump_GSHP_electricity'].eff_ey = 1.0
    technologies['heat_pump_GSHP_electricity'].year_eff_ey = 2020

    technologies['heat_pumps_electricity'].fueltype_str = 'electricity'
    technologies['heat_pumps_electricity'].eff_achieved = 1.0
    technologies['heat_pumps_electricity'].diff_method = 'linear'
    technologies['heat_pumps_electricity'].eff_by = 1.0
    technologies['heat_pumps_electricity'].eff_ey = 99999
    technologies['heat_pumps_electricity'].year_eff_ey = 2020

    heat_pump_assump = {
        'electricity': {
            'heat_pump_ASHP_electricity': 0.7,
            'heat_pump_GSHP_electricity': 0.3
            }
    }

    result = tech_related.calc_av_heat_pump_eff_ey(
        technologies,
        heat_pump_assump)

    assert result['heat_pumps_electricity'].eff_ey == 0.7 * 0.5 + 0.3 * 1.0
