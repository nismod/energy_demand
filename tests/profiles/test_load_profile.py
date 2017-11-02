
"""Testing
"""
from energy_demand.profiles import load_profile
import sys
import numpy as np

def test_abs_to_rel():
    """Test
    """

    absolute_array = np.array([1,2,3])
    absolute_array2 = np.array([0,0,0])

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

    assert result_obj.stock_name == expected

    # -----
    result_obj.add_load_profile(
        unique_identifier="A123",
        technologies=['dummy_tech'],
        enduses=['cooking'],
        shape_yd=np.zeros((365)),
        shape_yh=np.zeros((365, 24)),
        sectors=False,
        enduse_peak_yd_factor=1.0/365,
        shape_peak_dh=np.full((24), 1.0/24))

    result = result_obj.enduses_in_stock

    result2 = load_profile.get_all_enduses_in_stock(result_obj.load_profile_dict)

    assert result == ['cooking']
    assert result2 == ['cooking']

    # ---
    # -----
    result_obj.add_load_profile(
        unique_identifier="A123",
        technologies=['dummy_tech'],
        enduses=['cooking'],
        shape_yd=np.zeros((365)),
        shape_yh=np.zeros((365, 24)),
        sectors=['sectorA'],
        enduse_peak_yd_factor=1.0/365,
        shape_peak_dh=np.full((24), 1.0/24))

    result = result_obj.enduses_in_stock
    assert result == ['cooking']

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
        enduse_peak_yd_factor=0.7,
        shape_peak_dh=np.zeros((24)))

    

    assert result_obj.enduses == ['heating']
