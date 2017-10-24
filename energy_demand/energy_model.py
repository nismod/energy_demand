"""Energy Model
==============

The main function executing all the submodels of the energy demand model
"""
import uuid
import logging
from collections import defaultdict
import numpy as np
from energy_demand.geography import region
from energy_demand.geography import weather_region
import energy_demand.rs_model as rs_model
import energy_demand.ss_model as ss_model
import energy_demand.is_model as is_model
from energy_demand.dwelling_stock import dw_stock
#from energy_demand.profiles import load_factors as load_factors
from energy_demand.basic import testing_functions as testing
from energy_demand.profiles import load_profile
from energy_demand.initalisations import helpers
from energy_demand.profiles import generic_shapes
from energy_demand.geography import weather_station_location as wl

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
        """Main function of ED model
        """
        logging.info("... start main energy demand function")
        self.curr_yr = data['sim_param']['curr_yr']

        # Create non regional dependent load profiles
        data['non_regional_lp_stock'] = self.create_load_profile_stock(
            data['tech_lp'],
            data['assumptions'],
            data['sectors'])

        # Weather Regions
        self.weather_regions = self.create_weather_regions(
            data['weather_stations'], data)

        logging.debug("... Generate dwelling stock for base year")
        data['rs_dw_stock'] = defaultdict(dict)
        data['ss_dw_stock'] = defaultdict(dict)
        for region_name in region_names:
            data['rs_dw_stock'][region_name][data['sim_param']['base_yr']] = dw_stock.rs_dw_stock(region_name, data, data['sim_param']['base_yr'])
            data['ss_dw_stock'][region_name][data['sim_param']['base_yr']] = dw_stock.ss_dw_stock(region_name, data, data['sim_param']['base_yr'])

        # ---------------------------------------------
        # Initialise and iterate over years
        # ---------------------------------------------
        fuel_indiv_regions_yh = helpers.init_loop_dicts(data)
        reg_enduses_fueltype_y = np.zeros((data['lookups']['fueltypes_nr'], data['assumptions']['model_yeardays_nrs'], 24), dtype=float)
        tot_peak_enduses_fueltype = np.zeros((data['lookups']['fueltypes_nr'], 24), dtype=float)
        tot_fuel_y_max_enduses = np.zeros((data['lookups']['fueltypes_nr']), dtype=float)
        tot_fuel_y_enduse_specific_h = {}

        for array_nr_region, region_name in enumerate(region_names):
            logging.info("Running model for region %s", region_name)

            # Create Region
            region_obj = self.create_region(region_name, data)

            # Create dwelling stock
            data['rs_dw_stock'][region_name][self.curr_yr] = dw_stock.rs_dw_stock(region_name, data, self.curr_yr)
            data['ss_dw_stock'][region_name][self.curr_yr] = dw_stock.ss_dw_stock(region_name, data, self.curr_yr)

            # --------------------
            # Residential SubModel
            # --------------------
            self.rs_submodel = self.residential_submodel(
                region_obj,
                data, data['enduses']['rs_all_enduses'])

            # --------------------
            # Service SubModel
            # --------------------
            self.ss_submodel = self.service_submodel(
                region_obj,
                data, data['enduses']['ss_all_enduses'], data['sectors']['ss_sectors'])

            # --------------------
            # Industry SubModel
            # --------------------
            self.is_submodel = self.industry_submodel(
                region_obj,
                data, data['enduses']['is_all_enduses'], data['sectors']['is_sectors'])

            # ----------------------
            # Summarise functions
            # ----------------------
            logging.debug("... start summing")
            all_submodels = [self.ss_submodel, self.rs_submodel, self.is_submodel]

            # Sum across all regions, all enduse and sectors sum_reg
            fuel_indiv_regions_yh = self.fuel_regions_fueltype(
                fuel_indiv_regions_yh,
                data['lookups'],
                region_obj.region_name,
                array_nr_region,
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'],
                all_submodels)

            # Sum across all regions, all enduse and sectors
            reg_enduses_fueltype_y = self.fuel_aggr(
                reg_enduses_fueltype_y,
                'fuel_yh',
                all_submodels,
                'no_sum',
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            # Sum across all regions, enduses for peak hour
            tot_peak_enduses_fueltype = self.fuel_aggr(
                tot_peak_enduses_fueltype,
                'fuel_peak_dh',
                all_submodels,
                'no_sum',
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            tot_fuel_y_max_enduses = self.fuel_aggr(
                tot_fuel_y_max_enduses,
                'fuel_peak_h',
                all_submodels,
                'no_sum',
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            # Sum across all regions and provide specific enduse
            tot_fuel_y_enduse_specific_h = self.sum_enduse_all_regions(
                tot_fuel_y_enduse_specific_h,
                'fuel_yh',
                all_submodels,
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

        self.fuel_indiv_regions_yh = fuel_indiv_regions_yh
        self.reg_enduses_fueltype_y = reg_enduses_fueltype_y
        self.tot_peak_enduses_fueltype = tot_peak_enduses_fueltype
        self.tot_fuel_y_max_enduses = tot_fuel_y_max_enduses
        self.tot_fuel_y_enduse_specific_h = tot_fuel_y_enduse_specific_h

        #-------------------
        # TESTING
        #-------------------
        testing.test_region_selection(self.fuel_indiv_regions_yh)

        # ---------------------------
        # Functions for load calculations
        # Across all enduses calc_load_factor_h
        # ---------------------------
        '''rs_fuels_peak_h = self.fuel_aggr(
            'fuel_peak_h', [self.rs_submodel], 'no_sum', data['assumptions']['model_yearhours_nrs'], data['assumptions']['model_yeardays_nrs'])
        ss_fuels_peak_h = self.fuel_aggr(
            'fuel_peak_h', [self.ss_submodel], 'no_sum', data['assumptions']['model_yearhours_nrs'], data['assumptions']['model_yeardays_nrs'])
        self.rs_tot_fuels_all_enduses_y = self.fuel_aggr(
            'fuel_yh', [self.rs_submodel], 'no_sum', data['assumptions']['model_yearhours_nrs'], data['assumptions']['model_yeardays_nrs'])
        ss_tot_fuels_all_enduses_y = self.fuel_aggr(
            'fuel_yh', [self.ss_submodel], 'no_sum', data['assumptions']['model_yearhours_nrs'], data['assumptions']['model_yeardays_nrs'])
        self.rs_reg_load_factor_h = load_factors.calc_load_factor_h(
            data, self.rs_tot_fuels_all_enduses_y, rs_fuels_peak_h)
        self.ss_reg_load_factor_h = load_factors.calc_load_factor_h(
            data, ss_tot_fuels_all_enduses_y, ss_fuels_peak_h)
        '''

    def fuel_regions_fueltype(
            self,
            fuel_fueltype_regions,
            lookups,
            region_name,
            array_region,
            model_yearhours_nrs,
            model_yeardays_nrs,
            all_submodels
        ):
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
        {'final_electricity_demand': np.array((regions, model_yearhours_nrs)), dtype=float}
        """
        fuels = self.fuel_aggr(
            np.zeros((lookups['fueltypes_nr'], model_yeardays_nrs, 24), dtype=float),
            'fuel_yh',
            all_submodels,
            'no_sum',
            model_yearhours_nrs,
            model_yeardays_nrs,
            region_name
            )

        # Reshape
        for fueltype_str, fueltype_nr in lookups['fueltype'].items():
            fuel_fueltype_regions[fueltype_str][array_region] += fuels[fueltype_nr].reshape(model_yearhours_nrs)

        return fuel_fueltype_regions

    @classmethod
    def create_load_profile_stock(cls, tech_lp, assumptions, sectors):
        """Assign load profiles which are the same for all regions
        ``non_regional_load_profiles``

        Arguments
        ----------
        tech_lp : dict
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
            shape_yd=tech_lp['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
            shape_yh=tech_lp['rs_shapes_dh']['rs_lighting']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
            shape_peak_dh=tech_lp['rs_shapes_dh']['rs_lighting']['shape_peak_dh']
            )

        # rs_cold (residential refrigeration)
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_cold'],
            enduses=['rs_cold'],
            shape_yd=tech_lp['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'],
            shape_yh=tech_lp['rs_shapes_dh']['rs_cold']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_cold']['shape_peak_yd_factor'],
            shape_peak_dh=tech_lp['rs_shapes_dh']['rs_cold']['shape_peak_dh']
            )

        # rs_cooking
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_cooking'],
            enduses=['rs_cooking'],
            shape_yd=tech_lp['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'],
            shape_yh=tech_lp['rs_shapes_dh']['rs_cooking']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_cooking']['shape_peak_yd_factor'],
            shape_peak_dh=tech_lp['rs_shapes_dh']['rs_cooking']['shape_peak_dh']
            )

        # rs_wet
        non_regional_lp_stock.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['rs_wet'],
            enduses=['rs_wet'],
            shape_yd=tech_lp['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'],
            shape_yh=tech_lp['rs_shapes_dh']['rs_wet']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_wet']['shape_peak_yd_factor'],
            shape_peak_dh=tech_lp['rs_shapes_dh']['rs_wet']['shape_peak_dh']
            )

        # -- dummy rs technologies (apply enduse sepcific shape)
        for enduse in assumptions['rs_dummy_enduses']:
            tech_list = helpers.get_nested_dict_key(assumptions['rs_fuel_tech_p_by'][enduse])
            non_regional_lp_stock.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=tech_list,
                enduses=[enduse],
                shape_yd=tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                shape_yh=tech_lp['rs_shapes_dh'][enduse]['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'][:, np.newaxis],
                enduse_peak_yd_factor=tech_lp['rs_shapes_yd'][enduse]['shape_peak_yd_factor'],
                shape_peak_dh=tech_lp['rs_shapes_dh'][enduse]['shape_peak_dh']
                )

        # - dummy ss technologies
        for enduse in assumptions['ss_dummy_enduses']:
            tech_list = helpers.get_nested_dict_key(assumptions['ss_fuel_tech_p_by'][enduse])
            for sector in sectors['ss_sectors']:
                non_regional_lp_stock.add_load_profile(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=tech_lp['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=tech_lp['ss_shapes_dh'][sector][enduse]['shape_non_peak_y_dh'] * tech_lp['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    sectors=[sector],
                    enduse_peak_yd_factor=tech_lp['ss_shapes_yd'][sector][enduse]['shape_peak_yd_factor'],
                    shape_peak_dh=tech_lp['ss_shapes_dh'][sector][enduse]['shape_peak_dh']
                    )

        # dummy is - Flat load profile
        shape_peak_dh, _, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh = generic_shapes.flat_shape(
            assumptions['model_yeardays_nrs'], )

        # If space heating, add load shapes for service sector
        shape_peak_dh_sectors_enduses = defaultdict(dict)
        all_enduses_including_heating = assumptions['is_dummy_enduses']
        all_enduses_including_heating.append("is_space_heating")
        for sector in sectors['is_sectors']:
            for enduse in all_enduses_including_heating:
                if enduse == "is_space_heating":
                    shape_peak_dh_sectors_enduses[sector][enduse] = {
                        'shape_peak_dh': tech_lp['ss_shapes_dh'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_peak_dh']}
                else:
                    shape_peak_dh_sectors_enduses[sector][enduse] = {
                        'shape_peak_dh': shape_peak_dh}

        for enduse in assumptions['is_dummy_enduses']:

            # Add load profile for space heating of ss sector
            if enduse == "is_space_heating":
                tech_list = helpers.get_nested_dict_key(assumptions['is_fuel_tech_p_by'][enduse])
                for sector in sectors['is_sectors']:
                    non_regional_lp_stock.add_load_profile(
                        unique_identifier=uuid.uuid4(),
                        technologies=tech_list,
                        enduses=[enduse],
                        shape_yd=tech_lp['ss_shapes_yd'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_non_peak_yd'],
                        shape_yh=tech_lp['ss_shapes_dh'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_non_peak_y_dh'] * tech_lp['ss_shapes_yd'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_non_peak_yd'][:, np.newaxis],
                        sectors=[sector],
                        enduse_peak_yd_factor=tech_lp['ss_shapes_yd'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_peak_yd_factor'],
                        shape_peak_dh=shape_peak_dh_sectors_enduses
                        )
            else:
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
                        shape_peak_dh=shape_peak_dh_sectors_enduses
                        )

        return non_regional_lp_stock

    def get_regional_yh(self, fueltypes_nr, region_name, model_yeardays_nrs):
        """Get yh fuel for all fueltype for a specific region of all submodels

        Arguments
        ----------
        region_name : str
            Name of region to get attributes
        fueltypes_nr : int
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
            fueltypes_nr,
            [self.ss_submodel, self.rs_submodel, self.is_submodel],
            'no_sum',
            model_yeardays_nrs,
            region_name,
            )

        return region_fuel_yh

    @classmethod
    def industry_submodel(cls, region_obj, data, enduses, sectors):
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

        for sector in sectors:
            for enduse in enduses:

                # Take load profile for is space heating
                # from service sector space heating
                if enduse == "is_space_heating":
                    crit_flat_profile = False
                else:
                    crit_flat_profile = True

                # Create submodule
                submodule = is_model.IndustryModel(
                    data,
                    region_obj,
                    enduse,
                    sector=sector,
                    crit_flat_profile=crit_flat_profile
                    )

                # Add to list
                submodules.append(submodule)

                _scrap_cnt += 1
                logging.debug(
                    "... industry model {} in %s %s",
                    data['sim_param']['curr_yr'],
                    (100*_scrap_cnt)/(len(data['lu_reg']) * len(sectors) * len(enduses)))

        return submodules

    @classmethod
    def residential_submodel(cls, region_obj, data, enduses, sectors=False):
        """Create the residential submodules (per enduse and region) and add them to list

        Arguments
        ----------
        data : dict
            Data container
        enduses : list
            All residential enduses
        sectors : dict, default=False
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

        if not sectors:
            sectors=['dummy_sector']
        else:
            pass

        submodule_list = []

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

        return submodule_list

    @classmethod
    def service_submodel(cls, region_obj, data, enduses, sectors):
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
                logging.debug(
                    " ...running service model %s %s",
                    data['sim_param']['curr_yr'],
                    100.0 / (len(data['lu_reg']) * len(sectors) * len(enduses)) * _scrap_cnt)

        return submodule_list

    @classmethod
    def create_weather_regions(cls, weather_regions, data):
        """Create all weather regions and calculate

        Arguments
        ----------
        weather_region : list
            The name of the Weather Region
        data : dict
            Data container
        """
        weather_region_objs = []

        for weather_region_name in weather_regions:

            region_obj = weather_region.WeatherRegion(
                weather_region_name=weather_region_name,
                sim_param=data['sim_param'],
                assumptions=data['assumptions'],
                lookups=data['lookups'],
                all_enduses=data['enduses'],
                temperature_data=data['temp_data'],
                tech_lp=data['tech_lp'],
                sectors=data['sectors']
                )

            weather_region_objs.append(region_obj)

        return weather_region_objs

    def create_region(self, region_name, data):
        """Create all regions and add them in a list

        Arguments
        ----------
        region_name : list
            Region name
        data : dict
            Data container
        """
        logging.debug("... creating region: '%s'", region_name)

        # Get closest weather station to `Region`
        closest_reg = wl.get_closest_station(
            data['reg_coord'][region_name]['longitude'],
            data['reg_coord'][region_name]['latitude'],
            data['weather_stations']
            )
        weather_reg_obj = get_weather_reg(
            self.weather_regions, closest_reg)

        region_obj = region.Region(
            region_name=region_name,
            data=data,
            weather_reg_obj=weather_reg_obj
            )

        return region_obj

    def sum_enduse_all_regions(self, input_dict, attribute_to_get, sector_models, model_yearhours_nrs, model_yeardays_nrs):
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
        enduse_dict = input_dict

        for sector_model in sector_models:
            for model_object in sector_model:

                if model_object.enduse not in enduse_dict:
                    enduse_dict[model_object.enduse] = 0

                # Add fuel with flat load shape
                enduse_dict[model_object.enduse] += self.get_fuels_yh(
                    model_object, attribute_to_get, model_yearhours_nrs, model_yeardays_nrs)

        return enduse_dict

    def fuel_aggr(
            self,
            input_array,
            attribute_to_get,
            sector_models,
            sum_crit,
            model_yearhours_nrs,
            model_yeardays_nrs,
            region_name=False
        ):
        """Collect hourly data from all regions and sum across all fuel types and enduses

        Arguments
        ----------
        attribute_to_get : str
            Attribue to summarise
        sector_models : list
            Sector models to summarise
        lp_crit, sum_crit : str
            Criteria
        region_name : str
            Name of region

        Returns
        -------
        input_array : array
            Summarised array
        """
        # Select specific region if defined
        if region_name:
            for sector_model in sector_models:
                for model_object in sector_model:
                    if model_object.region_name == region_name:
                        input_array += self.get_fuels_yh(
                            model_object,
                            attribute_to_get,
                            model_yearhours_nrs,
                            model_yeardays_nrs)
        else:
            for sector_model in sector_models:
                for model_object in sector_model:
                    input_array += self.get_fuels_yh(
                        model_object,
                        attribute_to_get,
                        model_yearhours_nrs,
                        model_yeardays_nrs)

        if sum_crit == 'no_sum':
            return input_array
        elif sum_crit == 'sum':
            return np.sum(input_array)

    @classmethod
    def get_fuels_yh(cls, model_object, attribute_to_get, model_yearhours_nrs, model_yeardays_nrs):
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
        -   Flat shape
        """
        if model_object.enduse_object.crit_flat_profile:

            # Yearly fuel
            fuels_reg_y = model_object.enduse_object.fuel_y

            if attribute_to_get == 'fuel_peak_dh':
                shape_peak_dh = np.full((24), 1 / 8760)
                fuels_reg_peak = fuels_reg_y
                fuels = fuels_reg_peak[:, np.newaxis] * shape_peak_dh

            elif attribute_to_get == 'fuel_peak_h':
                shape_peak_h = 1 / 8760
                fuels = fuels_reg_y * shape_peak_h

            elif attribute_to_get == 'shape_non_peak_y_dh':
                shape_non_peak_y_dh = np.full((model_yeardays_nrs, 24), (1.0 / 24))
                fuels = fuels_reg_y * shape_non_peak_y_dh

            elif attribute_to_get == 'shape_non_peak_yd':
                shape_non_peak_yd = np.ones((model_yeardays_nrs), dtype=float) / model_yeardays_nrs
                fuels = fuels_reg_y * shape_non_peak_yd
                #FAST TODO:_a = np.full(
                # (model_yeardays_nrs), (fuels_reg_y / model_yeardays_nrs), dtype=float)

            elif attribute_to_get == 'fuel_yh':
                nr_modelled_hours_factor = 1 / model_yearhours_nrs
                fast_shape = np.full(
                    (model_object.enduse_object.fuel_new_y.shape[0], model_yeardays_nrs, 24),
                    nr_modelled_hours_factor, dtype=float)
                fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * fast_shape

        else: #If not flat shape, use yh load profile of enduse
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

def get_weather_reg(weather_regions, closest_reg):
    """Iterate list with weather regions and get weather region object

    Arguments
    ---------
    weather_regions : dict
        Weather regions
    closest_reg : str
        Station ID

    Return
    ------
    weather_region : object
        Weather region
    """
    for weather_region in weather_regions:
        if weather_region.weather_region_name == closest_reg:
            return weather_region
        