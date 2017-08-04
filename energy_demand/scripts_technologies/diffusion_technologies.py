"""Funtions related to the diffusion of technologies
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
import math
import copy
import numpy as np
from scipy.optimize import curve_fit
from energy_demand.scripts_initalisations import initialisations as init
from energy_demand.scripts_plotting import plotting_program as plotting

def linear_diff(base_yr, curr_yr, value_start, value_end, sim_years):
    """This function assumes a linear fuel_enduse_switch diffusion.

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.
    Parameters
    ----------
    base_yr : int
        The year of the current simulation.
    curr_yr : int
        The year of the current simulation.
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    sim_years : str
        Total number of simulated years.

    Returns
    -------
    fract_sy : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    # If current year is base year, return zero
    if curr_yr == base_yr or sim_years == 0:
        fract_sy = 0
    else:
        #-1 because in base year no change
        fract_sy = ((value_end - value_start) / (sim_years - 1)) * (curr_yr - base_yr)

    return fract_sy

def sigmoid_function(x_value, l_value, midpoint, steepness):
    """Sigmoid function

    Paramters
    ---------
    x_value : float
        X-Value
    l_value : float
        The curv'es maximum value
    midpoint : float
        The midpoint x-value of the sigmoid's midpoint
    k : dict
        The steepness of the curve

    Return
    ------
    y : float
        Y-Value

    Notes
    -----
    This function is used for fitting and plotting

    """
    y_value = l_value / (1 + np.exp(-steepness * ((x_value - 2000) - midpoint)))

    return y_value

def sigmoid_diffusion(base_yr, curr_yr, end_yr, sig_midpoint, sig_steeppness):
    """Calculates a sigmoid diffusion path of a lower to a higher value with
    assumed saturation at the end year

    Parameters
    ----------
    base_yr : int
        Base year of simulation period
    curr_yr : int
        The year of the current simulation
    end_yr : int
        The year a fuel_enduse_switch saturaes
    sig_midpoint : float
        Mid point of sigmoid diffusion function can be used to shift
        curve to the left or right (standard value: 0)
    sig_steeppness : float
        Steepness of sigmoid diffusion function The steepness of the
        sigmoid curve (standard value: 1)

    Returns
    -------
    cy_p : float
        The fraction of the diffusion in the current year

    Infos
    -------
    It is always assuemed that for the simulation year the share is
    replaced with technologies having the efficencies of the current year. For technologies
    which get replaced fast (e.g. lightbulb) this is corret assumption, for longer lasting
    technologies, this is more problematic (in this case, over every year would need to be iterated
    and calculate share replaced with efficiency of technology in each year).

    TODO: Always return positive value. Needs to be considered for changes in negative
    """
    if curr_yr == base_yr:
        return 0

    if curr_yr == end_yr:
        return 1 # 100 % diffusion
    else:
        # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
        if end_yr == base_yr:
            y_trans = 5.0
        else:
            y_trans = -5.0 + (10.0 / (end_yr - base_yr)) * (curr_yr - base_yr)

        # Get a value between 0 and 1 (sigmoid curve ranging from 0 to 1)
        cy_p = 1.0 / (1 + math.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

        return cy_p

def fit_sigmoid_diffusion(l_value, x_data, y_data, start_parameters):
    """Fit sigmoid curve based on two points on the diffusion curve

    Parameters
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

    Info
    ----
    The Sigmoid is substacted - 2000 to allow for better fit with low values

    RuntimeWarning is ignored

    """
    def sigmoid_fitting_function(x_value, x0_value, k_value):
        """Sigmoid function used for fitting
        """
        y_value = l_value / (1 + np.exp(-k_value * ((x_value - 2000) - x0_value)))

        return y_value

    popt, _ = curve_fit(sigmoid_fitting_function, x_data, y_data, p0=start_parameters)

    return popt

def get_sig_diffusion(data, service_switches, fuel_switches, enduses, tech_increased_service, share_service_tech_ey_p, enduse_tech_maxl_by_p, service_fueltype_by_p, service_tech_by_p, fuel_enduse_tech_p_by):
    """Calculates parameters for sigmoid diffusion of technologies which are switched to/installed.

    Parameters
    ----------
    data : dict
        Data
    service_switches : dict
        Service switches
    fuel_swithes : dict
        Fuel switches
    enduses : list
        Enduses
    fuels : array
        Fuels

    Return
    ------
    data : dict
        Data dictionary containing all calculated parameters in assumptions

    Info
    ----
    It is assumed that the technology diffusion is the same over all the uk (no regional different diffusion)
    """
    # Test is Service Switch is implemented
    if len(service_switches) > 0:
        crit_switch_service = True
        print("...crit_switch_service  " + str(crit_switch_service))
    else:
        crit_switch_service = False

    installed_tech = {}
    sig_param_tech = {}

    for enduse in enduses:
        if crit_switch_service: # Sigmoid calculation in case of 'service switch'

            # Tech with lager service shares in end year
            installed_tech = tech_increased_service

            # End year service shares (scenaric input)
            service_tech_switched_p = share_service_tech_ey_p

            # Maximum shares of each technology
            l_values_sig = enduse_tech_maxl_by_p

        else: # Sigmoid calculation in case of 'fuel switch'

            # Tech with lager service shares in end year (installed in fuel switch)
            installed_tech = get_tech_installed(enduses, fuel_switches)

            # Calculate future service demand after fuel switches for each technology
            service_tech_switched_p = calc_service_fuel_switched(
                enduses,
                fuel_switches,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_enduse_tech_p_by,
                installed_tech,
                'actual_switch'
            )

            # Calculate L for every technology for sigmod diffusion
            l_values_sig = tech_l_sigmoid(
                enduses,
                fuel_switches,
                installed_tech,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_enduse_tech_p_by
                )

        # -------------------------------------------------------------
        # Calclulate sigmoid parameters for every installed technology
        # -------------------------------------------------------------
        sig_param_tech[enduse] = tech_sigmoid_parameters(
            data,
            enduse,
            crit_switch_service,
            installed_tech,
            l_values_sig,
            service_tech_by_p,
            service_tech_switched_p,
            fuel_switches
        )

    return installed_tech, sig_param_tech

def tech_l_sigmoid(enduses, fuel_switches, installed_tech, service_fueltype_p, service_tech_by_p, fuel_enduse_tech_p_by):
    """Calculate L value for every installed technology with maximum theoretical replacement value

    Parameters
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
    l_values_sig = init.init_dict(enduses, 'brackets')

    for enduse in enduses:
        # Check wheter there are technologies in this enduse which are switched

        if installed_tech[enduse] == []:
            #print("No technologies to calculate sigmoid  {}".format(enduse))
            pass
        else:
            print("Technologes it calculate sigmoid  {}  {}".format(enduse, installed_tech[enduse]))

            # Iterite list with enduses where fuel switches are defined
            for technology in installed_tech[enduse]:
                print("Technology: {} Enduse:  {}".format(technology, enduse))
                # Calculate service demand for specific tech
                tech_install_p = calc_service_fuel_switched(
                    enduses,
                    fuel_switches,
                    service_fueltype_p,
                    service_tech_by_p, # Percentage of service demands for every technology
                    fuel_enduse_tech_p_by,
                    {str(enduse): [technology]},
                    'max_switch'
                    )

                # Read L-values with calculating maximum sigmoid theoretical diffusion
                l_values_sig[enduse][technology] = tech_install_p[enduse][technology]

    return l_values_sig

def tech_sigmoid_parameters(data, enduse, crit_switch_service, installed_tech, l_values, service_tech_by_p, service_tech_switched_p, fuel_switches):
    """Calculate diffusion parameters based on energy service demand in base year and projected future energy service demand

    The future energy servie demand is calculated based on fuel switches.
    A sigmoid diffusion is fitted.

    Parameters
    ----------
    data : dict
        data
    enduses : enduses
        enduses
    crit_switch_service : bool
        Criteria whether sigmoid is calculated for service switch or not
    installed_tech : dict
        Technologies for enduses with fuel switch
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
    NTH: improve fitting

    Manually the fitting parameters can be defined which are not considered as
    a good fit: fit_crit_a, fit_crit_b
    If service definition, the year until switched is the end model year

    """
    #sigmoid_parameters = init.init_nested_dict(enduses, installed_tech, 'brackets')
    sigmoid_parameters = {}

    #-----------------
    # Fitting criteria where the calculated sigmoid slope and midpoint can be provided limits
    #-----------------
    fit_crit_a = 200
    fit_crit_b = 0.001

    if installed_tech[enduse] == []:
        print("NO TECHNOLOGY...{}  {}".format(enduse, installed_tech[enduse]))
    else:
        for technology in installed_tech[enduse]:
            print("... create sigmoid difufsion parameters {}  {}".format(enduse, technology))
            sigmoid_parameters[technology] = {}

            # If service switch
            if crit_switch_service:
                year_until_switched = data['base_sim_param']['end_yr'] # Year until service is switched
                market_entry = data['assumptions']['technologies'][technology]['market_entry']
            else:

                # Get the most future year of the technology in the enduse which is switched to
                year_until_switched = 0
                for switch in fuel_switches:
                    if switch['enduse'] == enduse and switch['technology_install'] == technology:
                        if year_until_switched < switch['year_fuel_consumption_switched']:
                            year_until_switched = switch['year_fuel_consumption_switched']

                market_entry = data['assumptions']['technologies'][technology]['market_entry']

            # --------
            # Test whether technology has the market entry before or after base year,
            # If afterwards, set very small number in market entry year
            # --------
            if market_entry > data['base_sim_param']['base_yr']:
                point_x_by = market_entry
                point_y_by = 0.001 # very small service share if market entry in a future year
            else: # If market entry before, set to 2015
                point_x_by = data['base_sim_param']['base_yr']
                point_y_by = service_tech_by_p[enduse][technology] # current service share

                #If the base year is the market entry year use a very small number
                if point_y_by == 0:
                    point_y_by = 0.001

            # Future energy service demand (second point on sigmoid curve for fitting)
            point_x_projected = year_until_switched
            point_y_projected = service_tech_switched_p[enduse][technology]

            # Data of the two points
            xdata = np.array([point_x_by, point_x_projected])
            ydata = np.array([point_y_by, point_y_projected])

            print("DATA TO FIT:   {}   {}".format(xdata, ydata))

            # ----------------
            # Parameter fitting
            # ----------------
            # Generate possible starting parameters for fit
            possible_start_parameters = [1.0, 0.001, 0.01, 0.1, 60, 100, 200, 400, 500, 1000]
            for start in [x * 0.05 for x in range(0, 100)]:
                possible_start_parameters.append(start)
            for start in range(1, 59):
                possible_start_parameters.append(start)

            cnt = 0
            successfull = False
            while not successfull:
                start_parameters = [
                    possible_start_parameters[cnt],
                    possible_start_parameters[cnt]
                    ]
                try:
                    '''
                    print("----------- Technology " + str(technology) + str("  ") + str(cnt))
                    print("xdata: " + str(point_x_by) + str("  ") + str(point_x_projected))
                    print("ydata: " + str(point_y_by) + str("  ") + str(point_y_projected))
                    print("Lvalue: " + str(l_values[enduse][technology]))
                    print("start_parameters: " + str(start_parameters))
                    '''
                    fit_parameter = fit_sigmoid_diffusion(l_values[enduse][technology], xdata, ydata, start_parameters)
                    #print("fit_parameter: " + str(fit_parameter))

                    # Criteria when fit did not work
                    if fit_parameter[0] > fit_crit_a or fit_parameter[0] < fit_crit_b or fit_parameter[1] > fit_crit_a or fit_parameter[1] < 0  or fit_parameter[0] == start_parameters[0] or fit_parameter[1] == start_parameters[1]:
                        successfull = False
                        cnt += 1
                        if cnt >= len(possible_start_parameters):
                            sys.exit("Error2: CURVE FITTING DID NOT WORK")
                    else:
                        successfull = True
                        print("Fit successful {} for Technology: {} with fitting parameters: {} ".format(successfull, technology, fit_parameter))
                except:
                    #print("Tried unsuccessfully to do the fit with the following parameters: " + str(start_parameters[1]))
                    cnt += 1

                    if cnt >= len(possible_start_parameters):
                        sys.exit("Error: CURVE FITTING DID NOT WORK. Try changing fit_crit_a and fit_crit_b")

            # Insert parameters
            sigmoid_parameters[technology]['midpoint'] = fit_parameter[0] #midpoint (x0)
            sigmoid_parameters[technology]['steepness'] = fit_parameter[1] #Steepnes (k)
            sigmoid_parameters[technology]['l_parameter'] = l_values[enduse][technology]

            #plot sigmoid curve
            plotting.plotout_sigmoid_tech_diff(
                l_values,
                technology,
                enduse,
                xdata,
                ydata,
                fit_parameter,
                True
                )

    return sigmoid_parameters

def get_tech_installed(enduses, fuel_switches):
    """Read out all technologies which are specifically switched to

    Parameter
    ---------
    fuel_switches : dict
        All fuel switches where a share of a fuel of an enduse is switched to a specific technology

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

def calc_service_fuel_switched(enduses, fuel_switches, service_fueltype_p, service_tech_by_p, fuel_enduse_tech_p_by, installed_tech_switches, switch_type):
    """Calculate energy service demand percentages after fuel switches

    Parameters
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    fuel_switches : dict
        Fuel switches
    service_fueltype_p : dict
        Service demand per fueltype
    fuel_tech_p_by : dict
        Technologies in base year
    service_tech_by_p : dict
        Percentage of service demand per technology for base year
    tech_fueltype_by : dict
        Technology stock
    fuel_enduse_tech_p_by : dict
        Fuel shares for each technology of an enduse
    installed_tech_switches : dict
        Technologies which are installed in fuel switches
    maximum_switch : crit
        Wheater this function is executed with the switched fuel share or the maximum switchable fuel share

    Return
    ------
    service_tech_switched_p : dict
        Service in future year with added and substracted service demand for every technology

    Notes
    -----
    Implement changes in heat demand (all technolgies within a fueltypes are replaced proportionally)
    """
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
                        change_service_fueltype_p = orig_service_p * fuel_switch['max_theoretical_switch'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent
                    elif switch_type == 'actual_switch':
                        change_service_fueltype_p = orig_service_p * fuel_switch['share_fuel_consumption_switched'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent

                    # ---SERVICE DEMAND ADDITION
                    service_tech_switched_p[enduse][tech_install] += change_service_fueltype_p

                    # Get all technologies which are replaced related to this fueltype
                    replaced_tech_fueltype = fuel_enduse_tech_p_by[enduse][fueltype_tech_replace].keys()

                    # Calculate total energy service in this fueltype, Substract service demand for replaced technologies
                    for tech in replaced_tech_fueltype:
                        service_tech_switched_p[enduse][tech] -= change_service_fueltype_p * service_tech_by_p[enduse][tech]

    return service_tech_switched_p
