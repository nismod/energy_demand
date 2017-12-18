"""Energy Model
==============

The main function executing all the submodels of the energy demand model
"""
import logging
from collections import defaultdict
import numpy as np
import energy_demand.enduse_func as endusefunctions
from energy_demand.geography.region import Region
from energy_demand.geography.weather_region import WeatherRegion
from energy_demand.dwelling_stock import dw_stock
from energy_demand.geography.weather_station_location import get_closest_station
from energy_demand.basic import testing_functions as testing
from energy_demand.profiles import load_profile, load_factors
from energy_demand.charts import figure_HHD_gas_demand

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
        data['non_regional_lp_stock'] = load_profile.create_load_profile_stock(
            data['tech_lp'], data['assumptions'], data['sectors'])

        # Weather Regions
        weather_regions = {}
        for weather_region_name in data['weather_stations']:
            weather_regions[weather_region_name] = WeatherRegion(
                weather_region_name=weather_region_name,
                sim_param=data['sim_param'],
                assumptions=data['assumptions'],
                lookups=data['lookups'],
                all_enduses=data['enduses'],
                temp_by=data['temp_data'][weather_region_name],
                tech_lp=data['tech_lp'],
                sectors=data['sectors'])

        # --------------
        # Dwelling stock
        # --------------
        if data['criterias']['virtual_building_stock_criteria']:
            logging.info("... Generate virtual dwelling stock for base year")

            data['rs_dw_stock'] = defaultdict(dict)
            data['ss_dw_stock'] = defaultdict(dict)
            for region_name in region_names:
                data['rs_dw_stock'][region_name][data['sim_param']['base_yr']] = dw_stock.rs_dw_stock(
                    region_name, data, data['sim_param']['base_yr'], data['sim_param']['base_yr'])
                data['ss_dw_stock'][region_name][data['sim_param']['base_yr']] = dw_stock.ss_dw_stock(
                    region_name, data, data['sim_param']['base_yr'], data['sim_param']['base_yr'])

                data['rs_dw_stock'][region_name][self.curr_yr] = dw_stock.rs_dw_stock(region_name, data, self.curr_yr, data['sim_param']['base_yr'])
                data['ss_dw_stock'][region_name][self.curr_yr] = dw_stock.ss_dw_stock(region_name, data, self.curr_yr, data['sim_param']['base_yr'])
            logging.info("... finished virtual dwelling stock for base year")
        else:
            # -------------------------------------
            # Create dwelling stock from NEWCASTLE
            # -------------------------------------
            # Create dwelling stock from imported data from newcastle

            #data['rs_dw_stock'][region_name][self.curr_yr] = dw_stock.createNEWCASTLE_dwelling_stock(
            # self.curr_yr,
            # region_name,
            # )
            #data['ss_dw_stock'][region_name][self.curr_yr] = dw_stock.createNEWCASTLE_dwelling_stock(self.curr_yr)
            pass

        # ---------------------------------------------
        # Initialise and iterate over years
        # ---------------------------------------------
        fueltypes_nr = data['lookups']['fueltypes_nr']
        yearhours_nrs = data['assumptions']['model_yearhours_nrs']
        yeardays_nrs = data['assumptions']['model_yeardays_nrs']
        reg_nrs = data['reg_nrs']

        ed_fueltype_regs_yh = np.zeros((fueltypes_nr, reg_nrs, yearhours_nrs), dtype=float)
        ed_fueltype_national_yh = np.zeros((fueltypes_nr, yeardays_nrs, 24), dtype=float)
        tot_peak_enduses_fueltype = np.zeros((fueltypes_nr, 24), dtype=float)
        tot_fuel_y_max_enduses = np.zeros((fueltypes_nr), dtype=float)
        tot_fuel_y_enduse_specific_h = {}
        reg_load_factor_y = np.zeros((fueltypes_nr, reg_nrs), dtype=float)
        reg_load_factor_yd = np.zeros((fueltypes_nr, reg_nrs, yeardays_nrs), dtype=float)
        reg_load_factor_seasons = {
            'summer' : np.zeros((fueltypes_nr, reg_nrs), dtype=float),
            'spring': np.zeros((fueltypes_nr, reg_nrs), dtype=float),
            'winter': np.zeros((fueltypes_nr, reg_nrs), dtype=float),
            'autumn': np.zeros((fueltypes_nr, reg_nrs), dtype=float)}

        averaged_h = {
            'summer' : np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float),
            'spring': np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float),
            'winter': np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float),
            'autumn': np.zeros((fueltypes_nr, reg_nrs, 24), dtype=float)}

        for array_nr_region, region_name in enumerate(region_names):
            logging.info("... Generate region %s for year %s", region_name, self.curr_yr)

            # ----------------------
            # Simulate region
            # ----------------------
            region_submodels = simulate_region(
                region_name,
                data,
                weather_regions)

            # ----------------------
            # Summarise functions
            # ----------------------
            logging.debug("... start summing")

            # Sum across all regions, all enduse and sectors sum_reg
            # [fueltype, region, fuel_yh], [fueltype, fuel_yh]
            ed_fueltype_regs_yh, fuel_region_yh = fuel_regions_fueltype(
                ed_fueltype_regs_yh,
                data['lookups'],
                region_name,
                array_nr_region,
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'],
                region_submodels)

            # Sum across all regions, all enduse and sectors
            ed_fueltype_national_yh = fuel_aggr(
                ed_fueltype_national_yh,
                'fuel_yh',
                region_submodels,
                'no_sum',
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            # Sum across all regions and calculate peak dh shape per fueltype
            tot_peak_enduses_fueltype = fuel_aggr(
                tot_peak_enduses_fueltype,
                'fuel_peak_dh',
                region_submodels,
                'no_sum',
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            tot_fuel_y_max_enduses = fuel_aggr(
                tot_fuel_y_max_enduses,
                'fuel_peak_h',
                region_submodels,
                'no_sum',
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            # Sum across all regions and provide specific enduse
            tot_fuel_y_enduse_specific_h = sum_enduse_all_regions(
                tot_fuel_y_enduse_specific_h,
                'fuel_yh',
                region_submodels,
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'])

            # --------------------------------------
            # Calculate averaged hour profile per season
            # --------------------------------------
            averaged_h = averaged_season_hourly(
                averaged_h,
                fuel_region_yh,
                array_nr_region,
                data['lookups']['fueltype'].values(),
                data['assumptions']['seasons'])

            # --------------------------------------
            # Regional load factor calculations
            # --------------------------------------

            # Calculate average load for every day
            average_fuel_yd = np.mean(fuel_region_yh, axis=2)

            # Calculate load factors across all enduses (Yearly lf)
            load_factor_y = load_factors.calc_lf_y(fuel_region_yh, average_fuel_yd)

            # Calculate load factors across all enduses (Daily lf)
            load_factor_yd = load_factors.calc_lf_d(fuel_region_yh, average_fuel_yd)
            load_factor_seasons = load_factors.calc_lf_season(
                data['assumptions']['seasons'], fuel_region_yh, average_fuel_yd)

            # Copy regional load factors
            for fueltype_nr in range(data['lookups']['fueltypes_nr']):
                reg_load_factor_y[fueltype_nr][array_nr_region] = load_factor_y[fueltype_nr]
                reg_load_factor_yd[fueltype_nr][array_nr_region] = load_factor_yd[fueltype_nr]

                for season, lf_season in load_factor_seasons.items():
                    reg_load_factor_seasons[season][fueltype_nr][array_nr_region] = lf_season[fueltype_nr]

        # -------------------------------------------------
        # Assign values for all region in EnergyModel object
        # -------------------------------------------------
        self.ed_fueltype_regs_yh = ed_fueltype_regs_yh
        self.ed_fueltype_national_yh = ed_fueltype_national_yh
        self.tot_peak_enduses_fueltype = tot_peak_enduses_fueltype
        self.tot_fuel_y_max_enduses = tot_fuel_y_max_enduses
        self.tot_fuel_y_enduse_specific_h = tot_fuel_y_enduse_specific_h

        self.reg_load_factor_y = reg_load_factor_y
        self.reg_load_factor_yd = reg_load_factor_yd
        self.reg_load_factor_seasons = reg_load_factor_seasons

        # Calculate averaged across regions
        self.averaged_h = averaged_h

        # ------------------------------
        # TESTING
        # ------------------------------
        testing.test_region_selection(self.ed_fueltype_regs_yh)

        _scrap = 0
        for reg_nr, reg in enumerate(ed_fueltype_regs_yh[2]):
            print("Region =========================" + str(reg_nr))
            print(np.sum(reg))
            _scrap += np.sum(reg)
        print("TOTAL: " + str(_scrap))

        # ------------------------------
        # Chart HDD * Pop vs actual gas demand
        # ------------------------------
        if data['criterias']['plot_HDD_chart']:
            logging.info("plot figure HDD comparison")
            figure_HHD_gas_demand.main(region_names, weather_regions, data)

def simulate_region(region_name, data, weather_regions):
    """Run submodels for a single region, return aggregate results

    Arguments
    ---------
    region_name : str
        Region name
    data : dict
        Data container
    weather_regions : oject
        Weather regions

    Returns
    -------
    region_submodels : list
        All submodel objects
    """
    logging.debug("Running model for region %s  %s  %s", region_name, data['reg_coord'][region_name]['longitude'], data['reg_coord'][region_name]['latitude'])

    # Get closest weather station to `Region`
    closest_weather_region_name = get_closest_station(
        data['reg_coord'][region_name]['longitude'],
        data['reg_coord'][region_name]['latitude'],
        data['weather_stations'])

    closest_weather_region = weather_regions[closest_weather_region_name]
    logging.debug("===============================Closest weather station: %s", closest_weather_region_name)

    region = Region(
        region_name=region_name,
        rs_fuel_disagg=data['rs_fuel_disagg'][region_name],
        ss_fuel_disagg=data['ss_fuel_disagg'][region_name],
        is_fuel_disagg=data['is_fuel_disagg'][region_name],
        weather_region=closest_weather_region)

    # --------------------
    # Residential SubModel
    # --------------------
    rs_submodel = residential_submodel(
        region,
        data,
        data['enduses']['rs_all_enduses'])

    # --------------------
    # Service SubModel
    # --------------------
    ss_submodel = service_submodel(
        region,
        data,
        data['enduses']['ss_all_enduses'],
        data['sectors']['ss_sectors'])

    # --------------------
    # Industry SubModel
    # --------------------
    is_submodel = industry_submodel(
        region,
        data,
        data['enduses']['is_all_enduses'],
        data['sectors']['is_sectors'])

    # --------
    # Submodels
    # --------
    region_submodels = [rs_submodel, ss_submodel, is_submodel]

    return region_submodels

def fuel_aggr(
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
    sector_models : list of list of Enduse
        Enduse objects to summarise
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
            for enduse in sector_model:
                if enduse.region_name == region_name:
                    input_array += get_fuels_yh(
                        enduse,
                        attribute_to_get,
                        model_yearhours_nrs,
                        model_yeardays_nrs)
    else:
        for sector_model in sector_models:
            for enduse in sector_model:
                input_array += get_fuels_yh(
                    enduse,
                    attribute_to_get,
                    model_yearhours_nrs,
                    model_yeardays_nrs)

    if sum_crit == 'no_sum':
        return input_array
    elif sum_crit == 'sum':
        return np.sum(input_array)

def get_fuels_yh(enduse_object, attribute_to_get, model_yearhours_nrs, model_yeardays_nrs):
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
    if enduse_object.crit_flat_profile:

        # Yearly fuel
        fuels_reg_y = enduse_object.fuel_y

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
        elif attribute_to_get == 'fuel_yh':
            nr_modelled_hours_factor = 1 / model_yearhours_nrs
            fast_shape = np.full(
                (enduse_object.fuel_y.shape[0], model_yeardays_nrs, 24),
                nr_modelled_hours_factor, dtype=float)
            fuels = fuels_reg_y[:, np.newaxis, np.newaxis] * fast_shape

    else: #If not flat shape, use yh load profile of enduse
        if attribute_to_get == 'fuel_peak_dh':
            fuels = enduse_object.fuel_peak_dh
        elif attribute_to_get == 'fuel_peak_h':
            fuels = enduse_object.fuel_peak_h
        elif attribute_to_get == 'shape_non_peak_y_dh':
            fuels = enduse_object.shape_non_peak_y_dh
        elif attribute_to_get == 'shape_non_peak_yd':
            fuels = enduse_object.shape_non_peak_yd
        elif attribute_to_get == 'fuel_yh':
            fuels = enduse_object.fuel_yh

    return fuels

def industry_submodel(region, data, enduse_names, sector_names):
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
    """
    logging.debug("... industry submodel start")
    submodels = []

    for sector_name in sector_names:
        for enduse_name in enduse_names:

            # Take load profile for is space heating
            # from service sector space heating
            if enduse_name == "is_space_heating":
                crit_flat_profile = False
            else:
                crit_flat_profile = True

            if data['criterias']['spatial_exliclit_diffusion']:
                service_switches = data['assumptions']['is_service_switch'][enduse_name][region.region_name]
                sig_param_tech = data['assumptions']['is_sig_param_tech'][enduse_name][region.region_name]
                tech_increased_service = data['assumptions']['is_tech_increased_service'][enduse_name][region.region_name]
                tech_decreased_share = data['assumptions']['is_tech_decreased_share'][enduse_name][region.region_name]
                tech_constant_share = data['assumptions']['is_tech_constant_share'][enduse_name][region.region_name]
            else:
                service_switches = data['assumptions']['is_service_switch'][enduse_name]
                sig_param_tech = data['assumptions']['is_sig_param_tech'][enduse_name]

                tech_increased_service = data['assumptions']['is_tech_increased_service'][enduse_name]
                tech_decreased_share = data['assumptions']['is_tech_decreased_share'][enduse_name]
                tech_constant_share = data['assumptions']['is_tech_constant_share'][enduse_name]

            # Create submodule
            submodel = endusefunctions.Enduse(
                region_name=region.region_name,
                scenario_data=data['scenario_data'],
                lookups=data['lookups'],
                assumptions=data['assumptions'],
                non_regional_lp_stock=data['non_regional_lp_stock'],
                sim_param=data['sim_param'],
                enduse=enduse_name,
                sector=sector_name,
                fuel=region.is_enduses_sectors_fuels[sector_name][enduse_name],
                tech_stock=region.is_tech_stock,
                heating_factor_y=region.is_heating_factor_y,
                cooling_factor_y=region.is_cooling_factor_y,
                service_switches=service_switches,
                fuel_tech_p_by=data['assumptions']['is_fuel_tech_p_by'][enduse_name],
                tech_increased_service=tech_increased_service,
                tech_decreased_share=tech_decreased_share,
                tech_constant_share=tech_constant_share,
                sig_param_tech=sig_param_tech,
                enduse_overall_change=data['assumptions']['enduse_overall_change'],
                criterias=data['criterias'],
                regional_lp_stock=region.is_load_profiles,
                reg_scen_drivers=data['assumptions']['scenario_drivers']['is_submodule'],
                crit_flat_profile=crit_flat_profile)

            # Add to list
            submodels.append(submodel)

    return submodels

def residential_submodel(region, data, enduse_names, sector_names=False):
    """Create the residential submodules (per enduse and region) and add them to list

    Arguments
    ----------
    data : dict
        Data container
    enduse_names : list
        All residential enduses
    sector_names : list, default=False
        Sectors

    Returns
    -------
    submodule_list : list
        List with submodules
    """
    logging.debug("... residential submodel start")

    if not sector_names:
        sector_names = ['dummy_sector']
    else:
        pass

    submodels = []

    for sector_name in sector_names:
        for enduse_name in enduse_names:

            # Change if for multiple or single regions
            if data['criterias']['spatial_exliclit_diffusion']:
                service_switches = data['assumptions']['rs_service_switch'][enduse_name][region.region_name]
                sig_param_tech = data['assumptions']['rs_sig_param_tech'][enduse_name][region.region_name]
                tech_increased_service = data['assumptions']['rs_tech_increased_service'][enduse_name][region.region_name]
                tech_decreased_share = data['assumptions']['rs_tech_decreased_share'][enduse_name][region.region_name]
                tech_constant_share = data['assumptions']['rs_tech_constant_share'][enduse_name][region.region_name]

            else:
                service_switches = data['assumptions']['rs_service_switch'][enduse_name]
                sig_param_tech = data['assumptions']['rs_sig_param_tech'][enduse_name]
                tech_increased_service = data['assumptions']['rs_tech_increased_service'][enduse_name]
                tech_decreased_share = data['assumptions']['rs_tech_decreased_share'][enduse_name]
                tech_constant_share = data['assumptions']['rs_tech_constant_share'][enduse_name]

            # Create submodule
            submodel = endusefunctions.Enduse(
                region_name=region.region_name,
                scenario_data=data['scenario_data'],
                lookups=data['lookups'],
                assumptions=data['assumptions'],
                non_regional_lp_stock=data['non_regional_lp_stock'],
                sim_param=data['sim_param'],
                enduse=enduse_name,
                sector=sector_name,
                fuel=region.rs_enduses_fuel[enduse_name],
                tech_stock=region.rs_tech_stock,
                heating_factor_y=region.rs_heating_factor_y,
                cooling_factor_y=region.rs_cooling_factor_y,
                service_switches=service_switches,
                fuel_tech_p_by=data['assumptions']['rs_fuel_tech_p_by'][enduse_name],
                tech_increased_service=tech_increased_service,
                tech_decreased_share=tech_decreased_share,
                tech_constant_share=tech_constant_share,
                sig_param_tech=sig_param_tech,
                criterias=data['criterias'],
                enduse_overall_change=data['assumptions']['enduse_overall_change'],
                regional_lp_stock=region.rs_load_profiles,
                dw_stock=data['rs_dw_stock']
            )
            submodels.append(submodel)

    return submodels

def service_submodel(region, data, enduse_names, sector_names):
    """Create the service submodules per enduse, sector and region and add to list

    Arguments
    ----------
    data : dict
        Data container
    enduse_names : list
        All residential enduses
    sector_names : list
        Service sectors

    Returns
    -------
    submodels : list
        List with submodels
    """
    logging.debug("... service submodel start")
    submodels = []

    for sector_name in sector_names:
        for enduse_name in enduse_names:
            print("Enduse Name  {}  {}".format(enduse_name, sector_name))

            # Change if single or muplite region
            if data['criterias']['spatial_exliclit_diffusion']:
                service_switches = data['assumptions']['ss_service_switch'][enduse_name][region.region_name]
                sig_param_tech = data['assumptions']['ss_sig_param_tech'][enduse_name][region.region_name]

                tech_increased_service = data['assumptions']['ss_tech_increased_service'][enduse_name][region.region_name]
                tech_decreased_share = data['assumptions']['ss_tech_decreased_share'][enduse_name][region.region_name]
                tech_constant_share = data['assumptions']['ss_tech_constant_share'][enduse_name][region.region_name]

            else:
                service_switches = data['assumptions']['ss_service_switch'][enduse_name]
                sig_param_tech = data['assumptions']['ss_sig_param_tech'][enduse_name]

                tech_increased_service = data['assumptions']['ss_tech_increased_service'][enduse_name]
                tech_decreased_share = data['assumptions']['ss_tech_decreased_share'][enduse_name]
                tech_constant_share = data['assumptions']['ss_tech_constant_share'][enduse_name]

            # Create submodule
            submodel = endusefunctions.Enduse(
                region_name=region.region_name,
                scenario_data=data['scenario_data'],
                lookups=data['lookups'],
                assumptions=data['assumptions'],
                non_regional_lp_stock=data['non_regional_lp_stock'],
                sim_param=data['sim_param'],
                enduse=enduse_name,
                sector=sector_name,
                fuel=region.ss_enduses_sectors_fuels[sector_name][enduse_name],
                tech_stock=region.ss_tech_stock,
                heating_factor_y=region.ss_heating_factor_y,
                cooling_factor_y=region.ss_cooling_factor_y,
                service_switches=service_switches,
                fuel_tech_p_by=data['assumptions']['ss_fuel_tech_p_by'][enduse_name],
                tech_increased_service=tech_increased_service,
                tech_decreased_share=tech_decreased_share,
                tech_constant_share=tech_constant_share,
                sig_param_tech=sig_param_tech,
                criterias=data['criterias'],
                enduse_overall_change=data['assumptions']['enduse_overall_change'],
                regional_lp_stock=region.ss_load_profiles,
                dw_stock=data['ss_dw_stock'])

            # Add to list
            submodels.append(submodel)

    return submodels

def fuel_regions_fueltype(
        fuel_fueltype_regions,
        lookups,
        region_name,
        array_region_nr,
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
    array_region_nr : int
        Array nr position of region to store results
    Example
    -------
    {'final_electricity_demand': np.array((regions, model_yearhours_nrs)), dtype=float}
    """
    fuels = fuel_aggr(
        np.zeros((lookups['fueltypes_nr'], model_yeardays_nrs, 24), dtype=float),
        'fuel_yh',
        all_submodels,
        'no_sum',
        model_yearhours_nrs,
        model_yeardays_nrs,
        region_name)

    # Reshape
    for fueltype_nr in lookups['fueltype'].values():
        fuel_fueltype_regions[fueltype_nr][array_region_nr] += fuels[fueltype_nr].reshape(model_yearhours_nrs)

    fuel_region = np.zeros((lookups['fueltypes_nr'], model_yeardays_nrs, 24), dtype=float)
    for fueltype_nr in lookups['fueltype'].values():
        fuel_region[fueltype_nr] = fuels[fueltype_nr]
    return fuel_fueltype_regions, fuel_region

'''def get_regional_yh(fueltypes_nr, region_name, region_enduses, model_yeardays_nrs):
    """Get yh fuel for all fueltype for a specific region of all submodels

    Arguments
    ----------
    fueltypes_nr : int
        Number of fueltypes
    region_name : str
        Name of region to get attributes
    region_enduses : list of list of Enduse
        Enduse objects for each sector (service, residential, industrial)
        in the region

    Return
    ------
    region_fuel_yh : array
        Summed fuel of a region

    Note
    ----
    - Summing function
    """
    region_fuel_yh = fuel_aggr(
        'fuel_yh',
        fueltypes_nr,
        region_enduses,
        'no_sum',
        model_yeardays_nrs,
        region_name)

    return region_fuel_yh'''

def sum_enduse_all_regions(
        input_dict,
        attribute_to_get,
        sector_models,
        model_yearhours_nrs,
        model_yeardays_nrs
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
                enduse_dict[model_object.enduse] = 0

            # Add fuel with flat load shape
            enduse_dict[model_object.enduse] += get_fuels_yh(
                model_object, attribute_to_get, model_yearhours_nrs, model_yeardays_nrs)

    return enduse_dict

def averaged_season_hourly(averaged_h, fuel_region_yh, array_nr_region, fueltypes, seasons):
    """Calculate averaged hourly values for each season

    Arguments
    ---------
    averaged_h : dict
        Averaged hours per season (season, fueltype, array_nr_reg, 24)
    fuel_region_yh : array
        Fuel of region (fueltype, yearday)
    array_nr_region : int
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
                averaged_h[season][fueltype][array_nr_region] += fuel_region_yh[fueltype][yearday]

    # Calculate average hourly values for every season
    for season, yeardays_modelled in seasons.items():
        for fueltype in fueltypes:
            averaged_h[season][fueltype][array_nr_region] = averaged_h[season][fueltype][array_nr_region] / len(yeardays_modelled)

    '''tot_h_sum = 0
    for yearday in seasons['summer']:
        tot_h_sum += fuel_region_yh[1][yearday][0]
    assert averaged_h['summer'][1][array_nr_region][0] * len(seasons['summer']) == tot_h_sum'''

    return averaged_h
