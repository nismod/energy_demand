"""Plot min and max days from reading in multiple days of different scenario
"""
import csv
import os
from collections import defaultdict
from energy_demand.plotting import plotting_styles
import matplotlib.pyplot as plt

def read_csv_max_min(path_to_csv):
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        
        for row in rows:
            out_dict["Yearday"] = row
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

    for scenario in scenarios:
        if scenario == '__results_multiple_scenarios':
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
                if result_file.split("__")[0] == 'result_day' and result_file.split("__")[1] == 'max':
                    
                    dict_values = read_csv_max_min(os.path.join(result_folder, result_file))

                    year = int(result_file.split("__")[2])

                    data_container[scenario][year]['max'] = dict_values['values_list']
                
                elif result_file.split("__")[0] == 'result_day' and result_file.split("__")[1] == 'min':
                    dict_values = read_csv_max_min(os.path.join(result_folder, result_file))

                    year = int(result_file.split("__")[2])

                    data_container[scenario][year]['min'] = dict_values['values_list']
                else:
                    pass
        
        # ------------
        # Create maximum plot
        # ------------
        colors = plotting_styles.color_list()
        for counter, (scenario, scenario_data) in enumerate(data_container.items()):

            x_data = range(24)

            # Take last simluated year
            plot_yr = list(scenario_data.keys())[-1]

            y_data = scenario_data[plot_yr]['max']
            print(len(x_data))
            print(len(y_data))
            plt.plot(x_data, list(y_data), color=colors[counter], label='{}__{}'.format(scenario, plot_yr))

        #plt.title("Daily profile of day: {} yr: {}".format(day, sim_yr))
        plt.tight_layout()
        plt.margins(x=0)
        plt.show()


# Execute script
generate_min_max_resilience_plot(
    path_to_scenarios="C://Users//cenv0553//ED//results//_resilience_paper_results")
