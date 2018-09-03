"""
"""
from energy_demand.initalisations import helpers
from energy_demand.read_write import read_data

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

    assert "c" in keys
    assert "d" in keys
    assert "e" in keys

def test_set_same_eff_all_tech():
    """Test
    """
    eff_to_assign = 0.5

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

    techs_eff = helpers.set_same_eff_all_tech(
        technologies=technologies,
        f_eff_achieved=0.44)

    assert techs_eff['boilerA'].eff_achieved == 0.44
