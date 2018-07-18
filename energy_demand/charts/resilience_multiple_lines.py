"""Plot min and max days from reading in multiple days of different scenario
"""
import csv
import os
from collections import defaultdict
from energy_demand.plotting import plotting_styles
import matplotlib.pyplot as plt
from energy_demand.plotting import plotting_results
from energy_demand.plotting import plotting_program
from energy_demand.read_write import write_data
from energy_demand.basic import basic_functions

def read_csv_max_min(path_to_csv):
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        
        for row in rows:
            out_dict["yearday"] = row
            break
        for row in rows:
            out_dict["date"] = row
            break

        values_list = []
        for line_nr, row in enumerate(rows):
            values_list.append(float(row[0]))

        out_dict["values_list"] = values_list

    return out_dict

def generate_min_max_resilience_plot(path_to_scenarios):
    # Iterate result folder


    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    data_container = {}
    statistics_to_print = ["scenario \tmin \tmax \tdiff \tDate maximum day \tDate minimum day", "=============================", " "]

    for scenario in scenarios:
        if scenario == '__results_resilience':
            pass
        else:

            # ----
            # Read in min and max day
            # ----
            path_fist_scenario = os.path.join(path_to_scenarios, scenario)
            
            data_container[scenario] = defaultdict(dict)

            # Folders with Resilience min and max day
            result_folder = os.path.join(path_fist_scenario, "model_run_results_txt", "resilience_paper")

            result_files = os.listdir(result_folder)

            # Get all max day files
            for result_file in result_files:
                if result_file.split("__")[0] != 'result_day':
                    pass
                else:
                    if result_file.split("__")[0] == 'result_day' and result_file.split("__")[1] == 'max':
                        dict_values = read_csv_max_min(os.path.join(result_folder, result_file))
                        year = int(result_file.split("__")[2])
                        data_container[scenario][year]['max_values'] = dict_values['values_list']
                        data_container[scenario][year]['max_yearday'] = dict_values['yearday']
                        data_container[scenario][year]['max_date'] = dict_values['date']

                    elif result_file.split("__")[0] == 'result_day' and result_file.split("__")[1] == 'min':
                        dict_values = read_csv_max_min(os.path.join(result_folder, result_file))
                        year = int(result_file.split("__")[2])
                        data_container[scenario][year]['min_values'] = dict_values['values_list']
                        data_container[scenario][year]['min_yearday'] = dict_values['yearday']
                        data_container[scenario][year]['min_date'] = dict_values['date']
    # ------------------
    # Calculate statistics
    # --------------------
    for scenario in data_container.keys():
        statistics_to_print.append("{} \t{} \t{} \t{} \t{} \t{}".format(
            scenario,
            round(min(data_container[scenario][year]['min_values']), 2),
            round(max(data_container[scenario][year]['max_values']), 2),
            round(max(data_container[scenario][year]['max_values']) - min(data_container[scenario][year]['min_values']), 2),
            data_container[scenario][year]['max_date'],
            data_container[scenario][year]['min_date']))

    # ------------------
    # Write statiscs to txt
    # --------------------
    basic_functions.create_folder(path_to_scenarios, "__results_resilience")

    write_data.write_list_to_txt(
        os.path.join(path_to_scenarios, "__results_resilience", "statistics.txt"),
        statistics_to_print)

    # ------------------------------------------------
    # Create maximum plot
    # ------------------------------------------------
    ymax = 60

    fig_name = os.path.join(path_to_scenarios, "__results_resilience", "max_days.pdf")

    colors = plotting_styles.color_list_resilience()
    fig = plt.figure(
        figsize=plotting_program.cm2inch(8, 8)) #width, height

    for counter, (scenario, scenario_data) in enumerate(data_container.items()):
        x_data = range(24)

        # Take last simluated year
        plot_yr = list(scenario_data.keys())[-1]
        y_data = scenario_data[plot_yr]['max_values']

        # smooth line
        x_data_smoothed, y_data_smoothed = plotting_results.smooth_data(x_data, y_data, num=40000)
        plt.plot(x_data_smoothed, list(y_data_smoothed), color=colors[counter], label='{}__{}'.format(scenario, plot_yr))

        # Plot base year line
        if counter == 1:
            x_data_smoothed, y_data_smoothed = plotting_results.smooth_data(x_data, scenario_data[2015]['max_values'], num=40000)
            plt.plot(x_data_smoothed, list(y_data_smoothed), color='black', label='{}__{}'.format(scenario, plot_yr))

    plt.tight_layout()
    plt.ylim(ymin=0, ymax=ymax)
    plt.xlim(xmin=0, xmax=23)

    # Legend #https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        fancybox=False,
        shadow=False,
        ncol=2,
        prop={
            'family': 'arial',
            'size': 6})

    plt.savefig(fig_name)

    # ------------------------------------------------
    # Create minimum plot
    # ------------------------------------------------
    fig_name = os.path.join(path_to_scenarios, "__results_resilience", "min_days.pdf")

    colors = plotting_styles.color_list_resilience()
    fig = plt.figure(
        figsize=plotting_program.cm2inch(8, 8)) #width, height

    for counter, (scenario, scenario_data) in enumerate(data_container.items()):
        x_data = range(24)

        # Take last simluated year
        plot_yr = list(scenario_data.keys())[-1]
        y_data = scenario_data[plot_yr]['min_values']

        # smooth line
        x_data_smoothed, y_data_smoothed = plotting_results.smooth_data(x_data, y_data, num=40000)
        plt.plot(x_data_smoothed, list(y_data_smoothed), color=colors[counter], label='{}__{}'.format(scenario, plot_yr))

        # Plot base year line
        if counter == 1:
            x_data_smoothed, y_data_smoothed = plotting_results.smooth_data(x_data, scenario_data[2015]['min_values'], num=40000)
            plt.plot(x_data_smoothed, list(y_data_smoothed), color='black', label='{}__{}'.format(scenario, plot_yr))

    plt.tight_layout()
    plt.ylim(ymin=0, ymax=ymax)
    plt.xlim(xmin=0, xmax=23)

    # Legend #https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        fancybox=False,
        shadow=False,
        ncol=2,
        prop={
            'family': 'arial',
            'size': 6})

    plt.savefig(fig_name)

    print("---------------------------------")
    print("Finished resilience_multiple_lines")
    print("---------------------------------")

# Execute script
generate_min_max_resilience_plot(
    path_to_scenarios="C://Users//cenv0553//ED//results//_resilience_paper_results")
