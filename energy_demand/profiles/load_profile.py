"""Functions related to load profiles
"""
import uuid
import logging
import numpy as np
from energy_demand.profiles import generic_shapes
from energy_demand.initalisations import helpers

class LoadProfileStock(object):
    """Collection of load shapes in a list

    Arguments
    ----------
    name : string
        Load profile stock name
    """
    def __init__(self, name):
        self.name = name
        self.load_profiles = {}
        self.dict_tuple_keys = {}
        self.stock_enduses = set([])

    def add_lp(
            self,
            unique_identifier,
            technologies,
            enduses,
            shape_yd,
            shape_yh,
            sectors=False,
            f_peak_yd=1.0/365,
            shape_peak_dh=np.full((24), 1.0/24)
        ):
        """Add load profile to stock

        Arguments
        ---------
        unique_identifier : str
            Name (unique identifier)
        technologies : list
            Technologies for which the profile applies
        enduses : list
            Enduses for which the profile applies
        shape_yd : array
            Shape yd (from year to day)
        shape_yh : array
            Shape yh (from year to hour)
        sectors : list, default=False
            Sectors for which the profile applies
        f_peak_yd : float
            Factor to calculate daily demand from yearly demand
            Standard value is average daily amount
        shape_peak_dh : array, default=1/24
            Shape (dh), shape of a day for every hour

        Note
        -----
        If no ``shape_peak_dh`` or ``f_peak_yd`` is provided
        a flat shape is assumed.
        """
        if not sectors:
            sectors = [False]
        else:
            pass

        self.load_profiles[unique_identifier] = LoadProfile(
            enduses,
            unique_identifier,
            shape_yd,
            shape_yh,
            f_peak_yd,
            shape_peak_dh)

        # Generate lookup dictionary with triple key
        self.dict_tuple_keys = generate_key_lu_dict(
            self.dict_tuple_keys,
            unique_identifier,
            enduses,
            sectors,
            technologies)

        # Update enduses in stock
        self.stock_enduses = get_stock_enduses(self.load_profiles)

    def get_lp(self, enduse, sector, technology, shape):
        """Get shape for a certain technology, enduse and sector

        Arguments
        ----------
        enduse : str
            Enduse
        sector : str
            Sector
        technology : str
            technology
        shape : str
            Type of shape which is to be read out from 'load_profiles'

        Return
        ------
        Load profile attribute
        """
        # Get key from lookup dict
        position_in_dict = self.dict_tuple_keys[(enduse, sector, technology)]

        # Get correct object
        load_profile_obj = self.load_profiles[position_in_dict]

        if shape == 'shape_yh':
            return load_profile_obj.shape_yh
        elif shape == 'shape_yd':
            return load_profile_obj.shape_yd
        elif shape == 'shape_y_dh':
            return load_profile_obj.shape_y_dh
        elif shape == 'f_peak_yd':
            return load_profile_obj.f_peak_yd
        elif shape == 'shape_peak_dh':
            return load_profile_obj.shape_peak_dh
        else:
            logging.critical("Specific load shape is not found in object")
            return

    def get_shape_peak_dh(self, enduse, sector, technology):
        """Get peak_dh shape for a certain technology, enduse and sector

        Arguments
        ----------
        enduse : str
            Enduse
        sector : str
            Sector
        technology : str
            technology
        """
        position_in_dict = self.dict_tuple_keys[(enduse, sector, technology)]
        load_profile_obj = self.load_profiles[position_in_dict]

        # Test if dummy sector and thus shape_peak not provided for different sectors
        if sector == False:
            return load_profile_obj.shape_peak_dh
        else:
            # CHECK
            '''if isinstance(load_profile_obj.shape_peak_dh, dict):
                return load_profile_obj.shape_peak_dh[enduse][sector]['shape_peak_dh']
            else:
                return load_profile_obj.shape_peak_dh'''
            return load_profile_obj.shape_peak_dh

def generate_key_lu_dict(dict_tuple_keys, unique_identifier, enduses, sectors, technologies):
    """Generate look_up keys to position in 'load_profiles'

    Arguments
    ----------
    dict_tuple_keys : dict
        Already existing lu keys
    unique_identifier : string
        Unique identifier of load shape object
    enduses : list
        List with enduses
    sectors : list
        List with sectors
    technologies : list
        List with technologies

    Returns
    -------
    dict_tuple_keys : str
        Lookup position in dict
    """
    for enduse in enduses:
        for sector in sectors:
            for technology in technologies:
                dict_tuple_keys[(enduse, sector, technology)] = unique_identifier

    return dict_tuple_keys

def get_stock_enduses(load_profiles):
    """Update the list of the object with all
    enduses for which load profies are provided

    Arguments
    ---------
    load_profiles : dict
        All load profiles of load profile stock

    Returns
    ------
    all_enduses : list
        All enduses in stock
    """
    all_enduses = set([])
    for profile_obj in load_profiles.values():
        for enduse in profile_obj.enduses:
            all_enduses.add(enduse)

    return list(all_enduses)

class LoadProfile(object):
    """Load profile container to store differengt shapes

    Arguments
    ----------
    unique_identifier : string
        Unique identifer for LoadProfile object
    shape_yd : array
        Shape yd (from year to day)
    shape_yh : array
        Shape yh (from year to hour)
    f_peak_yd : float
        Factor to calculate daily demand from yearly demand
        Standard value is average daily amount
    shape_peak_dh : array
        Shape (dh), shape of a day for every hour
    """
    def __init__(
            self,
            enduses,
            unique_identifier,
            shape_yd,
            shape_yh,
            f_peak_yd,
            shape_peak_dh
        ):
        """Constructor
        """
        self.unique_identifier = unique_identifier
        self.enduses = enduses
        self.shape_yd = shape_yd
        self.shape_yh = shape_yh
        self.f_peak_yd = f_peak_yd
        self.shape_peak_dh = shape_peak_dh

        # Calculate percentage for every day
        self.shape_y_dh = calc_y_dh_shape_from_yh(shape_yh)

def calc_y_dh_shape_from_yh(shape_yh):
    """Calculate shape for every day

    Returns
    -------
    shape_y_dh : array
        Shape for every day

    Note
    ----
    The output gives the shape for every day in a year (total sum == nr_of_days)
    Within each day, the sum is 1

    A RuntimeWarning may be raised if in one day a zero value is found.
    The resulting inf are replaced however and thus this warning
    can be ignored
    """
    # Calculate even if flat shape is assigned
    # Info: nansum does not through an ErrorTimeWarning
    # Some rowy may be zeros, i.e. division by zero results in inf values

    # Unable local RuntimeWarning: divide by zero encountered
    with np.errstate(divide='ignore'):
        sum_every_day_p = 1 / np.sum(shape_yh, axis=1)
    sum_every_day_p[np.isinf(sum_every_day_p)] = 0 # Replace inf by zero

    # Multiply (nr_of_days) + with (nr_of_days, 24)
    shape_y_dh = sum_every_day_p[:, np.newaxis] * shape_yh

    # Replace nan by zero
    shape_y_dh[np.isnan(shape_y_dh)] = 0

    return shape_y_dh

def abs_to_rel(absolute_array):
    """Convert absolute numbers in an array to relative

    Arguments
    ----------
    absolute_array : array
        Contains absolute numbers in it

    Returns
    -------
    relative_array : array
        Contains relative numbers

    Note
    ----
    - If the total sum is zero, return an array with zeros
    """
    sum_array = float(np.sum(absolute_array))
    if sum_array != 0.0:
        relative_array = absolute_array / sum_array
        relative_array[np.isnan(relative_array)] = 0
        return relative_array
    else:
        return absolute_array

def calk_peak_h_dh(fuel_peak_dh):
    """Ger peak hour in peak day

    Arguments
    ----------
    fuel_peak_dh : array
        Fuel of peak day for every fueltype

    Return
    ------
    peak_fueltype_h : array
        Fuel for maximum hour in peak day per fueltype
    """
    # Get maximum value per row (maximum fuel hour per fueltype)
    peak_fueltype_h = np.max(fuel_peak_dh, axis=1)

    return peak_fueltype_h

def calk_peak_h_dh_single_fueltype(fuel_peak_dh):
    """Ger peak hour in peak day

    Arguments
    ----------
    fuel_peak_dh : array
        Fuel of peak day for every fueltype

    Return
    ------
    peak_fueltype_h : array
        Fuel for maximum hour in peak day per fueltype
    """
    # Get maximum value per row (maximum fuel hour per fueltype)
    peak_fueltype_h = np.max(fuel_peak_dh, axis=0)

    return peak_fueltype_h

def create_load_profile_stock(
        tech_lp,
        assumptions,
        sectors,
        model_yeardays,
        all_enduses
    ):
    """Assign load profiles which are the same for all regions
    ``non_regional_load_profiles``

    Arguments
    ----------
    tech_lp : dict
        Load profiles
    assumptions : dict
        Assumptions
    sectors : dict
        Sectors
    all_enduses : dict
        Enduses

    Returns
    -------
    non_regional_lp_stock : object
        Load profile stock with non regional dependent load profiles
    """
    non_regional_lp_stock = LoadProfileStock("non_regional_load_profiles")

    # ---------
    # Residential Submodel
    # ---------
    shape_yh = calc_yh(
        tech_lp['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
        tech_lp['rs_shapes_dh']['rs_lighting']['shape_non_peak_y_dh'],
        model_yeardays)

    # rs_lighting
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['lighting'],
        enduses=['rs_lighting'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
        shape_yh=shape_yh,
        f_peak_yd=tech_lp['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_lighting']['shape_peak_dh'])

    # Skip temperature dependent end uses (regional)
    if 'rs_cold' in assumptions['enduse_rs_space_cooling']:
        pass
    else:
        shape_yh = calc_yh(
            tech_lp['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'],
            tech_lp['rs_shapes_dh']['rs_cold']['shape_non_peak_y_dh'],
            model_yeardays)

        # rs_cold (residential refrigeration)
        non_regional_lp_stock.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['cold'],
            enduses=['rs_cold'],
            shape_yd=tech_lp['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'],
            shape_yh=shape_yh,
            f_peak_yd=tech_lp['rs_shapes_yd']['rs_cold']['shape_peak_yd_factor'],
            shape_peak_dh=tech_lp['rs_shapes_dh']['rs_cold']['shape_peak_dh'])

    # rs_cooking
    shape_yh = calc_yh(
        tech_lp['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'],
        tech_lp['rs_shapes_dh']['rs_cooking']['shape_non_peak_y_dh'],
        model_yeardays)
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['cooking'],
        enduses=['rs_cooking'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'],
        shape_yh=shape_yh,
        f_peak_yd=tech_lp['rs_shapes_yd']['rs_cooking']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_cooking']['shape_peak_dh'])

    # rs_wet
    shape_yh = calc_yh(
        tech_lp['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'],
        tech_lp['rs_shapes_dh']['rs_wet']['shape_non_peak_y_dh'],
        model_yeardays)
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['wet'],
        enduses=['rs_wet'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'],
        shape_yh=shape_yh,
        f_peak_yd=tech_lp['rs_shapes_yd']['rs_wet']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_wet']['shape_peak_dh'])

    # -- Apply enduse sepcific shapes for enduses with not technologies with own defined shapes
    for enduse in all_enduses['rs_enduses']:

        # Enduses where technology specific load profiles are defined for yh
        if enduse == 'rs_space_heating':
            pass
        else:
            tech_list = helpers.get_nested_dict_key(assumptions['rs_fuel_tech_p_by'][enduse])

            shape_yh = calc_yh(
                tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                tech_lp['rs_shapes_dh'][enduse]['shape_non_peak_y_dh'],
                model_yeardays)

            non_regional_lp_stock.add_lp(
                unique_identifier=uuid.uuid4(),
                technologies=tech_list,
                enduses=[enduse],
                shape_yd=tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                shape_yh=shape_yh,
                f_peak_yd=tech_lp['rs_shapes_yd'][enduse]['shape_peak_yd_factor'],
                shape_peak_dh=tech_lp['rs_shapes_dh'][enduse]['shape_peak_dh'])

    # ---------
    # Service Submodel
    # ----------
    # - Assign to each enduse the carbon fuel trust dataset
    for enduse in all_enduses['ss_enduses']:

        # Skip temperature dependent end uses (regional) because load profile in regional load profile stock
        if enduse in assumptions['enduse_space_heating'] or enduse in assumptions['ss_enduse_space_cooling']:
            pass
        else:
            for sector in sectors['ss_sectors']:

                # Get technologies with assigned fuel shares
                tech_list = helpers.get_nested_dict_key(
                    assumptions['ss_fuel_tech_p_by'][enduse][sector])

                # Apply correction factor for weekend_effect
                shape_non_peak_yd = tech_lp['ss_shapes_yd'][enduse][sector]['shape_non_peak_yd'] * assumptions['ss_weekend_f']
                shape_non_peak_yd_weighted = abs_to_rel(shape_non_peak_yd)

                shape_yh = calc_yh(
                    shape_non_peak_yd_weighted, #shape_non_peak_yd
                    tech_lp['ss_shapes_dh'][enduse][sector]['shape_non_peak_y_dh'],
                    model_yeardays)

                non_regional_lp_stock.add_lp(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=shape_non_peak_yd_weighted,
                    shape_yh=shape_yh,
                    sectors=[sector],
                    f_peak_yd=tech_lp['ss_shapes_yd'][enduse][sector]['shape_peak_yd_factor'],
                    shape_peak_dh=tech_lp['ss_shapes_dh'][enduse][sector]['shape_peak_dh'])

    # ---------
    # Industry Submodel
    # ---------
    # Generate flat load profiles
    shape_peak_dh, _, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh = generic_shapes.flat_shape(
        assumptions['model_yeardays_nrs'])

    # Apply correction factor for weekend_effect to flat load profile for industry
    shape_non_peak_yd = shape_non_peak_yd * assumptions['is_weekend_f']
    shape_non_peak_yd_weighted = abs_to_rel(shape_non_peak_yd)

    for enduse in all_enduses['is_enduses']:
        if enduse == "is_space_heating":
            pass # Do not create non regional stock because temp dependent
        else:
            for sector in sectors['is_sectors']:

                tech_list = helpers.get_nested_dict_key(
                    assumptions['is_fuel_tech_p_by'][enduse][sector])

                non_regional_lp_stock.add_lp(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=shape_non_peak_yd_weighted,
                    shape_yh=shape_non_peak_yh,
                    sectors=[sector],
                    f_peak_yd=shape_peak_yd_factor,
                    shape_peak_dh=shape_peak_dh)

    return non_regional_lp_stock

def calc_av_lp(demand_yh, seasons, model_yeardays_daytype):
    """Calculate average load profile for daytype and season
    for fuel of a fueltype

    Result
    ------
    demand_yh : array
        Energy demand for every day of a single fueltype
    seasons: dict
        Seasons and their yeardays
    model_yeardays_daytype : dict
        Yearday type of every year
    av_loadprofiles : dict
        season, daytype

    Returns
    -------
    av_season_daytypes : dict
        Averaged lp
    season_daytypes : dict
        Not averaged lp

    """
    season_daytypes = {
        'spring': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)},
        'summer': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)},
        'autumn': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)},
        'winter': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)}}

    av_season_daytypes = {
        'spring': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)},
        'summer': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)},
        'autumn': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)},
        'winter': {
            'workday': np.zeros((0, 24), dtype=float),
            'holiday': np.zeros((0, 24), dtype=float)}}

    for yearday, daytype_yearday in enumerate(model_yeardays_daytype):

        # Season
        if yearday in seasons['spring']:
            season = 'spring'
        elif yearday in seasons['summer']:
            season = 'summer'
        elif yearday in seasons['autumn']:
            season = 'autumn'
        else:
            season = 'winter'

        # Add data as row to array
        new_data_dh = demand_yh[yearday]
        existing_array = season_daytypes[season][daytype_yearday]

        # Add to dict
        season_daytypes[season][daytype_yearday] = np.vstack([existing_array, new_data_dh])

    # -----------------------------
    # Calculate average of all dict
    # -----------------------------
    # Calculate average over every hour in a day
    for season, daytypes_data in season_daytypes.items():
        for daytype, daytpe_data in daytypes_data.items():
            av_season_daytypes[season][daytype] = np.mean(daytpe_data, axis=0)

    return av_season_daytypes, season_daytypes

def calc_yh(shape_yd, shape_y_dh, model_yeardays):
    """Calculate the shape based on yh and y_dh shape

    Inputs
    -------
    shape_yd : array
        Shape with fuel amount for every day (365)
    shape_y_dh : array
        Shape for every day (365, 24), total sum = 365
    model_yeardays : array
        Modelled yeardays

    Returns
    -------
    shape_yh : array
        Shape for every hour in a year (total sum == 1)
    """
    shape_yh = shape_yd[:, np.newaxis] * shape_y_dh[[model_yeardays]]

    return shape_yh
