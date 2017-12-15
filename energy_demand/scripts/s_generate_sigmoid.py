"""Script to fit technology diffusion

This script calculates the three parameters of a sigmoid diffusion
for every technology which is diffused and has a larger service
fraction at the model end year
"""
import logging
from collections import defaultdict
import numpy as np
from scipy.optimize import curve_fit
from energy_demand.technologies import diffusion_technologies

def calc_sigmoid_parameters(l_value, xdata, ydata): #, fit_crit_max=400, fit_crit_min=0.00001):
    """Calculate sigmoid parameters

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

    #TODO: Implement that if fitting files, straight line?
    Returns
    ------
    fit_parameter : array
        Parameters (first position: midpoint, second position: slope)
    """
    # Generate possible starting parameters for fit
    start_param_list = []

    for start in [x * 0.05 for x in range(0, 100)]:
        start_param_list.append(float(start))

    for start in [1.0, 0.001, 0.01, 0.1, 60.0, 100.0, 200.0, 400.0, 500.0, 1000.0]:
        start_param_list.append(float(start))

    for start in range(1, 59):
        start_param_list.append(float(start))

    cnt = 0
    successfull = False
    while not successfull:
        try:
            start_parameters = [
                start_param_list[cnt],
                start_param_list[cnt]]

            # Fit function
            fit_parameter = fit_sigmoid_diffusion(
                l_value,
                xdata,
                ydata,
                start_parameters)

            logging.debug("Fit parameters: %s %s %s", fit_parameter, xdata, ydata)
            '''logging.debug("Fit parameters: %s", fit_parameter)
            from energy_demand.plotting import plotting_program
            #plot sigmoid curve
            plotting_program.plotout_sigmoid_tech_diff(
                l_value,
                "GG",
                "DD",
                xdata,
                ydata,
                fit_parameter,
                False)'''

            # Criteria when fit did not work
            '''if (fit_parameter[0] > fit_crit_max) or (
                fit_parameter[0] < fit_crit_min) or (
                    fit_parameter[1] > fit_crit_max) or (
                        fit_parameter[1] < 0) or (
                            fit_parameter[0] == start_parameters[0]) or (
                                fit_parameter[1] == start_parameters[1]) or (
                                    fit_parameter[0] == fit_parameter[1]):'''
            # Fit must be positive and paramaters not input parameters
            if (fit_parameter[1] < 0) or (fit_parameter[0] == start_parameters[0]) or (fit_parameter[1] == start_parameters[1]):
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
                print("... Fitting measure in percent: %s", fit_measure_in_percent)

                if fit_measure_in_percent < 99.0:
                    logging.critical("The sigmoid fitting is not good enough")

        except (RuntimeError, IndexError):
            print("Unsuccessful fit %s", start_parameters[0], start_parameters[1])
            cnt += 1

            if cnt >= len(start_param_list):
                print("Check whether start year is <= the year 2000")
                logging.critical("Sigmoid fit error: Try changing fit_crit_max and fit_crit_min")
                import sys
                sys.exit()

    return fit_parameter

def tech_sigmoid_parameters(
        base_yr,
        technologies,
        enduse,
        crit_switch_service,
        installed_tech,
        l_values,
        service_tech_by_p,
        service_tech_switched_p,
        fuel_switches,
        service_switches
    ):
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
    enduse : str
        Enduse
    crit_switch_service : bool
        Criteria whether sigmoid is calculated for service switch or not

    installed_tech : list
        List with installed technologies in fuel switches
    l_values : dict
        L values for maximum possible diffusion of technologies
    service_tech_by_p : dict
        Energy service demand for base year (1.sigmoid point)
    service_tech_switched_p : dict
        Service demand after fuelswitch
    fuel_switches : dict
        Fuel switch information

    Returns
    -------
    sigmoid_parameters : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)

    Notes
    -----
    Manually the fitting parameters can be defined which are not considered as
    a good fit: fit_crit_max, fit_crit_min
    If service definition, the year until switched is the end model year
    """
    # As fit does not work with a starting point of 0,
    # an initial small value needs to be assumed
    fit_assump_init = 0.001

    sigmoid_parameters = defaultdict(dict)

    # Fitting criteria where the calculated sigmoid slope and midpoint can be provided limits
    if installed_tech == []:
        logging.debug("NO TECHNOLOGY...%s %s", enduse, installed_tech)
    else:
        for tech in installed_tech:
            logging.debug("... create sigmoid diffusion parameters %s %s", enduse, tech)

            # If service switch
            if crit_switch_service:

                # Get year until switched
                for switch in service_switches:
                    if switch.technology_install == tech:
                        yr_until_switched = switch.switch_yr

                market_entry = technologies[tech].market_entry
            else: #fuel switch

                # Get the most future year of the technology in the enduse which is switched to
                yr_until_switched = 0
                for switch in fuel_switches:
                    if switch.enduse == enduse and switch.technology_install == tech:
                        if yr_until_switched < switch.switch_yr:
                            yr_until_switched = switch.switch_yr

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
                l_values[enduse][tech],
                xdata,
                ydata)

            logging.debug(
                " ... Fitting: Midpoint: %s steepness: %s", fit_parameter[0], fit_parameter[1])

            # Insert parameters
            sigmoid_parameters[tech]['midpoint'] = fit_parameter[0] #midpoint (x0)
            sigmoid_parameters[tech]['steepness'] = fit_parameter[1] #Steepnes (k)
            sigmoid_parameters[tech]['l_parameter'] = l_values[enduse][tech]

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

def get_tech_future_service(service_tech_by_p, service_tech_ey_p, regions=False, regional_specific=False):
    """Get all those technologies with increased service in future

    Arguments
    ----------
    service_tech_by_p : dict
        Share of service per technology of base year of total service
    service_tech_ey_p : dict
        Share of service per technology of end year of total service
    regions : dict
        Regions
    regional_specific : bool
        Criteria to decide whether the function is executed
        for individual regions only once

    Returns
    -------
    assumptions : dict
        assumptions

    Note
    -----
    tech_increased_service : dict
        Technologies with increased future service
    tech_decreased_share : dict
        Technologies with decreased future service
    tech_decreased_share : dict
        Technologies with unchanged future service

    The assumptions are always relative to the simulation end year
    """
    tech_increased_service = defaultdict(dict)
    tech_decreased_share = defaultdict(dict)
    tech_constant_share = defaultdict(dict)

    if regional_specific:
        for reg in regions:

            # If no service switch defined
            if service_tech_ey_p[reg] == {}:
                tech_increased_service[reg] = []
                tech_decreased_share[reg] = []
                tech_constant_share[reg] = []
            else:
                tech_increased_service[reg] = {}
                tech_decreased_share[reg] = {}
                tech_constant_share[reg] = {}

                # Calculate fuel for each tech
                for tech in service_tech_by_p.keys():
                    if tech == 'dummy_tech':
                        pass
                    else:
                        tech_by_p = round(service_tech_by_p[tech], 4)
                        tech_ey_p = round(service_tech_ey_p[reg][tech], 4)

                        if tech_by_p < tech_ey_p: #future larger
                            tech_increased_service[reg][tech] = service_tech_ey_p[reg][tech]
                        elif tech_by_p > tech_ey_p: #future smaller
                            tech_decreased_share[reg][tech] = service_tech_ey_p[reg][tech]
                        else: #same
                            tech_constant_share[reg][tech] = service_tech_ey_p[reg][tech]
    else:

        # If no service switch defined
        if service_tech_ey_p == {}:
            tech_increased_service = []
            tech_decreased_share = []
            tech_constant_share = []
        else:

            # Calculate fuel for each tech
            for tech in service_tech_by_p.keys():
                if tech == 'dummy_tech':
                    pass
                else:
                    tech_by_p = round(service_tech_by_p[tech], 4)
                    tech_ey_p = round(service_tech_ey_p[tech], 4)

                    if tech_by_p < tech_ey_p: #future larger
                        tech_increased_service[tech] = service_tech_ey_p[tech]
                    elif tech_by_p > tech_ey_p: #future smaller
                        tech_decreased_share[tech] = service_tech_ey_p[tech]
                    else: #same
                        tech_constant_share[tech] = service_tech_ey_p[tech]

    return dict(tech_increased_service), dict(tech_decreased_share), dict(tech_constant_share)

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
    It cannot fit a value starting from 0. Therfore, some initial penetration needs
    to be assumed (e.g. 0.001%)
    RuntimeWarning is ignored
    https://stackoverflow.com/questions/4359959/overflow-in-exp-in-scipy-numpy-in-python
    """
    def sigmoid_fitting_function(x_value, x0_value, k_value):
        """Sigmoid function used for fitting
        """
        #RuntimeWarning: overflow encountered in exp
        with np.errstate(over='ignore'):
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
        enduse,
        fuel_switches,
        technologies,
        installed_tech,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by
    ):
    """Calculate L value (maximum possible theoretical market penetration)
    for every installed technology with maximum theoretical replacement value

    Arguments
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    assumptions : dict
        Assumptions
    service_tech_by_p : dict
        Percentage of service demands for every technology

    Returns
    -------
    l_values_sig : dict
        L value for sigmoid diffusion of all technologies
        for which a switch is implemented

    Notes
    -----
    Gets second sigmoid point
    """
    l_values_sig = {}

    # Check wheter there are technologies in this enduse which are switched
    if installed_tech[enduse] == []: #[enduse] == []:
        pass
    else:
        logging.debug("Technologes it calculate sigmoid %s %s", enduse, installed_tech[enduse])

        # Iterite list with enduses where fuel switches are defined
        for technology in installed_tech[enduse]:
            logging.debug("Technology: %s Enduse:  %s", technology, enduse)

            # Calculate service demand for specific tech
            tech_install_p = calc_service_fuel_switched(
                enduse,
                fuel_switches,
                technologies,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by,
                'max_switch')

            # Read L-values with calculating maximum sigmoid theoretical diffusion
            l_values_sig[technology] = tech_install_p[technology]

    return dict(l_values_sig)

def calc_service_fuel_switched(
        enduse,
        fuel_switches,
        technologies,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type
    ):
    """Calculate energy service demand percentages after fuel switches

    Arguments
    ----------
    enduse : str
        enduse where with fuel switches
    fuel_switches : dict
        Fuel switches
    technologies : dict
        Technologies
    service_fueltype_by_p : dict
        Service demand per fueltype
    service_tech_by_p : dict
        Percentage of service demand per technology for base year
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

    #service_tech_switched_p = defaultdict(dict) #BELUGA SCRAP
    for fuel_switch in fuel_switches:
        if fuel_switch.enduse == enduse:

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
                fueltype_of_tech_replacing = technologies[tech].fuel_type_int
                service_tech_switched_p[tech] = service_tech_by_p[tech] - (change_service_fueltype_by_p * fuel_tech_p_by[fueltype_of_tech_replacing][tech])

    # -----------------------
    # Calculate service fraction of all technologies in enduse not affected
    # by fuel switch TODO WRITE MORE DOCU
    # -----------------------
    affected_service_p_ey = sum(service_tech_switched_p.values())

    remaining_service_to_distr_p = 1 - affected_service_p_ey

    # Calculate service fraction of remaining technologies
    all_fractions_not_affected_by_switch = {}
    for tech in service_tech_by_p:
        if tech not in service_tech_switched_p.keys():
            all_fractions_not_affected_by_switch[tech] = service_tech_by_p[tech]
    
    # Iterate all technologies of enduse_by
    service_tot_remaining = sum(all_fractions_not_affected_by_switch.values())

    # Get relative distribution of all not affected techs
    for tech in all_fractions_not_affected_by_switch:

        # Relative share
        rel_service_fraction_p = all_fractions_not_affected_by_switch[tech] / service_tot_remaining
        
        service_tech_switched_p[tech] = rel_service_fraction_p * remaining_service_to_distr_p

    return dict(service_tech_switched_p)

def get_tech_installed_single_enduse(enduse, fuel_switches):
    """Read out all technologies which are
    specifically switched to for all enduses
    TODO CHANGED
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
    installed_tech = {}

    # Add technology list for every enduse with affected switches
    installed_tech[enduse] = set([])

    for switch in fuel_switches:
        if switch.enduse == enduse:
            installed_tech[enduse].add(switch.technology_install)
    # Convert set to lists
    for enduse, set_values in installed_tech.items():
        installed_tech[enduse] = list(set_values)

    return installed_tech

'''def get_sig_diffusion(
        base_yr,
        technologies,
        service_switches,
        fuel_switches,
        enduses,
        tech_increased_service,
        service_tech_ey_p,
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
    fuel_switches : dict
        Fuel switches
    enduses : list
        Enduses
    tech_increased_service : list
        Technologies with increased service
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
    if len(service_switches) > 0:
        crit_switch_service = True
    else:
        crit_switch_service = False

    if regional_specific:
        installed_tech, sig_param_tech = defaultdict(dict), {}
        l_values_sig = defaultdict(dict)
        sig_param_tech = defaultdict(dict)
    else:
        installed_tech, sig_param_tech = {}, {}
        l_values_sig = defaultdict(dict)

    for enduse in enduses:

        if crit_switch_service:
            """Sigmoid calculation in case of 'service switch'
            """

            # Tech with lager service shares in end year
            installed_tech[enduse] = tech_increased_service[enduse]

            # End year service shares (scenaric input)
            service_tech_switched_p = service_tech_ey_p

            if regional_specific:
                # Maximum shares of each technology
                for reg in regions:
                    l_values_sig[reg][enduse] = {}
                    #same techs for every region
                    for tech in installed_tech[enduse][reg]:
                        l_values_sig[reg][enduse][tech] = technologies[tech].tech_max_share
            else:

                if tech_increased_service[enduse] == []:
                    pass
                else:
                    # Maximum shares of each technology
                    for tech in installed_tech[enduse]:
                        l_values_sig[enduse][tech] = technologies[tech].tech_max_share
        else:
            """Sigmoid calculation in case of 'fuel switch'
            """
            if regional_specific:

                # Tech with lager service shares in end year (installed in fuel switch)
                techs = get_tech_installed(enduses, fuel_switches)
                for reg in regions:
                    for _enduse in techs.keys():
                        installed_tech[_enduse][reg] = techs[_enduse]

                service_tech_switched_p = {}

                for reg in regions:

                    # Calculate future service demand after fuel switches for each technology
                    service_tech_switched_p[reg] = calc_service_fuel_switched(
                        enduses,
                        fuel_switches,
                        technologies,
                        service_fueltype_by_p,
                        service_tech_by_p,
                        fuel_tech_p_by,
                        techs,
                        'actual_switch')

                    # Calculate L for every technology for sigmod diffusion
                    l_values_sig[reg] = tech_l_sigmoid(
                        enduses,
                        fuel_switches,
                        technologies,
                        techs,
                        service_fueltype_by_p,
                        service_tech_by_p,
                        fuel_tech_p_by)
            else:

                # Tech with lager service shares in end year (installed in fuel switch)
                installed_tech = get_tech_installed(enduses, fuel_switches)

                # Calculate future service demand after fuel switches for each technology
                service_tech_switched_p = calc_service_fuel_switched(
                    enduses,
                    fuel_switches,
                    technologies,
                    service_fueltype_by_p,
                    service_tech_by_p,
                    fuel_tech_p_by,
                    installed_tech,
                    'actual_switch')

                # Calculate L for every technology for sigmod diffusion
                l_values_sig = tech_l_sigmoid(
                    enduses,
                    fuel_switches,
                    technologies,
                    installed_tech,
                    service_fueltype_by_p,
                    service_tech_by_p,
                    fuel_tech_p_by)

        if regional_specific:

            for reg in l_values_sig:
                # Calclulate sigmoid parameters for every installed technology
                sig_param_tech[reg][enduse] = tech_sigmoid_parameters(
                    base_yr,
                    technologies,
                    enduse,
                    crit_switch_service,
                    installed_tech[enduse][reg],
                    l_values_sig[reg],
                    service_tech_by_p[enduse],
                    service_tech_switched_p[reg][enduse],
                    fuel_switches,
                    service_switches)
        else:
            # Calclulate sigmoid parameters for every installed technology
            sig_param_tech[enduse] = tech_sigmoid_parameters(
                base_yr,
                technologies,
                enduse,
                crit_switch_service,
                installed_tech[enduse],
                l_values_sig,
                service_tech_by_p[enduse],
                service_tech_switched_p[enduse],
                fuel_switches,
                service_switches)

    return dict(installed_tech), dict(sig_param_tech), dict(service_tech_switched_p) #NEW --> End year service fraction
'''
def get_sig_diffusion_service(
        technologies,
        tech_increased_service,
        service_tech_ey_p,
        regions=False,
        regional_specific=False
    ):
    """Calculates parameters for sigmoid diffusion of
    technologies which are switched to/installed.

    Arguments
    ----------
    service_switches : dict
        Service switches
    fuel_switches : dict
        Fuel switches
    enduse : str
        Enduses
    tech_increased_service : list
        Technologies with increased service (installed technologies)
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
    l_values_sig = {}

    # End year service shares (scenaric input)
    service_tech_switched_p = service_tech_ey_p

    if regional_specific:
        # Maximum shares of each technology
        for reg in regions:
            l_values_sig[reg] = {}
            #same techs for every region
            for tech in tech_increased_service[reg]:
                l_values_sig[reg][tech] = technologies[tech].tech_max_share
    else:
        if tech_increased_service == []:
            pass
        else:
            # Maximum shares of each technology
            for tech in tech_increased_service:
                l_values_sig[tech] = technologies[tech].tech_max_share

    return dict(service_tech_switched_p), dict(l_values_sig)

def calc_diff_fuel_switch(
        technologies,
        fuel_switches,
        enduse,
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
    fuel_switches : dict
        Fuel switches
    enduse : str
        Enduse
    tech_increased_service : list
        Technologies with increased service
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
        installed_tech = defaultdict(dict)
        l_values_sig = defaultdict(dict)
        service_tech_switched_p = {}

        # Tech with lager service shares in end year (installed in fuel switch)
        techs = get_tech_installed_single_enduse(enduse, fuel_switches)
        for reg in regions:
            installed_tech[reg] = techs

        for reg in regions:

            # Calculate service demand after fuel switches for each technology
            service_tech_switched_p[reg] = calc_service_fuel_switched(
                enduse,
                fuel_switches,
                technologies,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by,
                'actual_switch')

            # Calculate L for every technology for sigmod diffusion
            l_values_sig[reg] = tech_l_sigmoid(
                enduse,
                fuel_switches,
                technologies,
                techs,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by)
    else:
        installed_tech = {}
        l_values_sig = defaultdict(dict)

        # Tech with lager service shares in end year (installed in fuel switch)
        installed_tech = get_tech_installed_single_enduse(enduse, fuel_switches)

        # Calculate future service demand after fuel switches for each technology
        service_tech_switched_p = calc_service_fuel_switched(
            enduse,
            fuel_switches,
            technologies,
            service_fueltype_by_p,
            service_tech_by_p,
            fuel_tech_p_by,
            'actual_switch')

        # Calculate L for every technology for sigmod diffusion
        l_values_sig = tech_l_sigmoid(
            enduse,
            fuel_switches,
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
        techs,
        regions=False,
        regional_specific=False
    ):
    if regional_specific:
        installed_tech = defaultdict(dict)
        sig_param_tech = {}

        for reg in regions:
            if techs[reg] == []:
                installed_tech[reg] = []
            else:
                installed_tech[reg] = techs[reg].keys()

        for reg in l_values_sig:

            # Calclulate sigmoid parameters for every installed technology
            sig_param_tech[reg] = tech_sigmoid_parameteNEW(
                base_yr,
                technologies,
                installed_tech[reg],
                l_values_sig[reg],
                service_tech_by_p,
                service_tech_switched_p[reg],
                service_switches[reg])
    else:
        sig_param_tech = {}

        if techs == []:
            installed_tech = []
        else:
            installed_tech = list(techs.keys())

        # Calclulate sigmoid parameters for every installed technology
        sig_param_tech = tech_sigmoid_parameteNEW(
            base_yr,
            technologies,
            installed_tech,
            l_values_sig,
            service_tech_by_p,
            service_tech_switched_p,
            service_switches)

    return sig_param_tech

def tech_sigmoid_parameteNEW(
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
    enduse : str
        Enduse
    crit_switch_service : bool
        Criteria whether sigmoid is calculated for service switch or not

    installed_tech : list
        List with installed technologies in fuel switches
    l_values : dict
        L values for maximum possible diffusion of technologies
    service_tech_by_p : dict
        Energy service demand for base year (1.sigmoid point)
    service_tech_switched_p : dict
        Service demand after fuelswitch
    fuel_switches : dict
        Fuel switch information

    Returns
    -------
    sigmoid_parameters : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)

    Notes
    -----
    Manually the fitting parameters can be defined which are not considered as
    a good fit: fit_crit_max, fit_crit_min
    If service definition, the year until switched is the end model year
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
            print("... create sigmoid diffusion parameters %s", tech)

            # Get year until switched
            for switch in service_switches:
                if switch.technology_install == tech:
                    yr_until_switched = switch.switch_yr

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
                l_values[tech],
                xdata,
                ydata)

            logging.debug(
                " ... Fitting: Midpoint: %s steepness: %s", fit_parameter[0], fit_parameter[1])

            # Insert parameters
            sigmoid_parameters[tech]['midpoint'] = fit_parameter[0] #midpoint (x0)
            sigmoid_parameters[tech]['steepness'] = fit_parameter[1] #Steepnes (k)
            sigmoid_parameters[tech]['l_parameter'] = l_values[tech]

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
