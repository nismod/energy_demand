
"""Testing
"""
import numpy as np
from energy_demand.profiles import load_profile

def test_calc_yh():
    """testing"""
    shape_yd = np.ones((365))
    shape_y_dh = np.zeros((365, 24))

    shape_yd[0] = 2.0 #add plus one
    shape_y_dh[0] = np.ones((24))
    shape_y_dh[0][0] = 2.0 #add plus one in day

    out = load_profile.calc_yh(
        shape_yd=shape_yd,
        shape_y_dh=shape_y_dh,
        model_yeardays=list(range(365)))

    assert out[0][0] == 2 * 2
    assert out[0][1] == 2 * 1

def test_abs_to_rel():
    """Test
    """
    absolute_array = np.array([1, 2, 3])
    absolute_array2 = np.array([0, 0, 0])

    relative_array = load_profile.abs_to_rel(absolute_array)
    relative_array2 = load_profile.abs_to_rel(absolute_array2)

    expected_relative_array = np.array(
        [
            float(absolute_array[0]) / np.sum(absolute_array),
            float(absolute_array[1]) / np.sum(absolute_array),
            float(absolute_array[2]) / np.sum(absolute_array)
            ]
    )

    np.testing.assert_equal(np.round(relative_array,3), np.round(expected_relative_array, 3))
    np.testing.assert_equal(relative_array2, absolute_array2)

def test_calk_peak_h_dh():
    """testing
    """
    fuel_yh = np.zeros((2, 24)) #two fueltypes, 24 hours
    fuel_yh[1] = np.array([1,2,3,4,5,4,3,2,1,1,1,1,1,1,1,1,2,2,1,1,3,4,5,6])

    result = load_profile.calk_peak_h_dh(fuel_yh)

    assert result[0] == np.max(fuel_yh[0])
    assert result[1] == np.max(fuel_yh[1])

def test_LoadProfileStock():
    """testing
    """

    result_obj = load_profile.LoadProfileStock("test_stock")

    expected = "test_stock"

    assert result_obj.name == expected
    model_yeardays = list(range(365))
    # -----
    result_obj.add_lp(
        unique_identifier="A123",
        technologies=['placeholder_tech'],
        enduses=['cooking'],
        shape_y_dh=np.zeros((365)),
        shape_yd=np.zeros((365)),
        shape_yh=np.zeros((365, 24)),
        sectors=False,
        model_yeardays=model_yeardays)

    result = result_obj.stock_enduses

    result2 = load_profile.get_stock_enduses(result_obj.load_profiles)

    assert result == ['cooking']
    assert result2 == ['cooking']

    # ---
    # -----
    result_obj.add_lp(
        unique_identifier="A123",
        technologies=['placeholder_tech'],
        enduses=['cooking'],
        shape_y_dh=np.zeros((365)),
        shape_yd=np.zeros((365)),
        shape_yh=np.zeros((365, 24)),
        sectors=['sectorA'],
        model_yeardays=model_yeardays)

    result = result_obj.stock_enduses
    assert result == ['cooking']

    # test get_lp()
    np.testing.assert_array_equal(np.zeros((365, 24)), result_obj.get_lp('cooking', 'sectorA', 'placeholder_tech', 'shape_yh'))

    # test get_shape_peak_dh()
    '''_var = result_obj.get_lp('cooking', 'sectorA', 'placeholder_tech', 'shape_peak_dh')
    np.testing.assert_array_equal(
        _var, 
        result_obj.get_shape_peak_dh('cooking', 'sectorA', 'placeholder_tech'))'''

def test_generate_key_lu_dict():
    """
    """
    result = load_profile.generate_key_lu_dict(
        {"A": 3},
        "100D",
        ['cooking'],
        ["sectorA", "sectorB"],
        ['techA'])
    
    expected = {"A": 3, ('cooking', "sectorA", 'techA'): "100D", ('cooking', "sectorB", 'techA'): "100D"}

    assert expected == result

def test_LoadProfile():

    result_obj = load_profile.LoadProfile(
        enduses=['heating'],
        unique_identifier="A123",
        shape_yd=np.zeros((365)),
        shape_yh=np.zeros((365, 24)),
        shape_y_dh=np.full((365), 1/365),
        model_yeardays=list(range(365)))

    assert result_obj.enduses == ['heating']

def test_calc_av_lp():

    model_yeardays_daytype = [
        'holiday',
        'workday',
        'workday',
        'workday',

        'holiday',
        'workday',
        'workday',
        'workday',

        'holiday',
        'workday',
        'workday',
        'workday',

        'holiday',
        'workday',
        'workday',
        'workday',
        ] #

    # Example with 16 days
    seasons = {}
    seasons['winter'] = [0, 1, 2, 3]
    seasons['spring'] = [4, 5, 6, 7]
    seasons['summer'] = [8, 9, 10, 11]
    seasons['autumn'] = [12, 13, 14, 15]

    demand_yh = np.zeros((16, 24)) + 10

    for i in range(4):
        demand_yh[i] = 12

    for i in range(4, 8):
        demand_yh[i] = 10

    # weekend
    demand_yh[0] = 100
    demand_yh[4] = 200

    result_av, _ = load_profile.calc_av_lp(demand_yh, seasons, model_yeardays_daytype)
    
    expected = {
        'winter': {'workday': np.full((24), 12), 'holiday': np.full((24), 100)},
        'spring': {'workday': np.full((24), 10), 'holiday': np.full((24), 200)},
        'summer': {'workday': np.full((24), 12), 'holiday': np.full((24), 100)},
        'autmn': {'workday': np.full((24), 10), 'holiday': np.full((24), 10)}
        }

    np.testing.assert_array_equal(expected['winter']['workday'], result_av['winter']['workday'])
    np.testing.assert_array_equal(expected['winter']['holiday'], result_av['winter']['holiday'])
    np.testing.assert_array_equal(expected['spring']['workday'], result_av['spring']['workday'])
    np.testing.assert_array_equal(expected['spring']['holiday'], result_av['spring']['holiday'])
