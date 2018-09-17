"""Virtual Dwelling Generator - Generates a virtual dwelling stock
"""
import numpy as np
from energy_demand.basic import lookup_tables

from energy_demand.technologies import diffusion_technologies

'''def createNEWCASTLE_dwelling_stock(curr_yr, region, data, parameter_list):
    """Create dwelling stock based on input from
    building model from Newcastle

    Arguments
    ---------
    curr_yr : int
        Current year
    """
    # ------
    # Get all regional information concering floor area etc.
    # Either preprocessed or direct
    # ------
    stock_pop = {}
    floor_area = {}
    # Iterate all buildings
    # see which dwelling type -->
    # see which age_class -->
    # see which building attribute (e.g. resid, industry)
    # --> summen the following attributes according these categories
    #       - population stock_pop[]
    #       - floor area
    #       -
    # ----------------
    # Create residential dwelling stock
    # ----------------
    # Create dwellings Residential
    # Inputs Residential
    #   - building_type/dwelling_type/dwellingtype_ageclass
    #   -
    dw_stock = []
    dwelling_types = ["detached", "semi_detached"]
    age_classs = [1920, 1930, 1940] #Age categories
    building_type = "residential"

    for dwelling_type in dwelling_types:
        for age_class in age_classs:

            # Get pop of age class
            pop_dwtype_age_class = stock_pop[building_type][dwelling_type][age_class]

            # Get floor area of building type, dwelling_ype, age_class
            floor_area_dwtype_age_class = floor_area[building_type][dwelling_type][age_class]

            dwelling_obj = Dwelling(
                curr_yr=curr_yr,
                coordinates=data['reg_coord'][region],
                floorarea=floor_area_dwtype_age_class,
                enduses=data['enduses']['residential'],
                driver_assumptions=data['assumptions'].scenario_drivers['rs_submodule'],
                population=pop_dwtype_age_class,
                age=age_class,
                dwtype=dwelling_type,
                gva=data['scenario_data']['gva'][curr_yr][region])
            dw_stock.append(dwelling_obj)

    dwelling_stock = DwellingStock(
        dw_stock,
        data['enduses']['residential'])

    return dwelling_stock
'''
class Dwelling(object):
    """Dwelling or aggregated group of dwellings

    Arguments
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
    - Depending on service or residential model, not all attributes
      are filled (then they are inistialised as None or zero)
    - For every dwelling, the scenario drivers are calculated for each enduse
    """
    def __init__(
            self,
            curr_yr,
            coordinates,
            floorarea,
            enduses,
            driver_assumptions,
            population=None,
            age=None,
            dwtype=None,
            sector=None,
            gva=None,
            #air_leakage_rate=1.0
        ):
        """Constructor of Dwelling Class
        """
        self.curr_yr = curr_yr
        self.enduses = enduses
        self.longitude = coordinates['longitude']
        self.latitude = coordinates['longitude']
        self.dwtype = dwtype
        self.age = age
        self.population = population
        self.floorarea = floorarea
        self.sector = sector
        self.gva = gva #TODO IS THIS USED?
        #self.air_leakage_rate = air_leakage_rate
        #self.income = get_income_factor(income)?? MAYBE
        #self.household_size = get_household_factor(household_size)?? MAYBE

        # FACTORS
        # HOW MUCH MORE ENERGY e.g. certain dwelling type uses
        #self.ed_dw_type_factor =

        #: Calculate heat loss coefficient with age and dwelling type if possible
        self.hlc = get_hlc(dwtype, age)

        # Generate attribute for each enduse containing calculated scenario driver value
        self.calc_scenario_driver(driver_assumptions)

        # Testing
        assert floorarea != 0

    def calc_scenario_driver(self, driver_assumptions):
        """Sum scenario drivers per enduse and add as attribute

        Arguments
        ---------
        driver_assumptions : dict
            Scenario drivers for every enduse
        """
        for enduse in self.enduses:

            #used to sum (not zero!)
            scenario_driver_value = 1

            # If there is no scenario drivers for enduse, set to standard value 1
            if enduse not in driver_assumptions:
                Dwelling.__setattr__(self, enduse, scenario_driver_value)
            else:
                scenario_drivers = driver_assumptions[enduse]

                # Iterate scenario driver and get attriute to multiply values
                try:
                    for scenario_driver in scenario_drivers:

                        # If scenario driver is set to zero, do not use this driver
                        driver_value = getattr(self, scenario_driver)

                        # Ignore zero driver values
                        if driver_value == 0:
                            pass
                        else:
                            scenario_driver_value *= driver_value
                except TypeError:
                    #logging.info("Scenario driver `%s` calculation not possible", scenario_driver)
                    pass

                Dwelling.add_new_attribute(
                    self,
                    enduse,
                    scenario_driver_value)

            assert scenario_driver_value != 0

    def add_new_attribute(self, name, value):
        """Add a new self asttribute to DwellingStock
        """
        setattr(self, name, value)

class DwellingStock(object):
    """Class of the building stock in a region
    """
    def __init__(self, dwellings, enduses):
        """Returns a new building stock object for every `region`.

        Arguments
        ----------
        dwellings : list
            List containing all dwelling objects
        enduses : list
            Enduses
        """
        self.dwellings = dwellings

        # Calculate pop of dwelling stock
        self.population = get_tot_pop(dwellings)

        # Calculate enduse specific scenario driver
        for enduse in enduses:

            enduse_scenario_driver = self.get_scenario_driver(
                enduse)

            DwellingStock.add_new_attribute(
                self,
                enduse,
                enduse_scenario_driver)

    def get_scenario_driver(self, enduse):
        """Sum all scenario driver for an enduse

        Arguments
        ----------
        enduse: string
            Enduse to calculate scenario drivers
        """
        sum_driver = 0
        for dwelling in self.dwellings:
            sum_driver += getattr(dwelling, enduse)

        return sum_driver

    def add_new_attribute(self, name, value):
        """Add a new self asttribute to DwellingStock
        """
        setattr(self, name, value)

def get_tot_pop(dwellings):
    """Get total population of all dwellings

    Return
    ------
    tot_pop : float or bool
        If population is not provided, return `None`,
        otherwise summed population of all dwellings
    """
    tot_pop = 0

    for dwelling in dwellings:
        if dwelling.population is None:
            return None
        else:
            tot_pop += dwelling.population

    return tot_pop

def get_floorare_pp(
        floorarea,
        reg_pop_by,
        base_yr,
        sim_period,
        assump_diff_floorarea_pp
    ):
    """Calculate future floor area per person depending
    on assumptions on final change and base year data

    Arguments
    ----------
    floorarea : dict
        Floor area base year for all regions
    reg_pop_by : dict
        Population of base year for all regions
    base_yr, : int
        base year
    sim_period: list
        Simulation period
    assump_diff_floorarea_pp : float
        Assumption of change in floor area up to end of simulation

    Returns
    -------
    floor_area_pp : dict
        Contains all values for floor area per person for every year

    Note
    ----
    - Linear change of floor area per person is assumed over time
    """
    floor_area_pp = {}

    if reg_pop_by == 0:
        floor_area_pp[base_yr] = 0
    else:
        # Floor area per person of base year
        floor_area_pp[base_yr] = floorarea / reg_pop_by

    for curr_yr in sim_period:
        if curr_yr == base_yr:
            pass
        else:
            # Floor area of current year = floor area of base year * change
            floor_area_pp[curr_yr] = floor_area_pp[base_yr] * (1 + assump_diff_floorarea_pp[curr_yr])

    return floor_area_pp

def get_dwtype_floor_area(
        dwtype_floorarea_by,
        dwtype_floorarea_future,
        base_yr,
        sim_period
    ):
    """Calculates the floor area per dwelling type for every year

    Arguments
    ----------
    dwtype_distr_by : dict
        Distribution of dwelling types base year
    dwtype_floorarea_future : dict
        Distribution of future dwelling types end year
    base_yr : list
        Simulation parameters
    sim_period : list
        Simulation period
    sim_period_yrs : list
        Nr of simlated years

    Returns
    -------
    dwtype_floor_area : dict
        Contains the floor area change per dwelling type
    Note
    -----
    - A linear change over time is assumed

    Example
    -------
    out = {year: {'dwtype': 0.3}}
    """
    dwtype_floor_area = {}

    # Base year
    dwtype_floor_area[base_yr] = dwtype_floorarea_by

    # Simulation years
    for curr_yr in sim_period:

        if curr_yr == base_yr:
            pass
        else:
            y_distr = {}

            for dwtype in dwtype_floorarea_by:
                val_by = dwtype_floorarea_by[dwtype]
                val_future = dwtype_floorarea_future[dwtype]

                yr_until_changed = dwtype_floorarea_future['yr_until_changed']

                val_cy = diffusion_technologies.linear_diff(
                    base_yr,
                    curr_yr,
                    val_by,
                    val_future,
                    yr_until_changed)

                y_distr[dwtype] = val_cy

            dwtype_floor_area[curr_yr] = y_distr

    return dwtype_floor_area

def get_dwtype_distr(
        dwtype_distr_by,
        dwtype_distr_fy,
        base_yr,
        sim_period
    ):
    """Calculates the annual distribution of dwelling types
    based on assumption of base and end year distribution

    Arguments
    ----------
    dwtype_distr_by : dict
        Distribution of dwelling types base year
    dwtype_distr_fy : dict
        Distribution of dwelling types end year

    Returns
    -------
    dwtype_distr : dict
        Contains all dwelling type distribution for every year
    Note
    -----
    - A linear change over time is assumed

    Example
    -------
    out = {year: {'dwtype': 0.3}}
    """
    dwtype_distr = {}

    # Base year
    dwtype_distr[base_yr] = dwtype_distr_by

    # Simulation years
    for curr_yr in sim_period:
        if curr_yr == base_yr:
            pass
        else:
            y_distr = {}

            for dwtype in dwtype_distr_by:
                val_by = dwtype_distr_by[dwtype]
                val_future = dwtype_distr_fy[dwtype]

                yr_until_changed = dwtype_distr_fy['yr_until_changed']

                val_cy = diffusion_technologies.linear_diff(
                    base_yr,
                    curr_yr,
                    val_by,
                    val_future,
                    yr_until_changed)

                y_distr[dwtype] = val_cy

            dwtype_distr[curr_yr] = y_distr

    # Test if distribution is 100%
    for year in dwtype_distr:
        np.testing.assert_almost_equal(
            sum(dwtype_distr[year].values()),
            1.0,
            decimal=5,
            err_msg='The distribution of dwelling types went wrong', verbose=True)

    return dwtype_distr

def ss_dw_stock(
        region,
        enduses,
        sectors,
        scenario_data,
        reg_coord,
        assumptions,
        curr_yr,
        base_yr,
        virtual_building_stock_criteria
    ):
    """Create dwelling stock for service sector

    Arguments
    ----------
    regions : dict
        Regions
    data : dict
        Data container

    Returns
    -------
    dwelling_stock : list
        List with objects

    Note
    ----
    - Iterate years and change floor area depending on assumption on
      linear change up to ey
    """
    dw_stock = []
    for sector in sectors:

        # If virtual building stock, change floor area proportionally to population
        if virtual_building_stock_criteria:
            pop_by = scenario_data['population'][base_yr][region]
            pop_cy = scenario_data['population'][curr_yr][region]

            pop_factor = pop_cy / pop_by
            lin_diff_factor = pop_factor
            '''
            # Change in floor are for service submodel depending on sector
            # (if no change set to 1, if e.g. 10% decrease change to 0.9)
            assumptions.ss_floorarea_change_ey_p = {

                'yr_until_changed': yr_until_changed_all_things,

                'community_arts_leisure': 1,
                'education': 1,
                'emergency_services': 1,
                'health': 1,
                'hospitality': 1,
                'military': 1,
                'offices': 1,
                'retail': 1,
                'storage': 1,
                'other': 1}
                '''
        else:
            # Change in floor area up to end year
            if sector in assumptions.ss_floorarea_change_ey_p:
                change_floorarea_p_ey = assumptions.ss_floorarea_change_ey_p[sector]
                yr_until_changed = assumptions.ss_floorarea_change_ey_p['yr_until_changed']
            else:
                raise Exception(
                    "Error: The ss building stock sector floor area assumption is not defined")

            # Floor area of sector in current year considering linear diffusion
            lin_diff_factor = diffusion_technologies.linear_diff(
                base_yr,
                curr_yr,
                1.0,
                change_floorarea_p_ey,
                yr_until_changed)

        floorarea_sector_by = scenario_data['floor_area']['ss_floorarea'][base_yr][region][sector]
        floorarea_sector_cy = floorarea_sector_by * lin_diff_factor

        # GVA data
        try:
            gva_sector_lu = lookup_tables.economic_sectors_regional_MISTRAL()
            gva_nr = gva_sector_lu[sector]['match_int']
            gva_dw_data = scenario_data['gva_industry'][curr_yr][region][gva_nr]
        except KeyError:
            # If not sector specific GVA, use overal GVA per head
            gva_dw_data = scenario_data['gva_per_head'][curr_yr][region]

        # Create dwelling objects
        dw_stock.append(
            Dwelling(
                curr_yr=curr_yr,
                coordinates=reg_coord[region],
                population=pop_cy,
                floorarea=floorarea_sector_cy,
                enduses=enduses,
                driver_assumptions=assumptions.scenario_drivers,
                sector=sector,
                gva=gva_dw_data))

    # Add regional base year dwelling to dwelling stock
    dwelling_stock = DwellingStock(
        dw_stock,
        enduses)

    return dwelling_stock

def rs_dw_stock(
        region,
        assumptions,
        scenario_data,
        simulated_yrs,
        dwelling_types,
        enduses,
        reg_coord,
        driver_assumptions,
        curr_yr,
        base_yr,
        virtual_building_stock_criteria
    ):
    """Creates a virtual building stock for every year and region

    Arguments
    ----------
    region : dict
        Region name
    curr_yr : int
        Current year

    Returns
    -------
    dwelling_stock : dict
        Building stock wei

    reg_dw_stock_by : Base year building stock
        reg_building_stock_yr : Building stock for every simulation year

    Notes
    -----
    - The assumption about internal temperature change is
      used as for each dwelling the hdd are calculated
      based on wheater data and assumption on t_base

    - Doesn't take floor area as an input but calculates floor area
      based on floor area pp parameter. However, floor area
      could be read in by:

      1.) Inserting `tot_floorarea_cy = data['rs_floorarea'][curr_yr]`

      2.) Replacing 'dwtype_floor_area', 'dwtype_distr' and 'data_floorarea_pp'
          with more specific information from real building stock model
    """
    if virtual_building_stock_criteria:

        # Get changes in absolute floor area per dwelling type over time
        dwtype_floor_area = get_dwtype_floor_area(
            assumptions.dwtype_floorarea_by,
            assumptions.dwtype_floorarea_fy,
            base_yr,
            simulated_yrs)

        # Get distribution of dwelling types of all simulation years
        dwtype_distr = get_dwtype_distr(
            assumptions.dwtype_distr_by,
            assumptions.dwtype_distr_fy,
            base_yr,
            simulated_yrs)

        # Get floor area per person for every simulation year
        data_floorarea_pp = get_floorare_pp(
            scenario_data['floor_area']['rs_floorarea'][base_yr][region],
            scenario_data['population'][base_yr][region],
            base_yr,
            simulated_yrs,
            assumptions.non_regional_vars['assump_diff_floorarea_pp'])

        # Get fraction of total floorarea for every dwelling type
        floorarea_p = get_floorarea_dwtype_p(
            dwelling_types,
            dwtype_floor_area,
            dwtype_distr)

        floorarea_by = scenario_data['floor_area']['rs_floorarea'][base_yr][region]

        population_by = scenario_data['population'][base_yr][region]
        population_cy = scenario_data['population'][curr_yr][region]

        if population_by != 0:
            floorarea_pp_by = floorarea_by / population_by # [m2 / person]
        else:
            floorarea_pp_by = 0

        # Calculate new necessary floor area  per person of current year
        floorarea_pp_cy = data_floorarea_pp[curr_yr]

        # Calculate new floor area
        tot_floorarea_cy = floorarea_pp_cy * population_cy
    else:
        """
        #If floor_area is read in from model, this would be here
        # NEeds to be implemented
        # NEWCASTLE
        """
        floorarea_by = scenario_data['floor_area']['rs_floorarea'][curr_yr][region]
        tot_floorarea_cy = scenario_data['floor_area']['rs_floorarea'][curr_yr][region]

    new_floorarea_cy = tot_floorarea_cy - floorarea_by

    # Only calculate changing
    if curr_yr == base_yr:
        dw_stock_base = generate_dw_existing(
            driver_assumptions=driver_assumptions,
            scenario_data=scenario_data,
            enduses=enduses,
            reg_coord=reg_coord,
            region=region,
            curr_yr=curr_yr,
            dw_lu=dwelling_types,
            floorarea_p=floorarea_p[base_yr],
            floorarea_by=floorarea_by,
            dwtype_age_distr_by=assumptions.dwtype_age_distr[base_yr],
            floorarea_pp=floorarea_pp_by,
            gva_dw_data=scenario_data['gva_per_head'][curr_yr][region])

        # Create regional base year building stock
        dwelling_stock = DwellingStock(
            dw_stock_base,
            enduses)
    else:
        """The number of people in the base year dwelling stock may change.
        If the floor area pp decreased with constant pop, the same number of
        people will be living in too large houses. It is not assumed
        that area is demolished.
        """
        floor_area_cy = floorarea_pp_cy * population_by

        if floor_area_cy > floorarea_by:
            demolished_area = 0
        else:
            demolished_area = floorarea_by - floor_area_cy

        remaining_area = floorarea_by - demolished_area

        # Generate stock for existing area
        dw_stock_cy = generate_dw_existing(
            driver_assumptions=driver_assumptions,
            scenario_data=scenario_data,
            enduses=enduses,
            reg_coord=reg_coord,
            region=region,
            curr_yr=curr_yr,
            dw_lu=dwelling_types,
            floorarea_p=floorarea_p[curr_yr],
            floorarea_by=remaining_area,
            dwtype_age_distr_by=assumptions.dwtype_age_distr[base_yr],
            floorarea_pp=floorarea_pp_cy,
            gva_dw_data=scenario_data['gva_per_head'][curr_yr][region])

        # Append buildings of new floor area to
        if new_floorarea_cy > 0:
            dw_stock_cy = generate_dw_new(
                driver_assumptions=driver_assumptions,
                scenario_data=scenario_data,
                reg_coord=reg_coord,
                enduses=enduses,
                dwtypes=dwelling_types,
                region=region,
                curr_yr=curr_yr,
                floorarea_p_by=floorarea_p[curr_yr],
                floorarea_pp_cy=floorarea_pp_cy,
                dw_stock_new_dw=dw_stock_cy,
                new_floorarea_cy=new_floorarea_cy,
                gva_dw_data=scenario_data['gva_per_head'][curr_yr][region])
        else:
            pass # no new floor area is added

        # Generate region and save it in dictionary (Add old and new buildings to stock)
        dwelling_stock = DwellingStock(
            dw_stock_cy,
            enduses)

    return dwelling_stock

def get_floorarea_dwtype_p(dw_lookup, dw_floorarea, dwtype_distr):
    """Calculates the percentage of the total floor area
    belonging to each dwelling type. Depending on average
    floor area per dwelling type and the dwelling type
    distribution, the percentages are calculated
    for ever simulation year

    Arguments
    ----------
    dw_lookup : dw_lookup
        Dwelling types
    dw_floorarea : dict
        Floor area per type and year
    dwtype_distr : dict
        Distribution of dwelling type over the simulation period

    Returns
    -------
    dw_floorarea_p : dict
        Contains the percentage of the total floor
        area for each dwtype for every simulation year (must be 1.0 in tot)

    Notes
    -----
    This calculation is necessary as the share of dwelling types may differ depending the year
    """
    dw_floorarea_p = {}

    for curr_yr, type_distr_p in dwtype_distr.items():
        area_dw_type = {}

        # Calculate share of dwelling area based on absolute size and distribution
        for dw_type in dw_lookup.values():
            # Get absolut size of dw_type
            area_dw_type[dw_type] = type_distr_p[dw_type] * dw_floorarea[curr_yr][dw_type]

        # Convert absolute values into percentages
        tot_area = sum(area_dw_type.values())
        for dw_type, dw_type_area in area_dw_type.items():
            area_dw_type[dw_type] = dw_type_area / tot_area

        dw_floorarea_p[curr_yr] = area_dw_type

    return dw_floorarea_p

def generate_dw_existing(
        driver_assumptions,
        scenario_data,
        enduses,
        reg_coord,
        region,
        curr_yr,
        dw_lu,
        floorarea_p,
        floorarea_by,
        dwtype_age_distr_by,
        floorarea_pp,
        gva_dw_data
    ):
    """Generates dwellings according to age, floor area
    and distribution assumption

    Arguments
    ----------
    assumptions : dict
        Assumptions
    scenario_data : dict
        Scenario data
    enduses : list
        Enduses
    region : dict
        Region name
    curr_yr : int
        Base year
    dw_lu : dict
        Dwelling type look-up
    floorarea_p : dict
        Fraction of floor area per dwelling type
    floorarea_by : dict
        Floor area of base year
    dwtype_age_distr_by : dict
        Age distribution of dwelling
    floorarea_pp : dict
        Floor area per person
    tot_floorarea_cy : float
        Floor are in current year
    pop_by : dict
        Population in base year

    Return
    ------
    dw_stock_by : list
        Dwelling stocks in a list
    """
    dw_stock_by, control_pop, control_floorarea = [], 0, 0

    # Iterate dwelling types
    for dwtype_name in dw_lu.values():

        # Calculate floor area per dwelling type
        dwtype_floorarea = floorarea_p[dwtype_name] * floorarea_by

        # Distribute according to age
        for dwtype_age in dwtype_age_distr_by.keys():

            # Floor area of dwelling_class_age (distribute proportionally floor area)
            dwtype_age_class_floorarea = dwtype_floorarea * dwtype_age_distr_by[dwtype_age]

            # Floor area per person is divided by base area value to calc pop
            if floorarea_pp != 0:
                pop_dwtype_age_class = dwtype_age_class_floorarea / floorarea_pp
            else:
                pop_dwtype_age_class = 0

            # create building object
            dw_stock_by.append(
                Dwelling(
                    curr_yr=curr_yr,
                    coordinates=reg_coord[region],
                    floorarea=dwtype_age_class_floorarea,
                    enduses=enduses,
                    driver_assumptions=driver_assumptions,
                    population=pop_dwtype_age_class,
                    age=float(dwtype_age),
                    dwtype=dwtype_name,
                    gva=gva_dw_data))

            control_floorarea += dwtype_age_class_floorarea
            control_pop += pop_dwtype_age_class

    return dw_stock_by

def generate_dw_new(
        driver_assumptions,
        scenario_data,
        reg_coord,
        enduses,
        dwtypes,
        region,
        curr_yr,
        floorarea_p_by,
        floorarea_pp_cy,
        dw_stock_new_dw,
        new_floorarea_cy,
        gva_dw_data
    ):
    """Generate dwelling objects for all new dwellings

    All new dwellings are appended to the existing
    building stock of the region

    Arguments
    ----------
    data : dict
        Data container
    region : str
        Region
    curr_yr : int
        Current year
    floorarea_p_by : dict
        Fraction of floorarea in base year
    floorarea_pp_cy : dict
        Floor area per person in current year
    dw_stock_new_dw : dict
        New dwellings
    new_floorarea_cy : dict
        New floorarea in current year

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
    for dwtype_name in dwtypes.values():

        # Calculate new floor area per dewlling type
        dw_type_new_floorarea = floorarea_p_by[dwtype_name] * new_floorarea_cy

        # Calculate pop (Floor area is divided by floorarea_per_person)
        pop_dwtype_new_build_cy = dw_type_new_floorarea / floorarea_pp_cy

        # create building object
        dw_stock_new_dw.append(
            Dwelling(
                curr_yr=curr_yr,
                coordinates=reg_coord[region],
                floorarea=dw_type_new_floorarea,
                enduses=enduses,
                driver_assumptions=driver_assumptions,
                population=pop_dwtype_new_build_cy,
                age=curr_yr,
                dwtype=dwtype_name,
                gva=gva_dw_data))

        control_floorarea += dw_type_new_floorarea
        control_pop += pop_dwtype_new_build_cy

    # Test if floor area and pop are the same
    #assert round(new_floorarea_cy, 3) == round(control_floorarea, 3)
    #assert round(new_floorarea_cy/floorarea_pp_cy, 2) == round(control_pop, 2)
    return dw_stock_new_dw

def get_hlc(dw_type, age):
    """Calculates the linearly derived heat loss coeeficients
    depending on age and dwelling type

    Arguments
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
        #logging.debug(
        #    "The HLC could not be calculated of a dwelling age: {} dw_type: {}".format(dw_type, age))
        return None
    else:
        # Dict with linear fits for all different dwelling types {dw_type: [slope, constant]}
        linear_fits_hlc = {
            'detached': [-0.0223, 48.292],
            'semi_detached': [-0.0223, 48.251],
            'terraced': [-0.0223, 48.063],
            'flat': [-0.0223, 47.02],
            'bungalow': [-0.0223, 48.261]}

        # Get linearly fitted value
        hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]

        return hlc
