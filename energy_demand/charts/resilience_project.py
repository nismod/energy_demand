"""All code releated to resilience project

Execute script:
    Plot min and max days from reading in multiple days of different scenario
"""
import os
import csv
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

from energy_demand.basic import date_prop
from energy_demand.basic import basic_functions
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions
from energy_demand.read_write import write_data

def resilience_paper(
        sim_yr,
        path_result_folder,
        new_folder,
        file_name,
        results,
        submodels,
        regions,
        fueltypes,
        fueltype_str
    ):
    """Results for risk paper

    #TODO REMOVE

    results : array
        results_unconstrained (3, 391, 7, 365, 24)
    Get maximum and minimum h electricity for eversy submodel
    for base year
    """
    path_result_sub_folder = os.path.join(
        path_result_folder, new_folder)

    basic_functions.create_folder(path_result_sub_folder)

    # Create file path
    path_to_txt = os.path.join(
        path_result_sub_folder,
        "{}{}".format(file_name,".csv"))

    # Write csv
    file = open(path_to_txt, "w")

    file.write("{}, {}, {}".format(
        'lad_nr',
         #'submodel',
        'min_GW_elec',
        'max_GW_elec') + '\n')
        #'resid_min_GW_elec',
        #'resid_max_GW_elec',
        #'servi_min_GW_elec',
        #'servi_max_GW_elec',
        #'indus_min_GW_elec',
        #'indus_max_GW_elec') + '\n')

    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    for region_nr, region in enumerate(regions):

        min_GW_elec = 0
        max_GW_elec = 0

        for submodel_nr, submodel in enumerate(submodels):

            # Reshape
            reshape_8760h = results[submodel_nr][region_nr][fueltype_int].reshape(8760)

            # Aggregate min and max
            min_GW_elec += np.min(reshape_8760h)
            max_GW_elec += np.max(reshape_8760h)
 
            # Min and max
            '''if submodel_nr == 0:
                resid_min_GW_elec = np.min(reshape_8760h)
                resid_max_GW_elec = np.max(reshape_8760h)
            elif submodel_nr == 1:
                service_min_GW_elec = np.min(reshape_8760h)
                service_max_GW_elec = np.max(reshape_8760h)
            else:
                industry_min_GW_elec = np.min(reshape_8760h)
                industry_max_GW_elec = np.max(reshape_8760h)'''

        # Write to csv file
        file.write("{}, {}, {}".format(
            str.strip(region),
            float(min_GW_elec),
            float(max_GW_elec)) + '\n')

        # Write every hour of min and max day
        '''file.write("{}, {}, {}, {}, {}, {}, {}".format(
            str.strip(region),
            float(resid_min_GW_elec),
            float(resid_max_GW_elec),
            float(service_min_GW_elec),
            float(service_max_GW_elec),
            float(industry_min_GW_elec),
            float(industry_max_GW_elec)
            ) + '\n')'''

    file.close()

    # ---------------------
    # Write out statistics of aggregated national demand
    # ----------------------
    file_path_statistics = os.path.join(
        path_result_sub_folder,
        "{}{}".format(
            'statistics_{}'.format(sim_yr),
            ".csv"))

    file = open(file_path_statistics, "w")

    file.write("{}, {}, {}".format(
        "peak_h_national",
        "trough_h_national",
        "diff") + '\n')

    # Aggregate all submodels
    national_aggregated_submodels = np.sum(results, axis=0)

    # Aggregate over all regions
    sum_all_regs = np.sum(national_aggregated_submodels, axis=0)

    sum_all_regs_fueltype_8760 = sum_all_regs[fueltype_int].reshape(8760)

    # National peak
    peak_h_national = np.max(sum_all_regs_fueltype_8760)

    # National trough
    trough_h_national = np.min(sum_all_regs_fueltype_8760)

    file.write("{}, {}, {}".format(
        peak_h_national,
        trough_h_national,
        peak_h_national - trough_h_national) + '\n')

    print("PEAAK {}  {}".format(peak_h_national, trough_h_national))
    file.close()

    # --------------------
    # Plot min and max day of national aggregated demand
    # --------------------
    max_day = int(basic_functions.round_down((np.argmax(sum_all_regs_fueltype_8760) / 24), 1))
    min_day = int(basic_functions.round_down((np.argmin(sum_all_regs_fueltype_8760) / 24), 1))

    max_day_date = date_prop.yearday_to_date(sim_yr, max_day)
    min_day_date = date_prop.yearday_to_date(sim_yr, min_day)

    max_day_values = list(sum_all_regs_fueltype_8760[max_day * 24:(max_day+1)*24])
    min_day_values = list(sum_all_regs_fueltype_8760[min_day * 24:(min_day+1)*24])

    # ---------------------
    # TODO TO IMPROVE RESILIENCE NEW Plot share of submodel electricity demand per lad
    # ---------------------
    submodels = ['residential_min', 'service', 'industry']
    '''
    #results[submodel_nr][region_nr][fueltype_int].reshape(8760)
    for hour in range(24):
        list_to_write = [
            ['{}, {}, {}, {}, {}, {}\n'.format(
                'residential_min', 'residential_max','service_min', 'service_max', 'industry_min', 'industry_max')]
        
        for region_nr, region in enumerate(regions):
            tot_sector_elec_max = 0
            tot_sector_elec_min = 0
            for submodel_nr, submodel in submodels.items():
                submodel_demand = results[submodel_nr]
                
                # Total electrictiy of all sectors
                tot_sector_elec_max += submodel_demand[region_nr][fueltype_int][max_day][hour]
                tot_sector_elec_min += submodel_demand[region_nr][fueltype_int][min_day][hour]
            
            # Take only electricity
            max_day_elec_fuel_24h = submodel_demand[region_nr][fueltype_int][max_day][hour]
            min_day_elec_fuel_24h = submodel_demand[region_nr][fueltype_int][min_day][hour]

            # Fraction per submodel
            entry = []
            for submodel_nr, submodel in submodels.items():
                submodel_max_p = submodel_demand[region_nr][fueltype_int][max_day][hour] / tot_sector_elec_max
                submodel_min_p = submodel_demand[region_nr][fueltype_int][min_day][hour] / tot_sector_elec_min
                entry.append(submodel_min_p)
                entry.append(submodel_max_p)
           
            entry_str = '{}, {}, {}, {}, {}, {}\n'.format(
                entry[0], entry[1], entry[2], entry[3], entry[4], entry[5])
            list_to_write.append(entry_str)
        
        # Write to file
        path_out_file = os.path.join(
            path_result_sub_folder,
            "{}{}".format(
                'submodel_p__year-{}__hour-{}'.format(sim_yr, hour),
                ".csv"))
        
        file = open(path_out_file, "w")
        for line in list_to_write:
            file.write(line)
        file.close()
    '''

    # ---------------
    # Plot as pdf
    # ---------------
    file_path_max_day = os.path.join(
        path_result_sub_folder,
        "{}{}".format(
            'result_day__max__{}__'.format(sim_yr),
            ".csv"))
    file_path_min_day = os.path.join(
        path_result_sub_folder,
        "{}{}".format(
            'result_day__min__{}__'.format(sim_yr),
            ".csv"))

    # Write out to files
    write_data.write_min_max_result_to_txt(
        file_path=file_path_max_day,
        values=max_day_values,
        yearday=max_day,
        yearday_date=max_day_date)

    write_data.write_min_max_result_to_txt(
        file_path=file_path_min_day,
        values=min_day_values,
        yearday=min_day,
        yearday_date=min_day_date)
    
    # ------------------------------------------------------------
    # Write out for every region for max and min day houryl values
    # ------------------------------------------------------------
    for hour in range(24):

        path_out_file = os.path.join(
            path_result_sub_folder,
            "{}{}".format(
                'regs_hour_GW_{}_{}'.format(sim_yr, hour),
                ".csv"))

        file = open(path_out_file, "w")

        file.write("region, value_max_day, value_min_day\n")

        for region_nr, region in enumerate(regions):

            # Sum over all sumbodels
            reg_total_max_day = 0
            reg_total_min_day = 0
            for submodel_nr, submodel in enumerate(submodels):
                

                daily_values = results[submodel_nr][region_nr][fueltype_int].reshape(365, 24)

                reg_total_max_day += daily_values[max_day]
                reg_total_min_day += daily_values[min_day]

            file.write("{}, {}, {}\n".format(
                region,
                reg_total_max_day[hour],
                reg_total_min_day[hour]))

        file.close()

    # ----------------------
    # Write out national average
    # ----------------------
    path_to_txt_flat = os.path.join(
        path_result_sub_folder,
        "{}{}".format(
            'average_nr',
            ".csv"))

    file = open(path_to_txt_flat, "w")
    file.write("{}".format(
        'average_GW_UK') + '\n')

    uk_av_gw_elec = 0
    for submodel_nr, submodel in enumerate(submodels):
        for region_nr, region in enumerate(regions):
            reshape_8760h = results[submodel_nr][region_nr][fueltype_int].reshape(8760)
            uk_av_gw_elec += np.average(reshape_8760h)

    file.write("{}".format(uk_av_gw_elec))
    file.close()
    print("Finished writing out resilience csv files")
    return

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

def read_csv_average(path_to_csv):
    """read average value from csv
    """
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')

        for row in rows:
            out_dict["name"] = row
            break
        for row in rows:
            out_dict["average_value"] = row[0]
            break

    return out_dict

def generate_min_max_resilience_plot(path_to_scenarios):
    """
    """
    # Iterate result folder


    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)


    # The average scenario needs to be labelled 'av' and must not be at first position
    if scenarios[0] == 'av':
        del scenarios[0]
        scenarios.append('av')

    data_container = {}
    statistics_to_print = [
        "scenario \tmin \tmax \tdiff \tDate maximum day \tDate minimum day \tMax hour \tMin hour",
        "=============================",
        " "]

    for scenario in scenarios:
        if scenario == '__results_resilience':
            pass
        else:
            print("Scenario: " + str(scenario))
            print("-------------------------")
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
                print("result_file name: " + str(result_file.split("__")[0]))
                
                if result_file.split("__")[0] != 'result_day':
                    
                    # Get average value from file
                    if result_file == 'average_nr.csv':
                        average_demands_dict = read_csv_average(os.path.join(result_folder, result_file))
                        average_demands_by = float(average_demands_dict['average_value'])
                    else:
                        pass
                else:
                    if result_file.split("__")[0] == 'result_day' and result_file.split("__")[1] == 'max':
                        dict_values = read_csv_max_min(os.path.join(result_folder, result_file))
                        year = int(result_file.split("__")[2])
                        data_container[scenario][year]['max_values'] = dict_values['values_list']
                        data_container[scenario][year]['max_yearday'] = dict_values['yearday']
                        data_container[scenario][year]['max_date'] = dict_values['date']

                        # Get position in list (hour) of maximum value
                        data_container[scenario][year]['max_h'] = dict_values['values_list'].index(max(dict_values['values_list']))

                    elif result_file.split("__")[0] == 'result_day' and result_file.split("__")[1] == 'min':
                        dict_values = read_csv_max_min(os.path.join(result_folder, result_file))
                        year = int(result_file.split("__")[2])
                        data_container[scenario][year]['min_values'] = dict_values['values_list']
                        data_container[scenario][year]['min_yearday'] = dict_values['yearday']
                        data_container[scenario][year]['min_date'] = dict_values['date']
                        
                        # Get position in list (hour) of min value
                        data_container[scenario][year]['min_h'] = dict_values['values_list'].index(min(dict_values['values_list']))

    # ------------------
    # Calculate statistics
    # --------------------
    for scenario in data_container.keys():
        statistics_to_print.append("{} \t{} \t{} \t{} \t{} \t{} \t{} \t{}".format(
            scenario,
            round(min(data_container[scenario][year]['min_values']), 2),
            round(max(data_container[scenario][year]['max_values']), 2),
            round(max(data_container[scenario][year]['max_values']) - min(data_container[scenario][year]['min_values']), 2),
            data_container[scenario][year]['max_date'],
            data_container[scenario][year]['min_date'],
            data_container[scenario][year]['max_h'],
            data_container[scenario][year]['min_h']))

    # ------------------
    # Print maximum hour value for every peak day of scenario
    # --------------------
    peak_day_values_to_print = []

    cnt = 0
    for scenario in data_container.keys():
        peak_day_values_to_print.append(" ")
        peak_day_values_to_print.append("======================")
        peak_day_values_to_print.append("{}".format(scenario))
        peak_day_values_to_print.append("======================")
        peak_day_values_to_print.append(str(data_container[scenario][year]['max_values']))
        #for hour in range(24):
        #    peak_day_values_to_print.append("hour: {},  value: {}".format(
        #        hour,
        #        data_container[scenario][year]['max_values'][hour]))
        if cnt == 0:
            peak_day_values_to_print.append(" ")
            peak_day_values_to_print.append("======================")
            peak_day_values_to_print.append("current")
            peak_day_values_to_print.append("======================")
            peak_day_values_to_print.append(str(data_container[scenario][2015]['max_values']))
            cnt += 1

    # ------------------
    # Write statiscs to txt
    # --------------------
    basic_functions.create_folder(path_to_scenarios, "__results_resilience")

    write_data.write_list_to_txt(
        os.path.join(path_to_scenarios, "__results_resilience", "statistics.txt"),
        statistics_to_print)

    write_data.write_list_to_txt(
        os.path.join(path_to_scenarios, "__results_resilience", "values_peak_day_scenario.txt"),
        peak_day_values_to_print)

    # ------------------------------------------------
    # Create maximum plot
    #
    # Note: Midnight of the same day is inserted twice
    #       in the first and last hour of a 25 hour day
    #       to visually provide 24 hours of data
    # ------------------------------------------------
    ymax = 60
    line_width = 1.0
    x_data = range(24)

    fig_name = os.path.join(path_to_scenarios, "__results_resilience", "min_max_days.pdf")

    colors = [
        '#d7191c',
        '#2c7bb6',
        '#fdae61',
        '#abd9e9']

    fig = plt.figure(figsize=basic_plot_functions.cm2inch(8, 8)) #width, height

    for counter, (scenario, scenario_data) in enumerate(data_container.items()):

        # Take last simluated year
        plot_yr = list(scenario_data.keys())[-1]

        # Plot base year line
        if counter == 0:

            # Plot current year maximum day plot
            #day_24h = [scenario_data[2015]['max_values'][-1]] + scenario_data[2015]['max_values']
            day_24h = scenario_data[2015]['max_values']

            x_data_smoothed, y_data_smoothed = basic_plot_functions.smooth_data(x_data, day_24h, num=40000)
            plt.plot(
                x_data_smoothed,
                list(y_data_smoothed),
                color='black',
                linestyle='-',
                linewidth=1.5,
                label='{}__{}'.format(scenario, plot_yr))

            # Plot current year minimum day plot 
            #day_24h = [scenario_data[2015]['min_values'][-1]] + scenario_data[2015]['min_values']
            day_24h = scenario_data[2015]['min_values']
            x_data_smoothed, y_data_smoothed = basic_plot_functions.smooth_data(x_data, day_24h, num=40000)

            plt.plot(
                x_data_smoothed,
                list(y_data_smoothed),
                color='black',
                linestyle='-',
                linewidth=1.5,
                label='{}__{}'.format(scenario, plot_yr))

        y_data_max = scenario_data[plot_yr]['max_values']
        y_data_min = scenario_data[plot_yr]['min_values']

        # Maximum day line
        #day_24h = [y_data_max[-1]] + y_data_max
        day_24h = y_data_max
        x_data_smoothed, y_data_smoothed = basic_plot_functions.smooth_data(x_data, day_24h, num=40000)

        plt.plot(
            x_data_smoothed,
            list(y_data_smoothed),
            color=colors[counter],
            linestyle='--',
            linewidth=line_width,
            label='{}__{}'.format(scenario, plot_yr))

        # Minimum day line
        #day_24h = [y_data_min[-1]] + y_data_min
        day_24h = y_data_min
        x_data_smoothed, y_data_smoothed = basic_plot_functions.smooth_data(x_data, day_24h, num=40000)

        plt.plot(
            x_data_smoothed,
            list(y_data_smoothed),
            color=colors[counter],
            linestyle='--',
            linewidth=line_width,
            label='{}__{}'.format(scenario, plot_yr))

    plt.tight_layout()
    plt.ylim(ymin=0, ymax=ymax)
    plt.xlim(xmin=0, xmax=23)

    # 24 hour day ticks
    #plt.xticks([0,6,12,18,24], [0,6,12,18,24])
    #plt.xticks([0,5,11,17,23], [0,6,12,18,24])

    # Position  Label
    #plt.xticks([0,2,5,11,17,19, 23], [1,3,6,12,18,20,24])
    plt.xticks([0,5,11,17,23], [1,6,12,18,24])
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
            'size': 4})

    plt.savefig(fig_name)

    # ------------------------------------------------
    # Create minimum plot
    # ------------------------------------------------
    '''fig_name = os.path.join(path_to_scenarios, "__results_resilience", "min_days.pdf")

    colors = plotting_styles.color_list_resilience()
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(8, 8)) #width, height

    for counter, (scenario, scenario_data) in enumerate(data_container.items()):
        x_data = range(24)

        # Take last simluated year
        plot_yr = list(scenario_data.keys())[-1]
    
        # Plot base year line
        if counter == 0:
            x_data_smoothed, y_data_smoothed = basic_plot_functions.smooth_data(x_data, scenario_data[2015]['min_values'], num=40000)
            plt.plot(
                x_data_smoothed,
                list(y_data_smoothed),
                color='black',
                linestyle='-',
                linewidth=1.5,
                label='{}__{}'.format(scenario, plot_yr))

            # Add flat line
            plt.plot(
                x_data,
                list(flat_y_data),
                color=color_flat_line,
                linestyle='--',
                linewidth=0.5,
                label='{}__{}'.format("flat", 2015))

        y_data = scenario_data[plot_yr]['min_values']

        # smooth line
        x_data_smoothed, y_data_smoothed = basic_plot_functions.smooth_data(x_data, y_data, num=40000)
        plt.plot(
            x_data_smoothed,
            list(y_data_smoothed),
            color=colors[counter],
            linestyle='--',
            linewidth=line_width,
            label='{}__{}'.format(scenario, plot_yr))

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
            'size': 4})

    plt.savefig(fig_name)'''

    print("---------------------------------")
    print("Finished resilience_multiple_lines")
    print("---------------------------------")

# Execute script
#generate_min_max_resilience_plot(
#    path_to_scenarios="C://Users//cenv0553//ED//results//_resilience_paper_results")
