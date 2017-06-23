""" This File disaggregates total national demand """
import unittest
import numpy as np
import energy_demand.main_functions as mf
ASSERTIONS = unittest.TestCase('__init__')

def disaggregate_reg_base_demand(data, reg_data_assump_disaggreg):
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

    # ------------------
    # SS Disaggregate all fuel across sector and enduses for service sector
    print("DISAGGREGATE SERVICE")

    data['ss_fueldata_disagg'] = ss_disaggregate(data, data['ss_fuel_raw_data_enduses'])
    # ------------------


    # ------------------
    # RS Disaggregateion #TODO: IMPROVE
    # ------------------
    regions = data['lu_reg']
    base_yr = data['base_yr']

    rs_national_fuel = data['rs_fuel_raw_data_enduses']


    #reg_data_assump_disaggreg = reg_data_assump_disaggreg



    data['rs_fueldata_disagg'] = {}
    # Sum national fuel before disaggregation for testing purposes
    test_sum_before = sum_fuels_before(rs_national_fuel)

    # Calculate heating degree days in whole country for base year
    hdd_individ_region = mf.get_hdd_country(regions, data)

    # Total heated days for all person sum of
    tot_hdd_popreg = 0
    for region in regions:
        reg_pop = data['population'][base_yr][region] # Regional popluation
        tot_hdd_popreg += reg_pop * hdd_individ_region[region]

    # Iterate regions
    for region in regions:
        reg_pop = data['population'][base_yr][region] # Regional popluation
        total_pop = sum(data['population'][base_yr].values()) # Total population
        hdd_reg = hdd_individ_region[region] # Hdd of region
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
    ASSERTIONS.assertAlmostEqual(test_sum_before, test_sum_after, places=2, msg=None, delta=None)

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
        for sector in data['all_service_sectors']:
            print("sector: " + str(sector))
            ss_fueldata_disagg[region][sector] = {}

            # Calculate total national floor area of this sector
            national_floorarea_sector = 0
            for regionLocal in data['lu_reg']:
                national_floorarea_sector += sum(data['ss_sector_floor_area_by'][region].values())
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

    for sector in data['all_service_sectors']:
        for enduse in data['ss_all_enduses']:
            control_sum2 += np.sum(raw_fuel_sectors_enduses[sector][enduse])

    ASSERTIONS.assertAlmostEqual(control_sum1, control_sum2, places=2, msg=None, delta=None) #The loaded floor area must correspond to provided fuel sectors numers

    return ss_fueldata_disagg
