"""The function `EnergyDemandModel` executes all the submodels of the energy demand model
"""
import logging
from collections import defaultdict
import numpy as np
from sys import getsizeof
from pympler import summary
from pympler import muppy
from pympler import refbrowser

import energy_demand.enduse_func as endusefunctions
from energy_demand.geography.region import Region
from energy_demand.geography.weather_region import WeatherRegion
from energy_demand.dwelling_stock import dw_stock
from energy_demand.profiles import load_factors
from energy_demand.profiles import generic_shapes
from energy_demand.basic import demand_supply_interaction

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
    weather_yr : int
        Year of temperature
    """
    def __init__(
            self,
            regions,
            data,
            assumptions,
            weather_stations,
            weather_yr,
            weather_by
        ):
        """Constructor
        """
        logging.info("... start main energy demand function")

        self.curr_yr = assumptions.curr_yr

        # ----------------------------
        # Create Weather Regions
        # ----------------------------
        # current weather_yr
        weather_regions_weather_cy = {}
        for weather_region in weather_stations[weather_yr]:
            weather_regions_weather_cy[weather_region] = WeatherRegion(
                name=weather_region,
                latitude=weather_stations[weather_yr][weather_region]['latitude'],
                longitude=weather_stations[weather_yr][weather_region]['longitude'],
                assumptions=assumptions,
                technologies=data['technologies'],
                fueltypes=data['lookups']['fueltypes'],
                enduses=data['enduses'],
                temp_by=data['temp_data'][weather_yr][weather_region],
                tech_lp=data['tech_lp'],
                sectors=data['sectors'])

        # base weather_yr
        weather_regions_weather_by = {}
        for weather_region in weather_stations[weather_by]:
            weather_regions_weather_by[weather_region] = WeatherRegion(
                name=weather_region,
                latitude=weather_stations[weather_by][weather_region]['latitude'],
                longitude=weather_stations[weather_by][weather_region]['longitude'],
                assumptions=assumptions,
                technologies=data['technologies'],
                fueltypes=data['lookups']['fueltypes'],
                enduses=data['enduses'],
                temp_by=data['temp_data'][weather_by][weather_region],
                tech_lp=data['tech_lp'],
                sectors=data['sectors'])

        # ------------------------
        # Create Dwelling Stock
        # ------------------------
        if data['criterias']['virtual_building_stock_criteria']:
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

        # Initialise result container to aggregate results
        aggr_results = initialise_result_container(
            data['lookups']['fueltypes_nr'],
            data['reg_nrs'],
            submodels_enduses=data['enduses'])

        # -------------------------------------------
        # Simulate regions
        # -------------------------------------------
        for reg_array_nr, region in enumerate(regions):

            logging.info("... Simulate: region %s, simulation year: %s, weather_yr: %s, percent: (%s)",
                region, assumptions.curr_yr, weather_yr, round((100/data['reg_nrs'])*reg_array_nr, 2))
            print("... Simulate: region {}, simulation year: {}, weather_yr: {}, percent: ({})".format(
                region, assumptions.curr_yr, weather_yr, round((100/data['reg_nrs'])*reg_array_nr, 2)), flush=True)

            all_submodels = simulate_region(
                region,
                data,
                assumptions,
                weather_regions_weather_cy,
                weather_regions_weather_by)

            # ---------------------------------------------
            # Aggregate results specifically over regions
            # ---------------------------------------------
            aggr_results = aggregate_results_constrained(
                data['reg_nrs'],
                aggr_results,
                reg_array_nr,
                all_submodels,
                data['criterias']['mode_constrained'],
                data['lookups']['fueltypes_nr'],
                assumptions.enduse_space_heating,
                data['technologies'])

            #logging.info("Size " + str(getsizeof(all_submodels)))
            del all_submodels
            '''aggr_results = initialise_result_container(
                data['lookups']['fueltypes_nr'],
                data['reg_nrs'],
                submodels_enduses=data['enduses'])

            if reg_array_nr == 0:
                sum1 = summary.summarize(muppy.get_objects())
            if reg_array_nr == 1:
                sum2 = summary.summarize(muppy.get_objects())
                diff = summary.get_diff(sum1, sum2)
                print(summary.print_(diff))
                

                all_objects = muppy.get_objects()
                print(all_objects)
                for i in all_objects:
                    root = i
                    break
                ib = refbrowser.InteractiveBrowser(root)
                ib.main()
                
                raise Exception'''
            
            #if reg_array_nr == 1:
            #    break
            #sum1 = summary.summarize(muppy.get_objects())
            #sum2 = summary.summarize(muppy.get_objects())
            #diff = summary.get_diff(sum1, sum2)
            # print(summary.print_(diff))

        # ------------------------------
        # Plot generation to correlate HDD and energy demand
        # ------------------------------
        ## logging.info("plot figure HDD comparison")
        ## from energy_demand.charts import figure_HHD_gas_demand
        ## figure_HHD_gas_demand.main(regions, weather_regions, data)

        # ---------------------------------------------------
        # Aggregate results for all regions
        # ---------------------------------------------------
        aggr_results = aggregate_across_all_regs(
            aggr_results,
            data['lookups']['fueltypes_nr'],
            data['lookups']['fueltypes'],
            data['reg_nrs'],
            data['enduses'],
            data['assumptions'],
            data['criterias'],
            data['technologies'])

        # Set all keys of aggr_results as self.attributes
        for key_attribute_name, value in aggr_results.items():
            setattr(self, key_attribute_name, value)

def aggregate_across_all_regs(
        aggr_results,
        fueltypes_nr,
        fueltypes,
        reg_nrs,
        enduses,
        assumptions,
        criterias,
        technologies
    ):
    """Aggregate the regional results into different
    forms used for outputs

    Arguments
    ---------
    aggr_results : dict
        Aggregation container
    fueltypes_nr : int
        Number of fueltypes
    fueltypes : dict
        Fueltypes
    reg_nrs : int
        Number of regions
    enduses : dict
        Submodels and their sectors
    assumptions : dict
        Assumptions
    criterias : dict
        Criteria
    technologies : dict
        Technologies per enduse
    """

    # ----------------------------------------------------
    # Aggregate: [fueltype, region, fuel_yh_8760]
    # ----------------------------------------------------
    array_init = np.zeros((fueltypes_nr, reg_nrs, 8760))
    aggr_results['ed_fueltype_regs_yh'] = aggregate_from_full_results(
        array_init,
        aggr_results['ed_submodel_enduse_fueltype_regs_yh'],
        time_resolution='8760_h',
        per_region=True,
        per_sector=False,
        per_enduse=False)

    # ----------------------------------------------------
    # Aggregate: [fueltype, fuel_yh_8760]
    # ----------------------------------------------------
    array_init = np.zeros((fueltypes_nr, 365, 24))
    aggr_results['ed_fueltype_national_yh'] = aggregate_from_full_results(
        array_init,
        aggr_results['ed_submodel_enduse_fueltype_regs_yh'],
        time_resolution='365_24',
        per_region=False,
        per_sector=False,
        per_enduse=False)

    # ----------------------------------------------------
    # Aggregate: [fueltype, enduse, fuel_yh, 8760]
    # ----------------------------------------------------
    array_init = {}
    for submodel in enduses:
        for enduse in enduses[submodel]:
            array_init[enduse] = np.zeros((fueltypes_nr, 8760))
    aggr_results['tot_fuel_y_enduse_specific_yh'] = aggregate_from_full_results(
        array_init,
        aggr_results['ed_submodel_enduse_fueltype_regs_yh'],
        time_resolution='8760_h',
        per_region=False,
        per_sector=False,
        per_enduse=True)

    # ----------------------------------------------------
    # Calculate averaged hour profile per season
    # ----------------------------------------------------
    aggr_results['averaged_h'] = averaged_season_hourly(
        aggr_results['ed_fueltype_regs_yh'],
        fueltypes.values(),
        fueltypes_nr,
        assumptions.seasons,
        reg_nrs)

    # ----------------------------------------------------
    # Regional load factor calculations
    # ----------------------------------------------------
    #aggr_results['reg_seasons_lf'], aggr_results['reg_load_factor_y'], aggr_results['reg_load_factor_yd'] = aggregate_load_factors(
    aggr_results['reg_load_factor_y'], aggr_results['reg_load_factor_yd'] = aggregate_load_factors(
        aggr_results['ed_fueltype_regs_yh'],
        fueltypes_nr,
        reg_nrs,
        assumptions.seasons)

    # ----------------------------------------------------
    # Unconstrained results
    # np.array of all fueltypes (submodel, region, fueltype, hours)
    # ----------------------------------------------------
    aggr_results['results_unconstrained'] = aggregate_result_unconstrained(
        assumptions.nr_of_submodels,
        enduses,
        aggr_results['ed_submodel_enduse_fueltype_regs_yh'],
        fueltypes_nr,
        reg_nrs)

    # ----------------------------------------------------
    # Generate dict for supply model
    # ----------------------------------------------------
    if criterias['mode_constrained']:
        aggr_results['supply_results'] = demand_supply_interaction.constrained_results(
            aggr_results['results_constrained'],
            aggr_results['results_unconstrained'],
            assumptions.submodels_names,
            fueltypes,
            technologies)
    else:
        aggr_results['supply_results'] = demand_supply_interaction.unconstrained_results(
            aggr_results['results_unconstrained'],
            assumptions.submodels_names,
            fueltypes)

    return aggr_results

def aggregate_load_factors(
        ed_fueltype_regs_yh,
        fueltypes_nr,
        reg_nrs,
        seasons
    ):
    """Calculate load factors
    #TODO IMPROVE SPEED
    """
    # Initialise
    #reg_seasons_lf = {
    #    'summer' : np.zeros((fueltypes_nr, reg_nrs), dtype="float"),
    #    'spring': np.zeros((fueltypes_nr, reg_nrs), dtype="float"),
    #    'winter': np.zeros((fueltypes_nr, reg_nrs), dtype="float"),
    #    'autumn': np.zeros((fueltypes_nr, reg_nrs), dtype="float")}

    reg_load_factor_y = np.zeros((fueltypes_nr, reg_nrs), dtype="float")
    reg_load_factor_yd = np.zeros((fueltypes_nr, reg_nrs, 365), dtype="float")

    # Calculate annual load factors across all enduses
    for fueltype_nr in range(fueltypes_nr):
        for reg_array_nr in range(reg_nrs):

            reg_load_factor_y[fueltype_nr][reg_array_nr] = load_factors.calc_lf_y_8760(
                ed_fueltype_regs_yh[fueltype_nr][reg_array_nr])

            # Calculate average load for every day
            reg_load_factor_yd[fueltype_nr][reg_array_nr] = load_factors.calc_lf_d_8760(
                ed_fueltype_regs_yh[fueltype_nr][reg_array_nr])

            #load_factor_seasons = load_factors.calc_lf_season_8760(
            #    seasons,
            #    ed_fueltype_regs_yh[fueltype_nr][reg_array_nr])

            #print(load_factor_seasons)
            #print(reg_seasons_lf)
            #for season, lf_season in load_factor_seasons.items():
            #    reg_seasons_lf[season][fueltype_nr][reg_array_nr] = lf_season
    return reg_load_factor_y, reg_load_factor_yd
    #return reg_seasons_lf, reg_load_factor_y, reg_load_factor_yd

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

def simulate_region(
        region,
        data,
        assumptions,
        weather_regions_weather_cy,
        weather_regions_weather_by
    ):
    """Run submodels for a single region

    Arguments
    ---------
    region : str
        Region name
    data : dict
        Data container
    weather_regions_weather_cy : obj
        Weather regions pf current weather year
    weather_regions_weather_by : obj
        Weather regions of weather base year

    Returns
    -------
    all_submodels : list
        List with submodel objects depending on submodels
    """
    submodel_objs = []

    submodel_names = assumptions.submodels_names

    # Get region specific disaggregated fuel
    region_fuel_disagg = get_disaggregated_fuel_of_reg(
        submodel_names, data['fuel_disagg'], region)

    region_obj = Region(
        name=region,
        longitude=data['reg_coord'][region]['longitude'],
        latitude=data['reg_coord'][region]['latitude'],
        region_fuel_disagg=region_fuel_disagg,
        weather_reg_cy=weather_regions_weather_cy,
        weather_reg_by=weather_regions_weather_by)

    # Closest weather region object
    weather_region_obj = weather_regions_weather_cy[region_obj.closest_weather_reg]

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
                    f_weather_correction=region_obj.f_weather_correction[submodel_name],
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

    # Collect all submodels with respect to submodel names and store in list
    # e.g. [[all_residential-submodels], [all_service_submodels]...]
    all_submodels = []
    for submodel in data['lookups']['submodels_names']:
        submodels = get_all_submodels(submodel_objs, submodel)
        all_submodels.append(submodels)
      
    # remove garbage
    del region_obj
    del weather_region_obj
    del region_fuel_disagg

    return all_submodels

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

def aggr_complete_result(
        full_result_aggr,
        reg_array_nr,
        sector_models,
        technologies
    ):
    """Aggregate full results (except technology specific)

    Arguments
    ---------
    full_result_aggr : dict
        Dict to aggregat with form: submodel, enduse, region, fueltype, 8760 hours
    reg_array_nr : int
        Region number
    sector_models : list
        Sector models objects in list
    technologies : dict
        Technologies

    Return
    ------
    full_result_aggr : dict
        Full result aggregation dict
    """
    for submodel_nr, sector_model in enumerate(sector_models):
        for model_object in sector_model:
            fuels = get_fuels_yh(model_object, 'techs_fuel_yh')

            if isinstance(fuels, dict):
                for tech, fuel_tech in fuels.items():
                    tech_fueltype = technologies[tech].fueltype_int
                    full_result_aggr[submodel_nr][model_object.enduse][tech_fueltype][reg_array_nr] += fuel_tech.reshape(8760)
            else:
                fueltype_yh_365_24 = get_fuels_yh(model_object, 'fuel_yh')

                # Iterate over fueltype and add to region
                fueltype_yh_8760 = fueltype_yh_365_24.reshape(fueltype_yh_365_24.shape[0], 8760)
                for fueltype_nr, fuels_8760 in enumerate(fueltype_yh_8760):
                    full_result_aggr[submodel_nr][model_object.enduse][fueltype_nr][reg_array_nr] += fuels_8760

    return full_result_aggr

#TODO IS THIS USED?
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
        fueltype_region_yh,
        fueltypes,
        fueltypes_nr,
        seasons,
        reg_nrs
    ):
    """Calculate averaged hourly values for each season

    Arguments
    ---------
    averaged_h : dict
        Averaged hours per season (season, fueltype, array_nr_reg, 24)
    fueltype_region_yh : array
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
    averaged_h = {
        'summer' : np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float"),
        'spring': np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float"),
        'winter': np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float"),
        'autumn': np.zeros((fueltypes_nr, reg_nrs, 24), dtype="float")}

    fueltype_region_yh_365_24 = fueltype_region_yh.reshape(
        fueltype_region_yh.shape[0], fueltype_region_yh.shape[1], 365, 24)

    for fueltype in fueltypes:
        for season, yeardays_modelled in seasons.items():
            for region_nr in range(reg_nrs):
                for yearday in yeardays_modelled:
                    averaged_h[season][fueltype][region_nr] += fueltype_region_yh_365_24[fueltype][region_nr][yearday]

    # Calculate average hourly values for every season
    for season, yeardays_modelled in seasons.items():
        for fueltype in fueltypes:
            averaged_h[season][fueltype] = averaged_h[season][fueltype] / len(yeardays_modelled)

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

def aggregate_result_unconstrained(
        nr_of_submodels,
        submodels_enduses,
        ed_submodel_enduse_fueltype_regs_yh,
        fueltypes_nr,
        reg_nrs
    ):
    """Aggregated unconstrained results. Summarise energy demand
    of unconstrained mode (heat is provided)

    Arguments
    ---------
    nr_of_submodels : int
        Number of submodels
    submodels_enduses : dict
        Submodels and enduses
    ed_submodel_enduse_fueltype_regs_yh : array
        Fuel array
    fueltypes_nr : int
        Number of fueltypes
    reg_nrs : int
        Number of regions
    
    Returns
    --------
    constrained_array : array
        assumptions.nr_of_submodels, reg_nrs, fueltypes_nr, 8760
    """
    constrained_array = np.zeros((
        nr_of_submodels,
        reg_nrs,
        fueltypes_nr,
        8760), dtype="float")

    for submodel_nr, (_, submodel_enduses) in enumerate(submodels_enduses.items()):
        for enduse in submodel_enduses:
            for fueltype_nr in range(fueltypes_nr):
                for region_nr in range(reg_nrs):
                    constrained_array[submodel_nr][region_nr][fueltype_nr] += ed_submodel_enduse_fueltype_regs_yh[submodel_nr][enduse][fueltype_nr][region_nr]

    return constrained_array

def aggregate_result_constrained(
        tot_fuel_y_enduse_specific_yh,
        submodels_enduses,
        fueltypes_nr,
        enduse_space_heating,
        technologies
    ):
    """SCRAP NOT USED
    """
    results_constrained = {}

    # -----------------------------------------------------------------
    # Aggregate fuel of constrained technologies for heating
    # -----------------------------------------------------------------
    for submodel_nr, submodel_enduses in enumerate(submodels_enduses):
        for enduse in submodel_enduses:

            # Aggregate only over heating technologies
            if enduse in enduse_space_heating:

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
                    if heating_tech in results_constrained.keys():
                        results_constrained[heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel
                    else:
                        results_constrained[heating_tech] = np.zeros((len(all_submodels), reg_nrs, fueltypes_nr, 365, 24), dtype="float")
                        results_constrained[heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel

    return results_constrained

def aggregate_results_constrained(
        reg_nrs,
        aggr_results,
        reg_array_nr,
        all_submodels,
        mode_constrained,
        fueltypes_nr,
        enduse_space_heating,
        technologies
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
    aggr_results['ed_submodel_enduse_fueltype_regs_yh'] = aggr_complete_result(
        aggr_results['ed_submodel_enduse_fueltype_regs_yh'],
        reg_array_nr,
        all_submodels,
        technologies)

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
                            aggr_results['results_constrained'][heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel.reshape(8760)
                        else:
                            aggr_results['results_constrained'][heating_tech] = np.zeros((len(all_submodels), reg_nrs, fueltypes_nr, 8760), dtype="float")
                            aggr_results['results_constrained'][heating_tech][submodel_nr][reg_array_nr][fueltype_tech_int] += tech_fuel.reshape(8760)

    return aggr_results

def initialise_result_container(
        fueltypes_nr,
        reg_nrs,
        submodels_enduses
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
    container : dict
        Contained with all empty correctly formated values for aggregation
    """
    container = {}
    container['results_constrained'] = {}

    container['ed_submodel_enduse_fueltype_regs_yh'] = {}
    for submodel_nr, submodel in enumerate(submodels_enduses):
        container['ed_submodel_enduse_fueltype_regs_yh'][submodel_nr] = {}
        for enduse in submodels_enduses[submodel]:
            container['ed_submodel_enduse_fueltype_regs_yh'][submodel_nr][enduse] = np.zeros((
                fueltypes_nr, reg_nrs, 8760), dtype="float")

    return container

def aggregate_from_full_results(
        aggregated_container,
        full_sim_data,
        time_resolution,
        per_region,
        per_sector,
        per_enduse,
        reg_array_nr=False
    ):
    """Function to read from full simulation data
    specific demands

    Argument
    --------
    full_sim_data : dict
         Modelling results per submodel, enduse, region, fueltype, 8760h
    time_resolution : str
        Either 'annual', 'hourly', '360_24_h', '8760_h'
    """
    for submodel_nr in full_sim_data:
        for enduse in full_sim_data[submodel_nr]:

            # Get full data
            reg_fueltype_8760h = np.copy(full_sim_data[submodel_nr][enduse])

            # Test if reshaping and annual or hourly
            if time_resolution == 'annual':
                demand = np.sum(reg_fueltype_8760h, axis=2) # Sum all hours
            elif time_resolution == '8760_h':
                demand = reg_fueltype_8760h
            elif time_resolution == '365_24':
                demand = reg_fueltype_8760h.reshape(
                    reg_fueltype_8760h.shape[0],
                    reg_fueltype_8760h.shape[1],
                    365, 24)
            else:
                raise Exception("Provide either 'annual' or 'hourly' or '365_24'")

            # Aggregate according to criteria
            if per_sector:
                if per_region:
                    if per_enduse:
                        pass
                    else:
                        pass
                else:
                    if per_enduse:
                        pass
                    else:
                        pass
            else:
                if per_region:
                    if per_enduse:
                        aggregated_container[enduse] += demand
                    else:
                        aggregated_container += demand
                else:
                    # Sum across all regions
                    demand = np.sum(demand, axis=1)

                    if per_enduse:
                        aggregated_container[enduse] += demand
                    else:
                        aggregated_container += demand

    return aggregated_container
