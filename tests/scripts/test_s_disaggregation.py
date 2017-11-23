"""Testing
"""
import numpy as np
from energy_demand.scripts import s_disaggregation

def test_rs_disaggregate():
    """testing
    """
    lu_reg = ['regA', 'regB']
    sim_param = {'base_yr': 2015, 'curr_yr': 2020}

    national_fuel = 100
    rs_national_fuel = {'rs_space_heating': national_fuel}

    scenario_data = {
        'population': {2015: {'regA': 10, 'regB': 10}},
        'floor_area': {'rs_floorarea_newcastle': {2015: {'regA': 10, 'regB': 10}}},
        }

    assumptions = {
        'base_temp_diff_params': {
            'sig_midpoint': 0,
            'sig_steeppness': 1,
            'yr_until_changed': 2020},
        'strategy_variables': {'rs_t_base_heating_future_yr': 0},
        'rs_t_base_heating': {'rs_t_base_heating_base_yr': 0}}

    reg_coord = {
        'regA': {'longitude': 0,'latitude': 0},
        'regB': {'longitude': 0,'latitude': 0}}

    weather_stations = {
        'stationID_1': {'station_longitude': 1,'station_latitude': 1}}

    temp_data = {'stationID_1': np.ones((365, 24)) + 10}

    result = s_disaggregation.rs_disaggregate(
        lu_reg,
        sim_param,
        rs_national_fuel,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        crit_limited_disagg_pop_hdd=True,
        crit_limited_disagg_pop=False)

    assert result['regA']['rs_space_heating'] == national_fuel / 2

    # -----   

    result = s_disaggregation.rs_disaggregate(
        lu_reg,
        sim_param,
        rs_national_fuel,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        crit_limited_disagg_pop_hdd=False,
        crit_limited_disagg_pop=True)

    assert result['regA']['rs_space_heating'] == national_fuel / 2
