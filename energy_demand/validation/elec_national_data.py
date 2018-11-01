"""This scripts reads the national electricity data for the base year"""
import os
import csv
import logging
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

from energy_demand.basic import date_prop
from energy_demand.basic import conversions
from energy_demand.plotting import basic_plot_functions
from energy_demand.basic import basic_functions
from energy_demand.plotting import plotting_styles

def read_raw_elec_2015(path_to_csv, year=2015):
    """Read in national electricity values provided
    in MW and convert to GWh

    Arguments
    ---------
    path_to_csv : str
        Path to csv file
    year : int
        Year of data

    Returns
    -------
    elec_data_indo : array
        Hourly INDO electricity in GWh (INDO - National Demand)
    elec_data_itsdo : array
        Hourly ITSDO electricity in GWh (Transmission System Demand)

    Note
    -----
    Half hourly measurements are aggregated to hourly values

    Necessary data preparation: On 29 March and 25 Octobre
    there are 46 and 48 values because of the changing of the clocks
    The 25 Octobre value is omitted, the 29 March hour interpolated
    in the csv file

    Source
    ------
    http://www2.nationalgrid.com/uk/Industry-information/electricity-transmission-operational-data/
    For more information on INDO and ISTDO see DemandData Field Descriptions file:
    http://www2.nationalgrid.com/WorkArea/DownloadAsset.aspx?id=8589934632

    National Demand is calculated as a sum
    of generation based on National Grid
    operational generation metering
    """
    elec_data_indo = np.zeros((365, 24), dtype="float")
    elec_data_itsdo = np.zeros((365, 24), dtype="float")

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines)

        hour = 0
        counter_half_hour = 0

        for line in read_lines:
            month = basic_functions.get_month_from_string(line[0].split("-")[1])
            day = int(line[0].split("-")[0])

            # Get yearday
            yearday = date_prop.date_to_yearday(year, month, day)

            if counter_half_hour == 1:
                counter_half_hour = 0

                # Sum value of first and second half hour
                hour_elec_demand_INDO = half_hour_demand_indo + float(line[2])
                hour_elec_demand_ITSDO = half_hour_demand_itsdo + float(line[4])

                # Convert MW to GWH (input is MW aggregated for two half
                # hourly measurements, therfore divide by 0.5)
                elec_data_indo[yearday][hour] = conversions.mw_to_gwh(hour_elec_demand_INDO, 0.5)
                elec_data_itsdo[yearday][hour] = conversions.mw_to_gwh(hour_elec_demand_ITSDO, 0.5)

                hour += 1
            else:
                counter_half_hour += 1

                half_hour_demand_indo = float(line[2]) # INDO - National Demand
                half_hour_demand_itsdo = float(line[4]) # Transmission System Demand

            if hour == 24:
                hour = 0

    return elec_data_indo, elec_data_itsdo

def compare_results(
        name_fig,
        path_result,
        y_factored_indo,
        y_calculated_array,
        title_left,
        days_to_plot,
        plot_crit=False
    ):
    """Compare national electrictiy demand data with model results

    Note
    ----
    RMSE fit criteria : Lower values of RMSE indicate better fit
    https://stackoverflow.com/questions/17197492/root-mean-square-error-in-python

    https://matplotlib.org/examples/lines_bars_and_markers/marker_fillstyle_reference.html
    """
    logging.debug("...compare elec results")
    nr_of_h_to_plot = len(days_to_plot) * 24

    x_data = range(nr_of_h_to_plot)

    y_real_indo_factored = []
    y_calculated_list = []
    y_diff_p = []
    y_diff_abs = []

    for day in days_to_plot:
        for hour in range(24):
            y_calculated_list.append(y_calculated_array[day][hour])
            y_real_indo_factored.append(y_factored_indo[day][hour])

            # Calculate absolute differences
            abs_diff = abs(y_factored_indo[day][hour] - y_calculated_array[day][hour])
            y_diff_abs.append(abs_diff)

            # Calculate difference in percent
            if abs_diff == 0:
                p_diff = 0
            else:
                p_diff = (100 / y_factored_indo[day][hour]) * y_calculated_array[day][hour] - 100

            y_diff_p.append(p_diff)

    # -------------
    # RMSE
    # -------------
    rmse_val_corrected = basic_functions.rmse(
        np.array(y_real_indo_factored),
        np.array(y_calculated_list))

    # ----------
    # Standard deviation
    # ----------
    standard_dev_real_modelled = np.std(y_diff_p)       # Differences in %
    standard_dev_real_modelled_abs = np.std(y_diff_abs) # Absolute differences 

    logging.info(
        "Standard deviation given as percentage: " + str(standard_dev_real_modelled))
    logging.info(
        "Standard deviation given as GW:         " + str(standard_dev_real_modelled_abs))

    # ---------
    # R squared
    # ---------
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        y_real_indo_factored,
        y_calculated_list)

    # ----------
    # Plot residuals
    # ----------
    try:
        plot_residual_histogram(
            y_diff_p, path_result, "residuals_{}".format(name_fig))
    except:
        pass

    # ----------
    # Plot figure
    # ----------
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(22, 8))

    # smooth line
    x_data_smoothed, y_real_indo_factored_smoothed = basic_plot_functions.smooth_data(
        x_data, y_real_indo_factored, num=40000)

    # plot points
    plt.plot(
        x_data_smoothed,
        y_real_indo_factored_smoothed,
        label='indo_factored',
        linestyle='-',
        linewidth=0.5,
        fillstyle='full',
        color='black')

    # smooth line
    x_data_smoothed, y_calculated_list_smoothed = basic_plot_functions.smooth_data(
        x_data, y_calculated_list, num=40000)

    plt.plot(
        x_data_smoothed,
        y_calculated_list_smoothed,
        label='model',
        linestyle='--',
        linewidth=0.5,
        fillstyle='full',
        color='blue')

    plt.xlim([0, 8760])
    plt.margins(x=0)
    plt.axis('tight')

    # --------------------------------------
    # Label x axis in dates
    # --------------------------------------
    major_ticks_days, major_ticks_labels = get_date_strings(
        days_to_plot,
        daystep=1)

    plt.xticks(major_ticks_days, major_ticks_labels)

    # ----------
    # Labelling
    # ----------
    font_additional_info = plotting_styles.font_info(size=4)

    plt.title(
        'RMSE: {} Std_dev_% {} (+-{} GW) R_2: {}'.format(
            round(rmse_val_corrected, 3),
            round(standard_dev_real_modelled, 3),
            round(standard_dev_real_modelled_abs, 3),
            round(r_value, 3)),
        fontdict=font_additional_info,
        loc='right')

    plt.title(title_left, loc='left')

    plt.xlabel("hour", fontsize=10)
    plt.ylabel("uk elec use [GW] for {}".format(title_left), fontsize=10)

    plt.legend(frameon=False)

    plt.savefig(os.path.join(path_result, name_fig))

    if plot_crit:
        plt.show()
    plt.close()

def compare_peak(
        name_fig,
        path_result,
        real_elec_2015_peak,
        modelled_peak_dh,
        peak_day
    ):
    """Compare peak electricity day with calculated peak energy demand

    Arguments
    ---------
    name_fig : str
        Name of figure
    local_paths : dict
        Paths
    real_elec_2015_peak : array
        Real data of peak day
    modelled_peak_dh : array
        Modelled peak day
    """
    logging.debug("...compare elec peak results")

    real_elec_peak = np.copy(real_elec_2015_peak)
    # -------------------------------
    # Compare values
    # -------------------------------
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(8, 8))

    # smooth line
    x_smoothed, y_modelled_peak_dh_smoothed = basic_plot_functions.smooth_data(range(24), modelled_peak_dh, num=500)

    plt.plot(
        x_smoothed,
        y_modelled_peak_dh_smoothed,
        color='blue',
        linestyle='--',
        linewidth=0.5,
        label='model')

    x_smoothed, real_elec_peak_smoothed = basic_plot_functions.smooth_data(
        range(24), real_elec_peak, num=500)

    plt.plot(
        x_smoothed,
        real_elec_peak_smoothed,
        color='black',
        linestyle='-',
        linewidth=0.5,
        label='validation')

    #raise Exception
    # Calculate hourly differences in %
    diff_p_h = np.round((100 / real_elec_peak) * modelled_peak_dh, 1)

    # Calculate maximum difference
    max_h_real = np.max(real_elec_peak)
    max_h_modelled = np.max(modelled_peak_dh)

    max_h_diff = round((100 / max_h_real) * max_h_modelled, 2)
    max_h_diff_gwh = round((abs(100 - max_h_diff)/100) * max_h_real, 2)

    # Y-axis ticks
    plt.xlim(0, 23)
    plt.yticks(range(0, 60, 10))

    # because position 0 in list is 01:00, the labelling starts with 1
    plt.xticks([0, 5, 11, 17, 23], [1, 6, 12, 18, 24]) #ticks, labels

    plt.legend(frameon=False)

    # Labelling
    date_yearday = date_prop.yearday_to_date(2015, peak_day)
    plt.title("peak comparison {}".format(date_yearday))

    plt.xlabel("h (max {} ({} GWH)".format(max_h_diff, max_h_diff_gwh))
    plt.ylabel("uk electrictiy use [GW]")

    plt.text(
        5, #position
        5, #position
        diff_p_h,
        fontdict={
            'family': 'arial',
            'color': 'black',
            'weight': 'normal',
            'size': 4})

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(os.path.join(path_result, name_fig))
    plt.close()

def compare_results_hour_boxplots(
        name_fig,
        path_result,
        data_real,
        data_calculated
    ):
    """Calculate differences for everyhour and plot according
    to hour for the full year
    """
    data_h_full_year = {}
    for i in range(24):
        data_h_full_year[i] = []

    for yearday_python in range(365):
        for hour in range(24):

            # Differenc in % of real value
            diff_percent = (100 / data_real[yearday_python][hour]) * data_calculated[yearday_python][hour]

            # Add differene to list of specific hour
            data_h_full_year[hour].append(diff_percent)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Add a horizontal grid to the plot, but make it very light in color so we
    # can use it for reading data values but not be distracting
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax.axhline(y=100, xmin=0, xmax=3, c="red", linewidth=1, zorder=0)

    diff_values = []
    for hour in range(24):
        diff_values.append(np.asarray(data_h_full_year[hour]))

    ax.boxplot(diff_values)

    plt.xticks(range(1, 25), range(24))

    plt.xlabel("hour")
    plt.ylabel("Modelled electricity difference (real-modelled) [%]")

    plt.savefig(os.path.join(path_result, name_fig))
    plt.close()

def plot_residual_histogram(values, path_result, name_fig):
    """Plot residuals as histogram and test for normal distribution

    https://matplotlib.org/1.2.1/examples/pylab_examples/histogram_demo.html
    https://stackoverflow.com/questions/22179119/normality-test-of-a-distribution-in-python
    """
    plt.figure(facecolor="white")

    # Sort according to size
    values.sort()

    # the histogram of the data
    n, bins, patches = plt.hist(
        values,
        50,
        normed=1,
        facecolor='grey')

    # ------------------
    # Plot normal distribution
    # ------------------
    mu = np.average(values)
    sigma = np.std(values)
    plt.plot(
        bins,
        mlab.normpdf(bins, mu, sigma),
        color='r')

    # -----------
    # Test for normal distribution
    # https://stackoverflow.com/questions/12838993/scipy-normaltest-how-is-it-used
    # http://www.socscistatistics.com/pvalues/chidistribution.aspx
    # http://stattrek.com/chi-square-test/goodness-of-fit.aspx?Tutorial=AP
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html
    # -----------
    chi_squared, p_value = stats.normaltest(values)

    # ---------------
    # plot histogram
    # ---------------
    font_additional_info = plotting_styles.font_info()

    plt.xlabel('Smarts')
    plt.ylabel('Probability')
    plt.title("Residual distribution (chi_squared: {}  p_value:  {}".format(
        round(chi_squared, 4),
        round(p_value, 4)),
              fontsize=10,
              fontdict=font_additional_info,
              loc='right')

    plt.savefig(os.path.join(path_result, name_fig))

def get_date_strings(days_to_plot, daystep):
    """Calculate date and position for range input of yeardays

    Arguments
    ---------
    days_to_plot : list
        List with yeardays to plot
    daystep : int
        Intervall of days to assign label

    Return
    -------
    ticks_position : list
        Hourly ticks position
    major_ticks_labels : list
        Ticks labels
    """
    ticks_position, ticks_labels = [], []

    cnt = 0
    cnt_daystep = 1

    for day in days_to_plot:
        str_date = str(date_prop.yearday_to_date(2015, day))
        str_date_short = str_date[5:]

        # Because 0 posit in hour list is 01:00, substract minus one hour
        yearhour = (cnt * 24) - 1

        if daystep == cnt_daystep:
            ticks_labels.append(str_date_short)
            ticks_position.append(yearhour)

            cnt_daystep = 1
            cnt += 1
        else:
            cnt_daystep += 1
            cnt += 1

    return ticks_position, ticks_labels
