"""testing
"""
from energy_demand.scripts import s_rs_raw_shapes
import numpy as np

def test_assign_hes_data_to_year():

    hes_data = {
        'holiday': {
            0: np.zeros((24, 2)) + 10,
            1: np.zeros((24, 2)) + 20,
            2: np.zeros((24, 2)) + 30,
            3: np.zeros((24, 2)) + 40, 
            4: np.zeros((24, 2)) + 50, 
            5: np.zeros((24, 2)) + 60, 
            6: np.zeros((24, 2)) + 70, 
            7: np.zeros((24, 2)) + 80, 
            8: np.zeros((24, 2)) + 90, 
            9: np.zeros((24, 2)) + 100, 
            10: np.zeros((24, 2)) + 110,
            11: np.zeros((24, 2)) + 120
            },

        'workday' : {
            0: np.zeros((24, 2)) + 1,
            1: np.zeros((24, 2)) + 2,
            2: np.zeros((24, 2)) + 3,
            3: np.zeros((24, 2)) + 4, 
            4: np.zeros((24, 2)) + 5, 
            5: np.zeros((24, 2)) + 6, 
            6: np.zeros((24, 2)) + 7, 
            7: np.zeros((24, 2)) + 8, 
            8: np.zeros((24, 2)) + 9, 
            9: np.zeros((24, 2)) + 10, 
            10: np.zeros((24, 2)) + 11,
            11: np.zeros((24, 2)) + 12}
        }

    result = s_rs_raw_shapes.assign_hes_data_to_year(
        nr_of_appliances=2,
        hes_data=hes_data,
        base_yr=2017)

    assert result['holiday'][0][0] == 10 #daytype, month_python, appliances
    assert result['workday'][0][0] == 1
