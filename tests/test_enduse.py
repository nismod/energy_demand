"""
"""
import numpy as np
from energy_demand.enduse_func import Enduse
from energy_demand.scripts import s_generate_sigmoid

def test_service_switch():
    """Test
    """
    # DUMMY OBJECT
    class Enduse(object):
        def __init__(self, Name_Enduse):
            self.enduse = Name_Enduse

            # Increase boilerA to 100%
            share_boilerA_by = 0.5
            share_boilerA_cy = 1.0
            share_boilerB_by = 0.5
            share_boilerB_cy = 0.0
            curr_yr = 2050

            # ----- Calculate sigmoids
            l_value = 0.5
            xdata = np.array([2020.0, curr_yr])
            ydata = np.array([share_boilerA_by, share_boilerA_cy])

            # fit parameters
            fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
                l_value,
                xdata,
                ydata,
                fit_crit_a=200,
                fit_crit_b=0.001)

            # -----

            tot_service_yh_cy = np.ones((356, 24)) #constant share of 1 in every hour
            service_tech_by_p = {"boilerA": share_boilerA_by, "boilerB": share_boilerB_by}#, "boiler_C": 0.1}
            tech_increase_service = ["boilerA"]
            tech_decrease_service = ["boilerB"]
            tech_constant_service = []
            sig_param_tech = {
                "boilerA": {
                    'midpoint': fit_parameter[0],
                    'steepness': fit_parameter[1],
                    'l_parameter': l_value}
                    }
           
            result = Enduse.service_switch(
                tot_service_yh_cy,
                service_tech_by_p,
                tech_increase_service,
                tech_decrease_service,
                tech_constant_service,
                sig_param_tech,
                curr_yr)

            expected_service_tech_cy_p = {
                "boilerA": 8760 * share_boilerA_cy,
                "boilerB": 8760 * share_boilerB_cy}

            assert result == expected_service_tech_cy_p

    dummy_Enduse = Enduse("Dummy")
    