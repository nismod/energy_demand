"""
"""
from energy_demand.initalisations import helpers

def test_init_dict_brackets():
    """Test
    """
    first_level_keys = ["a", "b"]

    one_level_dict = helpers.init_dict_brackets(first_level_keys)

    expected = {"a": {}, "b": {}}

    assert one_level_dict == expected

def test_get_nested_dict_key():
    """Test
    """
    nested_dict = {"a": {"c": 1, "d": 3}, "b": {"e": 4}}

    keys = helpers.get_nested_dict_key(nested_dict)

    expected = ["c", "d", "e"]

    assert keys == expected

def test_helper_set_same_eff_all_tech():
    """Test
    """
    eff_to_assign = 0.5
    techs = {"tech_a": {'eff_achieved': 0}}
    techs_eff = helpers.helper_set_same_eff_all_tech(techs)

    expected = {"tech_a": {'eff_achieved': eff_to_assign}}

    assert techs_eff == expected
    