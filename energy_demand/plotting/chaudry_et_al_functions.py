"""Functions to generate figures
"""
import os
import pandas as pd
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt

def export_legend(legend, filename="legend.png"):
    """Export legend as seperate file
    """
    fig = legend.figure
    fig.canvas.draw()
    bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)

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
            'output_eh_tran_e_timestep'
            #'output_elec_load_shed_eh_timestep',
            #'output_tran_wind_power_timestep'

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
                        print("columns: " + str(file_data.columns))
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

            left = 'CENTRAL'
            right = 'DECENTRAL'

            df_right = fig_dict[year][right][scenario]
            df_left = fig_dict[year][left][scenario] * -1 # Convert to minus values
            #df_to_plot.plot.area()
            #df_to_plot.plot.bar(stacked=True)#, orientation='vertical')

            fig, ax = plt.subplots(ncols=1, sharey=True)

            df_right.plot(kind='barh', ax=ax, width=1.0, stacked=True)
            df_left.plot(kind='barh', ax=ax, width=1.0, legend=False, stacked=True)

            # Add vertical line
            ax.axvline(linewidth=1, color='black')

            # Limits
            plt.autoscale(enable=True, axis='x', tight=True)
            plt.autoscale(enable=True, axis='y', tight=True)

            #ax = plt.gca()
            #ax.invert_xaxis()
            #plt.gca().invert_yaxis()
            #df = pd.DataFrame(df_right) #TODO: WHY NO GREEN AREA?
            #df.plot.area()

            # Labels
            plt.xlabel("Unit")
            plt.ylabel("time")
            plt.title(left, fontdict=None, loc='left')
            plt.title(right, fontdict=None, loc='right')

            # Customize axis
            nr_of_bins = 4
            bin_value = int(np.max(df_right.values) / 4)
            right_ticks = np.array([bin_value * i for i in range(nr_of_bins + 1)])
            left_ticks = right_ticks * -1
            left_ticks = left_ticks[::-1]
            right_labels = [str(bin_value * i) for i in range(nr_of_bins + 1)]
            left_labels = right_labels[::-1]
            
            ticks = list(left_ticks) + list(right_ticks)
            labels = list(left_labels) + list(right_labels)

            plt.xticks(
                ticks=ticks,
                labels=labels)

            # Legend
            handles, labels = plt.gca().get_legend_handles_labels()

            by_label = OrderedDict(zip(labels, handles)) # remove duplicates
            legend = plt.legend(
                by_label.values(),
                by_label.keys(),
                ncol=2,
                prop={'size': 10},
                loc='upper center',
                bbox_to_anchor=(0.5, -0.1),
                frameon=False)

            # Save pdf of figure and legend
            fig_name = "{}_{}.pdf".format(scenario, year)
            path_out_file = os.path.join(path_out_folder, fig_name)

            seperate_legend = True
            if seperate_legend:
                export_legend(
                    legend,
                    os.path.join("{}__legend.pdf".format(path_out_file[:-4])))
                legend.remove()

            #plt.show()
            plt.savefig(path_out_file)

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
