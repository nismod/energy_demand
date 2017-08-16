"""Dummy technologies
"""

def insert_dummy_technologies(technologies, tech_p_by, all_specified_tech_enduse_by, fuel_enduse_tech_p_by):
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

    dummy_techs : dict
    TODO
    """
    for end_use in tech_p_by:
        for fuel_type in tech_p_by[end_use]:

            if tech_p_by[end_use][fuel_type] == {}:
                #installed_tech = True
                #pass
            #else:
                #installed_tech = False

            #if not installed_tech:
                #dummpy_tech = "dummy__{}__{}__{}__tech".format(end_use, fuel_type, installed_tech)
                all_specified_tech_enduse_by[end_use].append("dummy_tech")

                # Assign total fuel demand to dummy technology
                tech_p_by[end_use][fuel_type] = {"dummy_tech": 1.0}

                # Insert dummy tech
                technologies['dummy_tech'] = {}

    return tech_p_by, all_specified_tech_enduse_by, technologies

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
                #if tech[:5] == 'dummy':
                if tech == 'dummy_tech':
                    dummy_enduses.add(enduse)
                    continue

    return list(dummy_enduses)
