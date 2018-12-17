from energy_demand.read_write.narrative_related import crit_dim_var
from collections import OrderedDict

class TestCritDimensionsVar:

    def test_crit_in_list(self):

        crit_in_list = [
            {'sig_midpoint': 0, 'value_by': 5, 'diffusion_choice': 'linear',
            'fueltype_replace': 0, 'regional_specific': False,
            'base_yr': 2015, 'value_ey': 5, 'sig_steepness': 1,
            'end_yr': 2050, 'fueltype_new': 0}]

        actual = crit_dim_var(crit_in_list)
        expected = True
        print("AC ULT " + str(actual))
        assert actual == expected

    def test_nested_dict_in_list(self):

        nested_dict_in_list = [{'key': {'nested_dict': 'a value'}}]

        actual = crit_dim_var(nested_dict_in_list)
        expected = False
        print("AC ULT " + str(actual))
        assert actual == expected

    def test_nested_dict(self):

        nested_dict = {'key': {'nested_dict': 'a value'}}

        actual = crit_dim_var(nested_dict)
        expected = False
        assert actual == expected

        nested_dict = {'another_key': {}, 'key': []}
        actual = crit_dim_var(nested_dict)
        expected = True
        assert actual == expected

    def test_crit_list(self):

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

    def test_crit_dim_var_ordered(self):

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

    def test_crit_dim_var_buggy(self):

        fixture = [
            {'sig_steepness': 1,
             'sector': 'dummy_sector',
             'diffusion_choice': 'linear',
             'sig_midpoint': 0,
             'regional_specific': True,
             'base_yr': 2015,
             'value_ey': 0.05,
             'value_by': 0.05,
             'regional_vals_ey': {'W06000023': 0.05, 'W06000010': 0.05},
             'regional_vals_by': {'W06000023': 0.05, 'W06000010': 0.05},
             'end_yr': 2030,
             'enduse': [],
             'default_by': 0.05
             },
            {'sig_steepness': 1,
             'sector': 'dummy_sector',
             'diffusion_choice': 'linear',
             'sig_midpoint': 0,
             'regional_specific': True,
             'base_yr': 2030,
             'value_ey': 0.05,
             'value_by': 0.05,
             'regional_vals_ey': {'W06000023': 0.05, 'W06000010': 0.05},
             'regional_vals_by': {'W06000023': 0.05, 'W06000010': 0.05},
             'end_yr': 2050,
             'enduse': [],
             'default_by': 0.05
             }
            ]
        actual = crit_dim_var(fixture)
        expected = True
        assert actual == expected
