""" Functions for building stock"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

class Dwelling(object):
    """Class of a single dwelling or of a aggregated group of dwelling"""

    def __init__(self, coordinates, dwtype, house_id, age, pop, floor_area, temp):
        """Returns a new dwelling object.

        Parameters
        ----------
        coordinates : float
            coordinates
        dwtype : int
            Dwelling type id
        age :   int
            Age of dwelling
        hlc : float
            Heat loss coefficient
        dw_pop : float
            Dwelling population
        floor_area : float
            Floor area of dwelling
        temp : float
            Climate variable...(tbd)
        """
        self.house_id = house_id
        self.coordinates = coordinates
        self.dwtype = dwtype
        self.age = age
        self.hlc = get_hlc(dwtype, age) # Calculate heat loss coefficient with age and dwelling type
        self.pop = pop
        self.floor_area = floor_area
        self.temp = temp

    def scenario_driver_water_heating(self):
        """calc scenario driver with population and heat loss coefficient"""
        return self.pop

    def scenario_driver_lighting(self):
        """calc scenario driver with population and floor area"""
        return self.floor_area * self.pop

    def scenario_driver_space_heating(self):
        """calc scenario driver with population and floor area"""
        return self.floor_area * self.pop * self.temp * self.hlc

def get_hlc(dw_type, age):
    """Calculates the linearly derived hlc

    Parameters
    ----------
    dw_type : int
        Dwelling type
    age : int
        Age of dwelling

    Returns
    -------
    hls : Heat loss coefficient [W/m2 * K]

    Notes
    -----
    Source: Table 3.17 ECUK Tables
    """
    # Dict with linear fits for all different dwelling types { dw_type: [slope, constant]}
    linear_fits_hlc = {
        0: [-0.0223, 48.292],       # Detached
        1: [-0.0223, 48.251],       # Semi-Detached
        2: [-0.0223, 48.063],       # Terraced Average
        3: [-0.0223, 47.02],        # Flats
        4: [-0.0223, 48.261],       # Bungalow
        }

    # Get linearly fitted value
    hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]
    return hlc

class DwStockRegion(object):
    """Class of the building stock in a region"""
    # TODO: Include old and new stock

    def __init__(self, region_ID, dwellings):
        """Returns a new building stock region object.

        Parameters
        ----------
        region_ID : float
            Region ID of building stock
        dwellings : list
            List containing all dwelling objects
        """
        self.region_ID = region_ID
        self.dwellings = dwellings

    def get_tot_pop(self):
        """ Get total population"""
        totpop = 0
        for dwelling in self.dwellings:
            #print(dwelling.__dict__)
            totpop += dwelling.pop
        return round(totpop, 3)

    def get_sum_scenario_driver_water_heating(self):
        """ Sum all scenario driver for water heating"""
        sum_driver = 0
        for dwelling in self.dwellings:
            sum_driver += dwelling.scenario_driver_water_heating
        return sum_driver

    def get_sum_scenario_driver_space_heating(self):
        """ Sum all scenario driver for space heating"""
        sum_driver = 0
        for dwelling in self.dwellings:
            sum_driver += dwelling.scenario_driver_space_heating
        return sum_driver

    def get_sum_scenario_driver_lighting(self):
        """ Sum all scenario driver for lighting heating"""
        sum_driver = 0
        for dwelling in self.dwellings:
            sum_driver += dwelling.scenario_driver_lighting
        return sum_driver

def get_floor_area_pp(reg_floor_area, reg_pop, glob_var, assump_final_diff_floor_area_pp):
    """ Calculates future floor area per person depending on
    assumptions on final change and base year data

    Parameters
    ----------
    reg_floor_area : dict
        Floor area base year for all region

    reg_pop : dict
        Population of base year for all region

    glob_var : dict
        Contains all global simulation variables

    assump_final_diff_floor_area_pp : float
        Assumption of change in floor area up to end of simulation

    Returns
    -------
    data_floor_area_pp : dict
        Contains all values for floor area per person for every year

    Linear change of floor area
    # todo: check with simulation period
    """

    # initialisation
    data_floor_area_pp = {}
    sim_period = range(glob_var['base_year'], glob_var['end_year'] + 1, 1) #base year, current year, iteration step
    base_year = glob_var['base_year']

    # Iterate regions
    for reg_id in reg_pop:
        sim_years = {}
        floor_area_pp_by = reg_floor_area[reg_id] / reg_pop[reg_id] # Floor area per person of base year

        # Iterate simulation years
        for y in sim_period:
            curr_year = y - glob_var['base_year']

            if y == base_year:
                sim_years[y] = floor_area_pp_by # base year value
            else:
                # Change up to current year (linear)
                diff_cy = curr_year * (((1 + assump_final_diff_floor_area_pp) - 1) / (len(sim_period)-1)) # substract from sim_period 1 because of base year
                floor_ara_pp_sim_year = floor_area_pp_by * (1 + diff_cy)                                  # Floor area of simulation year
                sim_years[y] = floor_ara_pp_sim_year
        data_floor_area_pp[reg_id] = sim_years  # Values for every simulation year

    return data_floor_area_pp

def get_dwtype_dist(base_dwtype_distr, assump_dwtype_distr, glob_var):
    """Calculates the yearly distribution of dw types
    based on assumption of distribution on end_year

    Linear change over time

    # Todo: Check modelling interval (2050/2051)

    Parameters
    ----------
    base_dwtype_distr : dict
        Distribution of dwelling types base year

    assump_dwtype_distr : dict
        Distribution of dwelling types end year

    glob_var : dict
        Contains all global simulation variables

    Returns
    -------
    dwtype_distr : dict
        Contains all dwelling type distribution for every year
    """

    dwtype_distr = {}
    sim_period = range(glob_var['base_year'], glob_var['end_year'] + 1, 1) #base year, current year, iteration step

    # Iterate years
    for current_year in sim_period:
        sim_year = current_year - glob_var['base_year']
        y_distr = {}

        # iterate type
        for dtype in base_dwtype_distr:
            val_by = base_dwtype_distr[dtype]               # base year value
            val_cy = assump_dwtype_distr[dtype]             # cur year value

            diff_val = val_cy - val_by                      # Total difference
            diff_y = diff_val / (len(sim_period)-1)         # Linear difference per year

            y_distr[dtype] = val_by + (diff_y * sim_year)   # Differene up to current year
        dwtype_distr[current_year] = y_distr

    return dwtype_distr

def get_dwtype_age_distr(get_dwtype_age_distr_base):
    """Calculates age distribution

    Linear change over time

    # Todo: Check modelling interval (2050/2051)

    Parameters
    ----------
    base_dwtype_distr : dict
        Distribution of dwelling types base year

    assump_dwtype_distr : dict
        Distribution of dwelling types end year

    glob_var : dict
        Contains all global simulation variables

    Returns
    -------
    dwtype_distr : dict
        Contains all dwelling type distribution for every year
    """
    print(get_dwtype_age_distr_base)

    # {'1918': 20.82643491, '1941': 36.31645864, '1977.5': 29.44333304, '1996.5': 8.00677683, '2002': 5.407611848}


    prnt("...")

    return dwtype_age_distr_sim