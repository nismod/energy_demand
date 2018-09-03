"""Script functions which are executed after
model installation and after each scenario definition
"""
import logging
import numpy as np
from energy_demand.geography import spatial_diffusion
from energy_demand.read_write import read_data
from energy_demand.scripts import (s_fuel_to_service, s_generate_sigmoid)
from energy_demand.technologies import fuel_service_switch

def create_spatial_diffusion_factors(
        strategy_vars,
        fuel_disagg,
        regions,
        real_values,
        speed_con_max,
        p_outlier=5
    ):
    """

    p_outlier : float or int
        Nr of min and max outliers to flatten

    TODO. improve
    """
    if strategy_vars['spatial_explicit_diffusion']['scenario_value']:

        # Define diffusion speed
        speed_con_max = speed_con_max

        # Criteria whether a spatially differentiated diffusion is applied depending on real_values
        crit_all_the_same = False
    else:

        # NEW If not spatial different, set speed_con_max to 1
        speed_con_max = 1

        # Define that the penetration levels are the same for every region
        crit_all_the_same = True

    f_reg, f_reg_norm, f_reg_norm_abs = spatial_diffusion.calc_spatially_diffusion_factors(
        regions=regions,
        fuel_disagg=fuel_disagg,
        real_values=real_values,
        low_congruence_crit=True,
        speed_con_max=speed_con_max,
        p_outlier=p_outlier)

    '''plot_fig_paper = False
    if plot_fig_paper:
        from energy_demand.plotting import result_mapping
        # Global value to distribute
        global_value = 50

        # Select spatial diffusion factor
        #diffusion_vals = f_reg                                  # not weighted
        diffusion_vals = f_reg_norm['ss_space_heating']         # Weighted with enduse
        #diffusion_vals = f_reg_norm_abs['rs_space_heating']    # Absolute distribution (only for capacity installements)

        path_shapefile_input = os.path.abspath(
            'C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/lad_2016_uk_simplified.shp')

        result_mapping.plot_spatial_mapping_example(
            diffusion_vals=diffusion_vals,
            global_value=global_value,
            paths=data['result_paths'],
            regions=data['regions'],
            path_shapefile_input=path_shapefile_input,
            plotshow=True)'''

    return f_reg, f_reg_norm, f_reg_norm_abs, crit_all_the_same

def switch_calculations(
        data,
        f_reg,
        f_reg_norm,
        f_reg_norm_abs,
        crit_all_the_same
    ):
    """This function creates sigmoid diffusion values based
    on defined switches

    Arguments
    ----------
    data : dict
        Data container
    f_reg, f_reg_norm, f_reg_norm_abs : str
        Different spatial diffusion values
    crit_all_the_same : dict
        Criteria whether the diffusion is spatial explicit or not

    Returns
    -------
    rs_sig_param_tech, ss_sig_param_tech, is_sig_param_tech : dict
        Sigmoid diffusion parameters
    """
    # ---------------------------------------
    # Convert base year fuel input assumptions to energy service
    # ---------------------------------------
    # Residential submodel
    rs_s_tech_by_p,rs_s_fueltype_by_p = s_fuel_to_service.get_s_fueltype_tech(
        data['enduses']['rs_enduses'],
        data['lookups']['fueltypes'],
        data['assumptions'].rs_fuel_tech_p_by,
        data['fuels']['rs_fuel_raw'],
        data['technologies'])

    # Service submodel
    ss_s_tech_by_p = {}
    ss_s_fueltype_by_p = {}
    for sector in data['sectors']['ss_sectors']:
        ss_s_tech_by_p[sector], ss_s_fueltype_by_p[sector] = s_fuel_to_service.get_s_fueltype_tech(
            data['enduses']['ss_enduses'],
            data['lookups']['fueltypes'],
            data['assumptions'].ss_fuel_tech_p_by,
            data['fuels']['ss_fuel_raw'],
            data['technologies'],
            sector)

    # Industry submodel
    is_s_tech_by_p = {}
    is_s_fueltype_by_p = {}
    for sector in data['sectors']['is_sectors']:
        is_s_tech_by_p[sector], is_s_fueltype_by_p[sector] = s_fuel_to_service.get_s_fueltype_tech(
            data['enduses']['is_enduses'],
            data['lookups']['fueltypes'],
            data['assumptions'].is_fuel_tech_p_by,
            data['fuels']['is_fuel_raw'],
            data['technologies'],
            sector)

    # ========================================================================================
    # Capacity switches
    #
    # Calculate service shares considering potential capacity installations
    # ========================================================================================

    # Convert globally defined switches to regional switches
    f_diffusion = f_reg_norm_abs #TODO EXPLAIN # Select diffusion value

    reg_capacity_switches_rs = global_to_reg_capacity_switch(
        data['regions'], data['assumptions'].rs_capacity_switches, f_diffusion=f_diffusion)
    reg_capacity_switches_ss = global_to_reg_capacity_switch(
        data['regions'], data['assumptions'].ss_capacity_switches, f_diffusion=f_diffusion)
    reg_capacity_switches_is = global_to_reg_capacity_switch(
        data['regions'], data['assumptions'].is_capacity_switches, f_diffusion=f_diffusion)
    
    # sum across sectors
    ss_aggr_sector_fuels = s_fuel_to_service.sum_fuel_enduse_sectors(
        data['fuels']['ss_fuel_raw'],
        data['enduses']['ss_enduses'])

    is_aggr_sector_fuels = s_fuel_to_service.sum_fuel_enduse_sectors(
        data['fuels']['is_fuel_raw'],
        data['enduses']['is_enduses'])

    # Capacity switches
    rs_service_switches_incl_cap = fuel_service_switch.capacity_switch(
        data['regions'],
        reg_capacity_switches_rs,
        data['technologies'],
        data['fuels']['rs_fuel_raw'],
        data['assumptions'].rs_fuel_tech_p_by,
        data['assumptions'].base_yr)

    ss_service_switches_inlc_cap = fuel_service_switch.capacity_switch(
        data['regions'],
        reg_capacity_switches_ss,
        data['technologies'],
        ss_aggr_sector_fuels,
        data['assumptions'].ss_fuel_tech_p_by,
        data['assumptions'].base_yr)

    is_service_switches_incl_cap = fuel_service_switch.capacity_switch(
        data['regions'],
        reg_capacity_switches_is,
        data['technologies'],
        is_aggr_sector_fuels,
        data['assumptions'].is_fuel_tech_p_by,
        data['assumptions'].base_yr)

    # ========================================================================================
    # Service switches
    #
    # Get service shares of technologies for future year by considering
    # service switches. Potential capacity switches are used as inputs.
    #
    # Autocomplement defined service switches with technologies not
    # explicitly specified in switch on a global scale and distribute spatially.
    # ========================================================================================

    # Select spatial diffusion
    f_diffusion = f_reg_norm

    # Residential
    rs_share_s_tech_ey_p, rs_switches_autocompleted = fuel_service_switch.autocomplete_switches(
        data['assumptions'].rs_service_switches,
        data['assumptions'].rs_specified_tech_enduse_by,
        rs_s_tech_by_p,
        crit_all_the_same=crit_all_the_same,
        regions=data['regions'],
        f_diffusion=f_diffusion,
        techs_affected_spatial_f=data['assumptions'].techs_affected_spatial_f,
        service_switches_from_capacity=rs_service_switches_incl_cap)

    # Service
    ss_switches_autocompleted = {}
    ss_share_s_tech_ey_p = {}
    for sector in data['sectors']['ss_sectors']:

        # Get all switches of a sector
        sector_switches = get_sector_switches(
            sector, data['assumptions'].ss_service_switches)

        ss_share_s_tech_ey_p[sector], ss_switches_autocompleted[sector] = fuel_service_switch.autocomplete_switches(
            sector_switches,
            data['assumptions'].ss_specified_tech_enduse_by,
            ss_s_tech_by_p[sector],
            sector=sector,
            crit_all_the_same=crit_all_the_same,
            regions=data['regions'],
            f_diffusion=f_diffusion,
            techs_affected_spatial_f=data['assumptions'].techs_affected_spatial_f,
            service_switches_from_capacity=ss_service_switches_inlc_cap)

    # Industry
    is_switches_autocompleted = {}
    is_share_s_tech_ey_p = {}

    for sector in data['sectors']['is_sectors']:

        # Get all switches of a sector
        sector_switches = get_sector_switches(
            sector, data['assumptions'].is_service_switches)

        is_share_s_tech_ey_p[sector], is_switches_autocompleted[sector] = fuel_service_switch.autocomplete_switches(
            sector_switches,
            data['assumptions'].is_specified_tech_enduse_by,
            is_s_tech_by_p[sector],
            sector=sector,
            crit_all_the_same=crit_all_the_same,
            regions=data['regions'],
            f_diffusion=f_diffusion,
            techs_affected_spatial_f=data['assumptions'].techs_affected_spatial_f,
            service_switches_from_capacity=is_service_switches_incl_cap)

    # ========================================================================================
    # Fuel switches
    #
    # Calculate sigmoid diffusion considering fuel switches
    # and service switches. As inputs, service (and thus also capacity switches) are used
    # ========================================================================================

    # Residential
    rs_sig_param_tech = {}
    for enduse in data['enduses']['rs_enduses']:
        rs_sig_param_tech[enduse] = sig_param_calc_incl_fuel_switch(
            data['assumptions'].base_yr,
            data['assumptions'].crit_switch_happening,
            data['technologies'],
            enduse=enduse,
            fuel_switches=data['assumptions'].rs_fuel_switches,
            service_switches=rs_switches_autocompleted,
            s_tech_by_p=rs_s_tech_by_p[enduse],
            s_fueltype_by_p=rs_s_fueltype_by_p[enduse],
            share_s_tech_ey_p=rs_share_s_tech_ey_p[enduse],
            fuel_tech_p_by=data['assumptions'].rs_fuel_tech_p_by[enduse],
            regions=data['regions'],
            crit_all_the_same=crit_all_the_same)

    # Service
    ss_sig_param_tech = {}
    for enduse in data['enduses']['ss_enduses']:
        ss_sig_param_tech[enduse] = {}
        for sector in data['sectors']['ss_sectors']:
            ss_sig_param_tech[enduse][sector] = sig_param_calc_incl_fuel_switch(
                data['assumptions'].base_yr,
                data['assumptions'].crit_switch_happening,
                data['technologies'],
                enduse=enduse,
                fuel_switches=data['assumptions'].ss_fuel_switches,
                service_switches=ss_switches_autocompleted[sector],
                s_tech_by_p=ss_s_tech_by_p[sector][enduse],
                s_fueltype_by_p=ss_s_fueltype_by_p[sector][enduse],
                share_s_tech_ey_p=ss_share_s_tech_ey_p[sector][enduse],
                fuel_tech_p_by=data['assumptions'].ss_fuel_tech_p_by[enduse][sector],
                regions=data['regions'],
                sector=sector,
                crit_all_the_same=crit_all_the_same)

    # Industry
    is_sig_param_tech = {}
    for enduse in data['enduses']['is_enduses']:
        is_sig_param_tech[enduse] = {}
        for sector in data['sectors']['is_sectors']:
            is_sig_param_tech[enduse][sector] = sig_param_calc_incl_fuel_switch(
                data['assumptions'].base_yr,
                data['assumptions'].crit_switch_happening,
                data['technologies'],
                enduse=enduse,
                fuel_switches=data['assumptions'].is_fuel_switches,
                service_switches=is_switches_autocompleted[sector],
                s_tech_by_p=is_s_tech_by_p[sector][enduse],
                s_fueltype_by_p=is_s_fueltype_by_p[sector][enduse],
                share_s_tech_ey_p=is_share_s_tech_ey_p[sector][enduse],
                fuel_tech_p_by=data['assumptions'].is_fuel_tech_p_by[enduse][sector],
                regions=data['regions'],
                sector=sector,
                crit_all_the_same=crit_all_the_same)

    # ------------------
    # Convert to annual values TODO
    # ------------------

    return rs_sig_param_tech, ss_sig_param_tech, is_sig_param_tech

def spatial_explicit_modelling_strategy_vars(
        assumptions,
        regions,
        fuel_disagg,
        f_reg,
        f_reg_norm,
        f_reg_norm_abs
    ):
    """
    Spatial explicit modelling of scenario variables
    based on narratives. From UK factors to regional specific factors
    Convert strategy variables to regional variables

    Arguments
    ---------
    assumptions : dict
    regions

    """
    # Iterate strategy variables and calculate regional variable
    for var_name, strategy_var in assumptions.strategy_vars.items():
        logging.info("Spatially explicit diffusion modelling %s", var_name)

        new_narratives = []
        for narrative in strategy_var['narratives']:
            regional_vars_by = {}
            regional_vars_ey = {}
            if not narrative['regional_specific']:
                narrative['regional_vals_ey'] = narrative['value_ey']
                narrative['regional_vals_by'] = narrative['value_by']
                new_narratives.append(narrative)
            else:
                # Check whether scenario varaible is regionally modelled
                if var_name not in assumptions.spatially_modelled_vars:

                    # Variable is not spatially modelled
                    for region in regions:
                        regional_vars_ey[region] = float(narrative['value_ey'])
                        regional_vars_by[region] = float(narrative['value_by'])
                else:
                    if strategy_var['affected_enduse'] == []:
                        logging.info(
                            "For scenario var %s no affected enduse is defined. Thus speed is used for diffusion",
                                var_name)

                    # Get enduse specific fuel for each region
                    fuels_reg = spatial_diffusion.get_enduse_regs(
                        enduse=strategy_var['affected_enduse'],
                        fuels_disagg=[
                            fuel_disagg['rs_fuel_disagg'],
                            fuel_disagg['ss_fuel_disagg'],
                            fuel_disagg['is_fuel_disagg']])

                    # Calculate regional specific strategy variables values
                    reg_specific_variables_ey = spatial_diffusion.factor_improvements_single(
                        factor_uk=narrative['value_ey'],
                        regions=regions,
                        f_reg=f_reg,
                        f_reg_norm=f_reg_norm,
                        f_reg_norm_abs=f_reg_norm_abs,
                        fuel_regs_enduse=fuels_reg)

                    reg_specific_variables_by = spatial_diffusion.factor_improvements_single(
                        factor_uk=narrative['value_by'],
                        regions=regions,
                        f_reg=f_reg,
                        f_reg_norm=f_reg_norm,
                        f_reg_norm_abs=f_reg_norm_abs,
                        fuel_regs_enduse=fuels_reg)

                    # Add regional specific strategy variables values
                    for region in regions:
                        regional_vars_ey[region] = float(reg_specific_variables_ey[region])
                        regional_vars_by[region] = float(reg_specific_variables_by[region])

                narrative['regional_vals_by'] = regional_vars_by
                narrative['regional_vals_ey'] = regional_vars_ey
                new_narratives.append(narrative)

        assumptions.strategy_vars[var_name]['narratives'] = new_narratives

    return assumptions.strategy_vars

def global_to_reg_capacity_switch(
        regions,
        global_capactiy_switch,
        f_diffusion
    ):
    """Conversion of global capacity switch installations
    to regional installation

    Arguments
    ---------
    regions : list
        Regions
    global_capactiy_switch : float
        Global switch
    f_diffusion : dict

    Returns
    -------
    reg_capacity_switch : dict
        Regional capacity switch
    """
    reg_capacity_switch = {}
    for reg in regions:
        reg_capacity_switch[reg] = []

    # Get all affected enduses of capacity switches
    switch_enduses = set([])
    for switch in global_capactiy_switch:
        switch_enduses.add(switch.enduse)
    switch_enduses = list(switch_enduses)

    for enduse in switch_enduses:

        # Get all capacity switches related to this enduse
        enduse_capacity_switches = []
        for switch in global_capactiy_switch:
            if switch.enduse == enduse:
                enduse_capacity_switches.append(switch)

        for region in regions:
            for switch in enduse_capacity_switches:

                global_capacity = switch.installed_capacity
                regional_capacity = global_capacity  * f_diffusion[switch.enduse][region]

                new_switch = read_data.CapacitySwitch(
                    enduse=switch.enduse,
                    technology_install=switch.technology_install,
                    switch_yr=switch.switch_yr,
                    installed_capacity=regional_capacity,
                    sector=switch.sector)

            reg_capacity_switch[region].append(new_switch)

    return reg_capacity_switch

def sum_across_all_submodels_regs(
        fueltypes_nr,
        regions,
        submodels
    ):
    """Calculate total sum of fuel per region
    """
    fuel_aggregated_regs = {}

    for region in regions:

        tot_reg = np.zeros((fueltypes_nr), dtype="float")

        for submodel_fuel_disagg in submodels:

            for fuel_sector_enduse in submodel_fuel_disagg[region].values():

                # Test if fuel for sector
                if isinstance(fuel_sector_enduse, dict):
                    for sector_fuel in fuel_sector_enduse.values():
                        tot_reg += sector_fuel
                else:
                    tot_reg += fuel_sector_enduse

        fuel_aggregated_regs[region] = tot_reg

    return fuel_aggregated_regs

def sum_across_sectors_all_regs(fuel_disagg_reg):
    """Sum fuel across all sectors for every region

    Arguments
    ---------
    fuel_disagg_reg : dict
        Fuel per region, sector and enduse

    Returns
    -------
    fuel_aggregated : dict
        Aggregated fuel per region and enduse
    """
    fuel_aggregated = {}
    for reg, entries in fuel_disagg_reg.items():
        fuel_aggregated[reg] = {}
        for enduse in entries:
            for sector in entries[enduse]:
                fuel_aggregated[reg][enduse] = 0

        for enduse in entries:
            for sector in entries[enduse]:
                fuel_aggregated[reg][enduse] += np.sum(entries[enduse][sector])

    return fuel_aggregated

def convert_sharesdict_to_service_switches(
        yr_until_switched,
        enduse,
        s_tech_switched_p,
        regions=False
    ):
    """Convert service of technologies to service switches.

    Arguments
    ---------
    yr_until_switched : int
        Year until switch happens
    enduse : str
        Enduse
    s_tech_switched_p : dict
        Fraction of total service of technologies after switch
    regions : dict, default=False
        All regions

    Returns
    -------
    service_switches_after_fuel_switch : dict
        Changed services witches including fuel switches
    """
    new_service_switches = {}

    for reg in regions:
        new_service_switches[reg] = []

        for tech, s_tech_p in s_tech_switched_p[reg].items():
            if tech == 'placeholder_tech':
                pass
            else:
                switch_new = read_data.ServiceSwitch(
                    enduse=enduse,
                    technology_install=tech,
                    service_share_ey=s_tech_p,
                    switch_yr=yr_until_switched)

                new_service_switches[reg].append(switch_new)

    return new_service_switches

def sig_param_calc_incl_fuel_switch(
        base_yr,
        crit_switch_happening,
        technologies,
        enduse,
        fuel_switches,
        service_switches,
        s_tech_by_p,
        s_fueltype_by_p,
        share_s_tech_ey_p,
        fuel_tech_p_by,
        regions=False,
        sector=False,
        crit_all_the_same=True
    ):
    """Calculate sigmoid diffusion paramaters considering
    fuel or service switches. Test if service switch and
    fuel switch are defined simultaneously (raise error if true).

    Arguments
    ---------
    base_yr : int
        Base year
    technologies : dict
        technologies
    enduse : str
        enduse
    fuel_switches : dict
        fuel switches
    service_switches : dict
        service switches
    s_tech_by_p : dict
        Service share per technology in base year
    s_fueltype_by_p : dict
        Service share per fueltype for base year
    share_s_tech_ey_p : dict
        Service share per technology for end year
    fuel_tech_p_by : dict
        Fuel share per technology in base year
    regions : dict
        Regions

    Returns
    -------
    sig_param_tech : dict
        Sigmoid parameters for all affected technologies
    service_switches_out : list
        Service switches
    """
    # ----------------------------------------
    # Test if fuel switch is defined for enduse
    # Get affected technologies in fuel switch
    # ----------------------------------------
    tech_switch_affected = s_generate_sigmoid.get_tech_installed(
        enduse, fuel_switches)

    if len(tech_switch_affected) > 0:
        crit_fuel_switch = True
    else:
        crit_fuel_switch = False

    # ------------------------------------------
    # Test if service swich is defined for enduse
    # ------------------------------------------
    service_switches_enduse = fuel_service_switch.get_fuel_switches_enduse(
        service_switches, enduse)

    # ------------------------------------------
    # Initialisations
    # ------------------------------------------
    sig_param_tech = {}
    service_switches_out = {}
    for region in regions:
        sig_param_tech[region] = []
        service_switches_out[region] = service_switches_enduse[region]

    # Test if switch is defined
    crit_switch_service = fuel_service_switch.get_switch_criteria(
        enduse,
        sector,
        crit_switch_happening)

    # ------------------------------------------
    # SERVICE switch
    #
    # Calculate service shares considering service
    # switches and the diffusion parameters
    # ------------------------------------------
    if crit_switch_service:

        # Calculate only from service switch
        s_tech_switched_p = share_s_tech_ey_p

        # Calculate sigmoid diffusion parameters
        l_values_sig = s_generate_sigmoid.get_l_values(
            technologies=technologies,
            technologies_to_consider=s_tech_by_p.keys(),
            regions=regions)

    # ------------------------------------------
    # FUEL switch
    # ------------------------------------------
    if crit_fuel_switch:
        """
        Calculate future service share after fuel switches
        and calculte sigmoid diffusion paramters.
        """
        # Get fuel switches of enduse
        enduse_fuel_switches = fuel_service_switch.get_fuel_switches_enduse(
            fuel_switches, enduse)

        # Only calculate for one reg
        any_region = regions[0]

        l_values_sig = {}
        s_tech_switched_p = {}

        if crit_all_the_same:

            # Calculate service demand after fuel switches for each technology
            s_tech_switched_p_values__all_reg = s_generate_sigmoid.calc_service_fuel_switched(
                enduse_fuel_switches,
                technologies,
                s_fueltype_by_p,
                s_tech_by_p,
                fuel_tech_p_by,
                'actual_switch')

            # Calculate L for every technology for sigmod diffusion
            l_values_all_regs = s_generate_sigmoid.tech_l_sigmoid(
                s_tech_switched_p[any_region],
                enduse_fuel_switches,
                technologies,
                s_tech_by_p.keys(),
                s_fueltype_by_p,
                s_tech_by_p,
                fuel_tech_p_by)

            for region in regions:
                s_tech_switched_p[region] = s_tech_switched_p_values__all_reg
                l_values_sig[region] = l_values_all_regs
        else:
            for region in regions:

                # Calculate service demand after fuel switches for each technology
                s_tech_switched_p[region] = s_generate_sigmoid.calc_service_fuel_switched(
                    enduse_fuel_switches,
                    technologies,
                    s_fueltype_by_p,
                    s_tech_by_p,
                    fuel_tech_p_by,
                    'actual_switch')

                # Calculate L for every technology for sigmod diffusion
                l_values_sig[region] = s_generate_sigmoid.tech_l_sigmoid(
                    s_tech_switched_p[region],
                    enduse_fuel_switches,
                    technologies,
                    s_tech_by_p.keys(),
                    s_fueltype_by_p,
                    s_tech_by_p,
                    fuel_tech_p_by)

        # Get year of switches
        for fuelswitch in enduse_fuel_switches:
            yr_until_switched = fuelswitch.switch_yr
            break

        # Convert serivce shares to service switches
        service_switches_out = convert_sharesdict_to_service_switches(
            yr_until_switched=yr_until_switched,
            enduse=enduse,
            s_tech_switched_p=s_tech_switched_p,
            regions=regions)

        # Calculate only from fuel switch
        share_s_tech_ey_p = fuel_service_switch.switches_to_dict(
            service_switches_out)

    if crit_switch_service or crit_fuel_switch:
        logging.info("---------- switches %s %s %s", enduse, crit_switch_service, crit_fuel_switch)

        # Calculates parameters for sigmoid diffusion of
        # technologies which are switched to/installed.
        sig_param_tech = {}

        # ONly calculate for one reg
        any_region = regions[0]

        # Get year of switches (TODO: IMRPOVE THAT IN NARRATIVE)
        for switch in service_switches_out[any_region]:
            if switch.enduse == enduse:
                yr_until_switched = switch.switch_yr
                break

        if crit_all_the_same:

            # Calculate for one region
            sig_param_tech_all_regs_value = s_generate_sigmoid.tech_sigmoid_parameters(
                yr_until_switched,
                base_yr,
                technologies,
                l_values_sig[any_region],
                s_tech_by_p,
                s_tech_switched_p[any_region])

            for region in regions:
                sig_param_tech[region] = sig_param_tech_all_regs_value
        else:
            for region in regions:
                sig_param_tech[region] = s_generate_sigmoid.tech_sigmoid_parameters(
                    yr_until_switched,
                    base_yr,
                    technologies,
                    l_values_sig[region],
                    s_tech_by_p,
                    s_tech_switched_p[region])
    else:
        pass #no switches are defined

    return sig_param_tech

def get_sector_switches(sector_to_match, service_switches):
    """Get all switches of a sector if the switches are
    defined specifically for a sector. If the switches are
    not specifically for a sector, return all switches
    """
    # Get all sectors for this enduse
    switches = set([])
    for switch in service_switches:
        if switch.sector == sector_to_match:
            switches.add(switch)
        # Not defined specifically for sectors and add all
        elif not switch.sector:
            switches.add(switch)
        else:
            pass

    return list(switches)
