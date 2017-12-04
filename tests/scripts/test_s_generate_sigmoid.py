"""
Testing s_generate_sigmoid
"""
import numpy as np
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.technologies import diffusion_technologies
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related

def test_tech_sigmoid_paramters():
    """testng
    """
    fuel_switches = [read_data.FuelSwitch(
        enduse='heating',
        technology_install='boilerA',
        switch_yr=2050)]

    service_switches = [read_data.ServiceSwitch(
        technology_install='boilerA',
        switch_yr=2050)]

    technologies = {'boilerA': read_data.TechnologyData(
        market_entry=1990)}

    assump_fy = 1.0
    result = s_generate_sigmoid.tech_sigmoid_parameters(
        base_yr=2010,
        technologies=technologies,
        enduse='heating',
        crit_switch_service=True,
        installed_tech=['boilerA'],
        l_values={'heating': {'boilerA': 1.0}},
        service_tech_by_p={'boilerA': 0.5, 'boilerB': 0.5},
        service_tech_switched_p={'boilerA': assump_fy, 'boilerB': 0},
        fuel_switches=fuel_switches,
        service_switches=service_switches)

    y_calculated = diffusion_technologies.sigmoid_function(
        2050, 1.0, result['boilerA']['midpoint'], result['boilerA']['steepness'])

    assert y_calculated >= (assump_fy - 0.02) and y_calculated <= assump_fy + 0.02
    
    # ------------
    technologies = {'boilerA': read_data.TechnologyData(
        market_entry=1990)}

    assump_fy = 1.0
    result = s_generate_sigmoid.tech_sigmoid_parameters(
        base_yr=2010,
        technologies=technologies,
        enduse='heating',
        crit_switch_service=False,
        installed_tech=['boilerA'],
        l_values={'heating': {'boilerA': 1.0}},
        service_tech_by_p={'boilerA': 0.5, 'boilerB': 0.5},
        service_tech_switched_p={'boilerA': assump_fy, 'boilerB': 0},
        fuel_switches=fuel_switches,
        service_switches=service_switches)

    y_calculated = diffusion_technologies.sigmoid_function(
        2050, 1.0, result['boilerA']['midpoint'], result['boilerA']['steepness'])

    assert y_calculated >= (assump_fy - 0.02) and y_calculated <= assump_fy + 0.02

def test_get_tech_future_service():
    """
    """
    service_tech_by_p = {'heating': {'techA': 0.7, 'techB': 0.3}}
    service_tech_ey_p = {'heating':{'techA': 0.6, 'techB': 0.4}}
    tech_increased_service, tech_decreased_share, tech_constant_share = s_generate_sigmoid.get_tech_future_service(
        service_tech_by_p, service_tech_ey_p)

    assert tech_increased_service == {'heating': {'techB': 0.3}}
    assert tech_decreased_share == {'heating': {'techA': 0.7}}
    assert tech_constant_share == {'heating': {}}

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
    """"""
    enduses = ['heating', 'cooking']
    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB'
        ),
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerA'),
        read_data.FuelSwitch(
            enduse='cooking',
            technology_install='techC'
        )
        ]

    result = s_generate_sigmoid.get_tech_installed(enduses, fuel_switches)

    expected = {'heating': ['boilerB', 'boilerA'], 'cooking': ['techC']}

    assert 'boilerA' in expected['heating']
    assert 'boilerB' in expected['heating']
    assert result['cooking'] == expected['cooking']

def test_calc_service_fuel_switched():
    """
    """
    fueltype_lookup = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'biomass': 5,
        'hydrogen': 6,
        'heat': 7}

    technologies = {
        'boilerA': read_data.TechnologyData(
            fuel_type='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            fueltypes=fueltype_lookup),
        'boilerB': read_data.TechnologyData(
            fuel_type='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            fueltypes=fueltype_lookup),
        'boilerC': read_data.TechnologyData(
            fuel_type='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            fueltypes=fueltype_lookup)}

    enduses = ['heating']

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=1.0
        )]

    service_fueltype_p = {'heating': {1: 1.0, 2: 0.0}}
    service_tech_by_p = {'heating': {'boilerA': 1.0, 'boilerB': 0.0}}
    fuel_tech_p_by = {'heating': {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}}
    installed_tech = {'heating':['boilerB']}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        enduses,
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        installed_tech,
        switch_type='actual_switch')

    assert result['heating']['boilerB'] == 1.0
    assert result['heating']['boilerA'] == 0.0

    # -------

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=3050,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5
        )]

    service_fueltype_p = {'heating': {1: 1.0, 2: 0.0}}
    service_tech_by_p = {'heating': {'boilerA': 1.0, 'boilerB': 0.0}}
    fuel_tech_p_by  = {'heating': {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}}
    installed_tech = {'heating':['boilerB']}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        enduses,
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        installed_tech,
        switch_type='actual_switch')

    assert result['heating']['boilerB'] == 0.5
    assert result['heating']['boilerA'] == 0.5

    # -------

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=3050,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5
        )]

    service_fueltype_p = {'heating': {1: 0.5, 2: 0.5}}
    service_tech_by_p = {'heating': {'boilerA': 0.5, 'boilerB': 0.5}}
    fuel_tech_p_by  = {'heating': {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}}
    installed_tech = {'heating': ['boilerB']}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        enduses,
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        installed_tech,
        switch_type='actual_switch')

    assert result['heating']['boilerB'] == 0.75
    assert result['heating']['boilerA'] == 0.25

    # -------

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=3050,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5
        )]

    service_fueltype_p = {'heating': {1: 0.5, 2: 0.5}}
    service_tech_by_p = {'heating': {'boilerA': 0.25, 'boilerB': 0.5, 'boilerC': 0.25}}
    fuel_tech_p_by  = {'heating': {1: {'boilerA': 0.5, 'boilerC': 0.5,}, 2: {'boilerB': 1.0}}}
    installed_tech = {'heating': ['boilerB']}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        enduses,
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        installed_tech,
        switch_type='actual_switch')

    assert result['heating']['boilerC'] == 0.125
    assert result['heating']['boilerB'] == 0.75
    assert result['heating']['boilerA'] == 0.125

def test_tech_l_sigmoid():
    """testing
    """
    fueltype_lookup = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'biomass': 5,
        'hydrogen': 6,
        'heat': 7}
    technologies = {
        'boilerA': read_data.TechnologyData(
            fuel_type='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup),

        'boilerB': read_data.TechnologyData(
            fuel_type='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup)
        }

    enduses = ['heating']

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=1.0
        )]

    service_fueltype_p = {'heating': {1: 1.0, 2: 0.0}}
    service_tech_by_p = {'heating': {'boilerA': 1.0, 'boilerB': 0.0}}
    fuel_tech_p_by  = {'heating': {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}}
    installed_tech = {'heating':['boilerB']}

    result = s_generate_sigmoid.tech_l_sigmoid(
        enduses,
        fuel_switches,
        technologies,
        installed_tech,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by)

    assert result['heating']['boilerB'] == 1.0

    # -----
    technologies = {
        'boilerA': read_data.TechnologyData(
            fuel_type='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup),

        'boilerB': read_data.TechnologyData(
            fuel_type='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=0.8,
            fueltypes=fueltype_lookup)
        }

    enduses = ['heating']

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5 #info lower than max
        )]

    service_fueltype_p = {'heating': {1: 1.0, 2: 0.0}}
    service_tech_by_p = {'heating': {'boilerA': 1.0, 'boilerB': 0.0}}
    fuel_tech_p_by = {'heating': {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}}
    installed_tech = {'heating':['boilerB']}

    result = s_generate_sigmoid.tech_l_sigmoid(
        enduses,
        fuel_switches,
        technologies,
        installed_tech,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by)

    assert result['heating']['boilerB'] == 0.8


def test_get_sig_diffusion():
    """
    """
    fueltype_lookup = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'biomass': 5,
        'hydrogen': 6,
        'heat': 7}
    base_yr = 2015
    technologies = {
        'boilerA': read_data.TechnologyData(
            fuel_type='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup),
        'boilerC': read_data.TechnologyData(
            fuel_type='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=0.9990,
            fueltypes=fueltype_lookup),
        'boilerB': read_data.TechnologyData(
            fuel_type='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup)}
    enduses = ['heating']
    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=1.0
        )]

    service_switches = []
    tech_increased_service = {'heating': ['boilerA']}
    service_tech_ey_p = {'heating': {'boilerA': 0.6, 'boilerB': 0.4}}
    service_fueltype_p = {'heating': {1:  1.0}}

    result, sig_param = s_generate_sigmoid.get_sig_diffusion(
        base_yr,
        technologies,
        service_switches,
        fuel_switches,
        enduses,
        tech_increased_service,
        service_tech_ey_p,
        service_fueltype_p,
        service_tech_by_p={'heating': {'boilerA': 1.0, 'boilerB': 0.0}},
        fuel_tech_p_by={'heating': {1: {'boilerA': 1.0}, 'electricity': {'boilerB': 1.0}}})

    assert result['heating'] == ['boilerB']

    # -----

    service_switches = [read_data.ServiceSwitch(
        enduse='heating',
        technology_install='boilerC',
        service_share_ey=1.0,
        switch_yr=2050)]

    tech_increased_service = {'heating': ['boilerC']}
    service_tech_ey_p = {'heating': {'boilerC': 1.0, 'boilerA': 0.0, 'boilerB': 0.0}}

    result, sig_param = s_generate_sigmoid.get_sig_diffusion(
        base_yr,
        technologies,
        service_switches,
        fuel_switches,
        enduses,
        tech_increased_service,
        service_tech_ey_p,
        service_fueltype_p,
        service_tech_by_p={'heating': {'boilerC': 1.0, 'boilerA': 0.0, 'boilerB': 0.0}},
        fuel_tech_p_by={'heating': {'gas': {'boilerA': 0, 'boilerC': 1.0}, 'electricity': {'boilerB': 1.0}}})

    #TODO: Possibly add more test

    assert result['heating'] == ['boilerC']
