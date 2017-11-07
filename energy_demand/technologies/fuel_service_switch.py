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

def calc_service_switch_capacity(paths, enduses, assumptions, fuels, sim_param):
    """Create service switch based on assumption on
    changes in installed fuel capacity. Service switch are calculated
    based on the assumed capacity installation (in absolute GW)
    of technologies. Assumptions on capacities
    are defined in the CSV file `assumptions_capacity_installations.csv`

    Arguments
    ---------
    paths : dict
        Paths
    enduses : dict
        Enduses
    assumptions : dict
        Assumptions
    fuels : dict
        Fuels
    sim_param : dict
        Simulation parameters

    Returns
    -------
    assumptions : dict
        Dict with updated service switches

    Warning
    -------
    Capacity switches overwrite existing service switches
    """
    # --------------------------------
    # Reading in assumptions on capacity installations from csv file
    # --------------------------------
    capacity_switches = read_data.read_capacity_installation(
        paths['path_capacity_installation'])

    # -------------------------------------
    # Assign correct fuel shares and fuels
    # -------------------------------------
    rs_enduses_switch = set([])
    ss_enduses_switch  = set([])
    is_enduses_switch  = set([])
    for switch in capacity_switches:
        if switch['enduse'] in enduses['rs_all_enduses']:
            rs_enduses_switch.add(switch['enduse'])
        elif switch['enduse'] in enduses['ss_all_enduses']:
            ss_enduses_switch.add(switch['enduse'])
        elif switch['enduse'] in enduses['is_all_enduses']:
            is_enduses_switch.add(switch['enduse'])

    # -------------------------
    # Calculate service switches
    # -------------------------
    assumptions['rs_service_switches'] = create_service_switch(
        rs_enduses_switch, capacity_switches, assumptions, sim_param, fuels['rs_fuel_raw_data_enduses'], 'rs_fuel_tech_p_by')
    assumptions['ss_service_switches'] = create_service_switch(
        ss_enduses_switch, capacity_switches, assumptions, sim_param, fuels['ss_fuel_raw_data_enduses'], 'ss_fuel_tech_p_by')
    assumptions['is_service_switches'] = create_service_switch(
        is_enduses_switch, capacity_switches, assumptions, sim_param, fuels['is_fuel_raw_data_enduses'], 'is_fuel_tech_p_by')

    # Criteria that capacity switch is implemented
    assumptions['capacity_switch'] = True

    return assumptions

def create_service_switch(
        enduses,
        capacity_switches,
        assumptions,
        sim_param,
        fuels,
        fuel_shares_enduse_by_dict
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
    sim_param : dict
        Simulation parameters
    """
    # List to store service switches
    service_switches = []

    for enduse in enduses:
        for capacity_switch in capacity_switches:
            if capacity_switch['enduse'] == enduse:
                
                # Convert
                service_switches_enduse = convert_capacity_assumption_to_service(
                    enduse=enduse,
                    capacity_switches=capacity_switches,
                    technologies=assumptions['technologies'],
                    capacity_switch=capacity_switch,
                    fuel_shares_enduse_by=assumptions[fuel_shares_enduse_by_dict][enduse],
                    fuel_enduse_y=fuels[enduse],
                    sim_param=sim_param,
                    other_enduse_mode_info=assumptions['other_enduse_mode_info'])

                # Add service switch
                service_switches += service_switches_enduse

    return service_switches

def convert_capacity_assumption_to_service(
        enduse,
        capacity_switches,
        technologies,
        capacity_switch,
        fuel_shares_enduse_by,
        fuel_enduse_y,
        sim_param,
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
    sim_param_new['base_yr'] = sim_param['base_yr']
    sim_param_new['curr_yr'] = capacity_switch['year_fuel_consumption_switched']
    sim_param_new['end_yr'] = capacity_switch['year_fuel_consumption_switched']
    sim_param_new['sim_period_yrs'] = capacity_switch['year_fuel_consumption_switched'] + 1 - sim_param['base_yr']

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
                technologies[tech]['eff_by'],
                technologies[tech]['eff_ey'],
                other_enduse_mode_info,
                technologies[tech]['eff_achieved'],
                technologies[tech]['diff_method'])

            # Convert to service
            service_tech_ey_y = fuel_enduse_y[fueltype] * fuel_share_by * tech_eff_ey
            service_enduse_tech[tech] = service_tech_ey_y

    # -------------------------------------------
    # Calculate service for increased technologies
    # -------------------------------------------
    #If technology exists, add service
    for switch in capacity_switches:
        if enduse == switch['enduse']:
            technology_install = switch['technology_install']
            fuel_capacity_installed = switch['fuel_capacity_installed']

            tech_eff_ey = tech_related.calc_eff_cy(
                sim_param_new,
                technologies[technology_install]['eff_by'],
                technologies[technology_install]['eff_ey'],
                other_enduse_mode_info,
                technologies[technology_install]['eff_achieved'],
                technologies[technology_install]['diff_method'])

            # Convert fuel to service
            installed_capacity_ey = fuel_capacity_installed * tech_eff_ey

            # Add cpacity
            service_enduse_tech[technology_install] += installed_capacity_ey

    # -------------------------------------------
    # Calculate service in % per enduse
    # -------------------------------------------
    tot_service = sum(service_enduse_tech.values())
    for tech, service_tech in service_enduse_tech.items():
        service_enduse_tech[tech] = service_tech / tot_service

    # -------------------------------------------
    # Calculate to switch technology_install
    # -------------------------------------------
    service_switches_enduse = []

    for tech, service_tech_p in service_enduse_tech.items():
        service_switches_enduse.append({
            'enduse': enduse,
            'tech': tech,
            'service_share_ey': service_tech_p,
            'tech_assum_max': technologies[tech]['tech_assum_max_share']})

    return service_switches_enduse
