"""This file contains all calculations related
to spatial explicit calculations of technology/innovation
penetration.

TODO MORE INFO

1. Steps
- define concept (e.g. rural_urban)
- calculate congruence values
- attribute diffusion weights to congruence values
- Calculate spatial index

"""
import logging
from collections import defaultdict
import numpy as np
from random import randint
from energy_demand.scripts import init_scripts
from energy_demand.read_write import read_data

def from_socio_economic_data_to_spatial_diffusion_values(regions, diffusionv_values=None):
    """Create SDI from socio-economic data



    concepts : list
        List with concepts (e.g. poor, welathy, rich)


    Info
    ------
    *   SPEED 'diffusions_speed_lower_concept' 
    """
    spatial_diffusion_values = {}

    # ------------------
    # Diffusion speed
    # ------------------
    diffusions_speed_lower_concept = 1
    diffusions_speed_higher_concept = 2

    # How much congruent to urban (e.g. with rural population share) https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/591464/RUCLAD_leaflet_Jan2017.pdf
    congruence_value = {
        0 : {'congruence_value': 0, 'description': 'missing values'}, #Lower concept diffusion speed
        1 : {'congruence_value': 1 - 0.8, 'description': 'Mainly Rural (rural including hub towns >=80%)'},
        2 : {'congruence_value': 1 - 0.7, 'description': 'Largely Rural (rural including hub towns 50-79%)'},
        3 : {'congruence_value': 1 - 0.35, 'description': 'Urban with Significant Rural (rural including hub towns 26-49%)'},
        4 : {'congruence_value': 1 - 0.20, 'description': 'Urban with City and Town'},
        5 : {'congruence_value': 1 - 0.20, 'description': 'Urban with Minor Conurbation'},
        6 : {'congruence_value': 1 - 0.20, 'description': 'Urban with Major Conurbation'}}
    
    # Calculate diffusion values baed on speed attributes
    diffusion_values = {}
    for concept_id, con_values in congruence_value.items():
        lower_concept_val = con_values['congruence_value'] * diffusions_speed_lower_concept
        higher_concept_val = con_values['congruence_value'] * diffusions_speed_higher_concept

        diffusion_values[concept_id] = {}
        diffusion_values[concept_id]['diffusion_speed'] = lower_concept_val + higher_concept_val

    # ------------------
    # Real data
    # ------------------
    ruc11cd_values = read_data.taget_ruc11cd_values(
        path_to_csv="C://Users//cenv0553//nismod//data_energy_demand//_raw_data//RUC11_LAD11_ENv2.csv")

    for region in regions:

        # Multiply speed of diffusion of concept with concept congruence value
        try:
            ruc11cd_value = ruc11cd_values[region] 
        except KeyError:
            ruc11cd_value = 1
            ("ERROR: SET TO CONGRUEN VALUE +")

        spatial_diffusion_values[region] = diffusion_values[ruc11cd_value]['diffusion_speed']

    return spatial_diffusion_values

def load_spatial_diffusion_values(regions, enduses):
    """Load or calculate spatial diffusion values

    This are the values which already incorporate different
    speeds in diffusion and the congruence values

    
    e.g. based on urban/rural population

    TODO: Maybe read in

    Arguments
    ---------
    regions : dict
        Regions
    enduses : list
        Enduses for which spatial explicit is calculated

    Returns
    -------
    spatial_index : dict
        Spatial index
    """
    spatial_index = defaultdict(dict)

    spatial_index_cl = from_socio_economic_data_to_spatial_diffusion_values(regions)

    # Apply the diffusion values for all enduses
    for enduse in enduses:
        #dummy_indeces = [1.6, 2.5.]
        cnt = 0
        for region in regions:

           # dummy_index = 1
            #dummy_index = dummy_indeces[cnt]
            #dummy_index = randint(1, 10)
            #spatial_index[enduse][region] = dummy_index

            spatial_index[enduse][region] = spatial_index_cl[region]

            cnt += 1

    return dict(spatial_index)

def calc_diff_factor(regions, spatial_diff_values, fuels):
    """From spatial diffusion values calculate diffusion
    factor for every region (which needs to sum up to one
    across all regions) and end use. With help of these calculation diffusion
    factors, a spatial explicit diffusion of innovations can be
    implemented.

    Arguments
    ----------
    regions : dict
        Regions
    spatial_diff_values : dict
        Spatial diffusion index values Enduse, reg
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
    """
    # Calculate fraction of energy demand of every region of total demand
    reg_enduse_p = defaultdict(dict)
    fraction_p = defaultdict(dict)

    for fuel_submodel in fuels:

        # -----------------------------------
        # If sectors, sum fuel across sectors
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
        # Calculate % of enduse ed of a region of total enduse ed
        # --------------------
        for enduse in enduses:

            # Total uk fuel of enduse
            tot_enduse_uk = 0
            for reg in regions:
                tot_enduse_uk += np.sum(fuel_submodel[reg][enduse])

            # Calculate regional % of enduse
            for region in regions:
                reg_enduse_p[enduse][region] = np.sum(fuel_submodel[region][enduse]) / tot_enduse_uk

            tot_reg_enduse_p = sum(reg_enduse_p[enduse].values())

            # Calculate fraction
            for region in regions:
                fraction_p[enduse][region] = np.sum(reg_enduse_p[enduse][region]) / tot_reg_enduse_p

        # ----------
        # Multiply fraction of enduse with spatial_diff_values
        # ----------
        reg_fraction_multiplied_index = {}
        for enduse, regions_fuel_p in fraction_p.items():
            reg_fraction_multiplied_index[enduse] = {}
            for reg, fuel_p in regions_fuel_p.items():
                reg_fraction_multiplied_index[enduse][reg] = fuel_p * spatial_diff_values[enduse][reg]

    #-----------
    # Normalize
    #-----------
    for enduse in reg_fraction_multiplied_index:
        sum_enduse = sum(reg_fraction_multiplied_index[enduse].values())
        for reg in reg_fraction_multiplied_index[enduse]:
            reg_fraction_multiplied_index[enduse][reg] = reg_fraction_multiplied_index[enduse][reg] / sum_enduse

    # Testing
    for enduse in reg_fraction_multiplied_index:
        np.testing.assert_almost_equal(
            sum(reg_fraction_multiplied_index[enduse].values()),
            1,
            decimal=2)

    return reg_fraction_multiplied_index

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
    =========
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
    uk_service_enduse = 100

    for region in regions:

        # Disaggregation factor
        f_fuel_disagg = np.sum(fuel_disaggregated[region][enduse]) / uk_enduse_fuel

        # Calculate fraction of regional service
        for tech, uk_tech_service_ey_p in uk_techs_service_p.items():

            uk_service_tech = uk_tech_service_ey_p * uk_service_enduse

            # ---------------------------------------------
            # B.) Calculate regional service for technology
            # ---------------------------------------------
            if tech in techs_affected_spatial_f:
                # Use spatial factors
                reg_service_tech = uk_service_tech * spatial_factors[enduse][region]
            else:
                # If not specified, use fuel disaggregation for enduse factor
                reg_service_tech = uk_service_tech * f_fuel_disagg

            reg_enduse_tech_p_ey[region][tech] = reg_service_tech

        # ---------------------------------------------
        # C.) Calculate regional fraction
        # ---------------------------------------------
        tot_service_reg_enduse = f_fuel_disagg * uk_service_enduse

        for tech, service_tech in reg_enduse_tech_p_ey[region].items():
            reg_enduse_tech_p_ey[region][tech] = service_tech / tot_service_reg_enduse

    return dict(reg_enduse_tech_p_ey)

def spatially_differentiated_modelling(
        regions,
        all_enduses,
        init_cont,
        fuel_disagg,
        rs_share_s_tech_ey_p,
        ss_share_s_tech_ey_p,
        is_share_s_tech_ey_p,
        techs_affected_spatial_f,
    ):
    """
    TODO

    regions : dict
        Regions
    all_enduses : dict
        Enduse
    init_cont : dict
        TO_DEFINE
    sum_across_sectors_all_regs : dict
        TO_DEFINE
    rs_share_s_tech_ey_p : dict
        TO_DEFINE
    ss_share_s_tech_ey_p : dict
        TO_DEFINE
    is_share_s_tech_ey_p : dict
        TO_DEFINE
    techs_affected_spatial_f : list
        Technologies which are affected by spatially heterogeneous diffusion

    Returns
    --------
    rs_reg_share_s_tech_ey_p :
        TO_DEFINE
    ss_reg_share_s_tech_ey_p :
        TO_DEFINE
    is_reg_share_s_tech_ey_p :
        TO_DEFINE
    init_cont

    Explanation
    ============
    (1) Define all technologies which are spatially differentiated

    (2) Load all diffusion values

    (3) Calculate diffusion factors
    """
    # -----
    # Diffusion values
    # -----
    spatial_diff_values = load_spatial_diffusion_values(
        regions,
        all_enduses)

    # -----
    # Calculation of sigmoid diffusion factors
    # -----
    # Load diffusion factors
    f_spatial_diffusion = calc_diff_factor(
        regions,
        spatial_diff_values,
        [fuel_disagg['rs_fuel_disagg'], fuel_disagg['ss_fuel_disagg'], fuel_disagg['is_fuel_disagg']])

    # -------------
    # ===========================Technology specific diffusion of end year shares
    local = False
    if local == True:
        test_factor_overall_enduse_heating_improvement = 0.2
        affected_enduse = 'rs_space_heating'

        # Get enduse specific fuel for each region
        fuels_reg = get_enduse_specific_fuel_all_regs(
            enduse=affected_enduse,
            fuels_disagg=[fuel_disagg['rs_fuel_disagg'], fuel_disagg['ss_fuel_disagg'], fuel_disagg['is_fuel_disagg']])
        

        # end use specficic improvements 
        single_variable_d = {}
        single_variable_d[str(test_factor_overall_enduse_heating_improvement)] = factor_improvements_single(
            factor_uk=test_factor_overall_enduse_heating_improvement,
            regions=regions,
            spatial_factors=f_spatial_diffusion[affected_enduse],
            fuel_regs_enduse=fuels_reg)

    # ===========================

    # -------------
    # Technology specific diffusion of end year shares
    # -------------
    # TODO MAYBE WRITE IN FUNCTIONS
    # Residential spatial explicit modelling
    rs_reg_share_s_tech_ey_p = {}
    for enduse, uk_techs_service_p in rs_share_s_tech_ey_p.items():
        rs_reg_share_s_tech_ey_p[enduse] = calc_regional_services(
            enduse,
            uk_techs_service_p,
            regions,
            f_spatial_diffusion,
            fuel_disagg['rs_fuel_disagg'],
            techs_affected_spatial_f)

    # Generate sigmoid curves (s_generate_sigmoid) for every region
    ss_aggr_fuel = init_scripts.sum_across_sectors_all_regs(
        fuel_disagg['ss_fuel_disagg'])

    ss_reg_share_s_tech_ey_p = {}
    for sector, uk_techs_service_enduses_p in ss_share_s_tech_ey_p.items():
        ss_reg_share_s_tech_ey_p[sector] = {}
        for enduse, uk_techs_service_p in uk_techs_service_enduses_p.items():
            ss_reg_share_s_tech_ey_p[sector][enduse] = calc_regional_services(
                enduse,
                uk_techs_service_p,
                regions,
                f_spatial_diffusion,
                ss_aggr_fuel,
                techs_affected_spatial_f)

    is_aggr_fuel = init_scripts.sum_across_sectors_all_regs(
        fuel_disagg['is_fuel_disagg'])

    is_reg_share_s_tech_ey_p = {}
    for sector, uk_techs_service_enduses_p in is_share_s_tech_ey_p.items():
        is_reg_share_s_tech_ey_p[sector] = {}
        for enduse, uk_techs_service_p in uk_techs_service_enduses_p.items():
            is_reg_share_s_tech_ey_p[sector][enduse] = calc_regional_services(
                enduse,
                uk_techs_service_p,
                regions,
                f_spatial_diffusion,
                is_aggr_fuel,
                techs_affected_spatial_f)

    return rs_reg_share_s_tech_ey_p, ss_reg_share_s_tech_ey_p, is_reg_share_s_tech_ey_p, init_cont, f_spatial_diffusion

def factor_improvements_single(
        factor_uk,
        regions,
        spatial_factors,
        fuel_regs_enduse,
    ):
    """Calculate regional specific end year service shares
    of technologies (rs_reg_enduse_tech_p_ey)

    Arguments
    =========
    factor_uk : float
        Improvement of either an enduse or a variable for the whole UK


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
    reg_enduse_tech_p_ey = {}

    # ------------------------------------
    # Calculate national total enduse fuel and service
    # ------------------------------------
    uk_enduse_fuel = 0
    for fuel_reg in fuel_regs_enduse.values():
        uk_enduse_fuel += np.sum(fuel_reg)

    # ----
    # Service of enduse for all regions
    # ----
    ##uk_service_enduse = 100
    test = 0

    for region in regions:

        # Disaggregation factor (share of regional fuel compared to total fuel)
        f_fuel_disagg = np.sum(fuel_regs_enduse[region]) / uk_enduse_fuel

        # How much service is affected in current region if would be everywhere the same
        uk_service_factored = factor_uk ##* uk_service_enduse

        # ---------------------------------------------
        # B.) Calculate regional service for technology
        # ---------------------------------------------
        reg_service_tech = uk_service_factored * spatial_factors[region]

        #reg_enduse_tech_p_ey[region] = reg_service_tech

        # ---------------------------------------------
        # C.) Calculate regional fraction
        # ---------------------------------------------
        tot_service_reg_enduse = f_fuel_disagg ##* uk_service_enduse

        reg_enduse_tech_p_ey[region] = reg_service_tech / tot_service_reg_enduse

        logging.info(
            "FUEL FACTOR reg: {}  val: {}, f: {} fuel: {}  fuel: {} ".format(
                region,
                round(reg_enduse_tech_p_ey[region], 3),
                round(f_fuel_disagg, 3),
                round(uk_enduse_fuel, 3),
                round(np.sum(fuel_regs_enduse[region]), 3)
                ))
        '''(
            "FUEL FACTOR reg: {}  val: {}, f: {} fuel: {}  fuel: {} ".format(
                region,
                round(reg_enduse_tech_p_ey[region], 3),
                round(f_fuel_disagg, 3),
                round(uk_enduse_fuel, 3),
                round(np.sum(fuel_regs_enduse[region]), 3)
                ))'''

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

    # NORMALISE AS NOT LARGER THAN 0
    """normed_val = {}
    norm_sum = sum(reg_enduse_tech_p_ey.values())
    for reg, val in reg_enduse_tech_p_ey.items():
        normed_val[reg] = val / norm_sum

    test3 = 0
    for reg, val in normed_val.items():
        _a = val * uk_enduse_fuel
        test3 += _a
        logging.info("NORM: {}  {}  {}".format(
            reg,
            round(val, 3),
            round(_a, 3)))
    ("TESTDUM c " + str(test3))
    """
    #Soul be the same
    logging.info("FAKTOR UK :" + str(factor_uk))
    logging.info("Lost demand: " + str(demand_lost))
    logging.info("TESTDUM a " + str(test))
    logging.info("TESTDUM b " + str(uk_enduse_fuel * factor_uk))

    return reg_enduse_tech_p_ey

def get_enduse_specific_fuel_all_regs(
        enduse,
        fuels_disagg):
    """Get enduse for all regions for a specific enduse
    read from a list of 
    TODO: IMPROVE SPEED
    """
    fuels_enduse = {}

    for fuel_submodel in fuels_disagg:
        for reg, enduse_fuels in fuel_submodel.items():
            for enduse_to_match, fuels_regs in enduse_fuels.items():
                if enduse == enduse_to_match:
                    fuels_enduse[reg] = fuels_regs

    if fuels_enduse == {}:
        import sys
        sys.exit("ERROR NOT ABLE TO FIND FUE")
    else:
        return fuels_enduse
