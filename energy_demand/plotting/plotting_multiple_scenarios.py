"""
This file containes functions to plot multiple scenarios in a folder
"""
import os
import operator
import collections
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.plotting import plotting_styles
from energy_demand.plotting import plotting_program
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_results
from energy_demand.basic import lookup_tables
from energy_demand.technologies import tech_related

def plot_heat_pump_chart(
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
    lookups = lookup_tables.basic_lookups()

    year_to_plot = 2050

    # Collect value to display on axis
    result_dict = {} # {scenario_value:  {year: {fueltype: np.array(reg, value))}}

    for scenario_name, scenario_data in scenario_data.items():

        # Scenario value
        value_scenario = float(scenario_name.split("__")[1])

        # Get peak for all regions {year: {fueltype: np.array(reg,value))}
        y_lf_fueltype = {}

        for year, data_lf_fueltypes in scenario_data['load_factors_y'].items(): # {scenario_value: np.array((regions, result_value))}

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

        result_dict[value_scenario] = y_lf_fueltype

    # Sort dict and convert to OrderedDict
    result_dict = collections.OrderedDict(sorted(result_dict.items()))

    #-----
    # Plot
    # -----

    # Criteria to plot maximum boundaries
    plot_max_min_polygon = True
    plot_all_regs = False

    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(16, 8))
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
        for year in years:
            regs = fuel_fueltype_yrs[year]
            break
        break

    legend_entries = []
    for year in years:
        color_scenario = color_list_selection.pop()

        legend_entries.append("mean {}".format(year))

        # ----------------
        # For every region
        # ----------------
        for reg_nr, _ in enumerate(regs):
            year_data = []
            for _percent_value, fuel_fueltype_yrs in result_dict.items():
                year_data.append(fuel_fueltype_yrs[year][reg_nr])

            # Paste out if not individual regions and set plot_max_min_polygon to True
            if plot_all_regs:
                plt.plot(
                    list(all_percent_values),
                    list(year_data),
                    color=str(color_scenario))

        # --------------------
        # Plot max min polygon
        # --------------------
        if plot_max_min_polygon:

            # Create value {x_vals: [y_vals]}
            x_y_values = {}
            for _percent_value, fuel_fueltype_yrs in result_dict.items():
                x_y_values[_percent_value] = []
                for reg_nr, _ in enumerate(regs):
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
    plt.ylim(ymax=100)
    plt.xlim(xmin=0)
    plt.xlim(xmax=100)

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
    plt.ylabel("load factor [%] [{}]".format(fueltype_str_input))
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
    plt.figure(figsize=plotting_program.cm2inch(14, 8))

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

        plt.plot(
            list(fuel_fueltype_yrs['ed_peak_h'].keys()),     # years
            list(data_container),               # yearly data
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
    plt.figure(figsize=plotting_program.cm2inch(14, 8))

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
    color_list_selection = plotting_styles.color_list_selection()

    for scenario_name, fuel_fueltype_yrs in y_scenario.items():

        color_scenario = color_list_selection.pop()

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
                color=str(color_scenario))
    # ----
    # Axis
    # ----
    plt.ylim(ymin=0)

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        ncol=2,
        loc=3,
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)

    # ---------
    # Labels
    # ---------
    plt.ylabel("GWh")
    plt.xlabel("year")
    plt.title("tot y ED all fueltypes")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
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
    plt.figure(figsize=plotting_program.cm2inch(14, 8))

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
    color_list_selection = plotting_styles.color_list_selection()

    for scenario_name, fuel_fueltype_yrs in y_scenario.items():

        #scenario_name = "{} (tot: {} [TWh])".format(
        #scenario, round(tot_demand, 2))

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
        ncol=2,
        loc=2,
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
    else:
        plt.close()

def plot_radar_plots_average_peak_day(
        scenario_data,
        year_to_plot,
        fig_name,
        plotshow
    ):
    """Compare averaged dh profile overall regions for peak day
    for future year and base year

    MAYBE: SO FAR ONLY FOR ONE SCENARIO
    """
    lookups = lookup_tables.basic_lookups()

    # Scenarios
    all_scenarios = list(scenario_data.keys())
    first_scenario = str(all_scenarios[:1][0])

    # ----------------
    # Create base year peak load profile
    # -----------------
    all_regs_fueltypes_yh_by = {}
    for fueltype, fuels_regs in enumerate(scenario_data[first_scenario]['results_every_year'][2015]):
        for region_array_nr, fuel_reg in enumerate(fuels_regs):
            try:
                all_regs_fueltypes_yh_by[fueltype] += fuel_reg
            except KeyError:
                all_regs_fueltypes_yh_by[fueltype] = fuel_reg
            try:
                all_fuels_by += fuel_reg
            except:
                all_fuels_by = fuel_reg

    # ------------------------
    # Future year load profile
    # ------------------------
    all_regs_fueltypes_yh_ey = {}
    for fueltype, fuels_regs in enumerate(scenario_data[first_scenario]['results_every_year'][year_to_plot]):
        for region_array_nr, fuel_reg in enumerate(fuels_regs):
            try:
                all_regs_fueltypes_yh_ey[fueltype] += fuel_reg
            except KeyError:
                all_regs_fueltypes_yh_ey[fueltype] = fuel_reg

    # -----------
    # get peak day across all fueltypes
    # -----------
    for fueltype in all_regs_fueltypes_yh_by.keys():
        all_regs_fueltypes_yh_by[fueltype] = all_regs_fueltypes_yh_by[fueltype].reshape((365, 24))
    for fueltype in all_regs_fueltypes_yh_ey.keys():
        all_regs_fueltypes_yh_ey[fueltype] = all_regs_fueltypes_yh_ey[fueltype].reshape((365, 24))

    all_fuels_by_d = all_fuels_by.reshape((365, 24))

    peak_day_nr = np.argmax(np.sum(all_fuels_by_d, axis=1))

    for fueltype in all_regs_fueltypes_yh_by.keys():

        fueltype_str = tech_related.get_fueltype_str(lookups['fueltypes'], fueltype)

        name_spider_plot = os.path.join(fig_name, "spider_{}.pdf".format(fueltype_str))

        # ---------------------------
        # Calculate load factors
        # ---------------------------
        max_load_h_by = max(all_regs_fueltypes_yh_by[fueltype][peak_day_nr])
        average_load_y_by = np.average(all_regs_fueltypes_yh_by[fueltype])
        load_factor_fueltype_y_by = (average_load_y_by / max_load_h_by) * 100 #convert to percentage

        max_load_h_cy = max(all_regs_fueltypes_yh_ey[fueltype][peak_day_nr])
        average_load_y_cy = np.average(all_regs_fueltypes_yh_ey[fueltype])
        load_factor_fueltype_y_cy = (average_load_y_cy / max_load_h_cy) * 100 #convert to percentage

        # ----------------------------------
        # Plot dh for peak day for base year
        # ----------------------------------
        individ_radars_to_plot_dh = [
            list(all_regs_fueltypes_yh_by[fueltype][peak_day_nr]),
            list(all_regs_fueltypes_yh_ey[fueltype][peak_day_nr])]

        plotting_results.plot_radar_plot_multiple_lines(
            individ_radars_to_plot_dh,
            name_spider_plot,
            plot_steps=50,
            plotshow=False,
            lf_y_by=load_factor_fueltype_y_by,
            lf_y_cy=load_factor_fueltype_y_cy)

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
        figsize=plotting_program.cm2inch(9, 8))

    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_regions_nrs), 1)

    # ----------------------------------------------
    # Plot base year values
    # ----------------------------------------------
    base_year_data = []
    for reg_array_nr in sorted_regions_nrs:
        base_year_data.append(regions[reg_array_nr])
    total_base_year_sum = sum(base_year_data)
    print("SUM: " + str(total_base_year_sum))

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
