"""Function related to service or fuel switch
"""
import logging
from collections import defaultdict
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_data
from energy_demand.basic import basic_functions

def get_switch_criteria(
        enduse,
        sector,
        crit_switch_happening,
        base_yr=False,
        curr_yr=False
    ):
    """Test if switch is happending
    """
    if base_yr == curr_yr and (base_yr != False or curr_yr != False):
        crit_switch_service = False
    else:
        if enduse in crit_switch_happening:
            if not sector:
                crit_switch_service = True
            else:
                if sector in crit_switch_happening[enduse]:
                    crit_switch_service = True
                else:
                    crit_switch_service = False
        else:
            crit_switch_service = False

    return crit_switch_service

def sum_fuel_across_sectors(fuels):
    """Sum fuel across sectors of an enduse if multiple sectors.
    Otherwise return unchanged `fuels`

    Arguments
    ---------
    fuels : dict or np.array
        Fuels of an enduse either for sectors or already aggregated

    Returns
    -------
    sum_array : np.array
        Sum of fuels of all sectors
    """
    if isinstance(fuels, dict):
        sum_array = sum(fuels.values())
        return sum_array
    else:
        return fuels

def get_share_s_tech_ey(
        service_switches,
        specified_tech_enduse_by,
        spatial_explicit_diffusion
    ):
    """Get fraction of service for each technology
    defined in a switch for the future year

    Arguments
    ---------
    service_switches : list
        Service switches
    specified_tech_enduse_by : list
        Technologies defined per enduse for base year

    Return
    ------
    enduse_tech_ey_p : dict
        Enduse, share per technology in ey
    """
    enduse_tech_ey_p = defaultdict(dict)

    if spatial_explicit_diffusion:

        for reg, switches in service_switches.items():

            enduses = []
            for switch in switches:
                if switch.enduse not in enduses:
                    enduses.append(switch.enduse)
                    enduse_tech_ey_p[switch.enduse][reg] = {}

            # Iterate all endusese and assign all lines
            for enduse in enduses:
                for switch in switches:
                    if switch.enduse == enduse:
                        enduse_tech_ey_p[enduse][reg][switch.technology_install] = switch.service_share_ey

            # Add all other enduses for which no switch is defined
            for enduse in specified_tech_enduse_by:
                if enduse not in enduse_tech_ey_p:
                    enduse_tech_ey_p[enduse] = {}
                    for i in service_switches.keys(): #Regions
                        enduse_tech_ey_p[enduse][i] = {}
    else:
        enduses = []
        for switch in service_switches:
            if switch.enduse not in enduses:
                enduses.append(switch.enduse)
                enduse_tech_ey_p[switch.enduse] = {}

        # Iterate all endusese and assign all lines
        for enduse in enduses:
            for switch in service_switches:
                if switch.enduse == enduse:
                    enduse_tech_ey_p[enduse][switch.technology_install] = switch.service_share_ey

        # Add all other enduses for which no switch is defined
        for enduse in specified_tech_enduse_by:
            if enduse not in enduse_tech_ey_p:
                enduse_tech_ey_p[enduse] = {}

    return dict(enduse_tech_ey_p)

def create_switches_from_s_shares(
        enduse,
        s_tech_by_p,
        switch_technologies,
        specified_tech_enduse_by,
        enduse_switches,
        s_tot_defined,
        sector,
        switch_yr
    ):
    """
    Create swiches from service shares.
    If not 100% of the service share is defined,
    the switches get defined which proportionally
    decrease service of all not switched technologies

    Arguments
    ----------
    enduse : str
        Enduse
    s_tech_by_p :
        Service share per technology in base year
    switch_technologies : list
        Technologies involved in switch
    specified_tech_enduse_by : list
        Technologies per enduse
    enduse_switches : list
        Switches
    s_tot_defined : float
        Service defined
    sector : str
        Sector
    switch_yr : int
        Year

    Returns
    -------
    service_switches_out : dict
        Service switches
    """
    service_switches_out = []

    # Calculate relative by proportion of not assigned technologies in base year
    tech_not_assigned_by_p = {}
    for tech in specified_tech_enduse_by[enduse]:
        if tech not in switch_technologies:
            tech_not_assigned_by_p[tech] = s_tech_by_p[enduse][tech]

    # Normalise: convert to percentage
    tot_share_not_assigned = sum(tech_not_assigned_by_p.values())
    for tech, share_by in tech_not_assigned_by_p.items():
        tech_not_assigned_by_p[tech] = share_by / tot_share_not_assigned

    # Get all defined technologies in base year
    for tech in specified_tech_enduse_by[enduse]:

        if tech not in switch_technologies:

            if s_tot_defined == 1.0:
                switch_new = read_data.ServiceSwitch(
                    enduse=enduse,
                    sector=sector,
                    technology_install=tech,
                    service_share_ey=0,
                    switch_yr=switch_yr)
            else:
                # Calculate not defined share in switches
                s_not_assigned = 1 - s_tot_defined

                # Reduce share proportionally
                tech_ey_p = tech_not_assigned_by_p[tech] * s_not_assigned

                switch_new = read_data.ServiceSwitch(
                    enduse=enduse,
                    sector=sector,
                    technology_install=tech,
                    service_share_ey=tech_ey_p,
                    switch_yr=switch_yr)

            service_switches_out.append(switch_new)
        else:
            # If assigned copy to final switches
            for switch_new in enduse_switches:
                if switch_new.technology_install == tech:
                    service_switches_out.append(switch_new)

    return service_switches_out

def autocomplete_switches(
        service_switches,
        specified_tech_enduse_by,
        s_tech_by_p,
        sector=False,
        spatial_explicit_diffusion=False,
        regions=False,
        f_diffusion=False,
        techs_affected_spatial_f=False,
        service_switches_from_capacity=[]
    ):
    """Add not defined technologies in switches
    and set correct future service share.

    If the defined service switches do not sum up to 100% service,
    the remaining service is distriputed proportionally
    to all remaining technologies.

    Arguments
    ---------
    service_switches : dict
        Defined service switches
    specified_tech_enduse_by : dict
        Specified technologies of an enduse
    s_tech_by_p : dict
        Share of service of technology in base year

    Returns
    -------
    reg_share_s_tech_ey_p : dict
        Shares per technology in end year
    service_switches_out : list
        Added services switches which now in total sum up to 100%
    """
    # Get all enduses defined in switches
    enduses = set([])
    for switch in service_switches:
        enduses.add(switch.enduse)
    enduses = list(enduses)

    if spatial_explicit_diffusion:

        service_switches_out = {}

        for region in regions:
            service_switches_out[region] = []

            # Append regional other capacity switches
            service_switches_out[region].extend(
                service_switches_from_capacity[region])

            for enduse in enduses:

                # Get all switches of this enduse
                enduse_switches = []
                s_tot_defined = 0
                switch_technologies = []

                for switch in service_switches:
                    if switch.enduse == enduse:

                        # Global share of technology diffusion
                        s_share_ey_global = switch.service_share_ey

                        # If technology is affected by spatial exlicit diffusion
                        if switch.technology_install in techs_affected_spatial_f:

                            # Regional diffusion calculation
                            s_share_ey_regional = s_share_ey_global * f_diffusion[enduse][region]

                            # if larger than max crit, set to 1 TODO
                            max_crit = 1
                            if s_share_ey_regional > max_crit:
                                s_share_ey_regional = max_crit

                            if s_tot_defined + s_share_ey_regional > 1.0:

                                #TODO IMPROVE THAT ROUNDING 1 .. make nicer
                                if round(s_tot_defined + s_share_ey_regional) > 1:
                                    logging.warning("ERROR: MORE THAN ONE TECHNOLOG SWICHED WITH LARGER SHARE: ")
                                    logging.warning(" {}  {} {}".format(s_tot_defined, s_share_ey_regional, s_tot_defined + s_share_ey_regional))
                                    prnt(".")
                                else:
                                    s_share_ey_regional = max_crit - s_share_ey_regional
                            #logging.debug("A %s  %s", region, switch.technology_install)
                            #logging.debug(s_share_ey_global)
                            #logging.debug(s_share_ey_regional)
                        else:
                            s_share_ey_regional = switch.service_share_ey

                        switch_new = read_data.ServiceSwitch(
                            enduse=switch.enduse,
                            sector=switch.sector,
                            technology_install=switch.technology_install,
                            service_share_ey=s_share_ey_regional,
                            switch_yr=switch.switch_yr)
      
                        s_tot_defined += s_share_ey_regional
                        switch_technologies.append(switch.technology_install)
                        enduse_switches.append(switch_new)
                        switch_yr = switch.switch_yr

                        # Create switch TODO TODO SHIFTED ONE TAB CHECK 03.05.2018
                        switches_new = create_switches_from_s_shares(
                            enduse=enduse,
                            s_tech_by_p=s_tech_by_p,
                            switch_technologies=switch_technologies,
                            specified_tech_enduse_by=specified_tech_enduse_by,
                            enduse_switches=enduse_switches,
                            s_tot_defined=s_tot_defined,
                            sector=sector,
                            switch_yr=switch_yr)

                        service_switches_out[region].extend(switches_new)
    else:
        service_switches_out = []

        for enduse in enduses:

            # Get all switches of this enduse
            enduse_switches = []
            s_tot_defined = 0
            switch_technologies = []

            for switch in service_switches:
                if switch.enduse == enduse:
                    s_tot_defined += switch.service_share_ey
                    switch_technologies.append(switch.technology_install)
                    enduse_switches.append(switch)
                    switch_yr = switch.switch_yr

            # Calculate relative by proportion of not assigned technologies
            switches_new = create_switches_from_s_shares(
                enduse=enduse,
                s_tech_by_p=s_tech_by_p,
                switch_technologies=switch_technologies,
                specified_tech_enduse_by=specified_tech_enduse_by,
                enduse_switches=enduse_switches,
                s_tot_defined=s_tot_defined,
                sector=sector,
                switch_yr=switch_yr)

            service_switches_out.extend(switches_new)
            service_switches_out.extend(service_switches_from_capacity)


    # Calculate fraction of service for each technology
    reg_share_s_tech_ey_p = get_share_s_tech_ey(
        service_switches_out,
        specified_tech_enduse_by,
        spatial_explicit_diffusion)

    return reg_share_s_tech_ey_p, service_switches_out

def capacity_switch(
        capacity_switches,
        technologies,
        other_enduse_mode_info,
        fuels,
        fuel_shares_enduse_by,
        base_yr
    ):
    """Create service switches based on assumption on
    changes in installed fuel capacity (`capacity switches`).
    Service switch are calculated based on the assumed
    capacity installation (in absolute GW) of technologies.
    Assumptions on capacities are defined in the
    CSV file `xx_capacity_switch.csv`

    Note
    -----
    With the information about the installed capacity
    only the change in percentage in end year gets calulated.
    This means that there is not absolute change in demand (
        e.g. you cant add additional demand of an existing technology
        --> It is only a switch)
    Arguments
    ---------
    capacity_switches : list
        Capacity switches
    technologies : dict
        Technologies
    other_enduse_mode_info : dict
        Generic sigmoid diffusion information
    fuels : dict
        Fuels
    fuel_shares_enduse_by : dict
        Fuel technology shares in base year
    base_yr : int
        Base year

    Returns
    -------
    service_switches : dict
        Updated service switches containing converted
        capacity switches to service switches

    Warning
    -------
    Capacity switches overwrite existing service switches
    """
    # Get all affected enduses of capacity switches
    switch_enduses = set([])
    for switch in capacity_switches:
        switch_enduses.add(switch.enduse)
    switch_enduses = list(switch_enduses)

    if switch_enduses == []:
        service_switches = [] # not capacity switch defined
    else:
        # List to store service switches
        service_switches = []

        for enduse in switch_enduses:

            # Get all capacity switches related to this enduse
            enduse_capacity_switches = []
            for switch in capacity_switches:
                if switch.enduse == enduse:
                    enduse_capacity_switches.append(switch)

            # Iterate capacity switches
            for switch in enduse_capacity_switches:

                if switch.sector is None:

                    # Check depth of dict
                    depth_dict = basic_functions.dict_depth(
                        fuel_shares_enduse_by)

                    if depth_dict == 3:
                        # Fuel share are only given per enduses
                        fuel_shares = fuel_shares_enduse_by[enduse]
                        fuel_to_use = fuels[enduse]
                        sector = switch.sector
                    elif depth_dict == 4:
                        # Fuel shares are provide per enduse and sectors
                        any_sector = list(fuel_shares_enduse_by[enduse].keys())[0]
                        fuel_shares = fuel_shares_enduse_by[enduse][any_sector]
                        fuel_to_use = sum_fuel_across_sectors(fuels[enduse])
                        sector = None
                else:
                    # Get fuel share specifically for the enduse and sector
                    fuel_shares = fuel_shares_enduse_by[enduse][switch.sector]
                    fuel_to_use = fuels[enduse]
                    sector = switch.sector

                # Calculate service switches
                enduse_service_switches = create_service_switch(
                    enduse,
                    sector,
                    switch,
                    enduse_capacity_switches,
                    technologies,
                    other_enduse_mode_info,
                    fuel_shares,
                    base_yr,
                    fuel_to_use)

                # Add service switches
                service_switches += enduse_service_switches

    return service_switches

def create_service_switch(
        enduse,
        sector,
        switch,
        enduse_capacity_switches,
        technologies,
        other_enduse_mode_info,
        fuel_shares_enduse_by,
        base_yr,
        fuel_enduse_y
    ):
    """Generate service switch based on capacity assumptions

    Arguments
    ---------
    enduse : dict
        Enduse
    switch : obj
        Capacity switch
    enduse_capacity_switches : list
        All capacity switches of an enduse (see warning)
    technologies : dict
        Technologies
    other_enduse_mode_info : dict
        OTher diffusion information
    fuel_shares_enduse_by : dict
        Fuel shares per enduse for base year
    base_yr : int
        base year
    fuel_enduse_y : dict
        Fuels

    Returns
    ------
    service_switches : dict
        Service switches

    Major steps
    -------
        1.  Convert fuel per technology to service in ey
        2.  Convert installed capacity to service of ey and add service
        3.  Calculate percentage of service for ey
        4.  Write out as service switch

    Warning
    -------
        -   The year until the switch happens must be the same for all switches
    """
    # ------------
    # Calculate year until switch happens
    # -----------
    for switch in enduse_capacity_switches:
        switch_yr = switch.switch_yr
        continue

    # ---------------------------------------------
    # Calculate service per technology for end year
    # ---------------------------------------------
    service_enduse_tech = {}

    for fueltype, tech_fuel_shares in fuel_shares_enduse_by.items():
        for tech, fuel_share_by in tech_fuel_shares.items():

            # Efficiency of year when capacity is fully installed
            eff_ey = tech_related.calc_eff_cy(
                base_yr,
                switch.switch_yr,
                technologies[tech].eff_by,
                technologies[tech].eff_ey,
                technologies[tech].year_eff_ey,
                other_enduse_mode_info,
                technologies[tech].eff_achieved,
                technologies[tech].diff_method)

            # Convert to service (fuel * fuelshare * eff)
            s_tech_ey_y = fuel_enduse_y[fueltype] * fuel_share_by * eff_ey
            service_enduse_tech[tech] = s_tech_ey_y

    # -------------------------------------------
    # Calculate service of installed capacity of increased
    # (installed) technologies
    # -------------------------------------------
    for switch in enduse_capacity_switches:

        eff_ey = tech_related.calc_eff_cy(
            base_yr,
            switch.switch_yr,
            technologies[switch.technology_install].eff_by,
            technologies[switch.technology_install].eff_ey,
            technologies[switch.technology_install].year_eff_ey,
            other_enduse_mode_info,
            technologies[switch.technology_install].eff_achieved,
            technologies[switch.technology_install].diff_method)

        # Convert installed capacity to service
        installed_capacity_ey = switch.installed_capacity * eff_ey

        # Add capacity
        service_enduse_tech[switch.technology_install] += installed_capacity_ey

    # -------------------------------------------
    # Calculate service in % per enduse
    # -------------------------------------------
    tot_s = sum(service_enduse_tech.values())
    for tech, service_tech in service_enduse_tech.items():
        service_enduse_tech[tech] = service_tech / tot_s

    # -------------------------------------------
    # Add to switch of technology_install
    # -------------------------------------------
    service_switches_enduse = []
    for tech, s_tech_p in service_enduse_tech.items():

        service_switch = read_data.ServiceSwitch(
            enduse=enduse,
            sector=sector,
            technology_install=tech,
            service_share_ey=s_tech_p,
            switch_yr=switch_yr)

        service_switches_enduse.append(service_switch)

    return service_switches_enduse

def get_fuel_switches_enduse(switches, enduse, regional_specific=False):
    """Get all fuel switches of a specific enduse

    Arguments
    ----------
    switches : list
        Switches
    enduse : str
        Enduse

    Returns
    -------
    enduse_switches : list
        All switches of a specific enduse
    """
    if regional_specific:
        enduse_switches = {}
        for reg in switches:
            enduse_switches[reg] = []
            for fuel_switch in switches[reg]:
                if fuel_switch.enduse == enduse:
                    enduse_switches[reg].append(fuel_switch)
    else:
        enduse_switches = []
        for fuel_switch in switches:
            if fuel_switch.enduse == enduse:
                enduse_switches.append(fuel_switch)

    return enduse_switches

def switches_to_dict(service_switches, regional_specific):
    """Write switch to dict, i.e. providing service fraction
    of technology as dict: {tech: service_ey_p}

    Arguments
    ---------
    service_switches : dict
        Service switches
    regional_specific : crit
        Regional speciffic diffusion modelling criteria

    Returns
    -------
    s_tech_by_p : dict
        Service tech after service switch

    service_switches : dict
        Reg, fuel_swtiches
    """
    s_tech_by_p = defaultdict(dict)

    if regional_specific:
        for reg, reg_switches in service_switches.items():
            for switch in reg_switches:
                s_tech_by_p[reg][switch.technology_install] = switch.service_share_ey

            assert round(sum(s_tech_by_p[reg].values()), 3) == 1
    else:
        for switch in service_switches:
            s_tech_by_p[switch.technology_install] = switch.service_share_ey

        assert round(sum(s_tech_by_p.values()), 3) == 1

    return dict(s_tech_by_p)
