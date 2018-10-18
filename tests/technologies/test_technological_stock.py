"""
"""
import numpy as np
from energy_demand.technologies import technological_stock

def test_Technology():
    """
    """
    tech = technological_stock.Technology(
        name="boilerA",
        tech_type="heating_tech",
        fueltype_str="electricity",
        eff_achieved=1.0,
        diff_method='linear',
        eff_by=0.5,
        eff_ey=1.0,
        year_eff_ey=2020,
        base_yr=2015,
        curr_yr=2020,
        temp_by=np.zeros((365, 24)) + 10,
        temp_cy=np.zeros((365, 24)) + 10,
        t_base_heating_by=15.5,
        t_base_heating_cy=15.5)

    assert tech.name == "boilerA"
    assert tech.eff_cy == 1.0

    tech2 = technological_stock.Technology(
        name="boilerA",
        tech_type="heat_pump",
        fueltype_str="electricity",
        eff_achieved=1.0,
        diff_method='linear',
        eff_by=0.5,
        eff_ey=1.0,
        year_eff_ey=2020,
        base_yr=2015,
        curr_yr=2020,
        temp_by=np.zeros((365, 24)) + 10,
        temp_cy=np.zeros((365, 24)) + 10,
        t_base_heating_by=20,
        t_base_heating_cy=20)

    assert tech2.eff_cy == 1.0

    tech3 = technological_stock.Technology(
        name="dummy_tech",
        tech_type="heating_tech")

    assert tech3.name == "dummy_tech"

def test_TechStock():

    from energy_demand.read_write import read_data

    base_yr = 2015
    curr_yr = 2020

    all_technologies = {'boilerA': read_data.TechnologyData()}
    all_technologies['boilerA'].fueltype_str = 'electricity'
    all_technologies['boilerA'].eff_achieved = 1.0
    all_technologies['boilerA'].diff_method = 'linear'
    all_technologies['boilerA'].eff_by = 1.0
    all_technologies['boilerA'].eff_ey = 1.0
    all_technologies['boilerA'].year_eff_ey = 2020

    stock_obj = technological_stock.TechStock(
        name="name",
        technologies=all_technologies,
        base_yr=base_yr,
        curr_yr=curr_yr,
        fueltypes={'electricity': 2},
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': {'sectorA': ['boilerA']}})

    assert stock_obj.name == "name"
    assert stock_obj.get_tech_attr('heating', 'sectorA', 'boilerA', 'eff_by') == 1.0
