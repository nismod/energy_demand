"""Testing
"""
from energy_demand.scripts import s_fuel_to_service
from energy_demand.technologies import technological_stock
from energy_demand.read_write import read_data
import numpy as np

def init_nested_dict_brackets():
    """Testing"""
    result = s_fuel_to_service.init_nested_dict_brackets(
        first_level_keys=["A", "B"],
        second_level_keys=[1, 2])

    expected = {"A": {1: {}, 2: {}}, "B": {1: {}, 2: {}}}

    assert result == expected
    assert result[0] == expected[0]

def test_init_nested_dict_zero():
    """Testing"""
    result = s_fuel_to_service.init_nested_dict_zero(
        sector=None,
        first_level_keys=["A", "B"],
        second_level_keys=[1, 2])

    expected = {"A": {None: {1: 0, 2: 0}}, "B": {None: {1: 0, 2: 0}}}

    assert result == expected

def test_sum_2_level_dict():
    """Testing"""
    two_level_dict = {"A": {1: 30, 2: 2}, "B": {1: 1, 2: 0}}

    result = s_fuel_to_service.sum_2_level_dict(two_level_dict)

    assert result == 33

def test_get_s_fueltype_tech():
    """
    """
    tech_list = { 
        'heating_non_const': ['heat_p'],
        'heating_const': ['boilerA'],
        'storage_heating_electricity': ['boilerC'],
        'secondary_heating_electricity': []}

    fueltypes = {
        'gas': 0} 

    technologies = {
        'boilerA': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0)}

    fuel_p_tech_by = {'heating': {'sectorA': {0: {'boilerA': 1.0}}}}

    s_tech_by_p, s_fueltype_by_p = s_fuel_to_service.get_s_fueltype_tech(
       enduses=['heating'],
       fuel_p_tech_by=fuel_p_tech_by,
       fuels={'heating': {'sectorA': np.array([100])}},
       technologies=technologies,
       sector='sectorA')

    assert s_tech_by_p['heating']['boilerA'] == 1.0
    assert s_fueltype_by_p['heating']['sectorA'][0] == 1.0

    # -------------------------------------
    technologies = {
        'boilerA': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0),
        'boilerB': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0)}

    fuel_p_tech_by = {'heating': {'sectorA': {0: {'boilerA': 0.5, 'boilerB': 0.5}}}}

    s_tech_by_p, s_fueltype_by_p = s_fuel_to_service.get_s_fueltype_tech(
       enduses=['heating'],
       fuel_p_tech_by=fuel_p_tech_by,
       fuels={'heating': {'sectorA': np.array([100])}}, # 0 == gas
       technologies=technologies,
       sector='sectorA')

    assert s_tech_by_p['heating']['boilerA'] == 0.5
    assert s_tech_by_p['heating']['boilerB'] == 0.5
    assert s_fueltype_by_p['heating']['sectorA'][0] == 1.0

    # -------------------------------------

    tech_list = { 
        'heating_non_const': ['heat_p'],
        'heating_const': ['boilerA', 'boilerB'],
        'storage_heating_electricity': [],
        'secondary_heating_electricity': []}
    
    fueltypes = {
        'gas': 0,
        'electricity': 1} 

    technologies = {
        'boilerA': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0),
        'boilerB': read_data.TechnologyData(
            fueltype='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0)}

    fuel_p_tech_by = {'heating': {'sectorA': {0: {'boilerA': 1.0}, 1: {'boilerB': 1.0}}}}

    s_tech_by_p, s_fueltype_by_p = s_fuel_to_service.get_s_fueltype_tech(
       enduses=['heating'],
       fuel_p_tech_by=fuel_p_tech_by,
       fuels={'heating': {'sectorA': np.array([100, 300])}}, # tripple elec than gas
       technologies=technologies,
       sector='sectorA')

    assert s_tech_by_p['heating']['boilerA'] == 0.25
    assert s_tech_by_p['heating']['boilerB'] == 0.75
    assert s_fueltype_by_p['heating']['sectorA'][0] == 0.25
    assert s_fueltype_by_p['heating']['sectorA'][1] == 0.75
