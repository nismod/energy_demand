"""
"""
from energy_demand.technologies import fuel_service_switch
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid

'''def test_create_service_switch():

    enduses = ['heating']
    capacity_switches = [{
        'enduse': 'heating',
        'technology_install': 'boiler_gas',
        'market_entry': 2015,
        'year_fuel_consumption_switched': 2020,
        'fuel_capacity_installed': 100,
        'enduse_by_dict': 'rs_fuel_tech_p_by',
        'fuels': 'rs_fuel_raw_data_enduses'
    }]
    assumptions = {
        'technologies': {
                'boiler_oil': {
                    'fueltype': 'oil',
                    'eff_by': 0.5,
                    'eff_ey': 0.5,
                    'eff_achieved':	1.0,
                    'diff_method':	'linear',
                    'market_entry':	2010,
                    'tech_list': 'tech_heating',
                    'tech_assum_max_share': 1.0},

                'boiler_gas': {
                    'fueltype': 'gas',
                    'eff_by': 0.5,
                    'eff_ey': 0.5,
                    'eff_achieved':	1.0,
                    'diff_method':	'linear',
                    'market_entry':	2010,
                    'tech_list': 'tech_heating',
                    'tech_assum_max_share': 1.0},
                },
        'other_enduse_mode_info': {'diff_method': 'linear', 'sigmoid': {'sig_midpoint': 0,'sig_steeppness': 1}},
        'rs_fuel_tech_p_by': {'heating': {1 :{'boiler_oil': 1.0, 'boiler_gas': 0.0}}}
    }

    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'end_yr': 2020}
    fuels = {'heating': np.ones((365, 24))}

    results = fuel_service_switch.create_service_switch(
        enduses,
        capacity_switches,
        assumptions,
        sim_param,
        fuels,
        'rs_fuel_tech_p_by'
    )

    for i in results:
        print(i['tech'])
        print(np.sum(i['service_share_ey']))
    print("-----")
test_create_service_switch()
'''

def test_calc_service_switch_capacity():
    """
    """

    result = fuel_service_switch.calc_service_switch_capacity(paths, enduses, assumptinos, fuels, sim_param)

    '''# Install technology B and replace 50% of fueltype 0
    l_value = 0.9
    share_boilerA_by = 0.1
    share_boilerA_cy = 0.2 #1

    share_boilerB_by = 0.9
    share_boilerB_cy = 0.8

    base_yr = 2020
    curr_yr = 2060
    end_yr = 2060

    # ----- Calculate sigmoids

    xdata = np.array([base_yr, end_yr])
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
        "boilerA": 365*24 * share_boilerA_cy, # * 0.5
        "boilerB": 365*24 * share_boilerB_cy} # * 0.5
    #print(round(expected_service_tech_cy_p["boilerA"], 3))
    #print(round(np.sum(result["boilerA"]), 3))
    #print(round(expected_service_tech_cy_p["boilerB"], 3) )
    #print(round(np.sum(result["boilerB"]), 3))
    assert round(expected_service_tech_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_service_tech_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

    '''
    return
