"""
"""
from energy_demand.technologies import technological_stock
import numpy as np

def test_Technology():
    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'end_yr': 2020,
        'sim_period_yrs': 6}

    tech = technological_stock.Technology(
        tech_name="boilerA",
        tech_type="heating_tech",
        tech_fueltype="electricity",
        tech_eff_achieved=1.0,
        tech_diff_method='linear',
        tech_eff_by=0.5,
        tech_eff_ey=1.0,
        other_enduse_mode_info={'linear'},
        sim_param=sim_param,
        lookups= {'fueltype': {'electricity': 2}},
        temp_by=np.zeros((365, 24)) + 10,
        temp_cy=np.zeros((365, 24)) + 10,
        t_base_heating_by=15.5,
        t_base_heating_cy=15.5)

    assert tech.tech_name == "boilerA"
    assert tech.eff_cy == 1.0
