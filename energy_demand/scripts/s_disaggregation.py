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
def disaggregate_base_demand(data):
    """This function disaggregates fuel demand based on region specific parameters
    for the base year

    The residential, service and industry demand is disaggregated according to
    different factors

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

    # Disaggregate residential submodel data
    data['rs_fuel_disagg'] = rs_disaggregate(
        data['lu_reg'],
        data['sim_param'],
        data,
        data['fuels']['rs_fuel_raw_data_enduses'])

    # Disaggregate service submodel data
    data['ss_fuel_disagg'] = ss_disaggregate(data, data['fuels']['ss_fuel_raw_data_enduses'])

    # Disaggregate industry submodel data
    data['is_fuel_disagg'] = is_disaggregate(data, data['fuels']['is_fuel_raw_data_enduses'])

    # Check if total fuel is the same before and after aggregation
    np.testing.assert_almost_equal(
        sum_fuels_before(data['fuels']['rs_fuel_raw_data_enduses']),
        sum_fuels_after(data['rs_fuel_disagg']),
        decimal=2, err_msg="")

    return data

def ss_disaggregate(data, raw_fuel_sectors_enduses):
    """Disaggregate fuel for service submodel (per enduse and sector)
    """
    logging.debug("... disaggregate service demand")
    ss_fuel_disagg = {}

    # ---------------------------------------
    # Calculate heating degree days for regions
    # ---------------------------------------
    ss_hdd_individ_region = hdd_cdd.get_hdd_country(
        data['sim_param'],
        data['lu_reg'],
        data['temp_data'],
        data['assumptions']['smart_meter_diff_params'],
        data['assumptions']['ss_t_base_heating'],
        data['reg_coord'],
        data['weather_stations'],)

    ss_cdd_individ_region = hdd_cdd.get_cdd_country(
        data['sim_param'],
        data['lu_reg'],
        data['temp_data'],
        data['assumptions']['smart_meter_diff_params'],
        data['assumptions']['ss_t_base_cooling'],
        data['reg_coord'],
        data['weather_stations'])

    # ---------------------------------------
    # Overall disaggregation factors per enduse and sector
    # ---------------------------------------
    # Total floor area for every enduse per sector
    national_floorarea_by_sector = {}
    for sector in data['sectors']['ss_sectors']:
        national_floorarea_by_sector[sector] = 0
        for region in data['lu_reg']:
            national_floorarea_by_sector[sector] += data['ss_sector_floor_area_by'][region][sector]

    f_ss_catering = {}
    f_ss_computing = {}
    f_ss_cooling_ventilation = {}
    f_ss_water_heating = {}
    f_ss_space_heating = {}
    f_ss_lighting = {}
    f_ss_other_electricity = {}
    f_ss_other_gas = {}

    for sector in data['all_sectors']:
        f_ss_catering[sector] = 0
        f_ss_computing[sector] = 0
        f_ss_cooling_ventilation[sector] = 0
        f_ss_water_heating[sector] = 0
        f_ss_space_heating[sector] = 0
        f_ss_lighting[sector] = 0
        f_ss_other_electricity[sector] = 0
        f_ss_other_gas[sector] = 0

        for region_name in data['lu_reg']:

            # HDD
            reg_hdd = ss_hdd_individ_region[region_name]
            reg_cdd = ss_cdd_individ_region[region_name]

            # Floor Area of sector
            reg_floor_area = data['ss_sector_floor_area_by'][region_name][sector]

            # Population
            reg_pop = data['scenario_data']['population'][data['sim_param']['base_yr']][region_name]

            #reg_hdd, reg_pop, reg_cdd, reg_floor_area = 100, 100, 100, 100

            # National disaggregation factors
            f_ss_catering[sector] += reg_pop
            f_ss_computing[sector] += reg_pop
            f_ss_cooling_ventilation[sector] += reg_pop * reg_cdd
            f_ss_water_heating[sector] += reg_pop
            f_ss_space_heating[sector] += reg_floor_area * reg_hdd
            f_ss_lighting[sector] += reg_floor_area
            f_ss_other_electricity[sector] += reg_pop
            f_ss_other_gas[sector] += reg_pop

    # ---------------------------------------
    # Disaggregate according to enduse
    # ---------------------------------------
    for region_name in data['lu_reg']:
        ss_fuel_disagg[region_name] = defaultdict(dict)
        for sector in data['sectors']['ss_sectors']:
            for enduse in data['enduses']['ss_all_enduses']:

                # HDD
                reg_hdd = ss_hdd_individ_region[region_name]
                reg_cdd = ss_cdd_individ_region[region_name]

                # Floor Area of sector
                reg_floor_area = data['ss_sector_floor_area_by'][region_name][sector]

                # Population
                reg_pop = data['scenario_data']['population'][data['sim_param']['base_yr']][region_name]

                #reg_hdd, reg_pop, reg_cdd, reg_floor_area = 100, 100, 100, 100

                if enduse == 'ss_catering':
                    reg_diasg_factor = reg_pop / f_ss_catering[sector]
                elif enduse == 'ss_computing':
                    reg_diasg_factor = reg_pop / f_ss_computing[sector]
                elif enduse == 'ss_cooling_ventilation':
                    reg_diasg_factor = (reg_pop * reg_cdd) / f_ss_cooling_ventilation[sector]
                elif enduse == 'ss_water_heating':
                    reg_diasg_factor = reg_pop / f_ss_water_heating[sector]
                elif enduse == 'ss_space_heating':
                    reg_diasg_factor = (reg_floor_area * reg_hdd) / f_ss_space_heating[sector]
                elif enduse == 'ss_lighting':
                    reg_diasg_factor = reg_floor_area / f_ss_lighting[sector]
                elif enduse == 'ss_other_electricity':
                    reg_diasg_factor = reg_pop / f_ss_other_electricity[sector]
                elif enduse == 'ss_other_gas':
                    reg_diasg_factor = reg_pop / f_ss_other_gas[sector]

                # Disaggregate (fuel * factor)
                ss_fuel_disagg[region_name][sector][enduse] = raw_fuel_sectors_enduses[sector][enduse] * reg_diasg_factor

    # TESTING Check if total fuel is the same before and after aggregation
    control_sum1, control_sum2 = 0, 0
    for reg in ss_fuel_disagg:
        for sector in ss_fuel_disagg[reg]:
            for enduse in ss_fuel_disagg[reg][sector]:
                control_sum1 += np.sum(ss_fuel_disagg[reg][sector][enduse])

    for sector in data['sectors']['ss_sectors']:
        for enduse in data['enduses']['ss_all_enduses']:
            control_sum2 += np.sum(raw_fuel_sectors_enduses[sector][enduse])

    #The loaded floor area must correspond to provided fuel sectors numers
    np.testing.assert_almost_equal(control_sum1, control_sum2, decimal=2, err_msg="")
    return ss_fuel_disagg

def is_disaggregate(data, raw_fuel_sectors_enduses):
    """Disaggregate fuel for sector and enduses with floor
    area and GVA for sectors and enduses (IMPROVE)

    Arguments
    ---------
    data : dict
        Data container
    raw_fuel_sectors_enduses ; dict
        Fuels
    #TODO: DISAGGREGATE WITH OTHER DATA
    """
    is_fuel_disagg = {}

    national_floorarea_sector = 0
    for region_name in data['lu_reg']:
        national_floorarea_sector += sum(data['ss_sector_floor_area_by'][region_name].values())

    # Iterate regions
    for region_name in data['lu_reg']:
        is_fuel_disagg[region_name] = defaultdict(dict)

        # Iterate sector
        for sector in data['sectors']['is_sectors']:

            # Sector specifid info
            reg_floorarea_sector = sum(data['ss_sector_floor_area_by'][region_name].values())

            # Iterate enduse
            for enduse in data['enduses']['is_all_enduses']:
                national_fuel_sector_by = raw_fuel_sectors_enduses[sector][enduse]

                # ----------------------
                # Disaggregating factors
                # TODO: IMPROVE. SHOW HOW IS DISAGGREGATED
                reg_disaggregation_factor = reg_floorarea_sector / national_floorarea_sector

                # Disaggregated national fuel
                reg_fuel_sector_enduse = reg_disaggregation_factor * national_fuel_sector_by
                is_fuel_disagg[region_name][sector][enduse] = reg_fuel_sector_enduse

    return is_fuel_disagg

def rs_disaggregate(lu_reg, sim_param, data, rs_national_fuel):
    """Disaggregate residential fuel demand

    Arguments
    ----------
    lu_reg : dict
        Regions
    sim_param : dict
        Simulation parameters
    data : dict
        Data container
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

    # ---------------------------------------
    # Calculate heating degree days for regions
    # ---------------------------------------
    rs_hdd_individ_region = hdd_cdd.get_hdd_country(
        sim_param,
        lu_reg,
        data['temp_data'],
        data['assumptions']['smart_meter_diff_params'],
        data['assumptions']['rs_t_base_heating'],
        data['reg_coord'],
        data['weather_stations'])

    # ---------------------------------------
    # Overall disaggregation factors per enduse
    # ---------------------------------------
    total_pop = 0
    f_rs_lighting = 0
    fs_rs_cold = 0
    fs_rs_wet = 0
    fs_rs_consumer_electronics = 0
    fs_rs_home_computing = 0
    fs_rs_cooking = 0
    f_rs_space_heating = 0
    fs_rs_water_heating = 0

    for region_name in lu_reg:

        # HDD
        reg_hdd = rs_hdd_individ_region[region_name]

        # Floor Area across all sectors
        reg_floor_area = data['rs_floorarea'][sim_param['base_yr']][region_name]

        # Population
        reg_pop = data['scenario_data']['population'][sim_param['base_yr']][region_name]

        #reg_hdd, reg_pop, reg_cdd, reg_floor_area = 100, 100, 100, 100

        # National dissagregation factors
        f_rs_lighting += reg_floor_area
        fs_rs_cold += reg_pop
        fs_rs_wet += reg_pop
        fs_rs_consumer_electronics += reg_pop
        fs_rs_home_computing += reg_pop
        fs_rs_cooking += reg_pop
        f_rs_space_heating += reg_hdd * reg_floor_area
        fs_rs_water_heating += reg_pop
        total_pop += reg_pop

    # ---------------------------------------
    # Disaggregate according to enduse
    # ---------------------------------------
    rs_fuel_disagg = defaultdict(dict)

    for region_name in lu_reg:
        reg_pop = data['scenario_data']['population'][sim_param['base_yr']][region_name]
        reg_hdd = rs_hdd_individ_region[region_name]
        reg_floor_area = data['rs_floorarea'][sim_param['base_yr']][region_name]

        #reg_hdd, reg_pop, reg_cdd, reg_floor_area = 100, 100, 100, 100

        # Disaggregate fuel depending on end_use
        for enduse in rs_national_fuel:
            if enduse == 'rs_lighting':
                reg_diasg_factor = reg_floor_area / f_rs_lighting
            elif enduse == 'rs_cold':
                reg_diasg_factor = reg_pop / fs_rs_cold
            elif enduse == 'rs_wet':
                reg_diasg_factor = reg_pop / fs_rs_wet
            elif enduse == 'rs_consumer_electronics':
                reg_diasg_factor = reg_pop / fs_rs_consumer_electronics
            elif enduse == 'rs_home_computing':
                reg_diasg_factor = reg_pop / fs_rs_home_computing
            elif enduse == 'rs_cooking':
                reg_diasg_factor = reg_pop / fs_rs_cooking
            elif enduse == 're_space_heating':
                reg_diasg_factor = (reg_hdd * reg_floor_area) / f_rs_space_heating
            elif enduse == 'rs_water_heating':
                reg_diasg_factor = reg_pop / fs_rs_water_heating
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
    data = disaggregate_base_demand(data)

    #Write to csv file disaggregated demand
    write_disagg_fuel(
        os.path.join(data['local_paths']['dir_disattregated'], 'rs_fuel_disagg.csv'),
        data['rs_fuel_disagg'])
    write_disagg_fuel_sector(
        os.path.join(data['local_paths']['dir_disattregated'], 'ss_fuel_disagg.csv'),
        data['ss_fuel_disagg'])
    write_disagg_fuel_sector(
        os.path.join(data['local_paths']['dir_disattregated'], 'is_fuel_disagg.csv'),
        data['is_fuel_disagg'])

    logging.debug("... finished script %s", os.path.basename(__file__))
    return
