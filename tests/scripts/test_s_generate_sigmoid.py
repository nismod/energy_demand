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
        installed_tech=['boilerA'],
        l_values={'boilerA': 1.0},
        service_tech_by_p={'boilerA': 0.5, 'boilerB': 0.5},
        service_tech_switched_p={'boilerA': assump_fy, 'boilerB': 0},
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
        installed_tech=['boilerA'],
        l_values={'boilerA': 1.0},
        service_tech_by_p={'boilerA': 0.5, 'boilerB': 0.5},
        service_tech_switched_p={'boilerA': assump_fy, 'boilerB': 0},
        service_switches=service_switches)

    y_calculated = diffusion_technologies.sigmoid_function(
        2050, 1.0, result['boilerA']['midpoint'], result['boilerA']['steepness'])

    assert y_calculated >= (assump_fy - 0.02) and y_calculated <= assump_fy + 0.02

def test_get_tech_future_service():
    """
    """
    service_tech_by_p =  {'techA': 0.7, 'techB': 0.3}
    service_tech_ey_p = {'techA': 0.6, 'techB': 0.4}
    tech_increased_service, tech_decreased_service, tech_constant_service = s_generate_sigmoid.get_tech_future_service(
        service_tech_by_p, service_tech_ey_p)

    assert tech_increased_service == {'techB': 0.4}
    assert tech_decreased_service == {'techA': 0.6}
    assert tech_constant_service == {}

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
        ydata)

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
        ydata)

    y_calculated = diffusion_technologies.sigmoid_function(xdata[1], l_value, *fit_parameter)

    assert round(y_calculated, 3) == round(ydata[1], 3)


def test_calc_sigmoid_parameters3():
    """Testing
    """
    '''l_value = 1.0
    xdata = np.array([2015.0, 2050.0])
    ydata = np.array([0.76246772, 0.07624677])'''
    
    '''l_value = 1.0  #0.01521908  0.04503956
    xdata = np.array([2015.0, 2050.0])
    ydata = np.array([0.015219077406592408, 0.04503955540635414]) '''#[0.015219077406592408, 0.04503955540635414]) #np.array([0.01521908, 0.04503956]) 

    l_value = 1 #0.77 #0.7624677174012964
    xdata = np.array([2015.0, 2050.0])
    #ydata = np.array([0.76246772, 0.07624677])
    ydata = np.array([0.09, 0.09])
    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        error_range=0.01) #0.005

    y_calculated = diffusion_technologies.sigmoid_function(xdata[1], l_value, *fit_parameter)

    # PLOT
    from energy_demand.plotting import plotting_program
    plotting_program.plotout_sigmoid_tech_diff(
        l_value,
        "test technology in test",
        xdata,
        ydata,
        fit_parameter,
        False)

    assert round(y_calculated, 3) == round(ydata[1], 3)

#test_calc_sigmoid_parameters3()

def test_get_tech_installed():
    """"""
    enduse = 'heating'
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

    result = s_generate_sigmoid.get_tech_installed(enduse, fuel_switches)

    expected = {'heating': ['boilerB', 'boilerA']}

    assert 'boilerA' in expected['heating']
    assert 'boilerB' in expected['heating']

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
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            fueltypes=fueltype_lookup),
        'boilerB': read_data.TechnologyData(
            fueltype='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            fueltypes=fueltype_lookup),
        'boilerC': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            fueltypes=fueltype_lookup)}

    enduse = 'heating'

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=1.0
        )]

    service_fueltype_p = {1: 1.0, 2: 0.0}
    service_tech_by_p = {'boilerA': 1.0, 'boilerB': 0.0}
    fuel_tech_p_by = {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type='actual_switch')

    assert result['boilerB'] == 1.0
    assert result['boilerA'] == 0.0

    # -------

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=3050,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5
        )]

    service_fueltype_p = {1: 1.0, 2: 0.0}
    service_tech_by_p = {'boilerA': 1.0, 'boilerB': 0.0}
    fuel_tech_p_by = {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type='actual_switch')

    assert result['boilerB'] == 0.5
    assert result['boilerA'] == 0.5

    # -------

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=3050,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5
        )]

    service_fueltype_p = {1: 0.5, 2: 0.5}
    service_tech_by_p = {'boilerA': 0.5, 'boilerB': 0.5}
    fuel_tech_p_by = {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type='actual_switch')

    assert result['boilerB'] == 0.75
    assert result['boilerA'] == 0.25

    # -------

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=3050,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5
        )]

    service_fueltype_p = {1: 0.5, 2: 0.5}
    service_tech_by_p = {'boilerA': 0.25, 'boilerB': 0.5, 'boilerC': 0.25}
    fuel_tech_p_by  = {1: {'boilerA': 0.5, 'boilerC': 0.5,}, 2: {'boilerB': 1.0}}

    result = s_generate_sigmoid.calc_service_fuel_switched(
        fuel_switches,
        technologies,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type='actual_switch')

    assert result['boilerC'] == 0.125
    assert result['boilerB'] == 0.75
    assert result['boilerA'] == 0.125

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
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup),

        'boilerB': read_data.TechnologyData(
            fueltype='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup)
        }

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=1.0
        )]

    service_fueltype_p =  {1: 1.0, 2: 0.0}
    service_tech_by_p = {'boilerA': 1.0, 'boilerB': 0.0}
    fuel_tech_p_by  = {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}
    installed_tech = ['boilerB']

    result = s_generate_sigmoid.tech_l_sigmoid(
        fuel_switches,
        technologies,
        installed_tech,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by)

    assert result['boilerB'] == 1.0

    # -----
    technologies = {
        'boilerA': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup),

        'boilerB': read_data.TechnologyData(
            fueltype='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=0.8,
            fueltypes=fueltype_lookup)
        }

    fuel_switches = [
        read_data.FuelSwitch(
            enduse='heating',
            technology_install='boilerB',
            switch_yr=2020,
            enduse_fueltype_replace=tech_related.get_fueltype_int(fueltype_lookup, 'gas'),
            fuel_share_switched_ey=0.5 #info lower than max
        )]

    service_fueltype_p = {1: 1.0, 2: 0.0}
    service_tech_by_p = {'boilerA': 1.0, 'boilerB': 0.0}
    fuel_tech_p_by = {1: {'boilerA': 1.0}, 2: {'boilerB': 1.0}}
    installed_tech = ['boilerB']

    result = s_generate_sigmoid.tech_l_sigmoid(
        fuel_switches,
        technologies,
        installed_tech,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by)

    assert result['boilerB'] == 0.8

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

    technologies = {
        'boilerA': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup),
        'boilerC': read_data.TechnologyData(
            fueltype='gas',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=0.999,
            fueltypes=fueltype_lookup),
        'boilerB': read_data.TechnologyData(
            fueltype='electricity',
            eff_by=0.5,
            eff_ey=0.5,
            year_eff_ey=2015,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=1990,
            tech_max_share=1.0,
            fueltypes=fueltype_lookup)}

    tech_increased_service = ['boilerA']
    service_tech_ey_p =  {'boilerA': 0.6, 'boilerB': 0.4}

    sig_param = s_generate_sigmoid.get_l_values(
        technologies,
        tech_increased_service,
        service_tech_ey_p)

    assert sig_param['boilerA'] == 1.0

    # -----

    tech_increased_service = ['boilerC']
    service_tech_ey_p = {'boilerC': 0.5, 'boilerA': 0.0, 'boilerB': 0.0}

    sig_param = s_generate_sigmoid.get_l_values(
        technologies,
        tech_increased_service,
        service_tech_ey_p)


    assert sig_param['boilerC'] == 0.999
