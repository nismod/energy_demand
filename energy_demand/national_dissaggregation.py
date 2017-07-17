""" This File disaggregates total national demand """
import unittest
import numpy as np
from energy_demand.scripts_plotting import plotting_results
from energy_demand.scripts_shape_handling import hdd_cdd


'''
============================================
MEthod to derive GVA/POP SERVICE FLOOR AREAS
============================================

1. Step
Get correlation between regional GVA and (regional floor area/reg pop) of every sector of base year
-- Get this correlation for every region and build national correlation


2. Step
Calculate future regional floor area demand based on GVA and pop projection

'''

def disaggregate_base_demand(data):
    """This function disaggregates fuel demand based on region specific parameters
    for the base year

    The residential, service and industry demand is disaggregated according to
    different factors

    Parameters
    ----------
    data : dict
        Contains all data not provided externally
    reg_data_assump_disaggreg : reg_data_assump_disaggreg
        tbd

    Returns
    -------
    data : dict

    Notes
    -----
    - floorarea
    - population
    - etc...abs
     #TODO: Write disaggregation
    """
    def sum_fuels_before(fuel):
        """Inner function for testing purposes - sum fuel"""
        tot = 0
        for i in fuel:
            tot += np.sum(fuel[i])
        return tot

    def sum_fuels_after(reg_fuel):
        """Inner function for testing purposes - sum fuel"""
        tot = 0
        for reg in reg_fuel:
            for enduse in reg_fuel[reg]:
                tot += np.sum(reg_fuel[reg][enduse])
        return tot

    # TODO: COOLING DG DAYS to disaggregate regionaly
    regions = data['lu_reg']
    base_yr = data['base_yr']

    # SS Disaggregate all fuel across sector and enduses for service sector
    print("...disaggregate service demand")
    data['ss_fueldata_disagg'] = ss_disaggregate(data, data['ss_fuel_raw_data_enduses'])

    # ------------------
    # Disaggregate indusry data
    # ------------------
    data['is_fueldata_disagg'] = is_disaggregate(data, data['is_fuel_raw_data_enduses'])

    # TRANSPORTAIONT SCRAP
    from energy_demand.scripts_basic import unit_conversions
    fuel_national_tranport = np.zeros((data['nr_of_fueltypes']))
    fuel_national_tranport[2] = unit_conversions.convert_ktoe_gwh(385)  #Elec demand from ECUK for transport sector
    data['ts_fueldata_disagg'] = scrap_ts_disaggregate(data, fuel_national_tranport)

    # ------------------
    # RS Disaggregateion #TODO: IMPROVE
    # ------------------
    print("...disagreggate residential demand")

    rs_national_fuel = data['rs_fuel_raw_data_enduses']

    data['rs_fueldata_disagg'] = {}

    # Sum national fuel before disaggregation for testing purposes
    test_sum_before = sum_fuels_before(rs_national_fuel)

    # Calculate heating degree days in whole country for base year
    rs_hdd_individ_region = hdd_cdd.get_hdd_country(regions, data, 'rs_t_base_heating')

    # Total heated days for all person sum of
    tot_hdd_popreg = 0
    for region in regions:
        reg_pop = data['population'][base_yr][region] # Regional popluation
        tot_hdd_popreg += reg_pop * rs_hdd_individ_region[region]

    # Iterate regions
    for region in regions:
        reg_pop = data['population'][base_yr][region] # Regional popluation
        total_pop = sum(data['population'][base_yr].values()) # Total population
        hdd_reg = rs_hdd_individ_region[region] # Hdd of region
        inter_dict = {} # Disaggregate fuel depending on end_use

        #TODO: Improve specific disaggregation depending on enduse
        for enduse in rs_national_fuel:

            if enduse == 're_space_heating':
                # Use HDD and pop to disaggregat
                #print("------")
                #print(reg_pop)
                #print(total_pop)
                #print((reg_pop * hdd_reg) / tot_hdd_popreg)
                #print(reg_pop / total_pop )

                reg_diasg_factor = (reg_pop * hdd_reg) / tot_hdd_popreg

                #reg_diasg_factor = (reg_pop/total_pop) * (hdd_reg / hdd_total_country)
            else:
                # simply pop
                reg_diasg_factor = reg_pop / total_pop
                #TODO: Get enduse_specific disaggreagtion reg_diasg_factor

            inter_dict[enduse] = rs_national_fuel[enduse] * reg_diasg_factor

        data['rs_fueldata_disagg'][region] = inter_dict

    # Sum total fuel of all regions for testing purposes
    test_sum_after = sum_fuels_after(data['rs_fueldata_disagg'])

    # Check if total fuel is the same before and after aggregation
    np.testing.assert_almost_equal(test_sum_before, test_sum_after, decimal=2, err_msg="")
    return data

def ss_disaggregate(data, raw_fuel_sectors_enduses):
    """TODO: Disaggregate fuel for sector and enduses with floor area and GVA for sectors and enduses (IMPROVE)
    """

    ss_fueldata_disagg = {}

    #control_sum = 0
    #control_sum2 = 0

    # Iterate regions
    for region in data['lu_reg']:
        ss_fueldata_disagg[region] = {}
        print("Region: " + str(region))
        # Iterate sector
        for sector in data['ss_sectors']:
            print("sector: " + str(sector))
            ss_fueldata_disagg[region][sector] = {}

            # Calculate total national floor area of this sector
            national_floorarea_sector = 0
            for _reg in data['lu_reg']:
                national_floorarea_sector += sum(data['ss_sector_floor_area_by'][_reg].values())
            # Calculate total national GVA
            # todo national_GVA = 100

            # Sector specifid info
            regional_floorarea_sector = sum(data['ss_sector_floor_area_by'][region].values()) #get from Newcastl

            # Iterate enduse
            for enduse in data['ss_all_enduses']:
                national_fuel_sector_by = raw_fuel_sectors_enduses[sector][enduse]
                #control_sum2 += np.sum(national_fuel_sector_by)
                print("national_fuel_sector_by: " + str(national_fuel_sector_by))
                # ----------------------
                # Disaggregating factors
                # TODO: IMPROVE. SHOW HOW IS DISAGGREGATED
                # ----------------------
                if enduse == 'ss_space_heating':
                    reg_disaggregation_factor = (1 / national_floorarea_sector) * regional_floorarea_sector
                    #regional_GVA =
                else:
                    # TODO: USE DEPENDING ON ENDUSE OTHER FACTORS SUC HAS GVA OR SIMILAR
                    reg_disaggregation_factor = (1 / national_floorarea_sector) * regional_floorarea_sector
                    #regional_GVA

                print("reg_disaggregation_factor: " + str(reg_disaggregation_factor))
                print(national_floorarea_sector)

                # Disaggregated national fuel
                reg_fuel_sector_enduse = reg_disaggregation_factor * national_fuel_sector_by
                #control_sum += np.sum(reg_fuel_sector_enduse)

                ss_fueldata_disagg[region][sector][enduse] = reg_fuel_sector_enduse


    # TESTING Check if total fuel is the same before and after aggregation
    # ---------------
    control_sum1 = 0
    control_sum2 = 0
    for reg in ss_fueldata_disagg:
        for sector in ss_fueldata_disagg[reg]:
            for enduse in ss_fueldata_disagg[reg][sector]:
                control_sum1 += np.sum(ss_fueldata_disagg[reg][sector][enduse])

    for sector in data['ss_sectors']:
        for enduse in data['ss_all_enduses']:
            control_sum2 += np.sum(raw_fuel_sectors_enduses[sector][enduse])

    np.testing.assert_almost_equal(control_sum1, control_sum2, decimal=2, err_msg="") #The loaded floor area must correspond to provided fuel sectors numers
    return ss_fueldata_disagg

def scrap_ts_disaggregate(data, fuel_national):
    
    is_fueldata_disagg = {}

    national_floorarea_sector = 0
    for region in data['lu_reg']:
        national_floorarea_sector += sum(data['ss_sector_floor_area_by'][region].values())

    # Iterate regions
    for region in data['lu_reg']:
        is_fueldata_disagg[region] = {}

        regional_floorarea_sector = sum(data['ss_sector_floor_area_by'][region].values())
        
        national_fuel_sector_by = fuel_national

        reg_disaggregation_factor = (1 / national_floorarea_sector) * regional_floorarea_sector

        reg_fuel_sector_enduse = reg_disaggregation_factor * national_fuel_sector_by

        is_fueldata_disagg[region] = reg_fuel_sector_enduse

    return is_fueldata_disagg

def is_disaggregate(data, raw_fuel_sectors_enduses):
    """TODO: Disaggregate fuel for sector and enduses with floor area and GVA for sectors and enduses (IMPROVE)


    #TODO: DISAGGREGATE WITH OTHER DATA
    """
    is_fueldata_disagg = {}

    national_floorarea_sector = 0
    for region in data['lu_reg']:
        national_floorarea_sector += sum(data['ss_sector_floor_area_by'][region].values())

    # Iterate regions
    for region in data['lu_reg']:
        is_fueldata_disagg[region] = {}

        # Iterate sector
        for sector in data['is_sectors']:
            is_fueldata_disagg[region][sector] = {}


            # Sector specifid info
            regional_floorarea_sector = sum(data['ss_sector_floor_area_by'][region].values())
            # Iterate enduse
            for enduse in data['is_all_enduses']:
                national_fuel_sector_by = raw_fuel_sectors_enduses[sector][enduse]

                #print("national_fuel_sector_by: " + str(national_fuel_sector_by))
                # ----------------------
                # Disaggregating factors
                # TODO: IMPROVE. SHOW HOW IS DISAGGREGATED
                reg_disaggregation_factor = (1 / national_floorarea_sector) * regional_floorarea_sector

                # Disaggregated national fuel
                reg_fuel_sector_enduse = reg_disaggregation_factor * national_fuel_sector_by

                is_fueldata_disagg[region][sector][enduse] = reg_fuel_sector_enduse

    return is_fueldata_disagg
