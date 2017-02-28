""" Building Generator"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import energy_demand.building_stock_functions as bf

def virtual_building_stock(data, assumptions, data_ext):
    """Creates a virtual building stock based on base year data and assumptions

    Parameters
    ----------
    data : dict
        Base data (data loaded)
    assumptions : dict
        All assumptions
    data_ext : dict
        Data provided externally from simulation

    Returns
    -------
    dw_stock_old : list
        List containing dwelling objects of existing buildings

    dw_stock_new : list
        List containing dwelling objects of new buildings

    Notes
    -----
    The header row is always skipped.
    Needs as an input all population changes up to simulation period....(to calculate built housing)

    """
    uniqueID, reg_building_stock_cur_yr, reg_building_stock_by = 100000, {}, {}

    # Base year data
    base_year = data['glob_var']['base_year']
    dwtype_distr_by = data['dwtype_distr'][base_year]          # Distribution of dwelling types        2015.0: {'semi_detached': 26.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    dwtype_age_distr_by = data['dwtype_age_distr'][base_year]  # Age distribution of dwelling types    {2015: {1918: 20.8, 1928: 36.3, 1949: 29.4, 1968: 8.0, 1995: 5.4}} # year, average_age, percent
    #dwtype_floor_area = data['dwtype_floor_area']              # Floor area [m2]                       {'semi_detached': 96.0, 'terraced': 82.5, 'flat': 61.0, 'detached': 147.0, 'bungalow': 77.0}
    #reg_floor_area = data['reg_floor_area']                    # Floor Area in a region
    dw_lu = data['dwtype_lu']
    glob_var = data['glob_var']
    reg_lu = data['reg_lu']                                    # Regions

    # External data (current year)
    reg_pop_cy = data_ext['population']

    # ----- Building stock scenario assumptions
    data_floor_area_pp_sim = bf.get_floor_area_pp(data['reg_floor_area'], reg_pop_cy, glob_var, assumptions['change_floor_area_pp']) # Calculate floor area per person over simulation period
    dwtype_distr_sim = bf.get_dwtype_dist(dwtype_distr_by, assumptions['assump_dwtype_distr'], glob_var)                     # Calculate distribution of dwelling types over simulation period
    ##dwtype_age_distr_sim = bf.get_dwtype_age_distr(dwtype_age_distr)  ## Assume that alway the same for base building stock

    # Iterate regions
    for reg_id in reg_lu:
        floor_area_by = data['reg_floor_area'][reg_id]       # Read in floor area
        dw_nr_by = data['reg_dw_nr'][reg_id]            # Read in nr of dwellings

        # Percent of floor area of base year (could be changed)
        floor_area_p_by = p_floor_area_dwtype(dw_lu, dwtype_distr_by, data['dwtype_floor_area'], dw_nr_by) # Sum must be 0

        # --Scenario drivers
        # base year
        pop_by = data['reg_pop'][reg_id]                    # Read in population
        floor_area_pp_by = floor_area_by / pop_by           # Floor area per person [m2/person]
        floor_area_by_pd = floor_area_by / dw_nr_by         # Floor area per dwelling [m2/dwelling]

        # Current year of simulation
        pop_cy = reg_pop_cy[reg_id]                                              # Read in population for current year
        floor_area_pp_cy = data_floor_area_pp_sim[reg_id][glob_var['current_year']]     # Read in from simulated floor_area_pp dict for current year
        floor_area_by_pd_cy = floor_area_by_pd                                              ### #TODO:floor area per dwelling get new floor_area_by_pd (if not constant over time, cann't extrapolate for any year)

        # Total new floor area
        tot_floor_area_cy = floor_area_pp_cy * pop_cy
        tot_new_floor_area = tot_floor_area_cy - floor_area_by # tot new floor area - area base year = New needed floor area

        # Calculate total number of dwellings (existing build + need for new ones)
        dw_new = tot_new_floor_area / floor_area_by_pd_cy   # Needed new buildings (if not constant, must calculate nr of buildings in every year)
        total_nr_dw = dw_nr_by + dw_new                     # floor area / buildings

        # Dwelling stock base year
        dw_stock_base = generate_dwellings_distr(uniqueID, dw_lu, floor_area_p_by, floor_area_by, dwtype_age_distr_by, floor_area_pp_by, tot_floor_area_cy, pop_by)

        # Dwelling stock current year
        # Existing buildings
        dw_stock_cur_old = generate_dwellings_distr(uniqueID, dw_lu, floor_area_p_by, floor_area_by, dwtype_age_distr_by, floor_area_pp_cy, tot_floor_area_cy, tot_floor_area_cy/floor_area_pp_cy)

        # New buildings
        dw_stock_cur_new = []      
        for dw in dw_lu:
            dw_type_id, dw_type_name = dw, dw_lu[dw]

            # Iterate simulation years
            # ask will
            ## Get distribution for every year dwtype_distr_sim
            ## Get floor area & nr of dwellings for every year

            percent_dw_type = dwtype_distr_by[dw_type_name] / 100        # Percentage of dwelling type (TODO: Nimm scneario value)

            dw_type_dw_nr_new = percent_dw_type * dw_new # Nr of existing dwellings dw type new
            #print("Nr of Dwelling of tshi type: " + str(dw_type_dw_nr_new))

            # Floor area of dwelling type
            dw_type_floor_area = tot_new_floor_area * percent_dw_type

            # Pop
            pop_dwtype_dw_type = dw_type_floor_area / floor_area_pp_cy # Distribed with floor area..could do better

            # Get age of building construction
            sim_period = range(glob_var['base_year'], glob_var['current_year'] + 1, 1) #base year, current year + 1, iteration step
            nr_sim_y = len(sim_period)

            for simulation_year in sim_period:

                # create dwelling object
                dw_stock_cur_new.append(bf.Dwelling(['X', 'Y'], dw_type_id, uniqueID, simulation_year, pop_dwtype_dw_type/nr_sim_y, dw_type_floor_area/nr_sim_y, 9999))
                uniqueID += 1

        # Test if disaggregation was good (do some tests # Todo)
        '''print("Population old buildings:    " + str(_scrap_pop_old))
        print("Population new buildings:    " + str(_scrap_pop_new))

        print("Floor area old buildings:     " + str(_scrap_floor_old))
        print("Floor area new buildings:     " + str(_scrap_floor_new))
        print("---------------------------------------------------------------------------")
        print("Total disaggregated Pop:     " + str(_scrap_pop_new + _scrap_pop_old))
        print("Total disagg. floor area:    " + str(_scrap_floor_new + _scrap_floor_old))
        print("---")
        print("Population of current year:  " + str(pop_cy))
        print("Floor area of current year:  " + str(tot_floor_area_cy))
        '''
        # Generate region and save it in dictionary
        reg_building_stock_cur_yr[reg_id] = bf.DwStockRegion(reg_id, dw_stock_cur_old + dw_stock_cur_new)  # Add old and new buildings to stock
        reg_building_stock_by[reg_id] = bf.DwStockRegion(reg_id, dw_stock_base)                     # Add base year stock

        # Access list: reg_building_stock_by[reg_id].dwellings
        #print("dd")
        #for i in reg_building_stock_by[reg_id].dwellings:
        #    print (i.__dict__)
        #print(reg_building_stock_by[reg_id].get_tot_pop())

        #prnt("..")
    #print(reg_building_stock[0].dwelling_list)
    #l = reg_building_stock[0].dwelling_list
    #for i in l:
    #    print(i.__dict__)
    return reg_building_stock_by, reg_building_stock_cur_yr

def p_floor_area_dwtype(dw_lookup, dw_dist, dw_floor_area, dw_nr):
    """ Calculates the percentage of floor area  belonging to each dwelling type
    depending on average floor area per dwelling type
    dw_lookup - dwelling types
    dw_dist   - distribution of dwellin types
    dw_floor_area - floor area per type
    dw_nr - number of total dwlling

    returns a dict with percentage of each total floor area for each dwtype (must be 1.0 in tot)
    """

    tot_floor_area_cy = 0
    dw_floor_area_p = {} # Initialise percent of total floor area per dwelling type

    for dw_id in dw_lookup:
        dw_name = dw_lookup[dw_id]

        # Get number of building of dwellin type
        percent_buildings_dw = (dw_dist[dw_name])/100
        nr_dw_typXY = dw_nr * percent_buildings_dw

        # absolute usable floor area per dwelling type
        fl_type = nr_dw_typXY * dw_floor_area[dw_name]

        # sum total area
        tot_floor_area_cy += fl_type
        dw_floor_area_p[dw_name] = fl_type # add absolute are ato dict

    # Convert absolute values into percentages
    for i in dw_floor_area_p:
        dw_floor_area_p[i] = (1/tot_floor_area_cy)*dw_floor_area_p[i]

    return dw_floor_area_p

def generate_dwellings_distr(uniqueID, dw_lu, floor_area_p_by, floor_area_by, dwtype_age_distr_by, floor_area_pp_by, tot_floor_area_cy, pop_by):
    """Generates dwellings according to age, floor area and distribution assumptsion"""

    dw_stock_base, control_pop, control_floor_area = [], 0, 0

    # Iterate dwelling types
    for dw in dw_lu:
        dw_type_id, dw_type_name = dw, dw_lu[dw]
        dw_type_floor_area = floor_area_p_by[dw_type_name] * floor_area_by      # Floor area of existing buildlings

        # Distribute according to age
        for dwtype_age_id in dwtype_age_distr_by:
            age_class_p = dwtype_age_distr_by[dwtype_age_id] / 100 # Percent of dw of age class

            # Floor area of dwelling_class_age
            dw_type_age_class_floor_area = dw_type_floor_area * age_class_p # Distribute proportionally floor area
            control_floor_area += dw_type_age_class_floor_area

            # Pop
            pop_dwtype_age_class = dw_type_age_class_floor_area / floor_area_pp_by # Floor area is divided by base area value
            control_pop += pop_dwtype_age_class

            # --- create building object
            dw_stock_base.append(bf.Dwelling(['X', 'Y'], dw_type_id, uniqueID, float(dwtype_age_id), pop_dwtype_age_class, dw_type_age_class_floor_area, 9999))
            uniqueID += 1

    assert round(tot_floor_area_cy, 3) == round(control_floor_area, 3)  # Test if floor area are the same
    assert round(pop_by, 3) == round(control_pop, 3)                    # Test if pop is the same

    return dw_stock_base
