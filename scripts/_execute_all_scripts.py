"""Function to execute different scripts
"""

def run(run_basic_scripts=False, run_scenario_scripts=True):
    """Run scripts

    Parameters
    ----------
    run_basic_scripts : bool,default=False
        If ´True´ all basic scripts are run
    run_scenario_scripts : bool
        If ´True´ all scenario scripts are run

    Note
    ----
    If ´run_basic_scripts´ is true, all scripts are executed
    which only need to be executed once, independently of the scenario.
    E.g. load profiles are loaded from raw files

    ´run_scenario_scripts´ needs to be run everytime scenario
    assumptiosn are changed
    """

    # Assumptions are written out to csv files
    from energy_demand.assumptions import assumptions
    assumptions.run()

    # Scripts which need to be run for generating raw data
    if run_basic_scripts:

        # Read in residenital submodel shapes
        import script_rs_read_raw_shapes
        script_rs_read_raw_shapes.run()

        # Read in temperature data from raw files
        import script_read_raw_weather_data
        script_read_raw_weather_data.run()

    # Scripts which need to be run for every different scenario
    if run_scenario_scripts:

        # Read in temperature data and climate change assumptions and change weather data
        import script_assump_change_temp
        script_assump_change_temp.run()

        import script_convert_to_service
        script_convert_to_service.run()

        import script_assump_generate_sigmoid
        script_assump_generate_sigmoid.run()

    print("...  finished running all scripts")

# Execute script
run(run_basic_scripts=False, run_scenario_scripts=True)
