"""Script to fit technology diffusion

This script calculates the three parameters of a sigmoid diffusion
for every technology which is diffused and has a larger service
fraction at the model end year
"""
from collections import defaultdict
import numpy as np
from scipy.optimize import curve_fit
from energy_demand.technologies import diffusion_technologies
#from energy_demand.plotting import basic_plot_functions

def calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_assump_init=0.001,
        error_range=0.00002,
        number_of_iterations=1000
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
        chances are however higher that the fitting does not work anymore.

    Returns
    ------
    fit_parameter : array
        Parameters (first position: midpoint, second position: slope)
    """
    # ---------------------------------------------
    # Generate possible starting parameters for fit
    # ---------------------------------------------
    start_param_list = [0.0, 1.0, 0.0001, 0.001, 0.01]

    # ---------------------------------------------
    # Fit
    # ---------------------------------------------
    cnt = 0
    successfull = False
    while not successfull:
        try:
            start_parameters = [
                round(start_param_list[cnt], 3),
                round(start_param_list[cnt], 3)]

            # ------------------------------------------------
            # Test if parameter[1] should be minus or positive
            # ------------------------------------------------
            if ydata[0] < ydata[1]: # end point has higher value
                crit_plus_minus = 'plus'
            else:
                crit_plus_minus = 'minus'

                if l_value == ydata[0]:
                    l_value += fit_assump_init

            # Select start parameters depending on pos or neg diff
            if crit_plus_minus == 'minus':
                start_parameters[0] *= 1
                start_parameters[1] *= -1

            #logging.debug(" patameters {} {} {} {}".format(
            #    xdata, ydata, start_parameters, l_value))

            # Fit function
            fit_parameter = fit_sigmoid_diffusion(
                l_value,
                xdata,
                ydata,
                start_parameters,
                number_of_iterations=number_of_iterations)

            # Test if start paramters are identical to fitting parameters
            if (crit_plus_minus == 'plus' and fit_parameter[1] < 0) or (
                    crit_plus_minus == 'minus' and fit_parameter[1] > 0):
                cnt += 1
                if cnt >= len(start_param_list):
                    raise Exception("Error: Sigmoid curve fitting failed")
            else:
                if (fit_parameter[0] == start_parameters[0]) or (
                        fit_parameter[1] == start_parameters[1]):
                    cnt += 1
                    if cnt >= len(start_param_list):
                        raise Exception("Error: Sigmoid curve fitting failed")
                else:

                    # Check how good the fit is
                    y_calculated_ey = diffusion_technologies.sigmoid_function(
                        x_value=xdata[1],
                        l_value=l_value,
                        midpoint=fit_parameter[0],
                        steepness=fit_parameter[1])

                    y_calculated_by = diffusion_technologies.sigmoid_function(
                        x_value=xdata[0],
                        l_value=l_value,
                        midpoint=fit_parameter[0],
                        steepness=fit_parameter[1])

                    fit_measure_p_by = float((100.0 / ydata[0]) * y_calculated_by)
                    fit_measure_p_ey = float((100.0 / ydata[1]) * y_calculated_ey)

                    if (fit_measure_p_ey < (100.0 - error_range) or fit_measure_p_ey > (100.0 + error_range)) or (
                        fit_measure_p_by < (100.0 - error_range) or fit_measure_p_by > (100.0 + error_range)):
                        
                        #logging.debug("... Fitting measure %s %s (percent) is not good enough",
                        #    fit_measure_p_by, fit_measure_p_ey)
                        successfull = False
                        cnt += 1
                    else:
                        successfull = True

                        '''logging.info(
                            ".... fitting successfull %s %s %s", fit_measure_p_ey, fit_measure_p_by, fit_parameter)
                        basic_plot_functions.plotout_sigmoid_tech_diff(
                            l_value,
                            "FINISHED FITTING",
                            xdata,
                            ydata,
                            fit_parameter,
                            plot_crit=True,
                            close_window_crit=True)'''
        except (RuntimeError, IndexError):
            cnt += 1

            if cnt >= len(start_param_list):
                raise Exception(
                    "Fitting did not work: Check whether start year is <= the year 2000")

    return fit_parameter

def fit_sigmoid_diffusion(
        l_value,
        x_data,
        y_data,
        start_parameters,
        number_of_iterations=10000
    ):
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
        s_tech_switched_ey,
        enduse_fuel_switches,
        technologies,
        installed_tech,
        s_fueltype_by_p,
        s_tech_by_p,
        fuel_tech_p_by
    ):
    """Calculate L value (maximum possible theoretical market penetration)
    for every installed technology with maximum theoretical replacement
    share (calculate second sigmoid point).

    Arguments
    ----------
    s_tech_switched_ey : dict
        Ey service tech
    enduse_fuel_switches : dict
        Fuel switches of enduse
    installed_tech : dict
        Installed technologies (as keys)
    s_fueltype_by_p : dict
        Service share per fueltye of base year
    s_tech_by_p : dict
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
        # Iterite list with enduses where fuel switches are defined
        for technology in installed_tech:

            # If decreasing technology, L-Value stays initial value
            if s_tech_by_p[technology] > s_tech_switched_ey[technology]:
                l_values_sig[technology] = s_tech_by_p[technology]

            else:
                # Calculate maximum service demand for specific tech
                tech_install_p = calc_service_fuel_switched(
                    enduse_fuel_switches,
                    technologies,
                    s_fueltype_by_p,
                    s_tech_by_p,
                    fuel_tech_p_by,
                    'max_switch')

                # Read L-values with calculating maximum sigmoid theoretical diffusion
                l_values_sig[technology] = tech_install_p[technology]

    return l_values_sig

def calc_service_fuel_switched(
        fuel_switches,
        technologies,
        s_fueltype_by_p,
        s_tech_by_p,
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
    s_fueltype_by_p : dict
        Service share per fueltype in base year
    s_tech_by_p : dict
        Share of service demand per technology for base year
    fuel_tech_p_by : dict
        Fuel shares for each technology of an enduse for base year
    switch_type : str
        If either switch is for maximum theoretical switch
        of with defined switch until end year

    Return
    ------
    s_tech_switched_p : dict
        Service in future year with added and substracted
        service demand for every technology

    Note
    ----
    Assertion may be removed to increase speed
    """
    s_tech_switched_p = {}

    for fuel_switch in fuel_switches:

        tech_install = fuel_switch.technology_install
        tech_replace_fueltype = fuel_switch.fueltype_replace

        # Share of energy service of repalced fueltype before switch in base year
        service_p_by = s_fueltype_by_p[tech_replace_fueltype]

        # Service share of fueltype that will be switched
        if switch_type == 'max_switch':
            s_diff_fueltype_by_p = service_p_by * technologies[tech_install].tech_max_share
        elif switch_type == 'actual_switch':
            s_diff_fueltype_by_p = service_p_by * fuel_switch.fuel_share_switched_ey

        # ----------------
        # Service addition
        # ----------------
        s_tech_switched_p[tech_install] = s_tech_by_p[tech_install] + s_diff_fueltype_by_p

        # ----------------
        # Service substraction
        # ----------------
        # Iterate technologies which are replaced for this fueltype and substract service demand proportionally

        # Technologies with lower demands
        technologies_replaced = list(fuel_tech_p_by[tech_replace_fueltype].keys())

        # Calculate proportional share of technologies in replaced fueltype in by
        tot_by_share = 0
        for tech in technologies_replaced:
            tot_by_share += s_tech_by_p[tech]

        # Substract switched share proportionally to base year service in fueltype
        for tech in technologies_replaced:

            # Because of rounding error otherwise minus values possible
            round_digits = 5

            # Relative share in by
            rel_tech_by_p = s_tech_by_p[tech] / tot_by_share

            # Substract (service_by - service to switch * relative share)
            s_tech_switched_p[tech] = round(s_tech_by_p[tech], round_digits) - round(s_diff_fueltype_by_p * rel_tech_by_p, round_digits)

            assert s_tech_switched_p[tech] >= 0

    # -----------------------
    # Calculate service fraction of all technologies in
    # enduse not affected by fuel switch
    # -----------------------
    s_affected_p_ey = sum(s_tech_switched_p.values())
    unaffected_service_to_distr_p = 1 - s_affected_p_ey

    # Calculate service fraction of remaining technologies
    fractions_unaffected_switch = {}
    for tech, s_tech_p in s_tech_by_p.items():
        if tech not in s_tech_switched_p.keys():
            fractions_unaffected_switch[tech] = s_tech_p

    # Sum of unaffected service shares
    service_tot_remaining = sum(fractions_unaffected_switch.values())

    # Get relative distribution of all not affected techs
    for tech, tech_fraction in fractions_unaffected_switch.items():

        # Relative share
        s_rel_fraction_p = tech_fraction / service_tot_remaining
        s_tech_switched_p[tech] = s_rel_fraction_p * unaffected_service_to_distr_p

        assert s_tech_switched_p[tech] >= 0 #NEW

    return dict(s_tech_switched_p)

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
    crit_fuel_switch : bool
        Criteria wheter swich is defined or not
    """
    # Add technology list for every enduse with affected switches
    installed_tech = set([])

    for switch in fuel_switches:
        if switch.enduse == enduse:
            installed_tech.add(switch.technology_install)

    if len(list(installed_tech)) > 0:
        crit_fuel_switch = True
    else:
        crit_fuel_switch = False

    return list(installed_tech), crit_fuel_switch

def get_l_values(
        technologies,
        technologies_to_consider,
        regions=False
    ):
    """Get l values (Maximum shares of each technology)
    for all installed technologies

    Arguments
    ----------
    technologies : dict
        Technologies
    technologies_to_consider : list
        Technologies to consider
    s_fueltype_by_p :
        Fraction of service per fueltype in base year
    regions : dict
        Regions

    Return
    ------
    l_values_sig : dict
        Sigmoid paramters
    """
    l_values_sig = defaultdict(dict)

    for region in regions:
        if technologies_to_consider == []:
            pass
        else:
            for tech in technologies_to_consider:
                l_values_sig[region][tech] = technologies[tech].tech_max_share

    return dict(l_values_sig)

def tech_sigmoid_parameters(
        yr_until_switched,
        switch_yr_start,
        technologies,
        l_values,
        s_tech_by_p,
        s_tech_switched_p,
        fit_assump_init=0.001, #TODO FOUND ERROR
        plot_sigmoid_diffusion=False
    ):
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
    switch_yr_start : int
        Start year of story in narrative
    technologies : dict
        technologies
    l_values : dict
        L values for maximum possible diffusion of technologies
    s_tech_by_p : dict
        Energy service demand for base year (1. sigmoid point)
    s_tech_switched_p : dict
        Service demand after fuelswitch
    fit_assump_init : float
        Approximation helping small number to allow fit
    plot_sigmoid_diffusion : bool,default=True
        Criteria whether sigmoid are plotted

    Returns
    -------
    sig_params : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)

    Info
    -----
        `rounding_accuracy`     This rounds the by and ey service share
                                to the defined number of digits. Because of
                                rounding error, there might be very small
                                differences in percentual service demand.
    """
    def calc_m(x1, x2, y1, y2):
        m = (y1-y2) / (x1 - x2)
        return m

    def calc_c(m, x1, y1):
        c = y1 - (m * x1)
        return c

    rounding_accuracy = 4       # Criteria how much difference in % can be rounded
    linear_approx_crit = 0.001  # Criteria to simplify with linear approximation if difference is smaller (decimal)
    error_range = 0.0002        # Error how close the fit must be
    number_of_iterations = 100  # Number of iterations of sigmoid fitting algorithm

    # Technologies to apply calculation
    installed_techs = s_tech_by_p.keys()
    sig_params = defaultdict(dict)

    # Fitting criteria where the calculated sigmoid slope and midpoint can be provided limits
    if installed_techs == []:
        pass
    else:
        for tech in installed_techs:

            # --------
            # Test whether technology has the market entry before or after base year,
            # If afterwards, set very small number in market entry year
            # --------
            if technologies[tech].market_entry > switch_yr_start:
                point_x_by = technologies[tech].market_entry
                point_y_by = fit_assump_init
            else:
                point_x_by = switch_yr_start   # Base year
                point_y_by = s_tech_by_p[tech] # Base year service share

                # If the base year is the market entry year use a very small number
                if point_y_by == 0:
                    point_y_by = fit_assump_init

            # Future energy service demand
            point_x_ey = yr_until_switched
            point_y_ey = s_tech_switched_p[tech]

            # If future share is zero, entry small value #TODO: INSERT AGIAN
            if point_y_ey == 0:
                point_y_ey = fit_assump_init
            elif point_y_ey == 1.0:
                point_y_ey = 1 - fit_assump_init
            else:
                pass

            # Data of the two points
            xdata = np.array([point_x_by, point_x_ey])
            ydata = np.array([point_y_by, point_y_ey])
            #print("FFF {}  {} {}".format(tech, xdata, ydata))
            '''logging.info(
                "... create sigmoid diffusion %s - %s - %s - %s - l_val: %s - %s - %s lval: %s",
                tech,
                xdata,
                ydata,
                fit_assump_init,
                l_values[tech],
                point_y_by,
                point_y_ey,
                linear_approx_crit)'''

            # Test wheter maximum diffusion is larger than simulated end year share
            ## assert ydata[1] <= l_values[tech] + linear_approx_crit

            # If no change in by to ey but not zero (linear change)
            if (round(point_y_by, rounding_accuracy) == round(point_y_ey, rounding_accuracy)) and (
                    point_y_ey != fit_assump_init) and (
                        point_y_by != fit_assump_init):

                # Linear diffusion (because by and ey share are identical)
                sig_params[tech]['midpoint'] = 'linear'
                sig_params[tech]['steepness'] = 'linear'
                sig_params[tech]['l_parameter'] = 'linear'
                
                # Calculate linear slope and linear y-intercept (with two data points)
                sig_params[tech]['linear_slope'] = calc_m(xdata[0], xdata[1], ydata[0], ydata[1])
                sig_params[tech]['linear_y_intercept'] = calc_c(sig_params[tech]['linear_slope'], xdata[0], ydata[0])

                _a = (sig_params[tech]['linear_slope'] * 2050 + sig_params[tech]['linear_y_intercept'])
                if _a < 0:
                    assert _a < 0.0001
            else:
                # Test if no increase or decrease or if no future potential share
                if (point_y_by == fit_assump_init and point_y_ey == fit_assump_init) or (
                        l_values[tech] == 0):
                    sig_params[tech]['midpoint'] = None
                    sig_params[tech]['steepness'] = None
                    sig_params[tech]['l_parameter'] = None
                else:

                    # If difference is smaller than a certain share, approximate with linear
                    if abs(ydata[1] - ydata[0]) < linear_approx_crit:
                        #logging.info("Linear approximation...")
                        sig_params[tech]['midpoint'] = 'linear'
                        sig_params[tech]['steepness'] = 'linear'
                        sig_params[tech]['l_parameter'] = 'linear'

                        # Calculate linear slope and linear y-intercept (with two data points)
                        sig_params[tech]['linear_slope'] = calc_m(xdata[0], xdata[1], ydata[0], ydata[1])
                        sig_params[tech]['linear_y_intercept'] = calc_c(sig_params[tech]['linear_slope'], xdata[0], ydata[0])

                        _a = (sig_params[tech]['linear_slope'] * 2050 + sig_params[tech]['linear_y_intercept'])
                        if _a < 0:
                            assert _a < 0.0001
                    try:
                        # Parameter fitting
                        ##print("----start fitting" ) #, flush=True)
                        fit_parameter = calc_sigmoid_parameters(
                            l_values[tech],
                            xdata,
                            ydata,
                            fit_assump_init=fit_assump_init,
                            error_range=error_range,
                            number_of_iterations=number_of_iterations)

                        sig_params[tech]['midpoint'] = fit_parameter[0]
                        sig_params[tech]['steepness'] = fit_parameter[1]
                        sig_params[tech]['l_parameter'] = l_values[tech] # maximum p

                        '''if plot_sigmoid_diffusion:
                            basic_plot_functions.plotout_sigmoid_tech_diff(
                                l_values[tech],
                                tech,
                                xdata,
                                ydata,
                                fit_parameter,
                                plot_crit=True,
                                close_window_crit=True)'''
                    except:
                        """If sigmoid fitting failed, implement linear diffusion

                        The sigmoid diffusion may fail if the fitting does not work
                        because the points to fit are too similar. This could be 
                        improved by increasing the number of iterations 'number_of_iterations'
                        at higher computation costs
                        """
                        #logging.warning("Instead of sigmoid a linear approximation is used %s %s %s", tech, xdata, ydata)
                        sig_params[tech]['midpoint'] = 'linear'
                        sig_params[tech]['steepness'] = 'linear'
                        sig_params[tech]['l_parameter'] = 'linear'

                        # Calculate linear slope and linear y-intercept (with two data points)
                        sig_params[tech]['linear_slope'] = calc_m(xdata[0], xdata[1], ydata[0], ydata[1])
                        sig_params[tech]['linear_y_intercept'] = calc_c(sig_params[tech]['linear_slope'], xdata[0], ydata[0])

                        _a = (sig_params[tech]['linear_slope'] * 2050 + sig_params[tech]['linear_y_intercept'])
                        if _a < 0:
                            assert _a < 0.0001
     
    return dict(sig_params)
