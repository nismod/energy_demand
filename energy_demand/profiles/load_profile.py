"""Functions related to load profiles
"""
import uuid
import logging
from collections import defaultdict
import numpy as np
from energy_demand.profiles import generic_shapes
from energy_demand.initalisations import helpers

class LoadProfileStock(object):
    """Collection of load shapes in a list

    Arguments
    ----------
    stock_name : string
        Load profile stock name
    """
    def __init__(self, stock_name):
        self.stock_name = stock_name
        self.load_profile_dict = {}
        self.dict_tuple_keys = {}
        self.enduses_in_stock = set([])

    def add_lp(
            self,
            unique_identifier,
            technologies,
            enduses,
            shape_yd,
            shape_yh,
            sectors=False,
            enduse_peak_yd_factor=1.0/365,
            shape_peak_dh=np.full((24), 1.0/24)
        ):
        """Add load profile to stock

        Arguments
        ----------
        technologies : list
            Technologies for which the profile applies
        enduses : list
            Enduses for which the profile applies
        sectors : list
            Sectors for which the profile applies
        shape_yd : array
            Shape yd (from year to day)
        shape_yh : array
            Shape yh (from year to hour)
        enduse_peak_yd_factor : float
            Factor to calculate daily demand from yearly demand
            Standard value is average daily amount
        shape_peak_dh : array, default=1/24
            Shape (dh), shape of a day for every hour

        Note
        -----
        If no ``shape_peak_dh`` or ``enduse_peak_yd_factor`` is provided
        a flat shape is assumed.
        """
        if not sectors:
            sectors = ['dummy_sector']
        else:
            pass

        self.load_profile_dict[unique_identifier] = LoadProfile(
            enduses,
            unique_identifier,
            shape_yd,
            shape_yh,
            enduse_peak_yd_factor,
            shape_peak_dh)

        # Generate lookup dictionary with triple key
        self.dict_tuple_keys = generate_key_lu_dict(
            self.dict_tuple_keys,
            unique_identifier,
            enduses,
            sectors,
            technologies)

        # Update enduses in stock
        self.enduses_in_stock = get_all_enduses_in_stock(self.load_profile_dict)

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
            Type of shape which is to be read out from 'load_profile_dict'

        Return
        ------
        Load profile
        """
        # Get key from lookup dict
        position_in_dict = self.dict_tuple_keys[(enduse, sector, technology)]

        # Get correct object
        load_profile_obj = self.load_profile_dict[position_in_dict]

        if shape == 'shape_yh':
            return load_profile_obj.shape_yh
        elif shape == 'shape_yd':
            return load_profile_obj.shape_yd
        elif shape == 'shape_y_dh':
            return load_profile_obj.shape_y_dh
        elif shape == 'enduse_peak_yd_factor':
            return load_profile_obj.enduse_peak_yd_factor
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
        load_profile_obj = self.load_profile_dict[position_in_dict]

        # Test if dummy sector and thus shape_peak not provided for different sectors
        if sector == 'dummy_sector':
            return load_profile_obj.shape_peak_dh
        else:
            return load_profile_obj.shape_peak_dh[sector][enduse]['shape_peak_dh']

def generate_key_lu_dict(dict_tuple_keys, unique_identifier, enduses, sectors, technologies):
    """Generate look_up keys to position in 'load_profile_dict'

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
    """
    for enduse in enduses:
        for sector in sectors:
            for technology in technologies:
                dict_tuple_keys[(enduse, sector, technology)] = unique_identifier

    return dict_tuple_keys

def get_all_enduses_in_stock(load_profile_dict):
    """Update the list of the object with all
    enduses for which load profies are provided
    """
    all_enduses = set([])
    for profile_obj in load_profile_dict.values():
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
    enduse_peak_yd_factor : float
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
            enduse_peak_yd_factor,
            shape_peak_dh
        ):
        """Constructor
        """
        self.unique_identifier = unique_identifier
        self.enduses = enduses
        self.shape_yd = shape_yd
        self.shape_yh = shape_yh
        self.enduse_peak_yd_factor = enduse_peak_yd_factor

        # Calculate percentage for every day
        self.shape_y_dh = calc_y_dh_shape_from_yh(shape_yh)

        self.shape_peak_dh = shape_peak_dh

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

def create_load_profile_stock(tech_lp, assumptions, sectors):
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

    Returns
    -------
    non_regional_lp_stock : object
        Load profile stock with non regional dependent load profiles
    """
    non_regional_lp_stock = LoadProfileStock("non_regional_load_profiles")

    # Lighting (residential)
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['rs_lighting'],
        enduses=['rs_lighting'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
        shape_yh=tech_lp['rs_shapes_dh']['rs_lighting']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'][:, np.newaxis],
        enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_lighting']['shape_peak_dh'])

    # rs_cold (residential refrigeration)
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['rs_cold'],
        enduses=['rs_cold'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'],
        shape_yh=tech_lp['rs_shapes_dh']['rs_cold']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_cold']['shape_non_peak_yd'][:, np.newaxis],
        enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_cold']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_cold']['shape_peak_dh'])

    # rs_cooking
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['rs_cooking'],
        enduses=['rs_cooking'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'],
        shape_yh=tech_lp['rs_shapes_dh']['rs_cooking']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd'][:, np.newaxis],
        enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_cooking']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_cooking']['shape_peak_dh'])

    # rs_wet
    non_regional_lp_stock.add_lp(
        unique_identifier=uuid.uuid4(),
        technologies=assumptions['tech_list']['rs_wet'],
        enduses=['rs_wet'],
        shape_yd=tech_lp['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'],
        shape_yh=tech_lp['rs_shapes_dh']['rs_wet']['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd']['rs_wet']['shape_non_peak_yd'][:, np.newaxis],
        enduse_peak_yd_factor=tech_lp['rs_shapes_yd']['rs_wet']['shape_peak_yd_factor'],
        shape_peak_dh=tech_lp['rs_shapes_dh']['rs_wet']['shape_peak_dh'])

    # -- dummy rs technologies (apply enduse sepcific shape)
    for enduse in assumptions['rs_dummy_enduses']:
        tech_list = helpers.get_nested_dict_key(assumptions['rs_fuel_tech_p_by'][enduse])
        non_regional_lp_stock.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=tech_list,
            enduses=[enduse],
            shape_yd=tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
            shape_yh=tech_lp['rs_shapes_dh'][enduse]['shape_non_peak_y_dh'] * tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=tech_lp['rs_shapes_yd'][enduse]['shape_peak_yd_factor'],
            shape_peak_dh=tech_lp['rs_shapes_dh'][enduse]['shape_peak_dh'])

    # - dummy ss technologies
    for enduse in assumptions['ss_dummy_enduses']:
        tech_list = helpers.get_nested_dict_key(assumptions['ss_fuel_tech_p_by'][enduse])
        for sector in sectors['ss_sectors']:
            non_regional_lp_stock.add_lp(
                unique_identifier=uuid.uuid4(),
                technologies=tech_list,
                enduses=[enduse],
                shape_yd=tech_lp['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                shape_yh=tech_lp['ss_shapes_dh'][sector][enduse]['shape_non_peak_y_dh'] * tech_lp['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                sectors=[sector],
                enduse_peak_yd_factor=tech_lp['ss_shapes_yd'][sector][enduse]['shape_peak_yd_factor'],
                shape_peak_dh=tech_lp['ss_shapes_dh'][sector][enduse]['shape_peak_dh'])

    # dummy is - Flat load profile
    shape_peak_dh, _, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh = generic_shapes.flat_shape(
        assumptions['model_yeardays_nrs'], )

    # If space heating, add load shapes for service sector
    shape_peak_dh_sectors_enduses = defaultdict(dict)
    all_enduses_including_heating = assumptions['is_dummy_enduses']
    all_enduses_including_heating.append("is_space_heating")
    for sector in sectors['is_sectors']:
        for enduse in all_enduses_including_heating:
            if enduse == "is_space_heating":
                shape_peak_dh_sectors_enduses[sector][enduse] = {
                    'shape_peak_dh':
                    tech_lp['ss_shapes_dh'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_peak_dh']}
            else:
                shape_peak_dh_sectors_enduses[sector][enduse] = {
                    'shape_peak_dh': shape_peak_dh}

    for enduse in assumptions['is_dummy_enduses']:

        # Add load profile for space heating of ss sector
        if enduse == "is_space_heating":
            tech_list = helpers.get_nested_dict_key(assumptions['is_fuel_tech_p_by'][enduse])
            for sector in sectors['is_sectors']:
                non_regional_lp_stock.add_lp(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=tech_lp['ss_shapes_yd'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_non_peak_yd'],
                    shape_yh=tech_lp['ss_shapes_dh'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_non_peak_y_dh'] * tech_lp['ss_shapes_yd'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_non_peak_yd'][:, np.newaxis],
                    sectors=[sector],
                    enduse_peak_yd_factor=tech_lp['ss_shapes_yd'][sectors['ss_sectors'][0]]["ss_space_heating"]['shape_peak_yd_factor'],
                    shape_peak_dh=shape_peak_dh_sectors_enduses)
        else:
            tech_list = helpers.get_nested_dict_key(assumptions['is_fuel_tech_p_by'][enduse])
            for sector in sectors['is_sectors']:
                non_regional_lp_stock.add_lp(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=shape_non_peak_yd,
                    shape_yh=shape_non_peak_yh,
                    sectors=[sector],
                    enduse_peak_yd_factor=shape_peak_yd_factor,
                    shape_peak_dh=shape_peak_dh_sectors_enduses)

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
        'spring': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))},
        'summer': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))},
        'autumn': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))},
        'winter': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))}}

    av_season_daytypes = {
        'spring': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))},
        'summer': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))},
        'autumn': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))},
        'winter': {'workday': np.zeros((0, 24)), 'holiday': np.zeros((0, 24))}}

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

        stacked_array = np.vstack([existing_array, new_data_dh])

        # Add to dict
        season_daytypes[season][daytype_yearday] = stacked_array

    # -----------------------------
    # Calculate average of all dict
    # -----------------------------
    for season, daytypes_data in season_daytypes.items():
        for daytype, daytpe_data in daytypes_data.items():

            # Calculate average over every hour in a day
            av_season_daytypes[season][daytype] = np.mean(daytpe_data, axis=0)

    return av_season_daytypes, season_daytypes
