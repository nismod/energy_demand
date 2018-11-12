"""Functions related to technologies
"""
import logging
import numpy as np
from energy_demand.technologies import diffusion_technologies as diffusion
from energy_demand.read_write import read_data
from energy_demand.basic import lookup_tables

def test_if_tech_defined(enduse_fueltypes_techs):
    """Test if a technology has been configured,
    i.e. a fuel share has been assgined to one of the
    fueltpyes in `fuel_shares`.

    Arguments
    ---------
    enduse_fueltypes_techs : dict
        Configured technologies and fuel shares of an enduse

    Returns
    -------
    c_tech_defined : bool
        Criteria whether technologies have been configured
        for an enduse or not
    """
    c_tech_defined = False

    for fueltype in enduse_fueltypes_techs:
        if enduse_fueltypes_techs[fueltype] == {}:
            pass
        else:
            c_tech_defined = True
            break

    return c_tech_defined

def insert_placholder_techs(
        technologies,
        tech_p_by,
        specified_tech_enduse_by
    ):
    """If no technology is defined for a fueltype in an enduse add
    a dumppy technology. This is necessary because the model needs
    a technology for every fueltype in an enduse.

    Arguments
    ----------
    technologies : dict
        Technologies
    tech_p_by : dict
        Fuel assignement of technologies in base year
    specified_tech_enduse_by : dict
        Technologies per enduse

    Returns
    -------
    tech_p_by : dict
        Fuel assignement of technologies in base year
    specified_tech_enduse_by : dict
        Technologies per enduse
    technologies : dict
        Technologies
    """
    out_tech_p_by = {}
    for enduse, enduse_fueltypes_techs in tech_p_by.items():
        out_tech_p_by[enduse] = {}
        if list(enduse_fueltypes_techs.keys())[0] != 0:

            for sector in enduse_fueltypes_techs:
                out_tech_p_by[enduse][sector] = {}

                # Test if a technology is defined in any fueltype
                c_tech_defined = test_if_tech_defined(enduse_fueltypes_techs[sector])

                if not c_tech_defined:
                    for fueltype in enduse_fueltypes_techs[sector]:
                        if enduse_fueltypes_techs[sector][fueltype] == {}:

                            # Assign total fuel demand to dummy technology
                            out_tech_p_by[enduse][sector][fueltype] = {"placeholder_tech": 1.0}

                    specified_tech_enduse_by[enduse][sector].append("placeholder_tech")
                else:
                    out_tech_p_by[enduse][sector] = enduse_fueltypes_techs[sector]
        else:
            # If no sector is defined, add a dummy None setor
            dummy_sector = None

            out_tech_p_by[enduse][dummy_sector] = {}
            c_tech_defined = test_if_tech_defined(enduse_fueltypes_techs)
            if not c_tech_defined:
                for fueltype in enduse_fueltypes_techs:
                    if enduse_fueltypes_techs[fueltype] == {}:
                        out_tech_p_by[enduse][dummy_sector][fueltype] = {"placeholder_tech": 1.0}

                specified_tech_enduse_by[enduse][dummy_sector].append("placeholder_tech")
            else:
                out_tech_p_by[enduse][dummy_sector] = enduse_fueltypes_techs

    # Insert placeholder technology
    technologies['placeholder_tech'] = read_data.TechnologyData(
        eff_by=1,
        eff_ey=1,
        year_eff_ey=2100,
        eff_achieved=1,
        diff_method='linear',
        tech_type='placeholder_tech')

    return out_tech_p_by, specified_tech_enduse_by, technologies

def calc_hp_eff(
        temp_yh,
        efficiency_intersect,
        t_base_heating
    ):
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
    Because the efficieny of heat pumps is temperature dependent,
    the efficiency needs to be calculated based on slope and
    intersect which is provided as input for temp difference 10
    and treated as efficiency
    """
    efficiency_hp = m_slope * temp_diff + (efficiency_intersect - (m_slope * h_diff))

    # Calculate average efficiency over whole year
    efficiency_hp_mean = np.average(efficiency_hp)

    return efficiency_hp_mean

def get_fueltype_str(fueltype_lu, fueltype_nr):
    """Read from dict the fueltype string based on fueltype KeyError

    Arguments
    ---------
    fueltype : dict
        Fueltype lookup dictionary
    fueltype_nr : int
        Key which is to be found in lookup dict

    Returns
    -------
    fueltype_in_string : str
        Fueltype string
    """
    fueltype_lu = lookup_tables.basic_lookups()['fueltypes']

    for fueltype_str in fueltype_lu:
        if fueltype_lu[fueltype_str] == fueltype_nr:
            return fueltype_str

def get_fueltype_int(fueltype_str):
    """Read from dict the fueltype string based on fueltype KeyError

    Arguments
    ---------
    fueltype_str : int
        Key which is to be found in lookup dict

    Returns
    -------
    fueltype_in_string : str
        Fueltype string
    """
    fueltype_lu = lookup_tables.basic_lookups()['fueltypes']

    if not fueltype_str:
        return None
    else:
        return fueltype_lu[fueltype_str]

def calc_av_heat_pump_eff_ey(technologies, heat_pump_assump):
    """Calculate end year average efficiency of
    heat pumps depending on split of heat pumps

    Arguments
    ---------
    technologies : dict
        Technologies
    heat_pump_assump : dict
        Ditionary with split of heat pumps for every fueltype

    Return
    ------
    technologies : dict
        Updated technologies
    """
    for fueltype, heat_pump_split in heat_pump_assump.items():
        av_eff_hps_ey = 0

        for heat_pump_type, share_heat_pump in heat_pump_split.items():

            # End year efficiency of heat pump
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

        # Add technology to temperature dependent technology list
        temp_dependent_tech_list.append(name_av_hp)

        # Add new averaged technology
        technologies[name_av_hp] = read_data.TechnologyData(
            fueltype=fueltype,
            eff_by=av_eff_hps_by,
            eff_ey=av_eff_hps_ey,
            year_eff_ey=av_year_eff_ey,
            eff_achieved=eff_achieved_av,
            diff_method='linear',
            market_entry=market_entry_lowest,
            tech_type='heating_non_const',
            tech_max_share=tech_max_share)

        heat_pumps.append(name_av_hp)

    return technologies, temp_dependent_tech_list, heat_pumps

def calc_eff_cy(
        base_yr,
        curr_yr,
        eff_by,
        eff_ey,
        yr_until_changed,
        f_eff_achieved,
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
    f_eff_achieved : dict
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

    NICETOHAVE: Generate two types of sigmoid (convex & concav)
    """
    if diff_method == 'linear':
        # Theoretical maximum efficiency potential (linear improvement)
        theor_max_eff = diffusion.linear_diff(
            base_yr,
            curr_yr,
            eff_by,
            eff_ey,
            yr_until_changed)

        # Differencey in efficiency change
        max_eff_gain = theor_max_eff - eff_by

    elif diff_method == 'sigmoid':
        # Theoretical maximum efficiency potential (sigmoid improvement)
        diff_cy = diffusion.sigmoid_diffusion(
            base_yr,
            curr_yr,
            yr_until_changed,
            sig_midpoint=0,
            sig_steepness=1)

        # Differencey in efficiency change
        max_eff_gain = diff_cy * (eff_ey - eff_by)
    else:
        if not diff_method:
            return None
        else:
            logging.exception("Not correct diffusion assigned %s", diff_method)

    # Consider actual achieved efficiency
    actual_eff_gain = max_eff_gain * f_eff_achieved

    # Actual efficiency potential
    eff_cy = eff_by + actual_eff_gain

    return eff_cy

def generate_ashp_gshp_split(gshp_fraction):
    """Assing split for each fueltype of heat pump technologies,
    i.e. the share of GSHP of all heat pumps

    Arguments
    ----------
    gshp_fraction : float
        Fraction of GSHP (GSHP + ASHP = 100%)

    Returns
    --------
    installed_heat_pump_by : dict
        Ditionary with split of heat pumps for every fueltype
    """
    ashp_fraction = 1 - gshp_fraction

    installed_heat_pump_by = {
        'hydrogen': {
            'heat_pump_ASHP_hydrogen': ashp_fraction,
            'heat_pump_GSHP_hydrogen': gshp_fraction},
        'electricity': {
            'heat_pump_ASHP_electricity': ashp_fraction,
            'heat_pump_GSHP_electricity': gshp_fraction}
    }

    return installed_heat_pump_by
