"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
from datetime import date
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import energy_demand.regionClass as reg
import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
import energy_demand.technological_stock as ts
import unittest
assertions = unittest.TestCase('__init__')

def residential_model_main_function(data):
    """Main function of residential model

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally

    Returns
    -------
    resid_object : object
        Object containing all regions as attributes for the residential model
    """
    fuel_in = test_function_fuel_sum(data) #SCRAP_ TEST FUEL SUM

    # Add all region instances as an attribute (region name) into the class `CountryClass`
    resid_object = CountryClass(data['lu_reg'], data)

    #print("READ OUT SPECIFIC ENDUSE FOR A REGION")
    #print(resid_object.get_specific_enduse_region('Wales', 'resid_space_heating'))

    # ----------------------------
    # Attributes of whole country
    # ----------------------------
    fueltot = resid_object.tot_country_fuel # Total fuel of country
    #country_enduses = resid_object.tot_country_fuel_enduse_specific_h # Total fuel of country for each enduse

    print("Fuel input:          " + str(fuel_in))
    print("Fuel output:         " + str(fueltot))
    print("FUEL DIFFERENCE:     " + str(fueltot - fuel_in))
    print(" ")
    return resid_object

class CountryClass(object):
    """Class of a country containing all regions as self.attributes

    The main class of the residential model. For every region, a Region object needs to be generated.

    Parameters
    ----------
    reg_names : list
        Dictionary containign the name of the Region (unique identifier)
    data : dict
        Main data dictionary

    Notes
    -----
    this class has as many attributes as regions (for evry rgion an attribute)
    """
    def __init__(self, reg_names, data):
        """Constructor of the class which holds all regions of a country
        """
        # Create object for every region
        self.create_regions(reg_names, data)



        # Functions to summarise data for all Regions in the CountryClass class
        self.tot_country_fuel = self.get_overall_sum(reg_names)
        self.tot_country_fuel_enduse_specific_h = self.get_sum_for_each_enduse_h(data, reg_names) #yearly fuel
        self.tot_country_fuel_load_max_h = self.peak_loads_per_fueltype(data, reg_names, 'reg_load_factor_h')
        self.tot_country_fuel_max_allenduse_fueltyp = self.peak_loads_per_fueltype(data, reg_names, 'max_fuel_peak')
        self.tot_country_fuels_all_enduses = self.tot_fuels_all_enduses_yh(data, reg_names, 'tot_fuels_all_enduses_yh')
        #print("AA: " + str(self.get_specific_enduse_region('Wales', 'resid_space_heating')))

        # ----- Testing
        n = 0
        for i in self.tot_country_fuel_enduse_specific_h:
            n += self.tot_country_fuel_enduse_specific_h[i]
        #print("============================ddddddddddd= " + str(self.tot_country_fuel))

        # TESTING
        test_sum = 0
        for enduse in self.tot_country_fuel_enduse_specific_h:
            test_sum += self.tot_country_fuel_enduse_specific_h[enduse]
        np.testing.assert_almost_equal(np.sum(self.tot_country_fuel), test_sum, decimal=5, err_msg='', verbose=True)

    def create_regions(self, reg_names, data):
        """Create all regions and add them as attributes based on region name to the CountryClass Class

        Parameters
        ----------
        reg_names : list
            The name of the Region (unique identifier)
        """
        # Iterate all regions
        for reg_name in reg_names:

            # Set each region as an attribute of the CountryClass
            CountryClass.__setattr__(
                self,
                str(reg_name),
                reg.RegionClass(
                    reg_name,
                    data
                )
            )

        return

    def get_specific_enduse_region(self, spec_region, spec_enduse):
        """
        """
        reg_object = getattr(self, spec_region)
        enduse_fuels = reg_object.get_fuels_enduse_requested(spec_enduse)
        return enduse_fuels

    def get_overall_sum(self, reg_names):
        """Collect hourly data from all regions and sum across all fuel types and enduses
        """
        tot_sum = 0
        for reg_name in reg_names:
            reg_object = getattr(self, str(reg_name))

            # Get fuel data of region #Sum hourly demand # could also be read out as houly
            tot_sum += np.sum(getattr(reg_object, 'fuels_tot_enduses_h'))

        return tot_sum

    def get_sum_for_each_enduse_h(self, data, reg_names):
        """Collect end_use specific hourly data from all regions and sum across all fuel types

        out: {enduse: sum(all_fuel_types)}

        """
        tot_sum_enduses = {}
        for enduse in data['resid_enduses']:
            tot_sum_enduses[enduse] = 0

        for reg_name in reg_names:
            reg_object = getattr(self, str(reg_name)) # Get region

            # Get fuel data of region
            enduse_fuels_reg = getattr(reg_object, 'fuels_new_enduse_specific_h')

            for enduse in enduse_fuels_reg:
                tot_sum_enduses[enduse] += np.sum(enduse_fuels_reg[enduse]) # sum across fuels

        return tot_sum_enduses

    def tot_fuels_all_enduses_yh(self, data, reg_names, attribute_to_get):

        tot_fuels_all_enduses = np.zeros(((data['nr_of_fueltypes'], 365, 24)))

        for reg_name in reg_names:
            reg_object = getattr(self, str(reg_name))
            tot_fuels = getattr(reg_object, attribute_to_get) # Get fuel data of region

            for fueltype, tot_fuel in enumerate(tot_fuels):
                tot_fuels_all_enduses[fueltype] += tot_fuel

        return tot_fuels_all_enduses

    def peak_loads_per_fueltype(self, data, reg_names, attribute_to_get):
        """Get peak loads for fueltype per maximum h
        """
        peak_loads_fueltype_max_h = np.zeros((data['nr_of_fueltypes']))

        for reg_name in reg_names:
            reg_object = getattr(self, str(reg_name))

            # Get fuel data of region
            load_max_h = getattr(reg_object, attribute_to_get)

            for fueltype, load_max_h in enumerate(load_max_h):
                peak_loads_fueltype_max_h[fueltype] += load_max_h

        return peak_loads_fueltype_max_h








# ------------- Testing functions
def test_function_fuel_sum(data):
    """ Sum raw disaggregated fuel data """
    fuel_in = 0
    for reg in data['resid_fueldata_disagg']:
        for enduse in data['resid_fueldata_disagg'][reg]:
            fuel_in += np.sum(data['resid_fueldata_disagg'][reg][enduse])

    return fuel_in
