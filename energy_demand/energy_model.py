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
        data=data,
    )

    #print("READ OUT SPECIFIC ENDUSE FOR A REGION")
    #print(energ_demand_object.get_specific_enduse_region('Wales', 'rs_space_heating'))

    # ----------------------------
    fueltot = energ_demand_object.rs_tot_country_fuel # Total fuel of country

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
        self.curr_yr = data['curr_yr']

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




        # ---------------------------------------------------------------------
        # Functions to summarise data for all Regions in the EnergyModel class
        #  ---------------------------------------------------------------------

        #print("A: " + str(self.rs_tot_country_fuel + self.ss_tot_country_fuel))
        #self.rs_tot_country_fuel = self.get_overall_sum_regions_NEW('enduse_fuel_yh', data, [self.ss_submodel, self.rs_submodel], 'y')
        # DONE
        self.tot_country_fuel_enduse_specific_h = self.get_overall_sum_regions_NEW('enduse_fuel_yh', data, [self.ss_submodel, self.rs_submodel], 'y')


        self.rs_tot_country_fuel_enduse_specific_h = self.get_country_enduse('enduse_fuel_yh', data, [self.rs_submodel])
        self.ss_tot_country_fuel_enduse_specific_h = self.get_country_enduse('enduse_fuel_yh', data, [self.ss_submodel])
        #self.ss_tot_country_fuel_enduse_specific_h = self.get_overall_sum_regions_NEW('enduse_fuel_yh', data, [self.ss_submodel], 'yh')


        # SUMMARISE FOR EVERY REGION AND ENDSE
        #self.TODO = self.get_overall_sum_regions_NEW('enduse_fuel_yh', data, [self.ss_submodel, self.rs_submodel], 'y')

        #self.rs_tot_country_fuel_load_max_h = self.peak_loads_per_fueltype(data, self.regions, 'rs_reg_load_factor_h')

        self.rs_tot_country_fuel_max_allenduse_fueltyp = self.peak_loads_per_fueltype(data, self.regions, 'rs_max_fuel_peak')
        self.ss_tot_country_fuel_max_allenduse_fueltyp = self.peak_loads_per_fueltype(data, self.regions, 'ss_max_fuel_peak')

        self.rs_tot_country_fuels_all_enduses = self.get_overall_sum_regions_NEW('enduse_fuel_yh', data, [self.rs_submodel], 'yh')
        self.ss_tot_country_fuels_all_enduses = self.get_overall_sum_regions_NEW('enduse_fuel_yh', data, [self.ss_submodel], 'yh')

        # TESTING
        ''''test_sum = 0
        for enduse in self.rs_tot_country_fuel_enduse_specific_h:
            test_sum += self.rs_tot_country_fuel_enduse_specific_h[enduse]
        np.testing.assert_almost_equal(np.sum(self.rs_tot_country_fuel), test_sum, decimal=5, err_msg='', verbose=True)
        '''

    def residential_submodel(self, data, enduses):
        """Create the residential submodules
        """
        rs_submodules = []

        # Iterate regions and enduses
        for region_object in self.regions:
            for enduse in enduses:

                # Create submodule
                submodule = submodule_residential.ResidentialModel(data, region_object, enduse)

                # Add to list
                rs_submodules.append(submodule)

        return rs_submodules

    def service_submodel(self, data, enduses, sectors):
        """Create the service submodules
        """
        ss_submodules = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = submodule_service.ServiceModel(data, region_object, enduse, sector)

                    # Add to list
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

    def get_country_enduse(self, attribute_to_get, data, sector_models):

        enduse_dict = {}
        # Get sector models
        for sector_model_enduse in sector_models:
            # Iterate enduse
            for region_enduse_object in sector_model_enduse:

                if region_enduse_object.enduse_name not in enduse_dict:
                    enduse_dict[region_enduse_object.enduse_name] = 0

                enduse_dict[region_enduse_object.enduse_name] += np.sum(getattr(region_enduse_object.enduse_object, attribute_to_get))

        return enduse_dict

    def get_overall_sum_regions_NEW(self, attribute_to_get, data, sector_models, crit):
        """Collect hourly data from all regions and sum across all fuel types and enduses
        """
        tot_fuels_all_enduse = np.zeros((data['nr_of_fueltypes'], 365, 24))

        for sector_model in sector_models:
            for model_object in sector_model:
                    tot_fuels_all_enduse += getattr(model_object.enduse_object, attribute_to_get)
                    #tot_fuels_all_enduse += model_object.enduse_object.enduse_fuel_yh
        
        if crit == 'yh':
            tot_fuels_all_enduse = tot_fuels_all_enduse
        if crit == 'y':
            tot_fuels_all_enduse = np.sum(tot_fuels_all_enduse)

        return tot_fuels_all_enduse

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

    for region in data['ss_fueldata_disagg']:
        for sector in data['ss_fueldata_disagg'][region]:
            for enduse in data['ss_fueldata_disagg'][region][sector]:
                fuel_in += np.sum(data['ss_fueldata_disagg'][region][sector][enduse])

    return fuel_in
