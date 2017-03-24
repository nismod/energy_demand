""" This File disaggregates total national demand """
import numpy as np
import unittest

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

    regions = data['reg_lu']
    base_year = data_ext['glob_var']['base_year']
    national_fuel = data['data_residential_by_fuel_end_uses']
    data['fueldata_disagg'] = {} #Initialise to store aggregated fuels
    #reg_data_assump_disaggreg = reg_data_assump_disaggreg

    # Sum national fuel before disaggregation for testing purposes
    test_sum_before = sum_fuels_before(national_fuel)

    # Iterate regions
    for region in regions:

        #Scrap improve
        reg_pop = data_ext['population'][base_year][region] # Regional popluation
        total_pop = sum(data_ext['population'][base_year].values()) # Total population
        inter_dict = {} # Disaggregate fuel depending on end_use

        # So far simply pop
        #TODO: create dict with disaggregation factors
        reg_diasg_factor = reg_pop / total_pop

        for enduse in national_fuel:
            #TODO: Get enduse_specific disaggreagtion reg_diasg_factor
            inter_dict[enduse] = national_fuel[enduse] * reg_diasg_factor

        data['fueldata_disagg'][region] = inter_dict

    # Sum total fuel of all regions for testing purposes
    test_sum_after = sum_fuels_after(data['fueldata_disagg'])

    # Check if total fuel is the same before and after aggregation
    assertions = unittest.TestCase('__init__')
    assertions.assertAlmostEqual(test_sum_before, test_sum_after, places=2, msg=None, delta=None)

    return data

# Initialise resulting array (Fuel_Type, reg, End_Use))

# Read in base demand for whole country for all appliances
def read_in_all_base_demands():
    
    # Store in array (fuel_type, End_use)

    pass

def read_in_all_disaggregation_parameters():
    # Read in table characterizing every region:

    # pop, floor area, households, etc.....

    pass

def disaggregate(region_characteristics, yearly_data):


    pass