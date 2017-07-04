"""Functions related to technologies
"""

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
            fueltype_in_string = fueltype_str
            break

    return fueltype_in_string

def get_tech_type(tech_name, assumptions, enduse=''):
    """Get technology type of technology
    Either a technology is a hybrid technology, a heat pump,
    a constant heating technology or a regular technolgy
    Parameters
    ----------
    assumptions : dict
        All technology lists are defined in assumptions
    Returns
    ------
    tech_type : string
        Technology type
    """
    # If all technologies for enduse
    if enduse == 'rs_water_heating':
        tech_type = 'water_heating'
    else:
        if tech_name in assumptions['list_tech_heating_hybrid']:
            tech_type = 'hybrid_tech'
        elif tech_name in assumptions['list_tech_heating_temp_dep']:
            tech_type = 'heat_pump'
        elif tech_name in assumptions['list_tech_heating_const']:
            tech_type = 'boiler_heating_tech'
        elif tech_name in assumptions['list_tech_cooling_temp_dep']:
            tech_type = 'cooling_tech'
        elif tech_name in assumptions['list_tech_cooling_const']:
            tech_type = 'cooling_tech_temp_dependent'
        elif tech_name in assumptions['list_tech_rs_lighting']:
            tech_type = 'lighting_technology'
        #elif tech_name in assumptions['list_water_heating']:
        #    tech_type = 'water_heating'
        else:
            tech_type = 'regular_tech'

    return tech_type

def generate_heat_pump_from_split(data, temp_dependent_tech_list, technologies, heat_pump_assump):
    """Delete all heat_pump from tech dict and define averaged new heat pump
    technologies 'av_heat_pump_fueltype' with efficiency depending on installed ratio

    Parameters
    ----------
    temp_dependent_tech_list : list
        List to store temperature dependent technologies (e.g. heat-pumps)
    technologies : dict
        Technologies
    heat_pump_assump : dict
        The split of the ASHP and GSHP is provided

    Returns
    -------
    technologies : dict
        Technologies with added averaged heat pump technologies for every fueltype

    temp_dependent_tech_list : list
        List with added temperature dependent technologies

    Info
    ----
    # Assumptions:
    - Market Entry of different technologies must be the same year!
      (the lowest is selected if different years)
    - diff method is linear
    """
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
        name_av_hp = "{}_heat_pumps".format(str(get_fueltype_str(data['lu_fueltype'], fueltype)))
        print("Create new averaged heat pump technology: " + str(name_av_hp))

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

    # Remove all heat pumps from tech dict
    for fueltype in heat_pump_assump:
        for heat_pump_type in heat_pump_assump[fueltype]:
            del technologies[heat_pump_type]

    return technologies, temp_dependent_tech_list
