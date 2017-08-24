"""Run all scripts
"""
run_building_scripts = True
run_scenario_scripts = True

"""
Scripts which need to be run for generating raw data
"""
if run_building_scripts:
    
    # Read in residenital submodel shapes
    try:
        import script_rs_read_raw_shapes
    except:
        print("Error: Failed script_rs_read_raw_shapes")

    # Read in service submodel shapes
    try:
        import script_ss_read_raw_shapes
    except:
        print("Error: Failed script_ss_read_raw_shapes")

    # Read in temperature data from raw files
    try:
        import read_raw_weather_data
    except:
        print("Error: Failed read_raw_weather_data")

"""
Scripts which need to be run for every different scenario
"""
if run_scenario_scripts:

    # Read in temperature data and climate change assumptions and change weather data
    try:
        import assump_change_temp
    except:
        print("Error: Failed assump_change_temp")


print("...  finished running all scripts")
