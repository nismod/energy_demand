"""Generate plots for multiple scenarios
"""
import os
import sys
from energy_demand.processing import single_scenario

def process_result_multi_scen(
        path_to_scenarios="C:/Users/cenv0553/ed/results/_multiple_TEST",
        path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/msoa_uk/msoa_lad_2015_uk.shp",
        base_yr=2015,
        comparison_year=2050
    ):
    """Iterate the folders with scenario
    runs and generate PDF results of individual
    simulation runs

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    """

    raise Exception("dddd " + str(comparison_year))
    # Chose which plots should be generated
    plot_crit_dict = {
        "spatial_results": True,              # Spatial geopanda maps

        "plot_differences_p": True,           # Spatial maps of percentage difference per fueltype over time
        "plot_total_demand_fueltype": True, #False,  # Spatial maps of total demand per fueltype over time
        "plot_population": False,             # Spatial maps of population
        "plot_load_factors": False,           # Spatial maps of load factor
        "plot_load_factors_p": False,         # Spatial maps of load factor change
        "plot_abs_peak_h": False,             # Spatial maps of peak h demand
        "plot_diff_peak_h": True,             # Spatial maps of peak h difference (%)

        "plot_stacked_enduses": True,
        "plot_y_all_enduses": True,
        "plot_fuels_enduses_y": True,
        "plot_lf": False,
        "plot_week_h": False,
        "plot_h_peak_fueltypes": True,
        "plot_averaged_season_fueltype": True, # Compare for every season and daytype the daily loads
        "plot_radar": True,
        "plot_radar_seasonal": False,                      # Plot radar spider charts
        "plot_line_for_every_region_of_peak_demand": True,
        "plot_lad_cross_graphs": True}

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    for scenario in scenarios:
        if scenario == '__results_multiple_scenarios':
            pass
        else:

            # Execute script to generate PDF results
            single_scenario.main(
                os.path.join(path_to_scenarios, scenario),
                path_shapefile_input,
                plot_crit_dict,
                base_yr=base_yr,
                comparison_year=comparison_year)

    return

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    process_result_multi_scen(*sys.argv[1:])


# -------------------------------------
# Function to generate plots based on simulation results stored in a folder
# -------------------------------------
'''process_result_multi_scen(

    # Provide path to folder where results are stored (from step 3.2 in the readme file)
    "C:/Users/cenv0553/ed/results/_multiple_TEST",         

    # Provide path to shapefile of corresponding geography of results                                      
    #os.path.abspath('C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp')) # Used for LAD
    os.path.abspath('C:/Users/cenv0553/ED/data/region_definitions/msoa_uk/msoa_lad_2015_uk.shp'),# Used for MSOA

    # Provide base year of simulation
    base_yr=2015,

    # Provide year to generate comparison plots (provide e.g. latest simulation year)
    comparison_year=2050)'''

'''process_result_multi_scen(
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_eff_factor_example"),
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example"),
    #os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example_efficiency_improvement"),
    #os.path.abspath("C:/Users/cenv0553/ED/_mutli_results_hp_50__eff_achieved_0.5_pop_scenarios"),
    #os.path.abspath("C:/Users/cenv0553/ED/_MULTI"),
    #os.path.abspath("C:/Users/cenv0553/ED/__STORAGE"),
    #"C:/Users/cenv0553/ed/results/Fig_08_09",
    "C:/Users/cenv0553/ed/results/scen_D",
    os.path.abspath('C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp'))
'''