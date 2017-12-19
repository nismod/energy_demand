"""Function related to service or fuel switch
"""
from collections import defaultdict
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_data

def get_share_service_tech_ey(service_switches, specified_tech_enduse_by):
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
    enduse_tech_ey_p = {}

    all_enduses = []
    for switch in service_switches:
        enduse = switch.enduse
        if enduse not in all_enduses:
            all_enduses.append(enduse)
            enduse_tech_ey_p[enduse] = {}

    # Iterate all endusese and assign all lines
    for enduse in all_enduses:
        for switch in service_switches:
            if switch.enduse == enduse:
                enduse_tech_ey_p[enduse][switch.technology_install] = switch.service_share_ey

    # Add all other enduses for which no switch is defined
    for enduse in specified_tech_enduse_by:
        if enduse not in enduse_tech_ey_p:
            enduse_tech_ey_p[enduse] = {}

    return enduse_tech_ey_p

def autocomplete_switches(service_switches, specified_tech_enduse_by, service_tech_by_p):
    """Helper function to add not defined technologies in switch
    and set correct future year service share. If the defined
    service switches do not sum up to 100% service,
    the remaining service is distriputed proportionally
    to all remaining technologies

    Argument
    --------
    service_switches : dict
        Defined service switches
    specified_tech_enduse_by : dict
        Specified technologies of an enduse
    service_tech_by_p : dict
        Share of service of technology in base year

    Returns
    -------
    rs_service_switches_new : dict
        Added services switches which now in total sum up to 100%
    """
    service_switches_out = []

    # ---------------------------------
    # Get all enduses defined in switch
    # ---------------------------------
    all_enduses_with_switches = set([])
    for switch in service_switches:
        all_enduses_with_switches.add(switch.enduse)
    all_enduses_with_switches = list(all_enduses_with_switches)

    for enduse in all_enduses_with_switches:

        # Get all switches of this enduse
        switches_enduse = []
        assigned_service = 0
        assigned_technologies = []

        for switch in service_switches:
            if switch.enduse == enduse:
                assigned_service += switch.service_share_ey
                assigned_technologies.append(switch.technology_install)
                switches_enduse.append(switch)
                switch_yr = switch.switch_yr

        # Calculate relative by proportion of not assigned tchnologies
        tech_not_assigned_by_p = {}

        for tech in specified_tech_enduse_by[enduse]:
            if tech not in assigned_technologies:
                tech_not_assigned_by_p[tech] = service_tech_by_p[enduse][tech]

        # convert to percentage
        tot_share_not_assigned = sum(tech_not_assigned_by_p.values())
        for tech, share_by in tech_not_assigned_by_p.items():
            tech_not_assigned_by_p[tech] = share_by / tot_share_not_assigned

        # Calculate not defined share in switches
        not_assigned_service = 1 - assigned_service

        # Get all defined technologies in base year
        for tech in specified_tech_enduse_by[enduse]:

            if tech not in assigned_technologies:

                if assigned_service == 1.0:
                    switch_new = read_data.ServiceSwitch(
                        enduse=enduse,
                        technology_install=tech,
                        service_share_ey=0,
                        switch_yr=switch_yr)
                    service_switches_out.append(switch_new)
                else:
                    # Reduce share proportionally
                    tech_ey_p = tech_not_assigned_by_p[tech] * not_assigned_service

                    switch_new = read_data.ServiceSwitch(
                        enduse=enduse,
                        technology_install=tech,
                        service_share_ey=tech_ey_p,
                        switch_yr=switch_yr)
                    service_switches_out.append(switch_new)
            else:
                # If assigned copy to final switches
                for switch in switches_enduse:
                    if switch.technology_install == tech:
                        service_switches_out.append(switch)

    return service_switches_out

def get_service_rel_tech_decr_by(tech_decrease_service, service_tech_by_p):
    """Iterate technologies with future reduced service
    demand (replaced tech) and calculate their relative
    share of service in the base year

    Arguments
    ----------
    tech_decrease_service : dict
        Technologies with decreased service
    service_tech_by_p : dict
        Share of service of technologies in by

    Returns
    -------
    rel_share_service_tech_decr_by : dict
        Relative share of service of replaced technologies
    """
    rel_share_service_tech_decr_by = {}

    # Summed share of all diminishing technologies
    sum_service_tech_decrease_p = sum(
        [service_tech_by_p[tech] for tech in tech_decrease_service])

    # Relative of each diminishing tech (convert abs in dict to rel in dict)
    for tech in tech_decrease_service:
        try:
            rel_share_service_tech_decr_by[tech] = service_tech_by_p[tech] / float(sum_service_tech_decrease_p)
        except ZeroDivisionError:
            rel_share_service_tech_decr_by[tech] = 0

    return rel_share_service_tech_decr_by

def capacity_installations(
        service_switches,
        capacity_switches,
        technologies,
        other_enduse_mode_info,
        fuels,
        fuel_shares_enduse_by,
        base_yr
    ):
    """Create service switch based on assumption on
    changes in installed fuel capacity. Service switch are calculated
    based on the assumed capacity installation (in absolute GW)
    of technologies. Assumptions on capacities
    are defined in the CSV file `assumptions_capacity_installations.csv`

    Arguments
    ---------
    path : dict
        Path
    technologies : dict
        Technologies
    other_enduse_mode_info : dict
        Generic sigmoid diffusion information
    fuels : dict
        Fuels
    fuel_shares_enduse_by : dict
        Fuel technology shares in base year
    base_yr : dict
        Base year

    Returns
    -------
    assumptions : dict
        Dict with updated service switches

    Warning
    -------
    Capacity switches overwrite existing service switches
    """
    # -------------------------------------
    # Assign correct fuel shares and fuels
    # -------------------------------------
    enduses_switch = set([])

    for switch in capacity_switches:
        enduses_switch.add(switch.enduse)
    enduses_switch = list(enduses_switch)

    if enduses_switch == []:
        pass
    else:
        # -------------------------
        # Calculate service switches
        # -------------------------
        service_switches = create_service_switch(
            enduses_switch,
            capacity_switches,
            technologies,
            other_enduse_mode_info,
            fuel_shares_enduse_by,
            base_yr,
            fuels)

    return service_switches

def create_service_switch(
        enduses,
        capacity_switches,
        technologies,
        other_enduse_mode_info,
        fuel_shares_enduse_by,
        base_yr,
        fuels
    ):
    """Generate service switch based on capacity assumptions

    Arguments
    ---------
    enduses : dict
        Enduses
    capacity_switches : list
        List containing all capacity_switches
    assumptions : dict
        Assumptions
    fuels : dict
        Fuels
    base_yr : dict
        base year
    """
    service_switches = []

    for enduse in enduses:
        for capacity_switch in capacity_switches:
            if capacity_switch.enduse == enduse:

                # Convert
                service_switches_enduse = capacity_assumption_to_service(
                    enduse=enduse,
                    capacity_switches=capacity_switches,
                    capacity_switch=capacity_switch,
                    technologies=technologies,
                    fuel_shares_enduse_by=fuel_shares_enduse_by[enduse],
                    fuel_enduse_y=fuels[enduse],
                    base_yr=base_yr,
                    other_enduse_mode_info=other_enduse_mode_info)

                # Add service switch
                service_switches += service_switches_enduse

    return service_switches

def capacity_assumption_to_service(
        enduse,
        capacity_switches,
        capacity_switch,
        technologies,
        fuel_shares_enduse_by,
        fuel_enduse_y,
        base_yr,
        other_enduse_mode_info
    ):
    """Convert capacity assumption to service
    switches

    Arguments
    ---------
    enduse : str
        Enduse
    capacity_switch : dict
        All capacity switches
    technologies : dict
        Technologies
    fuel_shares_enduse_by : dict
        Fuel shares per technology per enduse
    fuel_enduse_y : array
        Fuel per enduse and fueltype
    sim_param : dict
        Simulation parameters
    other_enduse_mode_info : dict
        Sigmoid diffusion information

    Major steps
    ----
    1.  Convert fuel per technology to service in ey
    2.  Convert installed capacity to service of ey and add this
    3.  Calculate percentage of service for ey
    4.  Write out as service switch
    """
    curr_yr = capacity_switch.switch_yr

    # ---------------------------------------------
    # Calculate service per technolgies for end year
    # ---------------------------------------------
    service_enduse_tech = {}

    for fueltype, tech_fuel_shares in fuel_shares_enduse_by.items():
        for tech, fuel_share_by in tech_fuel_shares.items():

            # Efficiency of year when capacity is fully installed
            tech_eff_ey = tech_related.calc_eff_cy(
                base_yr,
                curr_yr,
                technologies[tech].eff_by,
                technologies[tech].eff_ey,
                technologies[tech].year_eff_ey,
                other_enduse_mode_info,
                technologies[tech].eff_achieved,
                technologies[tech].diff_method)

            # Convert to service (fuel * fuelshare * eff) TODO TEST
            service_tech_ey_y = fuel_enduse_y[fueltype] * fuel_share_by * tech_eff_ey
            service_enduse_tech[tech] = service_tech_ey_y

    # -------------------------------------------
    # Calculate service of installed capacity of increased technologies
    # -------------------------------------------
    for switch in capacity_switches: #If technology exists, add service
        if enduse == switch.enduse:
            technology_install = switch.technology_install
            installed_capacity = switch.installed_capacity

            tech_eff_ey = tech_related.calc_eff_cy(
                base_yr,
                curr_yr,
                technologies[technology_install].eff_by,
                technologies[technology_install].eff_ey,
                technologies[technology_install].year_eff_ey,
                other_enduse_mode_info,
                technologies[technology_install].eff_achieved,
                technologies[technology_install].diff_method)

            # Convert installed capacity to service
            installed_capacity_ey = installed_capacity * tech_eff_ey

            # Add cpacity
            service_enduse_tech[technology_install] += installed_capacity_ey

    # -------------------------------------------
    # Calculate service in % per enduse
    # -------------------------------------------
    tot_service = sum(service_enduse_tech.values())
    for tech, service_tech in service_enduse_tech.items():
        service_enduse_tech[tech] = service_tech / tot_service

    # -------------------------------------------
    # Add to switch of technology_install
    # -------------------------------------------
    service_switches_enduse = []
    for tech, service_tech_p in service_enduse_tech.items():

        # WARNING: MUST BE THE SAME YEAR FOR ALL CAPACITY SWITCHES
        for switch in capacity_switches:
            switch_yr = switch.switch_yr
            continue

        service_switch = read_data.ServiceSwitch(
            enduse=enduse,
            technology_install=tech,
            service_share_ey=service_tech_p,
            switch_yr=switch_yr)

        service_switches_enduse.append(service_switch)

    return service_switches_enduse

def get_fuel_switches_enduse(switches, enduse):
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
    service_tech_by_p : dict
        Service tech after service switch

    service_switches : dict
        Reg, fuel_swtiches
    """
    service_tech_by_p = defaultdict(dict)

    if regional_specific:
        for reg, reg_switches in service_switches.items():
            for switch in reg_switches:
                service_tech_by_p[reg][switch.technology_install] = switch.service_share_ey
    else:
        for switch in service_switches:
            service_tech_by_p[switch.technology_install] = switch.service_share_ey

    return dict(service_tech_by_p)
