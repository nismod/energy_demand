"""Testing
"""
from energy_demand.scripts import s_fuel_to_service

def init_nested_dict_brackets():

    result = s_fuel_to_service.init_nested_dict_brackets(
        first_level_keys=["A", "B"],
        second_level_keys=[1,2])
    
    expected = {"A": {1: {}, 2: {}}, "B": {1: {}, 2: {}}}

    assert result == expected

def test_init_nested_dict_zero():

    result = s_fuel_to_service.init_nested_dict_zero(
        first_level_keys=["A", "B"],
        second_level_keys=[1,2])
    
    expected = {"A": {1: 0, 2: 0}, "B": {1: 0, 2: 0}}

    assert result == expected
