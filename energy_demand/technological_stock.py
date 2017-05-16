"""The technological stock for every simulation year"""
import numpy as np
import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325, R0902, R0913

class Technology(object):
    """Technology Class for residential technologies #TODO

    Notes
    -----
    The attribute `shape_peak_yd_factor` is initiated with dummy data and only filled with real data
    in the `Region` Class. The reason is because this factor depends on regional temperatures
    """
    def __init__(self, tech_name, data, temp_cy, year, reg_shape_yd, reg_shape_yh, peak_yd_factor):
        """Contructor of technology
        """
        self.curr_yr = year
        self.tech_name = tech_name
        self.fuel_type = data['assumptions']['technologies'][self.tech_name]['fuel_type']
        self.eff_by = mf.const_eff_y_to_h(data['assumptions']['technologies'][self.tech_name]['eff_by'])
        self.eff_ey = mf.const_eff_y_to_h(data['assumptions']['technologies'][self.tech_name]['eff_ey'])
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # Non peak
        self.shape_yd = reg_shape_yd
        self.shape_yh = reg_shape_yh

        # Peak
        self.shape_peak_yd_factor = peak_yd_factor # Only factor from year to d TODO: NOT IMPELEMENTED

        #self.shape_peak_dh = reg_shape_peak_dh # TODO

        # Daily load shapes --> Do not provide daily shapes because may be different for month/weekday/weekend etc.
        # See wheter the technology is part of a defined enduse and if yes, get technology specific peak shape
        if self.tech_name in data['assumptions']['list_tech_heating_const']:
            self.shape_peak_dh = (data['shapes_resid_heating_boilers'][3] / np.sum(data['shapes_resid_heating_boilers'][3])) # Peak curve robert sansom
        elif self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
            self.shape_peak_dh = (data['shapes_resid_heating_heat_pump_dh'][3] / np.sum(data['shapes_resid_heating_heat_pump_dh'][3])) # Peak curve robert sansom
        else:
            # Technology is not part of defined enduse (dummy data)
            self.shape_peak_dh = np.ones((24, 1)) # dummy

        # Calculate efficiency in current year
        self.eff_cy = self.calc_efficiency_cy(data, temp_cy, self.curr_yr, self.eff_by, self.eff_ey, self.diff_method, self.eff_achieved_factor)

    # Calculate efficiency in current year
    def calc_efficiency_cy(self, data, temp_cy, curr_yr, eff_by, eff_ey, diff_method, eff_achieved):
        """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency
        # per default linear diffusion assumed
        FUNCTION
        """
        efficiency_diff = eff_ey - eff_by

        if diff_method == 'linear':
            theor_max_eff = mf.linear_diff(data['data_ext']['glob_var']['base_yr'], curr_yr, eff_by, eff_ey, len(data['data_ext']['glob_var']['sim_period'])) # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
        elif diff_method == 'sigmoid':
            theor_max_eff = mf.sigmoid_diffusion(data['data_ext']['glob_var']['base_yr'], curr_yr, data['data_ext']['glob_var']['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        #print("theor_max_eff: " + str(efficiency_diff) + str("  ") + str(theor_max_eff) + str("  ") + str(data['data_ext']['glob_var']['base_yr']) + str("   ") + str(data_ext['glob_var']['curr_yr']))

        # Consider actual achived efficiency
        actual_eff = theor_max_eff * eff_achieved

        # Differencey in efficiency change
        efficiency_change = actual_eff * efficiency_diff

        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change

        # Temperature dependent efficiency
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
            eff_cy_hourly = mf.get_heatpump_eff(
                temp_cy,
                data['assumptions']['heat_pump_slope_assumption'], # Constant assumption of slope (linear assumption, even thoug not linear in realisty): -0.08
                eff_cy,
                data['assumptions']['t_base_heating_resid']['base_yr']
            )
        else:
            # Non temperature dependent efficiencies
            eff_cy_hourly = eff_cy

        return eff_cy_hourly

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.

    a Region Object needs to be generated

    #TODO: Assert if all technologies were assigned shape

    Parameters
    ----------
    data : dict
        tbd
    assumptions : dict
        tbd
    curr_yr : int
        Current year

    Notes
    -----
    The daily and hourly shape of the fuel used by this Technology
    is initiated with zeros. Within the `Region` Class these attributes
    are filled with real values.
    """
    def __init__(self, data, temp_cy, year):
        """Constructor of technologies for residential sector
        """

        # Crate all technologies and add as attribute
        for technology_name in data['tech_lu']:
            dummy_shape_yd = np.ones((365, 24))
            dummy_shape_yh = np.ones((365, 24))
            dummy_shape_peak_yd_factor = np.ones((365, 24))

            # Technology object
            technology_object = Technology(
                technology_name,
                data,
                temp_cy,
                year,
                dummy_shape_yd,
                dummy_shape_yh,
                dummy_shape_peak_yd_factor,
            )

            # Set technology object as attribute
            ResidTechStock.__setattr__(
                self,
                technology_name,
                technology_object
            )

    def get_technology_attribute(self, technology, attribute_to_get):
        """Read an attrribute from a technology in the technology stock
        """
        tech_object = getattr(self, str(technology))
        tech_attribute = getattr(tech_object, str(attribute_to_get))

        return tech_attribute

    def set_tech_attribute(self, technology, attribute_to_set, value_to_set):
        """Read an attrribute from a technology in the technology stock
        """
        tech_object = getattr(self, str(technology))
        setattr(tech_object, str(attribute_to_set), value_to_set)
