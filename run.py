"""The sector model wrapper for smif to run the energy demand model
"""
import os
import numpy as np
from smif.model.sector_model import SectorModel

from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.cli import run_model

class EDWrapper(SectorModel):
    """Energy Demand Wrapper"""

    def simulate(self, timestep, data=None):
        """

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

        # Scenario data
        population = data['population']
        gva = data['gva']
        floor_area = data['floor_area']

        data = load_assumptions()

        scenario_initalisation(data, output_path)

        data['sim_param']['current_year'] = timestep

        # Parameters
        assump_diff_floorarea_pp = data['assump_diff_floorarea_pp']
        climate_change_temp_diff_month = data['climate_change_temp_diff_month']
        rs_t_base_heating_ey = data['rs_t_base_heating_ey']
        efficiency_achieving_factor = data['efficiency_achieving_factor']

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
