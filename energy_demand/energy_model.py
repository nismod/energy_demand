"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import numpy as np
import uuid
import energy_demand.Region as Region
import energy_demand.WeatherRegion as WeatherRegion
import energy_demand.submodule_residential as submodule_residential
import energy_demand.submodule_service as submodule_service
import energy_demand.submodule_industry as submodule_industry
import energy_demand.submodule_transport as submodule_transport
from energy_demand.scripts_shape_handling import load_factors as load_factors
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_initalisations import helper_functions

class EnergyModel(object):
    """Class of a country containing all regions as self.attributes

    The main class of the residential model. For every region, a Region object needs to be generated.

    Parameters
    ----------
    regions : list
        Dictionary containign the name of the Region (unique identifier)
    data : dict
        Main data dictionary

    Notes
    -----
    this class has as many attributes as regions (for evry rgion an attribute)
    """
    def __init__(self, region_names, data):
        """Constructor of the class which holds all regions of a country
        """
        print("..start main energy demand function")
        self.curr_yr = data['base_sim_param']['curr_yr']

        # Non regional load profiles
        data['load_profile_stock_non_regional'] = self.create_load_profile_stock(data)

        # --------------------
        # Residential SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(data['weather_stations'], data, 'rs_submodel')
        self.regions = self.create_regions(region_names, data, 'rs_submodel')
        self.rs_submodel = self.residential_submodel(data, data['rs_all_enduses'], data['rs_sectors'])

        # --------------------
        # Service SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(data['weather_stations'], data, 'ss_submodel')
        self.regions = self.create_regions(region_names, data, 'ss_submodel')
        self.ss_submodel = self.service_submodel(data, data['ss_all_enduses'], data['ss_sectors'])

        # --------------------
        # Industry SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(data['weather_stations'], data, 'is_submodel')
        self.regions = self.create_regions(region_names, data, 'is_submodel')
        self.is_submodel = self.industry_submodel(data, data['is_all_enduses'], data['is_sectors'])

        # --------------------
        # Transport SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(data['weather_stations'], data, 'ts_submodel')
        self.regions = self.create_regions(region_names, data, 'ts_submodel')
        self.ts_submodel = self.other_submodels()

        # ---------------------------------------------------------------------
        # Functions to summarise data for all Regions in the EnergyModel class
        #  ---------------------------------------------------------------------
        # Sum according to weekend, working day

        # Sum across all regions, all enduse and sectors
        self.sum_uk_fueltypes_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel], 'sum', 'non_peak')

        self.all_submodels_sum_uk_specfuelype_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel], 'no_sum', 'non_peak')
        self.rs_sum_uk_specfuelype_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'non_peak')
        self.ss_sum_uk_specfuelype_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'non_peak')
        self.is_sum_uk_specfuelype_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.is_submodel], 'no_sum', 'non_peak')
        self.ts_sum_uk_specfuelype_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.ts_submodel], 'no_sum', 'non_peak')

        self.rs_tot_fuels_all_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'non_peak')
        self.ss_tot_fuels_all_enduses_y = self.sum_regions('enduse_fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'non_peak')

        # Sum across all regions for enduse
        self.all_models_tot_fuel_y_enduse_specific_h = self.sum_enduse_all_regions('enduse_fuel_yh', [self.rs_submodel, self.ss_submodel, self.is_submodel, self.ts_submodel])

        self.rs_tot_fuel_y_enduse_specific_h = self.sum_enduse_all_regions('enduse_fuel_yh', [self.rs_submodel])
        self.ss_tot_fuel_enduse_specific_h = self.sum_enduse_all_regions('enduse_fuel_yh', [self.ss_submodel])


        # Sum across all regions, enduses for peak hour

        # NEW
        self.peak_all_models_all_enduses_fueltype = self.sum_regions('enduse_fuel_peak_dh', data['nr_of_fueltypes'], [self.rs_submodel, self.ss_submodel, self.is_submodel, self.ts_submodel], 'no_sum', 'peak_dh')
        print("......PEAK SUMMING")
        print(np.sum(self.peak_all_models_all_enduses_fueltype[2]))

        self.rs_tot_fuel_y_max_allenduse_fueltyp = self.sum_regions('enduse_fuel_peak_h', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'peak_h')
        self.ss_tot_fuel_y_max_allenduse_fueltyp = self.sum_regions('enduse_fuel_peak_h', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'peak_h')

        # Functions for load calculations
        # ---------------------------
        self.rs_fuels_peak_h = self.sum_regions('enduse_fuel_peak_h', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'peak_h')
        self.ss_fuels_peak_h = self.sum_regions('enduse_fuel_peak_h', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'peak_h')

        # Across all enduses calc_load_factor_h
        self.rs_reg_load_factor_h = load_factors.calc_load_factor_h(data, self.rs_tot_fuels_all_enduses_y, self.rs_fuels_peak_h)
        self.ss_reg_load_factor_h = load_factors.calc_load_factor_h(data, self.ss_tot_fuels_all_enduses_y, self.ss_fuels_peak_h)

        # SUMMARISE FOR EVERY REGION AND ENDSE
        #self.tot_country_fuel_y_load_max_h = self.peak_loads_per_fueltype(data, self.regions, 'rs_reg_load_factor_h')

    def create_load_profile_stock(self, data):
        """Assign load profiles which are the same for all regions to profile stock

        Parameters
        ----------
        data : dict
            Data

        Returns
        -------
        """

        # Generate stock
        load_profile_stock_non_regional = shape_handling.LoadProfileStock("non_regional_load_profiles")

        # Lighting (residential)
        load_profile_stock_non_regional.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=data['assumptions']['technology_list']['rs_lighting'],
            enduses=['rs_lighting'],
            sectors=data['rs_sectors'],
            shape_yd=data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
            shape_yh=data['rs_shapes_dh']['rs_lighting']['shape_non_peak_dh'] * data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=data['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
            shape_peak_dh=data['rs_shapes_dh']['rs_lighting']['shape_peak_dh']
            )

        # -- dummy rs technologies
        for enduse in data['assumptions']['rs_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['rs_fuel_enduse_tech_p_by'][enduse])

            load_profile_stock_non_regional.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=tech_list,
                enduses=[enduse],
                sectors=data['rs_sectors'],
                shape_yd=data['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                shape_yh=data['rs_shapes_dh'][enduse]['shape_non_peak_dh'] * data['rs_shapes_yd'][enduse]['shape_non_peak_yd'][:, np.newaxis],
                enduse_peak_yd_factor=data['rs_shapes_yd'][enduse]['shape_peak_yd_factor'], ##TEST WHY ADD FRACTION. Improve that daily fraction read in and not needs to be calculated here * (1 / (365)), 
                shape_peak_dh=data['rs_shapes_dh'][enduse]['shape_peak_dh']
                )

        # - dummy is technologies
        for enduse in data['assumptions']['ss_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['ss_fuel_enduse_tech_p_by'][enduse])
            for sector in data['ss_sectors']:
                load_profile_stock_non_regional.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    sectors=[sector],
                    shape_yd=data['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=data['ss_shapes_dh'][sector][enduse]['shape_non_peak_dh'] * data['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    enduse_peak_yd_factor=data['ss_shapes_yd'][sector][enduse]['shape_peak_yd_factor'], # * (1 / (365)), #TODO: CHECK
                    shape_peak_dh=data['ss_shapes_dh']#[sector][enduse]['shape_peak_dh']
                    )
        
        # TODO: REPLACE BY generic_flat_shape SWISS
        # dummy is
        for enduse in data['assumptions']['is_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['is_fuel_enduse_tech_p_by'][enduse])
            for sector in data['is_sectors']:
                load_profile_stock_non_regional.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    sectors=[sector],
                    shape_yd=data['is_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=data['is_shapes_dh'][sector][enduse]['shape_non_peak_dh'] * data['is_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    enduse_peak_yd_factor=data['is_shapes_yd'][sector][enduse]['shape_peak_yd_factor']  * (1 / (365)), #TODO: CHECK
                    shape_peak_dh=data['is_shapes_dh']#[sector][enduse]['shape_peak_dh']
                    )

        return load_profile_stock_non_regional

    def get_regional_yh(self, nr_of_fueltypes, region_name):
        """Get fuel for all fueltype for yh for specific region (all submodels)

        Parameters
        ----------
        region_name : str
            Name of region to get attributes
        attributes : str
            Attributes to read out
        """
        #Get fuel of region
        region_fuel_yh = self.sum_specific_region(
            region_name, #input region
            'enduse_fuel_yh',
            nr_of_fueltypes,
            [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel],
            'no_sum',
            'non_peak'
            )

        return region_fuel_yh

    def get_fuel_region_all_models_yh(self, data, region_name_to_get, sector_models, attribute_to_get):
        """Summarise fuel yh for a certain region
        """
        tot_fuels_all_enduse_yh = np.zeros((data['nr_of_fueltypes'], 365, 24))

        for sector_model in sector_models:
            sector_model_objects = getattr(self, sector_model)
            for model_object in sector_model_objects:
                if model_object.region_name == region_name_to_get:
                    tot_fuels_all_enduse_yh += getattr(model_object.enduse_object, attribute_to_get)

        return tot_fuels_all_enduse_yh

    def other_submodels(self):
        """Other submodel
        """
        print("..other submodel start")
        _scrap_cnt = 0
        submodule_list = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:

            # Create submodule
            submodule = submodule_transport.OtherModel(
                region_object,
                'generic_transport_enduse'
            )

            # Add to list
            submodule_list.append(submodule)

            _scrap_cnt += 1
            print("   ...running other submodel {}  of total: {}".format(_scrap_cnt, len(self.regions)))

        # To save on memory
        del self.regions, self.weather_regions

        return submodule_list

    def industry_submodel(self, data, enduses, sectors):
        """Industry subsector model
        """
        _scrap_cnt = 0
        print("..industry submodel start")
        submodule_list = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = submodule_industry.IndustryModel(
                        data,
                        region_object,
                        enduse,
                        sector=sector
                        )

                    # Add to list
                    submodule_list.append(submodule)

                    _scrap_cnt += 1
                    print("   ...running industry model {}  of total: {}".format(_scrap_cnt, len(self.regions) * len(sectors) * len(enduses)))

        # To save on memory
        del self.regions, self.weather_regions

        return submodule_list

    def residential_submodel(self, data, enduses, sectors):
        """Create the residential submodules (per enduse and region) and add them to list

        Parameters
        ----------
        data : dict
            Data container
        enduses : list
            All residential enduses

        Returns
        -------
        submodule_list : list
            List with submodules
        """
        print("..residential submodel start")
        _scrap_cnt = 0
        submodule_list = []

        # Iterate regions and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodel_object = submodule_residential.ResidentialModel(
                        data,
                        region_object,
                        enduse,
                        sector
                        )

                    submodule_list.append(submodel_object)

                    _scrap_cnt += 1
                    print("   ...running residential model {}  of total: {}".format(_scrap_cnt, len(self.regions) * len(sectors) * len(enduses)))

        # To save on memory
        del self.regions, self.weather_regions

        return submodule_list

    def service_submodel(self, data, enduses, sectors):
        """Create the service submodules per enduse, sector and region and add to list

        Parameters
        ----------
        data : dict
            Data container
        enduses : list
            All residential enduses
        sectors : list
            Service sectors

        Returns
        -------
        submodule_list : list
            List with submodules
        """
        print("..service submodel start")
        _scrap_cnt = 0
        submodule_list = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = submodule_service.ServiceModel(
                        data,
                        region_object,
                        enduse,
                        sector
                        )

                    # Add to list
                    submodule_list.append(submodule)

                    _scrap_cnt += 1
                    print("   ...running service model {}  of total: {}".format(_scrap_cnt, len(self.regions) * len(sectors) * len(enduses)))

        # To save on memory
        del self.regions, self.weather_regions

        return submodule_list

    @classmethod
    def create_weather_regions(cls, weather_regions, data, model_type):
        """Create all weather regions and calculate

        TODO:
        -stocks
        -load profiles

        Parameters
        ----------
        weather_region : list
            The name of the Weather Region
        """
        weather_region_objects = []

        for weather_region_name in weather_regions:

            region_object = WeatherRegion.WeatherRegion(
                weather_region_name=weather_region_name,
                data=data,
                modeltype=model_type
                )

            weather_region_objects.append(region_object)

        return weather_region_objects

    def create_regions(self, region_names, data, submodel_type):
        """Create all regions and add them in a list

        Parameters
        ----------
        regions : list
            The name of the Region (unique identifier)
        """
        regions = []

        # Iterate all regions
        for region_name in region_names:
            print("...creating region: '{}'  {}".format(region_name, submodel_type))
            # Generate region object
            region_object = Region.Region(
                region_name=region_name,
                data=data,
                submodel_type=submodel_type,
                weather_regions=self.weather_regions
                )

            # Add region to list
            regions.append(region_object)

        return regions

    @classmethod
    def sum_enduse_all_regions(cls, attribute_to_get, sector_models):
        """Summarise an enduse attribute across all regions

        Parameters
        ----------
        attribute_to_get : string
            Enduse attribute to summarise
        sector_models : List
            List with sector models

        Return
        ------
        enduse_dict : dict
            Summarise enduses across all regions
        """
        enduse_dict = {}

        for sector_model_enduse in sector_models: # Iterate sector models
            for region_enduse_object in sector_model_enduse: # Iterate enduse

                # Get regional enduse object
                if region_enduse_object.enduse not in enduse_dict:
                    enduse_dict[region_enduse_object.enduse] = 0

                # Summarise enduse attribute
                enduse_dict[region_enduse_object.enduse] += np.sum(getattr(region_enduse_object.enduse_object, attribute_to_get))

        return enduse_dict

    def sum_regions(self, attribute_to_get, nr_of_fueltypes, sector_models, crit, crit2):
        """Collect hourly data from all regions and sum across all fuel types and enduses

        Parameters
        ----------
        attribute_to_get :
        data

        Returns
        -------
        """
        if crit2 == 'peak_h':
            fuels = np.zeros((nr_of_fueltypes, ))
        if crit2 == 'non_peak':
            fuels = np.zeros((nr_of_fueltypes, 365, 24))
        if crit2 == 'peak_dh':
            fuels = np.zeros((nr_of_fueltypes, 24))

        for sector_model in sector_models:
            for model_object in sector_model:
                fuels += getattr(model_object.enduse_object, attribute_to_get)

        if crit == 'no_sum':
            fuels = fuels
        if crit == 'sum':
            fuels = np.sum(fuels)

        return fuels

    def sum_specific_region(self, region, attribute_to_get, nr_of_fueltypes, sector_models, crit, crit2):
        """Collect hourly data from all regions and sum across all fuel types and enduses

        Parameters
        ----------
        attribute_to_get :
        data

        Returns
        -------
        """
        if crit2 == 'peak_h':
            fuels = np.zeros((nr_of_fueltypes, ))
        if crit2 == 'non_peak':
            fuels = np.zeros((nr_of_fueltypes, 365, 24))
        if crit2 == 'peak_dh':
            fuels = np.zeros((nr_of_fueltypes, 24))

        for sector_model in sector_models:
            for model_object in sector_model:
                if model_object.region_name == region:
                    fuels += getattr(model_object.enduse_object, attribute_to_get)

        if crit == 'no_sum':
            fuels = fuels
        if crit == 'sum':
            fuels = np.sum(fuels)

        return fuels
