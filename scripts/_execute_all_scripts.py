"""Run all scripts
"""
run_building_scripts = False
run_scenario_scripts = True


"""Executed if assumptions gets imported
""" 
if run_building_scripts == True or run_scenario_scripts == True:
    from energy_demand.assumptions import assumptions
    assumptions.run()

"""
Scripts which need to be run for generating raw data
"""
if run_building_scripts:
    
    # Read in residenital submodel shapes
    import script_rs_read_raw_shapes
    script_rs_read_raw_shapes.run()

    # Read in temperature data from raw files
    import script_read_raw_weather_data
    script_read_raw_weather_data.run()

"""
Scripts which need to be run for every different scenario
"""
if run_scenario_scripts:

    # Read in temperature data and climate change assumptions and change weather data
    import script_assump_change_temp
    script_assump_change_temp.run() # Run script

    import script_convert_to_service
    script_convert_to_service.run()

    import script_assump_generate_sigmoid
    script_assump_generate_sigmoid.run()

print("...  finished running all scripts")
