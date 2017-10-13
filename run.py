"""The sector model wrapper for smif to run the energy demand model
"""
import logging
from datetime import date
from smif.model.sector_model import SectorModel
from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.cli import run_model
from energy_demand.dwelling_stock import dw_stock
from energy_demand.read_write import read_data
from energy_demand.main import energy_demand_model
from energy_demand.read_write import data_loader
from energy_demand.assumptions import base_assumptions
from energy_demand.basic import date_handling
from pkg_resources import Requirement, resource_filename

from collections import defaultdict

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """

    def array_to_dict(self, input_array):
        """

        Arguments
        ---------
        input_array : numpy.ndarray
            timesteps, regions, interval

        Returns
        -------
        {}

        """
        data = defaultdict(dict)
        for t_idx, timestep in enumerate(self.timesteps):
            for r_idx, region in enumerate(self.get_region_names('lad')):
                data[timestep][region] = input_array[t_idx, r_idx, 0]
        return data

    def before_model_run(self):
        """Runs prior to any ``simulate()`` step

        Writes scenario data out into the scenario files

        Saves useful data into the ``self.user_data`` dictionary for access
        in the ``simulate()`` method

        Data is accessed using the `get_scenario_data()` method is provided
        as a numpy array with the dimensions timesteps-by-regions-by-intervals.

        Info
        -----
        `self.user_data` allows to pass data from before_model_run to main model
        """
        self.user_data['data_path'] = '/vagrant/data_energy_demand'
        self.processed_path = '/vagrant/data_energy_demand/_processed_data'
        self.result_path = '/vagrant/data_energy_demand/_result_data'

        # Obtain scenario data
        ed_data = {}
        ed_data['print_criteria'] = False #Print criteria

        pop_array = self.get_scenario_data('population')
        ed_data['population'] = self.array_to_dict(pop_array)
        self.user_data['population'] = self.array_to_dict(pop_array)

        gva_array = self.get_scenario_data('gva')
        ed_data['GVA'] = self.array_to_dict(gva_array)
        self.user_data['GVA'] = self.array_to_dict(gva_array)

        floor_array = self.get_scenario_data('floor_area')
        ed_data['rs_floorarea'] = self.array_to_dict(floor_array)
        ed_data['ss_floorarea'] = self.array_to_dict(floor_array)
        ed_data['reg_floorarea_resid'] = self.array_to_dict(floor_array)

        self.user_data['ss_floorarea'] = self.array_to_dict(floor_array)
        self.user_data['reg_floorarea_resid'] = self.array_to_dict(floor_array)

        ed_data['lu_reg'] = self.get_region_names('lad')
        #ed_data['reg_coord'] = regions.get_region_centroids('lad') #TO BE IMPLEMENTED BY THE SMIF GUYS

        # Load data (is to be replaced partly by scenario data (e.g. scenario assumptions))
        path_main = resource_filename(Requirement.parse("energy_demand"), "")
        ed_data['paths'] = data_loader.load_paths(path_main)
        ed_data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])
        ed_data['lookups'] = data_loader.load_basic_lookups()

        ed_data['reg_coord'], _ = data_loader.get_dummy_coordinates_and_regions(ed_data['local_paths']) #REMOVE IF CORRECT DATA IN
        
        ed_data['weather_stations'], ed_data['temp_data'] = data_loader.load_temp_data(ed_data['local_paths'])
        ed_data['enduses'], ed_data['sectors'], ed_data['fuels'] = data_loader.load_fuels(ed_data['paths'], ed_data['lookups'])
        ed_data['sim_param'], ed_data['assumptions'] = base_assumptions.load_assumptions(ed_data, write_sim_param=True)
        ed_data['tech_load_profiles'] = data_loader.load_data_profiles(ed_data['paths'], ed_data['local_paths'], ed_data['assumptions'])
        
        

        #========SCRAP (POP.....) THIS OVERRITES SMIF INPUT REMOVE
        #ed_data = data_loader.dummy_data_generation(ed_data)
        #ed_data['reg_coord'], _ = data_loader.get_dummy_coordinates_and_regions(ed_data['local_paths'])
        #========SCRAP (POP.....) THIS OVERRITES SMIF INPUT REMOVE

        # Initialise scenario
        self.user_data['temp_data'], self.user_data['fts_cont'], self.user_data['sgs_cont'], self.user_data['sd_cont'] = scenario_initalisation(
            self.user_data['data_path'],
            ed_data)

        # Generate dwelling stocks over whole simulation period 
        self.user_data['rs_dw_stock'] = dw_stock.rs_dw_stock(ed_data['lu_reg'], ed_data)
        self.user_data['ss_dw_stock'] = dw_stock.ss_dw_stock(ed_data['lu_reg'], ed_data)

    def initialise(self, initial_conditions):
        """
        """
        pass

    def simulate(self, timestep, data=None):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        timestep : int
            The name of the current timestep
        data : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Notes 
        -----
        1. Get scenario data

        Population data is required as a nested dict::

            data[year][region_geocode]

        GVA is the same::

            data[year][region_geocode]

        Floor area::

            data[year][region_geoode][sector]

        2. Run initialise scenarios
        3. For each timestep, run the model

        Data is provided to these methods in the format::

            {'parameter_name': value_array}

        where ``value_array`` is a regions-by-intervals numpy array.

        """
        self.user_data['data_path'] = '/vagrant/data_energy_demand'

        # ---------
        # Scenario data
        # ---------
        ed_data = {}
        ed_data['print_criteria'] = False # No plt.show() functions are exectued if False
        ed_data['population'] = self.user_data['population']
        ed_data['GVA'] = self.user_data['GVA']
        ed_data['rs_floorarea'] = self.user_data['rs_floor_area']
        ed_data['ss_floorarea'] = self.user_data['ss_floor_area']
        ed_data['reg_floorarea_resid'] = self.user_data['reg_floorarea_resid']

        # ---------
        # Replace data in ed_data with data provided from wrapper or before_model_run
        # Write data from smif to data container from energy demand model
        # ---------
        path_main = resource_filename(Requirement.parse("energy_demand"), "")
        ed_data['lu_reg'] = self.get_region_names('lad')

        #ed_data['reg_coord'] = regions.get_region_centroids('lad') #TO BE IMPLEMENTED BY THE SMIF GUYS
        ed_data['paths'] = data_loader.load_paths(path_main)
        ed_data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])
        ed_data['lookups'] = data_loader.load_basic_lookups()
        ed_data['enduses'], ed_data['sectors'], ed_data['fuels'] = data_loader.load_fuels(ed_data['paths'], ed_data['lookups'])
        ed_data['sim_param'], ed_data['assumptions'] = base_assumptions.load_assumptions(ed_data, write_sim_param=True)
        ed_data['tech_load_profiles'] = data_loader.load_data_profiles(ed_data['paths'], ed_data['local_paths'], ed_data['assumptions'])
        ed_data['weather_stations'], _ = data_loader.load_temp_data(ed_data['local_paths'])
        ed_data['reg_coord'], _ = data_loader.get_dummy_coordinates_and_regions(ed_data['local_paths']) #REPLACE BY SMIF INPUT
        ed_data['sim_param']['current_year'] = timestep
        ed_data['sim_param']['end_year'] = 2020
        ed_data['sim_param']['sim_years_intervall'] = 1

        ed_data['assumptions']['assump_diff_floorarea_pp'] = data['assump_diff_floorarea_pp']
        ed_data['assumptions']['climate_change_temp_diff_month'] = data['climate_change_temp_diff_month']
        ed_data['assumptions']['rs_t_base_heating']['end_yr'] = data['rs_t_base_heating_ey']
        ed_data['assumptions']['efficiency_achieving_factor'] = data['efficiency_achieving_factor']

        # Update: Necessary updates after external data definition
        ed_data['sim_param']['sim_period'] = range(ed_data['sim_param']['base_yr'], ed_data['sim_param']['end_yr'] + 1, ed_data['sim_param']['sim_years_intervall'])
        ed_data['sim_param']['sim_period_yrs'] = int(ed_data['sim_param']['end_yr'] + 1 - ed_data['sim_param']['base_yr'])
        ed_data['sim_param']['list_dates'] = date_handling.fullyear_dates(start=date(ed_data['sim_param']['base_yr'], 1, 1), end=date(ed_data['sim_param']['base_yr'], 12, 31))
        ed_data['assumptions'] = base_assumptions.update_assumptions(ed_data['assumptions']) #Maybe write s_script

        ed_data['rs_dw_stock'] = self.user_data['rs_dw_stock']
        ed_data['ss_dw_stock'] = self.user_data['ss_dw_stock']


        #========SCRAP (POP.....) THIS OVERRITES SMIF INPUT REMOVE
        #ed_data = data_loader.dummy_data_generation(ed_data)
        #ed_data['reg_coord'], _ = data_loader.get_dummy_coordinates_and_regions(ed_data['local_paths'])
        #========SCRAP (POP.....) THIS OVERRITES SMIF INPUT REMOVE

        # -----------------------
        # Load data from scripts (replacing #ed_data = read_data.load_script_data(ed_data))
        # -----------------------
        # fts_cont['ss_service_tech_by_p'], fts_cont['ss_service_fueltype_tech_by_p'], fts_cont['ss_service_fueltype_by_p']
        # Insert from script calculations which are stored in memory
        ed_data['temp_data'] = self.user_data['temp_data']
        ed_data['assumptions']['rs_service_tech_by_p'] = self.user_data['fts_cont']['rs_service_tech_by_p']
        ed_data['assumptions']['ss_service_tech_by_p'] = self.user_data['fts_cont']['ss_service_tech_by_p']
        ed_data['assumptions']['is_service_tech_by_p'] = self.user_data['fts_cont']['is_service_tech_by_p']
        ed_data['assumptions']['rs_service_fueltype_by_p'] = self.user_data['fts_cont']['rs_service_fueltype_by_p']
        ed_data['assumptions']['ss_service_fueltype_by_p'] = self.user_data['fts_cont']['ss_service_fueltype_by_p']
        ed_data['assumptions']['is_service_fueltype_by_p'] = self.user_data['fts_cont']['is_service_fueltype_by_p']
        ed_data['assumptions']['rs_service_fueltype_tech_by_p'] = self.user_data['fts_cont']['rs_service_fueltype_tech_by_p']
        ed_data['assumptions']['ss_service_fueltype_tech_by_p'] = self.user_data['fts_cont']['ss_service_fueltype_tech_by_p']
        ed_data['assumptions']['is_service_fueltype_tech_by_p'] = self.user_data['fts_cont']['is_service_fueltype_tech_by_p']
        ed_data['assumptions']['rs_tech_increased_service'] = self.user_data['sgs_cont']['rs_tech_increased_service']
        ed_data['assumptions']['ss_tech_increased_service'] = self.user_data['sgs_cont']['ss_tech_increased_service']
        ed_data['assumptions']['is_tech_increased_service'] = self.user_data['sgs_cont']['is_tech_increased_service']
        ed_data['assumptions']['rs_tech_decreased_share'] = self.user_data['sgs_cont']['rs_tech_decreased_share']
        ed_data['assumptions']['ss_tech_decreased_share'] = self.user_data['sgs_cont']['ss_tech_decreased_share']
        ed_data['assumptions']['is_tech_decreased_share'] = self.user_data['sgs_cont']['is_tech_decreased_share']
        ed_data['assumptions']['rs_tech_constant_share'] = self.user_data['sgs_cont']['rs_tech_constant_share']
        ed_data['assumptions']['ss_tech_constant_share'] = self.user_data['sgs_cont']['ss_tech_constant_share']
        ed_data['assumptions']['is_tech_constant_share'] = self.user_data['sgs_cont']['is_tech_constant_share']
        ed_data['assumptions']['rs_sig_param_tech'] = self.user_data['sgs_cont']['rs_sig_param_tech']
        ed_data['assumptions']['ss_sig_param_tech'] = self.user_data['sgs_cont']['ss_sig_param_tech']
        ed_data['assumptions']['is_sig_param_tech'] = self.user_data['sgs_cont']['is_sig_param_tech']
        ed_data['assumptions']['rs_installed_tech'] = self.user_data['sgs_cont']['rs_installed_tech']
        ed_data['assumptions']['ss_installed_tech'] = self.user_data['sgs_cont']['ss_installed_tech']
        ed_data['assumptions']['is_installed_tech'] = self.user_data['sgs_cont']['is_installed_tech']
        ed_data['rs_fuel_disagg'] = self.user_data['sd_cont']['rs_fuel_disagg']
        ed_data['ss_fuel_disagg'] = self.user_data['sd_cont']['ss_fuel_disagg']
        ed_data['is_fuel_disagg'] = self.user_data['sd_cont']['is_fuel_disagg']

        # ---------
        # Run model
        # ---------
        results = energy_demand_model(ed_data)

        # ---------
        # Process results
        # ---------
        out_to_supply = results.fuel_indiv_regions_yh

        logging.debug("FINISHED WRAPPER CALCULATIONS")
        return results

    def extract_obj(self, results):
        """Implement this method to return a scalar value objective function

        This method should take the results from the output of the `simulate`
        method, process the results, and return a scalar value which can be
        used as the objective function

        Arguments
        =========
        results : :class:`dict`
            The results from the `simulate` method

        Returns
        =======
        float
            A scalar component generated from the simulation model results
        """
        pass

'''
if __name__ == '__main__':

    data = {'population': {},
            'gva': {},
            'floor_area': {}}


    data['assump_diff_floorarea_pp'] = 1
    data['climate_change_temp_diff_month'] = 1
    data['rs_t_base_heating_ey'] = 1
    data['efficiency_achieving_factor'] = 1

    ed = EDWrapper('ed')
    from smif.convert.area import get_register as get_region_register
    from smif.convert.area import RegionSet
    from smif.convert.interval import get_register as get_interval_register
    from smif.convert.interval import IntervalSet
    from unittest.mock import Mock
    regions = get_region_register()
    regions.register(RegionSet('lad', []))

    ed.before_model_run()

    ed.simulate(2010, data)
'''
