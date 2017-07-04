"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import unittest
import numpy as np
import energy_demand.region as reg
import energy_demand.submodule_residential as submodule_residential
import energy_demand.submodule_service as submodule_service

ASSERTIONS = unittest.TestCase('__init__')

def model_main_function(data):
    """Main function of residential model

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally

    Returns
    -------
    energ_demand_object : object

    """
    fuel_in = test_function_fuel_sum(data) #SCRAP_ TEST FUEL SUM

    # Add all region instances as an attribute (region name) into the class `EnergyModel`
    energ_demand_object = EnergyModel(
        reg_names=data['lu_reg'],
        data=data
    )

    #print("READ OUT SPECIFIC ENDUSE FOR A REGION")
    #print(energ_demand_object.get_specific_enduse_region('Wales', 'rs_space_heating'))

    # ----------------------------
    fueltot = energ_demand_object.rs_tot_country_fuel # Total fuel of country
    #country_enduses = energ_demand_object.rs_tot_country_fuel_enduse_specific_h # Total fuel of country for each enduse

    print("Fuel input:          " + str(fuel_in))
    print("Fuel output:         " + str(fueltot))
    print("FUEL DIFFERENCE:     " + str(fueltot - fuel_in))
    print(" ")
    return energ_demand_object

class EnergyModel(object):
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

        # Create object for every region and add into list
        self.regions = self.create_regions(reg_names, data)

        # Generate different energy sub_models

        # --------------
        # Residential SubModel
        # --------------
        self.rs_submodel = self.residential_submodel(data, data['rs_all_enduses'])

        # --------------
        # Service SubModel
        # --------------
        self.ss_submodel = self.service_submodel(data, data['ss_all_enduses'], data['all_service_sectors'])
        print("EEEEEEEEEEEEEEEEERFOLGREICH")

        # ---------------------------------------------------------------------
        # Functions to summarise data for all Regions in the EnergyModel class

        self.rs_tot_country_fuel = self.get_overall_sum_regions(self.regions, 'rs_fuels_tot_enduses_h')

        self.rs_tot_country_fuel_enduse_specific_h = self.get_sum_for_each_enduse_h(data['rs_all_enduses'], self.regions, 'rs_fuels_new_enduse_specific_h') #yearly fuel
        self.ss_tot_country_fuel_enduse_specific_h = self.get_sum_for_each_enduse_h(data['ss_all_enduses'], self.regions, 'ss_fuels_new_enduse_specific_h') #yearly fuel

        self.rs_tot_country_fuel_load_max_h = self.peak_loads_per_fueltype(data, self.regions, 'rs_reg_load_factor_h')

        self.rs_tot_country_fuel_max_allenduse_fueltyp = self.peak_loads_per_fueltype(data, self.regions, 'rs_max_fuel_peak')
        self.ss_tot_country_fuel_max_allenduse_fueltyp = self.peak_loads_per_fueltype(data, self.regions, 'ss_max_fuel_peak')

        self.rs_tot_country_fuels_all_enduses = self.get_tot_fuels_all_enduses_yh(data, self.regions, 'rs_tot_fuels_all_enduses_yh')
        self.ss_tot_country_fuels_all_enduses = self.get_tot_fuels_all_enduses_yh(data, self.regions, 'ss_tot_fuels_all_enduses_yh')
        #print("AA: " + str(self.get_specific_enduse_region('Wales', 'rs_space_heating')))

        # TESTING
        ''''test_sum = 0
        for enduse in self.rs_tot_country_fuel_enduse_specific_h:
            test_sum += self.rs_tot_country_fuel_enduse_specific_h[enduse]
        np.testing.assert_almost_equal(np.sum(self.rs_tot_country_fuel), test_sum, decimal=5, err_msg='', verbose=True)
        '''

    def residential_submodel(self, data, enduses):
        """
        """
        rs_submodules = []

        for region_object in self.regions:
            for enduse in enduses:

                # Assumptions

                # Create submodule
                submodule = submodule_residential.ResidentialModel(data, region_object, enduse)

                rs_submodules.append(submodule)

        return rs_submodules

    def service_submodel(self, data, enduses, sectors):
        """
        """
        ss_submodules = []

        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = submodule_service.ServiceModel(data, region_object, enduse, sector)

                    ss_submodules.append(submodule)

        return ss_submodules

    def create_regions(self, reg_names, data):
        """Create all regions and add them as attributes based on region name to the EnergyModel Class

        Parameters
        ----------
        reg_names : list
            The name of the Region (unique identifier)
        """
        regions = []
        # Iterate all regions
        for reg_name in reg_names:

            # Generate region objects
            region_object = reg.Region(
                reg_name=reg_name,
                data=data
                )

            # Add regions to list
            regions.append(region_object)

        return regions

    def get_specific_enduse_region(self, spec_region, spec_enduse):
        """
        """
        reg_object = getattr(self, spec_region)
        enduse_fuels = reg_object.get_fuels_enduse_requested(spec_enduse)
        return enduse_fuels

    def get_overall_sum_regions(self, regions, attribute_to_get):
        """Collect hourly data from all regions and sum across all fuel types and enduses
        """
        tot_sum = 0
        for region in regions:

            # Get fuel data of region #Sum hourly demand # could also be read out as houly
            tot_sum += np.sum(getattr(region, attribute_to_get))

        return tot_sum

    def get_sum_for_each_enduse_h(self, enduses, regions, fuel_attribute_to_get):
        """Collect end_use specific hourly data from all regions and sum across all fuel types

        out: {enduse: sum(all_fuel_types)}

        """
        tot_sum_enduses = {}
        for enduse in enduses:
            tot_sum_enduses[enduse] = 0

        for region in regions:

            # Get fuel data of region
            enduse_fuels_reg = getattr(region, fuel_attribute_to_get)

            for enduse in enduse_fuels_reg:
                tot_sum_enduses[enduse] += np.sum(enduse_fuels_reg[enduse]) # sum across fuels

        return tot_sum_enduses

    def get_tot_fuels_all_enduses_yh(self, data, regions, attribute_to_get):
        """
        """

        tot_fuels_all_enduses = np.zeros(((data['nr_of_fueltypes'], 365, 24)))

        for reg_object in regions:
            tot_fuels = getattr(reg_object, attribute_to_get) # Get fuel data of region

            for fueltype, tot_fuel in enumerate(tot_fuels):
                tot_fuels_all_enduses[fueltype] += tot_fuel

        return tot_fuels_all_enduses

    def peak_loads_per_fueltype(self, data, regions, attribute_to_get):
        """Get peak loads for fueltype per maximum h
        """
        peak_loads_fueltype_max_h = np.zeros((data['nr_of_fueltypes']))

        for reg_object in regions:

            # Get fuel data of region
            load_max_h = getattr(reg_object, attribute_to_get)

            for fueltype, load_max_h in enumerate(load_max_h):
                peak_loads_fueltype_max_h[fueltype] += load_max_h

        return peak_loads_fueltype_max_h








# ------------- Testing functions
def test_function_fuel_sum(data):
    """ Sum raw disaggregated fuel data """
    fuel_in = 0
    for region in data['rs_fueldata_disagg']:
        for enduse in data['rs_fueldata_disagg'][region]:
            fuel_in += np.sum(data['rs_fueldata_disagg'][region][enduse])

    return fuel_in
