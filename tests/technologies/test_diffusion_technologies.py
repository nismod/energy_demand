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
        yr_until_changed=2020)
    assert out_value_1 == expected1
    out_value_2 = diffusion_technologies.linear_diff(
        base_yr=2015,
        curr_yr=2016.5,
        value_start=1.0,
        value_end=2.0,
        yr_until_changed=2018)
    assert out_value_2 == expected2
    out_value_3 = diffusion_technologies.linear_diff(
        base_yr=2000,
        curr_yr=2100,
        value_start=0,
        value_end=100.0,
        yr_until_changed=3000)
    assert out_value_3 == expected3
    out_value_4 = diffusion_technologies.linear_diff(
        base_yr=2015,
        curr_yr=2015,
        value_start=0,
        value_end=1,
        yr_until_changed=2015)
    assert out_value_4 == expected4

def test_sigmoid_diffusion():
    """testing
    """
    base_yr = 2015
    curr_yr = 2015
    end_yr = 2020
    sig_midpoint = 0
    sig_steepness = 1

    result = diffusion_technologies.sigmoid_diffusion(
        base_yr,
        curr_yr,
        end_yr,
        sig_midpoint,
        sig_steepness)

    assert result == 0


    base_yr = 2015
    curr_yr = 2020
    end_yr = 2020
    sig_midpoint = 0
    sig_steepness = 1

    result = diffusion_technologies.sigmoid_diffusion(
        base_yr,
        curr_yr,
        end_yr,
        sig_midpoint,
        sig_steepness)

    assert result == 1
    
    # ---

    base_yr = 2015
    curr_yr = 2015
    end_yr = 2020
    sig_midpoint = 0
    sig_steepness = 1

    result = diffusion_technologies.sigmoid_diffusion(
        base_yr,
        curr_yr,
        end_yr,
        sig_midpoint,
        sig_steepness)

    assert result == 0    

    # ---

    base_yr = 2015
    curr_yr = 2020
    end_yr = 2025
    sig_midpoint = 0
    sig_steepness = 1

    result = diffusion_technologies.sigmoid_diffusion(
        base_yr,
        curr_yr,
        end_yr,
        sig_midpoint,
        sig_steepness)

    assert result == 0.5
