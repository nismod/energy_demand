"""
"""
from energy_demand.technologies import diffusion_technologies

def test_linear_diff():
    """Testing function
    """
    expected1 = 1
    expected2 = 1.5
    expected3 = 10
    expected4 = 0

    # call function
    out_value_1 = diffusion_technologies.linear_diff(
        base_yr=2015,
        curr_yr=2020,
        value_start=0.0,
        value_end=1.0,
        sim_years=6
        )
    assert out_value_1 == expected1
    out_value_2 = diffusion_technologies.linear_diff(
        base_yr=2015,
        curr_yr=2016.5,
        value_start=1.0,
        value_end=2.0,
        sim_years=4 #until 2018
        )
    assert out_value_2 == expected2
    out_value_3 = diffusion_technologies.linear_diff(
        base_yr=2000,
        curr_yr=2100,
        value_start=0,
        value_end=100.0,
        sim_years=1001.0
        )
    assert out_value_3 == expected3
    out_value_4 = diffusion_technologies.linear_diff(
        base_yr=2015,
        curr_yr=2015,
        value_start=0,
        value_end=1,
        sim_years=0
        )
    assert out_value_4 == expected4
