"""
"""
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

from energy_demand.profiles import load_factors
from energy_demand.plotting import basic_plot_functions

def plot_cross_graphs(
        base_yr,
        comparison_year,
        regions,
        ed_year_fueltype_regs_yh,
        reg_load_factor_y,
        fueltype_int,
        fueltype_str,
        fig_name,
        label_points,
        plotshow):

    result_dict = defaultdict(dict)

    # -------------------------------------------
    # Get base year modelled demand
    # -------------------------------------------
    for year, fuels in ed_year_fueltype_regs_yh.items():

        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['demand_by'][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                result_dict['peak_h_demand_by'][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

            # Demand across all regs
            result_dict['demand_by_all_regs'] = np.sum(fuels[fueltype_int])

            # Peak demand
            fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0)# Sum across all regions
            result_dict['peak_h_demand_by_all_regs'] = np.max(fuel_all_reg_yh)

            # Calculate national load factor
            fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
            load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
            result_dict['lf_by_all_regs_av'] = load_factor_y[fueltype_int]

        elif year == comparison_year:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['demand_cy'][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                result_dict['peak_h_demand_cy'][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

            # Demand across all regs
            result_dict['demand_cy_all_regs'] = np.sum(fuels[fueltype_int])

            # Peak demand
            fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0) # Sum across all regions
            result_dict['peak_h_demand_cy_all_regs'] = np.max(fuel_all_reg_yh)

            # Calculate national load factor
            fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
            load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
            result_dict['lf_cy_all_regs_av'] = load_factor_y[fueltype_int]
        else:
            pass

    # Get load factor
    result_dict['lf_cy'] = {}
    result_dict['lf_by'] = {}
    for year, lf_fueltype_regs in reg_load_factor_y.items():
        print("lf_fueltype_regs")
        print(lf_fueltype_regs.shape)
        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['lf_by'][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]

        elif year == comparison_year:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['lf_cy'][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]
        else:
            pass

    labels = []

    #Base year
    x_values, y_values = [], []
    x_values_0_quadrant, y_values_0_quadrant = [], []
    x_values_1_quadrant, y_values_1_quadrant = [], []
    x_values_2_quadrant, y_values_2_quadrant = [], []
    x_values_3_quadrant, y_values_3_quadrant = [], []

    for reg_nr, reg_geocode in enumerate(regions):

        # Change in load factor
        lf_change_p = ((100 / result_dict['lf_by'][reg_geocode]) * result_dict['lf_cy'][reg_geocode]) - 100

        # Change in peak h deman
        demand_peak_h_p = ((100 / result_dict['peak_h_demand_by'][reg_geocode]) * result_dict['peak_h_demand_cy'][reg_geocode]) - 100

        # Change in total regional demand
        tot_demand_p = ((100 / result_dict['demand_by'][reg_geocode]) * result_dict['demand_cy'][reg_geocode]) - 100

        x_values.append(lf_change_p)
        #y_values.append(tot_demand_p)
        y_values.append(demand_peak_h_p)

        labels.append(reg_geocode)

        if lf_change_p < 0 and tot_demand_p > 0:
            x_values_0_quadrant.append(lf_change_p)
            y_values_0_quadrant.append(tot_demand_p)
        elif lf_change_p > 0 and tot_demand_p > 0:
            x_values_1_quadrant.append(lf_change_p)
            y_values_1_quadrant.append(tot_demand_p)
        elif lf_change_p > 0 and tot_demand_p < 0:
            x_values_2_quadrant.append(lf_change_p)
            y_values_2_quadrant.append(tot_demand_p)
        else:
            x_values_3_quadrant.append(lf_change_p)
            y_values_3_quadrant.append(tot_demand_p)

    # Add average
    national_tot_cy_p = ((100 / result_dict['lf_by_all_regs_av']) * result_dict['lf_cy_all_regs_av']) - 100
    #national_tot_demand_p = ((100 / result_dict['demand_by_all_regs']) * result_dict['demand_cy_all_regs']) - 100
    national_peak_h_p = ((100 / result_dict['peak_h_demand_by_all_regs']) * result_dict['peak_h_demand_cy_all_regs']) - 100

    x_val_national_lf_demand_cy = [national_tot_cy_p]
    #y_val_national_lf_demand_cy = [national_tot_demand_p]
    y_val_national_lf_demand_cy = [national_peak_h_p]

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(
        x_values_0_quadrant,
        y_values_0_quadrant,
        alpha=0.6,
        color='rosybrown',
        s=8)
    ax.scatter(
        x_values_1_quadrant,
        y_values_1_quadrant,
        alpha=0.6,
        color='firebrick',
        s=8)
    ax.scatter(
        x_values_2_quadrant,
        y_values_2_quadrant,
        alpha=0.6,
        color='forestgreen',
        s=8)
    ax.scatter(
        x_values_3_quadrant,
        y_values_3_quadrant,
        alpha=0.6,
        color='darkolivegreen',
        s=8)

    # Add average
    ax.scatter(
        x_val_national_lf_demand_cy,
        y_val_national_lf_demand_cy,
        alpha=1.0,
        color='black',
        s=20,
        marker="v",
        linewidth=0.5,
        edgecolor='black',
        label='national')

    # --------
    # Axis
    # --------
    ax.set_xlabel("load factor change (%) {}".format(fueltype_str))
    ax.set_ylabel("change in peak h (%) {}".format(fueltype_str))

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='on',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='on') # labels along the bottom edge are off

    # --------
    # Grd
    # --------
    ax.set_axisbelow(True)
    ax.set_xticks([0], minor=True)
    ax.set_yticks([0], minor=True)
    ax.yaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')
    ax.xaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')

    # Limit
    #plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_values[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=6)
    # --------
    # Legend
    # --------
    '''legend(
        loc=3,
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)'''

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    plt.close()

def plot_cross_graphs_scenarios(
        base_yr,
        comparison_year,
        regions,
        scenario_data,
        fueltype_int,
        fueltype_str,
        fig_name,
        label_points,
        plotshow):

    result_dict = defaultdict(dict)

    # -------------------------------------------
    # Get base year modelled demand of any scenario (becasue base year the same in every scenario)
    # -------------------------------------------$
    all_scenarios = list(scenario_data.keys())
    first_scenario = all_scenarios[0]
    ed_year_fueltype_regs_yh = scenario_data[first_scenario]['results_every_year']

    for year, fuels in ed_year_fueltype_regs_yh.items():

        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['demand_by'][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                result_dict['peak_h_demand_by'][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

            # Demand across all regs
            result_dict['demand_by_all_regs'] = np.sum(fuels[fueltype_int])

            # Peak demand
            fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0)# Sum across all regions
            result_dict['peak_h_demand_by_all_regs'] = np.max(fuel_all_reg_yh)

            # Calculate national load factor
            fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
            load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
            result_dict['lf_by_all_regs_av'] = load_factor_y[fueltype_int]

    for scenario, data in scenario_data.items():
        result_dict['demand_cy'][scenario] = {}
        result_dict['peak_h_demand_cy'][scenario] = {}

        for year, fuels in data['results_every_year'].items():
            if year == comparison_year:
                for reg_nr, reg_geocode in enumerate(regions):
                    result_dict['demand_cy'][scenario][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                    result_dict['peak_h_demand_cy'][scenario][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

                # Demand across all regs
                result_dict['demand_cy_all_regs'][scenario] = np.sum(fuels[fueltype_int])

                # Peak demand
                fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0) # Sum across all regions
                result_dict['peak_h_demand_cy_all_regs'][scenario] = np.max(fuel_all_reg_yh)

                # Calculate national load factor
                fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
                load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
                result_dict['lf_cy_all_regs_av'][scenario] = load_factor_y[fueltype_int]
            else:
                pass

    # Get load factor of base year
    reg_load_factor_y = scenario_data[first_scenario]['reg_load_factor_y']
    for year, lf_fueltype_regs in reg_load_factor_y.items():
        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['lf_by'][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]

    for scenario, data in scenario_data.items():
        reg_load_factor_y = scenario_data[scenario]['reg_load_factor_y']
        result_dict['lf_cy'][scenario] = {}

        for year, lf_fueltype_regs in reg_load_factor_y.items():
            if year == comparison_year:
                for reg_nr, reg_geocode in enumerate(regions):
                    result_dict['lf_cy'][scenario][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]
            else:
                pass

    # --------------------------
    # Iterate scenario and plot
    # --------------------------
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(18, 8)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    color_list = plotting_styles.color_list_scenarios()
    marker_list = plotting_styles.marker_list()

    all_x_values = []
    all_y_values = []

    for scenario_nr, scenario in enumerate(all_scenarios):

        labels = []

        #Base year
        x_values, y_values = [], []

        for reg_nr, reg_geocode in enumerate(regions):

            # Change in load factor
            lf_change_p = (
                (100 / result_dict['lf_by'][reg_geocode]) * result_dict['lf_cy'][scenario][reg_geocode]) - 100

            # Change in peak h deman
            demand_peak_h_p = (
                (100 / result_dict['peak_h_demand_by'][reg_geocode]) * result_dict['peak_h_demand_cy'][scenario][reg_geocode]) - 100

            # Change in total regional demand
            tot_demand_p = (
                (100 / result_dict['demand_by'][reg_geocode]) * result_dict['demand_cy'][scenario][reg_geocode]) - 100

            x_values.append(lf_change_p)
            #y_values.append(tot_demand_p)
            y_values.append(demand_peak_h_p)

            labels.append(reg_geocode)

        # Add average
        national_tot_cy_p = ((100 / result_dict['lf_by_all_regs_av']) * result_dict['lf_cy_all_regs_av'][scenario]) - 100
        #national_tot_demand_p = ((100 / result_dict['demand_by_all_regs']) * result_dict['demand_cy_all_regs'][scenario]) - 100
        national_peak_h_p = ((100 / result_dict['peak_h_demand_by_all_regs']) * result_dict['peak_h_demand_cy_all_regs'][scenario]) - 100

        x_val_national_lf_demand_cy = [national_tot_cy_p]
        #y_val_national_lf_demand_cy = [national_tot_demand_p]
        y_val_national_lf_demand_cy = [national_peak_h_p]

        all_x_values += x_values
        all_y_values += y_values
        # -------------------------------------
        # Plot
        # -------------------------------------
        color = color_list[scenario_nr]
        marker = marker_list[scenario_nr]

        alpha_value = 0.6
        marker_size = 7
        ax.scatter(
            x_values,
            y_values,
            alpha=alpha_value,
            color=color,
            #marker=marker,
            edgecolor=color,
            linewidth=0.5,
            s=marker_size,
            label=scenario)

        # Add average
        ax.scatter(
            x_val_national_lf_demand_cy,
            y_val_national_lf_demand_cy,
            alpha=1.0,
            color=color,
            s=20,
            marker="v",
            linewidth=0.5,
            edgecolor='black',
            label='national')

    # --------
    # Axis
    # --------
    ax.set_xlabel("load factor change (%) {}".format(fueltype_str))
    ax.set_ylabel("change in peak h (%) {}".format(fueltype_str))

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='on',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='on') # labels along the bottom edge are off

    # --------
    # Grd
    # --------
    ax.set_axisbelow(True)
    #ax.grid(True)
    #ax.set_xticks(minor=False)
    ax.set_xticks([0], minor=True)
    #ax.set_yticks(minor=False)
    ax.set_yticks([0], minor=True)
    #ax.yaxis.grid(True, which='major')
    ax.yaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')
    #ax.xaxis.grid(True, which='major')
    ax.xaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')

    # Limit
    #plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_values[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=6)

    # -------
    # Title information
    # -------
    max_lf = round(max(all_x_values), 2)
    min_lf = round(min(all_x_values), 2)
    min_peak_h = round(min(all_y_values), 2)
    max_peak_h = round(max(all_y_values), 2)

    font_additional_info = plotting_styles.font_info(size=4)

    plt.title(
        "max_peak_h: {} min_peak_h: {}, min_lf: {} max_lf: {}".format(
            max_peak_h,
            min_peak_h,
            min_lf,
            max_lf),
        fontdict=font_additional_info)

    # --------
    # Legend
    # --------
    plt.legend(
        loc='best',
        ncol=1,
        prop={
            'family': 'arial',
            'size': 3},
        frameon=False)

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    plt.close()
