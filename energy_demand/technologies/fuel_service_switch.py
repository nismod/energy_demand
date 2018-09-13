"""Function related to service or fuel switch
"""
import logging
from collections import defaultdict
from energy_demand.technologies import tech_related
from energy_demand.read_write import read_data
from energy_demand.basic import basic_functions
from energy_demand.scripts import init_scripts

def get_all_narrative_points(switches, enduse):
    """Get all narrative points of an enduse

    Arguments
    ---------
    switches : list
        All switches
    enduse : str
        Enduse

    Returns
    -------
    switch_yrs : list
        All sorted defined timesteps from narrative
    """
    switch_yrs = set([])

    for switch in switches:
        if switch.enduse == enduse:
            switch_yrs.add(switch.switch_yr)

    list(switch_yrs).sort()

    return switch_yrs

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

            # If None, then switch is true across all sectors or sector == None
            if not crit_switch_happening[enduse] or not sector:
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
        specified_tech_enduse_by
    ):
    """Get fraction of service for each technology
    defined in a switch for every narrative year

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
    narrative_yrs_enduse_tech_ey_p = defaultdict(dict)

    # Calculate enduse tech_ey_p for every narrative temporal point
    for region, switches in service_switches.items():

        # Get all enduses defined in switches
        enduses = get_all_enduses_of_switches(switches)

        for enduse in enduses:
            narrative_yrs_enduse_tech_ey_p[enduse][region] = defaultdict(dict)

            for switch in switches:
                if switch.enduse == enduse:
                    narrative_yrs_enduse_tech_ey_p[enduse][region][switch.switch_yr][switch.technology_install] = switch.service_share_ey

    return dict(narrative_yrs_enduse_tech_ey_p)

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
            tech_not_assigned_by_p[tech] = s_tech_by_p[sector][enduse][tech]

    # Normalise: convert to percentage
    tot_share_not_assigned = sum(tech_not_assigned_by_p.values())
    for tech, share_by in tech_not_assigned_by_p.items():

        if tot_share_not_assigned == 0:
            tech_not_assigned_by_p[tech] = 0
        else:
            tech_not_assigned_by_p[tech] = share_by / tot_share_not_assigned

    # Get all defined technologies in base year
    for tech in specified_tech_enduse_by[enduse]:

        if tech not in switch_technologies:

            if s_tot_defined == 1.0:
                # All technologies are fully defined
                switch_new = read_data.ServiceSwitch(
                    enduse=enduse,
                    sector=sector,
                    technology_install=tech,
                    service_share_ey=0,
                    switch_yr=switch_yr)
            else:
                # Calculate not defined share in switches
                s_not_assigned = 1 - s_tot_defined

                # Reduce not assigned share proportionally
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

                    # If no fuel demand, also no switch possible
                    if tot_share_not_assigned == 0:
                        switch_new.service_share_ey = 0

                    service_switches_out.append(switch_new)

    return service_switches_out

def get_all_enduses_of_switches(switches):
    '''Read all endueses of defined switches

    Arguments
    ---------
    switches : list
        Defined switches

    Returns
    -------
    enduses : list
        All enduses defined in switches
    '''
    enduses = set([])
    for switch in switches:
        enduses.add(switch.enduse)
    enduses = list(enduses)

    return enduses

def get_all_sectors_of_switches(switches, enduse_to_match):
    '''

    Arguments
    ---------
    switches : list
        Defined switches

    Returns
    -------
    enduses : list
        All enduses defined in switches
    '''
    sectors = set([])
    for switch in switches:
        if switch.enduse == enduse_to_match:
            sectors.add(switch.sector)

    sectors = list(sectors)

    return sectors

def get_sectors_of_enduse(enduse_to_match, enduses, sectors):
    """Get corresponding sectors of an enduse

    Arguments
    ---------
    enduse_to_match : str
        Enduse to match sectors
    enduses : dict
        All enduses per submodel
    sectors : dict
        All sectors per submodel

    Returns
    -------
    sectors_of_enduse : list
        All sectors of an enduse
    """
    for submodel, submodel_enduses in enduses.items():
        if enduse_to_match in submodel_enduses:
            sectors_of_enduse = sectors[submodel]

    return sectors_of_enduse

def autocomplete_switches(
        service_switches,
        specified_tech_enduse_by,
        s_tech_by_p,
        enduses,
        sectors,
        crit_all_the_same=True,
        regions=False,
        f_diffusion=False,
        techs_affected_spatial_f=False,
        service_switches_from_capacity=[]
    ):
    """Add not defined technologies in switches and set
    correct future service share.

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
    enduses : list
        Enduses
    sectors : list
        Sectors
    crit_all_the_same : bool
        Criteria wheter regionally specific or not
    regions : list
        Regions
    f_diffusion : 
        
    techs_affected_spatial_f : 

    service_switches_from_capacity : list, default=[]
        Service switches stemming from capacity switches
    Returns
    -------
    reg_share_s_tech_ey_p : dict
        Shares per technology in end year
    service_switches_out : list
        Added services switches which now in total sum up to 100%
    """
    reg_share_s_tech_ey_p = {}
    service_switches_out = {}

    # Enduses form direct switches
    switch_enduses = get_all_enduses_of_switches(service_switches)

    # Enduses from capacity witches
    any_region = list(service_switches_from_capacity.keys())[0]
    switch_enduses_capacity_switches = get_all_enduses_of_switches(
        service_switches_from_capacity[any_region])

    # All enduses
    switch_enduses = set(switch_enduses + switch_enduses_capacity_switches)

    # Iterate enduses
    for enduse in switch_enduses:
        logging.info("... calculating service switches: {} crit_all_the_same: {}".format(enduse, crit_all_the_same))

        sectors_of_enduse = get_sectors_of_enduse(
            enduse, enduses, sectors)

        # Iterate sectors of enduse
        for sector in sectors_of_enduse:

            switches_enduse = init_scripts.get_sector__enduse_switches(
                sector, enduse, service_switches)

            # -----------------------------------------
            #  Append service switches which were
            #  generated from capacity switches
            # -----------------------------------------
            service_switches_out[sector] = {}
            for region in regions:
                service_switches_out[sector][region] = service_switches_from_capacity[region]

            if crit_all_the_same:
                updated_switches = []

                # Get all narrative years
                switch_yrs = get_all_narrative_points(
                    switches_enduse, enduse=enduse)

                # Execut function for every narrative year
                for switch_yr in switch_yrs:

                    enduse_switches = []
                    s_tot_defined = 0
                    switch_technologies = []

                    for switch in switches_enduse:
                        if switch.enduse == enduse and switch.switch_yr == switch_yr:
                            s_tot_defined += switch.service_share_ey
                            switch_technologies.append(switch.technology_install)
                            enduse_switches.append(switch)

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

                    updated_switches.extend(switches_new)

                # For every region, set same switches
                for region in regions:
                    service_switches_out[sector][region].extend(updated_switches)
            else:
                for region in regions:

                    # Get all narrative year
                    switch_yrs = get_all_narrative_points(
                        service_switches, enduse=enduse)

                    # Execut function for yvery narrative year
                    for switch_yr in switch_yrs:

                        # Get all switches of this enduse
                        enduse_switches = []
                        s_tot_defined = 0
                        switch_technologies = []

                        for switch in switches_enduse:
                            if switch.enduse == enduse and switch.switch_yr == switch_yr:

                                # Global share of technology diffusion
                                s_share_ey_global = switch.service_share_ey

                                # If technology is affected by spatial exlicit diffusion
                                if switch.technology_install in techs_affected_spatial_f:

                                    # Regional diffusion calculation
                                    s_share_ey_regional = s_share_ey_global * f_diffusion[enduse][region]

                                    # -------------------------------------
                                    # if larger than max crit, set to 1
                                    # -------------------------------------
                                    max_crit = 1
                                    if s_share_ey_regional > max_crit:
                                        s_share_ey_regional = max_crit

                                    if s_tot_defined + s_share_ey_regional > 1.0:

                                        if round(s_tot_defined + s_share_ey_regional) > 1:
                                            # TODO
                                            logging.warning(
                                                "{}  {} {}".format(s_tot_defined, s_share_ey_regional, s_tot_defined + s_share_ey_regional))
                                            raise Exception(
                                                "Error of regional parameter calcuation. More than one technology switched with larger share") 
                                        else:
                                            s_share_ey_regional = max_crit - s_share_ey_regional
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

                                # Create switch
                                switches_new = create_switches_from_s_shares(
                                    enduse=enduse,
                                    s_tech_by_p=s_tech_by_p,
                                    switch_technologies=switch_technologies,
                                    specified_tech_enduse_by=specified_tech_enduse_by,
                                    enduse_switches=enduse_switches,
                                    s_tot_defined=s_tot_defined,
                                    sector=sector,
                                    switch_yr=switch_yr)

                                service_switches_out[sector][region].extend(switches_new)

            # Calculate fraction of service for each technology
            reg_share_s_tech_ey_p[sector] = get_share_s_tech_ey(
                service_switches_out[sector],
                specified_tech_enduse_by)

    return reg_share_s_tech_ey_p

def capacity_switch(
        narrative_timesteps,
        regions,
        capacity_switches,
        technologies,
        fuels,
        fuel_shares_enduse_by,
        base_yr
    ):
    """Create service switches based on assumption on
    changes in installed fuel capacity (`capacity switches`).
    Service switch are calculated based on the assumed
    capacity installation (in absolute GW) of technologies.
    Assumptions on capacities are defined in the
    CSV file `switches_capacity.csv`

    Note
    -----
    With the information about the installed capacity
    only the change in percentage in end year gets calulated.
    This means that there is not absolute change in demand (
        e.g. you cant add additional demand of an existing technology
        --> It is only a switch)
    Arguments
    ---------
    narrative_timesteps : dict
        List with narrative timestep for every enduse
    regions : list
        Regions
    capacity_switches : list
        Capacity switches
    technologies : dict
        Technologies
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
    """
    service_switches = {}

    for region in regions:
        service_switches[region] = []

        # Get all affected enduses of capacity switches
        switch_enduses = get_all_enduses_of_switches(
            capacity_switches[region])

        if switch_enduses == []:
            pass # no capacity switch defined
        else:
            for enduse in switch_enduses:

                # Get all capacity switches related to this enduse
                enduse_capacity_switches = get_switches_of_enduse(
                    capacity_switches[region], enduse, crit_region=False)

                for switch in enduse_capacity_switches:

                    sector_info_crit = basic_functions.test_if_sector(
                        fuel_shares_enduse_by[enduse])

                    # Check if enduse has sectors
                    if not sector_info_crit:
                        fuel_shares = fuel_shares_enduse_by[enduse]
                    else:
                        any_sector = list(fuel_shares_enduse_by[enduse].keys())[0]
                        fuel_shares = fuel_shares_enduse_by[enduse][any_sector]

                    # Convert capacity switches to service switches
                    enduse_service_switches = create_service_switch(
                        narrative_timesteps[enduse],
                        enduse,
                        switch.sector,
                        switch,
                        enduse_capacity_switches,
                        technologies,
                        fuel_shares,
                        base_yr,
                        fuels[enduse])

                    # Add service switches
                    service_switches[region] += enduse_service_switches

    return service_switches

def create_service_switch(
        narrative_timesteps,
        enduse,
        sector,
        switch,
        enduse_capacity_switches,
        technologies,
        fuel_shares_enduse_by,
        base_yr,
        fuel_enduse_y
    ):
    """Generate service switch based on capacity assumptions

    Arguments
    ---------
    narrative_timesteps : list
        Narrative timesteps
    enduse : dict
        Enduse
    switch : obj
        Capacity switch
    enduse_capacity_switches : list
        All capacity switches of an enduse (see warning)
    technologies : dict
        Technologies
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
    """
    service_switches_enduse = []

    for switch_yr in narrative_timesteps:

        # Get switches of narrative timestep
        capacity_switches = get_switches_of_enduse(
            enduse_capacity_switches, enduse, year=switch_yr, crit_region=False)

        # ---------------------------------------------
        # Calculate service per technology for switch_yr
        # ---------------------------------------------
        service_enduse_tech = {}

        for fueltype, tech_fuel_shares in fuel_shares_enduse_by.items():
            for tech, fuel_share_by in tech_fuel_shares.items():

                # Efficiency of year when capacity is fully installed
                eff_cy = tech_related.calc_eff_cy(
                    base_yr,
                    switch.switch_yr,
                    technologies[tech].eff_by,
                    technologies[tech].eff_ey,
                    technologies[tech].year_eff_ey,
                    technologies[tech].eff_achieved,
                    technologies[tech].diff_method)

                # Convert to service (fuel * fuelshare * eff)
                s_tech_ey_y = fuel_enduse_y[fueltype] * fuel_share_by * eff_cy
                service_enduse_tech[tech] = s_tech_ey_y

        # -------------------------------------------
        # Calculate service of installed capacity of
        # increased (installed) technologies
        # -------------------------------------------
        for switch in capacity_switches:
            eff_cy = tech_related.calc_eff_cy(
                base_yr,
                switch.switch_yr,
                technologies[switch.technology_install].eff_by,
                technologies[switch.technology_install].eff_ey,
                technologies[switch.technology_install].year_eff_ey,
                technologies[switch.technology_install].eff_achieved,
                technologies[switch.technology_install].diff_method)

            # Convert installed capacity to service
            installed_capacity_ey = switch.installed_capacity * eff_cy

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
        for tech, s_tech_p in service_enduse_tech.items():

            service_switch = read_data.ServiceSwitch(
                enduse=enduse,
                sector=sector,
                technology_install=tech,
                service_share_ey=s_tech_p,
                switch_yr=switch_yr)

            service_switches_enduse.append(service_switch)

    return service_switches_enduse

def get_switches_of_enduse(
        switches,
        enduse,
        year=False,
        crit_region=True
    ):
    """Get all fuel switches of a specific enduse and
    year (optional)

    Arguments
    ----------
    switches : list
        Switches
    enduse : str
        Enduse
    year : int,default=False
        Year
    crit_region : bool, default=True
        Criteria whether region specific switches

    Returns
    -------
    enduse_switches : list
        All switches of a specific enduse
    """
    if crit_region:
        enduse_switches = {}
        for reg in switches:
            enduse_switches[reg] = []
            for switch in switches[reg]:

                if not year:
                    if switch.enduse == enduse:
                        enduse_switches[reg].append(switch)
                else:
                    if switch.enduse == enduse and switch.switch_yr == year:
                        enduse_switches[reg].append(switch)
    else:
        enduse_switches = []
        for switch in switches:
            if not year:
                if switch.enduse == enduse:
                    enduse_switches.append(switch)
            else:
                if switch.enduse == enduse and switch.switch_yr == year:
                    enduse_switches.append(switch)

    return enduse_switches

def switches_to_dict(service_switches):
    """Write switch to dict, i.e. providing service fraction
    of technology as dict: {tech: service_ey_p}

    Arguments
    ---------
    service_switches : dict
        Service switches

    Returns
    -------
    s_tech_by_p : dict
        Service tech after service switch

    service_switches : dict
        Reg, fuel_swtiches
    """
    s_tech_by_p = defaultdict(dict)

    for reg, reg_switches in service_switches.items():
        for switch in reg_switches:
            s_tech_by_p[reg][switch.technology_install] = switch.service_share_ey

        assert round(sum(s_tech_by_p[reg].values()), 3) == 1

    return dict(s_tech_by_p)
