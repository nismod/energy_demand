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
    dw_stock_new_dwellings = []

    # Base year data
    glob_var = data_ext['glob_var']
    base_year = glob_var['base_year']
    current_year = glob_var['current_year']
    dwtype_distr_by = data['dwtype_distr'][base_year]          # Distribution of dwelling types        2015.0: {'semi_detached': 26.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    dwtype_age_distr_by = data['dwtype_age_distr'][base_year]  # Age distribution of dwelling types    {2015: {1918: 20.8, 1928: 36.3, 1949: 29.4, 1968: 8.0, 1995: 5.4}} # year, average_age, percent
    #dwtype_floorarea = data['dwtype_floorarea']              # Floor area [m2]                       {'semi_detached': 96.0, 'terraced': 82.5, 'flat': 61.0, 'detached': 147.0, 'bungalow': 77.0}
    #reg_floorarea = data['reg_floorarea']                    # Floor Area in a region
    dw_lu = data['dwtype_lu']
    reg_lu = data['reg_lu']                                    # Regions

    # External data (current year)
    reg_pop_cy = data_ext['population'][current_year]

    # ----- Building stock scenario assumptions
    data_floorarea_pp_sim = bf.get_floorarea_pp(data['reg_floorarea'], data_ext['population'][base_year], glob_var, assumptions['change_floorarea_pp']) # Calculate floor area per person over simulation period
    dwtype_distr_sim = bf.get_dwtype_dist(dwtype_distr_by, assumptions['assump_dwtype_distr_ey'], glob_var)                                                    # Calculate distribution of dwelling types over simulation period
    ##dwtype_age_distr_sim = bf.get_dwtype_age_distr(dwtype_age_distr)  ## Assume that alway the same for base building stock

    # Iterate regions
    for reg_id in reg_lu:

        # Base year
        floorarea_by = data['reg_floorarea'][reg_id]      # Read in floor area of base year
        dw_nr_by = data['reg_dw_nr'][reg_id]              # Read in nr of dwellings of base year
        pop_by = data['reg_pop'][reg_id]                  # Read in population
        floorarea_pp_by = floorarea_by / pop_by           # Floor area per person [m2/person]
        #floorarea_by_pd = floorarea_by / dw_nr_by        # Floor area per dwelling [m2/dwelling]

        print(dwtype_distr_sim)
        print("okoko")
        floorarea_p_by = p_floorarea_dwtype(dw_lu, dwtype_distr_by, data['dwtype_floorarea'], dw_nr_by, dwtype_distr_sim) # Percent of floor area of base year (could be changed)

        print("JHJ: " )
        print(floorarea_p_by)

        sim_period = range(base_year, current_year + 1, 1) #base year, current year + 1, iteration step

        # Iterate simulation year
        for sim_y in sim_period:

            # Poulation of simulation year
            reg_pop_sy_all_reg = data_ext['population'][sim_y]           # Read in population for simulation year
            reg_pop_sy = data_ext['population'][sim_y][reg_id]           # Read in population for simulation year

            # Necessary new floor area of simulation year. Get Floor area per person of simulation year
            data_floorarea_pp_sim = bf.get_floorarea_pp(data['reg_floorarea'], reg_pop_sy_all_reg, glob_var, assumptions['change_floorarea_pp']) # Calculate floor area per person over simulation period
            floorarea_pp_sy = data_floorarea_pp_sim[reg_id][sim_y]       # Read in from simulated floorarea_pp dict for current year
            #floorarea_by_pd_cy = floorarea_by_pd                        ### #TODO:floor area per dwelling get new floorarea_by_pd (if not constant over time, cann't extrapolate for any year)

            # Total new floor area
            tot_floorarea_sy = floorarea_pp_sy * reg_pop_sy
            new_floorarea_sim_year = tot_floorarea_sy - floorarea_by # tot new floor area - area base year

            # Only calculate changing
            if sim_y == base_year:
                dw_stock_base = generate_dwellings_distr(uniqueID, dw_lu, floorarea_p_by[base_year], floorarea_by, dwtype_age_distr_by, floorarea_pp_by, floorarea_by, pop_by)
            else:
                # - existing dwellings
                print("generate existing buildings")
                # The number of people in the existing dwelling stock may change. Therfore calculate alos except for base year. Total floor number is assumed to be identical Here age of buildings could be changed
                dw_stock_new_dwellings = generate_dwellings_distr(uniqueID, dw_lu, floorarea_p_by[base_year], floorarea_by, dwtype_age_distr_by, floorarea_pp_sy, floorarea_by, floorarea_by/floorarea_pp_sy)

                # - new dwellings
                print("generate new buildings")
                print(sim_y)
                print(floorarea_p_by[base_year])
                print(floorarea_p_by[sim_y])
                if new_floorarea_sim_year > 0: # If new floor area new buildings are necessary
                    dw_stock_new_dwellings = generate_dw_new_sim_period(uniqueID, sim_y, dw_lu, floorarea_p_by[sim_y], floorarea_pp_sy, dw_stock_new_dwellings, new_floorarea_sim_year)

        # Generate region and save it in dictionary
        reg_building_stock_cur_yr[reg_id] = bf.DwStockRegion(reg_id, dw_stock_new_dwellings)    # Add old and new buildings to stock
        reg_building_stock_by[reg_id] = bf.DwStockRegion(reg_id, dw_stock_base)                 # Add base year stock

    '''print("Base dwelling")
    l = reg_building_stock_by[0].dwellings
    for i in l:
        print(i.__dict__)

    print("Curryear dwelling")
    l = reg_building_stock_cur_yr[0].dwellings
    for i in l:
        print(i.__dict__)
    '''
    return reg_building_stock_by, reg_building_stock_cur_yr

def p_floorarea_dwtype(dw_lookup, dw_dist, dw_floorarea, dw_nr, dwtype_distr_sim):
    """ Calculates the percentage of floor area  belonging to each dwelling type
    depending on average floor area per dwelling type and dwelling type distribution
    dw_lookup - dwelling types
    dw_dist   - distribution of dwellin types
    dw_floorarea - floor area per type
    dw_nr - number of total dwlling
    dwtype_distr_sim - Distribution of dwelling time over the simulation period

    returns a dict with percentage of each total floor area for each dwtype (must be 1.0 in tot)
    """

    
    dw_floorarea_p = {} # Initialise percent of total floor area per dwelling type

    # ITERATE ALL SIMULATION YEARS and use dwtype_distr_sim
    for sim_yr in dwtype_distr_sim:
        print("sim_yr: " + str(sim_yr))
        print(dwtype_distr_sim[sim_yr])
        y_dict = {}
        tot_floorarea_sy = 0
        
        for dw_id in dw_lookup:
            dw_name = dw_lookup[dw_id]

            # Calculate number of building of dwellin type for each seimulation
            percent_buildings_dw = (dwtype_distr_sim[sim_yr][dw_name])/100  # Get distribution in simulation year
            nr_dw_typ = dw_nr * percent_buildings_dw

            # absolute usable floor area per dwelling type
            fl_type = nr_dw_typ * dw_floorarea[dw_name]

            # sum total area
            tot_floorarea_sy += fl_type
            y_dict[dw_name] = fl_type # add absolute are ato dict

        # Convert absolute values into percentages
        for i in y_dict:
            y_dict[i] = (1/tot_floorarea_sy)*y_dict[i]
        print(y_dict)
        print("--")
        dw_floorarea_p[sim_yr] = y_dict
    
    #for i in dw_floorarea_p:
    #    print(dw_floorarea_p[i])
    #    print("---")

    # Test if 100%
    for i in dw_floorarea_p:
        print(dw_floorarea_p[i])
        print("---")
        n = 0
        for e in dw_floorarea_p[i]:
            n += dw_floorarea_p[i][e]
        print(n)
        if round(n, 1) != 1:
            print("ERROR")
            print(dw_floorarea_p[i])
            import sys
            sys.exit()

    return dw_floorarea_p

def generate_dwellings_distr(uniqueID, dw_lu, floorarea_p, floorarea_by, dwtype_age_distr_by, floorarea_pp_by, tot_floorarea_cy, pop_by):
    """Generates dwellings according to age, floor area and distribution assumptsion"""

    dw_stock_base, control_pop, control_floorarea = [], 0, 0

    # Iterate dwelling types
    for dw in dw_lu:
        dw_type_id, dw_type_name = dw, dw_lu[dw]
        dw_type_floorarea = floorarea_p[dw_type_name] * floorarea_by      # Floor area of existing buildlings

        # Distribute according to age
        for dwtype_age_id in dwtype_age_distr_by:
            age_class_p = dwtype_age_distr_by[dwtype_age_id] / 100              # Percent of dw of age class

            # Floor area of dwelling_class_age
            dw_type_age_class_floorarea = dw_type_floorarea * age_class_p     # Distribute proportionally floor area
            control_floorarea += dw_type_age_class_floorarea

            # Pop
            pop_dwtype_age_class = dw_type_age_class_floorarea / floorarea_pp_by # Floor area is divided by base area value
            control_pop += pop_dwtype_age_class

            # create building object
            dw_stock_base.append(bf.Dwelling(['X', 'Y'], dw_type_id, uniqueID, float(dwtype_age_id), pop_dwtype_age_class, dw_type_age_class_floorarea, 9999))
            uniqueID += 1

    assert round(tot_floorarea_cy, 3) == round(control_floorarea, 3)  # Test if floor area are the same
    assert round(pop_by, 3) == round(control_pop, 3)                    # Test if pop is the same

    return dw_stock_base

def generate_dw_new_sim_period(uniqueID, sim_y, dw_lu, floorarea_p_by, floorarea_pp_sy, dw_stock_new_dwellings, new_floorarea_sim_year):
    """Generate objects for all new dwellings

    All new dwellings are appended to the existing building stock of the region

    Parameters
    ----------
    uniqueID : uniqueID
        Unique dwellinge id

        ...

    Returns
    -------
    dw_stock_new_dwellings : list
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
        dw_type_floorarea_new_build = floorarea_p_by[dw_type_name] * new_floorarea_sim_year      # Floor area of existing buildlings
        control_floorarea += dw_type_floorarea_new_build

        # Pop
        pop_dwtype_sim_year_new_build = dw_type_floorarea_new_build / floorarea_pp_sy             # Floor area is divided by floorarea_per_person
        control_pop += pop_dwtype_sim_year_new_build

        # create building object
        #Todo: Add climate??/internal heat data
        dw_stock_new_dwellings.append(bf.Dwelling(['X', 'Y'], dw_type_id, uniqueID, sim_y, pop_dwtype_sim_year_new_build, dw_type_floorarea_new_build, 9999))
        uniqueID += 1

    print(new_floorarea_sim_year)
    print(control_floorarea)
    print(new_floorarea_sim_year/floorarea_pp_sy)
    print(control_pop)

    assert round(new_floorarea_sim_year, 3) == round(control_floorarea, 3)  # Test if floor area are the same
    assert round(new_floorarea_sim_year/floorarea_pp_sy, 3) == round(control_pop, 3)                    # Test if pop is the same

    return dw_stock_new_dwellings
