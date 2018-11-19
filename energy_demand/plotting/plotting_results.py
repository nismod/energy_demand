"""Plotting model results and storing as PDF to result folder
"""
import os
import logging

from energy_demand.technologies import tech_related

from energy_demand.plotting import plotting_styles
from energy_demand.plotting import fig_lad_related
from energy_demand.plotting import fig_one_fueltype_multiple_regions_peak_h
from energy_demand.plotting import fig_fuels_enduses_y
from energy_demand.plotting import fig_stacked_enduse
from energy_demand.plotting import fig_cross_graphs
from energy_demand.plotting import fig_stacked_enduse_sectors
from energy_demand.plotting import fig_lf
from energy_demand.plotting import fig_fuels_enduses_week
from energy_demand.plotting import fig_load_profile_dh_multiple
from energy_demand.plotting import fig_fuels_peak_h
from energy_demand.plotting import fig_weather_variability_priod

#matplotlib.use('Agg') # Used to make it work in linux179

def run_all_plot_functions(
        results_container,
        reg_nrs,
        regions,
        lookups,
        result_paths,
        assumptions,
        enduses,
        plot_crit,
        base_yr,
        comparison_year
    ):
    """Summary function to plot all results

    comparison_year : int
        Year to generate comparison plots
    """
    if plot_crit['plot_lad_cross_graphs']:

        try:
            # Plot cross graph where very region is a dot
            fig_cross_graphs.plot_cross_graphs(
                base_yr=base_yr,
                comparison_year=comparison_year,
                regions=regions,
                ed_year_fueltype_regs_yh=results_container['ed_fueltype_regs_yh'],
                reg_load_factor_y=results_container['reg_load_factor_y'],
                fueltype_int=lookups['fueltypes']['electricity'],
                fueltype_str='electricity',
                fig_name=os.path.join(
                    result_paths['data_results_PDF'], "comparions_LAD_cross_graph_electricity_by_cy.pdf"),
                label_points=False,
                plotshow=False)

            fig_cross_graphs.plot_cross_graphs(
                base_yr=base_yr,
                comparison_year=comparison_year,
                regions=regions,
                ed_year_fueltype_regs_yh=results_container['ed_fueltype_regs_yh'],
                reg_load_factor_y=results_container['reg_load_factor_y'],
                fueltype_int=lookups['fueltypes']['gas'],
                fueltype_str='gas',
                fig_name=os.path.join(
                    result_paths['data_results_PDF'], "comparions_LAD_cross_graph_gas_by_cy.pdf"),
                label_points=False,
                plotshow=False)
        except KeyError:
            logging.info("Check if correct comparison year is provided, i.e. really data exists for this year")

    # ----------
    # Plot LAD differences for first and last year
    # ----------
    try:
        fig_lad_related.plot_lad_comparison(
            base_yr=2015,
            comparison_year=2050,
            regions=regions,
            ed_year_fueltype_regs_yh=results_container['ed_fueltype_regs_yh'],
            fueltype_int=lookups['fueltypes']['electricity'],
            fueltype_str='electricity',
            fig_name=os.path.join(
                result_paths['data_results_PDF'], "comparions_LAD_modelled_electricity_by_cy.pdf"),
            label_points=False,
            plotshow=False)
        print("... plotted by-cy LAD energy demand compariosn")

        # Plot peak h for every hour
        fig_lad_related.lad_comparison_peak(
            base_yr=2015,
            comparison_year=2050,
            regions=regions,
            ed_year_fueltype_regs_yh=results_container['ed_fueltype_regs_yh'],
            fueltype_int=lookups['fueltypes']['electricity'],
            fueltype_str='electricity',
            fig_name=os.path.join(
                result_paths['data_results_PDF'], "comparions_LAD_modelled_electricity_peakh_by_cy.pdf"),
            label_points=False,
            plotshow=False)
        print("... plotted by-cy LAD energy demand compariosn")
    except:
        pass

    # ----------------
    # Plot demand for every region over time
    # -------------------
    if plot_crit['plot_line_for_every_region_of_peak_demand']:
        logging.info("... plot fuel per fueltype for every region over annual teimsteps")
        fig_one_fueltype_multiple_regions_peak_h.plt_regions_peak_h(
            results_container['ed_fueltype_regs_yh'],
            lookups,
            regions,
            os.path.join(
                result_paths['data_results_PDF'],
                'peak_h_total_electricity.pdf'),
            fueltype_str_to_plot="electricity")

    if plot_crit['plot_fuels_enduses_y']:

        #... Plot total fuel (y) per fueltype as line chart"
        fig_fuels_enduses_y.run(
            results_container['ed_fueltype_regs_yh'],
            lookups,
            os.path.join(
                result_paths['data_results_PDF'],
                'y_fueltypes_all_enduses.pdf'))

    # ------------
    # Plot stacked annual enduses
    # ------------
    if plot_crit['plot_stacked_enduses']:

        rs_enduses_sorted = [
            'rs_space_heating',
            'rs_water_heating',
            'rs_lighting',
            'rs_cold',
            'rs_wet',
            'rs_consumer_electronics',
            'rs_home_computing',
            'rs_cooking']
    
        ss_enduses_sorted = [
            'ss_space_heating',
            'ss_water_heating',
            'ss_lighting',
            'ss_catering',
            'ss_small_power',
            'ss_fans',
            'ss_cooling_humidification',
            'ss_ICT_equipment',
            'ss_other_gas',
            'ss_other_electricity',
            'ss_cooled_storage']
        
        is_enduses_sorted = [
            'is_space_heating',
            'is_lighting',
            'is_refrigeration',
            'is_motors',
            'is_compressed_air',
            'is_high_temp_process',
            'is_low_temp_process',
            'is_other',
            'is_drying_separation']

        rs_color_list = plotting_styles.rs_color_list_selection()
        ss_color_list = plotting_styles.ss_color_list_selection()
        is_color_list = plotting_styles.is_color_list_selection()

        # Residential
        fig_stacked_enduse.run(
            assumptions['sim_yrs'],
            results_container['results_enduse_every_year'],
            rs_enduses_sorted,
            rs_color_list,
            os.path.join(
                result_paths['data_results_PDF'], "stacked_rs_country.pdf"),
            plot_legend=True)

        # Service
        fig_stacked_enduse.run(
            assumptions['sim_yrs'],
            results_container['results_enduse_every_year'],
            ss_enduses_sorted,
            ss_color_list,
            os.path.join(
                result_paths['data_results_PDF'], "stacked_ss_country.pdf"),
            plot_legend=True)

        # Industry
        fig_stacked_enduse.run(
            assumptions['sim_yrs'],
            results_container['results_enduse_every_year'],
            is_enduses_sorted,
            is_color_list,
            os.path.join(
                result_paths['data_results_PDF'], "stacked_is_country_.pdf"),
            plot_legend=True)

    # ------------------------------
    # Plot annual demand for enduses for all submodels
    # ------------------------------
    if plot_crit['plot_y_all_enduses']:

        fig_stacked_enduse_sectors.run(
            lookups,
            assumptions['sim_yrs'],
            results_container['results_enduse_every_year'],
            enduses['residential'],
            enduses['service'],
            enduses['industry'],
            os.path.join(result_paths['data_results_PDF'],
            "stacked_all_enduses_country.pdf"))

    # --------------
    # Fuel per fueltype for whole country over annual timesteps
    # ----------------
    if plot_crit['plot_fuels_enduses_y']:
        logging.info("... plot fuel per fueltype for whole country over annual timesteps")
        #... Plot total fuel (y) per fueltype as line chart"
        fig_fuels_enduses_y.run(
            results_container['ed_fueltype_regs_yh'],
            lookups,
            os.path.join(
                result_paths['data_results_PDF'],
                'y_fueltypes_all_enduses.pdf'))

    # ----------
    # Plot seasonal typical load profiles
    # Averaged load profile per daytpe for a region
    # ----------

    # ------------------------------------
    # Load factors per fueltype and region
    # ------------------------------------
    if plot_crit['plot_lf'] :
        for fueltype_str, fueltype_int in lookups['fueltypes'].items():
            '''fig_lf.plot_seasonal_lf(
                fueltype_int,
                fueltype_str,
                results_container['load_factor_seasons'],
                reg_nrs,
                os.path.join(
                    result_paths['data_results_PDF'],
                    'lf_seasonal_{}.pdf'.format(fueltype_str)))'''

            '''fig_lf.plot_lf_y(
                fueltype_int,
                fueltype_str,
                results_container['reg_load_factor_yd'],
                reg_nrs,
                os.path.join(
                    result_paths['data_results_PDF'], 'lf_yd_{}.pdf'.format(fueltype_str)))'''

            # reg_load_factor_yd = max daily value / average annual daily value
            fig_lf.plot_lf_y(
                fueltype_int,
                fueltype_str,
                results_container['reg_load_factor_y'],
                reg_nrs,
                os.path.join(
                    result_paths['data_results_PDF'],
                    'lf_y_{}.pdf'.format(fueltype_str)))

    # --------------
    # Fuel week of base year
    # ----------------
    if plot_crit['plot_week_h']:
        fig_fuels_enduses_week.run(
            results_resid=results_container['ed_fueltype_regs_yh'],
            lookups=lookups,
            hours_to_plot=range(7*24),
            year_to_plot=2015,
            fig_name=os.path.join(result_paths['data_results_PDF'], "tot_all_enduse03.pdf"))

    # ------------------------------------
    # Plot averaged per season and fueltype
    # ------------------------------------
    if plot_crit['plot_averaged_season_fueltype']:
        for year in results_container['av_season_daytype_cy'].keys():
            for fueltype_int in results_container['av_season_daytype_cy'][year].keys():

                fueltype_str = tech_related.get_fueltype_str(
                    lookups['fueltypes'], fueltype_int)

                fig_load_profile_dh_multiple.run(
                    path_fig_folder=result_paths['data_results_PDF'],
                    path_plot_fig=os.path.join(
                        result_paths['data_results_PDF'],
                        'season_daytypes_by_cy_comparison__{}__{}.pdf'.format(year, fueltype_str)),
                    calc_av_lp_modelled=results_container['av_season_daytype_cy'][year][fueltype_int],  # current year
                    calc_av_lp_real=results_container['av_season_daytype_cy'][base_yr][fueltype_int], # base year
                    calc_lp_modelled=results_container['season_daytype_cy'][year][fueltype_int],        # current year
                    calc_lp_real=results_container['season_daytype_cy'][base_yr][fueltype_int],       # base year
                    plot_peak=True,
                    plot_all_entries=False,
                    plot_max_min_polygon=True,
                    plotshow=False,
                    plot_radar=plot_crit['plot_radar_seasonal'],
                    max_y_to_plot=120,
                    fueltype_str=fueltype_str,
                    year=year)

    # ---------------------------------
    # Plot hourly peak loads over time for different fueltypes
    # --------------------------------
    if plot_crit['plot_h_peak_fueltypes']:

        fig_fuels_peak_h.run(
            results_container['ed_fueltype_regs_yh'],
            lookups,
            os.path.join(
                result_paths['data_results_PDF'],
                'fuel_fueltypes_peak_h.pdf'))

    print("finisthed plotting")
    return
