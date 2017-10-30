"""Function related to service or fuel switch
"""
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_data

def get_service_rel_tech_decr_by(tech_decreased_share, service_tech_by_p):
    """Iterate technologies with future reduced service demand (replaced tech)
    and calculate their relative share of service in the base year

    Arguments
    ----------
    tech_decreased_share : dict
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
        [service_tech_by_p[tech] for tech in tech_decreased_share])

    # Relative of each diminishing tech (convert abs in dict to rel in dict)
    for tech in tech_decreased_share:
        try:
            rel_share_service_tech_decr_by[tech] = service_tech_by_p[tech] / float(sum_service_tech_decrease_p)
        except ZeroDivisionError:
            rel_share_service_tech_decr_by[tech] = 0

    return rel_share_service_tech_decr_by

def calc_service_switch_capacity(paths, enduses, assumptions, fuels, sim_param):
    """Create service switch based on assumption on
    changes in installed fuel capacity. Service switch are calculated
    based on the assumed capacity installation (in absolute GW)
    of a technologies. Assumptions on capacities
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
    """
    # --------------------------------
    # Reading in assumptions on capacity
    # installations from csv file
    # --------------------------------
    capcity_switches = read_data.read_capacity_installation(
        paths['path_capacity_installation'])

    # -------------------------------------
    # Assign correct fuel shares and fuels
    # -------------------------------------
    rs_enduses = []
    ss_enduses = []
    is_enduses = []
    for switch in capcity_switches:
        if switch['enduse'] in enduses['rs_all_enduses']:
            switch['fuel_shares_enduse_by_dict'] = 'rs_fuel_tech_p_by'
            switch['fuels'] = 'rs_fuel_raw_data_enduses'
            rs_enduses.append(switch['enduse'])
        elif switch['enduse'] in enduses['ss_all_enduses']:
            switch['fuel_shares_enduse_by_dict'] = 'ss_fuel_tech_p_by'
            switch['fuels'] = 'ss_fuel_raw_data_enduses'
            ss_enduses.append(switch['enduse'])
        elif switch['enduse'] in enduses['is_all_enduses']:
            switch['fuel_shares_enduse_by_dict'] = 'is_fuel_tech_p_by'
            switch['fuels'] = 'is_fuel_raw_data_enduses'
            is_enduses.append(switch['enduse'])

    # ----------------------
    #
    # ----------------------
    assumptions['rs_service_switches'] = create_service_switch(rs_enduses, capcity_switches, assumptions, sim_param, fuels)
    assumptions['ss_service_switches'] = create_service_switch(ss_enduses, capcity_switches, assumptions, sim_param, fuels)
    assumptions['is_service_switches'] = create_service_switch(is_enduses, capcity_switches, assumptions, sim_param, fuels)
    return assumptions

def create_service_switch(enduses, capcity_switches, assumptions, sim_param, fuels):
    """
    """
    service_switches = []
    for enduse in enduses:
        for capcity_switch in capcity_switches:
            if capcity_switch['enduse'] == enduse:
                service_switches_enduse = add_GWH_heating_change_serivce_ey(
                    enduse=enduse,
                    capcity_switches=capcity_switches,
                    technologies=assumptions['technologies'],
                    capcity_switch=capcity_switch,
                    fuel_shares_enduse_by=assumptions[capcity_switch['fuel_shares_enduse_by_dict']][capcity_switch['enduse']],
                    fuel_enduse_y=fuels[capcity_switch['fuels']][capcity_switch['enduse']],
                    sim_param=sim_param,
                    other_enduse_mode_info=assumptions['other_enduse_mode_info'])
                service_switches += service_switches_enduse

    return service_switches

def add_GWH_heating_change_serivce_ey(
        enduse,
        capcity_switches,
        technologies,
        capcity_switch,
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
    capcity_switch : dict
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
        TODO

    Flow
    ----
    Convert fuel shares to absolute fuel per technology,
    add technology specific absolute fuel change.

    Calculate back to fuel shares in ey.


    - Add XY GWh for a specific technology (e.g. 20GWH heat pumps added until ey)

    TOODS
    - convert to service per technology for end_year
    - convert fuel input to service end year
    - Calculate percentage of service for ey (collect all different absolute fuel
    definitions (e.g. absolute fuel heat pumps & absolute fuel boiler C))
    --> This is actually a service switch --> Convert to service switch
    """
    """Example boilerA: 100GWH, boilerB: 100GWH by

    1. Calculate service for ey: 100GWH * 0.4 , 100 GWH * 0.7
    2. Calculate service for new tech: Boiler C 100 GWH * eff_boilerC_ey 0.5
    3. Convert all services to percent: BoilerA: 40/160 = 0.25; BoilerB: 70/160 = 0.43; boilerC:50/160 = 0.31

    --> Service 
    """
    sim_param_NEW = {
        'base_yr': sim_param['base_yr'],
        'curr_yr': capcity_switch['year_fuel_consumption_switched'],
        'end_yr': capcity_switch['year_fuel_consumption_switched'],
        'sim_period_yrs': capcity_switch['year_fuel_consumption_switched'] + 1 - sim_param['base_yr']
        }
    # ---------------------------------------------
    # Calculate service per technolgies of by for ey
    # ---------------------------------------------
    service_enduse_tech = {}
    tot_service_y = 0

    for fueltype, tech_fuel_shares in fuel_shares_enduse_by.items():
        for tech, fuel_share_by in tech_fuel_shares.items():

            # End year efficiency TODO: DO NOT TAKE EFFICIENCY OF END YEAR BUT EFFICIENCY OF SIMLATION YEAR
            #tech_eff_ey = tech_stock.get_tech_attr(enduse, tech, 'eff_ey')
            tech_eff_ey = tech_related.calc_eff_cy(
                    tech,
                    sim_param_NEW,
                    technologies,
                    other_enduse_mode_info,
                    technologies[tech]['eff_achieved'],
                    technologies[tech]['diff_method'])
                
            # Convert to service
            service_tech_ey_y = fuel_enduse_y[fueltype] * fuel_share_by * tech_eff_ey
            service_enduse_tech[tech] = service_tech_ey_y

            # Sum total yearly service
            tot_service_y += service_tech_ey_y

    # -------------------------------------------
    # Calculate service for increased technologies
    # -------------------------------------------
    #If technology exists, add service
    for switch in capcity_switches:
        if enduse == switch['enduse']:
            technology_install = switch['technology_install']
            fuel_capacity_installed = switch['fuel_capacity_installed']
            #TODO: UNIT CONVERSION!!
            tech_eff_ey = tech_related.calc_eff_cy(
                technology_install,
                sim_param_NEW,
                technologies,
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

        #TODO DEFINE tech_assum_max_share for all techs
        # TODO: Assert if tech_assum_max_share > than defined in technologies
        service_switches_enduse.append({
            'enduse': enduse,
            'tech': tech,
            'service_share_ey': service_tech_p,
            'tech_assum_max': technologies[tech]['tech_assum_max_share']
            }
            )

    return service_switches_enduse
