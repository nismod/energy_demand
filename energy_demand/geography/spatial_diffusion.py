"""This file contains all calculations related
to spatial explicit calculations of technology/innovation
penetration
"""
from collections import defaultdict
import numpy as np
from energy_demand.scripts import s_generate_sigmoid

def load_spatial_diff_values(regions, enduses):
    """Load or calculate spatial diffusion values
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

    for enduse in enduses:
        #dummy_indeces = [1.6, 2.5] #[2.8, 5.5] #[1.4, 2]
        cnt = 0
        for region in regions:

            dummy_index = 1 #TODO
            #dummy_index = dummy_indeces[cnt]

            spatial_index[enduse][region] = dummy_index
            cnt += 1

    return dict(spatial_index)

def calc_diff_factor(regions, spatial_diff_values, fuels):
    """From spatial diffusion values calculate diffusion
    factor for every region (which needs to sum up to one
    across all regions). With help of these calculation diffusion
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
    If e.g. the national assumption of a technology diffusion
    of 50% exists (e.g. 50% of service are heat pumps), this
    percentage can be changed per region, i.e. in some regions
    with higher diffusion factors, a larger percentage adapt
    the technology on the expense of other regions where a
    lower percentage adapt this technology. In sum however,
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

                #_y = 0
                for enduse in entries:
                    for sector in entries[enduse]:
                        fuel_submodel_new[reg][enduse] += np.sum(entries[enduse][sector])
                        #_y = _y + np.sum(entries[enduse][sector])
                
                #print(np.sum(fuel_submodel_new[reg][enduse]))
                #print(np.sum(_y))
                #prit("d")
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
        np.testing.assert_almost_equal(sum(reg_fraction_multiplied_index[enduse].values()), 1, decimal=2)

    return reg_fraction_multiplied_index

def calc_regional_services(
        uk_service_p,
        regions,
        spatial_factors,
        fuel_disaggregated,
        techs_affected_spatial_f
    ):
    """Calculate regional specific model end year service shares
    of technologies (rs_reg_enduse_tech_p_ey)

    Arguments
    =========
    uk_service_p : dict
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
    rs_reg_enduse_tech_p_ey = defaultdict(dict)

    for enduse, uk_techs_service_p in uk_service_p.items():

        # ------------------------------------
        # Calculate national total enduse fuel and service
        # ------------------------------------
        uk_enduse_fuel = 0
        for region in regions:
            rs_reg_enduse_tech_p_ey[enduse][region] = {}
            uk_enduse_fuel += np.sum(fuel_disaggregated[region][enduse])

        # ----
        # Service of enduse for all regions
        # ----
        uk_service_enduse = 100

        for region in regions:

            # Disaggregation factor
            fuel_disagg_factor = np.sum(fuel_disaggregated[region][enduse]) / uk_enduse_fuel

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
                    reg_service_tech = uk_service_tech * fuel_disagg_factor

                if reg_service_tech == 0:
                    rs_reg_enduse_tech_p_ey[enduse][region][tech] = 0
                else:
                    rs_reg_enduse_tech_p_ey[enduse][region][tech] = reg_service_tech

            # ---------------------------------------------
            # C.) Calculate regional fraction
            # ---------------------------------------------
            tot_service_reg_enduse = fuel_disagg_factor * uk_service_enduse

            for tech, service_tech in rs_reg_enduse_tech_p_ey[enduse][region].items():
                rs_reg_enduse_tech_p_ey[enduse][region][tech] = service_tech / tot_service_reg_enduse

    return dict(rs_reg_enduse_tech_p_ey)

def spatially_differentiated_modelling(
        regions,
        all_enduses,
        sd_cont,
        sgs_cont,
        fts_cont,
        sum_across_sectors_all_regs,
        rs_share_service_tech_ey_p,
        ss_share_service_tech_ey_p,
        is_share_service_tech_ey_p
    ):
    """
    TODO
    """
    # --------------------------------------------------
    # Define technologies affected by regional diffusion TODO
    # --------------------------------------------------
    techs_affected_spatial_f = ['heat_pumps_electricity'] #'boiler_hydrogen',

    # Load diffusion values
    spatial_diff_values = load_spatial_diff_values(
        regions,
        all_enduses)

    # Load diffusion factors
    spatial_diffusion_factor = calc_diff_factor(
        regions,
        spatial_diff_values,
        [sd_cont['rs_fuel_disagg'], sd_cont['ss_fuel_disagg'], sd_cont['is_fuel_disagg']])

    # Residential spatial explicit modelling
    rs_reg_share_service_tech_ey_p = calc_regional_services(
        rs_share_service_tech_ey_p,
        regions,
        spatial_diffusion_factor,
        sd_cont['rs_fuel_disagg'],
        techs_affected_spatial_f)

    # Generate sigmoid curves (s_generate_sigmoid) for every region
    ss_reg_share_service_tech_ey_p = calc_regional_services(
        ss_share_service_tech_ey_p,
        regions,
        spatial_diffusion_factor,
        sum_across_sectors_all_regs(sd_cont['ss_fuel_disagg']),
        techs_affected_spatial_f)

    is_reg_share_service_tech_ey_p = calc_regional_services(
        is_share_service_tech_ey_p,
        regions,
        spatial_diffusion_factor,
        sum_across_sectors_all_regs(sd_cont['is_fuel_disagg']),
        techs_affected_spatial_f)

    # -------------------------------
    # Calculate regional service shares of technologies for every technology
    # -------------------------------
    for enduse in fts_cont['rs_service_tech_by_p']:
        sgs_cont['rs_tech_increased_service'][enduse], sgs_cont['rs_tech_decreased_service'][enduse], sgs_cont['rs_tech_constant_service'][enduse], = s_generate_sigmoid.get_tech_future_service(
            fts_cont['rs_service_tech_by_p'][enduse],
            rs_reg_share_service_tech_ey_p[enduse],
            regions,
            True)

    for enduse in fts_cont['ss_service_tech_by_p']:
        sgs_cont['ss_tech_increased_service'][enduse], sgs_cont['ss_tech_decreased_service'][enduse], sgs_cont['ss_tech_constant_service'][enduse], = s_generate_sigmoid.get_tech_future_service(
            fts_cont['ss_service_tech_by_p'][enduse],
            ss_reg_share_service_tech_ey_p[enduse],
            regions,
            True)

    for enduse in fts_cont['is_service_tech_by_p']:
        sgs_cont['is_tech_increased_service'][enduse], sgs_cont['is_tech_decreased_service'][enduse], sgs_cont['is_tech_constant_service'][enduse], = s_generate_sigmoid.get_tech_future_service(
            fts_cont['is_service_tech_by_p'][enduse],
            is_reg_share_service_tech_ey_p[enduse],
            regions,
            True)
    
    return rs_reg_share_service_tech_ey_p, ss_reg_share_service_tech_ey_p, is_reg_share_service_tech_ey_p, sgs_cont
