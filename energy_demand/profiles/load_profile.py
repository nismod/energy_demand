"""Functions related to load profiles
"""
import sys
import numpy as np

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
        self.dict_with_tuple_keys = {} # dict_with_tuple_keys

        self.enduses_in_stock = set([])

    def get_all_enduses_in_stock(self):
        """Update the list of the object with all enduses for which load profies are provided
        """
        all_enduses = set([])

        for profile_obj in self.load_profile_dict.values():
            for enduse in profile_obj.enduses:
                all_enduses.add(enduse)

        setattr(self, 'enduses_in_stock', all_enduses)

    def add_load_profile(
            self,
            unique_identifier,
            technologies,
            enduses,
            shape_yd,
            shape_yh,
            sectors=['dummy_sector'],
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
        self.load_profile_dict[unique_identifier] = LoadProfile(
            enduses,
            unique_identifier,
            shape_yd,
            shape_yh,
            enduse_peak_yd_factor,
            shape_peak_dh
            )

        # Generate lookup dictionary with triple key
        self.generate_dict_with_tuple_keys(
            unique_identifier,
            enduses,
            sectors,
            technologies
            )

        # Update enduses in stock
        self.get_all_enduses_in_stock()

    def generate_dict_with_tuple_keys(self, unique_identifier, enduses, sectors, technologies):
        """Generate look_up keys to position in 'load_profile_dict'

        Arguments
        ----------
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
                    self.dict_with_tuple_keys[(enduse, sector, technology)] = unique_identifier

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
        position_in_dict = self.dict_with_tuple_keys[(enduse, sector, technology)]

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
            sys.error("Specific load shape is not found in object")
            return

    def get_shape_peak_dh(self, enduse, sector, technology):
        """Get peak dh shape for a certain technology, enduse and sector

        Arguments
        ----------
        enduse : str
            Enduse
        sector : str
            Sector
        technology : str
            technology
        """
        position_in_dict = self.dict_with_tuple_keys[(enduse, sector, technology)]
        load_profile_obj = self.load_profile_dict[position_in_dict]

        # Test if dummy sector and thus shape_peak not provided for different sectors
        if sector == 'dummy_sector':
            shape_peak_dh = load_profile_obj.shape_peak_dh
            return shape_peak_dh
        else:
            shape_peak_dh = load_profile_obj.shape_peak_dh[sector][enduse]['shape_peak_dh']
            return shape_peak_dh

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
    def __init__(self, enduses, unique_identifier, shape_yd, shape_yh, enduse_peak_yd_factor, shape_peak_dh):
        """Constructor
        """

        self.unique_identifier = unique_identifier
        self.enduses = enduses

        self.shape_yd = shape_yd
        self.shape_yh = shape_yh
        self.enduse_peak_yd_factor = enduse_peak_yd_factor

        # Calculate percentage for every day
        self.shape_y_dh = self.calc_y_dh_shape_from_yh()

        self.shape_peak_dh = shape_peak_dh

    def calc_y_dh_shape_from_yh(self):
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
        #sum_every_day_p = 1 / np.nansum(self.shape_yh, axis=1)
        sum_every_day_p = np.divide(1, np.sum(self.shape_yh, axis=1))
        sum_every_day_p[np.isinf(sum_every_day_p)] = 0 # Replace inf by zero

        # Multiply (nr_of_days) + with (nr_of_days, 24)
        shape_y_dh = sum_every_day_p[:, np.newaxis] * self.shape_yh

        # Replace nan by zero (faster than np.nan_to_num)
        shape_y_dh[np.isnan(shape_y_dh)] = 0

        return shape_y_dh

def abs_to_rel_no_nan(absolute_array):
    """Convert absolute to relative (without correcting the NaN values)
    If the total sum is zero, return same array

    Arguments
    ----------
    absolute_array : array
        Input array with absolute numbers

    Returns
    -------
    relative_array : array
        Array with relative numbers
    """
    sum_array = float(np.sum(absolute_array))

    if sum_array != 0:
        return np.divide(absolute_array, sum_array)
    else:
        return absolute_array

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
    if sum_array != 0:
        relative_array = np.divide(absolute_array, sum_array)
        relative_array[np.isnan(relative_array)] = 0
        return relative_array
    else:
        return absolute_array

def calk_peak_h_dh(fuel_peak_dh):
    """Ger peak hour in peak day

    Arguments
    ----------
    fuel_peak_dh : array
        Fuel of peak day

    Return
    ------
    peak_fueltype_h : array
        Fuel for maximum hour in peak day per fueltype
    """
    # Get maximum value per row (maximum fuel hour per fueltype)
    peak_fueltype_h = np.max(fuel_peak_dh, axis=1)

    return peak_fueltype_h
