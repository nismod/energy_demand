"""
"""
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid

def test_service_switch():
    """Test
    """
    # Increase boilerA to 100%
    l_value = 0.9
    share_boilerA_by = 0.1
    share_boilerA_cy = 0.2 #1

    share_boilerB_by = 0.9
    share_boilerB_cy = 0.8

    curr_yr = 2050

    # ----- Calculate sigmoids
    
    xdata = np.array([2020.0, curr_yr])
    ydata = np.array([share_boilerA_by, share_boilerA_cy])
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    tot_service_yh_cy = np.full((365, 24), 1.0) #constant share of 1 in every hour
    service_tech_by_p = {"boilerA": share_boilerA_by, "boilerB": share_boilerB_by}
    tech_increase_service = ["boilerA"]
    tech_decrease_service = ["boilerB"]
    tech_constant_service = []

    enduse = "heating"
    sig_param_tech = {
        enduse :{
            "boilerA": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value}
        }
    }

    result = enduse_func.service_switch(
        enduse,
        tot_service_yh_cy,
        service_tech_by_p,
        tech_increase_service,
        tech_decrease_service,
        tech_constant_service,
        sig_param_tech,
        curr_yr)

    expected_service_tech_cy_p = {
        "boilerA": 365*24 * share_boilerA_cy,
        "boilerB": 365*24 * share_boilerB_cy}

    #test boilerA
    print(expected_service_tech_cy_p["boilerA"])
    print(np.sum(result["boilerA"]))
    assert round(expected_service_tech_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)

    #test boilerB
    print(expected_service_tech_cy_p["boilerB"])
    print(np.sum(result["boilerB"]))
    assert round(expected_service_tech_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

test_service_switch()