"""Script to disaggregate national data into regional data
"""
import logging
import copy
from collections import defaultdict
from energy_demand.profiles import hdd_cdd
from energy_demand.basic import testing_functions
from energy_demand.basic import lookup_tables
from energy_demand.read_write import data_loader
from energy_demand.scripts import init_scripts

def disaggregate_demand(data):
    """Disaggregated demand

    Arguments
    ----------
    data : dict
        Data

    Returns
    --------
    disagg : dict
        Disaggregated energy demand
    """
    disagg = {}

    # ===========================================
    # I. Disaggregation
    # ===========================================

    # Load data for disaggregateion
    data['scenario_data']['employment_stats'] = data_loader.read_employment_stats(
        data['paths']['path_employment_statistics'])

    # Load population data for disaggregation
    pop_for_disagg = data['pop_for_disag']

    # Disaggregate fuel for all regions
    disagg['residential'], disagg['service'], disagg['industry'] = disaggregate_base_demand(
        pop_for_disagg,
        data['regions'],
        data['fuels'],
        data['scenario_data'],
        data['assumptions'],
        data['reg_coord'],
        data['weather_stations'],
        data['temp_data'],
        data['sectors'],
        data['enduses'],
        data['service_building_count'])

    # Sum demand across all sectors for every region
    disagg['ss_fuel_disagg_sum_all_sectors'] = init_scripts.sum_across_sectors_all_regs(
        disagg['service'])

    disagg['is_aggr_fuel_sum_all_sectors'] = init_scripts.sum_across_sectors_all_regs(
        disagg['industry'])

    # Sum demand across all submodels and sectors for every region
    disagg['tot_disaggregated_regs'] = init_scripts.sum_across_all_submodels_regs(
        data['lookups']['fueltypes_nr'],
        data['regions'],
        [disagg['residential'],
        disagg['service'],
        disagg['industry']])

    disagg['tot_disaggregated_regs_residenital'] = init_scripts.sum_across_all_submodels_regs(
        data['lookups']['fueltypes_nr'],
        data['regions'],
        [disagg['residential']])

    disagg['tot_disaggregated_regs_non_residential'] = init_scripts.sum_across_all_submodels_regs(
        data['lookups']['fueltypes_nr'],
        data['regions'],
        [disagg['service'], disagg['industry']])

    return disagg

def replace_msoa_reg_with_lad(region):
    """Replace mosa with corresponding LAD
    """
    lu_lad_msoa = lookup_tables.lad_msoa_mapping()

    for reg_lad, msoas_lad in lu_lad_msoa.items():
        if region in list(msoas_lad):
            #logging.info("Replaced msoa region %s with lad region %s", region, reg_lad)
            region = reg_lad
            break

    return region

def disaggregate_base_demand(
        pop_for_disagg,
        regions,
        fuels,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        sectors,
        enduses,
        service_building_count
    ):
    """This function disaggregates fuel demand based on
    region specific parameters for the base year. The residential,
    service and industry demand is disaggregated according to
    different factors.

    Arguments
    ----------
    pop_for_disagg : dict
        Population of years
    regions : list
        Regions
    fuels : dict
        Fuels
    scenario_data : dict
        Scenario data
    assumptions : obj
        Assumptions
    reg_coord : dict
        Region coordinates
    weather_stations : dict
        Weather stations
    temp_data : dict
        Temperature data
    sectors : dict
        Sectors per submodel
    enduses : dict
        Enduses per submodel
    service_building_count :

    Returns
    -------
    data : dict
    """
    # -------------------------------------
    # Factors to choose for disaggregation
    # -------------------------------------
    crit_limited_disagg_pop = False      # Only population
    crit_limited_disagg_pop_hdd = True   # Only population and HDD
    crit_full_disagg = False             # Use floor area as well
    census_disagg = True                 # Disagregatte is_demand with census statistics

    # Residential
    rs_fuel_disagg = rs_disaggregate(
        regions,
        fuels['residential'],
        scenario_data,
        pop_for_disagg,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        enduses['residential'],
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop,
        crit_full_disagg)

    # Service
    ss_fuel_disagg = ss_disaggregate(
        fuels['service'],
        service_building_count,
        assumptions,
        scenario_data,
        pop_for_disagg,
        regions,
        reg_coord,
        temp_data,
        weather_stations,
        enduses['service'],
        sectors['service'],
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop,
        crit_full_disagg)

    # Industry
    is_fuel_disagg = is_disaggregate(
        assumptions,
        temp_data,
        reg_coord,
        weather_stations,
        fuels['industry'],
        regions,
        enduses['industry'],
        sectors['industry'],
        scenario_data['employment_stats'],
        pop_for_disagg,
        census_disagg=census_disagg)

    logging.info("Finished disaggregation")
    return dict(rs_fuel_disagg), dict(ss_fuel_disagg), dict(is_fuel_disagg)

def ss_disaggregate(
        ss_national_fuel,
        service_building_count,
        assumptions,
        scenario_data,
        pop_for_disagg,
        regions,
        reg_coord,
        temp_data,
        weather_stations,
        enduses,
        sectors,
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop,
        crit_full_disagg
    ):
    """Disaggregate fuel for service submodel (per enduse and sector)

    Outputs
    -------
    ss_fuel_disagg : dict
        region, Enduse, Sectors
    """
    logging.debug("... disaggregate service demand")
    ss_fuel_disagg = {}

    # ---------------------------------------
    # Calculate heating degree days for regions
    # ---------------------------------------
    ss_hdd_individ_region = hdd_cdd.get_hdd_country(
        t_base_heating=assumptions.t_bases.ss_t_heating_by,
        regions=regions,
        temp_data=temp_data,
        reg_coord=reg_coord,
        weather_stations=weather_stations)

    ss_cdd_individ_region = hdd_cdd.get_cdd_country(
        t_base_cooling=assumptions.t_bases.ss_t_cooling_by,
        regions=regions,
        temp_data=temp_data,
        reg_coord=reg_coord,
        weather_stations=weather_stations)

    # ---------------------------------------------
    # Get all regions with floor area data
    # ---------------------------------------------
    regions_with_floorarea = list(regions)
    for reg in assumptions.ss_regions_without_floorarea:
        regions_with_floorarea.remove(reg)

    # ---------------------------------------
    # Overall disaggregation factors per enduse and sector
    # ---------------------------------------
    ss_fuel_disagg = {}
    ss_fuel_disagg_only_pop = ss_disaggr(
        all_regions=regions,
        regions=assumptions.ss_regions_without_floorarea,
        sectors=sectors,
        enduses=enduses,
        base_yr=assumptions.base_yr,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disagg,
        service_building_count=service_building_count,
        ss_hdd_individ_region=ss_hdd_individ_region,
        ss_cdd_individ_region=ss_cdd_individ_region,
        ss_national_fuel=ss_national_fuel,
        crit_limited_disagg_pop=False,      # Set to False
        crit_limited_disagg_pop_hdd=True,   # Set to True
        crit_full_disagg=False)
    ss_fuel_disagg.update(ss_fuel_disagg_only_pop)

    # Substract from national fuel already disaggregated fuel
    ss_national_fuel_remaining = copy.deepcopy(ss_national_fuel)
    for enduse in ss_national_fuel:
        for sector in ss_national_fuel[enduse]:
            for reg in ss_fuel_disagg:
                ss_national_fuel_remaining[enduse][sector] -= ss_fuel_disagg[reg][enduse][sector]

    # Disaggregate with floor area
    ss_fuel_disagg_full_data = ss_disaggr(
        all_regions=regions_with_floorarea,
        regions=regions_with_floorarea,
        sectors=sectors,
        enduses=enduses,
        base_yr=assumptions.base_yr,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disagg,
        service_building_count=service_building_count,
        ss_hdd_individ_region=ss_hdd_individ_region,
        ss_cdd_individ_region=ss_cdd_individ_region,
        ss_national_fuel=ss_national_fuel_remaining,
        crit_limited_disagg_pop=crit_limited_disagg_pop,
        crit_limited_disagg_pop_hdd=crit_limited_disagg_pop_hdd,
        crit_full_disagg=crit_full_disagg)
    ss_fuel_disagg.update(ss_fuel_disagg_full_data)

    # -----------------
    # Check if total fuel is the same before and after aggregation
    #------------------
    testing_functions.control_disaggregation(
        ss_fuel_disagg, ss_national_fuel, enduses, sectors)

    return dict(ss_fuel_disagg)

def ss_disaggr(
        all_regions,
        regions,
        sectors,
        enduses,
        base_yr,
        scenario_data,
        pop_for_disagg,
        service_building_count,
        ss_hdd_individ_region,
        ss_cdd_individ_region,
        ss_national_fuel,
        crit_limited_disagg_pop,
        crit_limited_disagg_pop_hdd,
        crit_full_disagg
    ):
    """Disaggregating
    """
    ss_fuel_disagg = {}

    # Total floor area for every enduse per sector
    '''national_floorarea_by_sector = {}
    for sector in sectors:
        national_floorarea_by_sector[sector] = 0
        for region in regions:
            national_floorarea_by_sector[sector] += scenario_data['floor_area']['ss_floorarea'][base_yr][region][sector]'''

    tot_pop = 0
    tot_cdd = 0
    tot_hdd = 0
    tot_floor_area = {}
    tot_floor_area_pop = {}
    tot_pop_hdd = {}
    tot_pop_cdd = {}
    tot_floor_area_hdd = {}
    tot_floor_area_cdd = {}
    tot_building_cnt = {}

    lu_tables = lookup_tables.basic_lookups()
    lu_building_cnt = lu_tables['building_cnt_lu']

    for sector in sectors:
        tot_floor_area[sector] = 0
        tot_floor_area_pop[sector] = 0
        tot_pop_hdd[sector] = 0
        tot_pop_cdd[sector] = 0
        tot_floor_area_hdd[sector] = 0
        tot_floor_area_cdd[sector] = 0
        tot_building_cnt[sector] = 0

    for region in all_regions:
        reg_hdd = ss_hdd_individ_region[region]
        reg_cdd = ss_cdd_individ_region[region]
        #reg_pop = scenario_data['population'][base_yr][region]
        reg_pop = pop_for_disagg[base_yr][region]
        tot_pop += reg_pop
        tot_cdd += reg_cdd
        tot_hdd += reg_hdd

        for sector in sectors:

            # Sector specific ino
            reg_floor_area = scenario_data['floor_area']['ss_floorarea'][base_yr][region][sector]

            try:
                nr_sector_cnt_building = lu_building_cnt[sector]
                reg_sector_building_cnt = service_building_count[nr_sector_cnt_building][region]
                tot_building_cnt[sector] += reg_sector_building_cnt
            except KeyError:
                #logging.debug("No building data for region {}".format(region))
                pass

            # National disaggregation factors
            tot_floor_area[sector] += reg_floor_area
            tot_floor_area_pop[sector] += reg_floor_area * reg_pop
            tot_floor_area_hdd[sector] += reg_floor_area * reg_hdd
            tot_pop_hdd[sector] += reg_pop * reg_hdd
            tot_pop_cdd[sector] += reg_pop * reg_cdd
            tot_floor_area_cdd[sector] += reg_floor_area * reg_cdd

    # ---------------------------------------
    # Disaggregate according to enduse
    # ---------------------------------------
    for region in regions:
        ss_fuel_disagg[region] = defaultdict(dict)

        # Regional factors
        reg_hdd = ss_hdd_individ_region[region]
        reg_cdd = ss_cdd_individ_region[region]
        #reg_pop = scenario_data['population'][base_yr][region]
        reg_pop = pop_for_disagg[base_yr][region]
        p_pop = reg_pop / tot_pop

        for enduse in enduses:
            for sector in sectors:
                if crit_limited_disagg_pop and not crit_limited_disagg_pop_hdd and not crit_full_disagg:

                    # ----
                    #logging.debug(" ... Disaggregation ss: populaton")
                    # ----
                    reg_diasg_factor = p_pop

                elif crit_limited_disagg_pop_hdd and not crit_full_disagg:

                    # ----
                    #logging.debug(" ... Disaggregation ss: populaton, HDD")
                    # ----
                    if enduse == 'ss_cooling_humidification':
                        reg_diasg_factor = (reg_pop * reg_cdd) / tot_pop_cdd[sector]

                    elif enduse == 'ss_space_heating':
                        reg_diasg_factor = (reg_pop * reg_hdd) / tot_pop_hdd[sector]
                    else:
                        reg_diasg_factor = p_pop

                elif crit_full_disagg:

                    reg_floor_area = scenario_data['floor_area']['ss_floorarea'][base_yr][region][sector]

                    # ----
                    # logging.debug(" ... Disaggregation ss: populaton, HDD, floor_area")
                    # ----
                    if enduse == 'ss_cooling_humidification':
                        reg_diasg_factor = (reg_floor_area * reg_cdd) / tot_floor_area_cdd[sector]
                    elif enduse == 'ss_space_heating':
                        reg_diasg_factor = (reg_floor_area * reg_hdd) / tot_floor_area_hdd[sector]
                    elif enduse == 'ss_lighting':
                        reg_diasg_factor = reg_floor_area / tot_floor_area[sector]
                    else:

                        # Disaggregate with population
                        #reg_diasg_factor = p_pop

                        # Disaggregate with nr of buildings
                        nr_sector_cnt_building = lu_building_cnt[sector]
                        reg_sector_building_cnt = service_building_count[nr_sector_cnt_building][region]
                        p_reg_sector_building_cnt = reg_sector_building_cnt / tot_building_cnt[sector]

                        reg_diasg_factor = p_reg_sector_building_cnt

                ss_fuel_disagg[region][enduse][sector] = ss_national_fuel[enduse][sector] * reg_diasg_factor

    return dict(ss_fuel_disagg)

def is_disaggregate(
        assumptions,
        temp_data,
        reg_coord,
        weather_stations,
        is_national_fuel,
        regions,
        enduses,
        sectors,
        employment_statistics,
        pop_for_disagg,
        census_disagg
    ):
    """Disaggregate industry related fuel for sector and enduses with
    employment statistics

    base_yr : int
        Base year
    is_national_fuel : dict
        Fuel
    regions : list
        Regions
    enduses : list
        Enduses
    sectors : list
        Sectors
    employment_statistics : dict
        Employment statistics
    crit_limited_disagg_pop : bool
        Criteria which diassgregation method
    crit_full_disagg : bool
        Criteria which diassgregation method

    Returns
    ---------
    is_fuel_disagg : dict
        reg, enduse, sector
    """
    is_hdd_individ_region = hdd_cdd.get_hdd_country(
        t_base_heating=assumptions.t_bases.is_t_heating_by,
        regions=regions,
        temp_data=temp_data,
        reg_coord=reg_coord,
        weather_stations=weather_stations)
    logging.debug("... disaggregate industry demand")

    is_fuel_disagg = {}

    # # Calculate total population of all regions
    tot_pop = 0
    tot_pop_hdd = 0
    for region in regions:
        tot_pop_hdd +=pop_for_disagg[assumptions.base_yr][region] * is_hdd_individ_region[region]
        tot_pop += pop_for_disagg[assumptions.base_yr][region]

    if not census_disagg:

        # ---
        # Disaggregate only with population
        # ---
        for region in regions:
            is_fuel_disagg[region] = {}

            reg_pop = pop_for_disagg[assumptions.base_yr][region]

            for enduse in enduses:
                is_fuel_disagg[region][enduse] = {}

                for sector in sectors:
                    if enduse == 'is_space_heating':
                        hdd_reg = is_hdd_individ_region[region]
                        reg_disagg_f = (hdd_reg * reg_pop) / tot_pop_hdd
                        is_fuel_disagg[region][enduse][sector] = is_national_fuel[enduse][sector] * reg_disagg_f
                    else:
                        reg_disagg_f = reg_pop / tot_pop
                        is_fuel_disagg[region][enduse][sector] = is_national_fuel[enduse][sector] * reg_disagg_f

        return is_fuel_disagg

    else:
        #logging.debug(" ... Disaggregation is: Employment statistics")
        # -----
        # Disaggregate with employment statistics
        # The BEIS sectors are matched with census data sectors {ECUK industry sectors: 'Emplyoment sectors'}
        sectormatch_ecuk_with_census = {

            # Significant improvement
            'mining': 'B', #'B',
            'food_production': 'C10-12',
            'pharmaceuticals': 'M',
            'computer': 'C26-30',
            'leather': 'C13-15',
            'wearing_appeal': 'C13-15',

            # Improvement
            'basic_metals': 'C',
            'non_metallic_mineral_products': 'C',
            'electrical_equipment': 'C26-30',
            'printing': 'C',
            'rubber_plastics': 'C19-22',
            'chemicals': 'C19-22',
            'wood': 'C16,17',
            'paper': 'C16,17',

            # Worse and better
            'fabricated_metal_products': 'C',   # Gas better, elec worse test C23-25  previous 'C'
            'textiles': 'C13-15',               # Gas better, elec worse
            'motor_vehicles': 'G',              # Gas better, elec worse

            # Unclear
            'machinery': None,                  # 'C'
            'tobacco': None,                    # 'C10-12'
            'other_transport_equipment': None,  # 'H'
            'other_manufacturing': None,        # 'C18,31,32'
            'water_collection_treatment': None, # 'E'
            'waste_collection': None,           # 'E'
            'furniture': None,                  # C18,31,32
            'beverages': None
        }
        # ----------------------------------------
        # Summarise national employment per sector
        # ----------------------------------------
        tot_national_sector_employment = {}
        tot_national_sector_employment_hdd = {}
        for region in regions:
            is_hdd = is_hdd_individ_region[region]

            # -------------------------------------------------------------------
            # In case MSOA are provided as input, the corresponing LAD is searched
            # -------------------------------------------------------------------
            region_remapped = replace_msoa_reg_with_lad(region)

            for employment_sector, employment in employment_statistics[region_remapped].items():
                try:
                    tot_national_sector_employment[employment_sector] += employment
                    tot_national_sector_employment_hdd[employment_sector] += employment * is_hdd
                except KeyError:
                    tot_national_sector_employment[employment_sector] = employment
                    tot_national_sector_employment_hdd[employment_sector] = employment * is_hdd

        # --------------------------------------------------
        # Disaggregate per region with employment statistics
        # --------------------------------------------------
        for region in regions:
            is_fuel_disagg[region] = {}

            #reg_pop = scenario_data['population'][assumptions.base_yr][region]
            reg_pop = pop_for_disagg[assumptions.base_yr][region]

            # Iterate sector
            for enduse in enduses:
                is_fuel_disagg[region][enduse] = {}

                for sector in sectors:

                    # ---------------------------------
                    # Try to match  with sector, otherwise disaggregate with population
                    # ----------------------------------
                    matched_sector = sectormatch_ecuk_with_census[sector]

                    # Disaggregate with population
                    if not matched_sector:

                        if enduse == 'is_space_heating':
                            hdd_reg = is_hdd_individ_region[region]
                            reg_disagg_f = (hdd_reg * reg_pop) / tot_pop_hdd
                            is_fuel_disagg[region][enduse][sector] = is_national_fuel[enduse][sector] * reg_disagg_f
                        else:
                            reg_disagg_f = reg_pop / tot_pop
                            is_fuel_disagg[region][enduse][sector] = is_national_fuel[enduse][sector] * reg_disagg_f
                    else:
                        # -------------------------------------------------------------------
                        # In case MSOA are provided as input, the corresponing LAD is searched
                        # -------------------------------------------------------------------
                        region_remapped = replace_msoa_reg_with_lad(region)

                        reg_sector_employment = employment_statistics[region_remapped][matched_sector]

                        if enduse == 'is_space_heating':
                            national_sector_employment_hdd = tot_national_sector_employment_hdd[matched_sector]
                            hdd_reg = is_hdd_individ_region[region]
                            reg_disagg_f = (hdd_reg * reg_sector_employment) / national_sector_employment_hdd
                        else:
                            national_sector_employment = tot_national_sector_employment[matched_sector]
                            try:
                                reg_disagg_f = reg_sector_employment / national_sector_employment
                            except ZeroDivisionError:
                                reg_disagg_f = 0 #No employment for this sector for this region

                        # Disaggregated national fuel
                        is_fuel_disagg[region][enduse][sector] = is_national_fuel[enduse][sector] * reg_disagg_f

    testing_functions.control_disaggregation(
        is_fuel_disagg,
        is_national_fuel,
        enduses,
        sectors)

    logging.debug("... finished disaggregateing industry demand")
    return is_fuel_disagg

def rs_disaggregate(
        regions,
        rs_national_fuel,
        scenario_data,
        pop_for_disagg,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        enduses,
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop,
        crit_full_disagg
    ):
    """Disaggregate residential fuel demand

    Arguments
    ----------
    regions : dict
        Regions
    rs_national_fuel : dict
        Fuel per enduse for residential submodel

    Returns
    -------
    rs_fuel_disagg : dict
        Disaggregated fuel per enduse for every region (fuel[region][enduse])

    Note
    -----
    Used disaggregation factors for residential according
    to enduse (see Documentation)
    """
    logging.debug("... disagreggate residential demand")
    rs_fuel_disagg = {}

    # ---------------------------------------
    # Calculate heating degree days for regions
    # ---------------------------------------
    rs_hdd_individ_region = hdd_cdd.get_hdd_country(
        t_base_heating=assumptions.t_bases.rs_t_heating_by,
        regions=regions,
        temp_data=temp_data,
        reg_coord=reg_coord,
        weather_stations=weather_stations)

    # ---------------------------------------
    # Get all regions with  floor area data
    # ---------------------------------------
    regions_with_floorarea = list(regions)
    for reg in assumptions.rs_regions_without_floorarea:
        regions_with_floorarea.remove(reg)

    # ====================================
    # Disaggregate for region without floor
    # area by population and hdd (set crit_full_disagg as False)
    # ====================================
    rs_fuel_disagg_only_pop = rs_disaggr(
        all_regions=regions,
        regions=assumptions.rs_regions_without_floorarea,
        base_yr=assumptions.base_yr,
        rs_hdd_individ_region=rs_hdd_individ_region,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disagg,
        rs_national_fuel=rs_national_fuel,
        crit_limited_disagg_pop=False, #True, #False,
        crit_limited_disagg_pop_hdd=True, #True, #Set to true
        crit_full_disagg=False)
    rs_fuel_disagg.update(rs_fuel_disagg_only_pop)

    # Substract fuel for regions where only population was used for disaggregation from total
    rs_national_fuel_remaining = copy.deepcopy(rs_national_fuel)
    for enduse in rs_national_fuel:
        for reg in rs_fuel_disagg:
            rs_national_fuel_remaining[enduse] -= rs_fuel_disagg[reg][enduse]

    # ====================================
    # Disaggregate for region with floor area
    # ====================================
    rs_fuel_disagg_full_data = rs_disaggr(
        all_regions=regions_with_floorarea,
        regions=regions_with_floorarea,
        base_yr=assumptions.base_yr,
        rs_hdd_individ_region=rs_hdd_individ_region,
        scenario_data=scenario_data,
        pop_for_disagg=pop_for_disagg,
        rs_national_fuel=rs_national_fuel_remaining,
        crit_limited_disagg_pop=crit_limited_disagg_pop,
        crit_limited_disagg_pop_hdd=crit_limited_disagg_pop_hdd,
        crit_full_disagg=crit_full_disagg)
    rs_fuel_disagg.update(rs_fuel_disagg_full_data)

    # -----------------
    # Check if total fuel is the same before and after aggregation
    #------------------ 
    testing_functions.control_disaggregation(
        rs_fuel_disagg, rs_national_fuel, enduses)

    return rs_fuel_disagg

def rs_disaggr(
        all_regions,
        regions,
        base_yr,
        rs_hdd_individ_region,
        scenario_data,
        pop_for_disagg,
        rs_national_fuel,
        crit_limited_disagg_pop,
        crit_limited_disagg_pop_hdd,
        crit_full_disagg
    ):
    """Disaggregate residential enduses
    """
    fuel_disagg = defaultdict(dict)

    total_pop = 0
    total_hdd_floorarea = 0
    total_floor_area = 0
    total_pop_hdd = 0
    total_hdd = 0

    for region in all_regions:
        reg_hdd = rs_hdd_individ_region[region]
        reg_floor_area = scenario_data['floor_area']['rs_floorarea'][base_yr][region]
        #reg_pop = scenario_data['population'][base_yr][region]
        reg_pop = pop_for_disagg[base_yr][region]

        # National dissagregation factors
        total_hdd_floorarea += reg_hdd * reg_floor_area
        total_floor_area += reg_floor_area
        total_pop += reg_pop
        total_pop_hdd += reg_pop * reg_hdd
        total_hdd += reg_hdd

    # ---------------------------------------
    # Disaggregate according to enduse
    # ---------------------------------------
    for region in regions:
        reg_hdd = rs_hdd_individ_region[region]
        reg_floor_area = scenario_data['floor_area']['rs_floorarea'][base_yr][region]
        reg_hdd_floor_area = reg_hdd * reg_floor_area
        #reg_pop = scenario_data['population'][base_yr][region]
        reg_pop = pop_for_disagg[base_yr][region]
        reg_pop_hdd = reg_pop * reg_hdd

        p_pop = reg_pop / total_pop
        p_floor_area = reg_floor_area / total_floor_area

        # Disaggregate fuel depending on end_use
        for enduse in rs_national_fuel:
            if crit_limited_disagg_pop and not crit_limited_disagg_pop_hdd and not crit_full_disagg:

                # ----------------------------------
                #logging.debug(" ... Disaggregation rss: populaton")
                # ----------------------------------
                reg_diasg_factor = p_pop

            elif crit_limited_disagg_pop_hdd and not crit_full_disagg:

                # -------------------
                #logging.debug(" ... Disaggregation rss: populaton, hdd")
                # -------------------
                if enduse == 'rs_space_heating':
                    reg_diasg_factor = reg_pop_hdd / total_pop_hdd
                else:
                    reg_diasg_factor = p_pop

            elif crit_full_disagg:

                # -------------------
                #logging.debug(" ... Disaggregation rss: populaton, hdd, floor_area")
                # -------------------
                if enduse == 'rs_space_heating':
                    reg_diasg_factor = reg_hdd_floor_area / total_hdd_floorarea
                elif enduse == 'rs_lighting':
                    reg_diasg_factor = p_floor_area
                else:
                    reg_diasg_factor = p_pop

            # Disaggregate
            fuel_disagg[region][enduse] = rs_national_fuel[enduse] * reg_diasg_factor

    return dict(fuel_disagg)

def write_disagg_fuel(path_to_txt, data):
    """Write out disaggregated fuel

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}".format(
        'region', 'enduse', 'fueltypes', 'fuel') + '\n')

    for region, enduses in data.items():
        for enduse, fuels in enduses.items():
            for fueltype, fuel in enumerate(fuels):
                file.write("{}, {}, {}, {}".format(
                    str.strip(region),
                    str.strip(enduse),
                    str(int(fueltype)),
                    str(float(fuel)) + '\n'))
    file.close()

    return

def write_disagg_fuel_ts(path_to_txt, data):
    """Write out disaggregated fuel

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}".format(
        'region', 'fueltypes', 'fuel') + '\n')

    for region, fuels in data.items():
        for fueltype, fuel in enumerate(fuels):
            file.write("{}, {}, {}".format(
                str.strip(region), str(int(fueltype)), str(float(fuel)) + '\n')
                      )
    file.close()

    return

def write_disagg_fuel_sector(path_to_txt, data):
    """Write out disaggregated fuel

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}, {}".format(
        'region', 'enduse', 'sector', 'fueltypes', 'fuel') + '\n')

    for region, sectors in data.items():
        for sector, enduses in sectors.items():
            for enduse, fuels in enduses.items():
                for fueltype, fuel in enumerate(fuels):
                    file.write("{}, {}, {}, {}, {}".format(
                        str.strip(region),
                        str.strip(enduse),
                        str.strip(sector),
                        str(int(fueltype)),
                        str(float(fuel)) + '\n'))
    file.close()

    return
