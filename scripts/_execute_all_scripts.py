"""Run all scripts
"""
run_building_scripts = False
run_scenario_scripts = True

"""
Scripts which need to be run for generating raw data
"""
if run_building_scripts:
    
    # Read in residenital submodel shapes
    try:
        import script_rs_read_raw_shapes
    except Exception as e:
        print("Error: Failed script_rs_read_raw_shapes")
        raise e

    # Read in service submodel shapes
    except Exception as e:
        print("Error: Failed script_ss_read_raw_shapes")
        raise e

    # Read in temperature data from raw files
    try:
        import script_read_raw_weather_data
    except Exception as e:
        print("Error: Failed read_raw_weather_data")
        raise e



"""
Scripts which need to be run for every different scenario
"""
if run_scenario_scripts:

    # Read in temperature data and climate change assumptions and change weather data
    try:
        import script_assump_change_temp
    except Exception as e:
        print("Error: Failed assump_change_temp")
        raise e

    try:
        import script_convert_to_service
    except Exception as e:
        print("Error: Failed assump_change_temp")
        raise e

    try:
        import script_assump_generate_sigmoid
    except Exception as e:
        print("Error: Failed script_assump_generate_sigmoid")
        raise e


print("...  finished running all scripts")
