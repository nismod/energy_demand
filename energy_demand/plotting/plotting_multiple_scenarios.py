"""
This file containes functions to plot multiple scenarios in a folder
"""
import math
import os
import operator
import collections
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.plotting import plotting_styles
from energy_demand.plotting import basic_plot_functions
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_results
from energy_demand import enduse_func
from energy_demand.profiles import load_factors
from energy_demand.read_write import write_data
#matplotlib.use('Agg') # Used to make it work in linux

def plot_heat_pump_chart_multiple(
        lookups,
        regions,
        hp_scenario_data,
        fig_name,
        txt_name,
        fueltype_str_input,
        plotshow=False):
    """
    Compare share of element on x axis (provided in name of scenario)
    with load factor

    Info
    -----
    Run scenarios with different value in scenarion name

    e.g. 0.1 heat pump --> scen_0.1
    """
    # Year for which the whole is is generated
    year_to_plot = 2050

    # Collect value to display on axis
    result_dict = {} # {scenario_value:  {year: {fueltype: np.array(reg, value))}}
    results_txt = []

    for scenario_hp, scen_data in hp_scenario_data.items():
        result_dict[scenario_hp] = {}
        for scenario_name, scenario_data in scen_data.items():
            print("Scenario to process: " + str(scenario_name))

            # Scenario value
            value_scenario = int(scenario_name.split("__")[1])

            # Get peak for all regions {year: {fueltype: np.array(reg,value))}
            y_lf_fueltype = {}

            # Load factor
            '''for year, data_lf_fueltypes in scenario_data['reg_load_factor_y'].items(): # {scenario_value: np.array((regions, result_value))}
                if year != year_to_plot:
                    continue

                y_lf_fueltype[year] = {}
                for fueltype_int, data_lf in enumerate(data_lf_fueltypes):
                    fueltype_str = tech_related.get_fueltype_str(lookups['fueltypes'], fueltype_int)

                    # Select only fueltype data
                    if fueltype_str == fueltype_str_input:
                        y_lf_fueltype[year] = data_lf
                    else:
                        pass
            '''
            # PEAK VALUE ed_peak_regs_h ed_peak_h
            #for year, data_lf_fueltypes in scenario_data['ed_peak_regs_h'].items():
            for year, year_data in scenario_data['ed_peak_h'].items():
                if year != year_to_plot:
                    pass
                else:
                    y_lf_fueltype[year] = {}
                    for fueltype_str, peak_h in year_data.items():

                        # Select only fueltype data
                        if fueltype_str == fueltype_str_input:
                            y_lf_fueltype[year] = peak_h

                            txt = "fueltype_str: {}  peak_h: {} scenario_name: {} ".format(
                                fueltype_str,
                                peak_h,
                                scenario_name)

                            results_txt.append(txt)

                        else:
                            pass

            result_dict[scenario_hp][value_scenario] = y_lf_fueltype

        # Sort dict and convert to OrderedDict
        result_dict[scenario_hp] = collections.OrderedDict(sorted(result_dict[scenario_hp].items()))

    # --------------------------
    # Save model results to txt
    # --------------------------
    write_data.write_list_to_txt(
        txt_name,
        results_txt)

    #-----
    # Plot
    # -----
    plot_max_min_polygon = False
    plot_all_regs = False

    # Set figure size
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(9, 8))
    ax = fig.add_subplot(1, 1, 1)

    # -----------------
    # Axis
    # -----------------
    first_scenario = list(result_dict.keys())[0]

    # Percentages on x axis
    major_ticks = list(result_dict[first_scenario].keys())

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list_selection = plotting_styles.get_colorbrewer_color(
        color_prop='sequential', #sequential
        color_palette='PuBu_4',
        inverse=False) # #https://jiffyclub.github.io/palettable/colorbrewer/sequential/

    # all percent values
    all_percent_values = list(result_dict[first_scenario].keys())

    # Nr of years
    for _percent_value, fuel_fueltype_yrs in result_dict[first_scenario].items():
        years = list(fuel_fueltype_yrs.keys())
        break

    for year in years:

        # ----------------
        # For every region
        # ----------------
        '''for reg_nr, _ in enumerate(regions):
            year_data = []
            for _percent_value, fuel_fueltype_yrs in result_dict.items():
                year_data.append(fuel_fueltype_yrs[year][reg_nr])

            # Paste out if not individual regions and set plot_max_min_polygon to True
            if plot_all_regs:
                plt.plot(
                    list(all_percent_values),
                    list(year_data),
                    color=str(color_scenario))'''

        # --------------------
        # Plot max min polygon
        # --------------------
        '''if plot_max_min_polygon:

            # Create value {x_vals: [y_vals]}
            x_y_values = {}
            for _percent_value, fuel_fueltype_yrs in result_dict.items():
                x_y_values[_percent_value] = []
                for reg_nr, _ in enumerate(regions):
                    x_y_values[_percent_value].append(result_dict[_percent_value][year])

            # Create polygons
            min_max_polygon = plotting_results.create_min_max_polygon_from_lines(x_y_values)

            polygon = plt.Polygon(
                min_max_polygon,
                color=color_scenario,
                alpha=0.2,
                edgecolor=None,
                linewidth=0,
                fill='True')

            ax.add_patch(polygon)'''
        color_scenarios = plotting_styles.color_list_scenarios()

        cnt = -1
        for scenario_hp, scenario_hp_result in result_dict.items():
            print("Scneario: " + str(scenario_hp))
            cnt += 1
            # Average across all regs
            year_data = []
            for _percent_value, fuel_fueltype_yrs in scenario_hp_result.items():

                regs = fuel_fueltype_yrs[year]

                # --------------------------------------
                # Average load factor across all regions
                # --------------------------------------
                lf_peak_across_all_regs = np.average(regs)
                year_data.append(lf_peak_across_all_regs)

            plt.plot(
                list(all_percent_values),
                list(year_data),
                label=scenario_hp,
                color=color_scenarios[cnt])
    

    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)
    plt.ylim(ymax=80)

    plt.xlim(xmin=0)
    plt.xlim(xmax=100)

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        #legend_entries,
        ncol=1,
        loc=3,
        prop={
            'family': 'arial',
            'size': 5},
        frameon=False)

    # ---------
    # Labels
    # ---------
    plt.xlabel("heat pump residential heating [%]")
    #plt.ylabel("load factor [%] [{}]".format(fueltype_str_input))
    plt.ylabel("Peak demand h [GW] {}".format(fueltype_str_input))
    #plt.title("impact of changing residential heat pumps to load factor")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    plt.close()

def plot_heat_pump_chart(
        lookups,
        regions,
        scenario_data,
        fig_name,
        fueltype_str_input,
        plotshow=False):
    """
    Compare share of element on x axis (provided in name of scenario)
    with load factor


    Info
    -----
    Run scenarios with different value in scenarion name

    e.g. 0.1 heat pump --> scen_0.1
    """
    year_to_plot = 2050

    # Collect value to display on axis
    result_dict = {} # {scenario_value:  {year: {fueltype: np.array(reg, value))}}

    for scenario_name, scenario_data in scenario_data.items():
        print("Scenario to process: " + str(scenario_name))
        # Scenario value
        value_scenario = float(scenario_name.split("__")[1])

        # Get peak for all regions {year: {fueltype: np.array(reg,value))}
        y_lf_fueltype = {}

        # Load factor
        '''for year, data_lf_fueltypes in scenario_data['reg_load_factor_y'].items(): # {scenario_value: np.array((regions, result_value))}
            if year != year_to_plot:
                continue

            y_lf_fueltype[year] = {}
            for fueltype_int, data_lf in enumerate(data_lf_fueltypes):
                fueltype_str = tech_related.get_fueltype_str(lookups['fueltypes'], fueltype_int)

                # Select only fueltype data
                if fueltype_str == fueltype_str_input:
                    y_lf_fueltype[year] = data_lf
                else:
                    pass
        '''
        # PEAK VALUE ed_peak_regs_h ed_peak_h
        #for year, data_lf_fueltypes in scenario_data['ed_peak_regs_h'].items():
        for year, data_lf_fueltypes in scenario_data['ed_peak_h'].items():
            if year != year_to_plot:
                continue

            y_lf_fueltype[year] = {}
            for fueltype_str, data_lf in data_lf_fueltypes.items():

                # Select only fueltype data
                if fueltype_str == fueltype_str_input:
                    y_lf_fueltype[year] = data_lf
                else:
                    pass

        result_dict[value_scenario] = y_lf_fueltype

    # Sort dict and convert to OrderedDict
    result_dict = collections.OrderedDict(sorted(result_dict.items()))

    #-----
    # Plot
    # -----

    # Criteria to plot maximum boundaries
    plot_max_min_polygon = False
    plot_all_regs = False

    # Set figure size
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(16, 8))
    ax = fig.add_subplot(1, 1, 1)

    # -----------------
    # Axis
    # -----------------
    # Percentages on x axis
    major_ticks = list(result_dict.keys())

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list_selection = plotting_styles.get_colorbrewer_color(
        color_prop='sequential', #sequential
        color_palette='PuBu_4',
        inverse=False) # #https://jiffyclub.github.io/palettable/colorbrewer/sequential/

    # all percent values
    all_percent_values = list(result_dict.keys())

    # Nr of years
    for _percent_value, fuel_fueltype_yrs in result_dict.items():
        years = list(fuel_fueltype_yrs.keys())
        break

    legend_entries = []
    for year in years:
        color_scenario = color_list_selection.pop()

        legend_entries.append("mean {}".format(year))

        # ----------------
        # For every region
        # ----------------
        '''for reg_nr, _ in enumerate(regions):
            year_data = []
            for _percent_value, fuel_fueltype_yrs in result_dict.items():
                year_data.append(fuel_fueltype_yrs[year][reg_nr])

            # Paste out if not individual regions and set plot_max_min_polygon to True
            if plot_all_regs:
                plt.plot(
                    list(all_percent_values),
                    list(year_data),
                    color=str(color_scenario))'''

        # --------------------
        # Plot max min polygon
        # --------------------
        if plot_max_min_polygon:

            # Create value {x_vals: [y_vals]}
            x_y_values = {}
            for _percent_value, fuel_fueltype_yrs in result_dict.items():
                x_y_values[_percent_value] = []
                for reg_nr, _ in enumerate(regions):
                    x_y_values[_percent_value].append(result_dict[_percent_value][year])

            # Create polygons
            min_max_polygon = plotting_results.create_min_max_polygon_from_lines(x_y_values)

            polygon = plt.Polygon(
                min_max_polygon,
                color=color_scenario,
                alpha=0.2,
                edgecolor=None,
                linewidth=0,
                fill='True')

            ax.add_patch(polygon)

        # Average across all regs
        year_data = []
        for _percent_value, fuel_fueltype_yrs in result_dict.items():

            regs = fuel_fueltype_yrs[year]

            # --------------------------------------
            # Average load factor across all regions
            # --------------------------------------
            lf_peak_across_all_regs = np.average(regs)
            year_data.append(lf_peak_across_all_regs)

        plt.plot(
            list(all_percent_values),
            list(year_data),
            color=str(color_scenario))
    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)
    plt.ylim(ymax=80)
    #plt.ylim(ymax=1.2)
    plt.xlim(xmin=0, xmax=60)

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        legend_entries,
        ncol=1,
        loc=3,
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)

    # ---------
    # Labels
    # ---------
    plt.xlabel("heat pump residential heating [%]")
    #plt.ylabel("load factor [%] [{}]".format(fueltype_str_input))
    plt.ylabel("Peak demand h [GW] {}".format(fueltype_str_input))
    #plt.title("impact of changing residential heat pumps to load factor")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plot_tot_y_peak_hour(
        scenario_data,
        fig_name,
        fueltype_str_input,
        plotshow=False
    ):
    """Plot fueltype specific peak h of all regions
    """
    plt.figure(figsize=basic_plot_functions.cm2inch(14, 8))

    # -----------------
    # Axis
    # -----------------
    base_yr, year_interval = 2015, 5
    first_scen = list(scenario_data.keys())[0]
    end_yr = list(scenario_data[first_scen]['ed_peak_h'].keys())[-1]

    major_ticks = np.arange(
        base_yr,
        end_yr + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list_selection = plotting_styles.color_list_selection()

    for scenario_name, fuel_fueltype_yrs in scenario_data.items():

        data_container = []
        for year, fuel_fueltypes in fuel_fueltype_yrs['ed_peak_h'].items():
            data_container.append(fuel_fueltypes[fueltype_str_input])

        # Calculate max peak in end year
        peak_gw = round(data_container[-1], 1)
        peak_p = round((100 / data_container[0]) * data_container[-1], 1)

        # Label
        label_scenario = "{} (peak: GW {} p: {})".format(
            scenario_name,
            peak_gw,
            peak_p)

        plt.plot(
            list(fuel_fueltype_yrs['ed_peak_h'].keys()),     # years
            list(data_container),               # yearly data
            color=str(color_list_selection.pop()),
            label=label_scenario) #scenario_name)

    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        ncol=1,
        loc=3,
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)

    # ---------
    # Labels
    # ---------
    plt.ylabel("GWh")
    plt.xlabel("year")
    plt.title("peak_h {} [GW]".format(fueltype_str_input))

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plot_reg_y_over_time(
        scenario_data,
        fig_name,
        plotshow=False
    ):
    """Plot total demand over simulation period for every
    scenario for all regions
    """
    # Set figure size
    plt.figure(figsize=basic_plot_functions.cm2inch(14, 8))

    y_scenario = {}

    for scenario_name, scen_data in scenario_data.items():

        data_years_regs = {}
        for year, fueltype_reg_time in scen_data['results_every_year'].items():
            data_years_regs[year] = {}

            for _fueltype, regions_fuel in enumerate(fueltype_reg_time):
                for region_nr, region_fuel in enumerate(regions_fuel):

                    # Sum all regions and fueltypes
                    reg_gwh_fueltype_y = np.sum(region_fuel)

                    try:
                        data_years_regs[year][region_nr] += reg_gwh_fueltype_y
                    except:
                        data_years_regs[year][region_nr] = reg_gwh_fueltype_y

        y_scenario[scenario_name] = data_years_regs

    # -----------------
    # Axis
    # -----------------
    base_yr, year_interval = 2015, 5
    first_scen = list(y_scenario.keys())[0]
    end_yr = list(y_scenario[first_scen].keys())[-1]

    major_ticks = np.arange(
        base_yr,
        end_yr + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list_selection = plotting_styles.color_list_scenarios()
    cnt = -1
    for scenario_name, fuel_fueltype_yrs in y_scenario.items():

        cnt += 1

        color_scenario = color_list_selection[cnt]

        for year, regs in fuel_fueltype_yrs.items():
            nr_of_reg = len(regs.keys())
            break

        for reg_nr in range(nr_of_reg):
            reg_data = []
            for year, regions_fuel in fuel_fueltype_yrs.items():
                reg_data.append(regions_fuel[reg_nr])

            plt.plot(
                list(fuel_fueltype_yrs.keys()),
                list(reg_data),
                label="{}".format(scenario_name),
                color=str(color_scenario))
    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)

    # ------------
    # Plot legend
    # ------------
    '''plt.legend(
        ncol=2,
        loc=3,
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)'''

    # ---------
    # Labels
    # ---------
    font_additional_info = plotting_styles.font_info(size=5)

    plt.ylabel("GWh")
    plt.xlabel("year")
    plt.title(
        "tot_y",
        fontdict=font_additional_info)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plot_tot_fueltype_y_over_time(
        scenario_data,
        fueltypes,
        fueltypes_to_plot,
        fig_name,
        txt_name,
        plotshow=False
    ):
    """Plot total demand over simulation period for every
    scenario for all regions
    """
    results_txt = []

    # Set figure size
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8))

    ax = fig.add_subplot(1, 1, 1)

    y_scenario = {}

    for scenario_name, scen_data in scenario_data.items():

        # Read out fueltype specific max h load
        data_years = {}
        for year, fueltype_reg_time in scen_data['results_every_year'].items():

            # Sum all regions
            tot_gwh_fueltype_yh = np.sum(fueltype_reg_time, axis=1)

            # Sum all hours
            tot_gwh_fueltype_y = np.sum(tot_gwh_fueltype_yh, axis=1)

            # Convert to TWh
            tot_gwh_fueltype_y = conversions.gwh_to_twh(tot_gwh_fueltype_y)

            data_years[year] = tot_gwh_fueltype_y

        y_scenario[scenario_name] = data_years

    # -----------------
    # Axis
    # -----------------
    base_yr, year_interval = 2020, 10
    first_scen = list(y_scenario.keys())[0]
    end_yr = list(y_scenario[first_scen].keys())

    major_ticks = np.arange(
        base_yr,
        end_yr[-1] + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    #color_list_selection_fueltypes = plotting_styles.color_list_selection()
    color_list_selection = plotting_styles.color_list_scenarios()
    linestyles = ['--', '-', ':', "-.", ".-"] #linestyles = plotting_styles.linestyles()

    cnt_scenario = -1
    for scenario_name, fuel_fueltype_yrs in y_scenario.items():
        cnt_scenario += 1
        color = color_list_selection[cnt_scenario]
        cnt_linestyle = -1

        for fueltype_str, fueltype_nr in fueltypes.items():

            if fueltype_str in fueltypes_to_plot:
                cnt_linestyle += 1
                # Get fuel per fueltpye for every year
                fuel_fueltype = []
                for entry in list(fuel_fueltype_yrs.values()):
                    fuel_fueltype.append(entry[fueltype_nr])

                plt.plot(
                    list(fuel_fueltype_yrs.keys()),      # years
                    fuel_fueltype,                       # yearly data per fueltype
                    color=color,
                    linestyle=linestyles[cnt_linestyle],
                    label="{}_{}".format(scenario_name, fueltype_str))

                # ---
                # Calculate difference in demand from 2015 - 2050
                # ---
                tot_2015 = fuel_fueltype[0]
                tot_2050 = fuel_fueltype[-1]
                diff_abs = tot_2050 - tot_2015
                p_diff_2015_2015 = ((100 / tot_2015) * tot_2050) - 100 # Diff
                
                txt = "fueltype_str: {} ed_tot_by: {} ed_tot_cy: {}, diff_p: {}, diff_abs: {} scenario: {}".format(
                    fueltype_str,
                    round(tot_2015, 1),
                    round(tot_2050, 1),
                    round(p_diff_2015_2015, 1),
                    round(diff_abs, 1),
                    scenario_name)

                results_txt.append(txt)

    # --------------------------
    # Save model results to txt
    # --------------------------
    write_data.write_list_to_txt(
        txt_name,
        results_txt)

    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)

    # ------------
    # Plot legend
    # ------------
    ax.legend(
        ncol=2,
        frameon=False,
        loc='upper center',
        prop={
            'family': 'arial',
            'size': 4},
        bbox_to_anchor=(0.5, -0.1))

    # ---------
    # Labels
    # ---------
    font_additional_info = plotting_styles.font_info(size=5)

    plt.ylabel("TWh")
    plt.xlabel("year")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()

    plt.close()

def plot_tot_y_over_time(
        scenario_data,
        fig_name,
        plotshow=False
    ):
    """Plot total demand over simulation period for every
    scenario for all regions
    """
    # Set figure size
    plt.figure(figsize=basic_plot_functions.cm2inch(14, 8))

    y_scenario = {}

    for scenario_name, scen_data in scenario_data.items():

        # Read out fueltype specific max h load
        data_years = {}
        for year, fueltype_reg_time in scen_data['results_every_year'].items():

            # Sum all regions and fueltypes
            tot_gwh_fueltype_y = np.sum(fueltype_reg_time)

            # Convert to TWh
            tot_twh_fueltype_y = conversions.gwh_to_twh(tot_gwh_fueltype_y)

            data_years[year] = tot_twh_fueltype_y

        y_scenario[scenario_name] = data_years

    # -----------------
    # Axis
    # -----------------
    base_yr, year_interval = 2015, 5
    first_scen = list(y_scenario.keys())[0]
    end_yr = list(y_scenario[first_scen].keys())

    major_ticks = np.arange(
        base_yr,
        end_yr[-1] + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
   # color_list_selection = plotting_styles.color_list_selection()
    color_list_selection = plotting_styles.color_list_scenarios()

    for scenario_name, fuel_fueltype_yrs in y_scenario.items():

        plt.plot(
            list(fuel_fueltype_yrs.keys()),     # years
            list(fuel_fueltype_yrs.values()),   # yearly data per fueltype
            color=str(color_list_selection.pop()),
            label=scenario_name)

    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        ncol=1,
        loc=3,
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)

    # ---------
    # Labels
    # ---------
    plt.ylabel("TWh")
    plt.xlabel("year")
    plt.title("tot y ED all fueltypes")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()

    plt.close()

def plot_radar_plots_average_peak_day(
        scenario_data,
        fueltype_to_model,
        fueltypes,
        year_to_plot,
        fig_name,
        base_yr=2015
    ):
    """Compare averaged dh profile overall regions for peak day
    for future year and base year

    MAYBE: SO FAR ONLY FOR ONE SCENARIO
    """
    name_spider_plot = os.path.join(
        fig_name, "spider_scenarios_{}.pdf".format(fueltype_to_model))

    fueltype_int = fueltypes[fueltype_to_model]

    # ----------------
    # Create base year peak load profile
    # Aggregate load profiles of all regions
    # -----------------
    individ_radars_to_plot_dh = []
    load_factor_fueltype_y_cy = []
    results_txt = []

    for scenario_cnt, scenario in enumerate(scenario_data):

        print("-------Scenario: {} {}".format(scenario, fueltype_to_model))

        # ------------------------
        # Future year load profile
        # ------------------------
        all_regs_fueltypes_yh_by = np.sum(scenario_data[scenario]['results_every_year'][base_yr], axis=1)
        all_regs_fueltypes_yh_cy = np.sum(scenario_data[scenario]['results_every_year'][year_to_plot], axis=1)

        # ---------------------------
        # Calculate load factors
        # ---------------------------
        peak_day_nr_by, by_max_h = enduse_func.get_peak_day_single_fueltype(
            all_regs_fueltypes_yh_by[fueltype_int])
        peak_day_nr_cy, cy_max_h = enduse_func.get_peak_day_single_fueltype(
            all_regs_fueltypes_yh_cy[fueltype_int])

        scen_load_factor_fueltype_y_by = load_factors.calc_lf_y(all_regs_fueltypes_yh_by)
        load_factor_fueltype_y_by = round(scen_load_factor_fueltype_y_by[fueltype_int], fueltype_int)

        scen_load_factor_fueltype_y_cy = load_factors.calc_lf_y(all_regs_fueltypes_yh_cy)
        load_factor_fueltype_y_cy.append(round(scen_load_factor_fueltype_y_cy[fueltype_int], fueltype_int))

        # ------------------------
        # Restult calculations
        # ------------------------
        # Calculate share or space and water heating of total electrictiy demand in 2050
        enduses_to_agg = [
            'rs_space_heating',
            'rs_water_heating',
            'ss_space_heating',
            'ss_water_heating',
            'is_space_heating']

        aggregated_enduse_fueltype_cy = np.zeros((365, 24))
        aggregated_enduse_fueltype_by = np.zeros((365, 24))

        for enduse in scenario_data[scenario]['results_enduse_every_year'][year_to_plot].keys():
            if enduse in enduses_to_agg:
                aggregated_enduse_fueltype_by += scenario_data[scenario]['results_enduse_every_year'][2015][enduse][fueltype_int]
                aggregated_enduse_fueltype_cy += scenario_data[scenario]['results_enduse_every_year'][year_to_plot][enduse][fueltype_int]

        # Total demand of selected enduses
        selected_enduses_peak_by = round(np.max(aggregated_enduse_fueltype_by), 1)
        selected_enduses_peak_cy = round(np.max(aggregated_enduse_fueltype_cy[peak_day_nr_cy]), 1)

        # Calculate change in peak
        all_regs_fueltypes_yh_by = all_regs_fueltypes_yh_by.reshape(all_regs_fueltypes_yh_by.shape[0], 365, 24)
        all_regs_fueltypes_yh_cy = all_regs_fueltypes_yh_cy.reshape(all_regs_fueltypes_yh_cy.shape[0], 365, 24)

        diff_max_h = round(((100 / by_max_h) * cy_max_h) - 100, 1)

        txt = "peak_h_by: {} peak_h_cy: {} diff_p: {}, peak_h_selected_enduses_by: {} peak_h_selected_enduses_cy: {} scenario: {}".format(
            round(by_max_h, 1),
            round(cy_max_h, 1),
            round(diff_max_h, 1),
            selected_enduses_peak_by,
            selected_enduses_peak_cy,
            scenario)

        results_txt.append(txt)

        print("Calculation of diff in peak: {} {} {} {}".format(
            scenario, round(diff_max_h, 1), round(by_max_h, 1), round(cy_max_h, 1)))

        # ----------------------------------
        # Plot dh for peak day for base year
        # ----------------------------------
        if scenario_cnt == 0:
            individ_radars_to_plot_dh.append(list(all_regs_fueltypes_yh_by[fueltype_int][peak_day_nr_by]))
        else:
            pass

        # Add current year
        individ_radars_to_plot_dh.append(list(all_regs_fueltypes_yh_cy[fueltype_int][peak_day_nr_cy]))

    # --------------------------
    # Save model results to txt
    # --------------------------
    write_data.write_list_to_txt(
        os.path.join(fig_name, name_spider_plot[:-3] + "txt"),
        results_txt)

    # --------------------------
    # Plot figure
    # --------------------------
    plot_radar_plot_multiple_lines(
        individ_radars_to_plot_dh,
        name_spider_plot,
        plot_steps=50,
        scenario_names=list(scenario_data.keys()),
        plotshow=False,
        lf_y_by=[],
        lf_y_cy=[],
        list_diff_max_h=results_txt)

def plot_LAD_comparison_scenarios(
        scenario_data,
        year_to_plot,
        fig_name,
        plotshow=True
    ):
    """Plot chart comparing total annual demand for all LADs

    Arguments
    ---------
    scenario_data : dict
        Scenario name, scenario data
    year_to_plot : int
        Year to plot different LAD values
    fig_name : str
        Path to out pdf figure
    plotshow : bool
        Plot figure or not

    Info
    -----
    if scenario name starts with _ the legend does not work
    """

    # Get first scenario in dict
    all_scenarios = list(scenario_data.keys())
    first_scenario = str(all_scenarios[:1][0])

    # ----------------
    # Sort regions according to size
    # -----------------
    regions = {}
    for fueltype, fuels_regs in enumerate(scenario_data[first_scenario]['results_every_year'][2015]):

        for region_array_nr, fuel_reg in enumerate(fuels_regs):
            try:
                regions[region_array_nr] += np.sum(fuel_reg)
            except KeyError:
                regions[region_array_nr] = np.sum(fuel_reg)

    sorted_regions = sorted(
        regions.items(),
        key=operator.itemgetter(1))

    sorted_regions_nrs = []
    for sort_info in sorted_regions:
        sorted_regions_nrs.append(sort_info[0])

    # Labels
    labels = []
    for sorted_region in sorted_regions_nrs:
        geocode_lad = sorted_region # If actual LAD name, change this
        labels.append(geocode_lad)

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8))

    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_regions_nrs), 1)

    # ----------------------------------------------
    # Plot base year values
    # ----------------------------------------------
    base_year_data = []
    for reg_array_nr in sorted_regions_nrs:
        base_year_data.append(regions[reg_array_nr])
    total_base_year_sum = sum(base_year_data)

    plt.plot(
        x_values,
        base_year_data,
        linestyle='None',
        marker='o',
        markersize=1.6,
        fillstyle='full',
        markerfacecolor='grey',
        markeredgewidth=0.4,
        color='black',
        label='actual_by ({})'.format(total_base_year_sum))

    # ----------------------------------------------
    # Plot all future scenario values
    # ----------------------------------------------
    color_list = plotting_styles.color_list()

    for scenario_nr, (scenario_name, fuel_data) in enumerate(scenario_data.items()):

        sorted_year_data = []
        for reg_array_nr in sorted_regions_nrs:
            tot_fuel_across_fueltypes = 0
            for fueltype, fuel_regs in enumerate(fuel_data['results_every_year'][year_to_plot]):
                tot_fuel_across_fueltypes += np.sum(fuel_regs[reg_array_nr])

            sorted_year_data.append(tot_fuel_across_fueltypes)

        tot_fuel_all_reg = np.sum(fuel_data['results_every_year'][year_to_plot])
        print("TOTAL FUEL in GWH " + str(tot_fuel_all_reg))

        # Calculate total annual demand
        tot_demand = sum(sorted_year_data)
        scenario_name = "{} (tot: {} [GWh])".format(
            scenario_name, round(tot_demand, 2))

        plt.plot(
            x_values,
            sorted_year_data,
            linestyle='None',
            marker='o',
            markersize=1.6,
            fillstyle='full',
            markerfacecolor=color_list[scenario_nr],
            markeredgewidth=0.4,
            color=color_list[scenario_nr],
            label=scenario_name)

    # --------
    # Axis
    # --------
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off

    # Limit
    plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    label_points = False
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                sorted_year_data[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=3)

    plt.title(
        "TEST",
        loc='left',
        fontdict=plotting_styles.font_info())

    plt.xlabel("UK regions (excluding northern ireland)")
    plt.ylabel("[GWh]")

    # --------
    # Legend
    # --------
    plt.legend(
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    else:
        plt.close()

def plot_radar_plot_multiple_lines(
        dh_profiles,
        fig_name,
        plot_steps,
        scenario_names,
        plotshow=False,
        lf_y_by=None,
        lf_y_cy=None,
        list_diff_max_h=None
    ):
    """Plot daily load profile on a radar plot

    Arguments
    ---------
    dh_profile : list
        Dh values to plot
    fig_name : str
        Path to save figure

    SOURCE: https://python-graph-gallery.com/390-basic-radar-chart/
    """
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 14))

    # Get maximum demand of all lines
    max_entry = 0
    for line_entries in dh_profiles:
        max_in_line = max(line_entries)
        if max_in_line > max_entry:
            max_entry = max_in_line

    max_demand = round(max_entry, -1) + 10 # Round to nearest 10 plus add 10

    nr_of_plot_steps = int(max_demand / plot_steps) + 1

    axis_plots_inner = []
    axis_plots_innter_position = []

    # --------------------
    # Ciruclar axis
    # --------------------
    for i in range(nr_of_plot_steps):
        axis_plots_inner.append(plot_steps*i)
        axis_plots_innter_position.append(str(plot_steps*i))

    # Minor ticks
    minor_tick_interval = plot_steps / 2
    minor_ticks = []
    for i in range(nr_of_plot_steps * 2):
        minor_ticks.append(minor_tick_interval * i)

    # ----
    # Select color scheme
    # ----

    # Colors with scenarios
    #color_scenarios = plotting_styles.color_list_scenarios() #Color scheme Fig 13

    # Colors for plotting Fig. 13
    color_scenarios = plotting_styles.color_list_selection_dm() # Color scheme Fig 13

    color_lines = ['black'] + color_scenarios
    years = ['2015', '2050']
    linewidth_list = [1.0, 0.7]
    linestyle_list = ['-', '--']
    scenario_names.insert(0, "any")

    # Iterate lines
    cnt = -1
    for dh_profile in dh_profiles:

        if cnt >= 0:
            cnt_year = 1
        else:
            cnt_year = 0
        cnt += 1

        # Line properties
        color_line = color_lines[cnt]
        year_line = years[cnt_year]

        data = {'dh_profile': ['testname']}

        # Key: Label outer circle
        for hour in range(24):
            data[hour] = dh_profile[hour]

        # Set data
        df = pd.DataFrame(data)

        # number of variable
        categories = list(df)[1:]
        N = len(categories)

        # We are going to plot the first line of the data frame.
        # But we need to repeat the first value to close the circular graph:
        values = df.loc[0].drop('dh_profile').values.flatten().tolist()
        values += values[:1]

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        # Initialise the spider plot
        ax = plt.subplot(111, polar=True)

        # Change axis properties
        ax.yaxis.grid(color='grey', linestyle=':', linewidth=0.4)
        ax.xaxis.grid(color='lightgrey', linestyle=':', linewidth=0.4)

        # Change to clockwise cirection
        ax.set_theta_direction(-1)

        # Set first hour on top
        ax.set_theta_zero_location("N")

        # Draw one axe per variable + add labels labels yet (numbers)
        plt.xticks(
            angles[:-1],
            categories,
            color='black',
            size=8)

        # Draw ylabels (numbers)
        ax.set_rlabel_position(0)

        # Working alternative
        plt.yticks(
            axis_plots_inner,
            axis_plots_innter_position,
            color="black",
            size=8)

        #ax.set_yticks(axis_plots_inner, minor=False)
        #ax.tick_params(axis='y', pad=35) 
        #ax.set_yticks(minor_ticks, minor=True) #Somehow not working

        # Set limit to size
        plt.ylim(0, max_demand)
        plt.ylim(0, nr_of_plot_steps*plot_steps)

        # Smooth lines
        angles_smoothed, values_smoothed = basic_plot_functions.smooth_data(
            angles, values, spider=True)

        # Plot data
        ax.plot(
            angles_smoothed,
            values_smoothed,
            color=color_line,
            linestyle=linestyle_list[cnt_year],
            linewidth=linewidth_list[cnt_year],
            label="{} {}".format(year_line, scenario_names[cnt]))

        # Radar area
        ax.fill(
            angles_smoothed,
            values_smoothed,
            color_line,
            alpha=0.05)

    # ------------
    # Write outs
    # ------------
    font_additional_info = plotting_styles.font_info(size=4)

    for cnt, entry in enumerate(list_diff_max_h):
        plt.text(
            0.15,
            0 + cnt/50,
            entry,
            fontdict=font_additional_info,
            transform=plt.gcf().transFigure)

    # ------------
    # Legend
    # ------------
    plt.legend(
        ncol=1,
        bbox_to_anchor=(0.2, -0.1),
        prop={'size': 4},
        frameon=False)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()

    plt.close()
