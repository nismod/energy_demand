"""
Testing s_generate_sigmoid
"""
import numpy as np
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.technologies import diffusion_technologies
#from energy_demand.plotting import plotting_program

def test_calc_sigmoid_parameters():
    """Testing
    """
    l_value = 1.0
    xdata = np.array([2020.0, 2050.0]) #[point_x_by, point_x_projected]
    ydata = np.array([0.1, 0.2]) #[point_y_by, point_y_projected]

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    #print("Plot graph: " + str(fit_parameter))
    '''plotting_program.plotout_sigmoid_tech_diff(
        l_value,
        "testtech",
        "test_enduse",
        xdata,
        ydata,
        fit_parameter,
        False # Close windows
        )
    '''
    x_to_test = xdata[1]
    y_calculated = diffusion_technologies.sigmoid_function(x_to_test, l_value, *fit_parameter)

    assert round(y_calculated, 3) == round(ydata[1], 3)
    '''expected_midpoint = 4.4
    expected_slope = None

    # call function
    out_midpoint = fit_parameter[0]
    out_slope = fit_parameter[1]

    assert out_midpoint == out_midpoint
    assert expected_slope == out_slope
    '''
