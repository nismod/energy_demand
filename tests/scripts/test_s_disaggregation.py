"""Testing
"""
import numpy as np
from energy_demand.scripts import s_disaggregation

def test_rs_disaggregate():
    """testing
    """
    lu_reg = ['regA', 'regB']
    base_yr= 2015
    curr_yr= 2020

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
        base_yr,
        curr_yr,
        rs_national_fuel,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        crit_limited_disagg_pop_hdd=True,
        crit_limited_disagg_pop=False,
        crit_full_disagg=False)

    assert result['regA']['rs_space_heating'] == national_fuel / 2

    # -----   
    result = s_disaggregation.rs_disaggregate(
        lu_reg,
        base_yr,
        curr_yr,
        rs_national_fuel,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        crit_limited_disagg_pop_hdd=False,
        crit_limited_disagg_pop=True,
        crit_full_disagg=False)

    assert result['regA']['rs_space_heating'] == national_fuel / 2

def test_ss_disaggregate():
    """testing
    """
    lu_reg = ['regA', 'regB']
    base_yr= 2015
    curr_yr= 2020

    national_fuel = 100
    raw_fuel_sectors_enduses = {'sectorA': {'ss_space_heating': national_fuel}}

    scenario_data = {
        'population': {2015: {'regA': 10, 'regB': 10}},
        'floor_area': {'ss_floorarea_newcastle': {2015: {'regA': 10, 'regB': 10}}},
        }

    assumptions = {
        'base_temp_diff_params': {
            'sig_midpoint': 0,
            'sig_steeppness': 1,
            'yr_until_changed': 2020},
        'strategy_variables': {'ss_t_base_heating_future_yr': 0, 'ss_t_base_cooling_future_yr': 0},
        'ss_t_base_heating': {'ss_t_base_heating_base_yr': 0},
        'ss_t_base_cooling': {'ss_t_base_cooling_base_yr': 0}}

    reg_coord = {
        'regA': {'longitude': 0,'latitude': 0},
        'regB': {'longitude': 0,'latitude': 0}}

    weather_stations = {
        'stationID_1': {'station_longitude': 1,'station_latitude': 1}}

    temp_data = {'stationID_1': np.ones((365, 24)) + 10}

    enduses = {'ss_all_enduses': ['ss_space_heating']}
    sectors = {'ss_sectors': ['sectorA']}
    all_sectors = ['sectorA']

    ss_floorarea_sector_2015_virtual_bs = {
        'regA': {'sectorA': 100},
        'regB': {'sectorA': 100}}

    result = s_disaggregation.ss_disaggregate(
        raw_fuel_sectors_enduses,
        assumptions,
        scenario_data,
        base_yr,
        curr_yr,
        lu_reg,
        reg_coord,
        temp_data,
        weather_stations,
        enduses,
        sectors,
        all_sectors,
        ss_floorarea_sector_2015_virtual_bs,
        crit_limited_disagg_pop_hdd=False,
        crit_limited_disagg_pop=True,
        crit_full_disagg=False)

    assert result['regA']['sectorA']['ss_space_heating'] == national_fuel / 2

def test_is_ss_disaggregate():
    """TESTING"""

    base_yr = 2015
    national_fuel = 100
    raw_fuel_sectors_enduses = {'mining': {'is_space_heating': national_fuel},
                                'pharmaceuticals': {'is_space_heating': national_fuel}}
    lu_reg = ['regA', 'regB']
    enduses = {'is_all_enduses': ['is_space_heating']}
    sectors = {'is_sectors': ['mining', 'pharmaceuticals']}

    employment_statistics = {
        'regA': {'B': 0, 'M': 10}, #mining, pharmaceuticals
        'regB': {'B': 5, 'M': 5}}

    scenario_data = {'population': {
        2015: {
            'regA': 10,
            'regB': 10}}}

    result = s_disaggregation.is_disaggregate(
        base_yr,
        raw_fuel_sectors_enduses,
        lu_reg,
        enduses,
        sectors,
        employment_statistics,
        scenario_data,
        crit_limited_disagg_pop=True,
        crit_employment=False)

    assert result['regA']['mining']['is_space_heating'] == 50
    # ----
    result = s_disaggregation.is_disaggregate(
        base_yr,
        raw_fuel_sectors_enduses,
        lu_reg,
        enduses,
        sectors,
        employment_statistics,
        scenario_data,
        crit_limited_disagg_pop=False,
        crit_employment=True)
    
    assert result['regA']['mining']['is_space_heating'] == 0
    assert round(result['regA']['pharmaceuticals']['is_space_heating'], 3) == round(10.0/15.0 * 100,3) 
    assert result['regB']['mining']['is_space_heating'] == 100
    assert round(result['regB']['pharmaceuticals']['is_space_heating'], 3)  == round(5.0/15.0 * 100, 3)
