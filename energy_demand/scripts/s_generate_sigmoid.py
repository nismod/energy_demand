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
from energy_demand.plotting import plotting_program

def calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_assump_init=0.001,
        error_range=0.00002
    ):
    """Calculate sigmoid parameters. Check if fitting is good enough.

    Arguments
    ----------
    l_value : float
        Maximum upper level
    xdata : array
        X data
    ydata : array
        Y data
    fit_assump_init : float
        Small value for correct sigmoid diffusion in case start value is equal to L
    fit_crit_max : float
        Criteria to control and abort fit
    fit_crit_min : float
        Criteria to control and abort fit (slope must be posititive)
    error_range : float,default=0.00002
        Allowed fitting offset in percent

    Note
    -------
    `error_range` can be changed if the plotting is weird. If you increase
    chances are however hiigher that the fitting does not work anymore.

        How start parameters are generated:

            start_param_list = []
            for start in [x * 0.05 for x in range(0, 100)]:
                start_param_list.append(float(start))
            for start in [1.0, 0.001, 0.01, 0.1, 60.0, 100.0, 200.0, 400.0, 500.0, 1000.0]:
                start_param_list.append(float(start))
            for start in range(1, 59):
                start_param_list.append(float(start))

    Returns
    ------
    fit_parameter : array
        Parameters (first position: midpoint, second position: slope)
    """
    # ---------------------------------------------
    # Generate possible starting parameters for fit
    # ---------------------------------------------
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

            # ------------------------------------------------
            # Test if parameter[1] shoudl be minus or positive
            # ------------------------------------------------
            if ydata[0] < ydata[1]: # end point has higher value
                crit_plus_minus = 'plus'
            else:
                crit_plus_minus = 'minus'

                if l_value == ydata[0]:
                    l_value += fit_assump_init
                else:
                    pass

            # Select start parameters depending on pos or neg diff
            if crit_plus_minus == 'minus':
                start_parameters[1] *= -1
            # -----------------------------------
            # Fit function
            # Info: If the fitting function throws errors,
            #       it is possible to change the parameters
            #       `number_of_iterations`.
            # -----------------------------------
            fit_parameter = fit_sigmoid_diffusion(
                l_value,
                xdata,
                ydata,
                start_parameters,
                number_of_iterations=1000)

            # Test if start paramters are identical to fitting parameters
            if (crit_plus_minus == 'plus' and fit_parameter[1] < 0) or (
                    crit_plus_minus == 'minus' and fit_parameter[1] > 0):
                cnt += 1
                if cnt >= len(start_param_list):
                    logging.critical("Error: Sigmoid curve fitting failed")
            else:
                #pass # corret sign

                if (fit_parameter[0] == start_parameters[0]) or (
                        fit_parameter[1] == start_parameters[1]):
                    cnt += 1
                    if cnt >= len(start_param_list):
                        logging.critical("Error: Sigmoid curve fitting failed")
                else:
                    successfull = True

                    logging.debug("Fit parameters: %s %s %s", fit_parameter, xdata, ydata)
                    '''plotting_program.plotout_sigmoid_tech_diff(
                        l_value,
                        "ttse",
                        xdata,
                        ydata,
                        fit_parameter,
                        plot_crit=True, #TRUE
                        close_window_crit=True)'''
                    # -------------------------
                    # Check how good the fit is
                    # -------------------------
                    y_calculated = diffusion_technologies.sigmoid_function(
                        x_value=xdata[1],
                        l_value=l_value,
                        midpoint=fit_parameter[0],
                        steepness=fit_parameter[1])

                    fit_measure_in_percent = float((100.0 / ydata[1]) * y_calculated)
                    if fit_measure_in_percent < (100.0 - error_range) or fit_measure_in_percent > (100.0 + error_range):
                        logging.debug(
                            "... Fitting measure %s (percent) is not good enough", fit_measure_in_percent)
                        successfull = False
                        cnt += 1
                    else:
                        logging.debug(
                            ".... fitting successfull %s %s", fit_measure_in_percent, fit_parameter)
                        '''plotting_program.plotout_sigmoid_tech_diff(
                            l_value,
                            "FINISHED FITTING",
                            xdata,
                            ydata,
                            fit_parameter,
                            plot_crit=True, #TRUE
                            close_window_crit=True)'''
        except (RuntimeError, IndexError):
            logging.debug("Unsuccessful fit %s %s", start_parameters[0], start_parameters[1])
            cnt += 1

            if cnt >= len(start_param_list):
                logging.critical("Check whether start year is <= the year 2000")
                raise Exception("Fitting did not work")

    return fit_parameter

def fit_sigmoid_diffusion(l_value, x_data, y_data, start_parameters, number_of_iterations=10000):
    """Fit sigmoid curve based on two points on the diffusion curve

    Arguments
    ----------
    l_value : float
        The sigmoids curve maximum value (max consumption)
    x_data : array
        X coordinate of two points
    y_data : array
        X coordinate of two points
    number_of_iterations : int
        Number of iterations used for sigmoid fitting

    Returns
    -------
    popt : dict
        Fitting parameters (l_value, midpoint, steepness)

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
        maxfev=number_of_iterations)

    return popt

def tech_l_sigmoid(
        service_tech_switched_ey,
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
    service_tech_switched_ey : dict
        Ey service tech
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
        logging.debug("Technologes to calculate sigmoid %s", installed_tech)

        # Iterite list with enduses where fuel switches are defined
        for technology in installed_tech:

            # If decreasing technology, L-Value stays initial value
            if service_tech_by_p[technology] > service_tech_switched_ey[technology]:
                l_values_sig[technology] = service_tech_by_p[technology]

            else:
                # Future service share is higher
                # Calculate maximum service demand for specific tech
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
        fuel_switches,
        technologies,
        service_fueltype_by_p,
        service_tech_by_p,
        fuel_tech_p_by,
        switch_type
    ):
    """Calculate energy service demand percentages after fuel switches.

    Arguments
    ----------
    fuel_switches : dict
        Fuel switches of a specific enduse
    technologies : dict
        Technologies
    service_fueltype_by_p : dict
        Service share per fueltype in base year
    service_tech_by_p : dict
        Share of service demand per technology for base year
    fuel_tech_p_by : dict
        Fuel shares for each technology of an enduse for base year
    switch_type : str
        If either switch is for maximum theoretical switch
        of with defined switch until end year

    Return
    ------
    service_tech_switched_p : dict
        Service in future year with added and substracted
        service demand for every technology
    """
    service_tech_switched_p = {}

    for fuel_switch in fuel_switches:

        tech_install = fuel_switch.technology_install
        tech_replace_fueltype = fuel_switch.enduse_fueltype_replace

        # Share of energy service of repalced fueltype before switch in base year
        service_p_by = service_fueltype_by_p[tech_replace_fueltype]

        # Service demand per fueltype that will be switched
        # (e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent)
        if switch_type == 'max_switch':
            diff_service_fueltype_by_p = service_p_by * technologies[tech_install].tech_max_share
        elif switch_type == 'actual_switch':
            diff_service_fueltype_by_p = service_p_by * fuel_switch.fuel_share_switched_ey

        # Service addition
        service_tech_switched_p[tech_install] = service_tech_by_p[tech_install] + diff_service_fueltype_by_p

        # Iterate technologies which are replaced for this fueltype and substract
        # service demand for replaced technologies proportionally
        for tech, fuel_tech_p in fuel_tech_p_by[tech_replace_fueltype].items():
            service_tech_switched_p[tech] = service_tech_by_p[tech] - (diff_service_fueltype_by_p * fuel_tech_p)

    # -----------------------
    # Calculate service fraction of all technologies in
    # enduse not affected by fuel switch
    # -----------------------
    affected_service_p_ey = sum(service_tech_switched_p.values())
    unaffected_service_to_distr_p = 1 - affected_service_p_ey

    # Calculate service fraction of remaining technologies
    fractions_unaffected_switch = {}
    for tech, service_tech_p in service_tech_by_p.items():
        if tech not in service_tech_switched_p.keys():
            fractions_unaffected_switch[tech] = service_tech_p

    # Sum of unaffected service shares
    service_tot_remaining = sum(fractions_unaffected_switch.values())

    # Get relative distribution of all not affected techs
    for tech, tech_fraction in fractions_unaffected_switch.items():

        # Relative share
        rel_service_fraction_p = tech_fraction / service_tot_remaining
        service_tech_switched_p[tech] = rel_service_fraction_p * unaffected_service_to_distr_p

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

    return list(installed_tech)

def get_l_values(
        technologies,
        technologies_to_consider,
        regions=False,
        regional_specific=False
    ):
    """Get l values (Maximum shares of each technology)
    for all installed technologies

    Arguments
    ----------
    technologies : dict
        Technologies
    technologies_to_consider : list
        Technologies to consider
    service_fueltype_by_p :
        Fraction of service per fueltype in base year
    regions : dict
        Regions
    regional_specific : bool
        Criteria if calculation for a specific region or not

    Return
    ------
    l_values_sig : dict
        Sigmoid paramters
    """
    l_values_sig = defaultdict(dict)

    if regional_specific:
        for reg in regions:
            if technologies_to_consider == []:
                pass
            else:
                for tech in technologies_to_consider:
                    l_values_sig[reg][tech] = technologies[tech].tech_max_share
    else:
        if technologies_to_consider == []:
            pass
        else:
            for tech in technologies_to_consider:
                l_values_sig[tech] = technologies[tech].tech_max_share

    return dict(l_values_sig)

def tech_sigmoid_parameters(
        yr_until_switched,
        base_yr,
        technologies,
        l_values,
        service_tech_by_p,
        service_tech_switched_p,
        fit_assump_init=0.001,
        plot_sigmoid_diffusion=True):
    """Calculate sigmoid diffusion parameters based on energy service
    demand in base year and projected future energy service demand. The
    future energy servie demand is calculated based on fuel switches.

    Three potential sigmoid outputs are possible:

        'linear':       No sigmoid fitting possible because the
                        service in the future year is identical
                        to the service in the base year

        None:           No sigmoid is fitted if the future
                        service share is zero.

        fit_parameters  Sigmoid diffusion parameters

    Because the sigmoid fitting does not work if the initial and
    end values are zero, small approximatie values `fit_assump_init`
    are inserted to allow the function 'calc_sigmoid_parameters'
    to fit.

    Arguments
    ----------
    yr_until_switched : int
        Year until switch is fully realised
    base_yr : int
        base year
    technologies : dict
        technologies
    l_values : dict
        L values for maximum possible diffusion of technologies
    service_tech_by_p : dict
        Energy service demand for base year (1. sigmoid point)
    service_tech_switched_p : dict
        Service demand after fuelswitch
    fit_assump_init : float
        Approximation helping small number to allow fit
    plot_sigmoid_diffusion : bool,default=True
        Criteria whether sigmoid are plotted

    Returns
    -------
    sig_params : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)
    """
    # Technologies to apply calculation
    installed_techs = service_tech_switched_p.keys()

    sig_params = defaultdict(dict)

    # Fitting criteria where the calculated sigmoid slope and midpoint can be provided limits
    if installed_techs == []:
        pass
    else:
        for tech in installed_techs:
            logging.debug("... create sigmoid diffusion parameters %s", tech)

            # --------
            # Test whether technology has the market entry before or after base year,
            # If afterwards, set very small number in market entry year
            # --------
            if technologies[tech].market_entry > base_yr:
                point_x_by = technologies[tech].market_entry
                point_y_by = fit_assump_init
            else:
                point_x_by = base_yr                 # Base year
                point_y_by = service_tech_by_p[tech] # Base year service share

                # If the base year is the market entry year use a very small number
                if point_y_by == 0:
                    point_y_by = fit_assump_init

            # Future energy service demand (second point on sigmoid curve for fitting)
            point_x_ey = yr_until_switched
            point_y_ey = service_tech_switched_p[tech]

            # If future share is zero, entry small value
            if point_y_ey == 0:
                point_y_ey = fit_assump_init

            # Data of the two points
            xdata = np.array([point_x_by, point_x_ey])
            ydata = np.array([point_y_by, point_y_ey])

            logging.debug(
                "... create sigmoid diffusion %s - %s - %s - %s - l_val: %s - %s - %s",
                tech, xdata, ydata, fit_assump_init, l_values[tech], point_y_by, point_y_ey)

            # If no change in by to ey but not zero (lineare change)
            if (round(point_y_by, 10) == round(point_y_ey, 10)) and (
                    point_y_ey != fit_assump_init) and (
                        point_y_by != fit_assump_init):

                # Linear diffusion (because by and ey share are identical)
                sig_params[tech]['midpoint'] = 'linear'
                sig_params[tech]['steepness'] = 'linear'
                sig_params[tech]['l_parameter'] = 'linear'
            else:
                # Test if ftting is possible ()
                if (point_y_by == fit_assump_init and point_y_ey == fit_assump_init) or (
                        l_values[tech] == 0):

                    # If no increase or decrease, if no future potential share
                    sig_params[tech]['midpoint'] = None
                    sig_params[tech]['steepness'] = None
                    sig_params[tech]['l_parameter'] = None
                else:

                    # Parameter fitting
                    fit_parameter = calc_sigmoid_parameters(
                        l_values[tech],
                        xdata,
                        ydata,
                        fit_assump_init=fit_assump_init,
                        error_range=0.0002)

                    logging.debug(
                        " ... Fitting  %s: Midpoint: %s steepness: %s",
                        tech, fit_parameter[0], fit_parameter[1])

                    # Insert parameters
                    sig_params[tech]['midpoint'] = fit_parameter[0] # midpoint (x0)
                    sig_params[tech]['steepness'] = fit_parameter[1] # Steepnes (k)
                    sig_params[tech]['l_parameter'] = l_values[tech] # maximum p

                    '''if plot_sigmoid_diffusion:
                        plotting_program.plotout_sigmoid_tech_diff(
                            l_values[tech],
                            tech,
                            xdata,
                            ydata,
                            fit_parameter,
                            plot_crit=False, #TRUE
                            close_window_crit=True)'''

    return dict(sig_params)
