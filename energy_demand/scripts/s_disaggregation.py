"""Script to disaggregate national data into regional data
"""
import os
import logging
from collections import defaultdict
import numpy as np
from energy_demand.profiles import hdd_cdd
'''
============================================
MEthod to derive GVA/POP SERVICE FLOOR AREAS
============================================

1. Step
Get correlation between regional GVA and (regional floor area/reg pop) of every sector of base year
-- Get this correlation for every region and build national correlation

2. Step
Calculate future regional floor area demand based on GVA and pop projection
'''

def disaggregate_base_demand(
        lu_reg,
        base_yr,
        curr_yr,
        fuels,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        sectors,
        all_sectors,
        enduses,
        ss_floorarea_sector_2015_virtual_bs
    ):
    """This function disaggregates fuel demand based on
    region specific parameters for the base year. The residential,
    service and industry demand is disaggregated according to
    different factors.

    Arguments
    ----------
    data : dict
        Contains all data not provided externally

    Returns
    -------
    data : dict
    """
    def sum_fuels_before(fuel):
        """Inner function for testing purposes - sum fuel"""
        tot = 0
        for i in fuel:
            tot += np.sum(fuel[i])
        return tot

    def sum_fuels_after(reg_fuel):
        """Inner function for testing purposes - sum fuel"""
        tot = 0
        for reg in reg_fuel:
            for enduse in reg_fuel[reg].values():
                tot += np.sum(enduse)
        return tot

    # -------------------------------------
    # Factors to choose for disaggregation
    # -------------------------------------
    #If all false --> Full disaggregation
    crit_limited_disagg_pop = True         # if True: Only disaggregate with population
    crit_limited_disagg_pop_hdd = True     # If True: Disaggregate with pop and hdd
    crit_employment = True                 # If false, only with pop

    # Disaggregate residential submodel data
    rs_fuel_disagg = rs_disaggregate(
        lu_reg,
        base_yr,
        curr_yr,
        fuels['rs_fuel_raw_data_enduses'],
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop)

    # Disaggregate service submodel data
    ss_fuel_disagg = ss_disaggregate(
        fuels['ss_fuel_raw_data_enduses'],
        assumptions,
        scenario_data,
        base_yr,
        curr_yr,
        lu_reg,
        reg_coord,
        temp_data,
        weather_stations,
        enduses,
        sectors,
        all_sectors,
        ss_floorarea_sector_2015_virtual_bs,
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop)

    # Disaggregate industry submodel data with employment statistics
    is_fuel_disagg = is_disaggregate(
        base_yr,
        fuels['is_fuel_raw_data_enduses'],
        lu_reg,
        enduses,
        sectors,
        scenario_data['employment_statistics'],
        scenario_data,
        crit_limited_disagg_pop,
        crit_employment)

    # Check if total fuel is the same before and after aggregation
    np.testing.assert_almost_equal(
        sum_fuels_before(fuels['rs_fuel_raw_data_enduses']),
        sum_fuels_after(rs_fuel_disagg),
        decimal=2, err_msg="")

    return rs_fuel_disagg, ss_fuel_disagg, is_fuel_disagg

def ss_disaggregate(
        raw_fuel_sectors_enduses,
        assumptions,
        scenario_data,
        base_yr,
        curr_yr,
        lu_reg,
        reg_coord,
        temp_data,
        weather_stations,
        enduses,
        sectors,
        all_sectors,
        ss_floorarea_sector_2015_virtual_bs,
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop
    ):
    """Disaggregate fuel for service submodel (per enduse and sector)
    TODO: So far only disaggregated with
    """
    logging.debug("... disaggregate service demand")
    ss_fuel_disagg = {}

    # ---------------------------------------
    # Calculate heating degree days for regions
    # ---------------------------------------
    ss_hdd_individ_region = hdd_cdd.get_hdd_country(
        base_yr,
        curr_yr,
        lu_reg,
        temp_data,
        assumptions['base_temp_diff_params'],
        assumptions['strategy_variables']['ss_t_base_heating_future_yr'],
        assumptions['ss_t_base_heating']['ss_t_base_heating_base_yr'],
        reg_coord,
        weather_stations)

    ss_cdd_individ_region = hdd_cdd.get_cdd_country(
        base_yr,
        curr_yr,
        lu_reg,
        temp_data,
        assumptions['base_temp_diff_params'],
        assumptions['strategy_variables']['ss_t_base_cooling_future_yr'],
        assumptions['ss_t_base_cooling']['ss_t_base_cooling_base_yr'],
        reg_coord,
        weather_stations)

    # ---------------------------------------
    # Overall disaggregation factors per enduse and sector
    # ---------------------------------------
    # Total floor area for every enduse per sector
    national_floorarea_by_sector = {}
    for sector in sectors['ss_sectors']:
        national_floorarea_by_sector[sector] = 0
        for region in lu_reg:
            national_floorarea_by_sector[sector] += ss_floorarea_sector_2015_virtual_bs[region][sector]

    tot_pop = {}
    tot_floor_area = {}
    tot_floor_area_pop = {}
    tot_pop_hdd = {}
    tot_pop_cdd = {}

    for sector in all_sectors:
        tot_pop[sector] = 0
        tot_floor_area[sector] = 0
        tot_floor_area_pop[sector] = 0
        tot_pop_hdd[sector] = 0
        tot_pop_cdd[sector] = 0

        for region_name in lu_reg:

            # HDD
            reg_hdd = ss_hdd_individ_region[region_name]
            reg_cdd = ss_cdd_individ_region[region_name]

            # Floor Area of sector
            reg_floor_area = ss_floorarea_sector_2015_virtual_bs[region_name][sector]

            # Population
            reg_pop = scenario_data['population'][base_yr][region_name]

            # National disaggregation factors
            tot_pop[sector] += reg_pop #for every sector full population
            tot_floor_area[sector] += reg_floor_area
            tot_floor_area_pop[sector] += reg_floor_area * reg_pop
            tot_pop_hdd[sector] += reg_pop * reg_hdd
            tot_pop_cdd[sector] += reg_pop * reg_cdd

    # ---------------------------------------
    # Disaggregate according to enduse
    # ---------------------------------------
    for region_name in lu_reg:
        ss_fuel_disagg[region_name] = {}
        for sector in sectors['ss_sectors']:
            ss_fuel_disagg[region_name][sector] = {}
            for enduse in enduses['ss_all_enduses']:

                # Regional factors
                reg_hdd = ss_hdd_individ_region[region_name]
                reg_cdd = ss_cdd_individ_region[region_name]
                reg_floor_area = ss_floorarea_sector_2015_virtual_bs[region_name][sector]
                reg_pop = scenario_data['population'][base_yr][region_name]

                if crit_limited_disagg_pop and not crit_limited_disagg_pop_hdd:
                    logging.debug(" ... Disaggregation ss: populaton")
                    # ----
                    # Only disaggregat with population
                    # ----
                    reg_diasg_factor = reg_pop / tot_pop[sector]

                elif crit_limited_disagg_pop_hdd:
                    logging.debug(" ... Disaggregation ss: populaton, HDD")
                    # ----
                    # Only disaggregat with population and hdd and cdd
                    # ----
                    if enduse == 'ss_cooling_ventilation':
                        reg_diasg_factor = (reg_pop * reg_cdd) / tot_pop_cdd[sector]
                    elif enduse == 'ss_space_heating':
                        reg_diasg_factor = (reg_pop * reg_hdd) / tot_pop_hdd[sector]
                    else:
                        reg_diasg_factor = reg_pop / tot_pop[sector]
                else:
                    logging.debug(" ... Disaggregation ss: populaton, HDD, floor_area")
                    # ----
                    # disaggregat with pop, hdd/cdd, floor area
                    # ----
                    if enduse == 'ss_cooling_ventilation':
                        reg_diasg_factor = (reg_pop * reg_cdd) / tot_pop_cdd[sector]
                    elif enduse == 'ss_space_heating':
                        reg_diasg_factor = (reg_floor_area * reg_hdd) / tot_floor_area_pop[sector]
                    elif enduse == 'ss_lighting':
                        reg_diasg_factor = reg_floor_area / tot_floor_area[sector]
                    else:
                        reg_diasg_factor = reg_pop / tot_pop[sector]

                ss_fuel_disagg[region_name][sector][enduse] = raw_fuel_sectors_enduses[sector][enduse] * reg_diasg_factor

    # TESTING Check if total fuel is the same before and after aggregation
    control_sum1, control_sum2 = 0, 0
    for reg in ss_fuel_disagg:
        for sector in ss_fuel_disagg[reg]:
            for enduse in ss_fuel_disagg[reg][sector]:
                control_sum1 += np.sum(ss_fuel_disagg[reg][sector][enduse])

    for sector in sectors['ss_sectors']:
        for enduse in enduses['ss_all_enduses']:
            control_sum2 += np.sum(raw_fuel_sectors_enduses[sector][enduse])

    #The loaded floor area must correspond to provided fuel sectors numers
    np.testing.assert_almost_equal(
        control_sum1,
        control_sum2,
        decimal=2, err_msg=" {}  {}".format(control_sum1, control_sum2))

    return ss_fuel_disagg

def is_disaggregate(
        base_yr,
        raw_fuel_sectors_enduses,
        lu_reg,
        enduses,
        sectors,
        employment_statistics,
        scenario_data,
        crit_limited_disagg_pop,
        crit_employment
    ):
    """Disaggregate fuel for sector and enduses with
    employment statistics

    Arguments
    ---------
    raw_fuel_sectors_enduses ; dict
        Fuels

    """
    is_fuel_disagg = {}
    if crit_limited_disagg_pop and not crit_employment:
        logging.debug(" ... Disaggregation is: Population")
        # ---
        # Disaggregate only with population
        # ---
        tot_pop = 0
        for reg in lu_reg:
            tot_pop += scenario_data['population'][base_yr][reg]

        for region_name in lu_reg:
            is_fuel_disagg[region_name] = {}
            reg_pop = scenario_data['population'][base_yr][region_name]

            reg_disagg_f = reg_pop/ tot_pop

            for sector in sectors['is_sectors']:
                is_fuel_disagg[region_name][sector] = {}
                for enduse in enduses['is_all_enduses']:
                    is_fuel_disagg[region_name][sector][enduse] = raw_fuel_sectors_enduses[sector][enduse] * reg_disagg_f

        return is_fuel_disagg
    else:
        logging.debug(" ... Disaggregation is: Employment statistics")
        # -----
        # Disaggregate with employment statistics
        # -----
        logging.info("___________________________ other data for disaggregation")
        # The BEIS sectors are matched with census data sectors
        sectormatch_ecuk_with_census = {
            'wood': 'C16,17',
            'textiles': 'C13-15',
            'chemicals': 'C19-22',
            'printing': 'C',
            'electrical_equipment':'C26-30',
            'paper': 'C16,17',
            'basic_metals': 'C',
            'beverages': 'C10-12',
            'pharmaceuticals': 'M',
            'machinery': 'C26-30',
            'water_collection_treatment': 'E',
            'food_production': 'C10-12',
            'rubber_plastics': 'C19-22',
            'wearing_appeal': 'C13-15',
            'other_transport_equipment': 'H',
            'leather': 'C13-15',
            'motor_vehicles': 'G',
            'waste_collection': 'E',
            'tobacco': 'C10-12',
            'mining': 'B',
            'other_manufacturing': 'C18,31,32',
            'furniture': 'C',
            'non_metallic_minearl_products': 'C',
            'computer': 'C26-30',
            'fabricated_metal_products': 'C'}

        # ----------------------------------------
        # Summarise national employment per sector
        # ----------------------------------------
        # Initialise dict
        tot_national_sector_employment = {}
        for sectors_reg in employment_statistics.values():
            for sector in sectors_reg:
                tot_national_sector_employment[sector] = 0
            continue
        for reg in lu_reg:
            for employment_sector, employment in employment_statistics[reg].items():
                tot_national_sector_employment[employment_sector] += employment

        # --------------------------------------------------
        # Disaggregate per region with employment statistics
        # --------------------------------------------------
        for region_name in lu_reg:
            is_fuel_disagg[region_name] = {}

            # Iterate sector
            for sector in sectors['is_sectors']:
                is_fuel_disagg[region_name][sector] = {}

                # Match sector
                matched_sector = sectormatch_ecuk_with_census[sector]

                # Iterate enduse
                for enduse in enduses['is_all_enduses']:
                    national_sector_employment = tot_national_sector_employment[matched_sector]
                    reg_sector_employment = employment_statistics[region_name][matched_sector]

                    try:
                        reg_disag_factor = reg_sector_employment / national_sector_employment
                    except ZeroDivisionError:
                        reg_disag_factor = 0 #No employment for this sector for this region

                    # Disaggregated national fuel
                    national_fuel_sector_by = raw_fuel_sectors_enduses[sector][enduse]
                    is_fuel_disagg[region_name][sector][enduse] = national_fuel_sector_by * reg_disag_factor

    return is_fuel_disagg

def rs_disaggregate(
        lu_reg,
        base_yr,
        curr_yr,
        rs_national_fuel,
        scenario_data,
        assumptions,
        reg_coord,
        weather_stations,
        temp_data,
        crit_limited_disagg_pop_hdd,
        crit_limited_disagg_pop
    ):
    """Disaggregate residential fuel demand

    Arguments
    ----------
    lu_reg : dict
        Regions
    sim_param : dict
        Simulation parameters
    rs_national_fuel : dict
        Fuel per enduse for residential submodel

    Returns
    -------
    rs_fuel_disagg : dict
        Disaggregated fuel per enduse for every region (fuel[region][enduse])

    Note
    -----
    Used disaggregation factors for residential according
    to enduse (see Section XY Documentation TODO)
    """
    logging.debug("... disagreggate residential demand")

    rs_fuel_disagg = defaultdict(dict)

    # ---------------------------------------
    # Calculate heating degree days for regions
    # ---------------------------------------
    rs_hdd_individ_region = hdd_cdd.get_hdd_country(
        base_yr,
        curr_yr,
        lu_reg,
        temp_data,
        assumptions['base_temp_diff_params'],
        assumptions['strategy_variables']['rs_t_base_heating_future_yr'],
        assumptions['rs_t_base_heating']['rs_t_base_heating_base_yr'],
        reg_coord,
        weather_stations)

    # ---------------------------------------
    # Overall disaggregation factors per enduse
    # ---------------------------------------
    total_pop = 0
    total_pop_hdd = 0
    total_floor_area = 0

    for region_name in lu_reg:

        # HDD
        reg_hdd = rs_hdd_individ_region[region_name]

        # Floor Area across all sectors
        reg_floor_area = scenario_data['floor_area']['rs_floorarea_newcastle'][base_yr][region_name]

        # Population
        reg_pop = scenario_data['population'][base_yr][region_name]

        # National dissagregation factors
        total_pop += reg_pop
        total_pop_hdd += reg_pop * reg_floor_area
        total_floor_area += reg_floor_area
        #TODO: GVA?

    # ---------------------------------------
    # Disaggregate according to enduse
    # ---------------------------------------
    for region_name in lu_reg:
        reg_pop = scenario_data['population'][base_yr][region_name]
        reg_hdd = rs_hdd_individ_region[region_name]
        reg_floor_area = scenario_data['floor_area']['rs_floorarea_newcastle'][base_yr][region_name]

        # Disaggregate fuel depending on end_use
        for enduse in rs_national_fuel:
            if crit_limited_disagg_pop and not crit_limited_disagg_pop_hdd:
                logging.debug(" ... Disaggregation rss: populaton")
                # ----------------------------------
                # Only disaggregate with population
                # ----------------------------------
                reg_diasg_factor = reg_pop / total_pop

            elif crit_limited_disagg_pop_hdd:
                logging.debug(" ... Disaggregation rss: populaton, hdd")
                # -------------------
                # Disaggregation with pop and hdd
                # -------------------
                if enduse == 're_space_heating':
                    reg_diasg_factor = (reg_hdd * reg_pop) / total_pop_hdd
                else:
                    reg_diasg_factor = reg_pop / total_pop
            else:
                logging.debug(" ... Disaggregation rss: populaton, hdd, floor_area")
                # -------------------
                # Full disaggregation
                # -------------------
                if enduse == 'rs_space_heating':
                    reg_diasg_factor = (reg_hdd * reg_floor_area) / total_pop_hdd
                elif enduse == 'rs_lighting':
                    reg_diasg_factor = reg_floor_area / total_floor_area
                else:
                    reg_diasg_factor = reg_pop / total_pop

            # Disaggregate
            rs_fuel_disagg[region_name][enduse] = rs_national_fuel[enduse] * reg_diasg_factor

    return rs_fuel_disagg

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
        'region', 'enduse', 'fueltype', 'fuel') + '\n'
              )

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
        'region', 'fueltype', 'fuel') + '\n'
              )

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
        'region', 'enduse', 'sector', 'fueltype', 'fuel') + '\n')

    for region, sectors in data.items():
        for sector, enduses in sectors.items():
            for enduse, fuels in enduses.items():
                for fueltype, fuel in enumerate(fuels):
                    file.write("{}, {}, {}, {}, {}".format(
                        str.strip(region),
                        str.strip(enduse),
                        str.strip(sector),
                        str(int(fueltype)),
                        str(float(fuel)) + '\n')
                              )
    file.close()

    return

def run(data):
    """Function run script
    """
    logging.debug("... start script %s", os.path.basename(__file__))

    # Disaggregation
    rs_fuel_disagg, ss_fuel_disagg, is_fuel_disagg = disaggregate_base_demand(
        data['lu_reg'],
        data['sim_param']['base_yr'],
        data['sim_param']['curr_yr'],
        data['fuels'],
        data['scenario_data'],
        data['assumptions'],
        data['reg_coord'],
        data['weather_stations'],
        data['temp_data'],
        data['sectors'],
        data['all_sectors'],
        data['enduses'],
        data['ss_floorarea_sector_2015_virtual_bs'])

    #Write to csv file disaggregated demand
    write_disagg_fuel(
        os.path.join(data['local_paths']['dir_disattregated'], 'rs_fuel_disagg.csv'),
        rs_fuel_disagg)
    write_disagg_fuel_sector(
        os.path.join(data['local_paths']['dir_disattregated'], 'ss_fuel_disagg.csv'),
        ss_fuel_disagg)
    write_disagg_fuel_sector(
        os.path.join(data['local_paths']['dir_disattregated'], 'is_fuel_disagg.csv'),
        is_fuel_disagg)

    logging.debug("... finished script %s", os.path.basename(__file__))
    return
