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
        year_eff_ey=2020,
        other_enduse_mode_info={'linear'},
        sim_param=sim_param,
        lookups={'fueltype': {'electricity': 2}},
        temp_by=np.zeros((365, 24)) + 10,
        temp_cy=np.zeros((365, 24)) + 10,
        t_base_heating_by=15.5,
        t_base_heating_cy=15.5)

    assert tech.tech_name == "boilerA"
    assert tech.eff_cy == 1.0

    tech2 = technological_stock.Technology(
        tech_name="boilerA",
        tech_type="heat_pump",
        tech_fueltype="electricity",
        tech_eff_achieved=1.0,
        tech_diff_method='linear',
        tech_eff_by=0.5,
        tech_eff_ey=1.0,
        year_eff_ey=2020,
        other_enduse_mode_info={'linear'},
        sim_param=sim_param,
        lookups={'fueltype': {'electricity': 2}},
        temp_by=np.zeros((365, 24)) + 10,
        temp_cy=np.zeros((365, 24)) + 10,
        t_base_heating_by=20,
        t_base_heating_cy=20)

    assert tech2.eff_cy == 1.0

    tech3 = technological_stock.Technology(
        tech_name="dummy_tech",
        tech_type="heating_tech")

    assert tech3.tech_name == "dummy_tech"

def test_TechStock():


    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020,
        'end_yr': 2020,
        'sim_period_yrs': 6}

    all_technologies = {'boilerA': {}}
    all_technologies['boilerA']['fuel_type'] = 'electricity'
    all_technologies['boilerA']['eff_achieved'] = 1.0
    all_technologies['boilerA']['diff_method'] = 'linear'
    all_technologies['boilerA']['eff_by'] = 1.0
    all_technologies['boilerA']['eff_ey'] = 1.0
    all_technologies['boilerA']['year_eff_ey'] = 2020

    stock_obj = technological_stock.TechStock(
        stock_name="stock_name",
        all_technologies=all_technologies,
        tech_list={'tech_heating_temp_dep': [], 'tech_heating_const': ['boilerA']},
        other_enduse_mode_info={'linear'},
        sim_param=sim_param,
        lookups={'fueltype': {'electricity': 2}},
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['boilerA']})

    assert stock_obj.stock_name == "stock_name"
    assert stock_obj.get_tech_attr('heating', 'boilerA', 'eff_by') == 1.0

test_TechStock()