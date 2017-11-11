"""
Testing s_generate_sigmoid
"""
import numpy as np
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.technologies import diffusion_technologies
from energy_demand.technologies import diffusion_technologies

def test_tech_sigmoid_paramters():
    """testng
    """
    assump_fy = 1.0
    result = s_generate_sigmoid.tech_sigmoid_parameters(
        base_yr=2010,
        technologies={'boilerA': {'market_entry': 1990}},
        enduse='heating',
        crit_switch_service=True,
        installed_tech=['boilerA'],
        l_values={'heating': {'boilerA': 1.0}},
        service_tech_by_p={'boilerA': 0.5, 'boilerB': 0.5},
        service_tech_switched_p={'boilerA': assump_fy, 'boilerB': 0},
        fuel_switches=[{'enduse': 'heating', 'technology_install': 'boilerA', 'year_fuel_consumption_switched': 2050}],
        service_switches=[{'tech': 'boilerA', 'year_switch_ey': 2050}])

    y_calculated = diffusion_technologies.sigmoid_function(
        2050, 1.0, result['boilerA']['midpoint'], result['boilerA']['steepness'])

    assert y_calculated >= (assump_fy - 0.02) and y_calculated <= assump_fy + 0.02


    assump_fy = 1.0
    result = s_generate_sigmoid.tech_sigmoid_parameters(
        base_yr=2010,
        technologies={'boilerA': {'market_entry': 1990}},
        enduse='heating',
        crit_switch_service=False,
        installed_tech=['boilerA'],
        l_values={'heating': {'boilerA': 1.0}},
        service_tech_by_p={'boilerA': 0.5, 'boilerB': 0.5},
        service_tech_switched_p={'boilerA': assump_fy, 'boilerB': 0},
        fuel_switches=[{'enduse': 'heating', 'technology_install': 'boilerA', 'year_fuel_consumption_switched': 2050}],
        service_switches=[{'tech': 'boilerA', 'year_switch_ey': 2050}])

    y_calculated = diffusion_technologies.sigmoid_function(
        2050, 1.0, result['boilerA']['midpoint'], result['boilerA']['steepness'])

    assert y_calculated >= (assump_fy - 0.02) and y_calculated <= assump_fy + 0.02

test_tech_sigmoid_paramters()
def test_get_tech_future_service():
    """
    """
    service_tech_by_p = {'heating': {'techA': 0.7, 'techB': 0.3}}
    service_tech_ey_p = {'heating':{'techA': 0.6, 'techB': 0.4}}
    tech_increased_service, tech_decreased_share, tech_constant_share = s_generate_sigmoid.get_tech_future_service(
        service_tech_by_p, service_tech_ey_p)

    assert tech_increased_service ==  {'heating': ['techB']}
    assert tech_decreased_share ==  {'heating': ['techA']}
    assert tech_constant_share == {'heating': []}

def test_calc_sigmoid_parameters():
    """Testing
    """
    l_value = 0.5
    xdata = np.array([2020.0, 2050.0])
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

    assert 'boilerA' in expected['heating']
    assert 'boilerB' in expected['heating']
    assert result['cooking'] == expected['cooking']
