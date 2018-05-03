"""The function `EnergyDemandModel` executes all the submodels of the energy demand model
"""
import logging
from collections import defaultdict
import numpy as np

import energy_demand.enduse_func as endusefunctions
from energy_demand.geography.region import Region
from energy_demand.geography.weather_region import WeatherRegion
from energy_demand.dwelling_stock import dw_stock
from energy_demand.basic import testing_functions as testing
from energy_demand.profiles import load_factors
from energy_demand.charts import figure_HHD_gas_demand

class EnergyDemandModel(object):
    """ Main function of energy demand model. All submodels
    are executed here and all aggregation functions of the results

    Arguments
    ----------
    regions : list
        Region names
    data : dict
        Main data container
    assumptions : obj
        Assumptions and calculations based on assumptions
    """
    def __init__(self, regions, data, assumptions):
        """Constructor
        """
        logging.info("... start main energy demand function")
        self.curr_yr = assumptions.curr_yr

        # ----------------------------
        # Create Weather Regions
        # ----------------------------
        weather_regions = {}
        for weather_region in data['weather_stations']:
            weather_regions[weather_region] = WeatherRegion(
                name=weather_region,
                assumptions=assumptions,
                technologies=data['technologies'],
                fueltypes=data['lookups']['fueltypes'],
                all_enduses=data['enduses'],
                temp_by=data['temp_data'][weather_region],
                tech_lp=data['tech_lp'],
                sectors=data['sectors'],
                criteria=data['criterias'])

        # ------------------------
        # Create Dwelling Stock
        # ------------------------
        logging.info("... Generate dwelling stocks")
        if data['criterias']['virtual_building_stock_criteria']:

            # Virtual dwelling stocks
            data['rs_dw_stock'], data['ss_dw_stock'] = create_virtual_dwelling_stocks(
                regions, assumptions.curr_yr, data)

        else:
            # Create dwelling stock from imported data from newcastle
            data = create_dwelling_stock(
                regions, assumptions.curr_yr, data)

        logging.info("... finished generating dwelling stock")

        # --------------------
        # Initialise result container to aggregate results
        # --------------------
        aggr_results = initialise_result_container(
            data['lookups']['fueltypes_nr'],
            data['sectors'],
            data['reg_nrs'],
            assumptions.model_yearhours_nrs,
            assumptions.model_yeardays_nrs,
            assumptions.heating_technologies)

        # ---------------------------------------------
        # Iterate over regions and Simulate
        # ---------------------------------------------
        for reg_array_nr, region in enumerate(regions):
            logging.info(
                "... Simulate region %s for year %s", region, assumptions.curr_yr)

            reg_rs_submodel, reg_ss_submodel, reg_is_submodel = simulate_region(
                region, data, assumptions, weather_regions)

            # Store submodel results
            all_submodels = [reg_rs_submodel, reg_ss_submodel, reg_is_submodel]

            # ---------------------------------------------
            # Aggregate results
            # ---------------------------------------------
            aggr_results = aggregate_final_results(
                aggr_results,
                reg_array_nr,
                all_submodels,
                data['criterias']['mode_constrained'],
                data['lookups']['fueltypes'],
                data['lookups']['fueltypes_nr'],
                assumptions.model_yearhours_nrs,
                assumptions.model_yeardays_nrs,
                assumptions.seasons,
                assumptions.enduse_space_heating,
                data['technologies'],
                data['criterias']['beyond_supply_outputs'])

        # -------
    	# Set all keys of aggr_results as self.attributes (EnergyDemandModel)
        # -------
        for key_attribute_name, value in aggr_results.items():
            setattr(self, key_attribute_name, value)

        # ------------------------------
        # TESTING
        # ------------------------------
        testing.test_region_selection(self.ed_fueltype_regs_yh)

        # ------------------------------
        # Chart HDD * Pop vs actual gas demand
        # ------------------------------
        if data['criterias']['plot_HDD_chart']:
            logging.info("plot figure HDD comparison")
            figure_HHD_gas_demand.main(regions, weather_regions, data)

def simulate_region(region, data, assumptions, weather_regions):
    """Run submodels for a single region

    Arguments
    ---------
    region : str
        Region name
    data : dict
        Data container
    weather_regions : oject
        Weather regions

    Returns
    -------
    XX_submodels : obj
        SubModel result object
    """
    logging.debug("... Simulate region %s", region)

    region_obj = Region(
        name=region,
        longitude=data['reg_coord'][region]['longitude'],
        latitude=data['reg_coord'][region]['latitude'],
        rs_fuel_disagg=data['fuel_disagg']['rs_fuel_disagg'][region],
        ss_fuel_disagg=data['fuel_disagg']['ss_fuel_disagg'][region],
        is_fuel_disagg=data['fuel_disagg']['is_fuel_disagg'][region],
        weather_stations=data['weather_stations'])

    # Closest weather region object
    weather_region_obj = weather_regions[region_obj.closest_weather_region_id]

    # --------------------
    # Residential SubModel
    # --------------------
    rs_submodel = residential_submodel(
        region_obj,
        weather_region_obj,
        data['scenario_data'],
        data['rs_dw_stock'][region],
        assumptions,
        data['lookups'],
        data['criterias'],
        data['enduses']['rs_enduses'])

    # --------------------
    # Service SubModel
    # --------------------
    ss_submodel = service_submodel(
        region_obj,
        weather_region_obj,
        data['scenario_data'],
        data['ss_dw_stock'][region],
        assumptions,
        data['lookups'],
        data['criterias'],
        data['enduses']['ss_enduses'],
        data['sectors']['ss_sectors'])

    # --------------------
    # Industry SubModel
    # --------------------
    is_submodel = industry_submodel(
        region_obj,
        weather_region_obj,
        data['scenario_data'],
        assumptions,
        data['lookups'],
        data['criterias'],
        data['enduses']['is_enduses'],
        data['sectors']['is_sectors'])

    return rs_submodel, ss_submodel, is_submodel

def fuel_aggr(
        sector_models,
        sum_crit,
        model_yearhours_nrs,
        model_yeardays_nrs,
        attribute_non_technology,
        attribute_technologies,
        technologies,
        input_array
    ):
    """Collect hourly data from all regions and sum across
    all fuel types and enduses

    Arguments
    ----------
    sector_models : list
        Sector models
    sum_crit : str
        Criteria
    model_yearhours_nrs : int
        Number of modelled hours in a year
    fueltypes_nr : int
        Number of fueltypes
    attribute_to_get : str
        Attribue to sumarise
    model_yeardays_nrs : int
        Number of modelled yeardays
    attribute_non_technology : str
        Attribute
    attribute_technologies : str
        Attribute 'techs_fuel_yh'
    technologies : dict
        Technologies
    input_array : array
        Input array to aggregate fuel

    Returns
    -------
    input_array : array
        Summarised array
    """
    for sector_model in sector_models:
        for enduse_object in sector_model:

            fuels = get_fuels_yh(
                enduse_object,
                attribute_technologies,
                model_yearhours_nrs,
                model_yeardays_nrs)

            if isinstance(fuels, dict):
                for tech, fuel_tech in fuels.items():
                    tech_fueltype = technologies[tech].fueltype_int
                    input_array[tech_fueltype] += fuel_tech
            else:
                # Fuel per technology
                fuels = get_fuels_yh(
                    enduse_object,
                    attribute_non_technology,
                    model_yearhours_nrs,
                    model_yeardays_nrs)
                input_array += fuels

    if sum_crit == 'no_sum':
        return input_array
    elif sum_crit == 'sum':
        return np.sum(input_array)

def get_fuels_yh(
        enduse_object,
        attribute_to_get,
        model_yearhours_nrs,
        model_yeardays_nrs
    ):
    """Get yh load profile and assign yh shape
    for enduses with flat load profiles

    Arguments
    ----------
    enduse_object : dict
        Object of submodel run
    attribute_to_get : str
        Attribute to read out
    model_yearhours_nrs : int
        Number of modelled hours in a year
    model_yeardays_nrs : int
        Number of modelled yeardays

    Returns
    -------
    fuels : array
        Fuels with flat load profile

    Note
    -----
    -   For enduses where 'flat_profile_crit' in Enduse Class is True
        a flat load profile is generated. Otherwise, the yh as calculated
        for each enduse is used
    -   Flat shape
    """
    if enduse_object.flat_profile_crit:

        # Annual fuel
        fuels_reg_y = enduse_object.fuel_y

        if attribute_to_get == 'fuel_peak_h':
            shape_peak_h = 1 / 8760
            fuels = fuels_reg_y * shape_peak_h
        elif attribute_to_get == 'shape_non_peak_y_dh':
            shape_non_peak_y_dh = np.full((model_yeardays_nrs, 24), (1.0 / 24))
            fuels = fuels_reg_y * shape_non_peak_y_dh
        elif attribute_to_get == 'shape_non_peak_yd':
            shape_non_peak_yd = np.ones((model_yeardays_nrs), dtype=float) / model_yeardays_nrs
            fuels = fuels_reg_y * shape_non_peak_yd
        elif attribute_to_get == 'fuel_yh' or attribute_to_get == 'techs_fuel_yh':
            nr_modelled_hours_factor = 1 / model_yearhours_nrs
            fast_shape = np.full(
                (enduse_object.fuel_y.shape[0], model_yeardays_nrs, 24),
                nr_modelled_hours_factor, dtype=float)
            fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * fast_shape
        elif attribute_to_get == 'techs_fuel_peak_h':
            fuels = 1 / model_yearhours_nrs
    else: #If not flat shape, use yh load profile of enduse

        fuels = getattr(enduse_object, attribute_to_get)

    return fuels

def residential_submodel(
        region,
        weather_region,
        scenario_data,
        rs_dw_stock,
        assumptions,
        lookups,
        criterias,
        enduses,
        sectors=False
    ):
    """Create the residential submodules (per enduse and region) and add them to list
    data['lookups']
    Arguments
    ----------
    data : dict
        Data container
    enduses : list
        All residential enduses
    sectors : list, default=False
        Sectors

    Returns
    -------
    submodule_list : list
        List with submodules
    """
    logging.debug("... residential submodel start")

    if not sectors:
        sectors = [False]
    else:
        pass

    submodels = []

    for sector in sectors:
        for enduse in enduses:

            # ------------------------------------------------------
            # Configure and select correct Enduse() specific inputs
            # ------------------------------------------------------
            if assumptions.strategy_variables['spatial_explicit_diffusion']['scenario_value']:
                sig_param_tech = assumptions.rs_sig_param_tech[enduse][region.name]
                strategy_variables = assumptions.regional_strategy_variables[region.name]
            else:
                sig_param_tech = assumptions.rs_sig_param_tech[enduse]
                strategy_variables = assumptions.strategy_variables

            # ------------------------------------------------------
            # Create submodel
            # ------------------------------------------------------
            submodel = endusefunctions.Enduse(
                submodel='rs_submodel',
                region=region.name,
                scenario_data=scenario_data,
                assumptions=assumptions,
                load_profiles=weather_region.rs_load_profiles,
                base_yr=assumptions.base_yr,
                curr_yr=assumptions.curr_yr,
                enduse=enduse,
                sector=sector,
                fuel=region.rs_enduses_fuel[enduse],
                tech_stock=weather_region.rs_tech_stock,
                heating_factor_y=weather_region.f_heat_rs_y,
                cooling_factor_y=weather_region.f_cooling_rs_y,
                fuel_fueltype_tech_p_by=assumptions.rs_fuel_tech_p_by[enduse],
                sig_param_tech=sig_param_tech,
                criterias=criterias,
                strategy_variables=strategy_variables,
                fueltypes_nr=lookups['fueltypes_nr'],
                fueltypes=lookups['fueltypes'],
                model_yeardays_nrs=assumptions.model_yeardays_nrs,
                enduse_overall_change=assumptions.enduse_overall_change,
                dw_stock=rs_dw_stock)

            submodels.append(submodel)

    return submodels

def service_submodel(
        region,
        weather_region,
        scenario_data,
        ss_dw_stock,
        assumptions,
        lookups,
        criterias,
        enduses,
        sectors
    ):
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
    submodels : list
        List with submodels
    """
    logging.debug("... service submodel start")
    submodels = []

    for sector in sectors:
        for enduse in enduses:

            # ------------------------------------------------------
            # Configure and select correct Enduse() specific inputs
            # ------------------------------------------------------
            if assumptions.strategy_variables['spatial_explicit_diffusion']['scenario_value']:
                sig_param_tech = assumptions.ss_sig_param_tech[enduse][sector][region.name]
                strategy_variables = assumptions.regional_strategy_variables[region.name]
            else:
                sig_param_tech = assumptions.ss_sig_param_tech[enduse][sector]
                strategy_variables = assumptions.strategy_variables

            # ------------------------------------------------------
            # Create submodel
            # ------------------------------------------------------
            submodel = endusefunctions.Enduse(
                submodel='ss_submodel',
                region=region.name,
                scenario_data=scenario_data,
                assumptions=assumptions,
                load_profiles=weather_region.ss_load_profiles,
                base_yr=assumptions.base_yr,
                curr_yr=assumptions.curr_yr,
                enduse=enduse,
                sector=sector,
                fuel=region.ss_enduses_sectors_fuels[enduse][sector],
                tech_stock=weather_region.ss_tech_stock,
                heating_factor_y=weather_region.f_heat_ss_y,
                cooling_factor_y=weather_region.f_cooling_ss_y,
                fuel_fueltype_tech_p_by=assumptions.ss_fuel_tech_p_by[enduse][sector],
                sig_param_tech=sig_param_tech,
                criterias=criterias,
                strategy_variables=strategy_variables,
                fueltypes_nr=lookups['fueltypes_nr'],
                fueltypes=lookups['fueltypes'],
                model_yeardays_nrs=assumptions.model_yeardays_nrs,
                enduse_overall_change=assumptions.enduse_overall_change,
                dw_stock=ss_dw_stock)

            # Add to list
            submodels.append(submodel)

    return submodels

def industry_submodel(
        region,
        weather_region,
        scenario_data,
        #non_regional_lp_stock,
        assumptions,
        lookups,
        criterias,
        enduses,
        sectors
    ):
    """Industry subsector model

    A flat load profile is assumed except for is_space_heating

    Arguments
    ----------
    region : int
        Region
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
    """
    logging.debug("... industry submodel start")
    submodels = []

    for sector in sectors:
        for enduse in enduses:

            # ------------------------------------------------------
            # Configure and select correct Enduse() specific inputs
            # ------------------------------------------------------
            if enduse == "is_space_heating":
                flat_profile_crit = False
            else:
                flat_profile_crit = True

            if assumptions.strategy_variables['spatial_explicit_diffusion']['scenario_value']:
                sig_param_tech = assumptions.is_sig_param_tech[enduse][sector][region.name]
                strategy_variables = assumptions.regional_strategy_variables[region.name]
            else:
                sig_param_tech = assumptions.is_sig_param_tech[enduse][sector]
                strategy_variables = assumptions.strategy_variables

            # ------------------------------------------------------
            # Create submodel
            # ------------------------------------------------------
            submodel = endusefunctions.Enduse(
                submodel='is_submodel',
                region=region.name,
                scenario_data=scenario_data,
                assumptions=assumptions,
                load_profiles=weather_region.is_load_profiles,
                base_yr=assumptions.base_yr,
                curr_yr=assumptions.curr_yr,
                enduse=enduse,
                sector=sector,
                fuel=region.is_enduses_sectors_fuels[enduse][sector],
                tech_stock=weather_region.is_tech_stock,
                heating_factor_y=weather_region.f_heat_is_y,
                cooling_factor_y=weather_region.f_cooling_is_y,
                fuel_fueltype_tech_p_by=assumptions.is_fuel_tech_p_by[enduse][sector],
                sig_param_tech=sig_param_tech,
                enduse_overall_change=assumptions.enduse_overall_change,
                criterias=criterias,
                strategy_variables=strategy_variables,
                fueltypes_nr=lookups['fueltypes_nr'],
                fueltypes=lookups['fueltypes'],
                model_yeardays_nrs=assumptions.model_yeardays_nrs,
                reg_scen_drivers=assumptions.scenario_drivers['is_submodule'],
                flat_profile_crit=flat_profile_crit)

            submodels.append(submodel)

    return submodels

def aggr_fuel_regions_fueltype(
        aggregation_array,
        fueltypes_nr,
        fueltypes,
        array_region_nr,
        model_yearhours_nrs,
        model_yeardays_nrs,
        submodels,
        technologies
    ):
    """Aggregate fuels for every fueltype, region and timestep (unconstrained mode).

    Arguments
    ---------
    aggregation_array : array
        Array to aggregate ed
    fueltypes_nr : dict
        Number of fueltypes
    fueltypes : dict
        Fueltypes
    array_region_nr : int
        Array nr position of region
    model_yearhours_nrs : int
        Modelled houry in a year (max 8760)
    model_yeardays_nrs : int
        Number of modelled yeardays (max 365)
    submodels : list
        List with submodels

    Returns
    -------
    aggregation_array : array
        Aggregated fuels per fueltype, region, yearhours

    fuel_region : dict
        Aggregated fuel per fueltype, yeardays, hours
    """
    input_array = np.zeros((
        fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

    fuel_region = fuel_aggr(
        submodels,
        'no_sum',
        model_yearhours_nrs,
        model_yeardays_nrs,
        'fuel_yh',
        'techs_fuel_yh',
        technologies,
        input_array=input_array)

    # Reshape
    for fueltype_nr in fueltypes.values():
        aggregation_array[fueltype_nr][array_region_nr] += fuel_region[fueltype_nr].reshape(model_yearhours_nrs)

    return aggregation_array, fuel_region

def sum_enduse_all_regions(
        input_dict,
        sector_models,
        technologies,
        model_yearhours_nrs,
        model_yeardays_nrs,
        fueltypes_nr
    ):
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
                enduse_dict[model_object.enduse] = np.zeros((fueltypes_nr, model_yeardays_nrs, 24))

            fuels = get_fuels_yh(
                model_object,
                'techs_fuel_yh',
                model_yearhours_nrs,
                model_yeardays_nrs)

            if isinstance(fuels, dict):
                for tech, fuel_tech in fuels.items():
                    tech_fueltype = technologies[tech].fueltype_int
                    enduse_dict[model_object.enduse][tech_fueltype] += fuel_tech
                    #enduse_dict[model_object.enduse] += fuel_tech
            else:
                # Fuel per technology
                fuels = get_fuels_yh(
                    model_object,
                    'fuel_yh',
                    model_yearhours_nrs,
                    model_yeardays_nrs)
                enduse_dict[model_object.enduse] += fuels

    return enduse_dict

def averaged_season_hourly(averaged_h, fuel_region_yh, reg_array_nr, fueltypes, seasons):
    """Calculate averaged hourly values for each season

    Arguments
    ---------
    averaged_h : dict
        Averaged hours per season (season, fueltype, array_nr_reg, 24)
    fuel_region_yh : array
        Fuel of region (fueltype, yearday)
    reg_array_nr : int
        Integer of region
    fueltypes : dict
        Fueltype lookup
    ed_fueltype_regs_yh : array
       (fueltypes_nr, reg_nrs, yearhours_nrs)

    Return
    ------
    averaged_h : dict
        Averaged hourly value per season {season: array(fuetlype, region, 24)}
    """
    for fueltype in fueltypes:
        for season, yeardays_modelled in seasons.items():
            for yearday in yeardays_modelled:
                averaged_h[season][fueltype][reg_array_nr] += fuel_region_yh[fueltype][yearday]

    # Calculate average hourly values for every season
    for season, yeardays_modelled in seasons.items():
        for fueltype in fueltypes:
            averaged_h[season][fueltype][reg_array_nr] = averaged_h[season][fueltype][reg_array_nr] / len(yeardays_modelled)

    return averaged_h

def create_virtual_dwelling_stocks(regions, curr_yr, data):
    """Create virtual dwelling stocks for residential
    and service sector
    """
    rs_dw_stock = defaultdict(dict)
    ss_dw_stock = defaultdict(dict)
    for region in regions:

        # Dwelling stock of residential SubModel for base year
        rs_dw_stock[region][data['assumptions'].base_yr] = dw_stock.rs_dw_stock(
            region,
            data['assumptions'],
            data['scenario_data'],
            data['assumptions'].simulated_yrs,
            data['lookups']['dwtype'],
            data['enduses']['rs_enduses'],
            data['reg_coord'],
            data['assumptions'].scenario_drivers['rs_submodule'],
            data['assumptions'].base_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

        # Dwelling stock of service SubModel for base year
        ss_dw_stock[region][data['assumptions'].base_yr] = dw_stock.ss_dw_stock(
            region,
            data['enduses']['ss_enduses'],
            data['sectors']['ss_sectors'],
            data['scenario_data'],
            data['reg_coord'],
            data['assumptions'],
            data['assumptions'].base_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

        # Dwelling stock of residential SubModel for current year
        rs_dw_stock[region][curr_yr] = dw_stock.rs_dw_stock(
            region,
            data['assumptions'],
            data['scenario_data'],
            data['assumptions'].simulated_yrs,
            data['lookups']['dwtype'],
            data['enduses']['rs_enduses'],
            data['reg_coord'],
            data['assumptions'].scenario_drivers['rs_submodule'],
            curr_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

        # Dwelling stock of service SubModel for current year
        ss_dw_stock[region][curr_yr] = dw_stock.ss_dw_stock(
            region,
            data['enduses']['ss_enduses'],
            data['sectors']['ss_sectors'],
            data['scenario_data'],
            data['reg_coord'],
            data['assumptions'],
            curr_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

    return dict(rs_dw_stock), dict(ss_dw_stock)

def create_dwelling_stock(regions, curr_yr, data):
    """Create dwelling stock based on NEWCASTLE data

    Arguments
    ---------

    Returns
    -------
    """
    #data['rs_dw_stock'][region][curr_yr] = dw_stock.createNEWCASTLE_dwelling_stock(
    # self.curr_yr,
    # region,
    # )
    #data['ss_dw_stock'][region][curr_yr] = dw_stock.createNEWCASTLE_dwelling_stock(self.curr_yr)
    return data

def aggregate_final_results(
        aggr_results,
        reg_array_nr,
        all_submodels,
        mode_constrained,
        fueltypes,
        fueltypes_nr,
        model_yearhours_nrs,
        model_yeardays_nrs,
        seasons,
        enduse_space_heating,
        technologies,
        beyond_supply_outputs=True
    ):
    """Aggregate results for a single region

    Parameters
    ----------
    aggr_results : dict
        Contains alls results to aggregate
        (key of this will be made self.attributes)
    reg_array_nr : int
        Region array number
    all_submodels : list
        Submodel objects
    mode_constrained : bool
        Mode of how to run the model
    fueltypes : dict
        Fueltypes lookup
    fueltypes_nr : int
        Number of fueltypes
    model_yearhours_nrs : int
        Number of modelled hours in a year
    model_yeardays_nrs : int
        Number of modelled days in a year
    seasons : dict
        Seasons
    enduse_space_heating : list
        All heating enduses
    technologies : dict
        Technologies
    beyond_supply_outputs : bool
        Criteria whether additional results are aggregated
        for plotting purposes going beyond the SMIF framework

    Returns
    --------
    aggr_results : dict
        Contains all aggregated results
    """
    logging.debug("... start summing for supply model")

    if mode_constrained:

        # -------------
        # Aggregate fuel of constrained technologies
        # -------------
        for submodel_nr, submodel in enumerate(all_submodels):
            for enduse_object in submodel:

                # Aggregate over heating technologies
                if enduse_object.enduse in enduse_space_heating:

                    # Get fuels for all techs
                    submodel_techs_fueltypes_yh = get_fuels_yh(
                        enduse_object,
                        'techs_fuel_yh',
                        model_yearhours_nrs,
                        model_yeardays_nrs)

                    # All used heating technologies
                    heating_techs = enduse_object.enduse_techs

                    # Iterate technologies and get fuel per technology
                    for heating_tech in heating_techs:

                        # Fuel of technology
                        tech_fuel = submodel_techs_fueltypes_yh[heating_tech]

                        # Fueltype of technology
                        fueltype_tech_int = technologies[heating_tech].fueltype_int

                        # Aggregate Submodel (sector) specific enduse for fueltype
                        aggr_results['ed_techs_submodel_fueltype_regs_yh'][heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel #TODO [fueltype_tech_int]

        # -------------
        # Summarise remaining fuel of other enduses
        # -------------
        for submodel_nr, submodel in enumerate(all_submodels):

            input_array = np.zeros((
                fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

            submodel_ed_fueltype_regs_yh = fuel_aggr(
                [submodel],
                'no_sum',
                model_yearhours_nrs,
                model_yeardays_nrs,
                'fuel_yh',
                'techs_fuel_yh',
                technologies,
                input_array=input_array)

            # Add SubModel specific ed
            aggr_results['ed_submodel_fueltype_regs_yh'][submodel_nr][reg_array_nr] += submodel_ed_fueltype_regs_yh
    else:
        # -------------
        # Summarise ed of Unconstrained mode (heat is provided)
        #
        # np.array(fueltypes, sectors, regions, timesteps)
        # -------------
        # Sum across all fueltypes, sectors, regs and hours
        for submodel_nr, submodel in enumerate(all_submodels):

            input_array = np.zeros((
                fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

            submodel_ed_fueltype_regs_yh = fuel_aggr(
                [submodel],
                'no_sum',
                model_yearhours_nrs,
                model_yeardays_nrs,
                'fuel_yh',
                'techs_fuel_yh',
                technologies,
                input_array=input_array)

            # Add SubModel specific ed
            aggr_results['ed_submodel_fueltype_regs_yh'][submodel_nr][reg_array_nr] += submodel_ed_fueltype_regs_yh

    # -----------
    # Other summing for other purposes
    # -----------
    if beyond_supply_outputs:

        # Sum across all regions, all enduse and sectors sum_reg
        # [fueltype, region, fuel_yh], [fueltype, fuel_yh]
        aggr_results['ed_fueltype_regs_yh'], fuel_region_yh = aggr_fuel_regions_fueltype(
            aggr_results['ed_fueltype_regs_yh'],
            fueltypes_nr,
            fueltypes,
            reg_array_nr,
            model_yearhours_nrs,
            model_yeardays_nrs,
            all_submodels,
            technologies)

        aggr_results['ed_fueltype_national_yh'] = fuel_aggr(
            all_submodels,
            'no_sum',
            model_yearhours_nrs,
            model_yeardays_nrs,
            'fuel_yh',          # unconstrained
            'techs_fuel_yh',    # constrained
            technologies,
            input_array=aggr_results['ed_fueltype_national_yh'])

        # Sum across all regions and provide specific enduse
        aggr_results['tot_fuel_y_enduse_specific_yh'] = sum_enduse_all_regions(
            aggr_results['tot_fuel_y_enduse_specific_yh'],
            all_submodels,
            technologies,
            model_yearhours_nrs,
            model_yeardays_nrs,
            fueltypes_nr)

        # --------------------------------------
        # Calculate averaged hour profile per season
        # --------------------------------------
        aggr_results['averaged_h'] = averaged_season_hourly(
            aggr_results['averaged_h'],
            fuel_region_yh,
            reg_array_nr,
            fueltypes.values(),
            seasons)

        # --------------------------------------
        # Regional load factor calculations
        # --------------------------------------
        # Calculate annual load factors across all enduses
        load_factor_y = load_factors.calc_lf_y(
            fuel_region_yh)

        # Calculate average load for every day
        average_fuel_yd = np.average(fuel_region_yh, axis=2)
        load_factor_yd = load_factors.calc_lf_d(
            fuel_region_yh,
            average_fuel_yd,
            mode_constrained=False)

        load_factor_seasons = load_factors.calc_lf_season(
            seasons,
            fuel_region_yh,
            average_fuel_yd)

        # Copy regional load factors
        for fueltype_nr in fueltypes.values():
            aggr_results['reg_load_factor_y'][fueltype_nr][reg_array_nr] = load_factor_y[fueltype_nr]
            aggr_results['reg_load_factor_yd'][fueltype_nr][reg_array_nr] = load_factor_yd[fueltype_nr]

            for season, lf_season in load_factor_seasons.items():
                aggr_results['reg_seasons_lf'][season][fueltype_nr][reg_array_nr] = lf_season[fueltype_nr]

    return aggr_results

def initialise_result_container(
        fueltypes_nr,
        sectors,
        reg_nrs,
        model_yearhours_nrs,
        model_yeardays_nrs,
        heating_technologies
    ):
    """Create container with empty dict or arrays
    as values in a dict. This is used to aggregate the
    region calculation results

    Arguments
    ---------
    fueltypes_nr : int
        Number of fueltypes
    sectors : list
        Sectors
    reg_nrs : int
        Number of regions
    model_yearhours_nrs : int
        Number of yearhours
    model_yeardays_nrs : int
        Number of yeardays
    heating_technologies : list
        Heating technologies

    Returns
    -------
    result_container : dict
        Contained with all empty correctly formated values for aggregation
    """
    result_container = {}

    result_container['ed_submodel_fueltype_regs_yh'] = np.zeros(
        (len(sectors.keys()), reg_nrs, fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

    result_container['ed_techs_submodel_fueltype_regs_yh'] = {}
    for heating_tech in heating_technologies:
        result_container['ed_techs_submodel_fueltype_regs_yh'][heating_tech] = np.zeros(
            (len(sectors.keys()), reg_nrs, fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

    result_container['ed_fueltype_regs_yh'] = np.zeros(
        (fueltypes_nr, reg_nrs, model_yearhours_nrs), dtype=float)

    result_container['ed_fueltype_national_yh'] = np.zeros(
        (fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

    result_container['tot_fuel_y_max_enduses'] = np.zeros(
        (fueltypes_nr), dtype=float)

    result_container['tot_fuel_y_enduse_specific_yh'] = {}

    result_container['reg_load_factor_y'] = np.zeros(
        (fueltypes_nr, reg_nrs), dtype=float)

    result_container['reg_load_factor_yd'] = np.zeros(
        (fueltypes_nr, reg_nrs, model_yeardays_nrs), dtype=float)

    result_container['reg_seasons_lf'] = {
        'summer' : np.zeros((fueltypes_nr, reg_nrs), dtype=float),
        'spring': np.zeros((fueltypes_nr, reg_nrs), dtype=float),
        'winter': np.zeros((fueltypes_nr, reg_nrs), dtype=float),
        'autumn': np.zeros((fueltypes_nr, reg_nrs), dtype=float)}

    result_container['averaged_h'] = {
        'summer' : np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float),
        'spring': np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float),
        'winter': np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float),
        'autumn': np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float)}

    return result_container
