""" This File disaggregates total national demand """
import unittest
import numpy as np

import energy_demand.main_functions as mf

def disaggregate_base_demand_for_reg(data, reg_data_assump_disaggreg, data_ext):
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
    #TODO: So far simple disaggregation by population
    - floorarea
    - population
    - etc...abs
    TODO: Write disaggregation
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

    # TODO: USE HDD and COOLING DG DAYS to disaggregate regionaly 

    regions = data['reg_lu']
    base_year = data_ext['glob_var']['base_year']
    national_fuel = data['data_residential_by_fuel_end_uses']
    data['fueldata_disagg'] = {} #Initialise to store aggregated fuels
    #reg_data_assump_disaggreg = reg_data_assump_disaggreg

    # Sum national fuel before disaggregation for testing purposes
    test_sum_before = sum_fuels_before(national_fuel)

    # Calculate heating degree days in whole country
    hdd_total_country, hdd_individ_region = mf.get_hdd_country(regions, data)

    # Total heated days for all person sum of (person in very region * hdd per region)
    tot_hdd_popreg = 0
    for region in regions:
        reg_pop = data_ext['population'][base_year][region] # Regional popluation
        hdd_reg = hdd_individ_region[region]
        tot_hdd_popreg += reg_pop * hdd_reg
    print("tot_hdd_popreg:  " + str(tot_hdd_popreg))
    print(hdd_total_country * sum(data_ext['population'][base_year].values()))

    # Iterate regions
    for region in regions:

        #Scrap improve
        reg_pop = data_ext['population'][base_year][region] # Regional popluation
        total_pop = sum(data_ext['population'][base_year].values()) # Total population
        inter_dict = {} # Disaggregate fuel depending on end_use

        # Hdd of region
        hdd_reg = hdd_individ_region[region]
        print("Region-----------")
        print(total_pop)
        print(reg_pop)
        print("hdd_reg: " + str(hdd_reg))
        print("hdd_total_country: " + str(hdd_total_country))
        
        for enduse in national_fuel:

            if enduse == 'heating':
                # Use HDD and pop to disaggregat
                print("------")
                #print(reg_pop)
                print(total_pop)
                print((reg_pop * hdd_reg) / tot_hdd_popreg)
                print(reg_pop / total_pop )
                print("o")
                reg_diasg_factor = (reg_pop * hdd_reg) / tot_hdd_popreg

                #reg_diasg_factor = (reg_pop/total_pop) * (hdd_reg / hdd_total_country)
            else:
                # simply pop
                reg_diasg_factor = reg_pop / total_pop 
                #TODO: Get enduse_specific disaggreagtion reg_diasg_factor

            
            inter_dict[enduse] = national_fuel[enduse] * reg_diasg_factor

            #print("enduse: " + str(enduse))
            #print(reg_diasg_factor)
            #print(inter_dict[enduse])

        data['fueldata_disagg'][region] = inter_dict

    # Sum total fuel of all regions for testing purposes
    test_sum_after = sum_fuels_after(data['fueldata_disagg'])

    # Check if total fuel is the same before and after aggregation
    assertions = unittest.TestCase('__init__')
    assertions.assertAlmostEqual(test_sum_before, test_sum_after, places=2, msg=None, delta=None)

    return data



def read_in_all_disaggregation_parameters():
    # Read in table characterizing every region:

    # pop, floor area, households, etc.....

    pass
