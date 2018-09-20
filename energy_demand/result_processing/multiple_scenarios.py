"""Function to generate plots based on simulation results stored in a folder
"""
import os
import sys

from energy_demand.result_processing import single_scenario

def process_result_multi_scen(
        path_to_folder_with_scenarios="C:/Users/cenv0553/ed/results/_multiple_TEST",
        #path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/msoa_uk/msoa_lad_2015_uk.shp",
        path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp",
        base_yr=2015,
        comparison_year=2050
    ):
    """Iterate the folders with scenario
    runs and generate PDF results of individual
    simulation runs

    Arguments
    ----------
    path_to_folder_with_scenarios : str
        Path to folders with stored results
    """

    # Chose which plots should be generated
    plot_crit_dict = {
        "spatial_results": True,              # Spatial geopanda maps

        "plot_differences_p": True,           # Spatial maps of percentage difference per fueltype over time
        "plot_total_demand_fueltype": True, #False,  # Spatial maps of total demand per fueltype over time
        "plot_population": True,             # Spatial maps of population
        "plot_load_factors": True,           # Spatial maps of load factor
        "plot_load_factors_p": True,         # Spatial maps of load factor change
        "plot_abs_peak_h": True,             # Spatial maps of peak h demand
        "plot_diff_peak_h": True,             # Spatial maps of peak h difference (%)

        "plot_stacked_enduses": True,
        "plot_y_all_enduses": True,
        "plot_fuels_enduses_y": True,
        "plot_lf": True,
        "plot_week_h": True,
        "plot_h_peak_fueltypes": True,
        "plot_averaged_season_fueltype": True, # Compare for every season and daytype the daily loads
        "plot_radar": True,
        "plot_radar_seasonal": True,                      # Plot radar spider charts
        "plot_line_for_every_region_of_peak_demand": True,
        "plot_lad_cross_graphs": True}

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_folder_with_scenarios)

    for scenario in scenarios:
        if scenario == '__results_multiple_scenarios':
            pass
        else:

            # Execute script to generate PDF results
            single_scenario.main(
                os.path.join(path_to_folder_with_scenarios, scenario),
                path_shapefile_input,
                plot_crit_dict,
                base_yr=base_yr,
                comparison_year=comparison_year)

    return

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    process_result_multi_scen(*sys.argv[1:])
