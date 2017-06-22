""" Functions for building stock"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325, R0902, R0913
import numpy as np
import energy_demand.main_functions as mf
import energy_demand.assumptions as assumpt

class Dwelling(object):
    """Class of a single dwelling or of a aggregated group of dwelling

    For every dwelling, the scenario drivers are calculated for each residential end_use.

    Parameters
    ----------
    curr_yr : int
        Current year of simulation
    coordinates : float
        coordinates
    dwtype : int
        Dwelling type id. Description can be found in `daytype_lu`
    house_id : int
        Unique ID of dwelling or dwelling group
    age : int
        Age of dwelling in years (year the building was built)
    pop : float
        Dwelling population
    floorarea : float
        Floor area of dwelling
    hlc : float
        Heat loss coefficient
    hdd : float
        Heating degree days

    Info
    -----
    Depending on service or residential model, not all attributes are filled (then they are inistialised as None or zero)

    """
    def __init__(self, curr_yr, reg_name, longitude, latitude, floorarea, enduses, driver_assumptions, pop=0, age=None, dwtype=None, sector_type=None):
        """Constructor of Dwelling Class
        """
        self.dw_ID = 'To_IMPEMENT'
        self.dw_reg_name = reg_name
        self.curr_yr = curr_yr
        self.enduses = enduses
        self.longitude = longitude
        self.latitude = latitude
        self.dwtype = dwtype
        self.age = age
        self.pop = pop
        self.floorarea = floorarea
        self.sector_type = sector_type

        self.hlc = assumpt.get_hlc(dwtype, age) #: Calculate heat loss coefficient with age and dwelling type if possible

        # Generate attribute for each enduse containing calculated scenario driver value
        self.calc_scenario_driver(driver_assumptions)

    def calc_scenario_driver(self, driver_assumptions):
        """ Summen driver values for dwellign depending on enduse and dfined assumptions and add as attribute
        IMPORTANT FUNCTION
        e.g. assumptION. {'resid_space_heating': ['pop', 'floorarea', 'hdd', 'hlc']}
        """
        # Set for the dwelling stock attributes for every enduse
        for enduse in self.enduses:
            driver_value = 1 #used to sum (not zero!)

            # If there are scenario drivers for enduse
            if enduse not in driver_assumptions:
                Dwelling.__setattr__(self, enduse, driver_value)
            else:
                drivers = driver_assumptions[enduse]

                # Iterate scenario driver and get attriute to multiply values
                for driver in drivers:
                    driver_value *= getattr(self, driver) # sum drivers

                # Set attribute
                Dwelling.__setattr__(
                    self,
                    enduse,
                    driver_value
                    )

        return

class DwStockRegion(object):
    """Class of the building stock in a region"""

    def __init__(self, region_name, dwellings, enduses):
        """Returns a new building stock region object.

        Parameters
        ----------
        region_name : float
            Region ID of building stock
        dwellings : list
            List containing all dwelling objects
        """
        self.region_name = region_name
        self.dwellings = dwellings

        self.pop = self.get_tot_pop()

        # SUM: (but same name as in dwelling)Summed scenario drivers across all dwellings for every enduse
        # Set for the dwelling stock attributes for every enduse
        for enduse in enduses:
            DwStockRegion.__setattr__(self, enduse, self.get_scenario_driver_enduse(enduse))

    def get_scenario_driver_enduse(self, enduse):
        """Sum all scenario driver for space heating"""
        sum_driver = 0
        for dwelling in self.dwellings:
            sum_driver += getattr(dwelling, enduse)

        return sum_driver

    def get_tot_pop(self):
        """Get total population of all dwellings"""
        totpop = 0
        for dwelling in self.dwellings:
            totpop += dwelling.pop

        return round(totpop, 3)

def calc_floorarea_pp(reg_floorarea_resid, reg_pop_by, base_yr, sim_period, assump_final_diff_floorarea_pp):
    """ Calculates future floor area per person depending on assumptions on final change and base year data

    Assumption: Linear Change of floor area per person


    Parameters
    ----------
    reg_floorarea_resid : dict
        Floor area base year for all region

    reg_pop_by : dict
        Population of base year for all region

    glob_var : dict
        Contains all global simulation variables

    assump_final_diff_floorarea_pp : float
        Assumption of change in floor area up to end of simulation

    Returns
    -------
    data_floorarea_pp : dict
        Contains all values for floor area per person for every year

    Linear change of floor area
    # todo: check with simulation period
    """
    data_floorarea_pp = {}

    # Iterate regions
    for reg_name in reg_pop_by:
        sim_yrs = {}
        floorarea_pp_by = reg_floorarea_resid[reg_name] / reg_pop_by[reg_name] # Floor area per person of base year

        # Iterate simulation years
        for sim_yr in sim_period:
            if sim_yr == base_yr:
                sim_yrs[sim_yr] = floorarea_pp_by # base year value
            else:
                # Change up to current year (linear)
                #print("sim_yr" + str(sim_yr))
                #print(assump_final_diff_floorarea_pp)
                #print(sim_period)
                #print(len(sim_period))
                lin_diff_factor = mf.linear_diff(base_yr, sim_yr, 0, assump_final_diff_floorarea_pp, len(sim_period))
                #print("lin_diff_factor: " + str(lin_diff_factor))
                #diff_cy = lin_diff_factor #(1 + assump_final_diff_floorarea_pp) + lin_diff_factor # NEW
                #print("diff_cy: " + str(diff_cy))

                # Floor area per person of simulation year
                sim_yrs[sim_yr] = floorarea_pp_by + (floorarea_pp_by * lin_diff_factor)
        data_floorarea_pp[reg_name] = sim_yrs  # Values for every simulation year

    return data_floorarea_pp

def get_dwtype_dist(dwtype_distr_by, assump_dwtype_distr_ey, base_yr, sim_period):
    """Calculates the yearly distribution of dw types
    based on assumption of distribution on end_yr

    Linear change over time

    # Todo: Check modelling interval (2050/2051)

    Parameters
    ----------
    base_dwtype_distr : dict
        Distribution of dwelling types base year

    assump_dwtype_distr_ey : dict
        Distribution of dwelling types end year

    data : dict
        Contains all global simulation variables

    Returns
    -------
    dwtype_distr : dict
        Contains all dwelling type distribution for every year

    Example
    -------

    out = {year: {'dwtype': 0.3}}
    """
    dwtype_distr = {}

    # Iterate years
    for sim_yr in sim_period:
        sim_yr_nr = sim_yr - base_yr

        if sim_yr == base_yr:
            y_distr = dwtype_distr_by # If base year, base year distribution
        else:
            y_distr = {}

            for dtype in dwtype_distr_by:
                val_by = dwtype_distr_by[dtype] # base year value
                sim_y = assump_dwtype_distr_ey[dtype] # cur year value
                diff_val = sim_y - val_by # Total difference
                diff_y = diff_val / (len(sim_period)-1) # Linear difference per year
                y_distr[dtype] = val_by + (diff_y * sim_yr_nr) # Difference up to current year

        dwtype_distr[sim_yr] = y_distr

    # Test if distribution is 100%
    for y in dwtype_distr:
        np.testing.assert_almost_equal(sum(dwtype_distr[y].values()), 1.0, decimal=5, err_msg='The distribution of dwelling types went wrong', verbose=True)

    return dwtype_distr
