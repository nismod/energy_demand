"""Functions related to load profiles
"""
import time
import numpy as np
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

class LoadProfileStock(object):
    """Collection of load shapes in a list
    """
    def __init__(self, stock_name):
        self.stock_name = stock_name
        #self.load_profile_list = []
        self.load_profile_dict = {}

        # dict_with_tuple_keys
        self.dict_with_tuple_keys = {}

    def add_load_profile(self, unique_identifier, technologies, enduses, sectors, shape_yd=np.zeros((365)), shape_yh=np.zeros((365, 24)), enduse_peak_yd_factor=1/365, shape_peak_dh=np.ones((24))):
        """Add load profile to stock

        Parameters
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
        shape_peak_dh : array
            Shape (dh), shape of a day for every hour
        """
        '''for enduse in enduses:
            for sector in sectors:
                for technology in technologies:
                    self.load_profile_dict[(enduse, sector, technology)] = LoadProfile(
                        technology,
                        enduse,
                        sector,
                        shape_yd,
                        shape_yh,
                        enduse_peak_yd_factor,
                        shape_peak_dh
                        )
        '''
        self.load_profile_dict[unique_identifier] = LoadProfile(
            unique_identifier,
            technologies,
            enduses,
            sectors,
            shape_yd,
            shape_yh,
            enduse_peak_yd_factor,
            shape_peak_dh
            )

        self.generate_dict_with_tuple_keys(unique_identifier, enduses, sectors, technologies)

    def generate_dict_with_tuple_keys(self, unique_identifier, enduses, sectors, technologies):
        """generate look_up keys to position in dict
        """
        for enduse in enduses:
            for sector in sectors:
                for technology in technologies:
                    self.dict_with_tuple_keys[(enduse, sector, technology)] = unique_identifier

    def get_load_profile(self, enduse, sector, technology, shape):
        """Get shape for a certain technology, enduse and sector

        Parameters
        ----------
        enduse : str
            Enduse
        sector : str
            Sector
        technology : str
            technology
        shape : str
            Type of shape which is to be read out

        Return
        ------
        attr_to_get : array
            Required shape
        """
        '''for load_profile_obj in self.load_profile_list:
            if enduse in load_profile_obj.enduses:
                if sector in load_profile_obj.sectors:
                    if technology in load_profile_obj.technologies:'''

        position_in_dict = self.dict_with_tuple_keys[(enduse, sector, technology)]
        load_profile_obj = self.load_profile_dict[position_in_dict]

        if shape == 'shape_yh':
            return load_profile_obj.shape_yh
        elif shape == 'shape_yd':
            return load_profile_obj.shape_yd
        elif shape == 'shape_y_dh':
            return load_profile_obj.shape_y_dh
        elif shape == 'enduse_peak_yd_factor':
            return load_profile_obj.enduse_peak_yd_factor

        #function_run_crit = False
        '''if (technology in load_profile_obj.technologies
                    and enduse in load_profile_obj.enduses
                    and sector in load_profile_obj.sectors):
            
                # SPEED: Slow version
                attr_to_get = getattr(load_profile_obj, shape)
                function_run_crit = True
                return attr_to_get
        '''
        '''if function_run_crit:
            return attr_to_get
        else:
            sys.exit("Error in get_load_profile: {} {} {} {}".format(
                enduse,
                sector,
                technology,
                shape))
        '''

    def get_shape_peak_dh(self, enduse, sector, technology):
        """Get peak dh shape for a certain technology, enduse and sector
        """
        '''for load_profile_obj in self.load_profile_list:
            if enduse in load_profile_obj.enduses:
                if sector in load_profile_obj.sectors:
                    if technology in load_profile_obj.technologies:'''
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
    """Load profile container to store different shapes

    Parameters
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
    shape_peak_dh : array
        Shape (dh), shape of a day for every hour
    """
    def __init__(self, unique_identifier, technologies, enduses, sectors, shape_yd, shape_yh, enduse_peak_yd_factor, shape_peak_dh=np.ones((24))):
        """Constructor
        """
        self.unique_identifier = unique_identifier
        self.technologies = technologies
        self.enduses = enduses
        self.sectors = sectors
        self.shape_yd = shape_yd
        self.shape_yh = shape_yh
        self.shape_peak_dh = shape_peak_dh
        self.enduse_peak_yd_factor = enduse_peak_yd_factor

        #Calculate percentage for every day
        self.shape_y_dh = self.calc_y_dh_shape_from_yh()

    def calc_y_dh_shape_from_yh(self):
        """Calculate percentage shape for every day
        """
        sum_every_day = np.sum(self.shape_yh, axis=1)
        sum_every_day_p = 1 / sum_every_day
        #sum_every_day_p[np.isnan(sum_every_day_p)] = 0
        #MAYBE TRUEsum_every_day_p = np.nan_to_num(sum_every_day_p) # Replace nan by zero #REMOVE
        sum_every_day_p[np.isinf(sum_every_day_p)] = 0   # Replace inf by zero

        # Multiply (365,) + with (365, 24)
        shape_y_dh = sum_every_day_p[:, np.newaxis] * self.shape_yh

        shape_y_dh[np.isnan(shape_y_dh)] = 0 # Faster than np.nan_to_num

        return shape_y_dh

def absolute_to_relative_without_nan(absolute_array):
    """
    """
    try:
        return (1 / np.sum(absolute_array)) * absolute_array
    except ZeroDivisionError:
        return absolute_array # If the total sum is zero, return same array

def absolute_to_relative(absolute_array):
    """Convert absolute numbers in an array to relative

    If the total sum is zero, return an array with zeros and raise a warning

    Parameters
    ----------
    absolute_array : array
        Contains absolute numbers in it

    Returns
    -------
    relative_array : array
        Contains relative numbers
    """
    try:
        ### ORIGrelative_array = np.nan_to_num((1 / np.sum(absolute_array)) * absolute_array)

        relative_array = (1 / np.sum(absolute_array)) * absolute_array
        relative_array[np.isnan(relative_array)] = 0 # replace nan by zero, faster than np.nan_to_num

        # relative_array[np.isinf(relative_array)] = 0   # replace inf by zero (not necessary because ZeroDivsionError)
    except ZeroDivisionError:
        relative_array = absolute_array # If the total sum is zero, return same array

    return relative_array

def calk_peak_h_dh(enduse_fuel_peak_dh):
    """Iterate peak day fuels and select peak hour
    SPEDO
    Return
    ------
    peak_fueltype_h : array
        Fuel for maximum hour in peak day per fueltype
    """
    # Get maximum value per row (maximum fuel hour per fueltype)
    peak_fueltype_h = np.max(enduse_fuel_peak_dh, axis=1)

    return peak_fueltype_h

def convert_dh_yd_to_yh(shape_yd, shape_y_dh):
    """Convert yd shape and shape for every day (y_dh) into yh

    Parameters
    ----------
    shape_yd : array
        Array with yd shape
    shape_y_dh : array
        Array with y_dh shape

    Return
    ------
    shape_yh : array
        Array with yh shape
    """
    shape_yh = np.zeros((365, 24))
    for day, value_yd in enumerate(shape_yd):
        shape_yh[day] = value_yd * shape_y_dh[day]

    return shape_yh

def get_hybrid_fuel_shapes_y_dh(fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, tech_low_high_p):
    """Calculate  fuel shapes for hybrid technologies for every day in a year (y_dh)

    Depending on the share of service each hybrid technology in every hour,
    the daily fuelshapes of each technology are taken for every hour respectively

    #TODO: IMPROVE DESCRITPION

    Parameters
    ----------
    fuel_shape_boilers_y_dh : array
        Fuel shape of low temperature technology (e.g. boiler technology)
    fuel_shape_hp_y_dh : array
        Fuel shape of high temp technology (y_dh) (heat pump technology)
    tech_low_high_p : array
        Share of service of technology in every hour (heat pump technology)

    Return
    ------
    fuel_shapes_hybrid_y_dh : array
        Fuel shape (y_dh) for hybrid technology

    Example
    --------
    E.g. 0-12, 16-24:   TechA
         12-16          TechA 50%, TechB 50%

    The daily shape is taken for TechA for 0-12 and weighted according to efficency
    Between 12 and Tech A and TechB are taken with 50% shares and weighted with either efficiency

    Info
    ----
    In case no fuel is provided for a day 'fuel_shapes_hybrid_y_dh' for this day is zero. Therfore
    the total sum of 'fuel_shapes_hybrid_y_dh not necessarily 365.
    """
    '''fuel_shapes_hybrid_y_dh = np.zeros((365, 24))

    for day in range(365): #SPEED
        dh_fuel_hybrid = np.zeros(24)
        for hour in range(24): #SPEED

            # Shares of each technology for every hour
            low_p = tech_low_high_p['low'][day][hour]
            high_p = tech_low_high_p['high'][day][hour]

            # Calculate fuel for every hour
            if low_p == 0:
                fuel_boiler = 0
            else:
                fuel_boiler = low_p * fuel_shape_boilers_y_dh[day][hour]

            if high_p == 0:
                fuel_hp = 0
            else:
                fuel_hp = high_p * fuel_shape_hp_y_dh[day][hour]

            # Weighted hourly dh shape with efficiencies
            dh_fuel_hybrid[hour] = fuel_boiler + fuel_hp

        # Normalise dh shape
        fuel_shapes_hybrid_y_dh[day] = absolute_to_relative(dh_fuel_hybrid)
    '''
    # FAST TODO #(share of fuel boiler * fuel shape boiler) + (share of fuel heat pump * shape of heat pump)
    _var = (tech_low_high_p['low'] * fuel_shape_boilers_y_dh) + (tech_low_high_p['high'] * fuel_shape_hp_y_dh)

    # Absolute to relative for every row
    fuel_shapes_hybrid_y_dh = np.apply_along_axis(absolute_to_relative, 1, _var) #absolute_to_relative_without_nan not possible
    '''plt.plot(fuel_shapes_hybrid_y_dh[1])
    plt.show()
    '''
    return fuel_shapes_hybrid_y_dh
