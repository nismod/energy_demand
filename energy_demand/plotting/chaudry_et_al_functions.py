"""Functions to generate figures
"""
import os
import math
import pandas as pd
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib import rcParams
from tabulate import tabulate

# Set default font
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']

def cm2inch(*tupl):
    """Convert input cm to inches (width, hight)
    """
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

def write_list_to_txt(path_result, list_out):
    """Write scenario population for a year to txt file
    """
    file = open(path_result, "w")
    for entry in list_out:
        file.write(entry + "\n")
    file.close()

def write_to_txt(path_result, entry):
    """Write scenario population for a year to txt file
    """
    file = open(path_result, "w")
    file.write(entry + "\n")
    file.close()

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

def load_data(in_path, scenarios, simulation_name, unit):
    """Read results

    Returns
    data_container : [scenario][mode][weather_scenario
    """
    data_container = {}
    modes = ['CENTRAL', 'DECENTRAL']

    for scenario in scenarios:
        data_container[scenario] = {}

        for mode in modes:
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

                        if unit == 'GW':
                            df_to_plot_national = df_to_plot_national / 1000.0
                        if unit == 'MW':
                            pass

                        # Set seasonal week attribute as index
                        #df_to_plot_national.set_index('seasonal_week')
                    except:
                        print("{}  has wrong format".format(file_name))
                    '''# Set energy_hub as index
                    try:
                        data_file.set_index('energy_hub')
                    except:
                        print("... file does not have 'energy_hub' as column")'''

                    data_container[scenario][mode][weather_scenario]['energy_supply_constrained'][file_name] = df_to_plot_national

    return data_container


def fig_3_hourly_comparison(
        path_out,
        data_container,
        filenames,
        scenarios,
        weather_scearnio,
        types_to_plot,
        unit,
        years=[2015, 2030, 2050],
        seperate_legend=True
    ):
    """Create x-y chart of a time-span (x-axis: demand, y-axis: time)
    """

    for fueltype in types_to_plot:
        print(".... fueltype: {}".format(fueltype))

        annote_crit = False #Add labels

        # Select hours to plots
        seasonal_week_day = 2
        hours_selected = range(24 * (seasonal_week_day) + 1, 24 * (seasonal_week_day + 1) + 1)

        modes = ['DECENTRAL', 'CENTRAL']
        left = 'CENTRAL'
        right = 'DECENTRAL'

        fontsize_small = 8
        fontsize_large = 10

        # Font info axis labels
        font_additional_info = {
            'color': 'black',
            'weight': 'bold',
            'size': fontsize_large}

        fig_dict = {}
        fig_dict_piecharts = {}
        fig_dict_fuelypes = {}

        path_out_folder = os.path.join(path_out, 'fig3')

        for year in years:
            fig_dict[year] = {}
            fig_dict_piecharts[year] = {}
            fig_dict_fuelypes[year] = {}

            for mode in modes:
                fig_dict[year][mode] = {}
                fig_dict_piecharts[year][mode] = {}
                fig_dict_fuelypes[year][mode] = {}

                for scenario in scenarios:
                    fig_dict[year][mode][scenario] = {}
                    fig_dict_fuelypes[year][mode][scenario] = pd.DataFrame(
                        [[0,0,0,0]], columns=['electricity', 'gas', 'heat', 'hydrogen'])
        
                    colors = []
                    data_files = data_container[scenario][mode][weather_scearnio]['energy_supply_constrained']
                    files_to_plot = filenames[fueltype].keys()

                    # Get all correct data to plot
                    df_to_plot = pd.DataFrame()

                    for file_name, file_data in data_files.items():
                        file_name_split_no_timpestep = file_name[:-9] #remove ending
                        name_column = file_name_split_no_timpestep[7:-9] #remove output_ and ending
                        file_name_split = file_name.split("_")
                        year_simulation = int(file_name_split[-1][:4])

                        if year == year_simulation:
                            data_column = file_data[name_column]
                            if file_name_split_no_timpestep in files_to_plot:
                                df_to_plot[str(name_column)] = data_column
                                color = filenames[fueltype][file_name_split_no_timpestep]
                                colors.append(color)
                            
                            # Get fueltype specific files
                            sum_file = data_column.sum()

                            if (file_name_split_no_timpestep in filenames['elec_hubs'].keys()) or (
                                file_name_split_no_timpestep in filenames['elec_transmission'].keys()):
                                fig_dict_fuelypes[year][mode][scenario]['electricity'] += sum_file
                            elif (file_name_split_no_timpestep in filenames['gas_hubs'].keys()) or (
                                file_name_split_no_timpestep in filenames['gas_transmission'].keys()):
                                fig_dict_fuelypes[year][mode][scenario]['gas'] += sum_file
                            elif file_name_split_no_timpestep in filenames['heat_hubs'].keys():
                                fig_dict_fuelypes[year][mode][scenario]['heat'] += sum_file
                            elif file_name_split_no_timpestep in filenames['hydrogen_hubs'].keys():
                                fig_dict_fuelypes[year][mode][scenario]['hydrogen'] += sum_file


                    # Aggregate across every energy hub region and group by "seasonal week"
                    #df_to_plot_national = df_to_plot.groupby(df_to_plot['seasonal_week']).sum()

                    # Select hours to plots
                    fig_dict[year][mode][scenario] = df_to_plot.loc[hours_selected]

                    # Aggregate annual demand for pie-charts
                    fig_dict_piecharts[year][mode][scenario] = df_to_plot.sum()

            # ----------------------
            # Fueltype chart showing the split between fueltypes
            # ----------------------
            for scenario in scenarios:
                table_out = []
                for mode in [right, left]:

                    fig, ax = plt.subplots(figsize=cm2inch(4.5, 3), ncols=1, sharey=True)

                    data_fueltypes = fig_dict_fuelypes[year][mode][scenario]

                    # Conver to percentages
                    data_fueltypes_p = data_fueltypes / data_fueltypes.sum().sum()
                    data_fueltypes_p = data_fueltypes_p.round(2)

                    headers = data_fueltypes_p.columns
                    
                    table_out.append(data_fueltypes_p.values)

                    data_fueltypes_p.plot(
                        kind='barh',
                        ax=ax,
                        width=1.0,
                        stacked=True,
                        colors=['red', 'blue','grey','green'])

                    # ------------
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

                    ##plt.xticks(
                    #    ticks=list(data_fueltypes_p.values),
                    #    labels=list(data_fueltypes_p.columns),
                    #    fontsize=fontsize_small)

                    # Remove ticks
                    plt.tick_params(axis='x', which='both', left=False) #remove ticks
                    plt.tick_params(axis='y', which='both', left=False) #remove ticks

                    # Save pdf of figure and legend
                    # ------------
                    fig_name = "{}_{}_{}__fueltypes_p.pdf".format(scenario, year, fueltype)
                    path_out_file = os.path.join(path_out_folder, fig_name)

                    if seperate_legend:
                        export_legend(
                            legend,
                            os.path.join("{}__legend.pdf".format(path_out_file[:-4])))
                        legend.remove()

                    # Limits
                    # ------------
                    plt.autoscale(enable=True, axis='x', tight=True)
                    plt.autoscale(enable=True, axis='y', tight=True)
                    #plt.tight()

                    # Remove frame
                    # ------------
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.spines['left'].set_visible(False)

                    plt.show()
                    plt.savefig(path_out_file)

                    # Write out results to txt
                    table_tabulate = tabulate(
                        table_out, headers=headers,
                        numalign="right")
                    write_to_txt(path_out_file[:-4] + ".txt", table_tabulate)

            # ----------------------
            # PLot pie-charts
            # ----------------------
            for scenario in scenarios:
                table_out = []
                for mode in [right, left]:

                    data_pie_chart = fig_dict_piecharts[year][mode][scenario]

                    #  Calculate radius 15 mio corresponds to radius 1 (100%)
                    radius_terawatt = 34 # 100% (radius 1) corresponds to 15 Terawatt
                    initial_radius = 1

                    total_sum = data_pie_chart.sum() / 1000
                    area_change_p = total_sum / radius_terawatt

                    # Convert that radius reflects the change in area (and not size)
                    new_radius = math.sqrt(area_change_p) * initial_radius

                    # write results to txt
                    total_sum = data_pie_chart.sum()
                    for index in data_pie_chart.index:
                        absolute = data_pie_chart.loc[index]
                        relative = (absolute / total_sum)
                        table_out.append([mode, index, absolute, relative])

                    # Explode distance
                    explode_factor = new_radius * 0.1
                    explode_distance = [explode_factor for i in range(len(data_pie_chart.index))]

                    # ---------------------
                    # Plotting pie chart
                    # ---------------------
                    fig, ax = plt.subplots(figsize=cm2inch(4.5, 5))

                    if not annote_crit:
                        plt.pie(
                            data_pie_chart.values,
                            explode=explode_distance,
                            radius=new_radius,
                            wedgeprops=dict(width=new_radius * 0.4))
                    else:
                        # ---------------------
                        # Plot annotations of pie chart
                        # ---------------------
                        min_label_crit = 1 #[%] Minimum label criterium 
                        # Round
                        labels_p = data_pie_chart.values / total_sum
                        labels = labels_p.round(3) * 100 #to percent

                        wedges, texts = plt.pie(
                            data_pie_chart.values,
                            explode=explode_distance,
                            radius=new_radius,
                            wedgeprops=dict(width=0.4),
                            textprops=dict(color="b"))

                        for i, p in enumerate(wedges):
                            ang = (p.theta2 - p.theta1)/2. + p.theta1
                            y = np.sin(np.deg2rad(ang))
                            x = np.cos(np.deg2rad(ang))
                            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
 
                            if labels[i] > min_label_crit: #larger than 1 percent
                                ax.annotate(
                                    labels[i],
                                    xy=(x, y),
                                    xytext=((new_radius + explode_distance[i] + 0.2)*np.sign(x), 1.4*y),
                                    horizontalalignment=horizontalalignment,
                                    color='grey',
                                    size=8,
                                    weight="bold")

                        '''value_crit = 5.0 # [%] Only labes larger than crit are plotted

                        wedges, texts = plt.pie(
                            data_pie_chart.values,
                            explode=explode_distance,
                            radius=new_radius,
                            wedgeprops=dict(width=0.5),
                            startangle=-40)

                        bbox_props = dict(boxstyle="square, pad=0.1", fc="w", ec="k", lw=0)
                        kw = dict(xycoords='data', textcoords='data', arrowprops=dict(arrowstyle="-"),
                                bbox=bbox_props, zorder=0, va="center")

                        # Round
                        labels_p = data_pie_chart.values / total_sum
                        labels = labels_p.round(3)
    
                        for i, p in enumerate(wedges):
                            ang = (p.theta2 - p.theta1)/2. + p.theta1
                            y = np.sin(np.deg2rad(ang))
                            x = np.cos(np.deg2rad(ang))
                            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
                            kw["arrowprops"].update({"connectionstyle": connectionstyle})

                            value = labels[i] * 100 #to percent

                            if value > value_crit: #larger than 1 percent
                                ax.annotate(value, xy=(x, y), xytext=((new_radius + 0.4)*np.sign(x), 1.4*y),
                                            horizontalalignment=horizontalalignment, **kw)
                        '''

                    # Labels
                    plt.xlabel('')
                    plt.ylabel('')

                    # Legend
                    # ------------
                    legend = plt.legend(
                        labels=data_pie_chart.index,
                        ncol=2,
                        prop={'size': 10},
                        loc='upper center',
                        bbox_to_anchor=(0.5, -0.1),
                        frameon=False)

                    # Save pdf of figure and legend
                    # ------------
                    fig_name = "{}_{}_{}__pie.pdf".format(scenario, year, fueltype)
                    path_out_file = os.path.join(path_out_folder, fig_name)

                    if seperate_legend:
                        export_legend(
                            legend,
                            os.path.join("{}__legend.pdf".format(path_out_file[:-4])))
                        legend.remove()

                    # Limits
                    # ------------
                    #plt.autoscale(enable=True, axis='x', tight=True)
                    #plt.autoscale(enable=True, axis='y', tight=True)
                    #plt.tight_layout()

                    # Remove frame
                    # ------------
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.spines['left'].set_visible(False)

                    #plt.show()
                    plt.savefig(path_out_file)

                    # Write out results to txt
                    table_tabulate = tabulate(
                        table_out, headers=['mode', 'type', 'absolute', 'relative'],
                        numalign="right")
                    write_to_txt(path_out_file[:-4] + ".txt", table_tabulate)

            # ----------
            # Plot x-y graph
            # ----------
            for scenario in scenarios:
                table_out = []

                # Data and plot
                # ------------
                df_right = fig_dict[year][right][scenario]
                df_left = fig_dict[year][left][scenario]

                headers = list(df_right.columns)
                headers.insert(0, "hour")
                headers.insert(0, "type")
                for index_hour in df_right.index:
                    row = list(df_right.loc[index_hour])
                    row.insert(0, index_hour)
                    row.insert(0, 'right')
                    table_out.append(row)

                for index_hour in df_left.index:
                    row = list(df_left.loc[index_hour])
                    row.insert(0, index_hour)
                    row.insert(0, 'left')
                    table_out.append(row)

                # Switch axis
                df_left = df_left * -1 # Convert to minus values
                #df_to_plot.plot.area()
                #df_to_plot.plot.bar(stacked=True)#, orientation='vertical')

                table_out.append([])

                fig, ax = plt.subplots(figsize=cm2inch(9, 5), ncols=1, sharey=True)

                df_right.plot(kind='barh', ax=ax, width=1.0, stacked=True, color=colors)
                df_left.plot(kind='barh', ax=ax, width=1.0, legend=False, stacked=True,  color=colors)

                # Add vertical line
                # ------------
                ax.axvline(linewidth=1, color='black')
                
                # Title
                # ------
                #plt.title(left, fontdict=None, loc='left', fontsize=fontsize_small)
                #plt.title(right, fontdict=None, loc='right', fontsize=fontsize_small)

                # Customize x-axis
                nr_of_bins = 4
                bin_value = int(np.max(df_right.values) / nr_of_bins)
                right_ticks = np.array([bin_value * i for i in range(nr_of_bins + 2)])
                left_ticks = right_ticks * -1
                left_ticks = left_ticks[::-1]
                right_labels = [str(bin_value * i) for i in range(nr_of_bins + 2)]
                left_labels = right_labels[::-1]
                ticks = list(left_ticks) + list(right_ticks)
                labels = list(left_labels) + list(right_labels)

                plt.xticks(
                    ticks=ticks,
                    labels=labels,
                    fontsize=fontsize_small)

                # Customize y-axis
                nr_of_bins = 4
                bin_width = int(len(hours_selected) / nr_of_bins)
                min_bin_value = int(np.min(hours_selected))

                ticks = np.array([(bin_width * i) - 0.5 for i in range(nr_of_bins + 1)])
                labels = np.array([str(min_bin_value + bin_width * i) for i in range(nr_of_bins + 1)])

                plt.yticks(
                    ticks=ticks,
                    labels=labels,
                    fontsize=fontsize_small)

                # Legend
                # ------------
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

                # Remove frame
                # ------------
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)

                # Limits
                # ------------
                plt.autoscale(enable=True, axis='x', tight=True)
                plt.autoscale(enable=True, axis='y', tight=True)

                # Add grid lines
                # ------------
                ax.grid(which='major', color='black', axis='y', linestyle='--')
                plt.tick_params(axis='y', which='both', left=False) #remove ticks

                # Save pdf of figure and legend
                # ------------
                fig_name = "{}_{}_{}__xy_plot.pdf".format(scenario, year, fueltype)
                path_out_file = os.path.join(path_out_folder, fig_name)

                if seperate_legend:
                    export_legend(
                        legend,
                        os.path.join("{}__legend.pdf".format(path_out_file[:-4])))
                    legend.remove()

                # Labels
                # ------------
                plt.xlabel("{}".format(unit), fontdict=font_additional_info)
                plt.ylabel("Time seasonal_week_day: {}".format(seasonal_week_day),  fontdict=font_additional_info)

                #plt.show()
                plt.savefig(path_out_file)
                
                # Write out results to txt
                table_tabulate = tabulate(
                    table_out,
                    headers=headers,
                    numalign="right")
                write_to_txt(path_out_file[:-4] + ".txt", table_tabulate)



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
