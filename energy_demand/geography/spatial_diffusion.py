"""This file contains all calculations related
to spatial explicit calculations of technology/innovation
penetration."""

import sys
import logging
from collections import defaultdict
import numpy as np

def realdata_to_spatialdiffval(regions, real_values, speed_con_max):
    """Create SDI from socio-economic data

    concepts : list
        List with concepts (e.g. poor, welathy, rich)

    Info
    ------
    *   SPEED 'speed_con_min'
    """
    diffusion_values = {}

    # Diffusion speed assumptions
    speed_con_min = 1               # Speed at val_con == 0
    speed_con_max = speed_con_max   # Speed at con_val == 1

    # Max congruence value
    con_max = max(real_values.values())

    for region in regions:

        # Multiply speed of diffusion of concept with concept congruence value
        try:
            real_value = real_values[region]
        except KeyError:
            real_value = np.mean(real_values.values())
            logging.warning("Set average real data for region %s", region)

        # Calculate congruence value
        congruence_value = real_value / con_max

        # Calculate diffusion value
        lower_concept_val = (1 - congruence_value) * speed_con_min
        higher_concept_val = congruence_value * speed_con_max

        diffusion_values[region] = lower_concept_val + higher_concept_val

        logging.info(
            "Reg: %s diffusion_value: %s real_value: %s",
            region,
            lower_concept_val + higher_concept_val,
            real_value)

    return diffusion_values

def spatial_diffusion_values(regions, pop_density):
    """Load spatial diffusion values

    This are the values which already incorporate different
    speeds in diffusion and the congruence values

    e.g. based on urban/rural population

    Arguments
    ---------
    regions : dict
        Regions

    Returns
    -------
    spatial_diff : dict
        Spatial diffusion values based on speed assumptions
    """
    spatial_diff = {}

    # Diffusion values based on urban/rural
    spatial_diff_urban_rural = realdata_to_spatialdiffval(
        regions=regions,                # Regions
        real_values=pop_density,        # Real values
        speed_con_max=2)                # Speed

    for region in regions:
        spatial_diff[region] = spatial_diff_urban_rural[region]

    return spatial_diff

def calc_diffusion_f(regions, f_reg, spatial_diff_values, fuels):
    """From spatial diffusion values calculate diffusion
    factor for every region (which needs to sum up to one
    across all regions) and end use. With help of these calculation diffusion
    factors, a spatial explicit diffusion of innovations can be
    implemented.

    Arguments
    ----------
    regions : dict
        Regions
    f_reg : dict
        Regional not weighted diffusion factors
    spatial_diff_values : dict
        Spatial diffusion index values
    fuels : array
        Fuels per enduse or fuel per sector and enduse

    Example
    -------
    If the national assumption of a technology diffusion
    of 50% is defined (e.g. 50% of service are heat pumps), this
    percentage can be changed per region, i.e. in some regions
    with higher diffusion factors, a larger percentage adopt
    the technology on the expense of other regions, where a
    lower percentage adopt this technology. In sum however,
    for all regions, the total service still sums up to 50%.

    Note
    -----
    The total sum can be higher than 1 in case of high values.
    Therfore the factors need to be capped. TODO MORE INFO
    """

    # Calculate fraction of energy demand of every region of total demand
    reg_enduse_p = defaultdict(dict)
    fuels_enduse = {}

    for fuel_submodel in fuels:

        # -----------------------------------
        # Sum fuel across sectors
        # -----------------------------------
        fuel_submodel_new = defaultdict(dict)
        for reg, entries in fuel_submodel.items():
            enduses = entries.keys()
            try:
                for enduse in entries:
                    for sector in entries[enduse]:
                        fuel_submodel_new[reg][enduse] = 0

                for enduse in entries:
                    for sector in entries[enduse]:
                        fuel_submodel_new[reg][enduse] += np.sum(entries[enduse][sector])

                fuel_submodel = fuel_submodel_new
            except IndexError:
                enduses = entries.keys()
                break

        # --------------------
        # Calculate fraction of fuel for each region
        # --------------------
        for enduse in enduses:
            fuels_enduse[enduse] = 0

            # Total uk fuel of enduse
            tot_enduse_uk = 0
            for reg in regions:
                tot_enduse_uk += np.sum(fuel_submodel[reg][enduse])

            # Calculate regional % of enduse
            for region in regions:
                reg_enduse_p[enduse][region] = np.sum(fuel_submodel[region][enduse]) / tot_enduse_uk
                fuels_enduse[enduse] += np.sum(fuel_submodel[region][enduse])

        # ----------
        # Norm spatial factor (f_reg_norm) with population (does not sum upt to 1.p Eq. 7 Appendix)
        # ----------
        f_reg_norm = {}

        for enduse, regions_fuel_p in reg_enduse_p.items():

            # Sum across all regs (factor * fuel_p)
            sum_p_f_all_regs = 0
            for i in regions:
                sum_p_f_all_regs += f_reg[i] * regions_fuel_p[reg]

            f_reg_norm[enduse] = {}
            for reg, fuel_p in regions_fuel_p.items():
                f_reg_norm[enduse][reg] = f_reg[reg] / sum_p_f_all_regs

        # ----------
        # Norm which sums up to 1 (f_reg_norm_abs) (e.g. distriubte 200 units across space)
        # ----------
        f_reg_norm_abs = {}
        for enduse, regions_fuel_p in reg_enduse_p.items():
            f_reg_norm_abs[enduse] = {}
            for reg, fuel_p in regions_fuel_p.items():
                f_reg_norm_abs[enduse][reg] = fuel_p * spatial_diff_values[reg]

    #-----------
    # Normalize f_reg_norm_abs
    #-----------
    for enduse in f_reg_norm_abs:
        sum_enduse = sum(f_reg_norm_abs[enduse].values())
        for reg in f_reg_norm_abs[enduse]:
            f_reg_norm_abs[enduse][reg] = f_reg_norm_abs[enduse][reg] / sum_enduse

    # Testing
    for enduse in f_reg_norm_abs:
        np.testing.assert_almost_equal(
            sum(f_reg_norm_abs[enduse].values()),
            1,
            decimal=2)

    #-----------
    # TESTING 
    #-----------
    '''enduse = 'ss_water_heating'
    tot_amount_to_distribute = 200

    # -----
    # f_reg_norm_abs
    # -----
    # To distribute full absolute amount across all regs
    __t = 0
    for reg in regions:
        __t += f_reg_norm_abs[enduse][reg] * tot_amount_to_distribute

    logging.info("TOTAL MOUNT TO DISTR: " + str(tot_amount_to_distribute))
    logging.info("TOTAL MOUNT TO DISTR CTONRLL: " + str(__t))

    # -----
    # f_reg_norm_abs
    # -----
    global_f = 0.9
    _0 = []
    _1 = []
    _2 = []
    
    for reg in regions:
        logging.warning("-------")
        logging.warning("Not Normed: %s ", f_reg[reg] * global_f)                               # not normed
        logging.warning("Normed: %s ", f_reg_norm[enduse][reg] * global_f)  # normed with not summing up to 1
        logging.warning("Sums up to one: %s ", (f_reg_norm_abs[enduse][reg] * global_f))    #new
        logging.warning((f_reg_norm_abs[enduse][reg] * global_f) / reg_enduse_p[enduse][reg]) #old

        _0.append(f_reg[reg] * global_f)
        _1.append(f_reg_norm[enduse][reg] * global_f)
        _2.append(f_reg_norm_abs[enduse][reg] * global_f)


    logging.info("INFOF FOR DEBBUGING")
    logging.info(max(_0))
    logging.info(max(_1))
    logging.info(max(_2))

    logging.info("--")

    logging.info(sum(_0))
    logging.info(sum(_1))
    logging.info(sum(_2))'''

    return f_reg_norm_abs, f_reg_norm

def calc_regional_services(
        enduse,
        uk_techs_service_p,
        regions,
        spatial_factors,
        fuel_disaggregated,
        techs_affected_spatial_f
    ):
    """Calculate regional specific end year service shares
    of technologies (rs_reg_enduse_tech_p_ey)

    Arguments
    ---------
    uk_techs_service_p : dict
        Service shares per technology for future year
    regions : dict
        Regions
    spatial_factors : dict
        Spatial factor per enduse and region
    fuel_disaggregated : dict
        Fuels per region
    techs_affected_spatial_f : list
        List with technologies where spatial diffusion is affected

    Returns
    -------
    rs_reg_enduse_tech_p_ey : dict
        Regional specific model end year service shares of techs

    Modelling steps
    -----
    A.) Calculation national end use service to reduce
        (e.g. 50% heat pumps for all regions) (uk_tech_service_ey_p)

    B.) Distribute this service according to spatial index for
        techs where the spatial explicit diffusion applies (techs_affected_spatial_f).
        Otherwise disaggregated according to fuel

    C.) Convert regional service reduction to ey % in region
    """
    reg_enduse_tech_p_ey = defaultdict(dict)

    # ------------------------------------
    # Calculate national total enduse fuel and service
    # ------------------------------------
    uk_enduse_fuel = 0
    for region in regions:
        reg_enduse_tech_p_ey[region] = {}
        uk_enduse_fuel += np.sum(fuel_disaggregated[region][enduse])

    # ----
    # Service of enduse for all regions
    # ----
    for region in regions:

        # Disaggregation factor
        f_fuel_disagg = np.sum(fuel_disaggregated[region][enduse]) / uk_enduse_fuel
        print("SUMME should be 1")
        print(sum(uk_techs_service_p.values()))
        # Calculate fraction of regional service
        for tech, uk_tech_service_ey_p in uk_techs_service_p.items():

            global_tech_service_ey_p = uk_tech_service_ey_p

            # ---------------------------------------------
            # B.) Calculate regional service for technology
            # ---------------------------------------------
            if tech in techs_affected_spatial_f:
                # Use spatial factors
                reg_service_tech = global_tech_service_ey_p * spatial_factors[enduse][region]
            else:
                # If not specified, use fuel disaggregation for enduse factor
                reg_service_tech = global_tech_service_ey_p #* f_fuel_disagg

            reg_enduse_tech_p_ey[region][tech] = reg_service_tech
            print("--")
            print(global_tech_service_ey_p)
            print(reg_service_tech)

        import pprint
        print(sum(reg_enduse_tech_p_ey[region].values()))
        pprint.pprint(reg_enduse_tech_p_ey[region])
        # ---------------------------------------------
        # C.) Calculate regional fraction
        # ---------------------------------------------
        #tot_service_reg_enduse = f_fuel_disagg ##* uk_service_enduse

        for tech, service_tech in reg_enduse_tech_p_ey[region].items():
            
            # ----------------------------------
            #MAYBE ADD CAPPING VALUE TODO
            # ----------------------------------
            capping_val = 1

            #service_share = service_tech / tot_service_reg_enduse
            service_share = service_tech

            if service_share > capping_val:
                reg_enduse_tech_p_ey[region][tech] = capping_val
                logging.warning("CAPPING VALUE REACHED {}  {}  ".format(region, service_share))
            else:
                reg_enduse_tech_p_ey[region][tech] = service_share
            #OlD
            #reg_enduse_tech_p_ey[region][tech] = service_tech / tot_service_reg_enduse

    return dict(reg_enduse_tech_p_ey)

def calc_spatially_diffusion_factors(
        regions,
        fuel_disagg,
        pop_density
    ):
    """

    Arguments
    ---------

    Returns
    -------

        f_reg_norm_abs : dict
        Diffusion values with normed population. If no value
        is larger than 1, the total sum of all shares calculated
        for every region is identical to the defined scenario variable.

    spatial_diff_values : dict
        Spatial diffusion values (not normed, only considering differences
        in speed and congruence values)


    Explanation
    ============
    (I)     Load diffusion values
    (II)    Calculate diffusion factors
    (III)   Calculate sigmoid diffusion values for technology
            specific enduse service shares for every region
    """
    # -----
    # I. Diffusion diffusion values
    # -----
    spatial_diff_values = spatial_diffusion_values(
        regions,
        pop_density)

    # -----
    # II. Calculation of diffusion factors ( Not weighted with demand)
    # -----
    f_reg = {}

    max_value_diffusion = max(list(spatial_diff_values.values()))
    for region in regions:
        f_reg[region] = spatial_diff_values[region] / max_value_diffusion

    # Weighted with demand
    f_reg_norm_abs, f_reg_norm = calc_diffusion_f(
        regions,
        f_reg,
        spatial_diff_values,
        [fuel_disagg['rs_fuel_disagg'], fuel_disagg['ss_fuel_disagg'], fuel_disagg['is_fuel_disagg']])

    return f_reg, f_reg_norm, f_reg_norm_abs

def spatially_differentiated_modelling(
        regions,
        fuel_disagg,
        rs_share_s_tech_ey_p,
        ss_share_s_tech_ey_p,
        is_share_s_tech_ey_p,
        techs_affected_spatial_f,
        spatial_diffusion_factor
    ):
    """
    Regional diffusion shares of technologies is calculated
    based on calcualted spatial diffusion factors

    Arguments
    ---------
    regions : dict
        Regions
    fuel_disagg : dict
        Fuel per region
    rs_share_s_tech_ey_p : dict
        Global technology service shares
    ss_share_s_tech_ey_p : dict
        Global technology service shares
    is_share_s_tech_ey_p : dict
        Global technology service shares
    techs_affected_spatial_f : list
        Technologies which are affected by spatially heterogeneous diffusion
    spatial_diffusion_factor : dict
        Spatial diffusion factor

    Returns
    --------
    XX_reg_share_s_tech_ey_p :
        Technology specific service shares for every region (residential)
        considering differences in diffusion speed. 
        
        If the calculate regional shares are larger than 1.0, the 
        diffusion is set to the maximum criteria (`cap_max`). 
        This means that if some regions reach the maximum defined value,
        thes cannot futher increase their share. This means that other regions diffuse
        slower and do not reach such high leves (and because the faster regions
        cannot over-compensate, the total sum is not identical).

    Calculate sigmoid diffusion values for technology
    specific enduse service shares for every region
    """
    # Residential spatial explicit modelling
    rs_reg_share_s_tech_ey_p = {}
    for enduse, uk_techs_service_p in rs_share_s_tech_ey_p.items():
        rs_reg_share_s_tech_ey_p[enduse] = calc_regional_services(
            enduse,
            uk_techs_service_p,
            regions,
            spatial_diffusion_factor,
            fuel_disagg['rs_fuel_disagg'],
            techs_affected_spatial_f)

    ss_reg_share_s_tech_ey_p = {}
    for sector, uk_techs_service_enduses_p in ss_share_s_tech_ey_p.items():
        ss_reg_share_s_tech_ey_p[sector] = {}
        for enduse, uk_techs_service_p in uk_techs_service_enduses_p.items():
            ss_reg_share_s_tech_ey_p[sector][enduse] = calc_regional_services(
                enduse,
                uk_techs_service_p,
                regions,
                spatial_diffusion_factor,
                fuel_disagg['ss_fuel_disagg_sum_all_sectors'],
                techs_affected_spatial_f)

    is_reg_share_s_tech_ey_p = {}
    for sector, uk_techs_service_enduses_p in is_share_s_tech_ey_p.items():
        is_reg_share_s_tech_ey_p[sector] = {}
        for enduse, uk_techs_service_p in uk_techs_service_enduses_p.items():
            is_reg_share_s_tech_ey_p[sector][enduse] = calc_regional_services(
                enduse,
                uk_techs_service_p,
                regions,
                spatial_diffusion_factor,
                fuel_disagg['is_aggr_fuel_sum_all_sectors'],
                techs_affected_spatial_f)

    return rs_reg_share_s_tech_ey_p, ss_reg_share_s_tech_ey_p, is_reg_share_s_tech_ey_p

def factor_improvements_single(
        factor_uk,
        regions,
        f_reg,
        f_reg_norm,
        f_reg_norm_abs,
        fuel_regs_enduse
    ):
    """Calculate regional specific end year service shares
    of technologies (rs_reg_enduse_tech_p_ey)

    Arguments
    =========
    factor_uk : float
        Improvement of either an enduse or a variable for the whole UK
    regions : dict
        Regions
    f_reg : dict
        Regional spatial factors not normed with fuel demand
    f_reg_norm : dict
        Regional spatial factors normed with fuel demand (sum is not 1)
    f_reg_norm_abs : dict
        Regional spatial factors normed with fuel demand and normed that sum is 1
    spatial_diff_values : dict
        Spatial diffusion values
    fuel_regs_enduse : dict
        Fuels per region and end use

    Returns
    -------
    rs_reg_enduse_tech_p_ey : dict
        Regional specific model end year service shares of techs

    Modelling steps
    -----
    A.) Calculation national end use service to reduce
        (e.g. 50% heat pumps for all regions) (uk_tech_service_ey_p)

    B.) Distribute this service according to spatial index for
        techs where the spatial explicit diffusion applies (techs_affected_spatial_f).
        Otherwise disaggregated according to fuel

    C.) Convert regional service reduction to ey % in region
    """
    reg_enduse_tech_p_ey = {}

    factor_uk = 0.5 #TODO SCRAP REMOVE

    # Check which factors is to be used
    # if only distribute: f_reg_norm_abs
    # if max 1: f_reg_nrm
    # if not intersted in correct sum: f_reg
    if fuel_regs_enduse == {}:
        spatial_factor = f_reg
    else:
        spatial_factor = f_reg_norm_abs

    # Sum fuel
    uk_enduse_fuel = 0
    for fuel_reg in fuel_regs_enduse.values():
        uk_enduse_fuel += np.sum(fuel_reg)

    test = 0
    for region in regions:
        reg_enduse_tech_p_ey[region] = factor_uk * spatial_factor[region]

        logging.info(
            "FUEL FACTOR reg: {}  val: {}, fuel: {}  fuel: {} ".format(
                region,
                round(reg_enduse_tech_p_ey[region], 3),
                round(uk_enduse_fuel, 3),
                round(np.sum(fuel_regs_enduse[region]), 3)
                ))

        test += (reg_enduse_tech_p_ey[region] * np.sum(fuel_regs_enduse[region]))

    # ---------
    # PROBLEM THAT MORE THAN 100 percent could be reached if nt normed
    # ---------
    reg_enduse_tech_p_ey_capped = {}

    # Cap regions which have already reached and are larger than 1.0
    cap_max_crit = 1.0 #100%
    demand_lost = 0
    for region, region_factor in reg_enduse_tech_p_ey.items():
        if region_factor > cap_max_crit:
            logging.warning("INFO: FOR A REGION THE SHARE OF IMPROVEMENTIS LARGER THAN 1.0.")

            # Demand which is lost and capped
            diff_to_cap = region_factor - cap_max_crit
            demand_lost += diff_to_cap * np.sum(fuel_regs_enduse[region])

            reg_enduse_tech_p_ey_capped[region] = cap_max_crit
        else:
            reg_enduse_tech_p_ey_capped[region] = region_factor

    # Replace
    reg_enduse_tech_p_ey = reg_enduse_tech_p_ey_capped

    logging.warning("FAKTOR UK :" + str(factor_uk))
    logging.warning("Lost demand: " + str(demand_lost))
    logging.warning("TESTDUM a " + str(test))
    logging.warning("TESTDUM b " + str(uk_enduse_fuel * factor_uk))

    return reg_enduse_tech_p_ey

def get_enduse_specific_fuel_all_regs(
        enduse,
        fuels_disagg):
    """Get enduse for all regions for a specific enduse
    read from a list of
    TODO: IMPROVE SPEE
    """
    fuels_enduse = {}

    if enduse == []:
        return fuels_enduse
    else:    
        for fuel_submodel in fuels_disagg:
            for reg, enduse_fuels in fuel_submodel.items():
                for enduse_to_match, fuels_regs in enduse_fuels.items():
                    if enduse == enduse_to_match:
                        fuels_enduse[reg] = fuels_regs

        if fuels_enduse == {}:
            sys.exit("ERROR NOT ABLE TO FIND FUEL")
        else:
            return fuels_enduse
