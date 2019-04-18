"""Functions to generate figures
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_folder(path_folder, name_subfolder=None):
    """Creates folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str, default=None
        Name of subfolder to create
    """
    if not name_subfolder:
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
    else:
        path_result_subolder = os.path.join(path_folder, name_subfolder)
        if not os.path.exists(path_result_subolder):
            os.makedirs(path_result_subolder)

def load_data(in_path, scenarios, simulation_name):
    """Read results

    Returns
    data_container : [scenario][mode][weather_scenario
    """

    data_container = {}

    for scenario in scenarios:
        data_container[scenario] = {}

        for mode in ['CENTRAL', 'DECENTRAL']:
            data_container[scenario][mode] = {}

            # Iterate over weather scenarios
            path_scenarios = os.path.join(in_path, scenario, mode)
            weather_scenarios = os.listdir(path_scenarios)

            for weather_scenario in weather_scenarios:
                data_container[scenario][mode][weather_scenario] = {}

                # ---------------------------
                # Load supply generation mix
                # ---------------------------
                data_container[scenario][mode][weather_scenario] ['energy_supply_constrained'] = {}
                path_supply_mix = os.path.join(in_path, scenario, mode, weather_scenario, simulation_name, 'energy_supply_constrained', 'decision_0')

                all_files = os.listdir(path_supply_mix)

                for file_name in all_files:
                    path_file = os.path.join(path_supply_mix, file_name)
                    print(".... loading file: {}".format(file_name))

                    # Load data
                    data_file = pd.read_csv(path_file)

                    try:
                        # Aggregate across every energy hub region and group by "seasonal week"
                        df_to_plot_national = data_file.groupby(data_file['seasonal_week']).sum()

                        # Set seasonal week attribute as index
                        df_to_plot_national.set_index('seasonal_week')
                    except:
                        print("{}  has wrong format".format(file_name))
                    '''# Set energy_hub as index
                    try:
                        data_file.set_index('energy_hub')
                    except:
                        print("... file does not have 'energy_hub' as column")'''

                    data_container[scenario][mode][weather_scenario]['energy_supply_constrained'][file_name] = df_to_plot_national

    return data_container


def fig_3(path_out, data_container, scenarios, weather_scearnio, fueltype, years=[2015, 2030, 2050]):
    """Create x-y chart of a time-span (x-axis: demand, y-axis: time)
    """

    '''
    technologies_to_plot = {
        electricity': [
            'output_industry_electricity_boiler_electricity_timestep',
            'output_industry_electricity_district_heating_electricity_timestep',
            'output_industry_electricity_heat_pumps_electricity_timestep',
            'output_industry_electricity_non_heating_timestep_2015',

            'output_service_electricity_boiler_electricity_timestep',
            'output_service_electricity_district_heating_electricity_timestep',
            'output_service_electricity_heat_pumps_electricity_timestep',
            'output_service_electricity_non_heating_timestep',
            
            'output_residential_electricity_boiler_electricity_timestep',
            'output_residential_electricity_district_heating_electricity_timestep',
            'output_residential_electricity_heat_pumps_electricity_timestep',
            'output_residential_electricity_non_heating_timestep'
            ]
    }
    '''
    file_names_to_plot = {
        'electricity': [
            'output_eh_electricboiler_b_timestep',
            'output_eh_heatpump_b_timestep',
            'output_eh_pv_power_timestep',
            ]}

    fig_dict = {}
    path_out_folder = os.path.join(path_out, 'fig3')

    for year in years:
        fig_dict[year] = {}
        for mode in ['DECENTRAL', 'CENTRAL']:
            fig_dict[year][mode] = {}

            for scenario in scenarios:
                fig_dict[year][mode][scenario] = {}

                data_files = data_container[scenario][mode][weather_scearnio]['energy_supply_constrained']

                files_to_plot = file_names_to_plot[fueltype]

                # Get all correct data to plot
                df_to_plot = pd.DataFrame()
        
                for file_name, file_data in data_files.items():
                    
                    file_name_split_without_timpestep = file_name[:-9] #remove ending

                    file_name_split = file_name.split("_")
                    year_simulation = int(file_name_split[-1][:4])

                    if (year == year_simulation) and (file_name_split_without_timpestep in files_to_plot):
                        value_column = list(file_data.columns)[1]
                        print("File_name: {} Value column: {}".format(file_name_split_without_timpestep, value_column))
                        df_to_plot[str(value_column)] = file_data[value_column]
                
                # Aggregate across every energy hub region and group by "seasonal week"
                #df_to_plot_national = df_to_plot.groupby(df_to_plot['seasonal_week']).sum()

                # Select hours to plots
                hours_selected = range(1, 25) #TODO SELECT TIME INTERVALE TP LOT
                df_to_plot_hrs_to_plot = df_to_plot.loc[hours_selected]

                fig_dict[year][mode][scenario] = df_to_plot_hrs_to_plot

        print("--ploting --") #MOVE DOWN ELEMENTS

        # ----------
        # Plot graph
        # ----------
        for scenario in scenarios:
            df_right = fig_dict[year]['CENTRAL'][scenario]
            df_left = fig_dict[year]['CENTRAL'][scenario] * -1 #Muptplied
            #df_to_plot.plot.area()
            #df_to_plot.plot.bar(stacked=True)#, orientation='vertical')
            
            # Add vertical line
            fig, ax = plt.subplots(ncols=1, sharey=True)
            ax.axvline(linewidth=1, color='black')
            
            df_right.plot(kind='barh', legend=True, ax=ax, width=1.0, stacked=True)
            df_left.plot(kind='barh', legend=True, ax=ax, width=1.0, stacked=True)

            #plt.show()

            #ax = plt.gca()
            #ax.invert_xaxis()

            #plt.gca().invert_yaxis()
            #df = pd.DataFrame(data, columns=columns)
            #df.plot.area()
            #plt.show()

            # Save pdf
            fig_name = "{}_{}".format(scenario, year)
            path_out_file = os.path.join(path_out_folder, "{}.pdf".format(fig_name))
            plt.savefig(path_out_file)
            raise Exception("FF")
    return


def fig_4(data_container):
    """
    """

    return


def fig_5(data_container):
    """
    """

    return


def fig_6(data_container):
    """
    """

    return
