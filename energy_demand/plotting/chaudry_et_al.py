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


filenames = {
    'emissions': {
        'output_e_emissions_eh_timestep':'gray',
        'output_e_emissions_timestep': 'green',
        'output_h_emissions_eh_timestep': 'yellow',
    },
    #Electricity Generation mix in energy hubs
    'elec_hubs': { 
        'output_eh_gas_fired_other_timestep': 'gray',
        'output_eh_chp_gas_timestep': 'peru',
        'output_eh_chp_biomass_timestep': 'green',
        'output_eh_chp_waste_timestep': 'violet',
        'output_eh_fuel_cell_timestep': 'slateblue',
        'output_eh_wind_power_timestep': 'firebrick',
        'output_eh_pv_power_timestep': 'orange',
        'output_eh_tran_e_timestep': 'darkcyan'},

    #Electricity Generation mix in electricity transmisison
    'elec_transmission': {
        'output_tran_gas_fired_timestep': 'olivedrab',
        'output_tran_coal_timestep': 'olivedrab',
        'output_tran_pump_power_timestep': 'olivedrab',
        'output_tran_hydro_timestep': 'olivedrab',
        'output_tran_nuclear_timestep': 'olivedrab',
        'output_tran_interconnector_timestep': 'olivedrab',
        'output_tran_renewable_timestep': 'olivedrab',
        'output_e_reserve_timestep': 'olivedrab',
        'output_tran_wind_power_timestep': 'olivedrab',
        'output_tran_pv_power_timestep': 'olivedrab',
        'output_tran_wind_curtailed_timestep': 'olivedrab',
        'output_tran_pv_curtailed_timestep': 'olivedrab'},

    #Heat Supply Mix in energy hubs
    'heat_hubs':{ 
        'output_eh_gasboiler_b_timestep': 'darkcyan',
        'output_eh_heatpump_b_timestep': 'plum',
        'output_eh_gasboiler_dh_timestep': 'orange',
        'output_eh_gaschp_dh_timestep': 'y',
        'output_eh_heatpump_dh_timestep': 'indianred',
        'output_eh_biomassboiler_b_timestep': 'red',
        'output_eh_biomassboiler_dh_timestep': 'gold',
        'output_eh_biomasschp_dh_timestep': 'darkgreen',
        'output_eh_wastechp_dh_timestep': 'darkmagenta',
        'output_eh_electricboiler_b_timestep': 'aqua',
        'output_eh_electricboiler_dh_timestep': 'greenyellow',
        'output_eh_hydrogenboiler_b_timestep': 'yellow',
        'output_eh_hydrogen_fuelcell_dh_timestep': 'olivedrab',
        'output_eh_hydrogen_heatpump_b_timestep': 'gold'},

    #Natural gas supply mix in gas transmissios
    'gas_transmission': {
        'output_gas_domestic_timestep': 'olivedrab',
        'output_gas_lng_timestep': 'olivedrab',
        'output_gas_interconnector_timestep': 'olivedrab',
        'output_gas_storage_timestep': 'olivedrab',
        'output_storage_level_timestep': 'olivedrab',
    },
    #Load Shedding (Unserved demand)
    'load_shedding': {
        'output_gas_load_shed_timestep': 'olivedrab',
        'output_elec_load_shed_timestep': 'olivedrab',
        'output_gas_load_shed_eh_timestep': 'olivedrab',
        'output_elec_load_shed_eh_timestep': 'olivedrab',
    },
    #Gas Supply Mix in Energy hubs
    'gas_hubs': {
        'output_eh_tran_g_timestep': 'olivedrab',
        'output_eh_gas_qs_timestep': 'olivedrab',
        'output_eh_gstorage_level_timestep': 'olivedrab',
    },
    #Hydrogen supply mix in energy hubs
    'hydrogen_hubs': {
        'output_eh_h2_timestep': 'olivedrab',
        'output_eh_h2_qs_timestep': 'olivedrab',
        'output_eh_h2storage_level_timestep': 'olivedrab',
    }

}

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
    filenames=filenames,
    scenarios=scenarios,
    weather_scearnio=weather_scenario,
    unit=unit,
    types_to_plot=['elec_hubs', 'heat_hubs'])


#chaudry_et_al_functions.fig_4(data_container, fueltype=fueltype)
#chaudry_et_al_functions.fig_5(data_container, fueltype=fueltype)
#chaudry_et_al_functions.fig_6(data_container, fueltype=fueltype)
print("Finished creasting figures")