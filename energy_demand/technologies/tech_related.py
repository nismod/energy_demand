"""Functions related to technologies
"""
import logging
import numpy as np
from energy_demand.technologies import diffusion_technologies as diffusion
from energy_demand.read_write import read_data

def insert_dummy_tech(technologies, tech_p_by, all_specified_tech_enduse_by):
    """Define dummy technologies. Where no specific technologies are
    assigned for an enduse and a fueltype, dummy technologies
    are generated. This is necessary because the model needs
    a technology for every fueltype in an enduse.

    Arguments
    ----------
    technologies : dict
        Technologies
    tech_p_by : dict
        Fuel assignement of technologies in base year
    all_specified_tech_enduse_by : dict
        Technologies per enduse

    Returns
    -------
    tech_p_by : dict
        Fuel assignement of technologies in base year
    all_specified_tech_enduse_by : dict
        Technologies per enduse
    technologies : dict
        Technologies
    """
    for end_use in tech_p_by:
        for fuel_type in tech_p_by[end_use]:
            all_defined_tech_in_fueltype = tech_p_by[end_use].values()
            for definition in all_defined_tech_in_fueltype:

                crit_tech_defined_in_enduse = False
                all_defined_tech_in_fueltype = tech_p_by[end_use].values()
                for definition in all_defined_tech_in_fueltype:
                    if definition == {}:
                        #crit_tech_defined_in_enduse = False #
                        pass
                    else:
                        crit_tech_defined_in_enduse = True
                        continue

            # If an enduse has no defined technologies across all fueltypes
            if crit_tech_defined_in_enduse is False:
                if tech_p_by[end_use][fuel_type] == {}:
                    all_specified_tech_enduse_by[end_use].append("dummy_tech")

                    # Assign total fuel demand to dummy technology
                    tech_p_by[end_use][fuel_type] = {"dummy_tech": 1.0}

                    # Insert dummy tech
                    technologies['dummy_tech'] = read_data.TechnologyData()

    return tech_p_by, all_specified_tech_enduse_by, technologies

def get_enduses_with_dummy_tech(enduse_tech_p_by):
    """Find all enduses with defined dummy technologies

    Arguments
    ----------
    enduse_tech_p_by : dict
        Fuel share definition of technologies

    Return
    ------
    dummy_enduses : list
        List with all endueses with dummy technologies
    """
    dummy_enduses = []
    for enduse, fueltype_techs in enduse_tech_p_by.items():
        for techs in fueltype_techs.values():
            for tech in techs:
                if tech == 'dummy_tech':
                    dummy_enduses.append(enduse)
                    continue

    return list(set(dummy_enduses))

def calc_hp_eff(temp_yh, efficiency_intersect, t_base_heating):
    """Calculate efficiency of heat pumps according to
    temperature difference.

    Arguments
    ----------
    temp_yh : array
        Temperatures for every hour in a year
    efficiency_intersect : float
        Y-value (Efficiency) at 10 degree difference
    t_base_heating : float
        Base temperature for heating

    Return
    ------
    av_eff_hp : float
        Average eEfficiency for every hour in a year

    Note
    -----
    - For every hour the temperature difference is calculated and the efficiency
      of the heat pump calculated based on efficiency assumptions

    - The efficiency assumptions of the heat pump are taken from
      Staffell et al. (2012). Expexted average efficiencies for
      heating are expected to be for ASHP around 3.3 - 3.9, for
      GSHP around 4.5 - 5.4.
      For hot water, it is around 2.3 - 2.8 for ASHP and
      3.1-3.8 for GSHP.

      Staffell, I., Brett, D., Brandon, N., & Hawkes, A. (2012). A review of domestic heat pumps.
      Energy & Environmental Science, 5(11), 9291. https://doi.org/10.1039/c2ee22653g
    """
    # Calculate temperature difference to t_base_heating
    temp_difference_temp_yh = t_base_heating - temp_yh

    #Ignore all hours where no heating is necessary
    temp_difference_temp_yh[temp_difference_temp_yh < 0] = 0

    # Calculate average efficiency of heat pumps over full year
    av_eff_hp = eff_heat_pump(
        temp_difference_temp_yh,
        efficiency_intersect)

    return float(av_eff_hp)

def eff_heat_pump(temp_diff, efficiency_intersect, m_slope=-.08, h_diff=10):
    """Calculate efficiency of heat pumps

    Arguments
    ----------
    temp_diff: array
        Temperature difference between base temperature and temperature
    efficiency_intersect : float,default=-0.08
        Extrapolated intersect at temperature
        difference of 10 degree (which is treated as efficiency)
    m_slope : float, default=10
        Temperature dependency of heat pumps (slope)
    h_diff : float
        Temperature difference

    Return
    ------
    efficiency_hp_mean : array
        Mean efficiency of heat pump

    Note
    ----
    Because the efficieny of heat pumps is temperature dependent, the efficiency needs to
    be calculated based on slope and intersect which is provided as input for temp difference 10
    and treated as efficiency
    """
    #efficiency_hp = m_slope * h_diff + (intersect + (-1 * m_slope * 10))
    #var_c = efficiency_intersect - (m_slope * h_diff)
    #efficiency_hp = m_slope * temp_diff + var_c

    efficiency_hp = m_slope * temp_diff + (efficiency_intersect - (m_slope * h_diff))

    # Calculate average efficiency over whole year
    efficiency_hp_mean = np.mean(efficiency_hp)

    return efficiency_hp_mean

def get_fueltype_str(fueltype_lu, fueltype_nr):
    """Read from dict the fueltype string based on fueltype KeyError

    Inputs
    ------
    fueltype : dict
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

def get_fueltype_int(fueltypes, fueltype_string):
    """Read from dict the fueltype string based on fueltype KeyError

    Inputs
    ------
    fueltype : dict
        Fueltype lookup dictionary
    fueltype_string : int
        Key which is to be found in lookup dict

    Returns
    -------
    fueltype_in_string : str
        Fueltype string
    """
    if fueltypes is None:
        return None
    else:
        return fueltypes[fueltype_string]

def get_tech_type(tech_name, tech_list):
    """Get technology type of technology

    Arguments
    ----------
    tech_name : string
        Technology name

    tech_list : dict
        All technology lists are defined in assumptions

    Returns
    ------
    tech_type : string
        Technology type
    """
    if tech_name in tech_list['tech_heating_temp_dep']:
        tech_type = 'heat_pump'
    elif tech_name in tech_list['tech_heating_const']:
        tech_type = 'boiler_heating_tech'
    elif tech_name in tech_list['primary_heating_electricity']:
        tech_type = 'storage_heating_electricity'
    elif tech_name in tech_list['secondary_heating_electricity']:
        tech_type = 'secondary_heating_electricity'
    elif tech_name == 'dummy_tech':
        tech_type = 'dummy_tech'
    else:
        tech_type = 'regular_tech'

    return tech_type

def calc_av_heat_pump_eff_ey(technologies, heat_pump_assump):
    """Calculate end year average efficiency of
    heat pumps depending on split of heat pumps

    Arguments
    ---------
    technologies : dict
        Technologies

    Return
    ------
    technologies : dict
        Updated technologies
    """
    for fueltype in heat_pump_assump:
        av_eff_hps_ey = 0

        for heat_pump_type in heat_pump_assump[fueltype]:
            share_heat_pump = heat_pump_assump[fueltype][heat_pump_type]
            eff_heat_pump_ey = technologies[heat_pump_type].eff_ey

            # Calc average values
            av_eff_hps_ey += share_heat_pump * eff_heat_pump_ey

        # Add average 'av_heat_pumps' to technology dict
        name_av_hp = "heat_pumps_{}".format(fueltype)

        # Add new averaged technology
        technologies[name_av_hp].eff_ey = av_eff_hps_ey

    return technologies

def generate_heat_pump_from_split(technologies, heat_pump_assump, fueltypes):
    """Define average new heat pumptechnologies 'av_heat_pump_fueltype' with
    efficiency depending on installed ratio of heat pumps

    Arguments
    ----------
    technologies : dict
        Technologies
    heat_pump_assump : dict
        The split of the ASHP and GSHP
    fueltypes : dict
        Fueltypes lookup

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
    temp_dependent_tech_list = []
    heat_pumps = []

    # Calculate average efficiency of heat pump depending on installed ratio
    for fueltype in heat_pump_assump:
        av_eff_hps_by, av_eff_hps_ey, eff_achieved_av, market_entry_lowest = 0, 0, 0, 2200
        av_year_eff_ey = 0

        for heat_pump_type in heat_pump_assump[fueltype]:
            share_heat_pump = heat_pump_assump[fueltype][heat_pump_type]

            eff_heat_pump_by = technologies[heat_pump_type].eff_by
            eff_heat_pump_ey = technologies[heat_pump_type].eff_ey
            eff_achieved = technologies[heat_pump_type].eff_achieved
            market_entry = technologies[heat_pump_type].market_entry
            tech_max_share = technologies[heat_pump_type].tech_max_share

            av_year_eff_ey += technologies[heat_pump_type].year_eff_ey

            # Calc average values
            av_eff_hps_by += share_heat_pump * eff_heat_pump_by
            av_eff_hps_ey += share_heat_pump * eff_heat_pump_ey
            eff_achieved_av += share_heat_pump * eff_achieved

            if market_entry < market_entry_lowest:
                market_entry_lowest = market_entry

        # Calculate average year until efficiency improvements are implemented
        av_year_eff_ey = av_year_eff_ey / len(heat_pump_assump[fueltype])

        # Add average 'av_heat_pumps' to technology dict
        name_av_hp = "heat_pumps_{}".format(fueltype)

        logging.debug("... create new averaged heat pump technology: %s", name_av_hp)

        # Add technology to temperature dependent technology list
        temp_dependent_tech_list.append(name_av_hp)

        # Add new averaged technology
        technologies[name_av_hp] = read_data.TechnologyData(
            fuel_type=fueltype,
            eff_by=av_eff_hps_by,
            eff_ey=av_eff_hps_ey,
            year_eff_ey=av_year_eff_ey,
            eff_achieved=eff_achieved_av,
            diff_method='linear',
            market_entry=market_entry_lowest,
            tech_list='tech_heating_temp_dep',
            tech_max_share=tech_max_share,
            fueltypes=fueltypes)

        heat_pumps.append(name_av_hp)

    return technologies, temp_dependent_tech_list, heat_pumps

def calc_eff_cy(
        base_yr,
        curr_yr,
        eff_by,
        eff_ey,
        yr_until_changed,
        other_enduse_mode_info,
        tech_eff_achieved_f,
        diff_method
    ):
    """Calculate efficiency of current year based on efficiency
    assumptions and achieved efficiency

    Arguments
    ----------
    base_yr : int
        Base year
    curr_yr : int
        Current year
    eff_by : dict
        Base year efficiency
    eff_ey : dict
        End year efficiency
    yr_until_changed : int
        Year for which the eff_ey is defined
    other_enduse_mode_info : Dict
        diffusion information
    tech_eff_achieved_f : dict
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

    TODO: Generate two types of sigmoid (convex & concav)
    """
    # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
    if diff_method == 'linear':
        theor_max_eff = diffusion.linear_diff(
            base_yr,
            curr_yr,
            eff_by,
            eff_ey,
            yr_until_changed)

        # Consider actual achieved efficiency
        eff_cy = theor_max_eff * tech_eff_achieved_f

        return eff_cy

    elif diff_method == 'sigmoid':
        theor_max_eff = diffusion.sigmoid_diffusion(
            base_yr,
            curr_yr,
            yr_until_changed,
            other_enduse_mode_info['sigmoid']['sig_midpoint'],
            other_enduse_mode_info['sigmoid']['sig_steeppness'])

        # Differencey in efficiency change
        efficiency_change = theor_max_eff * (eff_ey - eff_by)

        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change

        return eff_cy

def generate_ashp_gshp_split(split_hp_gshp_ashp):
    """Assing split for each fueltype of heat pump technologies,
    i.e. the share of GSHP of all heat pumps

    Arguments
    ----------
    split_factor : float
        Fraction of ASHP to GSHP

    Returns
    --------
    installed_heat_pump_by : dict
        Ditionary with split of heat pumps for every fueltype

    Example
    ------
    split_hp_ashp_gshp = 0.2 means that 80% are GSHP and 20% ASHP
    """
    gshp_fraction = split_hp_gshp_ashp
    ashp_fraction = 1 - split_hp_gshp_ashp

    installed_heat_pump_by = {
        'hydrogen': {
            'heat_pump_ASHP_hydro': ashp_fraction,
            'heat_pump_GSHP_hydro': gshp_fraction
            },
        'electricity': {
            'heat_pump_ASHP_electricity': ashp_fraction,
            'heat_pump_GSHP_electricity': gshp_fraction
            }
    }

    return installed_heat_pump_by
