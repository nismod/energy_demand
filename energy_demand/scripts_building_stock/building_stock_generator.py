""" Building Generator"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325, R0902, R0913, R0914
import sys
import numpy as np
from energy_demand.scripts_building_stock import building_stock_functions
from energy_demand.scripts_plotting import plotting_results
from energy_demand.scripts_technologies import diffusion_technologies as diffusion

def ss_build_stock(data):
    """Create dwelling stock for service sector with service dwellings

    Iterate years and change floor area depending on assumption on
    linear change up to ey

    Parameters
    ----------
    data : dict
        Data

    Returns
    -------

    """

    # ------------TODO: REPLACE Newcastle
    # Generate floor area data for service sector
    # All info is necessary with the following structure
    # --data['ss_dw_input_data'][sim_yr][region][sector]['floorarea']
    # --data['ss_dw_input_data'][sim_yr][region][sector]['age']
    # ..
    # ------------

    dw_stock_every_year = {}

    # Iterate regions
    for region_name in data['lu_reg']:
        dw_stock_every_year[region_name] = {}

        # Iterate simulation year
        for sim_yr in data['sim_period']:

            # ------------------
            # Generate serivce dwellings
            # ------------------
            dw_stock = []

            # Iterate sectors
            for sector in data['ss_sectors']:

                # -------------------------
                #TODO: READ FROM Newcastle DATASET
                # -------------------------

                # -------------------------
                # -- Virstual service stock (so far very simple, e.g. not age considered)
                # -------------------------
                # Base year floor area
                floorarea_sector_by = data['ss_sector_floor_area_by'][region_name][sector]

                # Change in floor area up to end year
                if sector in data['assumptions']['ss_floorarea_change_ey_p']:
                    change_floorarea_p_ey = data['assumptions']['ss_floorarea_change_ey_p'][sector]
                else:
                    sys.exit("Error: The virtual ss building stock sector floor area assumption is not defined")

                # Floor area of sector in current year considering linear diffusion
                lin_diff_factor = diffusion.linear_diff(data['base_yr'], sim_yr, 1.0, change_floorarea_p_ey, len(data['sim_period']))

                floorarea_sector_cy = floorarea_sector_by + lin_diff_factor

                if floorarea_sector_cy == 0:
                    '''print(data['base_yr'])
                    print(sim_yr)
                    print(change_floorarea_p_ey)
                    print(len(data['sim_period']))
                    print(floorarea_sector_by)
                    print(lin_diff_factor)
                    print(change_floorarea_p_ey)
                    '''
                    sys.exit("ERROR: FLOORAREA CANNOT BE ZERO")

                # create building object
                dw_stock.append(
                    building_stock_functions.Dwelling(
                        curr_yr=sim_yr,
                        region_name=region_name,
                        longitude=data['reg_coordinates'][region_name]['longitude'],
                        latitude=data['reg_coordinates'][region_name]['latitude'],
                        floorarea=floorarea_sector_cy,
                        enduses=data['ss_all_enduses'],
                        driver_assumptions=data['assumptions']['ss_scen_driver_assumptions'],
                        sector_type=sector
                    )
                )

            # Add regional base year dwelling to dwelling stock
            dw_stock_every_year[region_name][sim_yr] = building_stock_functions.DwellingStock(
                region_name,
                dw_stock,
                data['ss_all_enduses']
                )

    return dw_stock_every_year

def rs_build_stock(data):
    """Creates a virtual building stock based on base year data and assumptions for every region

    Because the heating degree days are calculated for every region,

    Parameters
    ----------
    data : dict
        Base data (data loaded)

    Returns
    -------
    data : dict
        Adds reg_dw_stock_by and reg_building_stock_yr to the data dictionary:

        reg_dw_stock_by : Base year building stock
        reg_building_stock_yr : Building stock for every simulation year

    Notes
    -----
    The assumption about internal temperature change is used as for each dwelling the hdd are calculated
    based on wheater data and assumption on t_base.

    The header row is always skipped.
    Needs as an input all population changes up to simulation period....(to calculate built housing)

    """
    base_yr = data['base_yr']

    dw_stock_every_year = {}

    # Get distribution of dwelling types of all simulation years
    dwtype_distr_sim = building_stock_functions.get_dwtype_dist(
        data['assumptions']['assump_dwtype_distr_by'],
        data['assumptions']['assump_dwtype_distr_ey'],
        base_yr,
        data['sim_period']
        )

    # Get floor area per person for every simulation year
    data_floorarea_pp = building_stock_functions.calc_floorarea_pp(
        data['reg_floorarea_resid'],
        data['population'][base_yr],
        base_yr,
        data['sim_period'],
        data['assumptions']['assump_diff_floorarea_pp']
        )

    # Todo if necessary: Possible to implement that absolute size of households changes #floorarea_by_pd_cy = floorarea_by_pd  ### #TODO:floor area per dwelling get new floorarea_by_pd (if not constant over time, cann't extrapolate for any year)
    floorarea_p_sy = p_floorarea_dwtype(
        data['dwtype_lu'],
        data['assumptions']['assump_dwtype_floorarea'],
        dwtype_distr_sim
        )

    # Iterate regions
    for region_name in data['lu_reg']:
        floorarea_by = data['reg_floorarea_resid'][region_name]
        pop_by = data['population'][base_yr][region_name]
        floorarea_pp_by = np.divide(floorarea_by, pop_by) # Floor area per person [m2 / person]
        dw_stock_every_year[region_name] = {}

        # Iterate simulation year
        for sim_yr in data['sim_period']:

            # Calculate new necessary floor area of simulation year
            floorarea_pp_sy = data_floorarea_pp[region_name][sim_yr] # Get floor area per person of sim_yr

            # Floor area per person simulation year * population of simulation year in region
            tot_floorarea_sy = floorarea_pp_sy * data['population'][sim_yr][region_name] # TODO: WHy not + 1?
            new_floorarea_sy = tot_floorarea_sy - floorarea_by # tot new floor area - area base year

            # Only calculate changing
            if sim_yr == base_yr:
                dw_stock_base = generate_dw_existing(
                    data,
                    region_name,
                    sim_yr,
                    data['dwtype_lu'],
                    floorarea_p_sy[base_yr],
                    floorarea_by,
                    data['assumptions']['dwtype_age_distr'][base_yr],
                    floorarea_pp_by,
                    floorarea_by,
                    pop_by
                    )

                # Add regional base year building stock
                dw_stock_every_year[region_name][base_yr] = building_stock_functions.DwellingStock(region_name, dw_stock_base, data['rs_all_enduses']) # Add base year stock
                #dw_stock_new_dw = dw_stock_base # IF base year, the cy dwellign stock is the base year stock (bug found)
            else:
                # - existing dwellings
                # The number of people in the existing dwelling stock may change. Therfore calculate alos except for base year. Total floor number is assumed to be identical Here age of buildings could be changed
                # if smaler floor area pp, the same mount of people will be living in too large houses --> No. We demolish floor area...
                if pop_by * floorarea_pp_sy > floorarea_by:
                    demolished_area = 0
                else:
                    demolished_area = floorarea_by - (pop_by * floorarea_pp_sy)

                new_area_minus_demolished = floorarea_by - demolished_area
                pop_in_exist_dw_new_floor_area_pp = floorarea_by / floorarea_pp_sy #In existing building stock fewer people are living

                #dw_stock_new_dw = generate_dw_existing(data, region, sim_yr, data['dwtype_lu'], floorarea_p_sy[base_yr], floorarea_by, assumptions['dwtype_age_distr'][base_yr], floorarea_pp_sy, new_area_minus_demolished, pop_in_exist_dw_new_floor_area_pp, assumptions, data_ext)
                dw_stock_new_dw = generate_dw_existing(
                    data,
                    region_name,
                    sim_yr,
                    data['dwtype_lu'],
                    floorarea_p_sy[sim_yr],
                    new_area_minus_demolished,
                    data['assumptions']['dwtype_age_distr'][base_yr],
                    floorarea_pp_sy,
                    new_area_minus_demolished,
                    pop_in_exist_dw_new_floor_area_pp)

                # - new dwellings
                if new_floorarea_sy < 0:
                    print("EMPTY HOUSES???")

                if new_floorarea_sy > 0: # If new floor area new buildings are necessary
                    #print("=================================")
                    #print("floorarea_pp_sy   " + str(tot_floorarea_sy))
                    #print("new_floorarea_sy: " + str(new_floorarea_sy))
                    #print("floorarea_pp_by   " + str(floorarea_pp_by))
                    #print("floorarea_pp_sy   " + str(floorarea_pp_sy))
                    dw_stock_new_dw = generate_dw_new(
                        data,
                        region_name,
                        sim_yr,
                        data['dwtype_lu'],
                        floorarea_p_sy[sim_yr],
                        floorarea_pp_sy,
                        dw_stock_new_dw,
                        new_floorarea_sy,
                        data
                        )

                # Generate region and save it in dictionary
                dw_stock_every_year[region_name][sim_yr] = building_stock_functions.DwellingStock(region_name, dw_stock_new_dw, data['rs_all_enduses']) # Add old and new buildings to stock

        # Add regional base year building stock
        #dw_stock_every_year[region_name][base_yr] = building_stock_functions.DwellingStock(region_name, dw_stock_base, data['rs_all_enduses']) # Add base year stock

    return dw_stock_every_year

def p_floorarea_dwtype(dw_lookup, dw_floorarea_by, dwtype_distr_sim):
    """Calculates the percentage of the total floor area belonging to each dwelling type

    Depending on average floor area per dwelling type and the dwelling type
    distribution, the percentages are calculated for ever simulation year

    Parameters
    ----------
    dw_lookup : dw_lookup
        Dwelling types
    dw_floorarea_by : dict
        floor area per type
    dw_nr_by : int
        Number of dwellings of base year
    dwtype_distr_sim : dict
        Distribution of dwelling time over the simulation period
    dwtype_floorarea : dict
        Average Floor are per dwelling type of base year

    Returns
    -------
    dw_floorarea_p : dict
        Contains the percentage of the total floor area for each dwtype for every simulation year (must be 1.0 in tot)

    Notes
    -----
    This calculation is necessary as the share of dwelling types may differ depending the year
    """
    # Initialise percent of total floor area per dwelling type
    dw_floorarea_p = {}

    # Itreate simulation years
    for sim_yr in dwtype_distr_sim:
        y_dict, _tot_area = {}, 0

        for dw_id in dw_lookup:
            dw_name = dw_lookup[dw_id]

            # Calculate share of dwelling area based on absolute size and distribution
            p_buildings_dw = dwtype_distr_sim[sim_yr][dw_name]  # Get distribution of dwellings of simulation year
            _area_dw = p_buildings_dw * dw_floorarea_by[dw_name] # Get absolut size of dw_type

            _tot_area += _area_dw
            y_dict[dw_name] = _area_dw

        # Convert absolute values into percentages
        for i in y_dict:
            y_dict[i] = (1/_tot_area)*y_dict[i]
        dw_floorarea_p[sim_yr] = y_dict

    return dw_floorarea_p

def generate_dw_existing(data, region_name, curr_yr, dw_lu, floorarea_p, floorarea_by, dwtype_age_distr_by, floorarea_pp, tot_floorarea_cy, pop_by):
    """Generates dwellings according to age, floor area and distribution assumptsion"""

    dw_stock_base, control_pop, control_floorarea = [], 0, 0

    # Iterate dwelling types
    for dw_type, dw_type_name in dw_lu.items():
        dw_type_floorarea = floorarea_p[dw_type_name] * floorarea_by # Floor area of existing buildlings

        # Distribute according to age
        for dwtype_age_id in dwtype_age_distr_by:
            age_class_p = np.divide(dwtype_age_distr_by[dwtype_age_id], 100) # Percent of dw of age class

            # Floor area of dwelling_class_age
            dw_type_age_class_floorarea = dw_type_floorarea * age_class_p # Distribute proportionally floor area

            control_floorarea += dw_type_age_class_floorarea

            # Pop
            pop_dwtype_age_class = np.divide(dw_type_age_class_floorarea, floorarea_pp) # Floor area is divided by base area value

            control_pop += pop_dwtype_age_class

            # create building object
            dw_stock_base.append(
                building_stock_functions.Dwelling(
                    curr_yr=curr_yr,
                    region_name=region_name,
                    longitude=data['reg_coordinates'][region_name]['longitude'],
                    latitude=data['reg_coordinates'][region_name]['latitude'],
                    floorarea=dw_type_age_class_floorarea,
                    enduses=data['rs_all_enduses'],
                    driver_assumptions=data['assumptions']['rs_scen_driver_assumptions'],
                    pop=pop_dwtype_age_class,
                    age=float(dwtype_age_id),
                    dwtype=dw_type
                    )
                )

            # TODO: IF Necessary calculate absolute number of buildings by dividng by the average floor size of a dwelling
            # Calculate number of dwellings

    #Testing
    np.testing.assert_array_almost_equal(tot_floorarea_cy, control_floorarea, decimal=3, err_msg="Error NR XXX  {} ---  {}".format(tot_floorarea_cy, control_floorarea))    # Test if floor area are the same
    np.testing.assert_array_almost_equal(pop_by, control_pop, decimal=3, err_msg="Error NR XXX")

    return dw_stock_base

def generate_dw_new(data, region_name, curr_yr, dw_lu, floorarea_p_by, floorarea_pp_sy, dw_stock_new_dw, new_floorarea_sy, data_ext):
    """Generate objects for all new dwellings

    All new dwellings are appended to the existing building stock of the region

    Parameters
    ----------
    uniqueID : uniqueID
        Unique dwellinge id

        ...

    Returns
    -------
    dw_stock_new_dw : list
        List with appended dwellings

    Notes
    -----
    The floor area id divided proprtionally depending on dwelling type
    Then the population is distributed
    builindg is creatd
    """
    control_pop, control_floorarea = 0, 0

    # Iterate dwelling types
    for dw in dw_lu:
        dw_type_id, dw_type_name = dw, dw_lu[dw]

        # Floor area
        dw_type_floorarea_new_build = floorarea_p_by[dw_type_name] * new_floorarea_sy # Floor area of existing buildlings
        control_floorarea += dw_type_floorarea_new_build

        # Pop
        pop_dwtype_sim_yr_new_build = dw_type_floorarea_new_build / floorarea_pp_sy             # Floor area is divided by floorarea_per_person
        control_pop += pop_dwtype_sim_yr_new_build

        # create building object
        dw_stock_new_dw.append(
            building_stock_functions.Dwelling(
                curr_yr=curr_yr,
                region_name=region_name,
                longitude=data['reg_coordinates'][region_name]['longitude'],
                latitude=data['reg_coordinates'][region_name]['latitude'],
                floorarea=dw_type_floorarea_new_build,
                enduses=data['rs_all_enduses'],
                driver_assumptions=data['assumptions']['rs_scen_driver_assumptions'],
                pop=pop_dwtype_sim_yr_new_build,
                age=curr_yr,
                dwtype=dw_type_id
                )
            )

    assert round(new_floorarea_sy, 3) == round(control_floorarea, 3)  # Test if floor area are the same
    assert round(new_floorarea_sy/floorarea_pp_sy, 3) == round(control_pop, 3) # Test if pop is the same

    return dw_stock_new_dw
