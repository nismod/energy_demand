"""Energy Model
==============

The main function executing all the submodels of the energy demand model
"""
import uuid
import logging
import numpy as np
from energy_demand.geography import region
from energy_demand.geography import WeatherRegion
import energy_demand.rs_model as rs_model
import energy_demand.ss_model as ss_model
import energy_demand.is_model as is_model
import energy_demand.ts_model as ts_model
from energy_demand.profiles import load_factors as load_factors
from energy_demand.profiles import load_profile
from energy_demand.initalisations import helpers
from energy_demand.profiles import generic_shapes
#pylint: disable=W1202

class EnergyModel(object):
    """EnergyModel of a simulation yearly run

    Arguments
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
        logging.debug("... start main energy demand function")
        self.curr_yr = data['sim_param']['curr_yr']

        # Non regional load profiles
        data['non_regional_lp_stock'] = self.create_load_profile_stock(
            data['tech_load_profiles'],
            data['assumptions'],
            data['sectors']
            )

        # --------------------
        # Industry SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'is_submodel')
        self.regions = self.create_regions(
            region_names, data, 'is_submodel')
        self.is_submodel = self.industry_submodel(
            data, data['enduses']['is_all_enduses'], data['sectors']['is_sectors'])

        # --------------------
        # Residential SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'rs_submodel')
        self.regions = self.create_regions(
            region_names, data, 'rs_submodel')
        self.rs_submodel = self.residential_submodel(
            data, data['enduses']['rs_all_enduses'])

        # --------------------
        # Service SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'ss_submodel')
        self.regions = self.create_regions(
            region_names, data, 'ss_submodel')
        self.ss_submodel = self.service_submodel(
            data, data['enduses']['ss_all_enduses'], data['sectors']['ss_sectors'])

        # --------------------
        # Transport SubModel
        # --------------------
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data, 'ts_submodel')
        self.regions = self.create_regions(
            region_names, data, 'ts_submodel')
        self.ts_submodel = self.other_submodels(data['assumptions']['nr_ed_modelled_dates'])

        # ---------------------------------------------------------------------
        # Summarise functions
        # ---------------------------------------------------------------------
        logging.debug("... start summing")
        all_submodels = [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel]

        # Sum across all regions, all enduse and sectors sum_reg
        self.fuel_indiv_regions_yh = self.fuel_regions_fueltype(data['lookups'], region_names, data['assumptions']['nr_ed_modelled_dates'])
        
        # Sum across all regions, all enduse and sectors
        self.reg_enduses_fueltype_y = self.fuel_aggr('fuel_yh', data['lookups']['nr_of_fueltypes'], all_submodels, 'no_sum', 'non_peak', data['assumptions']['nr_ed_modelled_dates'])
        
        # Sum across all regions for enduse
        self.tot_fuel_y_enduse_specific_h = self.sum_enduse_all_regions('fuel_yh', all_submodels, data['assumptions']['nr_ed_modelled_dates'])

        # Sum across all regions, enduses for peak hour
        self.tot_peak_enduses_fueltype = self.fuel_aggr('fuel_peak_dh', data['lookups']['nr_of_fueltypes'], all_submodels, 'no_sum', 'peak_dh', data['assumptions']['nr_ed_modelled_dates'])
        self.tot_fuel_y_max_allenduse_fueltyp = self.fuel_aggr('fuel_peak_h', data['lookups']['nr_of_fueltypes'], all_submodels, 'no_sum', 'peak_h', data['assumptions']['nr_ed_modelled_dates'])
        
        #-------------------
        # TESTING WHALE
        #-------------------
        print("FUEL FOR FIRST WEEK")
        hours_modelled = 7 * 24
        _sum_first_week = 0
        for fueltype, fuels in self.fuel_indiv_regions_yh.items():
            for region_fuel in fuels:
                print("a" + str(region_fuel.shape))
                _sum_first_week += region_fuel[:hours_modelled]
        
        print("_sum_first_week")
        print(np.sum(_sum_first_week))

        _sum_all = 0
        for fueltype, fuels in self.fuel_indiv_regions_yh.items():
            for region_fuel in fuels:
                _sum_all += np.sum(region_fuel)

        print("_sum_all: " + str(_sum_all))

        #-------------------

        # ---------------------------
        # Functions for load calculations
        # Across all enduses calc_load_factor_h
        # ---------------------------
        rs_fuels_peak_h = self.fuel_aggr('fuel_peak_h', data['lookups']['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'peak_h', data['assumptions']['nr_ed_modelled_dates'])
        ss_fuels_peak_h = self.fuel_aggr('fuel_peak_h', data['lookups']['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'peak_h', data['assumptions']['nr_ed_modelled_dates'])
        self.rs_tot_fuels_all_enduses_y = self.fuel_aggr('fuel_yh', data['lookups']['nr_of_fueltypes'], [self.rs_submodel], 'no_sum', 'non_peak', data['assumptions']['nr_ed_modelled_dates'])
        ss_tot_fuels_all_enduses_y = self.fuel_aggr('fuel_yh', data['lookups']['nr_of_fueltypes'], [self.ss_submodel], 'no_sum', 'non_peak', data['assumptions']['nr_ed_modelled_dates'])
        self.rs_reg_load_factor_h = load_factors.calc_load_factor_h(data, self.rs_tot_fuels_all_enduses_y, rs_fuels_peak_h)
        self.ss_reg_load_factor_h = load_factors.calc_load_factor_h(data, ss_tot_fuels_all_enduses_y, ss_fuels_peak_h)
        
    def fuel_regions_fueltype(self, lookups, region_names, nr_ed_modelled_dates):
        """Collect fuels for every fueltype and region (unconstrained mode). The
        regions are stored in an array for every timestep

        Arguments
        ---------
        lookups : dict
            Lookup container
        region_names : list
            All region names

        Example
        -------
        {'final_electricity_demand': np.array((regions, nr_ed_modelled_dates * 24)), dtype=float}
        """
        fuel_fueltype_regions = {}
        for fueltype, fueltype_nr in lookups['fueltype'].items():
            fuel_fueltype_regions[fueltype] = np.zeros((len(region_names), nr_ed_modelled_dates * 24), dtype=float)

            for array_region, region_name in enumerate(region_names):
                fuels = self.fuel_aggr(
                    'fuel_yh',
                    lookups['nr_of_fueltypes'],
                    [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel],
                    'no_sum',
                    'non_peak',
                    nr_ed_modelled_dates,
                    region_name
                    )
                # Reshape nr_ed_modelled_dates*24 to 8760
                fuel_fueltype_regions[fueltype][array_region] = fuels[fueltype_nr].reshape(nr_ed_modelled_dates * 24) #formerly 8760

        return fuel_fueltype_regions

    @classmethod
    def create_load_profile_stock(cls, tech_load_profiles, assumptions, sectors):
        """Assign load profiles which are the same for all regions
        ``non_regional_load_profiles``

        Arguments
        ----------
        tech_load_profiles : dict
            Load profiles
        assumptions : dict
            Assumptions
        sectors : dict
            Sectors

        Returns
        -------
        non_regional_lp_stock : object
            Load profile stock with non regional dependent load profiles
        """
        non_regional_lp_stock = load_profile.LoadProfileStock("non_regional_load_profiles")

        # Lighting (residential)
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_lighting'],
            enduses=['rs_lighting'],
            shape_yd=tech_load_profiles['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
            shape_yh=tech_load_profiles['rs_shapes_dh']['rs_lighting']['shape_non_peak_y_dh'] * tech_load_profiles['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_load_profiles['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
            shape_peak_dh=tech_load_profiles['rs_shapes_dh']['rs_lighting']['shape_peak_dh']
            )

        # rs_cold (residential refrigeration)
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_cold'],
            enduses=['rs_cold'],
            shape_yd=tech_load_profiles['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'],
            shape_yh=tech_load_profiles['rs_shapes_dh']['rs_cold']['shape_non_peak_y_dh'] * tech_load_profiles['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_load_profiles['rs_shapes_yd']['rs_cold']['shape_peak_yd_factor'],
            shape_peak_dh=tech_load_profiles['rs_shapes_dh']['rs_cold']['shape_peak_dh']
            )

        # rs_cooking
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_cooking'],
            enduses=['rs_cooking'],
            shape_yd=tech_load_profiles['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'],
            shape_yh=tech_load_profiles['rs_shapes_dh']['rs_cooking']['shape_non_peak_y_dh'] * tech_load_profiles['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_load_profiles['rs_shapes_yd']['rs_cooking']['shape_peak_yd_factor'],
            shape_peak_dh=tech_load_profiles['rs_shapes_dh']['rs_cooking']['shape_peak_dh']
            )

        # rs_wet
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_wet'],
            enduses=['rs_wet'],
            shape_yd=tech_load_profiles['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'],
            shape_yh=tech_load_profiles['rs_shapes_dh']['rs_wet']['shape_non_peak_y_dh'] * tech_load_profiles['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_load_profiles['rs_shapes_yd']['rs_wet']['shape_peak_yd_factor'],
            shape_peak_dh=tech_load_profiles['rs_shapes_dh']['rs_wet']['shape_peak_dh']
            )

        # -- dummy rs technologies (apply enduse sepcific shape)
        for enduse in assumptions['rs_dummy_enduses']:
            tech_list = helpers.get_nested_dict_key(assumptions['rs_fuel_tech_p_by'][enduse])
            non_regional_lp_stock.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=tech_list,
                enduses=[enduse],
                shape_yd=tech_load_profiles['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                shape_yh=tech_load_profiles['rs_shapes_dh'][enduse]['shape_non_peak_y_dh'] * tech_load_profiles['rs_shapes_yd'][enduse]['shape_non_peak_yd'][:, np.newaxis],
                enduse_peak_yd_factor=tech_load_profiles['rs_shapes_yd'][enduse]['shape_peak_yd_factor'],
                shape_peak_dh=tech_load_profiles['rs_shapes_dh'][enduse]['shape_peak_dh']
                )

        # - dummy ss technologies
        for enduse in assumptions['ss_dummy_enduses']:
            tech_list = helpers.get_nested_dict_key(assumptions['ss_fuel_tech_p_by'][enduse])
            for sector in sectors['ss_sectors']:
                non_regional_lp_stock.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=tech_load_profiles['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=tech_load_profiles['ss_shapes_dh'][sector][enduse]['shape_non_peak_y_dh'] * tech_load_profiles['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    sectors=[sector],
                    enduse_peak_yd_factor=tech_load_profiles['ss_shapes_yd'][sector][enduse]['shape_peak_yd_factor'],
                    shape_peak_dh=tech_load_profiles['ss_shapes_dh'][sector][enduse]['shape_peak_dh']
                    )

        # dummy is - Flat load profile
        shape_peak_dh, _, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh = generic_shapes.flat_shape(assumptions['nr_ed_modelled_dates'])

        for enduse in assumptions['is_dummy_enduses']:
            tech_list = helpers.get_nested_dict_key(assumptions['is_fuel_tech_p_by'][enduse])
            for sector in sectors['is_sectors']:
                non_regional_lp_stock.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=shape_non_peak_yd,
                    shape_yh=shape_non_peak_yh,
                    sectors=[sector],
                    enduse_peak_yd_factor=shape_peak_yd_factor,
                    shape_peak_dh=shape_peak_dh
                    )

        return non_regional_lp_stock

    def get_regional_yh(self, nr_of_fueltypes, region_name, nr_ed_modelled_dates):
        """Get yh fuel for all fueltype for a specific region of all submodels

        Arguments
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
        region_fuel_yh = self.fuel_aggr(
            'fuel_yh',
            nr_of_fueltypes,
            [self.ss_submodel, self.rs_submodel, self.is_submodel, self.ts_submodel],
            'no_sum',
            'non_peak',
            nr_ed_modelled_dates,
            region_name,
            )

        return region_fuel_yh

    '''def get_fuel_region_all_models_yh(self, nr_of_fueltypes, region_name_to_get, sector_models, attribute_to_get, nr_of_days):
        """Summarise fuel yh for a certain region

        Arguments
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
        tot_fuels_all_enduse_yh = np.zeros((nr_of_fueltypes, nr_of_days, 24)) #WHALE #assumptions['nr_ed_modelled_dates'] 
        
        for sector_model in sector_models:
            sector_model_objects = getattr(self, sector_model)
            for model_object in sector_model_objects:
                if model_object.region_name == region_name_to_get:
                    tot_fuels_all_enduse_yh += self.get_fuels_yh(model_object, attribute_to_get)

        return tot_fuels_all_enduse_yh
    '''

    def other_submodels(self, nr_ed_modelled_dates):
        """Other submodel

        Return
        ------
        submodules : list
            Submodule objects

        Note
        ----
        - The ``regions`` and ``weather_regions`` gets deleted to save memory
        """
        logging.debug("..other submodel start")
        submodules = []

        # Iterate regions, sectors and enduses
        for region_obj in self.regions:

            # Create submodule
            submodule = ts_model.OtherModel(
                region_obj,
                'generic_transport_enduse',
                nr_ed_modelled_dates
            )

            # Add to list
            submodules.append(submodule)

            #logging.debug("   ...running other submodel {}   of total: {}".format(_scrap_cnt, len(self.regions)))

        del self.regions, self.weather_regions
        logging.debug("... finished other submodel")
        return submodules

    def industry_submodel(self, data, enduses, sectors):
        """Industry subsector model

        Arguments
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
        logging.debug("... industry submodel start")
        _scrap_cnt = 0
        submodules = []

        # Iterate regions, sectors and enduses
        for region_obj in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = is_model.IndustryModel(
                        data,
                        region_obj,
                        enduse,
                        sector=sector
                        )

                    # Add to list
                    submodules.append(submodule)

                    _scrap_cnt += 1
                    logging.debug("   ...running industry model {} in % {} ".format(data['sim_param']['curr_yr'], 100 / (len(self.regions) * len(sectors) * len(enduses)) *_scrap_cnt))

        del self.regions, self.weather_regions

        return submodules

    def residential_submodel(self, data, enduses, sectors=['dummy_sector']):
        """Create the residential submodules (per enduse and region) and add them to list

        Arguments
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
        logging.debug("... residential submodel start")

        submodule_list = []

        # Iterate regions and enduses
        for region_obj in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodel_object = rs_model.ResidentialModel(
                        data,
                        region_obj,
                        enduse,
                        sector
                        )

                    submodule_list.append(submodel_object)

        del self.regions, self.weather_regions # To save on memory

        return submodule_list

    def service_submodel(self, data, enduses, sectors):
        """Create the service submodules per enduse, sector and region and add to list

        Arguments
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
        logging.debug("... service submodel start")
        _scrap_cnt = 0
        submodule_list = []

        # Iterate regions, sectors and enduses
        for region_obj in self.regions:
            for sector in sectors:
                for enduse in enduses:

                    # Create submodule
                    submodule = ss_model.ServiceModel(
                        data,
                        region_obj,
                        enduse,
                        sector
                        )

                    # Add to list
                    submodule_list.append(submodule)

                    _scrap_cnt += 1
                    logging.debug("   ...running service model {}  {}".format(data['sim_param']['curr_yr'], 100.0 / (len(self.regions) * len(sectors) * len(enduses)) * _scrap_cnt))

        # To save on memory
        del self.regions, self.weather_regions

        return submodule_list

    @classmethod
    def create_weather_regions(cls, weather_regions, data, model_type):
        """Create all weather regions and calculate

        Arguments
        ----------
        weather_region : list
            The name of the Weather Region
        data : dict
            Data container
        model_type : str
            Name of model ("e.g. rs_ or ss_)
        """
        weather_region_objs = []

        for weather_region_name in weather_regions:

            region_obj = WeatherRegion.WeatherRegion(
                weather_region_name=weather_region_name,
                sim_param=data['sim_param'],
                assumptions=data['assumptions'],
                lookups=data['lookups'],
                all_enduses=data['enduses'],
                temperature_data=data['temp_data'],
                tech_load_profiles=data['tech_load_profiles'],
                sectors=data['sectors'],
                modeltype=model_type
                )

            weather_region_objs.append(region_obj)

        return weather_region_objs

    def create_regions(self, region_names, data, submodel_type):
        """Create all regions and add them in a list

        Arguments
        ----------
        region_names : list
            Regions
        data : dict
            Data container
        submodel_type : str
            Type of submodel [rs_submodel, ss_submodel, ...]
        """
        regions = []

        for region_name in region_names:
            logging.debug("... creating region: '{}'  {}".format(region_name, submodel_type))

            region_obj = region.Region(
                region_name=region_name,
                data=data,
                submodel_type=submodel_type,
                weather_regions=self.weather_regions
                )

            regions.append(region_obj)

        return regions

    def sum_enduse_all_regions(self, attribute_to_get, sector_models, nr_ed_modelled_dates):
        """Summarise an enduse attribute across all regions

        Arguments
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
                    model_object, attribute_to_get, nr_ed_modelled_dates)

        return enduse_dict

    def fuel_aggr(self, attribute_to_get, nr_of_fueltypes, sector_models, sum_crit, lp_crit, nr_ed_modelled_dates, region_name=False):
        """Collect hourly data from all regions and sum across all fuel types and enduses

        Arguments
        ----------
        attribute_to_get : str
            Attribue to summarise
        nr_of_fueltypes : int
            Number of fueltypes
        sector_models : list
            Sector models to summarise
        lp_crit, sum_crit : str
            Criteria
        region_name : str
            Name of region

        Returns
        -------
        fuels : array
            Summarised fuels
        """
        if lp_crit == 'peak_h':
            fuels = np.zeros((nr_of_fueltypes))
        elif lp_crit == 'non_peak':
            fuels = np.zeros((nr_of_fueltypes, nr_ed_modelled_dates, 24))
        elif lp_crit == 'peak_dh':
            fuels = np.zeros((nr_of_fueltypes, 24))
        else:
            logging.error("Cannot properly sum, wrongly defined lp_crit : {}".format(lp_crit))

        for sector_model in sector_models:
            for model_object in sector_model:

                # Select specific region if defined
                if region_name:
                    if model_object.region_name == region_name:
                        fuels += self.get_fuels_yh(model_object, attribute_to_get, nr_ed_modelled_dates)
                else:
                    fuels += self.get_fuels_yh(model_object, attribute_to_get, nr_ed_modelled_dates)

        # Criteria if fuel is summed or not
        if sum_crit == 'no_sum':
            fuels = fuels
        elif sum_crit == 'sum':
            fuels = np.sum(fuels)

        return fuels

    @classmethod
    def get_fuels_yh(cls, model_object, attribute_to_get, nr_of_days):
        """Assign yh shape for enduses with flat load profiles

        Arguments
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
                shape_peak_dh = np.full((24), 1/24) # Flat shape
                # Because flat shape, the dh_peak is 24/8760
                fuels_reg_peak = fuels_reg_y * (1/365) #TEST
                fuels = fuels_reg_peak[:, np.newaxis] * shape_peak_dh

            elif attribute_to_get == 'fuel_peak_h':
                shape_peak_h = 1/8760 # Flat shape
                fuels = fuels_reg_y * shape_peak_h

            elif attribute_to_get == 'shape_non_peak_y_dh':
                shape_non_peak_y_dh = np.full((nr_of_days, 24), (1.0/24)) # Flat shape
                fuels = fuels_reg_y * shape_non_peak_y_dh

            elif attribute_to_get == 'shape_non_peak_yd':
                shape_non_peak_yd = np.ones((nr_of_days)) / nr_of_days # Flat shape
                fuels = fuels_reg_y * shape_non_peak_yd

            elif attribute_to_get == 'fuel_yh':
                shape_non_peak_yh = np.full((nr_of_days, 24), 1/(nr_of_days * 24)) # Flat shape
                fast_shape_non_peak_yh = np.zeros((model_object.enduse_object.fuel_new_y.shape[0], nr_of_days, 24))

                for fueltype, _ in enumerate(fast_shape_non_peak_yh):
                    fast_shape_non_peak_yh[fueltype] = shape_non_peak_yh

                fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * fast_shape_non_peak_yh
        else:
            # If not flat shape, use yh load profile of enduse
            #fuels = getattr(model_object.enduse_object, attribute_to_get)

            #SHARK: MAYBE FASTER
            if attribute_to_get == 'fuel_peak_dh':
                fuels = model_object.enduse_object.fuel_peak_dh
            elif attribute_to_get == 'fuel_peak_h':
                fuels = model_object.enduse_object.fuel_peak_h
            elif attribute_to_get == 'shape_non_peak_y_dh':
                fuels = model_object.enduse_object.shape_non_peak_y_dh
            elif attribute_to_get == 'shape_non_peak_yd':
                fuels = model_object.enduse_object.shape_non_peak_yd
            elif attribute_to_get == 'fuel_yh':
                fuels = model_object.enduse_object.fuel_yh

        return fuels
