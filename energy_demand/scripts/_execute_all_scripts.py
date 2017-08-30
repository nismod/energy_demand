"""Function to execute different scripts
"""
import os

def run(run_basic_scripts=False, run_scenario_scripts=True):
    """Run scripts

    Parameters
    ----------
    run_basic_scripts : bool,default=False
        If `True` all basic scripts are run
    run_scenario_scripts : bool
        If `True` all scenario scripts are run

    Note
    ----
    If `run_basic_scripts` is true, all scripts are executed
    which only need to be executed once, independently of the scenario.
    E.g. load profiles are loaded from raw files

    `run_scenario_scripts` needs to be run everytime scenario
    assumptiosn are changed
    """
    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-21])
    local_data_path = r'Y:\01-Data_NISMOD\data_energy_demand'

    # Assumptions are written out to csv files
    from energy_demand.assumptions import assumptions
    assumptions.run()

    # Scripts which need to be run for generating raw data
    if run_basic_scripts:

        # Read in temperature data from raw files
        import s_raw_weather_data
        s_raw_weather_data.run(path_main, local_data_path)

        # Read in residenital submodel shapes
        import s_rs_raw_shapes
        s_rs_raw_shapes.run(path_main, local_data_path)

        # Read in service submodel shapes
        import s_ss_raw_shapes
        s_ss_raw_shapes.run(path_main, local_data_path)

    # Scripts which need to be run for every different scenario
    if run_scenario_scripts:

        import s_change_temp
        s_change_temp.run(path_main)

        import s_fuel_to_service
        s_fuel_to_service.run(path_main, local_data_path)

        import s_generate_sigmoid
        s_generate_sigmoid.run(path_main, local_data_path)

        import s_disaggregation
        s_disaggregation.run(path_main, local_data_path)

    print("...  finished running all scripts")
    return

# Execute script
run(run_basic_scripts=False, run_scenario_scripts=True)
