"""The function `EnergyDemandModel` executes all the submodels of the energy demand model

Notes
-----
some observations from @willu47

- suggest moving bulk of EnergyDemandModel class contents out of __init__ method
  and into class methods, and then calling each method in turn
- suggest explictly creating class properties to access results, rather than
  the ``setattr`` magic
- potential for parallelisation of the for-loop around regions for generation
  by dwelling stocks
- suggest splitting ``aggregate_across_all_regions`` into separate methods as each
  of these requires creating a very large array which is then held in memory,
  along with all of the disaggregated results. Ideally, only those aggregatation
  which are required could be run, then written to disk and then removed from
  memory before moving onto the next
- Lots of potential for a map-reduce approach to this, which could be streamlined
  by using vectorised numpy methods consistently throughout the codebase rather
  than for-loops over indexes of the arrays - this will result in memory and
  performance improvements
- Otherwise, the many of the methods are nicely packaged and will be easily
  testable and refactored going forward, so some profiling would help direct
  attention to where further work is most appropriate
"""
import logging
from collections import defaultdict
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, *_, **__):
        """Alternative to tqdm, with no progress bar - ignore any arguments after the first
        """
        return iterator

from energy_demand.basic import lookup_tables
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
            criterias,
            assumptions,
            weather_yr,
            weather_by
        ):
        """Constructor
        """
        self.curr_yr = assumptions.curr_yr
        # ------------------------
        # Create Dwelling Stock
        # ------------------------
        logging.debug("... generating dwelling stocks")
        lookups = lookup_tables.basic_lookups()

        if criterias['virtual_building_stock_criteria']:
            rs_dw_stock, ss_dw_stock = create_virtual_dwelling_stocks(
                regions, assumptions.curr_yr, data, criterias)

            data['dw_stocks'] = {
                lookups['submodels_names'][0]: rs_dw_stock,
                lookups['submodels_names'][1]: ss_dw_stock,
                lookups['submodels_names'][2]: None}
        else:
            # Create dwelling stock from imported data from newcastle
            data = create_dwelling_stock(
                regions, assumptions.curr_yr, data)

        # Initialise result container to aggregate results
        aggr_results = initialise_result_container(
            assumptions.fueltypes_nr,
            assumptions.reg_nrs,
            assumptions.lookup_enduses,
            assumptions.nr_of_submodels)

        # -------------------------------------------
        # Simulate regions
        # -------------------------------------------
        for reg_array_nr, region in enumerate(tqdm(regions)):

            print("... Simulate: region %s, simulation year: %s, percent: (%s)",
                region, assumptions.curr_yr, round((100/assumptions.reg_nrs)*reg_array_nr, 2), flush=True)
            #logging.info("... Simulate: region %s, simulation year: %s, percent: (%s)",
            #    region, assumptions.curr_yr, round((100/assumptions.reg_nrs)*reg_array_nr, 2))
            all_submodels = simulate_region(
                region,
                data,
                criterias,
                assumptions,
                weather_yr,
                weather_by)
    
            # ---------------------------------------------
            # Aggregate results specifically over regions
            # ---------------------------------------------
            aggr_results = aggregate_single_region(
                assumptions.reg_nrs,
                assumptions.lookup_enduses,
                aggr_results,
                reg_array_nr,
                all_submodels,
                criterias['mode_constrained'],
                assumptions.fueltypes_nr,
                assumptions.enduse_space_heating,
                assumptions.technologies)

        # ---------------------------------------------------
        # Aggregate results for all regions
        # ---------------------------------------------------
        aggr_results = aggregate_across_all_regs(
            aggr_results,
            assumptions.fueltypes_nr,
            data['assumptions'].reg_nrs,
            data['enduses'],
            data['assumptions'],
            criterias,
            assumptions.technologies)

        # Set all keys of aggr_results as self.attributes
        for key_attribute_name, value in aggr_results.items():
            setattr(self, key_attribute_name, value)

def aggregate_across_all_regs(
        aggr_results,
        fueltypes_nr,
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
    fueltypes = lookup_tables.basic_lookups()['fueltypes']

    # ----------------------------------------------------
    # Aggregate: [fueltype, region, fuel_yh_8760]
    # ----------------------------------------------------
    array_init = np.zeros((fueltypes_nr, reg_nrs, 8760))
    aggr_results['ed_fueltype_regs_yh'] = aggregate_from_full_results(
        assumptions.lookup_enduses,
        array_init,
        aggr_results['ed_enduse_fueltype_regs_yh'],
        time_resolution='8760_h',
        per_region=True,
        per_sector=False,
        per_enduse=False)

    # ----------------------------------------------------
    # Aggregate: [fueltype, fuel_yh_8760]
    # ----------------------------------------------------
    array_init = np.zeros((fueltypes_nr, 365, 24))
    aggr_results['ed_fueltype_national_yh'] = aggregate_from_full_results(
        assumptions.lookup_enduses,
        array_init,
        aggr_results['ed_enduse_fueltype_regs_yh'],
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
        assumptions.lookup_enduses,
        array_init,
        aggr_results['ed_enduse_fueltype_regs_yh'],
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
    aggr_results['reg_load_factor_y'], aggr_results['reg_load_factor_yd'] = aggregate_load_factors(
        aggr_results['ed_fueltype_regs_yh'],
        fueltypes_nr,
        reg_nrs)

    # ----------------------------------------------------
    # Generate dict for supply model
    # ----------------------------------------------------
    if criterias['mode_constrained']:
        aggr_results['supply_results'] = demand_supply_interaction.constrained_results(
            aggr_results['results_constrained'],
            aggr_results['results_unconstrained_no_heating'],
            assumptions.submodels_names,
            technologies)
    else:
        aggr_results['supply_results'] = demand_supply_interaction.unconstrained_results(
            aggr_results['results_unconstrained'],
            assumptions.submodels_names)

    return aggr_results

def aggregate_load_factors(
        ed_fueltype_regs_yh,
        fueltypes_nr,
        reg_nrs
    ):
    """Calculate load factors and aggregate
    """
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

    return reg_load_factor_y, reg_load_factor_yd

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
        criterias,
        assumptions,
        weather_yr,
        weather_by
    ):
    """Run submodels for a single region

    Arguments
    ---------
    region : str
        Region name
    data : dict
        Data container

    Returns
    -------
    all_submodels : list
        List with submodel objects depending on submodels
    """
    submodel_names = assumptions.submodels_names

    # ----------------------------
    # Create Base year and current weather Regions
    # ----------------------------
    weather_region_cy = WeatherRegion(
        name=region,
        assumptions=assumptions,
        technologies=assumptions.technologies,
        enduses=data['enduses'],
        temp_by=data['temp_data'][weather_by][region],
        temp_cy=data['temp_data'][weather_yr][region],
        tech_lp=data['tech_lp'],
        sectors=data['sectors'],
        crit_temp_min_max=criterias['crit_temp_min_max'])

    # Get region specific disaggregated fuel
    region_fuel_disagg = get_disaggregated_fuel_of_reg(
        submodel_names, data['fuel_disagg'], region)

    # ----------------------------
    # Create Region
    # ----------------------------
    region_obj = Region(
        name=region,
        longitude=data['reg_coord'][region]['longitude'],
        latitude=data['reg_coord'][region]['latitude'],
        region_fuel_disagg=region_fuel_disagg)

    for submodel_name in submodel_names:
        for sector in data['sectors'][submodel_name]:
            for enduse in data['enduses'][submodel_name]:

                # ------------------------------------------------------
                # Configure and select correct Enduse specific inputs
                # ------------------------------------------------------
                if submodel_name == 'industry' and enduse != "is_space_heating":
                    flat_profile_crit = True
                else:
                    flat_profile_crit = False

                if not data['dw_stocks'][submodel_name]:
                    dw_stock = False
                else:
                    dw_stock = data['dw_stocks'][submodel_name][region_obj.name]

                # ---------------
                # Create submodel for region and enduse
                # ---------------
                yield endusefunctions.Enduse(
                    submodel_name=submodel_name,
                    region=region_obj.name,
                    scenario_data=data['scenario_data'],
                    assumptions=assumptions,
                    load_profiles=weather_region_cy.load_profiles,
                    base_yr=assumptions.base_yr,
                    curr_yr=assumptions.curr_yr,
                    enduse=enduse,
                    sector=sector,
                    fuel=region_obj.fuels[submodel_name][enduse][sector],
                    tech_stock=weather_region_cy.tech_stock[submodel_name],
                    heating_factor_y=weather_region_cy.f_heat[submodel_name],
                    cooling_factor_y=weather_region_cy.f_colling[submodel_name],
                    fuel_tech_p_by=assumptions.fuel_tech_p_by[enduse][sector],
                    criterias=criterias,
                    strategy_vars=assumptions.regional_vars[region_obj.name],
                    fueltypes_nr=assumptions.fueltypes_nr,
                    fueltypes=assumptions.fueltypes,
                    dw_stock=dw_stock,
                    reg_scen_drivers=assumptions.scenario_drivers,
                    flat_profile_crit=flat_profile_crit)

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
    sector_models : list[Enduse]
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

    for enduse_object in sector_models:

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
            f_hour = 1 / 8760
            flat_shape = np.full((enduse_object.fuel_y.shape[0], 365, 24), f_hour, dtype="float")
            fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * flat_shape
    else: #If not flat shape, use yh load profile of enduse
        fuels = getattr(enduse_object, attribute_to_get)

    return fuels

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

def create_virtual_dwelling_stocks(regions, curr_yr, data, criterias):
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
        dwtype = lookup_tables.basic_lookups()['dwtype']

        # Base year
        rs_dw_stock[region][data['assumptions'].base_yr] = dw_stock.rs_dw_stock(
            region,
            data['assumptions'],
            data['scenario_data'],
            data['assumptions'].sim_yrs,
            dwtype,
            data['enduses']['residential'],
            data['reg_coord'],
            data['assumptions'].scenario_drivers,
            data['assumptions'].base_yr,
            data['assumptions'].base_yr,
            criterias['virtual_building_stock_criteria'])

        # Current year
        rs_dw_stock[region][curr_yr] = dw_stock.rs_dw_stock(
            region,
            data['assumptions'],
            data['scenario_data'],
            data['assumptions'].sim_yrs,
            dwtype,
            data['enduses']['residential'],
            data['reg_coord'],
            data['assumptions'].scenario_drivers,
            curr_yr,
            data['assumptions'].base_yr,
            criterias['virtual_building_stock_criteria'])

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
            criterias['virtual_building_stock_criteria'])

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
            criterias['virtual_building_stock_criteria'])

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

def aggregate_single_region(
        reg_nrs,
        lookup_enduses,
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
    all_submodels : list[Enduse]
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

    # Get enduse number for enduse
    submodel_to_idx = {
        name: idx
        for idx, name in enumerate(lookup_tables.basic_lookups()['submodels_names'])
    }

    for enduse_object in all_submodels: # Iterate all simulation results
        # -----------------------------------------------------------------
        # Aggregate fuel of all technologies
        # -----------------------------------------------------------------
        techs_fueltypes_yh = get_fuels_yh(enduse_object, 'techs_fuel_yh')
        enduse_array_nr = lookup_enduses[enduse_object.enduse]
        submodel_nr = submodel_to_idx[enduse_object.submodel_name]

        if isinstance(techs_fueltypes_yh, dict):

            for tech, fuel_tech in techs_fueltypes_yh.items():
                tech_fueltype = technologies[tech].fueltype_int
                reshaped_fuel = fuel_tech.reshape(8760)

                # -------------------------------------------            
                # Add all technologies to main aggreator (heating & non heating)
                # -------------------------------------------
                aggr_results['ed_enduse_fueltype_regs_yh'][enduse_array_nr][tech_fueltype][reg_array_nr] += reshaped_fuel

                # -----------------------------------------------------------------
                # Aggregate fuel of constrained technologies for heating
                # Only add heating technologies to constrained results
                # -----------------------------------------------------------------
                if mode_constrained:
                    if enduse_object.enduse in enduse_space_heating:

                        # Aggregate Submodel (sector) specific enduse for fueltype
                        if tech in aggr_results['results_constrained'].keys():
                            aggr_results['results_constrained'][tech][submodel_nr][reg_array_nr][tech_fueltype] += reshaped_fuel
                        else:
                            if tech not in aggr_results['results_constrained']:
                                aggr_results['results_constrained'][tech] = np.zeros((len(submodel_to_idx), reg_nrs, fueltypes_nr, 8760), dtype="float")
                            aggr_results['results_constrained'][tech][submodel_nr][reg_array_nr][tech_fueltype] += reshaped_fuel
                    else:
                        aggr_results['results_unconstrained_no_heating'][submodel_nr][reg_array_nr][tech_fueltype] += reshaped_fuel
                else:
                    aggr_results['results_unconstrained_no_heating'][submodel_nr][reg_array_nr][tech_fueltype] += reshaped_fuel

        else:
            # Only add heating technologies to constrained results
            fueltype_yh_365_24 = get_fuels_yh(enduse_object, 'fuel_yh')
            fueltype_yh_8760 = fueltype_yh_365_24.reshape(fueltypes_nr, 8760)

            for fueltype_nr, fuels_8760 in enumerate(fueltype_yh_8760):
                aggr_results['ed_enduse_fueltype_regs_yh'][enduse_array_nr][fueltype_nr][reg_array_nr] += fuels_8760

                aggr_results['results_unconstrained_no_heating'][submodel_nr][reg_array_nr][fueltype_nr] += fuels_8760

    return aggr_results

def initialise_result_container(
        fueltypes_nr,
        reg_nrs,
        lookup_enduses,
        nr_of_submodels
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
    lookup_enduses : dict
        Lookup of enduses of array position
    reg_nrs : int
        Number of regions

    Returns
    -------
    container : dict
        Contained with all empty correctly formated values for aggregation
    """
    container = {}
    container['results_constrained'] = {}
    container['results_unconstrained_no_heating'] = np.zeros((
        nr_of_submodels, reg_nrs, fueltypes_nr, 8760), dtype="float")
    container['ed_enduse_fueltype_regs_yh'] = np.zeros((
        len(lookup_enduses), fueltypes_nr, reg_nrs, 8760), dtype="float")

    return container

def get_enduse_from_array_nr(enduse_array_yr_to_get, lookup_enduse):
    """Get enduse string of enduse array number

    Arguments
    ---------
    enduse_array_yr_to_get : int
        Array positoin
    lookup_enduse : dict
        dictionary with enduse and enduse nr

    Returns
    -------
    enduse_str_to_get : str
        Enduse string name
    """
    for enduse_str, enduse_arry_nr in lookup_enduse.items():
        if enduse_arry_nr == enduse_array_yr_to_get:
            enduse_str_to_get = enduse_str
            break

    return enduse_str_to_get

def aggregate_from_full_results(
        lookup_enduse,
        aggregated_container,
        full_sim_data,
        time_resolution,
        per_region,
        per_sector,
        per_enduse
    ):
    """Function to read from full simulation data specific demands

    Argument
    --------
    lookup_enduse : dict
        Enduse lookup
    aggregated_container : dict
        Container to aggregate
    full_sim_data : array
         Modelling results per submodel, enduse, region, fueltype, 8760h
    time_resolution : str
        Either 'annual', 'hourly', '360_24_h', '8760_h'
    """
    for enduse_array_yr, reg_fueltype_8760h in enumerate(full_sim_data):

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
                    aggregated_container[enduse_array_yr] += demand
                else:
                    aggregated_container += demand
            else:
                # Sum across all regions
                demand = np.sum(demand, axis=1)

                # Get enduse str
                enduse_str = get_enduse_from_array_nr(enduse_array_yr, lookup_enduse)

                if per_enduse:
                    aggregated_container[enduse_str] += demand
                else:
                    aggregated_container += demand

    return aggregated_container
