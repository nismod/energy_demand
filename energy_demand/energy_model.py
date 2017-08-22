"""Energy Model
==============

The main function executing all the submodels of the energy demand model
"""
import uuid
import numpy as np
from energy_demand.geography import region
from energy_demand.geography import WeatherRegion
import energy_demand.rs_model as rs_model
import energy_demand.ss_model as ss_model
import energy_demand.is_model as is_model
import energy_demand.ts_model as ts_model
from energy_demand.profiles import load_factors as load_factors
from energy_demand.profiles import load_profile
from energy_demand.initalisations import helper_functions
from energy_demand.profiles import generic_shapes
'''# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member'''

class EnergyModel(object):
    """EnergyModel of a simulation yearly run

    Parameters
    ----------
    region_names : list
        Region names
    data : dict
        Main data dictionary

    Note
    ----
    - All submodels are executed here
    - All aggregation functions of the results are exectued here
    """
    def __init__(self, region_names, data):
        """Constructor
        """
        print("..start main energy demand function")
        self.curr_yr = data['sim_param']['curr_yr']

        # Non regional load profiles
        data['non_regional_profile_stock'] = self.create_load_profile_stock(data)

        # --------------------
        # Industry SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'is_submodel')
        self.regions = self.create_regions(
            region_names, data, 'is_submodel')
        self.is_submodel = self.industry_submodel(
            data, data['is_all_enduses'], data['is_sectors'])

        # --------------------
        # Residential SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'rs_submodel')
        self.regions = self.create_regions(
            region_names, data, 'rs_submodel')
        self.rs_submodel = self.residential_submodel(
            data, data['rs_all_enduses'])

        # --------------------
        # Service SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'ss_submodel')
        self.regions = self.create_regions(
            region_names, data, 'ss_submodel')
        self.ss_submodel = self.service_submodel(
            data, data['ss_all_enduses'], data['ss_sectors'])

        # --------------------
        # Transport SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'ts_submodel')
        self.regions = self.create_regions(
            region_names, data, 'ts_submodel')
        self.ts_submodel = self.other_submodels()

        # ---------------------------------------------------------------------
        # Functions to summarise data for all Regions in the EnergyModel class
        #  ---------------------------------------------------------------------
        print("...summarise fuel")
        # Sum according to weekend, working day

        # Sum across all regions, all enduse and sectors sum_reg
        self.sum_uk_fueltypes_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel], 'sum', 'non_peak')

        self.all_submodels_sum_uk_specfuelype_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel], 'no_sum', 'non_peak')
        self.rs_sum_uk_specfuelype_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'non_peak')
        self.ss_sum_uk_specfuelype_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'non_peak')
        self.is_sum_uk_specfuelype_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.is_submodel], 'no_sum', 'non_peak')
        self.ts_sum_uk_specfuelype_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.ts_submodel], 'no_sum', 'non_peak')

        self.rs_tot_fuels_all_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'non_peak')
        self.ss_tot_fuels_all_enduses_y = self.sum_reg('fuel_yh', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'non_peak')

        # Sum across all regions for enduse
        self.all_models_tot_fuel_y_enduse_specific_h = self.sum_enduse_all_regions('fuel_yh', [self.rs_submodel, self.ss_submodel, self.is_submodel, self.ts_submodel])

        self.rs_tot_fuel_y_enduse_specific_h = self.sum_enduse_all_regions('fuel_yh', [self.rs_submodel])
        self.ss_tot_fuel_enduse_specific_h = self.sum_enduse_all_regions('fuel_yh', [self.ss_submodel])


        # Sum across all regions, enduses for peak hour

        # NEW
        self.peak_all_models_all_enduses_fueltype = self.sum_reg('fuel_peak_dh', data['nr_of_fueltypes'], [self.rs_submodel, self.ss_submodel, self.is_submodel, self.ts_submodel], 'no_sum', 'peak_dh')

        self.rs_tot_fuel_y_max_allenduse_fueltyp = self.sum_reg('fuel_peak_h', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'peak_h')
        self.ss_tot_fuel_y_max_allenduse_fueltyp = self.sum_reg('fuel_peak_h', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'peak_h')

        # Functions for load calculations
        # ---------------------------
        self.rs_fuels_peak_h = self.sum_reg('fuel_peak_h', data['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'peak_h')
        self.ss_fuels_peak_h = self.sum_reg('fuel_peak_h', data['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'peak_h')

        # Across all enduses calc_load_factor_h
        self.rs_reg_load_factor_h = load_factors.calc_load_factor_h(data, self.rs_tot_fuels_all_enduses_y, self.rs_fuels_peak_h)
        self.ss_reg_load_factor_h = load_factors.calc_load_factor_h(data, self.ss_tot_fuels_all_enduses_y, self.ss_fuels_peak_h)

        # SUMMARISE FOR EVERY REGION AND ENDSE
        #self.tot_country_fuel_y_load_max_h = self.peak_loads_per_fueltype(data, self.regions, 'rs_reg_load_factor_h')

    @classmethod
    def create_load_profile_stock(cls, data):
        """Assign load profiles which are the same for all regions
        ``non_regional_load_profiles``

        Parameters
        ----------
        data : dict
            Data container

        Returns
        -------
        non_regional_profile_stock : object
            Load profile stock with non regional dependent load profiles
        """
        non_regional_profile_stock = load_profile.LoadProfileStock("non_regional_load_profiles")

        # Lighting (residential)
        non_regional_profile_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=data['assumptions']['technology_list']['rs_lighting'],
            enduses=['rs_lighting'],
            shape_yd=data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
            shape_yh=data['rs_shapes_dh']['rs_lighting']['shape_non_peak_y_dh'] * data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=data['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
            shape_peak_dh=data['rs_shapes_dh']['rs_lighting']['shape_peak_dh']
            )
        
        # RS_cold (residential refrigeration)
        non_regional_profile_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=data['assumptions']['technology_list']['rs_cold'],
            enduses=['rs_cold'],
            shape_yd=data['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'],
            shape_yh=data['rs_shapes_dh']['rs_cold']['shape_non_peak_y_dh'] * data['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=data['rs_shapes_yd']['rs_cold']['shape_peak_yd_factor'],
            shape_peak_dh=data['rs_shapes_dh']['rs_cold']['shape_peak_dh']
            )

        # -- dummy rs technologies (apply enduse sepcific shape)
        for enduse in data['assumptions']['rs_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['rs_fuel_tech_p_by'][enduse])
            non_regional_profile_stock.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=tech_list,
                enduses=[enduse],
                shape_yd=data['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                shape_yh=data['rs_shapes_dh'][enduse]['shape_non_peak_y_dh'] * data['rs_shapes_yd'][enduse]['shape_non_peak_yd'][:, np.newaxis],
                enduse_peak_yd_factor=data['rs_shapes_yd'][enduse]['shape_peak_yd_factor'],
                shape_peak_dh=data['rs_shapes_dh'][enduse]['shape_peak_dh']
                )

        # - dummy ss technologies
        for enduse in data['assumptions']['ss_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['ss_fuel_tech_p_by'][enduse])
            for sector in data['ss_sectors']:
                non_regional_profile_stock.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    sectors=[sector],
                    shape_yd=data['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=data['ss_shapes_dh'][sector][enduse]['shape_non_peak_y_dh'] * data['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    enduse_peak_yd_factor=data['ss_shapes_yd'][sector][enduse]['shape_peak_yd_factor'],
                    shape_peak_dh=data['ss_shapes_dh'][sector][enduse]['shape_peak_dh']
                    )

        # dummy is - Flat load profile
        shape_peak_dh, _, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh = generic_shapes.generic_flat_shape()

        for enduse in data['assumptions']['is_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['is_fuel_tech_p_by'][enduse])
            for sector in data['is_sectors']:
                non_regional_profile_stock.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    sectors=[sector],
                    shape_yd=shape_non_peak_yd,
                    shape_yh=shape_non_peak_yh,
                    enduse_peak_yd_factor=shape_peak_yd_factor,
                    shape_peak_dh=shape_peak_dh
                    )

        return non_regional_profile_stock

    def get_regional_yh(self, nr_of_fueltypes, region_name):
        """Get yh fuel for all fueltype for a specific region of all submodels

        Parameters
        ----------
        region_name : str
            Name of region to get attributes
        nr_of_fueltypes : int
            Number of fueltypes

        Return
        ------
        region_fuel_yh : array
            Summed fuel of a region

        Note
        ----
        - Summing function
        """
        region_fuel_yh = self.sum_reg(
            'fuel_yh',
            nr_of_fueltypes,
            [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel],
            'no_sum',
            'non_peak',
            region_name,
            )

        return region_fuel_yh

    def get_fuel_region_all_models_yh(self, nr_of_fueltypes, region_name_to_get, sector_models, attribute_to_get):
        """Summarise fuel yh for a certain region

        Parameters
        ----------
        nr_of_fueltypes : int
            Number of fueltypes
        region_name_to_get : str
            Name of region to read out
        sector_models : list
            Objectos of submodel runs
        attribute_to_get : str
            Attribute to get

        Note
        ----
        - Summing function
        """
        tot_fuels_all_enduse_yh = np.zeros((nr_of_fueltypes, 365, 24))

        for sector_model in sector_models:
            sector_model_objects = getattr(self, sector_model)
            for model_object in sector_model_objects:
                if model_object.region_name == region_name_to_get:
                    tot_fuels_all_enduse_yh += self.get_fuels_yh(model_object, attribute_to_get)

        return tot_fuels_all_enduse_yh

    def other_submodels(self):
        """Other submodel

        Return
        ------
        submodules : list
            Submodule objects

        Note
        ----
        - The ``regions`` and ``weather_regions`` gets deleted to save memory
        """
        #print("..other submodel start")
        #_scrap_cnt = 0
        submodules = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:

            # Create submodule
            submodule = ts_model.OtherModel(
                region_object,
                'generic_transport_enduse'
            )

            # Add to list
            submodules.append(submodule)

            #_scrap_cnt += 1
            #print("   ...running other submodel {}   of total: {}".format(_scrap_cnt, len(self.regions)))

        del self.regions, self.weather_regions
        print("...finished other submodel")
        return submodules

    def industry_submodel(self, data, enduses, sectors):
        """Industry subsector model

        Parameters
        ----------
        data : dict
            Data containter
        enduses : list
            Enduses of industry submodel
        sectors : list
            Sectors of industry submodel

        Return
        ------
        submodules : list
            Submodule objects

        Note
        ----
        - The ``regions`` and ``weather_regions`` gets deleted to save memory
        """
        print("..industry submodel start")
        #_scrap_cnt = 0
        submodules = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = is_model.IndustryModel(
                        data,
                        region_object,
                        enduse,
                        sector=sector
                        )

                    # Add to list
                    submodules.append(submodule)

                    #_scrap_cnt += 1
                    #print("   ...running industry model {} in % {} ".format(data['sim_param']['curr_yr'], 100 / (len(self.regions) * len(sectors) * len(enduses)) *_scrap_cnt))

        del self.regions, self.weather_regions

        return submodules

    def residential_submodel(self, data, enduses, sectors=['dummy_sector']):
        """Create the residential submodules (per enduse and region) and add them to list

        Parameters
        ----------
        data : dict
            Data container
        enduses : list
            All residential enduses
        sectors : dict, default=['dummy_sector']
            Sectors

        Returns
        -------
        submodule_list : list
            List with submodules

        Note
        ----
        - The ``regions`` and ``weather_regions`` gets deleted to save memory
        """
        print("..residential submodel start")
        #_scrap_cnt = 0
        submodule_list = []

        # Iterate regions and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodel_object = rs_model.ResidentialModel(
                        data,
                        region_object,
                        enduse,
                        sector
                        )

                    submodule_list.append(submodel_object)

                    #_scrap_cnt += 1
                    #print("   ...running residential model {} {}  of total".format(data['sim_param']['curr_yr'], 100.0 / (len(self.regions) * len(sectors) * len(enduses)) * _scrap_cnt))

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

        Note
        ----
        - The ``regions`` and ``weather_regions`` gets deleted to save memory
        """
        print("..service submodel start")
        _scrap_cnt = 0
        submodule_list = []

        # Iterate regions, sectors and enduses
        for region_object in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = ss_model.ServiceModel(
                        data,
                        region_object,
                        enduse,
                        sector
                        )

                    # Add to list
                    submodule_list.append(submodule)

                    _scrap_cnt += 1
                    print("   ...running service model {}  {}".format(data['sim_param']['curr_yr'], 100.0 / (len(self.regions) * len(sectors) * len(enduses)) * _scrap_cnt))

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
        region_names : list
            Regions
        data : dict
            Data container
        submodel_type : str
            Type of submodel [rs_submodel, ss_submodel, ...]
        """
        regions = []

        # Iterate all regions
        for region_name in region_names:
            print("...creating region: '{}'  {}".format(region_name, submodel_type))
            # Generate region object
            region_object = region.Region(
                region_name=region_name,
                data=data,
                submodel_type=submodel_type,
                weather_regions=self.weather_regions
                )

            # Add region to list
            regions.append(region_object)

        return regions

    def sum_enduse_all_regions(self, attribute_to_get, sector_models):
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

        for sector_model in sector_models:
            for model_object in sector_model:

                if model_object.enduse not in enduse_dict:
                    enduse_dict[model_object.enduse] = 0

                # Add fuel with flat load shape
                enduse_dict[model_object.enduse] += self.get_fuels_yh(
                    model_object, attribute_to_get)

        return enduse_dict

    def sum_reg(self, attribute_to_get, nr_of_fueltypes, sector_models, crit, crit2, region_name=False):
        """Collect hourly data from all regions and sum across all fuel types and enduses

        Parameters
        ----------
        attribute_to_get : str
            Attribue to summarise
        nr_of_fueltypes : int
            Number of fueltypes
        sector_models : list
            Sector models to summarise
        crit : str
            Criteria
        crit2 : str
        Criteria
        region_name : str
            Name of region

        Returns
        -------
        fuels : array
            Summarised fuels
        """
        if crit2 == 'peak_h':
            fuels = np.zeros((nr_of_fueltypes, ))
        elif crit2 == 'non_peak':
            fuels = np.zeros((nr_of_fueltypes, 365, 24))
        elif crit2 == 'peak_dh':
            fuels = np.zeros((nr_of_fueltypes, 24))

        # Iterate all submodel
        for sector_model in sector_models:
            for model_object in sector_model:

                # Select specific region
                if region_name:
                    if model_object.region_name == region_name:
                        fuels += self.get_fuels_yh(model_object, attribute_to_get)
                else:
                    fuels += self.get_fuels_yh(model_object, attribute_to_get)

        # Criteria if fuel is summed or not
        if crit == 'no_sum':
            fuels = fuels
        elif crit == 'sum':
            fuels = np.sum(fuels)

        return fuels

    def get_fuels_yh(self, model_object, attribute_to_get):
        """Assign yh shape for enduses with flat load profiles

        Parameters
        ----------
        model_object : dict
            Object of submodel run
        attribute_to_get : str
            Attribute to read out

        Returns
        -------
        fuels : array
            Fuels with flat load profile

        Note
        -----
        -   For enduses where 'crit_flat_profile' in Enduse Class is True
            a flat load profile is generated. Otherwise, the yh as calculated
            for each enduse is used
        """
        if model_object.enduse_object.crit_flat_profile:

            # Yearly fuel
            fuels_reg_y = model_object.enduse_object.fuel_y

            if attribute_to_get == 'fuel_peak_dh':
                # Flat shape
                shape_peak_dh = np.full((24), 1/24)

                # Because flat shape, the dh_peak is 24/8760
                fuels_reg_peak = fuels_reg_y * (1/365)

                fuels = fuels_reg_peak[:, np.newaxis] * shape_peak_dh

            elif attribute_to_get == 'shape_non_peak_y_dh':
                # Flat shape
                shape_non_peak_y_dh = np.full((365, 24), (1.0/24))
                fuels = fuels_reg_y * shape_non_peak_y_dh

            elif attribute_to_get == 'shape_non_peak_yd':
                # Flat shape
                shape_non_peak_yd = np.ones((365)) / 365
                fuels = fuels_reg_y * shape_non_peak_yd

            elif attribute_to_get == 'fuel_yh':
                # Flat shape
                shape_non_peak_yh = np.full((365, 24), 1/8760)
                fast_shape_non_peak_yh = np.zeros((model_object.enduse_object.fuel_new_y.shape[0], 365, 24))

                for fueltype, _ in enumerate(fast_shape_non_peak_yh):
                    fast_shape_non_peak_yh[fueltype] = shape_non_peak_yh

                fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * fast_shape_non_peak_yh
        else:
            # If not flat shape, use yh load profile of enduse
            fuels = getattr(model_object.enduse_object, attribute_to_get)

        return fuels
