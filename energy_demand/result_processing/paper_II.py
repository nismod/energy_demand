"""Function to generate plots based on simulation results stored in a folder
"""
import os
import sys

from energy_demand.plotting import plots_paper_II

def paper_II_plots(
        path_to_folder_with_scenarios="C:/Users/cenv0553/ed/results/_multiple_TEST",
        path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp"
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

        # Needs to have weatehryr_stationid files in folder
        "plot_national_regional_hdd_disaggregation": False,

        # Plot weather variability for every weather station
        # of demand generated with regional HDD calculation
        "plot_weather_day_year": False,

        # Plot spatial distribution of differences in
        # variability of demand by weather variability
        # normed by population
        "plot_spatial_weather_var_peak": False,

        # Plot scenario years sorted with weather variability
        "plot_scenarios_sorted": True}

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_folder_with_scenarios)

    scenario_names_ignored = [
        '__results_multiple_scenarios',
        '_FigII_non_regional_2015',
        '_results_PDF_figs']

    for scenario in scenarios:
        if scenario in scenario_names_ignored:
            pass
        else:
            plots_paper_II.main(
                os.path.join(path_to_folder_with_scenarios, scenario),
                path_shapefile_input,
                plot_crit_dict)
    return

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    paper_II_plots(*sys.argv[1:])
