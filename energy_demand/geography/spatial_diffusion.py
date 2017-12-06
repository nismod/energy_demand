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
    """
    spatial_index = defaultdict(dict)

    for enduse in enduses:
        dummy_indeces = [1.4, 2]
        cnt = 0
        for region in regions:

            #dummy_index = 1 #TODO
            dummy_index = dummy_indeces[cnt] #TODO

            spatial_index[enduse][region] = dummy_index
            cnt += 1

    return dict(spatial_index)

def calc_diff_factor(regions, spatial_diffusion_index, fuels):
    """Calculate factor for every region to calculate
    energy demand to be reduced for every region

    Multiply index with % of total ed demand of region
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
                print("enduse {}  reg {}  fuel {}".format(enduse, reg, np.sum(fuel_submodel[reg][enduse])))
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
        service,
        uk_service_p,
        regions,
        spatial_factors,
        fuel_disaggregated,
        technologies
    ):
    """Calculate regional service_tech_ey_p

    Arguments
    =========
    
    # Calculation national end use service to reduce : e.g. 40 % hp of uk --> service of heat pumps in ey?
    
    # Distribute this service according to spatial index

    # Convert regional service reduction to ey % in region

    """
    reg_service_tech_p = {}
    for enduse, techs_service_p in uk_service_p.items():
        reg_service_tech_p[enduse] = {}

        # Calculate national total enduse fuel
        uk_enduse_fuel = 0
        for region in regions:
            reg_service_tech_p[enduse][region] = {}
            print("FUEL " + str(np.sum(fuel_disaggregated[region][enduse])))
            uk_enduse_fuel += np.sum(fuel_disaggregated[region][enduse])
        
        uk_service_enduse = 0
        for fueltype in service[enduse]:
            uk_service_enduse += sum(service[enduse][fueltype].values())
        print(uk_service_enduse)
        print("uk_service_enduse: " + str(uk_service_enduse))

        _servicesum = 0
        for region in regions:
            print("============== Region " + str(region))
            print(np.sum(fuel_disaggregated[region][enduse]))
            # Calculate fraction of regional service
            reg_diagg_f = np.sum(fuel_disaggregated[region][enduse]) / uk_enduse_fuel
            print("reg_diagg_f: + " + str(reg_diagg_f))
           
            _sum_p_region = 0
            
            for tech, tech_service_ey_p in techs_service_p.items():
                print("----tech  " + str(tech))

                # Calculate national enduse of technology
                tech_fueltype = technologies[tech].fuel_type_int

                #old
                #uk_service_tech = service[enduse][tech_fueltype][tech] * tech_service_ey_p

                uk_service_tech = tech_service_ey_p * uk_service_enduse

                # Distribute the service to reduce according to spatial factor
                reg_service_enduse = uk_service_enduse * reg_diagg_f
                print("reg_service_enduse: " + str(reg_service_enduse))

                # Calculate regional service for technology
                if tech == 'heat_pumps_electricity':
                    #TODO ONLY FOR HEAT PUMP SPECIAL
                    reg_service_tech = uk_service_tech * spatial_factors[enduse][region] #* reg_diagg_f
                else:
                    reg_service_tech = uk_service_tech * 1

                
                #print(" =====reg_service_tech_spatial: " + str(reg_service_tech))
                
                # Calculate fraction of tech
                if reg_service_tech == 0:
                    reg_service_tech_p[enduse][region][tech] = 0
                else:
                    reg_service_tech_p[enduse][region][tech] = reg_service_tech #/ reg_service_enduse

                    _sum_p_region += reg_service_tech / reg_service_enduse

                #print("_sum_p_region: " + str(_sum_p_region))
                _servicesum += reg_service_tech
                #print("_servicesum_dd: " + str(_servicesum))

            # Normalise in region
            tot_service_reg_enduse = sum(reg_service_tech_p[enduse][region].values())
            for tech, service_tech in reg_service_tech_p[enduse][region].items():
                reg_service_tech_p[enduse][region][tech] = service_tech / tot_service_reg_enduse

            print("==============================")
            print("TOT REGIONA:     " + str(tot_service_reg_enduse))

        print("_servicesum final: " + str(_servicesum))
    #TODO: WHY GAS BOILER SO HIGH
    return reg_service_tech_p
