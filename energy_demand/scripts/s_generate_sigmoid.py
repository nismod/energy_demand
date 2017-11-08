"""Script to fit technology diffusion

This script calculates the three parameters of a sigmoid diffusion
for every technology which is diffused and has a larger service
fraction at the model end year
"""
import os
import sys
import copy
import logging
from collections import defaultdict
import numpy as np
from scipy.optimize import curve_fit
from energy_demand.read_write import read_data
from energy_demand.initalisations import helpers
from energy_demand.technologies import diffusion_technologies

def calc_sigmoid_parameters(l_value, xdata, ydata, fit_crit_a=200, fit_crit_b=0.001):
    """Calculate sigmoid parameters

    Arguments
    ----------
    l_value : float
        Maximum upper level
    xdata : array
        X data
    ydata : array
        Y data
    fit_crit_a : float
        Criteria to control and abort fit
    fit_crit_b : float
        Criteria to control and abort fit

    Returns
    ------
    fit_parameter : array
        Parameters (first position: midpoint, second position: slope)
    """
    # Generate possible starting parameters for fit
    start_param_list = [1.0, 0.001, 0.01, 0.1, 60.0, 100.0, 200.0, 400.0, 500.0, 1000.0]
    for start in [x * 0.05 for x in range(0, 100)]:
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
                False
                )'''

            # Criteria when fit did not work
            if (fit_parameter[0] > fit_crit_a) or (
                fit_parameter[0] < fit_crit_b) or (
                    fit_parameter[1] > fit_crit_a) or (
                        fit_parameter[1] < 0) or (
                            fit_parameter[0] == start_parameters[0]) or (
                                fit_parameter[1] == start_parameters[1]):

                cnt += 1
                if cnt >= len(start_param_list):
                    sys.exit("Error2: CURVE FITTING DID NOT WORK")
            else:
                successfull = True

                # -------------------------
                # Check how good the fit is
                # -------------------------
                y_calculated = diffusion_technologies.sigmoid_function(
                    xdata[1], l_value, *fit_parameter)

                #print("Calculated value:  " + str(y_calculated))
                #print("original value:    " + str(ydata[1]))
                fit_measure_in_percent = (100.0 / ydata[1]) * y_calculated
                logging.debug("... Fitting measure in percent: %s", fit_measure_in_percent)
                logging.debug("... Fitting measure in percent: %s", fit_measure_in_percent)

                if fit_measure_in_percent < 99.0:
                    logging.critical("The sigmoid fitting is not good enough")
                    sys.exit()

        except RuntimeError:
            logging.debug("Unsuccessful fit %s", start_parameters[1])
            cnt += 1

            if cnt >= len(start_param_list):
                sys.exit("Sigmoid fit error: Try changing fit_crit_a and fit_crit_b")

    return fit_parameter

def tech_sigmoid_parameters(
        data,
        enduse,
        crit_switch_service,
        installed_tech,
        l_values,
        service_tech_by_p,
        service_tech_switched_p,
        fuel_switches,
        service_switches #BELUGA
    ):
    """Calculate diffusion parameters based on energy service
    demand in base year and projected future energy service demand

    The future energy servie demand is calculated based on fuel switches.
    A sigmoid diffusion is fitted.

    Arguments
    ----------
    data : dict
        data
    enduses : enduses
        enduses
    crit_switch_service : bool
        Criteria whether sigmoid is calculated for service switch or not
    installed_tech : dict
        Technologies with fuel switch for enduse
    installed_tech : dict
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
    a good fit: fit_crit_a, fit_crit_b
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
            logging.debug("... create sigmoid difufsion parameters %s %s", enduse, tech)

            # If service switch
            if crit_switch_service:
                #year_until_switched = data['sim_param']['end_yr'] # Year until service is switched

                #BELUGA AL NEW
                for switch in service_switches:
                    if switch['tech'] == tech:
                        year_until_switched = switch['year_switch_ey']

                market_entry = data['assumptions']['technologies'][tech]['market_entry']
            else: #fuel switch

                # Get the most future year of the technology in the enduse which is switched to
                year_until_switched = 0
                for switch in fuel_switches:
                    if switch['enduse'] == enduse and switch['technology_install'] == tech:
                        if year_until_switched < switch['year_fuel_consumption_switched']:
                            year_until_switched = switch['year_fuel_consumption_switched']

                market_entry = data['assumptions']['technologies'][tech]['market_entry']

            # --------
            # Test whether technology has the market entry before or after base year,
            # If afterwards, set very small number in market entry year
            # --------
            if market_entry > data['sim_param']['base_yr']:
                point_x_by = market_entry
                point_y_by = fit_assump_init # very small service share if market entry in a future year
            else: # If market entry before, set to 2015
                point_x_by = data['sim_param']['base_yr']
                point_y_by = service_tech_by_p[tech] # current service share

                #If the base year is the market entry year use a very small number
                if point_y_by == 0:
                    point_y_by = fit_assump_init

            # Future energy service demand (second point on sigmoid curve for fitting)
            point_x_projected = year_until_switched
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

    return sigmoid_parameters

def get_tech_future_service(service_tech_by_p, service_tech_ey_p):
    """Get all those technologies with increased service in future

    Arguments
    ----------
    service_tech_by_p : dict
        Share of service per technology of base year of total service
    service_tech_ey_p : dict
        Share of service per technology of end year of total service

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
    tech_increased_service = {}
    tech_decreased_share = {}
    tech_constant_share = {}

    for enduse in service_tech_by_p:

        # If no service switch defined
        if service_tech_ey_p[enduse] == {}:
            tech_increased_service[enduse] = []
            tech_decreased_share[enduse] = []
            tech_constant_share[enduse] = []
        else:
            tech_increased_service[enduse] = []
            tech_decreased_share[enduse] = []
            tech_constant_share[enduse] = []

            # Calculate fuel for each tech
            for tech in service_tech_by_p[enduse]:

                # If future larger share
                if service_tech_by_p[enduse][tech] < service_tech_ey_p[enduse][tech]:
                    tech_increased_service[enduse].append(tech)

                # If future smaller service share
                elif service_tech_by_p[enduse][tech] > service_tech_ey_p[enduse][tech]:
                    tech_decreased_share[enduse].append(tech)
                else:
                    tech_constant_share[enduse].append(tech)

    return tech_increased_service, tech_decreased_share, tech_constant_share

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

def tech_l_sigmoid(enduses, fuel_switches, installed_tech, service_fueltype_p, service_tech_by_p, fuel_tech_p_by):
    """Calculate L value for every installed technology with maximum theoretical replacement value

    Arguments
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    assumptions : dict
        Assumptions

    Returns
    -------
    l_values_sig : dict
        L value for sigmoid diffusion of all technologies for which a switch is implemented

    Notes
    -----
    Gets second sigmoid point
    """
    l_values_sig = helpers.init_dict_brackets(enduses)

    for enduse in enduses:
        # Check wheter there are technologies in this enduse which are switched
        if installed_tech[enduse] == []:
            pass
        else:
            logging.debug("Technologes it calculate sigmoid %s %s", enduse, installed_tech[enduse])

            # Iterite list with enduses where fuel switches are defined
            for technology in installed_tech[enduse]:
                logging.debug("Technology: %s Enduse:  %s", technology, enduse)
                # Calculate service demand for specific tech
                tech_install_p = calc_service_fuel_switched(
                    enduses,
                    fuel_switches,
                    service_fueltype_p,
                    service_tech_by_p, # Percentage of service demands for every technology
                    fuel_tech_p_by,
                    {str(enduse): [technology]},
                    'max_switch')

                # Read L-values with calculating maximum sigmoid theoretical diffusion
                l_values_sig[enduse][technology] = tech_install_p[enduse][technology]

    return l_values_sig

def calc_service_fuel_switched(
        enduses,
        fuel_switches,
        service_fueltype_p,
        service_tech_by_p,
        fuel_tech_p_by,
        installed_tech_switches,
        switch_type
    ):
    """Calculate energy service demand percentages after fuel switches

    Arguments
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    fuel_switches : dict
        Fuel switches
    service_fueltype_p : dict
        Service demand per fueltype
    service_tech_by_p : dict
        Percentage of service demand per technology for base year
    fuel_tech_p_by : dict
        Technologies in base year
    fuel_tech_p_by : dict
        Fuel shares for each technology of an enduse
    installed_tech_switches : dict
        Technologies which are installed in fuel switches
    switch_type :

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
    #service_tech_switched_p = defaultdict(dict)
    service_tech_switched_p = copy.deepcopy(service_tech_by_p)

    for enduse in enduses:
        for fuel_switch in fuel_switches:
            if fuel_switch['enduse'] == enduse:

                tech_install = fuel_switch['technology_install']
                fueltype_tech_replace = fuel_switch['enduse_fueltype_replace']

                # Check if installed technology is considered for fuelswitch
                if tech_install in installed_tech_switches[enduse]:

                    # Share of energy service before switch
                    orig_service_p = service_fueltype_p[enduse][fueltype_tech_replace]

                    # Service demand per fueltype that will be switched
                    if switch_type == 'max_switch':
                        # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent
                        change_service_fueltype_p = orig_service_p * fuel_switch['max_theoretical_switch']
                    elif switch_type == 'actual_switch':
                        # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent
                        change_service_fueltype_p = orig_service_p * fuel_switch['share_fuel_consumption_switched']

                    # ---Service addition
                    service_tech_switched_p[enduse][tech_install] += change_service_fueltype_p
                    #service_tech_switched_p[enduse][tech_install] = service_tech_switched_p[enduse][tech_install] + change_service_fueltype_p

                    # Get all technologies which are replaced related to this fueltype
                    replaced_tech_fueltype = fuel_tech_p_by[enduse][fueltype_tech_replace].keys()

                    # Calculate total energy service in this fueltype, Substract service demand for replaced technologies
                    for tech in replaced_tech_fueltype:
                        service_tech_switched_p[enduse][tech] -= change_service_fueltype_p * service_tech_by_p[enduse][tech]

    return service_tech_switched_p

def get_tech_installed(enduses, fuel_switches):
    """Read out all technologies which are
    specifically switched to for all enduses

    Parameter
    ---------
    enduses : list
        List with enduses
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
    for enduse in enduses:
        installed_tech[enduse] = set([])

    for switch in fuel_switches:
        enduse_fuelswitch = switch['enduse']
        installed_tech[enduse_fuelswitch].add(switch['technology_install'])

    # Convert set to lists
    for enduse in installed_tech:
        installed_tech[enduse] = list(installed_tech[enduse])

    return installed_tech

def get_sig_diffusion(
        data,
        service_switches,
        fuel_switches,
        enduses,
        tech_increased_service,
        service_tech_ey_p,
        enduse_tech_maxl_by_p,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by
    ):
    """Calculates parameters for sigmoid diffusion of technologies which are switched to/installed.

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
    enduse_tech_maxl_by_p :
        Maximum service (L crit) per technology
    service_fueltype_by_p :
        Fraction of service per fueltype in base year
    service_tech_by_p :
        Fraction of service per technology in base year
    fuel_tech_p_by :
        Fraction of fuel per technology in base year

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

    installed_tech, sig_param_tech = {}, {}

    for enduse in enduses:
        if crit_switch_service:
            """Sigmoid calculation in case of 'service switch'
            """
            # Tech with lager service shares in end year
            installed_tech = tech_increased_service

            # End year service shares (scenaric input)
            service_tech_switched_p = service_tech_ey_p

            # Maximum shares of each technology
            l_values_sig = enduse_tech_maxl_by_p

        else:
            """Sigmoid calculation in case of 'fuel switch'
            """
            # Tech with lager service shares in end year (installed in fuel switch)
            installed_tech = get_tech_installed(enduses, fuel_switches)

            # Calculate future service demand after fuel switches for each technology
            service_tech_switched_p = calc_service_fuel_switched(
                enduses,
                fuel_switches,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by,
                installed_tech,
                'actual_switch')

            # Calculate L for every technology for sigmod diffusion
            l_values_sig = tech_l_sigmoid(
                enduses,
                fuel_switches,
                installed_tech,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_tech_p_by)

        # Calclulate sigmoid parameters for every installed technology
        sig_param_tech[enduse] = tech_sigmoid_parameters(
            data,
            enduse,
            crit_switch_service,
            installed_tech[enduse],
            l_values_sig,
            service_tech_by_p[enduse],
            service_tech_switched_p[enduse],
            fuel_switches,
            service_switches) #BELUGA

    return installed_tech, sig_param_tech

def write_installed_tech(path_to_txt, data):
    """Write out all technologies

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}".format(
        'enduse', 'technology') + '\n'
              )

    for enduse, technologies in data.items():
        if str(technologies) == "[]":
            file.write("{}, {}".format(
                str.strip(enduse), str(technologies) + '\n'))
        else:
            for technology in technologies:
                file.write("{}, {}".format(
                    str.strip(enduse), str.strip(technology) + '\n'))
    file.close()

    return

def write_sig_param_tech(path_to_txt, data):
    """Write out sigmoid parameters per technology
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}, {}".format(
        'enduse', 'technology', 'midpoint', 'steepness', 'l_parameter') + '\n'
              )
    for enduse, technologies in data.items():
        for technology, parameters in technologies.items():
            midpoint = float(parameters['midpoint'])
            steepness = float(parameters['steepness'])
            l_parameter = float(parameters['l_parameter'])

            file.write("{}, {}, {}, {}, {}".format(
                enduse, str.strip(technology), midpoint, steepness, l_parameter) + '\n')

    file.close()

    return

'''def write_tech_increased_service(path_to_txt, data):
    """Write out function

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}, {}".format(
        'enduse', 'technology', 'midpoint', 'steepness', 'l_parameter') + '\n'
              )
    for enduse, technologies in data.items():
        for technology, parameters in technologies.items():

            file.write("{}, {}, {}, {}, {}".format(
                enduse,
                str.strip(technology),
                float(parameters['midpoint']),
                float(parameters['steepness']),
                float(parameters['l_parameter'])) + '\n')

    file.close()

    return
'''

def run(data):
    """Function run script
    """
    logging.debug("... start script %s", os.path.basename(__file__))

    # Read in Services
    rs_service_tech_by_p = read_data.read_service_tech_by_p(os.path.join(
        data['local_paths']['dir_services'], 'rs_service_tech_by_p.csv'))
    ss_service_tech_by_p = read_data.read_service_tech_by_p(os.path.join(
        data['local_paths']['dir_services'], 'ss_service_tech_by_p.csv'))
    is_service_tech_by_p = read_data.read_service_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'is_service_tech_by_p.csv'))
    rs_service_fueltype_by_p = read_data.read_service_fueltype_by_p(
        os.path.join(data['local_paths']['dir_services'], 'rs_service_fueltype_by_p.csv'))
    ss_service_fueltype_by_p = read_data.read_service_fueltype_by_p(
        os.path.join(data['local_paths']['dir_services'], 'ss_service_fueltype_by_p.csv'))
    is_service_fueltype_by_p = read_data.read_service_fueltype_by_p(
        os.path.join(data['local_paths']['dir_services'], 'is_service_fueltype_by_p.csv'))

    # Calculate technologies with more, less and constant service based on service switch assumptions
    rs_tech_increased_service, rs_tech_decreased_share, rs_tech_constant_share = get_tech_future_service(
        rs_service_tech_by_p,
        data['assumptions']['rs_share_service_tech_ey_p'])
    ss_tech_increased_service, ss_tech_decreased_share, ss_tech_constant_share = get_tech_future_service(
        ss_service_tech_by_p,
        data['assumptions']['ss_share_service_tech_ey_p'])
    is_tech_increased_service, is_tech_decreased_share, is_tech_constant_share = get_tech_future_service(
        is_service_tech_by_p,
        data['assumptions']['is_share_service_tech_ey_p'])

    # Calculate sigmoid diffusion curves based on assumptions about fuel switches

    # --Residential
    rs_installed_tech, rs_sig_param_tech = get_sig_diffusion(
        data,
        data['assumptions']['rs_service_switches'],
        data['assumptions']['rs_fuel_switches'],
        data['enduses']['rs_all_enduses'],
        rs_tech_increased_service,
        data['assumptions']['rs_share_service_tech_ey_p'],
        data['assumptions']['rs_enduse_tech_maxL_by_p'],
        rs_service_fueltype_by_p,
        rs_service_tech_by_p,
        data['assumptions']['rs_fuel_tech_p_by'])

    # --Service
    ss_installed_tech, ss_sig_param_tech = get_sig_diffusion(
        data,
        data['assumptions']['ss_service_switches'],
        data['assumptions']['ss_fuel_switches'],
        data['enduses']['ss_all_enduses'],
        ss_tech_increased_service,
        data['assumptions']['ss_share_service_tech_ey_p'],
        data['assumptions']['ss_enduse_tech_maxL_by_p'],
        ss_service_fueltype_by_p,
        ss_service_tech_by_p,
        data['assumptions']['ss_fuel_tech_p_by'])

    # --Industry
    is_installed_tech, is_sig_param_tech = get_sig_diffusion(
        data,
        data['assumptions']['is_service_switches'],
        data['assumptions']['is_fuel_switches'],
        data['enduses']['is_all_enduses'],
        is_tech_increased_service,
        data['assumptions']['is_share_service_tech_ey_p'],
        data['assumptions']['is_enduse_tech_maxL_by_p'],
        is_service_fueltype_by_p,
        is_service_tech_by_p,
        data['assumptions']['is_fuel_tech_p_by'])

    # Write out to csv
    write_installed_tech(
        os.path.join(data['local_paths']['path_sigmoid_data'], 'rs_installed_tech.csv'),
                         rs_installed_tech)
    write_installed_tech(
        os.path.join(data['local_paths']['path_sigmoid_data'], 'ss_installed_tech.csv'),
                         ss_installed_tech)
    write_installed_tech(
        os.path.join(data['local_paths']['path_sigmoid_data'], 'is_installed_tech.csv'),
                         is_installed_tech)
    write_sig_param_tech(
        os.path.join(data['local_paths']['path_sigmoid_data'], 'rs_sig_param_tech.csv'),
                         rs_sig_param_tech)
    write_sig_param_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'ss_sig_param_tech.csv'),
                         ss_sig_param_tech)
    write_sig_param_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'is_sig_param_tech.csv'),
                         is_sig_param_tech)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'rs_tech_increased_service.csv'),
                         rs_tech_increased_service)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'ss_tech_increased_service.csv'),
                         ss_tech_increased_service)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'is_tech_increased_service.csv'),
                         is_tech_increased_service)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'rs_tech_decreased_share.csv'),
                         rs_tech_decreased_share)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'ss_tech_decreased_share.csv'),
                         ss_tech_decreased_share)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'is_tech_decreased_share.csv'),
                         is_tech_decreased_share)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'rs_tech_constant_share.csv'),
                         rs_tech_constant_share)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'ss_tech_constant_share.csv'),
                         ss_tech_constant_share)
    write_installed_tech(os.path.join(
        data['local_paths']['path_sigmoid_data'], 'is_tech_constant_share.csv'),
                         is_tech_constant_share)

    logging.debug("... finished script %s", os.path.basename(__file__))
    return
