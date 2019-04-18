'''Script to create figures for paper


Info
-----
A folder (path_in) with the following structure needs to be generated:

... path_in
        EW
            central
                WeatherScenario
                ...
            decentral
                WeatherScenario
                ...
        MW     
            ...
'''
import os
from energy_demand.plotting import chaudry_et_al_functions #Reset imports


# -----------------------------------
# Configure paths
# -----------------------------------
path_out = "C:/_test"   # Path to store results

path_in = "C:/Users/cenv0553/nismod2/results/PLOTTINGFOLDER"            # Path with results

scenarios = ['EV'] #'MV', 
weather_scenario = 'NF1'
fueltype = 'electricity'

# ------------------------
# Create empty result folders
# ------------------------
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
    scenarios=scenarios)

print("loaded data")

# ------------------------
# Create figures
# ------------------------
chaudry_et_al_functions.fig_3(data_container, fueltype=fueltype)
chaudry_et_al_functions.fig_4(data_container, fueltype=fueltype)
chaudry_et_al_functions.fig_5(data_container, fueltype=fueltype)
chaudry_et_al_functions.fig_6(data_container, fueltype=fueltype)
print("Finished creasting figures")