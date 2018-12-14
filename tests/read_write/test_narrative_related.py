from energy_demand.read_write.narrative_related import crit_dim_var
from collections import OrderedDict

def test_crit_dim_var():

    nested_dict = {'key': {'nested_dict': 'a value'}}

    actual = crit_dim_var(nested_dict)
    expected = False
    assert actual == expected

    nested_dict = {'another_key': {}, 'key': []}
    actual = crit_dim_var(nested_dict)
    expected = True
    assert actual == expected

    a_list = []
    actual = crit_dim_var(a_list)
    expected = True
    assert actual == expected

    the_bug = {'enduse': [], 'diffusion_type': 'linear', 'default_value': 15.5,
               'name': 'ss_t_base_heating', 'sector': True,
               'regional_specific': False,
               'description': 'Base temperature',
               'scenario_value': 15.5}
    actual = crit_dim_var(the_bug)
    expected = True
    assert actual == expected

def test_crit_dim_var_ordered():

    the_bug = OrderedDict()
    the_bug['a'] = {'diffusion_type': 'linear', 'default_value': 15.5,
                    'name': 'ss_t_base_heating', 'sector': True,
                    'regional_specific': False,
                    'description': 'Base temperature',
                    'scenario_value': 15.5,
                    'enduse': []}
    the_bug['b'] = 'vakye'
    actual = crit_dim_var(the_bug)
    expected = False
    assert actual == expected
