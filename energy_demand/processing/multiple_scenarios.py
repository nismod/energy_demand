"""Generate plots for multiple scenarios
"""
import os
import logging
from energy_demand.read_write import read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_multiple_scenarios
from energy_demand.processing import single_scenario
from energy_demand.basic import basic_functions

def process_result_multi_scen(path_to_scenarios, path_shapefile_input):
    """Iterate the folders with scenario
    runs and calculate PDF results

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    """
    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    for scenario in scenarios:
        single_scenario.main(
            os.path.join(path_to_scenarios, scenario),
            path_shapefile_input)

    return

# Execute rusult processing for every scenario
process_result_multi_scen(
    os.path.abspath("C:/Users/cenv0553/ED/_multiple_results"),
    os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))

