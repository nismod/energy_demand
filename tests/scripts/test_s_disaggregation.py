"""Testing
"""
import numpy as np
from energy_demand.scripts import s_disaggregation
from energy_demand.assumptions import general_assumptions

def test_rs_disaggregate():
    """testing
    """
    dummy_sector = None
    regions = ['regA', 'regB']

    national_fuel = 100
    rs_national_fuel = {'rs_space_heating': {dummy_sector: national_fuel}}

    scenario_data = {
        'population': {2015: {'regA': 10, 'regB': 10}},
        'floor_area': {'rs_floorarea': {2015: {'regA': 10, 'regB': 10}}}}

    assumptions = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'rs_regions_without_floorarea': [],
        'base_temp_diff_params': {
            'sig_midpoint': 0,
            'sig_steepness': 1,
            'yr_until_changed': 2020},
        'strategy_vars': {'rs_t_base_heating': {'scenario_value': 15}}}
    assumptions = general_assumptions.DummyClass(assumptions)
    assumptions.__setattr__('t_bases', general_assumptions.DummyClass({'rs_t_heating': 15}))

    reg_coord = {
        'regA': {'longitude': 0,'latitude': 0},
        'regB': {'longitude': 0,'latitude': 0}}

    weather_stations = {
        'stationID_1': {'longitude': 1,'latitude': 1}}

    temp_data = {'stationID_1': np.ones((365, 24)) + 10}
    enduses = ['rs_space_heating']

    pop_for_disag = {
        2015: {
            'regA': 100,
            'regB': 100},
        2020: {
            'regA': 100,
            'regB': 100}} 

    result = s_disaggregation.rs_disaggregate(
        regions=regions,
        rs_national_fuel=rs_national_fuel,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disag,
        assumptions=assumptions,
        reg_coord=reg_coord,
        weather_stations=weather_stations,
        temp_data=temp_data,
        enduses=enduses,
        crit_limited_disagg_pop_hdd=True,
        crit_limited_disagg_pop=False,
        crit_full_disagg=False,
        dummy_sector=dummy_sector)
    
    assert result['regA']['rs_space_heating'][None] == national_fuel / 2

    result = s_disaggregation.rs_disaggregate(
        regions=regions,
        rs_national_fuel=rs_national_fuel,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disag,
        assumptions=assumptions,
        reg_coord=reg_coord,
        weather_stations=weather_stations,
        temp_data=temp_data,
        enduses=enduses,
        crit_limited_disagg_pop_hdd=False,
        crit_limited_disagg_pop=True,
        crit_full_disagg=False,
        dummy_sector=dummy_sector)

    assert result['regA']['rs_space_heating'][None] == national_fuel / 2

def test_ss_disaggregate():
    """testing
    """
    regions = ['regA', 'regB']
    national_fuel = 100
    raw_fuel_sectors_enduses = {'ss_space_heating': {'offices': national_fuel}}

    scenario_data = {
        'population': {2015: {'regA': 10, 'regB': 10}},
        'floor_area': {
            'ss_floorarea_newcastle': {
                2015: {'regA': 10, 'regB': 10}},
            'ss_floorarea' :{
                 2015: {'regA': {'offices': 100}, 'regB': {'offices': 100}}}
            },
        }

    assumptions = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'ss_regions_without_floorarea': [],
        'base_temp_diff_params': {
            'sig_midpoint': 0,
            'sig_steepness': 1,
            'yr_until_changed': 2020},
        'strategy_vars': {
            'ss_t_base_heating': {'scenario_value': 15},
            'ss_t_base_cooling': {'scenario_value': 20}}}

    assumptions = general_assumptions.DummyClass(assumptions)
    assumptions.__setattr__('t_bases', general_assumptions.DummyClass(
        {'ss_t_heating': 15, 'ss_t_cooling': 20}))

    reg_coord = {
        'regA': {'longitude': 0, 'latitude': 0},
        'regB': {'longitude': 0, 'latitude': 0}}

    weather_stations = {
        'stationID_1': {'longitude': 1,'latitude': 1}}

    temp_data = {'stationID_1': np.ones((365, 24)) + 10}

    enduses = ['ss_space_heating']
    sectors = ['offices']

    service_building_count = {}
    service_building_count[9] = {}
    service_building_count[9]['regA'] = 10
    service_building_count[9]['regB'] = 10

    pop_for_disag = {
        2015: {
            'regA': 100,
            'regB': 100},
        2020: {
            'regA': 100,
            'regB': 100}}            

    result = s_disaggregation.ss_disaggregate(
        ss_national_fuel=raw_fuel_sectors_enduses,
        service_building_count=service_building_count,
        assumptions=assumptions,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disag,
        regions=regions,
        reg_coord=reg_coord,
        temp_data=temp_data,
        weather_stations=weather_stations,
        enduses=enduses,
        sectors=sectors,
        crit_limited_disagg_pop_hdd=False,
        crit_limited_disagg_pop=True,
        crit_full_disagg=False)

    assert result['regA']['ss_space_heating']['offices'] == national_fuel / 2

def test_is_disaggregate():
    """TESTING"""
    temp_data = {'stationID_1': np.ones((365, 24)) + 10}
    reg_coord = {
        'regA': {'longitude': 0, 'latitude': 0},
        'regB': {'longitude': 0, 'latitude': 0}}

    weather_stations = {
        'stationID_1': {'longitude': 1,'latitude': 1}}

    national_fuel = 100
    raw_fuel_sectors_enduses = {'is_space_heating': {
        'mining': national_fuel,
        'pharmaceuticals': national_fuel}}

    assumptions = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'base_temp_diff_params': {
            'sig_midpoint': 0,
            'sig_steepness': 1,
            'yr_until_changed': 2020},
        'strategy_vars': {
            'is_t_heating': {'scenario_value': 0},
            'is_t_base_heating': {'scenario_value': 15},
            'is_t_base_cooling_future_yr': {'scenario_value': 15}}}

    assumptions = general_assumptions.DummyClass(assumptions)
    assumptions.__setattr__('t_bases', general_assumptions.DummyClass({'is_t_heating': 15, 'is_t_cooling': 15}))

    regions = ['regA', 'regB']
    enduses = ['is_space_heating']
    sectors = ['mining', 'pharmaceuticals']

    employment_statistics = {
        'regA': {'B': 0, 'M': 10}, #mining, pharmaceuticals
        'regB': {'B': 5, 'M': 5}}

    pop_for_disag = {
        2015: {
            'regA': 10,
            'regB': 10}}

    result = s_disaggregation.is_disaggregate(
        assumptions=assumptions,
        temp_data=temp_data,
        reg_coord=reg_coord,
        weather_stations=weather_stations,
        is_national_fuel=raw_fuel_sectors_enduses,
        regions=regions,
        enduses=enduses,
        sectors=sectors,
        employment_statistics=employment_statistics,
        pop_for_disagg=pop_for_disag,
        census_disagg=False,
        )

    assert result['regA']['is_space_heating']['mining'] == 50.0

    # ----
    result = s_disaggregation.is_disaggregate(
        assumptions=assumptions,
        temp_data=temp_data,
        reg_coord=reg_coord,
        weather_stations=weather_stations,
        is_national_fuel=raw_fuel_sectors_enduses,
        regions=regions,
        enduses=enduses,
        sectors=sectors,
        employment_statistics=employment_statistics,
        pop_for_disagg=pop_for_disag,
        census_disagg=True)

    assert result['regA']['is_space_heating']['mining'] == 0
    assert round(result['regA']['is_space_heating']['pharmaceuticals'], 3) == round(10.0/15.0 * 100,3) 
    assert result['regB']['is_space_heating']['mining'] == 100
    assert round(result['regB']['is_space_heating']['pharmaceuticals'], 3)  == round(5.0/15.0 * 100, 3)
