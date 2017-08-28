"""Functions related to technologies
"""
import numpy as np
from energy_demand.technologies import diffusion_technologies as diffusion

def get_heatpump_eff(temp_yr, efficiency_intersect, t_base_heating):
    """Calculate efficiency according to temperature difference of base year

    Parameters
    ----------
    temp_yr : array
        Temperatures for every hour in a year (365, 24)
    efficiency_intersect : float
        Y-value (Efficiency) at 10 degree difference
    t_base_heating : float
        Base temperature for heating

    Return
    ------
    eff_hp_yh : array
        Efficiency for every hour in a year  (365, 24)

    Note
    -----
    - For every hour the temperature difference is calculated  and the efficiency
      of the heat pump calculated based on efficiency assumptions
    - The efficiency assumptions of the heat pump are taken from Staffell et al. (2012).

      Staffell, I., Brett, D., Brandon, N., & Hawkes, A. (2012). A review of domestic heat pumps.
      Energy & Environmental Science, 5(11), 9291. https://doi.org/10.1039/c2ee22653g
    """

    # Calculate temperature difference to t_base_heating
    temp_difference_temp_yr = np.abs(temp_yr - t_base_heating)

    # Calculate efficiency
    eff_hp_yh = eff_heat_pump(temp_difference_temp_yr, efficiency_intersect)

    return eff_hp_yh

def eff_heat_pump(temp_diff, efficiency_intersect, m_slope=-.08, h_diff=10):
    """Calculate efficiency of heat pump

    Parameters
    ----------
    temp_diff: array
        Temperature difference
    efficiency_intersect : float,default=-0.08
        Extrapolated intersect at temp diff of 10 degree (which is treated as efficiency)
    m_slope : float, default=10
        Temperature dependency of heat pumps (slope) derived from Staffell et al. (2012),
    h_diff : float
        Temperature difference

    Return
    ------
    efficiency_hp : array
        Efficiency of heat pump

    Note
    ----
    Because the efficieny of heat pumps is temperature dependent, the efficiency needs to
    be calculated based on slope and intersect which is provided as input for temp difference 10
    and treated as efficiency

    The intersect at temp differenc 10 is for ASHP about 6, for GSHP about 9
    """
    #efficiency_hp = m_slope * h_diff + (intersect + (-1 * m_slope * 10))
    #var_c = efficiency_intersect - (m_slope * h_diff)
    #var_c = efficiency_intersect - (m_slope * h_diff)
    #efficiency_hp = m_slope * temp_diff + var_c

    #SLOW
    efficiency_hp = m_slope * temp_diff + (efficiency_intersect - (m_slope * h_diff))

    #FAST
    #efficiency_hp = -.08 * temp_diff + (efficiency_intersect - (-0.8))
    return efficiency_hp

def const_eff_yh(input_eff):
    """Assing a constant efficiency to every hour in a year

    Parameters
    ----------
    input_eff : float
        Efficiency of a technology

    Return
    ------
    eff_yh : array
        Array with efficency for every hour in a year (365,24)
    """
    eff_yh = np.full((365, 24), input_eff)

    return eff_yh

def get_fueltype_str(fueltype_lu, fueltype_nr):
    """Read from dict the fueltype string based on fueltype KeyError

    Inputs
    ------
    fueltype_lu : dict
        Fueltype lookup dictionary
    fueltype_nr : int
        Key which is to be found in lookup dict

    Returns
    -------
    fueltype_in_string : str
        Fueltype string
    """
    for fueltype_str in fueltype_lu:
        if fueltype_lu[fueltype_str] == fueltype_nr:
            return fueltype_str

def get_fueltype_int(fueltype_lu, fueltype_string):
    """Read from dict the fueltype string based on fueltype KeyError

    Inputs
    ------
    fueltype_lu : dict
        Fueltype lookup dictionary
    fueltype_string : int
        Key which is to be found in lookup dict

    Returns
    -------
    fueltype_in_string : str
        Fueltype string
    """
    return fueltype_lu[fueltype_string]

def get_tech_type(tech_name, technology_list):
    """Get technology type of technology

    Parameters
    ----------
    tech_name : string
        Technology name

    technology_list : dict
        All technology lists are defined in assumptions

    Returns
    ------
    tech_type : string
        Technology type
    
    Note
    -----
    -  Either a technology is a hybrid technology, a heat pump,
       a constant heating technology or a regular technolgy
    """
    if tech_name in technology_list['tech_heating_hybrid']:
        tech_type = 'hybrid_tech'
    elif tech_name in technology_list['tech_heating_temp_dep']:
        tech_type = 'heat_pump'
    elif tech_name in technology_list['tech_heating_const']:
        tech_type = 'boiler_heating_tech'
    elif tech_name in technology_list['primary_heating_electricity']:
        tech_type = 'storage_heating_electricity'
    elif tech_name in technology_list['secondary_heating_electricity']:
        tech_type = 'secondary_heating_electricity'
    elif tech_name == 'dummy_tech':
        tech_type = 'dummy_tech'
    else:
        tech_type = 'regular_tech'

    return tech_type

def generate_heat_pump_from_split(data, temp_dependent_tech_list, technologies, heat_pump_assump):
    """Delete all heat_pump from tech dict, define average new heat pump
    technologies 'av_heat_pump_fueltype' with efficiency depending on installed ratio

    Parameters
    ----------
    temp_dependent_tech_list : list
        List to store temperature dependent technologies (e.g. heat-pumps)
    technologies : dict
        Technologies
    heat_pump_assump : dict
        The split of the ASHP and GSHP

    Returns
    -------
    technologies : dict
        Technologies with added averaged heat pump technologies for every fueltype
    temp_dependent_tech_list : list
        List with added temperature dependent technologies

    Note
    ----
    - Market Entry of different technologies must be the same year!
      (the lowest is selected if different years)
    - Diff method is linear
    """
    heat_pumps = []

    # Calculate average efficiency of heat pump depending on installed ratio
    for fueltype in heat_pump_assump:

        av_eff_hps_by, av_eff_hps_ey, eff_achieved_av, market_entry_lowest = 0, 0, 0, 2200

        for heat_pump_type in heat_pump_assump[fueltype]:
            share_heat_pump = heat_pump_assump[fueltype][heat_pump_type]
            eff_heat_pump_by = technologies[heat_pump_type]['eff_by']
            eff_heat_pump_ey = technologies[heat_pump_type]['eff_ey']
            eff_achieved = technologies[heat_pump_type]['eff_achieved']
            market_entry = technologies[heat_pump_type]['market_entry']

            # Calc average values
            av_eff_hps_by += share_heat_pump * eff_heat_pump_by
            av_eff_hps_ey += share_heat_pump * eff_heat_pump_ey
            eff_achieved_av += share_heat_pump * eff_achieved

            if market_entry < market_entry_lowest:
                market_entry_lowest = market_entry

        # Add average 'av_heat_pumps' to technology dict
        name_av_hp = "heat_pumps_{}".format(str(get_fueltype_str(data['lu_fueltype'], fueltype)))

        #print("...create new averaged heat pump technology: " + str(name_av_hp))

        # Add technology to temperature dependent technology list
        temp_dependent_tech_list.append(name_av_hp)

        # Add new averaged technology
        technologies[name_av_hp] = {}
        technologies[name_av_hp]['fuel_type'] = fueltype
        technologies[name_av_hp]['eff_by'] = av_eff_hps_by
        technologies[name_av_hp]['eff_ey'] = av_eff_hps_ey
        technologies[name_av_hp]['eff_achieved'] = eff_achieved_av
        technologies[name_av_hp]['diff_method'] = 'linear'
        technologies[name_av_hp]['market_entry'] = market_entry_lowest

        heat_pumps.append(name_av_hp)

    # Remove all heat pumps from tech dict
    for fueltype in heat_pump_assump:
        for heat_pump_type in heat_pump_assump[fueltype]:
            del technologies[heat_pump_type]

    return technologies, temp_dependent_tech_list, heat_pumps

def calc_eff_cy(eff_by, technology, base_sim_param, assumptions, eff_achieved_factor, diff_method):
    """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency

    Parameters
    ----------
    eff_by : array
        Efficiency of current year
    technology :
    base_sim_param : dict
        Base simulation parameters
    assumptions : dict
        Assumptions
    eff_achieved_factor : dict
        Efficiency achievement factor (how much of the efficiency is achieved)
    diff_method : str
        Diffusion method

    Returns
    -------
    eff_cy : array
        Array with hourly efficiency of current year

    Notes
    -----
    The development of efficiency improvements over time is assumed to be linear
    This can however be changed with the `diff_method` attribute

    TODO: TODO: Generate two types of sigmoid (convex & concav)
    """
    # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
    if diff_method == 'linear':
        theor_max_eff = diffusion.linear_diff(
            base_sim_param['base_yr'],
            base_sim_param['curr_yr'],
            assumptions['technologies'][technology]['eff_by'],
            assumptions['technologies'][technology]['eff_ey'],
            base_sim_param['sim_period_yrs']
        )
    elif diff_method == 'sigmoid':

        theor_max_eff = diffusion.sigmoid_diffusion(
            base_sim_param['base_yr'],
            base_sim_param['curr_yr'],
            base_sim_param['end_yr'],
            assumptions['other_enduse_mode_info']['sig_midpoint'],
            assumptions['other_enduse_mode_info']['sig_steeppness'])

    # Consider actual achieved efficiency
    actual_max_eff = theor_max_eff * eff_achieved_factor

    # Differencey in efficiency change
    efficiency_change = actual_max_eff * (
        assumptions['technologies'][technology]['eff_ey'] - assumptions['technologies'][technology]['eff_by'])

    # Actual efficiency potential
    eff_cy = eff_by + efficiency_change

    return eff_cy

def get_all_defined_hybrid_technologies(assumptions, technologies, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
    """All hybrid technologies and their charactersitics are defined

    Parameters
    ----------
    assumptions : dict
        Assumptions
    technologies : dict
        Technologies
    hybrid_cutoff_temp_low : float
        Temperature below which 100% of service is provided by
        low temperature technology (typically heat pump)
    hybrid_cutoff_temp_high : float
        Temperature above which 100% of service is provided by high
        temperature technology (typically boiler)

    Return
    ------
    technologies : dict
        Technologies
    hybrid_technologies : list
        Name of hybrid technologies
    hybrid_tech : dict
        Definition of hybrid technologies

    Note
    ----
    - The low and high temperature technology is defined, whereby the high temperature technology
      must be a heatpump.

    - Cut off temperatures can be defined to change the share of service for each
      technology at a given temperature (see doumentation for more information)

    - So far, the standard heat pump is only electricity. Can be changed however

    #TODO: DEFINE WITH REAL VALUES
    """
    hybrid_tech = {
        'hybrid_gas_electricity': {
            "tech_low_temp": 'boiler_gas',
            "tech_high_temp": 'heat_pumps_electricity',
            "hybrid_cutoff_temp_low": hybrid_cutoff_temp_low,
            "hybrid_cutoff_temp_high": hybrid_cutoff_temp_high,
            "average_efficiency_national_by": get_average_eff_by(
                tech_low_temp='boiler_gas',
                tech_high_temp='heat_pumps_electricity',
                assump_service_share_low_tech=0.2,
                assumptions=assumptions
                )
            },
        'hybrid_hydrogen_electricity': {
            "tech_low_temp": 'boiler_hydrogen',
            "tech_high_temp": 'heat_pumps_electricity',
            "hybrid_cutoff_temp_low": hybrid_cutoff_temp_low,
            "hybrid_cutoff_temp_high": hybrid_cutoff_temp_high,
            "average_efficiency_national_by": get_average_eff_by(
                tech_low_temp='boiler_hydrogen',
                tech_high_temp='heat_pumps_electricity',
                assump_service_share_low_tech=0.2,
                assumptions=assumptions
                )
            },
        'hybrid_biomass_electricity': {
            "tech_low_temp": 'boiler_biomass',
            "tech_high_temp": 'heat_pumps_electricity',
            "hybrid_cutoff_temp_low": hybrid_cutoff_temp_low,
            "hybrid_cutoff_temp_high": hybrid_cutoff_temp_high,
            "average_efficiency_national_by": get_average_eff_by(
                tech_low_temp='boiler_biomass',
                tech_high_temp='heat_pumps_electricity',
                assump_service_share_low_tech=0.2,
                assumptions=assumptions
                )
            },
    }

    # Hybrid technologies
    hybrid_technologies = hybrid_tech.keys()

    # Add hybrid technologies to technological stock and define other attributes
    for tech_name, tech in hybrid_tech.items():

        #print("Add hybrid technology to technology stock {}".format(tech_name))
        technologies[tech_name] = tech
        technologies[tech_name]['eff_achieved'] = 1
        technologies[tech_name]['diff_method'] = 'linear'

        # Select market entry of later appearing technology
        entry_tech_low = assumptions['technologies'][tech['tech_low_temp']]['market_entry']
        entry_tech_high = assumptions['technologies'][tech['tech_high_temp']]['market_entry']

        if entry_tech_low < entry_tech_high:
            technologies[tech_name]['market_entry'] = entry_tech_high
        else:
            technologies[tech_name]['market_entry'] = entry_tech_low

    return technologies, list(hybrid_technologies), hybrid_tech

def generate_ashp_gshp_split(split_factor, data):
    """Assing split for each fueltype of heat pump technologies

    Parameters
    ----------
    split_factor : float
        Fraction of ASHP to GSHP
    data : dict
        Data

    Returns
    --------
    installed_heat_pump : dict
        Ditionary with split of heat pumps for every fueltype

    Note
    -----
    The heat pump technologies need to be defined in ``get_all_defined_hybrid_technologies``
    """
    ashp_fraction = split_factor
    gshp_fraction = 1 - split_factor

    installed_heat_pump = {
        data['lu_fueltype']['hydrogen']: {
            'heat_pump_ASHP_hydro': ashp_fraction,
            'heat_pump_GSHP_hydro': gshp_fraction
            },
        data['lu_fueltype']['electricity']: {
            'heat_pump_ASHP_electricity': ashp_fraction,
            'heat_pump_GSHP_electricity': gshp_fraction
            },
        data['lu_fueltype']['gas']: {
            'heat_pump_ASHP_gas': ashp_fraction,
            'heat_pump_GSHP_gas': gshp_fraction
            },
    }

    return installed_heat_pump

def get_average_eff_by(tech_low_temp, tech_high_temp, assump_service_share_low_tech, assumptions):
    """Calculate average efficiency for base year of hybrid technologies for
    overall national energy service calculation

    Parameters
    ----------
    tech_low_temp : str
        Technology for lower temperatures
    tech_high_temp : str
        Technology for higher temperatures
    assump_service_share_low_tech : float
        Assumption about the overall share of the service provided
        by the technology used for lower temperatures
        (needs to be between 1.0 and 0)
    assumptions : dict
        Assumptions

    Returns
    -------
    av_eff : float
        Average efficiency of hybrid tech

    Note
    -----
    It is necssary to define an average efficiency of hybrid technologies to calcualte
    the share of total energy service in base year for the whole country. Because
    the input is fuel for the whole country, it is not possible to calculate the
    share for individual regions
    """
    # The average is calculated for the 10 temp difference intercept
    # because input for heat pumps is provided for 10 degree differences
    average_h_diff_by = 10

    # Service shares
    service_low_temp_tech_p = assump_service_share_low_tech
    service_high_temp_tech_p = 1 - assump_service_share_low_tech

    # Efficiencies of technologies of hybrid tech
    if tech_low_temp in assumptions['technology_list']['tech_heating_temp_dep']:
        eff_tech_low_temp = eff_heat_pump(
            temp_diff=average_h_diff_by,
            efficiency_intersect=assumptions['technologies'][tech_low_temp]['eff_by'])
    else:
        eff_tech_low_temp = assumptions['technologies'][tech_low_temp]['eff_by']

    if tech_high_temp in assumptions['technology_list']['tech_heating_temp_dep']:
        eff_tech_high_temp = eff_heat_pump(
            temp_diff=average_h_diff_by,
            efficiency_intersect=assumptions['technologies'][tech_high_temp]['eff_by'])
    else:
        eff_tech_high_temp = assumptions['technologies'][tech_high_temp]['eff_by']

    # Weighted average efficiency
    av_eff = service_low_temp_tech_p * eff_tech_low_temp + service_high_temp_tech_p * eff_tech_high_temp

    return av_eff
