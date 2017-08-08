"""Dummy technologies
"""

def insert_dummy_technologies(tech_p_by, all_specified_tech_enduse_by, fuel_enduse_tech_p_by):
    """Define dummy technologies

    Where no specific technologies are assigned for an enduse
    and a fueltype, dummy technologies are generated. This is
    necessary because the model needs a technology for every
    fueltype in an enduse. Technologies are however defined
    with no efficiency changes, so that the energy demand
    for an enduse per fueltype can be treated not related
    to technologies (e.g. definieng definin overall
    eficiency change)

    Parameters
    ----------
    tech_p_by : dict
        Fuel assignement of technologies in base year
    all_specified_tech_enduse_by : dict
        Technologies per enduse

    Returns
    -------
    tech_p_by : dict

    all_specified_tech_enduse_by : dict

    dummpy_techs : dict
    TODO
    """
    dummpy_techs = []

    for end_use in tech_p_by:
        for fuel_type in tech_p_by[end_use]:

            installed_tech = False
            if tech_p_by[end_use][fuel_type] != {}:
                installed_tech = True

            if not installed_tech:
                dummpy_tech = "dummy__{}__{}__{}__tech".format(end_use, fuel_type, installed_tech)
                dummpy_techs.append(dummpy_tech)
                all_specified_tech_enduse_by[end_use].append(dummpy_tech)

                # Assign total fuel demand to dummy technology
                tech_p_by[end_use][fuel_type] = {dummpy_tech: 1.0}

    return tech_p_by, all_specified_tech_enduse_by, dummpy_techs

def define_dummy_technologies(dummy_techs, technologies):
    """Define generated dummy technologies and add to other technologies

    Parameters
    ----------
    dummy_techs : list
        Dummy technologies
    technologies : dict
        Technologies

    Returns
    -------
    technologies : dict
        Technologies with added dummy technologies

    Info
    ----
    All dummy technologies have efficiencies of one in base and end year,
    a sigmoid diffusion and a market entry of 2015
    """

    for dummy_tech in dummy_techs:
        technologies[dummy_tech] = {
            'fuel_type': int(dummy_tech.split("__")[2]),
            'eff_by': 1.0,
            'eff_ey': 1.0,
            'eff_achieved': 1.0,
            'diff_method': 'sigmoid',
            'market_entry': 2015
        }

    return technologies

def get_enduses_with_dummy_tech(enduse_tech_p_by):
    """Find all enduses with defined dummy technologies

    Parameters
    ----------
    enduse_tech_p_by : dict
        Fuel share definition of technologies

    Return
    ------
    dummy_enduses : list
        List with all endueses with dummy technologies
    """
    dummy_enduses = set([])
    for enduse in enduse_tech_p_by:
        for fueltype in enduse_tech_p_by[enduse]:
            for tech in enduse_tech_p_by[enduse][fueltype]:
                if tech[:5] == 'dummy':
                    dummy_enduses.add(enduse)
                    continue

    return list(dummy_enduses)
