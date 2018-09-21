"""The function `EnergyDemandModel` executes all the submodels of the energy demand model
"""
import logging
from collections import defaultdict
import numpy as np
import pandas as pd

import energy_demand.enduse_func as endusefunctions
from energy_demand.geography.region import Region
from energy_demand.geography.weather_region import WeatherRegion
from energy_demand.dwelling_stock import dw_stock
from energy_demand.profiles import load_factors
from energy_demand.profiles import generic_shapes
from energy_demand.plotting import validation_enduses
from energy_demand.technologies import tech_related

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
                enduses=data['enduses'],
                temp_by=data['temp_data'][weather_region],
                tech_lp=data['tech_lp'],
                sectors=data['sectors'])

        # ------------------------
        # Create Dwelling Stock
        # ------------------------
        if data['criterias']['virtual_building_stock_criteria']:
            logging.info("... Generate virtual dwelling stocks")

            # Virtual dwelling stocks
            rs_dw_stock, ss_dw_stock = create_virtual_dwelling_stocks(
                regions, assumptions.curr_yr, data)

            data['dw_stocks'] = {
                data['lookups']['submodels_names'][0]: rs_dw_stock,
                data['lookups']['submodels_names'][1]: ss_dw_stock,
                data['lookups']['submodels_names'][2]: None}
        else:
            # Create dwelling stock from imported data from newcastle
            data = create_dwelling_stock(
                regions, assumptions.curr_yr, data)

        # --------------------
        # Initialise result container to aggregate results
        # --------------------
        aggr_results = initialise_result_container(
            data['lookups']['fueltypes_nr'],
            data['assumptions'].submodels_names,
            data['reg_nrs'])

        # ---------------------------------------------
        # Iterate over regions and simulate region
        # ---------------------------------------------
        for reg_array_nr, region in enumerate(regions):
            logging.info(
                "... Simulate region %s, year %s, (%s)",
                region,
                assumptions.curr_yr,
                round((100/data['reg_nrs'])*reg_array_nr, 2))

            all_submodel_objs = simulate_region(
                region, data, assumptions, weather_regions)

            # Collect all submodels with respect to submodel names and store in list
            # e.g. [[all_residential-submodels], [all_service_submodels]...]
            all_submodels = []
            for submodel in data['lookups']['submodels_names']:
                submodels = get_all_submodels(all_submodel_objs, submodel)
                all_submodels.append(submodels)

            # ---------------------------------------------
            # Aggregate results
            # ---------------------------------------------
            aggr_results = aggregate_final_results(
                data['reg_nrs'],
                aggr_results,
                reg_array_nr,
                all_submodels,
                data['criterias']['mode_constrained'],
                data['lookups']['fueltypes'],
                data['lookups']['fueltypes_nr'],
                data['lookups']['submodels_names'],
                assumptions.seasons,
                assumptions.enduse_space_heating,
                data['technologies'],
                data['criterias']['write_txt_additional_results'])
            
        # -------
    	# Set all keys of aggr_results as self.attributes (EnergyDemandModel)
        # -------
        for key_attribute_name, value in aggr_results.items():
            setattr(self, key_attribute_name, value)

        # ------------------------------
        # Plot generation to correlate HDD and energy demand
        # ------------------------------
        ## logging.info("plot figure HDD comparison")
        ## from energy_demand.charts import figure_HHD_gas_demand
        ## figure_HHD_gas_demand.main(regions, weather_regions, data)

def get_all_submodels(submodels, submodel_name):
    """Collect all submodel objects for a
    specific submodel name

    Arguments
    ---------
    submodels : list
        All calculated model objects
    submodel_name : str
        Name of submodels to collect

    Returns
    -------
    specific_submodels : list
        Contains all submodels
    """
    specific_submodels = []

    for submodel in submodels:
        if submodel.submodel_name == submodel_name:
            specific_submodels.append(submodel)

    return specific_submodels

def get_disaggregated_fuel_of_reg(submodel_names, fuel_disagg, region):
    """Get disaggregated region for every submodel
    for a specific region

    Arguments
    -------
    submodel_names : dict
        Name of all submodels
    fuel_disagg : dict
        Fuel per submodel for all regions
    region : str
        Region

    Returns
    -------
    region_fuel_disagg : dict
        Disaggregated fuel for a specific region
    """
    region_fuel_disagg = {}

    for submodel_name in submodel_names:
        region_fuel_disagg[submodel_name] = fuel_disagg[submodel_name][region]

    return region_fuel_disagg

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
    submodel_objs : obj
        SubModel result object
    """
    submodel_names = assumptions.submodels_names

    # Get region specific disaggregated fuel
    region_fuel_disagg = get_disaggregated_fuel_of_reg(
        submodel_names, data['fuel_disagg'], region)

    region_obj = Region(
        name=region,
        longitude=data['reg_coord'][region]['longitude'],
        latitude=data['reg_coord'][region]['latitude'],
        region_fuel_disagg=region_fuel_disagg,
        weather_stations=data['weather_stations'])

    # Closest weather region object
    weather_region_obj = weather_regions[region_obj.closest_weather_region_id]

    submodel_objs = []

    # Iterate overall submodels
    for submodel_name in submodel_names:

        # Iterate overall sectors in submodel
        for sector in data['sectors'][submodel_name]:

            # Iterate overall enduses and sectors in submodel
            for enduse in data['enduses'][submodel_name]:

                # ------------------------------------------------------
                # Configure and select correct Enduse specific inputs
                # ------------------------------------------------------
                if submodel_name == 'industry' and enduse != "is_space_heating":
                    flat_profile_crit = True
                else:
                    flat_profile_crit = False

                if sector:
                    fuel = region_obj.fuels[submodel_name][enduse][sector]
                    fuel_tech_p_by = assumptions.fuel_tech_p_by[enduse][sector]
                else:
                    fuel = region_obj.fuels[submodel_name][enduse]
                    fuel_tech_p_by = assumptions.fuel_tech_p_by[enduse]
                
                if not data['dw_stocks'][submodel_name]:
                    dw_stock = False
                else:
                    dw_stock = data['dw_stocks'][submodel_name][region_obj.name]

                # ---------------
                # Create submodel for region and enduse
                # ---------------
                submodel_obj = endusefunctions.Enduse(
                    submodel_name=submodel_name,
                    region=region_obj.name,
                    scenario_data=data['scenario_data'],
                    assumptions=assumptions,
                    load_profiles=weather_region_obj.load_profiles,
                    base_yr=assumptions.base_yr,
                    curr_yr=assumptions.curr_yr,
                    enduse=enduse,
                    sector=sector,
                    fuel=fuel,
                    tech_stock=weather_region_obj.tech_stock[submodel_name],
                    heating_factor_y=weather_region_obj.f_heat[submodel_name],
                    cooling_factor_y=weather_region_obj.f_colling[submodel_name],
                    fuel_tech_p_by=fuel_tech_p_by,
                    criterias=data['criterias'],
                    strategy_vars=assumptions.regional_vars[region_obj.name],
                    fueltypes_nr=data['lookups']['fueltypes_nr'],
                    fueltypes=data['lookups']['fueltypes'],
                    dw_stock=dw_stock,
                    reg_scen_drivers=assumptions.scenario_drivers,
                    flat_profile_crit=flat_profile_crit)

                submodel_objs.append(submodel_obj)

    return submodel_objs

def fuel_aggr(
        sector_models,
        sum_crit,
        attribute_non_technology,
        attribute_technologies,
        technologies,
        shape_aggregation_array
    ):
    """Collect hourly data from all regions and sum across
    all fuel types and enduses

    Arguments
    ----------
    sector_models : list
        Sector models
    sum_crit : str
        Criteria

    fueltypes_nr : int
        Number of fueltypes
    attribute_to_get : str
        Attribue to sumarise
    attribute_non_technology : str
        Attribute
    attribute_technologies : str
        Attribute 'techs_fuel_yh'
    technologies : dict
        Technologies
    shape_aggregation_array : array
        Input array to aggregate fuel

    Returns
    -------
    input_array : array
        Summarised array
    """
    input_array = np.zeros(shape_aggregation_array, dtype="float")

    for sector_model in sector_models:
        for enduse_object in sector_model:

            fuels = get_fuels_yh(
                enduse_object,
                attribute_technologies)

            if isinstance(fuels, dict):
                for tech, fuel_tech in fuels.items():
                    tech_fueltype = technologies[tech].fueltype_int
                    input_array[tech_fueltype] += fuel_tech
            else:
                # Fuel per technology
                fuels = get_fuels_yh(
                    enduse_object,
                    attribute_non_technology)
                input_array += fuels

    if sum_crit == 'no_sum':
        return input_array
    elif sum_crit == 'sum':
        return np.sum(input_array)

def get_fuels_yh(enduse_object, attribute_to_get):
    """Get yh load profile and assign yh shape
    for enduses with flat load profiles

    Arguments
    ----------
    enduse_object : dict
        Object of submodel run
    attribute_to_get : str
        Attribute to read out

    Returns
    -------
    fuels : array
        Fuels with flat load profile

    Note
    -----
    For enduses where 'flat_profile_crit' in Enduse Class is True
    a flat load profile is generated. Otherwise, the yh as calculated
    for each enduse is used
    """
    if enduse_object.flat_profile_crit:

        # Annual fuel
        fuels_reg_y = enduse_object.fuel_y

        # Get flat load profile
        flat_shape_yd, flat_shape_yh, _ = generic_shapes.flat_shape()

        if attribute_to_get == 'shape_non_peak_y_dh':
            fuels = fuels_reg_y * flat_shape_yh
        elif attribute_to_get == 'shape_non_peak_yd':
            fuels = fuels_reg_y * flat_shape_yd
        elif attribute_to_get == 'fuel_yh' or attribute_to_get == 'techs_fuel_yh':
            f_hour = 0.00011415525114155251 #1 / 8760
            flat_shape = np.full((enduse_object.fuel_y.shape[0], 365, 24), f_hour, dtype="float")
            fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * flat_shape
    else: #If not flat shape, use yh load profile of enduse
        fuels = getattr(enduse_object, attribute_to_get)

    return fuels

def aggr_fuel_regions_fueltype(
        aggregation_array,
        fueltypes_nr,
        fueltypes,
        array_region_nr,
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
    submodels : list
        List with submodels

    Returns
    -------
    aggregation_array : array
        Aggregated fuels per fueltype, region, yearhours

    fuel_region : dict
        Aggregated fuel per fueltype, yeardays, hours
    """
    fuel_region = fuel_aggr(
        submodels,
        'no_sum',
        'fuel_yh',
        'techs_fuel_yh',
        technologies,
        shape_aggregation_array=(fueltypes_nr, 365, 24))

    # Reshape
    for fueltype_nr in fueltypes.values():
        aggregation_array[fueltype_nr][array_region_nr] += fuel_region[fueltype_nr].reshape(8760)

    return aggregation_array, fuel_region

def sum_enduse_all_regions(
        aggr_dict,
        sector_models,
        technologies,
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
    for sector_model in sector_models:
        for model_object in sector_model:

            if model_object.enduse not in aggr_dict:
                aggr_dict[model_object.enduse] = np.zeros((fueltypes_nr, 365, 24), dtype="float")

            fuels = get_fuels_yh(
                model_object,
                'techs_fuel_yh')

            if isinstance(fuels, dict):
                for tech, fuel_tech in fuels.items():
                    tech_fueltype = technologies[tech].fueltype_int
                    aggr_dict[model_object.enduse][tech_fueltype] += fuel_tech
            else:
                fuels = get_fuels_yh(model_object, 'fuel_yh')

                aggr_dict[model_object.enduse] += fuels

    return aggr_dict

def averaged_season_hourly(
        averaged_h,
        fuel_region_yh,
        reg_array_nr,
        fueltypes,
        seasons
    ):
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
    and service sector.

    If no floor area is avilable, calculate average floor
    area with population information

    Arguments
    ---------

    """
    rs_dw_stock = defaultdict(dict)
    ss_dw_stock = defaultdict(dict)

    for region in regions:

        # -------------
        # Residential dwelling stocks
        # -------------
        # Base year
        rs_dw_stock[region][data['assumptions'].base_yr] = dw_stock.rs_dw_stock(
            region,
            data['assumptions'],
            data['scenario_data'],
            data['assumptions'].simulated_yrs,
            data['lookups']['dwtype'],
            data['enduses']['residential'],
            data['reg_coord'],
            data['assumptions'].scenario_drivers,
            data['assumptions'].base_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

        # Current year
        rs_dw_stock[region][curr_yr] = dw_stock.rs_dw_stock(
            region,
            data['assumptions'],
            data['scenario_data'],
            data['assumptions'].simulated_yrs,
            data['lookups']['dwtype'],
            data['enduses']['residential'],
            data['reg_coord'],
            data['assumptions'].scenario_drivers,
            curr_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

        # -------------
        # Service dwelling stocks
        # -------------
        # base year
        ss_dw_stock[region][data['assumptions'].base_yr] = dw_stock.ss_dw_stock(
            region,
            data['enduses']['service'],
            data['sectors']['service'],
            data['scenario_data'],
            data['reg_coord'],
            data['assumptions'],
            data['assumptions'].base_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

        # current year
        ss_dw_stock[region][curr_yr] = dw_stock.ss_dw_stock(
            region,
            data['enduses']['service'],
            data['sectors']['service'],
            data['scenario_data'],
            data['reg_coord'],
            data['assumptions'],
            curr_yr,
            data['assumptions'].base_yr,
            data['criterias']['virtual_building_stock_criteria'])

    return dict(rs_dw_stock), dict(ss_dw_stock)

def create_dwelling_stock(regions, curr_yr, data):
    """Create dwelling stock based on NEWCASTLE data

    TODO: Implement

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
        reg_nrs,
        aggr_results,
        reg_array_nr,
        all_submodels,
        mode_constrained,
        fueltypes,
        fueltypes_nr,
        submodels_names,
        seasons,
        enduse_space_heating,
        technologies,
        write_txt_additional_results=True
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
    seasons : dict
        Seasons
    enduse_space_heating : list
        All heating enduses
    technologies : dict
        Technologies
    write_txt_additional_results : bool
        Criteria whether additional results are aggregated
        for plotting purposes going beyond the SMIF framework

    Returns
    --------
    aggr_results : dict
        Contains all aggregated results
    """
    if mode_constrained:

        # -----------------------------------------------------------------
        # Aggregate fuel of constrained technologies for heating
        # -----------------------------------------------------------------
        for submodel_nr, submodel in enumerate(all_submodels):
            for enduse_object in submodel:

                # Aggregate only over heating technologies
                if enduse_object.enduse in enduse_space_heating:

                    submodel_techs_fueltypes_yh = get_fuels_yh(
                        enduse_object,
                        'techs_fuel_yh')

                    # All used heating technologies
                    heating_techs = enduse_object.enduse_techs

                    # Iterate technologies and get fuel per technology
                    for heating_tech in heating_techs:

                        tech_fuel = submodel_techs_fueltypes_yh[heating_tech]       # Fuel of technology
                        fueltype_tech_int = technologies[heating_tech].fueltype_int # Fueltype of technology

                        # Aggregate Submodel (sector) specific enduse for fueltype
                        if heating_tech in aggr_results['results_constrained'].keys():
                            aggr_results['results_constrained'][heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel
                        else:
                            aggr_results['results_constrained'][heating_tech] = np.zeros((len(all_submodels), reg_nrs, fueltypes_nr, 365, 24), dtype="float")
                            aggr_results['results_constrained'][heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel

    # -------------
    # Summarise energy demand of Unconstrained mode (heat is provided)
    # Aggregate total fuel (incl. heating)
    # np.array(fueltypes, sectors, regions, timesteps)
    # -------------
    for submodel_nr, submodel in enumerate(all_submodels):

        submodel_ed_fueltype_regs_yh = fuel_aggr(
            [submodel],
            'no_sum',
            'fuel_yh',
            'techs_fuel_yh',
            technologies,
            shape_aggregation_array=(fueltypes_nr, 365, 24))

        # Add SubModel specific ed
        aggr_results['results_unconstrained'][submodel_nr][reg_array_nr] += submodel_ed_fueltype_regs_yh

    # --------------------------------------------
    # Sum restuls for other purposes
    # --------------------------------------------
    if write_txt_additional_results:

        # Sum across all regions, all enduse and sectors sum_reg
        # [fueltype, region, fuel_yh], [fueltype, fuel_yh]
        aggr_results['ed_fueltype_regs_yh'], fuel_region_yh = aggr_fuel_regions_fueltype(
            aggr_results['ed_fueltype_regs_yh'],
            fueltypes_nr,
            fueltypes,
            reg_array_nr,
            all_submodels,
            technologies)

        ed_fueltype_yh_aggr = fuel_aggr(
            all_submodels,
            'no_sum',
            'fuel_yh',          # unconstrained
            'techs_fuel_yh',    # constrained
            technologies,
            shape_aggregation_array=aggr_results['ed_fueltype_national_yh'].shape)
        aggr_results['ed_fueltype_national_yh'] += ed_fueltype_yh_aggr

        # Sum across enduses
        new_tot_fuel_y_enduse_specific_yh = sum_enduse_all_regions(
            aggr_results['tot_fuel_y_enduse_specific_yh'],
            all_submodels,
            technologies,
            fueltypes_nr)
        aggr_results['tot_fuel_y_enduse_specific_yh'] = new_tot_fuel_y_enduse_specific_yh

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






    # -----------------------------
    # Validation plot
    # -----------------------------
    '''fueltype_to_plot = 'gas'
    fueltype_to_plot_str = tech_related.get_fueltype_int(fueltype_to_plot)

    if mode_constrained:

        dt_to_plot = pd.DataFrame()

        _total_heating = np.zeros((fueltypes_nr, 365, 24))
        for sector_nr, sector in enumerate(submodels_names):
            
            # Heating
            all_heating_techs_per_sector = np.zeros((fueltypes_nr, 365, 24))
            for heating_tech, submodel_data in aggr_results['results_constrained'].items():

                # Fueltype of technology
                fueltype_tech_int = technologies[heating_tech].fueltype_int
                
                if fueltype_tech_int == fueltype_to_plot_str:
                    all_heating_techs_per_sector += submodel_data[sector_nr][reg_array_nr][fueltype_tech_int]
                    _total_heating += submodel_data[sector_nr][reg_array_nr][fueltype_tech_int]
     
            col_name = '{}_heat'.format(sector)
            
            dt_to_plot[col_name] = list(all_heating_techs_per_sector[fueltype_to_plot_str].reshape(8760))
    
            # Non heating
            col_name = '{}_non_heat'.format(sector)
            try:
                dt_to_plot[col_name] += list(aggr_results['results_unconstrained'][submodel_nr][reg_array_nr][fueltype_to_plot_str].reshape(8760))
            except KeyError:
                 dt_to_plot[col_name] = list(aggr_results['results_unconstrained'][submodel_nr][reg_array_nr][fueltype_to_plot_str].reshape(8760))

        # Total heating
        dt_to_plot['_total_heating'] = list(_total_heating[fueltype_to_plot_str].reshape(8760))

    # Plot
    validation_enduses.plot_dataframe_function(
        dt_to_plot,
        x_column_name=dt_to_plot.index.values, # set index as x values
        y_column_names=list(dt_to_plot.columns.values),
        plot_kind='line')'''

    return aggr_results

def initialise_result_container(
        fueltypes_nr,
        submodels,
        reg_nrs
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

    Returns
    -------
    result_container : dict
        Contained with all empty correctly formated values for aggregation
    """
    result_container = {}

    result_container['results_unconstrained'] = np.zeros(
        (len(submodels), reg_nrs, fueltypes_nr, 365, 24), dtype="float")

    result_container['results_constrained'] = {}

    result_container['ed_fueltype_regs_yh'] = np.zeros(
        (fueltypes_nr, reg_nrs, 8760), dtype="float")

    result_container['ed_fueltype_national_yh'] = np.zeros(
        (fueltypes_nr, 365, 24), dtype="float")

    result_container['tot_fuel_y_max_enduses'] = np.zeros(
        (fueltypes_nr), dtype="float")

    result_container['tot_fuel_y_enduse_specific_yh'] = {}

    result_container['reg_load_factor_y'] = np.zeros(
        (fueltypes_nr, reg_nrs), dtype="float")

    result_container['reg_load_factor_yd'] = np.zeros(
        (fueltypes_nr, reg_nrs, 365), dtype="float")

    result_container['reg_seasons_lf'] = {
        'summer' : np.zeros((fueltypes_nr, reg_nrs), dtype="float"),
        'spring': np.zeros((fueltypes_nr, reg_nrs), dtype="float"),
        'winter': np.zeros((fueltypes_nr, reg_nrs), dtype="float"),
        'autumn': np.zeros((fueltypes_nr, reg_nrs), dtype="float")}

    result_container['averaged_h'] = {
        'summer' : np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float"),
        'spring': np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float"),
        'winter': np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float"),
        'autumn': np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float")}

    return result_container
