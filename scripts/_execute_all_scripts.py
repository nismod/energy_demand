"""Run all scripts
"""
# Read in residenital submodel shapes
import script_rs_read_raw_shapes

# Read in service submodel shapes
import script_ss_read_raw_shapes

# Read in temperature data from raw files
import read_raw_weather_data

# Read in temperature data and climate change assumptions and change weather data
import assump_change_temp

print("..  finished running all scripts")
