"""The sector model wrapper for smif to run the energy demand model
"""
import numpy as np
from datetime import date
from smif.model.sector_model import SectorModel
from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.cli import run_model
from energy_demand.dwelling_stock import dw_stock
from energy_demand.read_write import read_data
from energy_demand.main import energy_demand_model
from energy_demand.read_write import data_loader
from energy_demand.assumptions import assumptions
from energy_demand.basic import date_handling
from pkg_resources import Requirement
from pkg_resources import resource_filename

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def initialise(self, initial_conditions):
        
        # energy_demand_data_path = '/vagrant/energy_demand_data'
        #energy_demand_data_processed_path = '/vagrant/energy_demand_data/_processed_data'
        #energy_demand_data_result_path = '/vagrant/energy_demand_data/_result_data'

        # Scenario data
        # ed_data = {}
        # ed_data['population'] = data['population']
        # ed_data['GVA'] = data['gva']
        # ed_data['rs_floorarea'] = data['floor_area']
        # ed_data['ss_floorarea'] = data['floor_area'] #Wrong TODO
        # ed_data['reg_floorarea_resid'] = data['floor_area']
        # ed_data['lu_reg'] = self.regions.get_entry('lad').get_entry_names()

        # # Load data (is to be replaced partly by scenario data (e.g. scenario assumptions))
        # path_main = resource_filename(Requirement.parse("energy_demand"), "")
        # ed_data['paths'] = data_loader.load_paths(path_main)
        # ed_data['local_paths'] = data_loader.load_local_paths(energy_demand_data_path)
        # ed_data = data_loader.load_fuels(ed_data)
        # ed_data['sim_param'], ed_data['assumptions'] = assumptions.load_assumptions(ed_data)
        # ed_data['weather_stations'], ed_data['temperature_data'] = data_loader.load_data_temperatures(ed_data['local_paths'])
        # ed_data = data_loader.dummy_data_generation(ed_data)

        # # Initialise SCNEARIO == NEEDS TO BE IN INIT
        # scenario_initalisation(energy_demand_data_path, ed_data)
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

        """
        energy_demand_data_path = '/vagrant/energy_demand_data'
        #energy_demand_data_processed_path = '/vagrant/energy_demand_data/_processed_data'
        #energy_demand_data_result_path = '/vagrant/energy_demand_data/_result_data'

        # Scenario data
        ed_data = {}
        ed_data['population'] = data['population']
        ed_data['GVA'] = data['gva']
        ed_data['rs_floorarea'] = data['floor_area']
        ed_data['ss_floorarea'] = data['floor_area'] #Wrong TODO
        ed_data['reg_floorarea_resid'] = data['floor_area']
        ed_data['lu_reg'] = self.regions.get_entry('lad').get_entry_names()

        # Load data (is to be replaced partly by scenario data (e.g. scenario assumptions))
        path_main = resource_filename(Requirement.parse("energy_demand"), "")
        ed_data['paths'] = data_loader.load_paths(path_main)
        ed_data['local_paths'] = data_loader.load_local_paths(energy_demand_data_path)
        ed_data['lookups'] = data_loader.load_basic_lookups()
        ed_data = data_loader.load_fuels(ed_data)
        ed_data = data_loader.load_data_profiles(ed_data)
        ed_data['sim_param'], ed_data['assumptions'] = assumptions.load_assumptions(ed_data)
        ed_data['weather_stations'], ed_data['temperature_data'] = data_loader.load_data_temperatures(ed_data['local_paths'])
        ed_data = data_loader.dummy_data_generation(ed_data)
    
        scenario_initalisation(energy_demand_data_path, ed_data)

        # Write data from smif to data container from energy demand model
        ed_data['sim_param']['current_year'] = timestep
        ed_data['sim_param']['end_year'] = 2015
        ed_data['sim_param']['sim_years_intervall'] = 1

        ed_data['assumptions']['assump_diff_floorarea_pp'] = data['assump_diff_floorarea_pp']
        ed_data['assumptions']['climate_change_temp_diff_month'] = data['climate_change_temp_diff_month']
        ed_data['assumptions']['rs_t_base_heating']['end_yr'] = data['rs_t_base_heating_ey']
        ed_data['assumptions']['efficiency_achieving_factor'] = data['efficiency_achieving_factor']

        # Update: Necessary updates after external data definition
        ed_data['sim_param']['sim_period'] = range(ed_data['sim_param']['base_yr'], ed_data['sim_param']['end_yr'] + 1, ed_data['sim_param']['sim_years_intervall'])
        ed_data['sim_param']['sim_period_yrs'] = int(ed_data['sim_param']['end_yr'] + 1 - ed_data['sim_param']['base_yr'])
        ed_data['sim_param']['list_dates'] = date_handling.fullyear_dates(
            start=date(ed_data['sim_param']['base_yr'], 1, 1),
            end=date(ed_data['sim_param']['base_yr'], 12, 31))

        ed_data['assumptions'] = assumptions.update_assumptions(ed_data['assumptions']) #Maybe write s_script

        # Generate dwelling stocks over whole simulation period
        ed_data['rs_dw_stock'] = dw_stock.rs_dw_stock(ed_data['lu_reg'], ed_data)
        ed_data['ss_dw_stock'] = dw_stock.ss_dw_stock(ed_data['lu_reg'], ed_data)

        # Run model
        ed_data = read_data.load_script_data(ed_data)

        _, results = energy_demand_model(ed_data)

        print("FINISHED WRAPPER CALCULATIONS")
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

    ed.simulate(2010, data)