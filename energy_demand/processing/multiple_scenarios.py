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
        if scenario == '__results_multiple_scenarios':
            pass
        else:

            # Execute script to generate PDF results
            single_scenario.main(
                os.path.join(path_to_scenarios, scenario),
                path_shapefile_input)

    return

# Execute rusult processing for every scenario
#process_result_multi_scen("C:/Users/cenv0553/ed/results/scen_A", os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
#process_result_multi_scen("C:/Users/cenv0553/ed/results/scen_B", os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
#process_result_multi_scen("C:/Users/cenv0553/ed/results/scen_C", os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
#process_result_multi_scen("C:/Users/cenv0553/ed/results/scen_D", os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))

# Use this to generate spatial plots
process_result_multi_scen(
    "C:/Users/cenv0553/ed/results/_multiple_TEST",
    #os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
    os.path.abspath('C:/Users/cenv0553/ED/data/region_definitions/msoa_uk/msoa_lad_2015_uk.shp'))
    

'''process_result_multi_scen(
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_eff_factor_example"),
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example"),
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example_efficiency_improvement"),
    #os.path.abspath("C:/Users/cenv0553/ED/_mutli_results_hp_50__eff_achieved_0.5_pop_scenarios"),
    #os.path.abspath("C:/Users/cenv0553/ED/_MULTI"),
    #os.path.abspath("C:/Users/cenv0553/ED/__STORAGE"),
    #"C:/Users/cenv0553/ed/results/Fig_08_09",
    "C:/Users/cenv0553/ed/results/scen_D",
    os.path.abspath('C:/Users/cenv0553/ED/data/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
'''