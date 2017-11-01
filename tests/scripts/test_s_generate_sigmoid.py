"""
Testing s_generate_sigmoid
"""
import numpy as np
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.technologies import diffusion_technologies

def test_calc_sigmoid_parameters():
    """Testing
    """
    l_value = 0.5
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
    '''
    #from energy_demand.plotting import plotting_program
    plotting_program.plotout_sigmoid_tech_diff(
        l_value,
        "testtech",
        "test_enduse",
        xdata,
        ydata,
        fit_parameter,
        False # Close windows
        )
    '''
    y_calculated = diffusion_technologies.sigmoid_function(xdata[1], l_value, *fit_parameter)

    assert round(y_calculated, 3) == round(ydata[1], 3)

def test_calc_sigmoid_parameters2():
    """Testing
    """
    l_value = 1.0
    xdata = np.array([2020.0, 2060.0])
    ydata = np.array([0, 1])

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    y_calculated = diffusion_technologies.sigmoid_function(xdata[1], l_value, *fit_parameter)

    assert round(y_calculated, 3) == round(ydata[1], 3)

def test_get_tech_installed():

    enduses = ['heating', 'cooking']
    fuel_switches = [
        {
            'enduse' : 'heating',
            'technology_install': 'boilerB'
        },
        {
            'enduse' : 'heating',
            'technology_install': 'boilerA'},
        {
            'enduse' : 'cooking',
            'technology_install': 'techC'
            }
        ]

    result = s_generate_sigmoid.get_tech_installed(enduses, fuel_switches)

    expected = {'heating': ['boilerB', 'boilerA'], 'cooking': ['techC']}

    assert result['heating'] == expected['heating']
    assert result['cooking'] == expected['cooking']
