"""Script to fit technology diffusion

This script calculates the three parameters of a sigmoid diffusion
for every technology which is diffused and has a larger service
fraction at the model end year
"""
import sys
import logging
from collections import defaultdict
import numpy as np
from scipy.optimize import curve_fit
from energy_demand.technologies import diffusion_technologies

def calc_sigmoid_parameters(l_value, xdata, ydata):
    """Calculate sigmoid parameters. Check if fitting is good enough.

    Arguments
    ----------
    l_value : float
        Maximum upper level
    xdata : array
        X data
    ydata : array
        Y data
    fit_crit_max : float
        Criteria to control and abort fit
    fit_crit_min : float
        Criteria to control and abort fit (slope must be posititive)

    Returns
    ------
    fit_parameter : array
        Parameters (first position: midpoint, second position: slope)
    """
    # ---------------------------------------------
    # Generate possible starting parameters for fit
    # ---------------------------------------------
    '''start_param_list = []

    for start in [x * 0.05 for x in range(0, 100)]:
        start_param_list.append(float(start))

    for start in [1.0, 0.001, 0.01, 0.1, 60.0, 100.0, 200.0, 400.0, 500.0, 1000.0]:
        start_param_list.append(float(start))

    for start in range(1, 59):
        start_param_list.append(float(start))'''
    start_param_list = [
        0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65,
        0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35,
        1.4, 1.45, 1.5, 1.55, 1.6, 1.650, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05,
        2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6, 2.65, 2.7, 2.75,
        2.8, 2.85, 2.9, 2.95, 3.0, 3.05, 3.1, 3.15, 3.2, 3.25, 3.3, 3.35, 3.40, 3.45,
        3.5, 3.55, 3.6, 3.65, 3.7, 3.75, 3.8, 3.85, 3.9, 3.95, 4.0, 4.05, 4.1, 4.15,
        4.2, 4.25, 4.3, 4.35, 4.4, 4.45, 4.5, 4.55, 4.6, 4.65, 4.7, 4.75, 4.8, 4.85,
        4.9, 4.95, 1.0, 0.001, 0.01, 0.1, 60.0, 100.0, 200.0, 400.0, 500.0, 1000.0,
        1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0,
        15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0,
        28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0,
        41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0,
        54.0, 55.0, 56.0, 57.0, 58.0]

    # ---------------------------------------------
    # Fit
    # ---------------------------------------------
    cnt = 0
    successfull = False
    while not successfull:
        try:
            start_parameters = [
                start_param_list[cnt],
                start_param_list[cnt]]

            # Fit function
            fit_parameter = fit_sigmoid_diffusion(
                l_value, xdata, ydata, start_parameters)

            #logging.debug("Fit parameters: %s %s %s", fit_parameter, xdata, ydata)

            # Fit must be positive and paramaters not input parameters
            if (fit_parameter[1] < 0) or (
                fit_parameter[0] == start_parameters[0]) or (
                    fit_parameter[1] == start_parameters[1]):
                cnt += 1
                if cnt >= len(start_param_list):
                    logging.critical("Error: Sigmoid curve fitting failed")
            else:
                successfull = True

                # -------------------------
                # Check how good the fit is
                # -------------------------
                y_calculated = diffusion_technologies.sigmoid_function(
                    xdata[1], l_value, *fit_parameter)

                fit_measure_in_percent = (100.0 / ydata[1]) * y_calculated
                if fit_measure_in_percent < 99.0:
                    logging.debug("... Fitting measure %s (percent) is not good enough", fit_measure_in_percent)

        except (RuntimeError, IndexError):
            #logging.debug("Unsuccessful fit %s %s", start_parameters[0], start_parameters[1])
            cnt += 1

            if cnt >= len(start_param_list):
                logging.critical("Check whether start year is <= the year 2000")
                logging.critical("Sigmoid fit error: Try changing fit_crit_max and fit_crit_min")
                sys.exit()

    return fit_parameter

def get_tech_future_service(
        service_tech_by_p,
        service_tech_ey_p,
        regions=False,
        regional_specific=False
    ):
    """Get all those technologies with increased service in future year

    Arguments
    ----------
    service_tech_by_p : dict
        Share of service per technology of base year of total service
    service_tech_ey_p : dict
        Share of service per technology of future year of total service
    regions : dict
        Regions
    regional_specific : bool
        Criteria to decide whether the function is executed
        for individual regions or not

    Returns
    -------
    tech_increased_service : dict
        Technologies with increased future service
    tech_decreased_service : dict
        Technologies with decreased future service
    tech_decreased_service : dict
        Technologies with unchanged future service
    """
    tech_increased_service = defaultdict(dict)
    tech_decreased_service = defaultdict(dict)
    tech_constant_service = defaultdict(dict)

    if regional_specific:
        for reg in regions:

            # If no service switch defined
            if service_tech_ey_p[reg] == {}:
                pass
            else:
                for tech in service_tech_by_p.keys():
                    if tech == 'dummy_tech':
                        pass
                    else:
                        # Check if larger, smaller or identical
                        if round(service_tech_by_p[tech], 4) < round(service_tech_ey_p[reg][tech], 4):
                            tech_increased_service[reg][tech] = service_tech_ey_p[reg][tech]
                        elif round(service_tech_by_p[tech], 4) > round(service_tech_ey_p[reg][tech], 4):
                            tech_decreased_service[reg][tech] = service_tech_ey_p[reg][tech]
                        else:
                            tech_constant_service[reg][tech] = service_tech_ey_p[reg][tech]
    else:
        if service_tech_ey_p == {}: # If no service switch defined
            pass
        else:
            for tech in service_tech_by_p.keys():
                if tech == 'dummy_tech':
                    pass
                else:
                    # Check if larger, smaller or identical
                    if round(service_tech_by_p[tech], 4) < round(service_tech_ey_p[tech], 4):
                        tech_increased_service[tech] = service_tech_ey_p[tech]
                    elif round(service_tech_by_p[tech], 4) > round(service_tech_ey_p[tech], 4):
                        tech_decreased_service[tech] = service_tech_ey_p[tech]
                    else:
                        tech_constant_service[tech] = service_tech_ey_p[tech]

    return dict(tech_increased_service), dict(tech_decreased_service), dict(tech_constant_service)

def fit_sigmoid_diffusion(l_value, x_data, y_data, start_parameters):
    """Fit sigmoid curve based on two points on the diffusion curve

    Arguments
    ----------
    l_value : float
        The sigmoids curve maximum value (max consumption)
    x_data : array
        X coordinate of two points
    y_data : array
        X coordinate of two points

    Returns
    -------
    popt : dict
        Fitting parameters

    Note
    ----
    The Sigmoid is substacted - 2000 to allow for better fit with low values

    Warning
    -------
    It cannot fit a value starting from 0. Therefore, some initial penetration needs
    to be assumed (e.g. 0.001%)
    RuntimeWarning is ignored
    https://stackoverflow.com/questions/4359959/overflow-in-exp-in-scipy-numpy-in-python
    """
    def sigmoid_fitting_function(x_value, x0_value, k_value):
        """Sigmoid function used for fitting
        """
        with np.errstate(over='ignore'): #RuntimeWarning: overflow encountered in exp
            y_value = l_value / (1 + np.exp(-k_value * ((x_value - 2000.0) - x0_value)))
            return y_value

    popt, _ = curve_fit(
        sigmoid_fitting_function,
        x_data,
        y_data,
        p0=start_parameters,
        maxfev=10000) # Numer of iterations

    return popt

def tech_l_sigmoid(
        enduse_fuel_switches,
        technologies,
        installed_tech,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by
    ):
    """Calculate L value (maximum possible theoretical market penetration)
    for every installed technology with maximum theoretical replacement
    share (calculate second sigmoid point).

    Arguments
    ----------
    enduse_fuel_switches : dict
        Fuel switches of enduse
    installed_tech : dict
        Installed technologies (as keys)
    service_fueltype_by_p : dict
        Service share per fueltye of base year
    service_tech_by_p : dict
        Percentage of service demands for every technology
    fuel_tech_p_by : dict
        Fuel share per technology of base year

    Returns
    -------
    l_values_sig : dict
        L value for sigmoid diffusion of all technologies
        for which a switch is implemented
    """
    l_values_sig = {}

    # Check wheter there are technologies in this enduse which are switched
    if installed_tech == []:
        pass
    else:
        logging.debug("Technologes it calculate sigmoid %s ", installed_tech)

        # Iterite list with enduses where fuel switches are defined
        for technology in installed_tech:
            logging.debug("Technology: %s", technology)

            # Calculate service demand for specific tech
            tech_install_p = calc_service_fuel_switched(
                enduse_fuel_switches,
                technologies,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by,
                'max_switch')

            # Read L-values with calculating maximum sigmoid theoretical diffusion
            l_values_sig[technology] = tech_install_p[technology]

    return l_values_sig

def calc_service_fuel_switched(
        enduse_fuel_switches,
        technologies,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type
    ):
    """Calculate energy service demand percentages after fuel switches


    TODO CLEAN AN IMPROVE

    Arguments
    ----------
    enduse_fuel_switches : dict
        Fuel switches of specific enduse
    technologies : dict
        Technologies
    service_fueltype_by_p : dict
        Service share per fueltype
    service_tech_by_p : dict
        Share of service demand per technology for base year
    fuel_tech_p_by : dict
        Fuel shares for each technology of an enduse
    switch_type : str
        If either switch is for maximum theoretical switch
        of with defined switch until end year

    Return
    ------
    service_tech_switched_p : dict
        Service in future year with added and substracted
        service demand for every technology

    Note
    ----
    Implement changes in heat demand (all technolgies within
    a fueltypes are replaced proportionally)
    """
    service_tech_switched_p = {}

    for fuel_switch in enduse_fuel_switches:
        tech_install = fuel_switch.technology_install
        fueltype_tech_replace = fuel_switch.enduse_fueltype_replace

        # Share of energy service before switch
        service_p_by = service_fueltype_by_p[fueltype_tech_replace]

        # Service demand per fueltype that will be switched
        # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent
        if switch_type == 'max_switch':
            change_service_fueltype_by_p = service_p_by * technologies[tech_install].tech_max_share
        elif switch_type == 'actual_switch':
            change_service_fueltype_by_p = service_p_by * fuel_switch.fuel_share_switched_ey

        # ---Service addition
        service_tech_switched_p[tech_install] = service_tech_by_p[tech_install] + change_service_fueltype_by_p

        # Get all technologies which are replaced related to this fueltype
        replaced_tech_fueltype = fuel_tech_p_by[fueltype_tech_replace].keys()

        # Substract service demand for replaced technologies
        for tech in replaced_tech_fueltype:
            service_tech_switched_p[tech] = service_tech_by_p[tech] - (change_service_fueltype_by_p * fuel_tech_p_by[fueltype_tech_replace][tech])

    # -----------------------
    # Calculate service fraction of all technologies in enduse not affected
    # by fuel switch TODO WRITE MORE DOCU
    # -----------------------
    affected_service_p_ey = sum(service_tech_switched_p.values())

    remaining_service_to_distr_p = 1 - affected_service_p_ey

    # Calculate service fraction of remaining technologies
    all_fractions_unaffected_switch = {}
    for tech in service_tech_by_p:
        if tech not in service_tech_switched_p.keys():
            all_fractions_unaffected_switch[tech] = service_tech_by_p[tech]

    # Iterate all technologies of enduse_by
    service_tot_remaining = sum(all_fractions_unaffected_switch.values())

    # Get relative distribution of all not affected techs
    for tech in all_fractions_unaffected_switch:

        # Relative share
        rel_service_fraction_p = all_fractions_unaffected_switch[tech] / service_tot_remaining
        service_tech_switched_p[tech] = rel_service_fraction_p * remaining_service_to_distr_p

    return dict(service_tech_switched_p)

def get_tech_installed(enduse, fuel_switches):
    """Read out all technologies which are specifically switched
    to of a specific enduse

    Parameter
    ---------
    enduse : str
        enduse
    fuel_switches : dict
        All fuel switches where a share of a fuel
        of an enduse is switched to a specific technology

    Return
    ------
    installed_tech : list
        List with all technologies where a fuel share is switched to
    """
    # Add technology list for every enduse with affected switches
    installed_tech = set([])

    for switch in fuel_switches:
        if switch.enduse == enduse:
            installed_tech.add(switch.technology_install)

    # Convert set to lists
    return list(installed_tech)

def get_l_values(
        technologies,
        tech_increased_service,
        regions=False,
        regional_specific=False
    ):
    """Get l values (Maximum shares of each technology)
    for all installed technologies

    Arguments
    ----------
    technologies : dict
        Technologies
    tech_increased_service : list
        Technologies with increased service (installed technologies)
    service_fueltype_by_p :
        Fraction of service per fueltype in base year
    regions : dict
        Regions
    regional_specific : bool
        Criteria if calculation for a specific region or not

    Return
    ------
    service_tech_switched_p : dict
        Share of service per technology after switch
    l_values_sig : dict
        Sigmoid paramters of all installed technologies
    """
    l_values_sig = defaultdict(dict)

    if regional_specific:
        for reg in regions:
            for tech in tech_increased_service[reg]:
                l_values_sig[reg][tech] = technologies[tech].tech_max_share
    else:
        if tech_increased_service == []:
            pass
        else:
            for tech in tech_increased_service:
                l_values_sig[tech] = technologies[tech].tech_max_share

    return dict(l_values_sig)

def calc_diff_fuel_switch(
        technologies,
        enduse_fuel_switches,
        installed_tech,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by,
        regions=False,
        regional_specific=False
    ):
    """Calculates parameters for sigmoid diffusion of
    technologies which are switched to/installed.

    Arguments
    ----------
    data : dict
        Data
    service_switches : dict
        Service switches
    enduse_fuel_switches : dict
        Fuel switches
    enduse : str
        Enduse
    tech_increased_service : list
        Technologies with increased service
        (tech with lager service shares in end year)
    service_tech_ey_p : dict
        Fraction of service in end year
    service_fueltype_by_p :
        Fraction of service per fueltype in base year
    service_tech_by_p :
        Fraction of service per technology in base year
    fuel_tech_p_by :
        Fraction of fuel per technology in base year
    regional_specific : bool
        Whether the calculation is for all regions or not

    TODO: HWERE FUEL SWTICH IS IMPLEMENTED

    Return
    ------
    data : dict
        Data dictionary containing all calculated
        parameters in assumptions

    Note
    ----
    It is assumed that the technology diffusion is the same over
    all the uk (no regional different diffusion)
    """
    if regional_specific:
        l_values_sig = {}
        service_tech_switched_p = {}

        for reg in regions:

            # Calculate service demand after fuel switches for each technology
            service_tech_switched_p[reg] = calc_service_fuel_switched(
                enduse_fuel_switches,
                technologies,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by,
                'actual_switch')

            # Calculate L for every technology for sigmod diffusion
            l_values_sig[reg] = tech_l_sigmoid(
                enduse_fuel_switches,
                technologies,
                installed_tech,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by)
    else:
        # Calculate future service demand after fuel switches for each technology
        service_tech_switched_p = calc_service_fuel_switched(
            enduse_fuel_switches,
            technologies,
            service_fueltype_by_p,
            service_tech_by_p,
            fuel_tech_p_by,
            'actual_switch')

        # Calculate L for every technology for sigmod diffusion
        l_values_sig = tech_l_sigmoid(
            enduse_fuel_switches,
            technologies,
            installed_tech,
            service_fueltype_by_p,
            service_tech_by_p,
            fuel_tech_p_by)

    return dict(service_tech_switched_p), dict(l_values_sig)

def calc_sigm_parameters(
        base_yr,
        technologies,
        l_values_sig,
        service_tech_by_p,
        service_tech_switched_p,
        service_switches,
        tech_increased_service,
        regions=False,
        regional_specific=False
    ):
    """
    Calculates parameters for sigmoid diffusion of
    technologies which are switched to/installed. With
    `regional_specific` the assumption can be changed that
    the technology diffusion is the same over all the uk
    (if `regional_specific`== False, no regionally different diffusion)

    Arguments
    ---------
    base_yr : int
        Base year
    technologies : dict
        Technologies
    l_values_sig : dict
        Maximum diffusion (l_values) of technologies
    service_tech_by_p : dict
        Service share per technology for base year
    service_tech_switched_p : dict
        Service share per technology after switch
    service_switches : list
        Service switches
    tech_increased_service : dict
        Technologies with increased service in end year
    regions : dict, default=False
        Regions
    regional_specific : bool, default=False
        Criteria if regional specific calcuations

    Returns
    -------
    sig_param_tech : dict
        Sigmoid parameters for increasing technologies
    """
    sig_param_tech = {}

    if regional_specific:
        for reg in regions:
            installed_techs = tech_increased_service[reg].keys()

            # Calclulate sigmoid parameters for every installed technology
            sig_param_tech[reg] = tech_sigmoid_parameters(
                base_yr,
                technologies,
                installed_techs,
                l_values_sig[reg],
                service_tech_by_p,
                service_tech_switched_p[reg],
                service_switches[reg])
    else:
        installed_techs = list(tech_increased_service.keys())

        # Calclulate sigmoid parameters for every installed technology
        sig_param_tech = tech_sigmoid_parameters(
            base_yr,
            technologies,
            installed_techs,
            l_values_sig,
            service_tech_by_p,
            service_tech_switched_p,
            service_switches)

    return sig_param_tech

def tech_sigmoid_parameters(
        base_yr,
        technologies,
        installed_tech,
        l_values,
        service_tech_by_p,
        service_tech_switched_p,
        service_switches):
    """Calculate diffusion parameters based on energy service
    demand in base year and projected future energy service demand

    The future energy servie demand is calculated based on fuel switches.
    A sigmoid diffusion is fitted.

    Arguments
    ----------
    base_yr : dict
        base year
    technologies : dict
        technologies
    installed_tech : list or dict
        Installed technologies
    installed_tech : list
        List with installed technologies in fuel switches
    l_values : dict
        L values for maximum possible diffusion of technologies
    service_tech_by_p : dict
        Energy service demand for base year (1.sigmoid point)
    service_tech_switched_p : dict
        Service demand after fuelswitch

    Returns
    -------
    sigmoid_parameters : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)
    """
    # As fit does not work with a starting point of 0,
    # an initial small value needs to be assumed
    fit_assump_init = 0.001

    sigmoid_parameters = defaultdict(dict)

    # Fitting criteria where the calculated sigmoid slope and midpoint can be provided limits
    if installed_tech == []:
        logging.debug("NO TECHNOLOGY.. %s", installed_tech)
    else:
        for tech in installed_tech:
            logging.debug("... create sigmoid diffusion parameters %s", tech)

            # Get year until switched
            for switch in service_switches:
                if switch.technology_install == tech:
                    yr_until_switched = switch.switch_yr
                    break

            market_entry = technologies[tech].market_entry

            # --------
            # Test whether technology has the market entry before or after base year,
            # If afterwards, set very small number in market entry year
            # --------
            if market_entry > base_yr:
                point_x_by = market_entry
                point_y_by = fit_assump_init
            else: # If market entry before, set to 2015
                point_x_by = base_yr
                point_y_by = service_tech_by_p[tech] # current service share

                #If the base year is the market entry year use a very small number
                if point_y_by == 0:
                    point_y_by = fit_assump_init

            # Future energy service demand (second point on sigmoid curve for fitting)
            point_x_projected = yr_until_switched
            point_y_projected = service_tech_switched_p[tech]

            # Data of the two points
            xdata = np.array([point_x_by, point_x_projected])
            ydata = np.array([point_y_by, point_y_projected])

            # ----------------
            # Parameter fitting
            # ----------------
            fit_parameter = calc_sigmoid_parameters(
                l_values[tech], xdata, ydata)

            logging.debug(
                " ... Fitting: Midpoint: %s steepness: %s", fit_parameter[0], fit_parameter[1])

            # Insert parameters
            sigmoid_parameters[tech]['midpoint'] = fit_parameter[0] # midpoint (x0)
            sigmoid_parameters[tech]['steepness'] = fit_parameter[1] # Steepnes (k)
            sigmoid_parameters[tech]['l_parameter'] = l_values[tech] # maximum p

            #plot sigmoid curve
            '''from energy_demand.plotting import plotting_program
            plotting_program.plotout_sigmoid_tech_diff(
                 l_values[enduse][tech],
                 tech,
                 enduse,
                 xdata,
                 ydata,
                 fit_parameter,
                 False)'''

    return dict(sigmoid_parameters)
