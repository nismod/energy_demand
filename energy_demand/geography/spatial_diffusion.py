"""This file calculates spatial diffusion index

Method to incorporate regional diffusion
# -----------------------------------------

1.  As an input provide national fuel share which is to be switched (or capacity installed or fuel switch). As defined already

2.  Provide for every region a diffusion value (see excel)

3.  Calculate for every region a diffusion index (see excel)

4.  Normalised diffusion index with service fraction and multiply with total switched service of UK --> Regional service to switch (see excel)

5.  Calculate diffusion parameters for region

6.  Use regional diffusion parameters

"""

from collections import defaultdict
import numpy as np

def calc_diff_index(regions, enduses):
    """Load or calculate spatial index e.g. based on urban/rural population

    TODO: Maybe read in

    Arguments
    ---------
    regions
    enduses

    Returns
    -------
    spatial_index : dict
        Spatial index
    """
    spatial_index = defaultdict(dict)

    for enduse in enduses:
        dummy_indeces = [1.6, 2.5] #[2.8, 5.5] #[1.4, 2]
        cnt = 0
        for region in regions:

            #dummy_index = 1 #TODO
            dummy_index = dummy_indeces[cnt]

            spatial_index[enduse][region] = dummy_index
            cnt += 1

    return dict(spatial_index)

def calc_diff_factor(regions, spatial_diffusion_index, fuels):
    """Calculate factor for every region to calculate
    energy demand to be reduced for every region

    Multiply index with % of total ed demand of region

    Arguments
    ----------
    regions : dict
        Regions
    spatial_diffusion_index : dict
        Spatial diffusion index values Enduse, reg
    fuels : array
        Fuels per enduse
    """
    # Calculate fraction of energy demand of every region of total demand
    reg_enduse_p = {}
    fraction_p = {}

    for fuel_submodel in fuels:

        # -----------------------------------
        # If sectors, sum fuel across sectors
        # -----------------------------------
        fuel_submodel_new = {}
        for reg, entries in fuel_submodel.items():

            try:
                enduses = []
                fuel_submodel_new[reg] = {}
                for sector in entries:
                    for enduse in entries[sector]:
                        fuel_submodel_new[reg][enduse] = 0
                        enduses.append(enduse)
                    break

                for sector in entries:
                    for enduse in entries[sector]:
                        fuel_submodel_new[reg][enduse] += np.sum(entries[sector][enduse])

                fuel_submodel = fuel_submodel_new

            except IndexError:
                enduses = entries.keys()
                break

        # --------------------
        # Calculate % of enduse ed of a region of total enduse ed
        # --------------------
        for enduse in enduses:
            reg_enduse_p[enduse] = {}
            fraction_p[enduse] = {}

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
        # Multiply fraction of enduse with spatial_diffusion_index
        # ----------
        reg_fraction_multiplied_index = {}
        for enduse, regions_fuel_p in fraction_p.items():
            reg_fraction_multiplied_index[enduse] = {}
            for reg, fuel_p in regions_fuel_p.items():
                reg_fraction_multiplied_index[enduse][reg] = fuel_p * spatial_diffusion_index[enduse][reg]

    #-----------
    # Normalize
    #-----------
    for enduse in reg_fraction_multiplied_index:
        sum_enduse = sum(reg_fraction_multiplied_index[enduse].values())
        for reg in reg_fraction_multiplied_index[enduse]:
            reg_fraction_multiplied_index[enduse][reg] = reg_fraction_multiplied_index[enduse][reg] / sum_enduse

    # TEsting
    for enduse in reg_fraction_multiplied_index:
        np.testing.assert_almost_equal(sum(reg_fraction_multiplied_index[enduse].values()), 1, decimal=2)

    return reg_fraction_multiplied_index

def calc_regional_services(
        rs_service_by,
        uk_service_p,
        regions,
        spatial_factors,
        fuel_disaggregated,
        affected_techs
    ):
    """Calculate regional specific model end year service shares
    of technologies (service_tech_ey_p)

    Arguments
    =========
    affected_techs : list
        List where spatial diffusion is affected

    # Calculation national end use service to reduce : e.g. 40 % hp of uk --> service of heat pumps in ey?

    # Distribute this service according to spatial index

    # Convert regional service reduction to ey % in region

    # Note small differences might occur
    # because conversion from energy to service is the same
    # in every region because of heat pumps
    """
    reg_service_tech_p = defaultdict(dict)
    for enduse, uk_techs_service_p in uk_service_p.items():

        # ------------------------------------
        # Calculate national total enduse fuel and service
        # ------------------------------------
        uk_enduse_fuel = 0
        for region in regions:
            reg_service_tech_p[region][enduse] = {}
            uk_enduse_fuel += np.sum(fuel_disaggregated[region][enduse])

        #new 
        total_service_uk = 0
        for fueltypes in rs_service_by[enduse]:
            for tech in rs_service_by[enduse][fueltypes]:
                total_service_uk += np.sum(rs_service_by[enduse][fueltypes][tech])
        uk_service_enduse = total_service_uk
        #

        uk_service_enduse = uk_enduse_fuel

        for region in regions:
            #np.testing.assert_almost_equal(sum(uk_techs_service_p.values()), 1, 2)
            
            fuel_disagg_factor = np.sum(fuel_disaggregated[region][enduse]) / uk_enduse_fuel

            # Calculate fraction of regional service
            _scrap = 0
            _scrap2 = 0
            for tech, uk_tech_service_ey_p in uk_techs_service_p.items():
                print("tech: " + str(tech))
                uk_service_tech = uk_tech_service_ey_p * uk_service_enduse
                _scrap += uk_service_tech
                _scrap2 += uk_tech_service_ey_p
                # Calculate regional service for technology
                if tech in affected_techs:
                    reg_service_tech = uk_service_tech * spatial_factors[enduse][region]
                else:
                    # If not specified, use fuel disaggregation for enduse factor
                    reg_service_tech = uk_service_tech * fuel_disagg_factor

                # Calculate fraction of tech
                if reg_service_tech == 0:
                    reg_service_tech_p[region][enduse][tech] = 0
                else:
                    reg_service_tech_p[region][enduse][tech] = reg_service_tech

            # Normalise in region

            print(_scrap)
            print(_scrap2)
            tot_service_reg_enduse = sum(reg_service_tech_p[region][enduse].values())
            print("tot_service_reg_enduse: " + str(tot_service_reg_enduse))
            
            #tot_service_reg_enduse = fuel_disagg_factor
            for tech, service_tech in reg_service_tech_p[region][enduse].items():
                reg_service_tech_p[region][enduse][tech] = service_tech / tot_service_reg_enduse

    return reg_service_tech_p
