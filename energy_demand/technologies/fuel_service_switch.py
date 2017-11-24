"""Function related to service or fuel switch
"""
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_data

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

def calc_service_switch_capacity(
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
        TODO
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

    # Criteria that capacity switch is implemented
    capacity_switch_crit = True

    return service_switches, capacity_switch_crit

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
    # List to store service switches
    service_switches = []

    for enduse in enduses:
        for capacity_switch in capacity_switches:
            if capacity_switch.enduse == enduse:

                # Convert
                service_switches_enduse = convert_capacity_assumption_to_service(
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

def convert_capacity_assumption_to_service(
        enduse,
        capacity_switches,
        capacity_switch,
        technologies,
        fuel_shares_enduse_by,
        fuel_enduse_y,
        base_yr,
        other_enduse_mode_info
    ):
    """Convert assumption about adding

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
    sim_param_new = {}
    sim_param_new['base_yr'] = base_yr
    sim_param_new['curr_yr'] = capacity_switch.switch_yr

    # ---------------------------------------------
    # Calculate service per technolgies of by for ey
    # ---------------------------------------------
    service_enduse_tech = {}

    for fueltype, tech_fuel_shares in fuel_shares_enduse_by.items():
        for tech, fuel_share_by in tech_fuel_shares.items():

            # Efficiency of year when capacity is fully installed
            # Assumption: Standard sigmoid diffusion
            tech_eff_ey = tech_related.calc_eff_cy(
                sim_param_new,
                technologies[tech].eff_by,
                technologies[tech].eff_ey,
                technologies[tech].year_eff_ey,
                other_enduse_mode_info,
                technologies[tech].eff_achieved,
                technologies[tech].diff_method)

            # Convert to service #TODO: ERROR WHY DOUBLE
            service_tech_ey_y = fuel_enduse_y[fueltype] * fuel_share_by * tech_eff_ey
            service_enduse_tech[tech] = service_tech_ey_y

    # -------------------------------------------
    # Calculate service for increased technologies
    # -------------------------------------------
    #If technology exists, add service
    for switch in capacity_switches:
        if enduse == switch.enduse:
            technology_install = switch.technology_install
            installed_capacity = switch.installed_capacity

            tech_eff_ey = tech_related.calc_eff_cy(
                sim_param_new,
                technologies[technology_install].eff_by,
                technologies[technology_install].eff_ey,
                technologies[technology_install].year_eff_ey,
                other_enduse_mode_info,
                technologies[technology_install].eff_achieved,
                technologies[technology_install].diff_method)

            # Convert fuel to service
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

