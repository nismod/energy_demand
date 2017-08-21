""" Functions for building stock"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325, R0902, R0913
import numpy as np
from energy_demand.technologies import diffusion_technologies as diffusion

class Dwelling(object):
    """Class of a single dwelling or of a aggregated group of dwellings

    For every dwelling, the scenario drivers are calculated for each enduse

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

    Note
    -----
    Depending on service or residential model, not all attributes are filled (then they are inistialised as None or zero)

    """
    def __init__(self, curr_yr, region_name, longitude, latitude, floorarea, enduses, driver_assumptions, population=0, age=None, dwtype=None, sector_type=None):
        """Constructor of Dwelling Class
        """
        self.dw_ID = 'To_IMPEMENT'
        self.dw_region_name = region_name
        self.curr_yr = curr_yr
        self.enduses = enduses
        self.longitude = longitude
        self.latitude = latitude
        self.dwtype = dwtype
        self.age = age
        self.population = population
        self.floorarea = floorarea
        self.sector_type = sector_type

        self.hlc = self.get_hlc(dwtype, age) #: Calculate heat loss coefficient with age and dwelling type if possible

        # Testing
        assert floorarea != 0

        # Generate attribute for each enduse containing calculated scenario driver value
        self.calc_scenario_driver(driver_assumptions)

    def calc_scenario_driver(self, driver_assumptions):
        """Sum scenario drivers per enduse and add as attribute
        IMPORTANT FUNCTION
        """
        for enduse in self.enduses:
            scenario_driver_value = 1 #used to sum (not zero!)

            # If there is no scenario drivers for enduse, set to standard value 1
            if enduse not in driver_assumptions:
                Dwelling.__setattr__(self, enduse, scenario_driver_value)
            else:
                scenario_drivers = driver_assumptions[enduse]

                # Iterate scenario driver and get attriute to multiply values
                for scenario_driver in scenario_drivers:
                    scenario_driver_value *= getattr(self, scenario_driver) # sum drivers

                # Set attribute
                Dwelling.__setattr__(
                    self,
                    enduse,
                    scenario_driver_value
                    )

            # Testing
            assert scenario_driver_value != 0

        return

    @classmethod
    def get_hlc(cls, dw_type, age):
        """Calculates the linearly derived heat loss coeeficients depending on age and dwelling type

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
        Source: Linear trends derived from Table 3.17 ECUK Tables
        https://www.gov.uk/government/collections/energy-consumption-in-the-uk
        """

        if dw_type is None or age is None:
            print("The HLC could not be calculated of a dwelling")
            return None

        # Dict with linear fits for all different dwelling types {dw_type: [slope, constant]}
        linear_fits_hlc = {
            0: [-0.0223, 48.292], # Detached
            1: [-0.0223, 48.251], # Semi-Detached
            2: [-0.0223, 48.063], # Terraced Average
            3: [-0.0223, 47.02], # Flats
            4: [-0.0223, 48.261], # Bungalow
            }

        # Get linearly fitted value
        hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]

        return hlc

class DwellingStock(object):
    """Class of the building stock in a region_name
    """
    def __init__(self, region_name, dwellings, enduses):
        """Returns a new building stock region_name object.

        Parameters
        ----------
        region_name : float
            Region of the dwelling
        dwellings : list
            List containing all dwelling objects
        enduses : list
            Enduses
        """
        self.region_name = region_name
        self.dwellings = dwellings

        self.population = self.get_tot_pop()

        # SUM: (but same name as in dwelling)Summed scenario drivers across all dwellings for every enduse
        # Set for the dwelling stock attributes for every enduse
        for enduse in enduses:
            DwellingStock.__setattr__(
                self,
                enduse,
                self.get_scenario_driver_enduse(enduse)
                )

    def get_scenario_driver_enduse(self, enduse):
        """Sum all scenario driver for space heating

        Parameters
        ----------
        enduse: string
            Enduse
        """
        sum_driver = 0
        for dwelling in self.dwellings:
            sum_driver += getattr(dwelling, enduse)

        return sum_driver

    def get_tot_pop(self):
        """Get total population of all dwellings
        """
        tot_pop = 0
        for dwelling in self.dwellings:
            tot_pop += dwelling.population

        return tot_pop

def calc_floorarea_pp(reg_floorarea_resid, reg_pop_by, base_yr, sim_period, sim_period_yrs, assump_final_diff_floorarea_pp):
    """Calculate future floor area per person depending on assumptions on final change and base year data

    Assumption: Linear change of floor area per person

    Parameters
    ----------
    reg_floorarea_resid : dict
        Floor area base year for all region_name
    reg_pop_by : dict
        Population of base year for all region_name
    base_yr : int
        Base year
    sim_period : int
        Simulation period
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

    for region_name in reg_pop_by:
        sim_yrs = {}

        if reg_pop_by[region_name] == 0:
            floorarea_pp_by = 0
        else:
            floorarea_pp_by = reg_floorarea_resid[region_name] / reg_pop_by[region_name] # Floor area per person of base year

        # Iterate simulation years
        for sim_yr in sim_period:
            if sim_yr == base_yr:
                sim_yrs[sim_yr] = floorarea_pp_by # base year value
            else:
                # Change up to current year (linear)
                #print("sim_yr" + str(sim_yr))
                #print(assump_final_diff_floorarea_pp)
                lin_diff_factor = diffusion.linear_diff(base_yr, sim_yr, 0, assump_final_diff_floorarea_pp, sim_period_yrs)

                # Floor area per person of simulation year
                sim_yrs[sim_yr] = floorarea_pp_by + (floorarea_pp_by * lin_diff_factor)

        data_floorarea_pp[region_name] = sim_yrs

    return data_floorarea_pp

def get_dwtype_dist(dwtype_distr_by, assump_dwtype_distr_ey, base_yr, sim_period, sim_period_yrs):
    """Calculates the yearly distribution of dw types
    based on assumption of distribution on end_yr

    Linear change over time

    # Todo: Check modelling interval (2050/2051)

    Parameters
    ----------
    dwtype_distr_by : dict
        Distribution of dwelling types base year
    assump_dwtype_distr_ey : dict
        Distribution of dwelling types end year
    base_yr : int
        Base year
    sim_period : list
        Simlulation period

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
    for sim_yr in sim_period: #TODO
        sim_yr_nr = sim_yr - base_yr

        if sim_yr == base_yr:
            y_distr = dwtype_distr_by # If base year, base year distribution
        else:
            y_distr = {}

            for dtype in dwtype_distr_by:
                val_by = dwtype_distr_by[dtype] # base year value
                sim_y = assump_dwtype_distr_ey[dtype] # cur year value
                diff_val = sim_y - val_by # Total difference
                diff_y = diff_val / sim_period_yrs # Linear difference per year #TODO: Vorher war no minus 1
                y_distr[dtype] = val_by + (diff_y * sim_yr_nr) # Difference up to current year

        dwtype_distr[sim_yr] = y_distr

    # Test if distribution is 100%
    for y in dwtype_distr:
        np.testing.assert_almost_equal(sum(dwtype_distr[y].values()), 1.0, decimal=5, err_msg='The distribution of dwelling types went wrong', verbose=True)

    return dwtype_distr
