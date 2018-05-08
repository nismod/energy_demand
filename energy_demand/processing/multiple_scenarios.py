"""Generate plots for multiple scenarios
"""
import os
from energy_demand.processing import single_scenario

def process_result_multi_scen(path_to_scenarios, path_shapefile_input):
    """Iterate the folders with scenario
    runs and generate PDF results of individual
    simulation runs

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    """
    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    for scenario in scenarios:
        print("Generating result pdf for scenario {}".format(scenario))
        # Execute script to generate PDF results
        single_scenario.main(
            os.path.join(path_to_scenarios, scenario),
            path_shapefile_input)

    return

# Execute rusult processing for every scenario
process_result_multi_scen(
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_eff_factor_example"),
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example"),
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example_efficiency_improvement"),
    #os.path.abspath("C:/Users/cenv0553/ED/_mutli_results_hp_50__eff_achieved_0.5_pop_scenarios"),
    #os.path.abspath("C:/Users/cenv0553/ED/_MULTI"),
    #os.path.abspath("C:/Users/cenv0553/ED/__STORAGE"),
    "C:/Users/cenv0553/ed/results/Fig_08_09",
    os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
