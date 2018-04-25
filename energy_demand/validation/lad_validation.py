"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
import os
import operator
import logging
import copy
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from energy_demand.basic import conversions
from energy_demand.profiles import generic_shapes
from energy_demand.plotting import plotting_program
from energy_demand.plotting import plotting_results
from energy_demand.validation import elec_national_data
from energy_demand.read_write import data_loader
from energy_demand.basic import date_prop
from energy_demand import enduse_func
from energy_demand.profiles import load_profile
from energy_demand.plotting import plotting_styles

def map_LAD_2011_2015(lad_data):
    """Map LAD 2015 values to LAD 2011.

    Arguments
    -----------
    lad_data : dict
        LAD 2015 data

    Returns
    --------
    mapped_lads : dict
        LAD 2011 census data lads
    """
    mapped_lads = copy.deepcopy(lad_data)

    mapped_lads.keys()

    # E41000324 (City of London, Westminster) splits
    # to E09000001 (City of London) and E09000033 (Westminster)
    mapped_lads['E41000324'] = lad_data['E09000001'] + lad_data['E09000033']
    del mapped_lads['E09000001']
    del mapped_lads['E09000033']

    # E41000052 (Cornwall, Isles of Scilly) splits
    # to E06000052 (Cornwall) and E06000053 (Isles of Scilly) (edited)
    mapped_lads['E41000052'] = lad_data['E06000052'] + lad_data['E06000053']
    del mapped_lads['E06000052']
    del mapped_lads['E06000053']

    # missing S12000013 (Na h-Eileanan Siar)
    # and S12000027 (Shetland Islands)
    del mapped_lads['S12000013']
    del mapped_lads['S12000027']

    return mapped_lads

def temporal_validation(
        result_paths,
        ed_fueltype_yh,
        elec_factored_yh,
        elec_2015_indo,
        elec_2015_itsdo,
        plot_criteria
    ):
    """National hourly electricity data is validated with
    the summed modelled hourly demand for all regions.
    Because the total annual modelled and real demands
    do not match (because of different data sources
    and because Northern Ireland is not included in the
    validation data) a correction factor is used.

    Arguments
    ---------
    result_paths : dict
        Paths
    ed_fueltype_yh : array
        Fuel type specific yh energy demand
    elec_2015_indo
    elec_2015_itsdo
    plot_criteria : bool
        Criteria to show plots or not
    """
    # ----------------
    # Plot a full year
    # ----------------
    days_to_plot = list(range(0, 365))
    elec_national_data.compare_results(
        'validation_temporal_electricity_8760h.pdf',
        result_paths['data_results_validation'],
        elec_2015_indo,
        elec_2015_itsdo,
        elec_factored_yh,
        ed_fueltype_yh,
        'all_submodels',
        days_to_plot,
        plot_crit=plot_criteria)

    # Plot four weeks (one of each season)
    winter_week = list(range(
        date_prop.date_to_yearday(2015, 1, 12), date_prop.date_to_yearday(2015, 1, 19))) #Jan
    spring_week = list(range(
        date_prop.date_to_yearday(2015, 5, 11), date_prop.date_to_yearday(2015, 5, 18))) #May
    summer_week = list(range(
        date_prop.date_to_yearday(2015, 7, 13), date_prop.date_to_yearday(2015, 7, 20))) #Jul
    autumn_week = list(range(
        date_prop.date_to_yearday(2015, 10, 12), date_prop.date_to_yearday(2015, 10, 19))) #Oct
    days_to_plot = winter_week + spring_week + summer_week + autumn_week

    elec_national_data.compare_results(
        'validation_temporal_electricity_weeks_selection.pdf',
        result_paths['data_results_validation'],
        elec_2015_indo,
        elec_2015_itsdo,
        elec_factored_yh,
        ed_fueltype_yh,
        'all_submodels',
        days_to_plot,
        plot_crit=plot_criteria)

    return

def tempo_spatial_validation(
        base_yr,
        model_yearhours_nrs,
        model_yeardays_nrs,
        scenario_data,
        ed_fueltype_national_yh,
        ed_fueltype_regs_yh,
        fueltypes,
        fueltypes_nr,
        result_paths,
        paths,
        regions,
        reg_coord,
        seasons,
        model_yeardays_daytype,
        plot_crit
    ):
    """Validate national hourly demand for yearls fuel
    for all LADs. Test how the national disaggregation
    works.

    Info
    -----
    Because the floor area is only availabe for LADs from 2001,
    the LADs are converted to 2015 LADs.
    """
    logging.info("... spatial validation")

    # -------------------------------------------
    # Add electricity and gas for transportation sector
    # -------------------------------------------
    fueltype_elec = fueltypes['electricity']
    fuel_ktoe_transport_2015 = 385
    fuel_national_tranport = np.zeros((fueltypes_nr), dtype=float)

    # Elec demand from ECUK for transport sector
    fuel_national_tranport[fueltype_elec] = conversions.ktoe_to_gwh(fuel_ktoe_transport_2015)

    # Create transport model (add flat shapes)
    model_object_transport = generic_shapes.GenericFlatEnduse(
        fuel_national_tranport, model_yeardays_nrs)

    # Add national fuel
    ed_fueltype_national_yh = np.add(ed_fueltype_national_yh, model_object_transport.fuel_yh)

    # Add electricity of transportion to regional yh fuel proportionally to population
    for region_array_nr, region in enumerate(regions):

        # Disaggregation factor for transport electricity
        factor_transport_reg = scenario_data['population'][base_yr][region] / sum(scenario_data['population'][base_yr].values())
        ed_fueltype_regs_yh[fueltype_elec][region_array_nr] += model_object_transport.fuel_yh[fueltype_elec].reshape(model_yearhours_nrs) * factor_transport_reg

    # -------------------------------------------
    # Spatial validation
    # -------------------------------------------
    subnational_elec = data_loader.read_national_real_elec_data(
        paths['path_val_subnational_elec'])
    subnational_gas = data_loader.read_national_real_gas_data(
        paths['path_val_subnational_gas'])

    # Create fueltype secific dict
    fuel_elec_regs_yh = {}
    for region_array_nr, region in enumerate(regions):
        gwh_modelled = np.sum(ed_fueltype_regs_yh[fueltypes['electricity']][region_array_nr])
        fuel_elec_regs_yh[region] = gwh_modelled

    # Create fueltype secific dict
    fuel_gas_regs_yh = {}
    for region_array_nr, region in enumerate(regions):
        gwh_modelled = np.sum(ed_fueltype_regs_yh[fueltypes['gas']][region_array_nr])
        fuel_gas_regs_yh[region] = gwh_modelled

    # ----------------------------------------
    # Remap demands between 2011 and 2015 LADs
    # ----------------------------------------
    subnational_elec = map_LAD_2011_2015(subnational_elec)
    subnational_gas = map_LAD_2011_2015(subnational_gas)
    fuel_elec_regs_yh = map_LAD_2011_2015(fuel_elec_regs_yh)
    fuel_gas_regs_yh = map_LAD_2011_2015(fuel_gas_regs_yh)

    logging.info("Validation of electricity")
    spatial_validation(
        reg_coord,
        fuel_elec_regs_yh,
        subnational_elec,
        regions,
        'elec',
        os.path.join(result_paths['data_results_validation'], 'validation_spatial_elec.pdf'),
        label_points=False,
        plotshow=plot_crit)

    logging.info("Validation of gas")
    spatial_validation(
        reg_coord,
        fuel_gas_regs_yh,
        subnational_gas,
        regions,
        'gas',
        os.path.join(result_paths['data_results_validation'], 'validation_spatial_gas.pdf'),
        label_points=False,
        plotshow=plot_crit)

    # -------------------------------------------
    # Temporal validation (hourly for national)
    # -------------------------------------------
    # Read validation data
    elec_2015_indo, elec_2015_itsdo = elec_national_data.read_raw_elec_2015(
        paths['path_val_nat_elec_data'])

    f_diff_elec = np.sum(ed_fueltype_national_yh[fueltypes['electricity']]) / np.sum(elec_2015_indo)
    logging.info(
        "... ed diff modellend and real [p] %s: ", (1 - f_diff_elec) * 100)

    elec_factored_yh = f_diff_elec * elec_2015_indo

    temporal_validation(
        result_paths,
        ed_fueltype_national_yh[fueltypes['electricity']],
        elec_factored_yh,
        elec_2015_indo,
        elec_2015_itsdo,
        plot_crit)

    # ---------------------------------------------------
    # Calculate average season and daytypes and plot
    # ---------------------------------------------------
    logging.info("...calculate average data and plot per season and fueltype")

    calc_av_lp_modelled, calc_lp_modelled = load_profile.calc_av_lp(
        ed_fueltype_national_yh[fueltypes['electricity']],
        seasons,
        model_yeardays_daytype)

    calc_av_lp_real, calc_lp_real = load_profile.calc_av_lp(
        elec_factored_yh,
        seasons,
        model_yeardays_daytype)

    # Plot average daily loads
    plotting_results.plot_load_profile_dh_multiple(
        path_fig_folder=result_paths['data_results_validation'],
        path_plot_fig=os.path.join(
            result_paths['data_results_validation'],
            'validation_all_season_daytypes.pdf'),
        calc_av_lp_modelled=calc_av_lp_modelled,
        calc_av_lp_real=calc_av_lp_real,
        calc_lp_modelled=calc_lp_modelled,
        calc_lp_real=calc_lp_real,
        plot_peak=True,
        plot_radar=False,
        plot_all_entries=False,
        plot_max_min_polygon=True,
        plotshow=False,
        max_y_to_plot=60,
        fueltype_str=False,
        year=False)

    # ---------------------------------------------------
    # Validation of national electrictiy demand for peak
    # ---------------------------------------------------
    logging.debug(
        "...validation of peak data: compare peak with data")

    # Because the coldest day is not the same for every region,
    # the coldest day needs to be defined manually or defined
    # by getting the hours with maximum electricity demand

    # Peak across all fueltypes WARNING: Fueltype specific
    peak_day_all_fueltypes = enduse_func.get_peak_day_all_fueltypes(ed_fueltype_national_yh)
    
    fueltype = fueltypes['electricity']
    peak_day_electricity, _ = enduse_func.get_peak_day_single_fueltype(ed_fueltype_national_yh[fueltype])

    elec_national_data.compare_peak(
        "validation_peak_elec_day_all_fueltypes.pdf",
        result_paths['data_results_validation'],
        elec_2015_indo[peak_day_all_fueltypes],
        ed_fueltype_national_yh[fueltypes['electricity']][peak_day_all_fueltypes],
        peak_day_all_fueltypes)

    elec_national_data.compare_peak(
        "validation_peak_elec_day_only_electricity.pdf",
        result_paths['data_results_validation'],
        elec_2015_indo[peak_day_electricity],
        ed_fueltype_national_yh[fueltypes['electricity']][peak_day_electricity],
        peak_day_electricity)

    # Manual peak day
    peak_day = 19
    elec_national_data.compare_peak(
        "validation_elec_peak_day_{}.pdf".format(peak_day),
        result_paths['data_results_validation'],
        elec_2015_indo[peak_day],
        ed_fueltype_national_yh[fueltypes['electricity']][peak_day],
        peak_day)

    peak_day = 33
    elec_national_data.compare_peak(
        "validation_elec_peak_day_{}.pdf".format(peak_day),
        result_paths['data_results_validation'],
        elec_2015_indo[peak_day],
        ed_fueltype_national_yh[fueltypes['electricity']][peak_day],
        peak_day)
    # ---------------------------------------------------
    # Validate boxplots for every hour (temporal validation)
    # ---------------------------------------------------
    elec_national_data.compare_results_hour_boxplots(
        "validation_hourly_boxplots_electricity_01.pdf",
        result_paths['data_results_validation'],
        elec_2015_indo,
        ed_fueltype_national_yh[fueltypes['electricity']])

    return

def spatial_validation(
        reg_coord,
        subnational_modelled,
        subnational_real,
        regions,
        fueltype_str,
        fig_name,
        label_points=False,
        plotshow=False
    ):
    """Compare gas/elec demand for LADs

    Arguments
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    ed_fueltype_regs_yh : object
        Regional fuel Given as GWh (?)
    subnational_real : dict
        for electricity: Sub-national electrcity demand given as GWh

    Note
    -----
    SOURCE OF LADS:
        - Data for northern ireland is not included in that, however in BEIS dataset!
    """
    logging.debug("... Validation of spatial disaggregation")
    result_dict = {}
    result_dict['real_demand'] = {}
    result_dict['modelled_demand'] = {}

    # -------------------------------------------
    # Match ECUK sub-regional demand with geocode
    # -------------------------------------------
    for region in regions:
        for reg_geocode in reg_coord:
            if reg_geocode == region:

                try:
                    # Test wheter data is provided for LAD or owtherwise ignore
                    if subnational_real[reg_geocode] == 0:
                        pass
                    else:
                        # --Sub Regional Electricity demand (as GWh)
                        result_dict['real_demand'][reg_geocode] = subnational_real[reg_geocode]
                        result_dict['modelled_demand'][reg_geocode] = subnational_modelled[reg_geocode]

                except KeyError:
                    logging.warning(
                        "Sub-national spatial validation: No fuel for region %s", reg_geocode)

    # --------------------
    # Calculate statistics
    # --------------------
    diff_real_modelled_p = []
    diff_real_modelled_abs = []

    for reg_geocode in regions:
        try:
            real = result_dict['real_demand'][reg_geocode]
            modelled = result_dict['modelled_demand'][reg_geocode]

            diff_real_modelled_p.append((100/real) * modelled)
            diff_real_modelled_abs.append(real - modelled)
        except KeyError:
            pass

    # Calculate the average deviation between reald and modelled
    av_deviation_real_modelled = np.average(diff_real_modelled_p)

    # Calculate standard deviation
    std_dev_p = np.std(diff_real_modelled_p)        # Given as percent
    std_dev_abs = np.std(diff_real_modelled_abs)    # Given as energy unit

    # -----------------
    # Sort results according to size
    # -----------------
    sorted_dict_real = sorted(
        result_dict['real_demand'].items(),
        key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=plotting_program.cm2inch(9, 8)) #width, height (9, 8)

    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_dict_real), 1)

    y_real_demand = []
    y_modelled_demand = []

    labels = []
    for sorted_region in sorted_dict_real:

        geocode_lad = sorted_region[0]

        y_real_demand.append(
            result_dict['real_demand'][geocode_lad])
        y_modelled_demand.append(
            result_dict['modelled_demand'][geocode_lad])

        logging.info(
            "validation %s LAD %s: %s %s (%s p diff)",
            fueltype_str,
            geocode_lad,
            round(result_dict['real_demand'][geocode_lad], 4),
            round(result_dict['modelled_demand'][geocode_lad], 4),
            round(100 - (100 / result_dict['real_demand'][geocode_lad]) * result_dict['modelled_demand'][geocode_lad], 4))

        # Labels
        labels.append(geocode_lad)

    # Calculate r_squared
    _slope, _intercept, r_value, _p_value, _std_err = stats.linregress(
        y_real_demand,
        y_modelled_demand)

    # --------
    # Axis
    # --------
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off

    # ----------------------------------------------
    # Plot
    # ----------------------------------------------
    plt.plot(
        x_values,
        y_real_demand,
        linestyle='None',
        marker='o',
        alpha=0.6,
        markersize=1.6,
        fillstyle='full',
        markerfacecolor='grey',
        markeredgewidth=0.2,
        color='black',
        label='actual')

    plt.plot(
        x_values,
        y_modelled_demand,
        marker='o',
        linestyle='None',
        markersize=1.6,
        alpha=0.6,
        markerfacecolor='white',
        fillstyle='none',
        markeredgewidth=0.5,
        markeredgecolor='blue',
        color='black',
        label='model')

    # Limit
    plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):

            ax.text(
                x_values[pos],
                y_modelled_demand[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=3)

    font_additional_info = plotting_styles.font_info()

    font_additional_info['size'] = 6

    title_info = ('R_2: {}, std_%: {} (GWh {}), av_diff_%: {}'.format(
        round(r_value, 2),
        round(std_dev_p, 2),
        round(std_dev_abs, 2),
        round(av_deviation_real_modelled, 2)))

    plt.title(
        title_info,
        loc='left',
        fontdict=font_additional_info)

    plt.xlabel("UK regions (excluding northern ireland)")
    plt.ylabel("{} [GWh]".format(fueltype_str))

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
