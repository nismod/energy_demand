'''Script to create figures for paper


Info
-----
A folder (path_in) with the following structure needs to be generated and the SMIF simulation restuls stored, for 
example in the path (C:/path_results/EW/Central/NF1/SMIF_RESULTS)

... path_in
        EW
            central
                WeatherScenario (i.e. NF1))
                ...
            decentral
                WeatherScenario
                ...
        MW     
            ...
'''
import os
import shutil
from energy_demand.plotting import chaudry_et_al_functions #Reset imports


# -----------------------------------
# Configure paths
# -----------------------------------
path_out = "C:/_test"   # Path to store results
path_in = "C:/Users/cenv0553/nismod2/results/PLOTTINGFOLDER" # Path with model runs

# Configure simulation names
simulation_name = 'energy_sd_constrained'   # Name of model

scenarios = ['EW', 'MV',] 
weather_scenario = 'NF1'
fueltype = 'electricity'
unit = 'GW'

# ------------------------
# Create empty result folders and delte preivous results
# ------------------------
shutil.rmtree(path_out) # delete results
chaudry_et_al_functions.create_folder(path_out)

paths_figs = ['fig3', 'fig4', 'fig5', 'fig6']

for fig_name in paths_figs:
    path_fig = os.path.join(path_out, fig_name)
    chaudry_et_al_functions.create_folder(path_fig)

# ------------------------
# Load data
# ------------------------
data_container = chaudry_et_al_functions.load_data(
    path_in,
    simulation_name=simulation_name,
    scenarios=scenarios,
    unit=unit)

print("... finished loading data")

# ------------------------
# Create figures
# ------------------------
# Dasboard figures
chaudry_et_al_functions.fig_3_hourly_comparison(
    path_out,
    data_container,
    scenarios=scenarios,
    weather_scearnio=weather_scenario,
    unit=unit,
    fueltypes=['heat'])#electricity', 'heat'])

#chaudry_et_al_functions.fig_4(data_container, fueltype=fueltype)
#chaudry_et_al_functions.fig_5(data_container, fueltype=fueltype)
#chaudry_et_al_functions.fig_6(data_container, fueltype=fueltype)
print("Finished creasting figures")