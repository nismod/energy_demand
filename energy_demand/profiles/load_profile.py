"""Functions related to load profiles
"""
import numpy as np

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
            shape_y_dh,
            model_yeardays,
            sectors=False,
            shape_yh=False
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
        shape_y_dh : array
            
        shape_yh : array
            Shape yh (from year to hour)
        sectors : list, default=False
            Sectors for which the profile applies
        """
        if not sectors:
            sectors = [None]
        else:
            pass

        self.load_profiles[unique_identifier] = LoadProfile(
            enduses,
            unique_identifier,
            shape_yh,
            shape_yd,
            shape_y_dh,
            model_yeardays)

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
        #try:
        # Get key from lookup dict
        position_in_dict = self.dict_tuple_keys[(enduse, sector, technology)]

        # Get correct object
        load_profile_obj = self.load_profiles[position_in_dict]

        '''except KeyError:
            raise Exception(
                "Please define load profile for '{}' '{}' '{}'".format(
                    technology, enduse, sector))'''

        return getattr(load_profile_obj, shape)

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
    enduses : list
        Enduses assigned to load profile
    unique_identifier : string
        Unique identifer for LoadProfile object
    shape_y_dh : array
        Shape of every day in a year (sum = 365)
    shape_yh : array
        Shape yh (from year to hour)
        Standard value is average daily amount
    shape_peak_dh : array
        Shape (dh), shape of a day for every hour
    """
    def __init__(
            self,
            enduses,
            unique_identifier,
            shape_yh,
            shape_yd,
            shape_y_dh,
            model_yeardays
        ):
        """Constructor
        """
        self.unique_identifier = unique_identifier
        self.enduses = enduses

        if isinstance(shape_yh, bool):
            self.shape_yh = calc_yh(
                shape_yd,
                shape_y_dh,
                model_yeardays)
        else:
            self.shape_yh = shape_yh

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
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")},
        'summer': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")},
        'autumn': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")},
        'winter': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")}}

    av_season_daytypes = {
        'spring': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")},
        'summer': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")},
        'autumn': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")},
        'winter': {
            'workday': np.zeros((0, 24), dtype="float"),
            'holiday': np.zeros((0, 24), dtype="float")}}

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
            av_season_daytypes[season][daytype] = np.average(daytpe_data, axis=0)

    return av_season_daytypes, season_daytypes

def calc_yh(shape_yd, shape_y_dh, model_yeardays):
    """Calculate the shape based on yh and y_dh shape

    Arguments
    ---------
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
