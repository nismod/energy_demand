"""This scripts reads the national electricity data for the base year"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_basic import unit_conversions
from energy_demand.scripts_technologies import diffusion_technologies as diffusion

def get_month_from_string(month_string):
    """Convert string month to int month with Jan == 1
    """
    if month_string == 'Jan':
        month_int = 1
    elif month_string == 'Feb':
        month_int = 2
    elif month_string == 'Mar':
        month_int = 3
    elif month_string == 'Apr':
        month_int = 4
    elif month_string == 'May':
        month_int = 5
    elif month_string == 'Jun':
        month_int = 6
    elif month_string == 'Jul':
        month_int = 7
    elif month_string == 'Aug':
        month_int = 8
    elif month_string == 'Sep':
        month_int = 9
    elif month_string == 'Oct':
        month_int = 10
    elif month_string == 'Nov':
        month_int = 11
    elif month_string == 'Dec':
        month_int = 12
    else:
        sys.exit("Could not convert string month to int month")

    return int(month_int)

def read_raw_elec_2015_data(path_to_csv):
    """Read in national electricity values provided in MW and convert to GWh

    Info
    -----
    Half hourly measurements are aggregated to hourly values

    Necessary data preparation: On 29 March and 25 Octobre there are 46 and 48 values because of the changing of the clocks
    The 25 Octobre value is omitted, the 29 March hour interpolated in the csv file
    """
    year = 2015
    total_MW = 0

    elec_data = np.zeros((365, 24))

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        hour = 0
        counter_half_hour = 0
        # Iterate rows
        for line in read_lines:

            month = get_month_from_string(line[0].split("-")[1])
            day = int(line[0].split("-")[0])

            # Get yearday
            yearday = date_handling.convert_date_to_yearday(year, month, day)

            if counter_half_hour == 1:
                counter_half_hour = 0

                # Sum value of first and second half hour
                hour_elec_demand = half_hour_demand + float(line[2]) 
                total_MW += hour_elec_demand

                # Convert MW to GWH (input is MW aggregated for two half
                # hourly measurements, therfore divide by 0.5)
                hour_elec_demand_gwh = unit_conversions.convert_mw_gwh(hour_elec_demand, 0.5)

                # Add to array
                #print(" sdf  {}  {}  {}  ".format(yearday, hour, hour_elec_demand_gwh))
                elec_data[yearday][hour] = hour_elec_demand_gwh

                hour += 1
            else:
                counter_half_hour += 1

                half_hour_demand = float(line[2])

            if hour == 24:
                hour = 0

    return elec_data

def compare_results(y_real_array, y_calculated_array, title_left):
    """Compare national electrictiy demand data with model results

    Info
    ----
    RMSE fit criteria : Lower values of RMSE indicate better fit
    https://stackoverflow.com/questions/17197492/root-mean-square-error-in-python
    """
    print("...compare elec results")
    def rmse(predictions, targets):
        """RMSE calculations
        """
        return np.sqrt(((predictions - targets) ** 2).mean())

    # Number of days to plot
    days_to_plot = list(range(0, 14)) + list(range(100, 114)) + list(range(200, 214)) + list(range(300, 314))

    nr_of_h_to_plot = len(days_to_plot) * 24

    x = range(nr_of_h_to_plot)

    y_real = []
    y_calculated = []

    for day in days_to_plot:
        for hour in range(24):
            y_real.append(y_real_array[day][hour])
            y_calculated.append(y_calculated_array[day][hour])

    # RMSE
    rmse_val = rmse(np.array(y_real), np.array(y_calculated))

    # plot points
    plt.plot(x, y_real, color='green', label='real') #'ro', markersize=1
    plt.plot(x, y_calculated, color='red', label='modelled') #'ro', markersize=1 

    plt.title('RMSE Value: {}'.format(rmse_val))
    plt.title(title_left, loc='left')
    #plt.title('Right Title', loc='right')
    plt.legend()

    plt.show()

def compare_peak(validation_elec_data_2015, peak_all_models_all_enduses_fueltype):
    """Compare Peak electricity day with calculated peak energy demand
    """
    print("...compare elec peak results")
    # -------------------------------
    # Find maximumg peak in real data
    # -------------------------------
    peak_day_real = np.zeros((24))

    max_h_year = 0
    max_day = "None"

    for day in range(365):
        max_h_day = np.max(validation_elec_data_2015[day])

        if max_h_day > max_h_year:
            max_h_year = max_h_day
            max_day = day

    print("Max Peak Day:                    " + str(max_day))
    print("max_h_year (real):               " + str(max_h_year))
    print("max_h_year (modelled):           " + str(np.max(peak_all_models_all_enduses_fueltype)))
    print("Fuel max peak day (real):        " + str(np.sum(validation_elec_data_2015[max_day])))
    print("Fuel max peak day (modelled):    " + str(np.sum(peak_all_models_all_enduses_fueltype)))
    # -------------------------------
    # Compare values
    # -------------------------------
    x = range(24)
    plt.plot(x, validation_elec_data_2015[max_day], color='green', label='real')
    plt.plot(x, peak_all_models_all_enduses_fueltype, color='red', label='modelled')

    plt.title("Peak day comparison", loc='left')
    plt.legend()
    plt.show()











def boxplots_month():
    """
    Thanks Josh Hemann for the example
    """

    # Generate some data from five different probability distributions,
    # each with different characteristics. We want to play with how an IID
    # bootstrap resample of the data preserves the distributional
    # properties of the original sample, and a boxplot is one visual tool
    # to make this assessment
    numDists = 5
    randomDists = ['Normal(1,1)', ' Lognormal(1,1)', 'Exp(1)', 'Gumbel(6,4)',
                'Triangular(2,9,11)']
    N = 500
    np.random.seed(0)
    norm = np.random.normal(1, 1, N)
    logn = np.random.lognormal(1, 1, N)
    expo = np.random.exponential(1, N)
    gumb = np.random.gumbel(6, 4, N)
    tria = np.random.triangular(2, 9, 11, N)

    # Generate some random indices that we'll use to resample the original data
    # arrays. For code brevity, just use the same random indices for each array
    bootstrapIndices = np.random.random_integers(0, N - 1, N)
    normBoot = norm[bootstrapIndices]
    expoBoot = expo[bootstrapIndices]
    gumbBoot = gumb[bootstrapIndices]
    lognBoot = logn[bootstrapIndices]
    triaBoot = tria[bootstrapIndices]

    data = [norm, normBoot, logn, lognBoot, expo, expoBoot, gumb, gumbBoot,
            tria, triaBoot]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.canvas.set_window_title('A Boxplot Example')
    plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

    bp = plt.boxplot(data, notch=0, sym='+', vert=1, whis=1.5)
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')

    # Add a horizontal grid to the plot, but make it very light in color
    # so we can use it for reading data values but not be distracting
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                alpha=0.5)

    # Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    ax1.set_title('Comparison of IID Bootstrap Resampling Across Five Distributions')
    ax1.set_xlabel('Distribution')
    ax1.set_ylabel('Value')

    # Now fill the boxes with desired colors
    boxColors = ['darkkhaki', 'royalblue']
    numBoxes = numDists*2
    medians = list(range(numBoxes))
    for i in range(numBoxes):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        boxCoords = list(zip(boxX, boxY))
        # Alternate between Dark Khaki and Royal Blue
        k = i % 2
        boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
        ax1.add_patch(boxPolygon)
        # Now draw the median lines back over what we just filled in
        med = bp['medians'][i]
        medianX = []
        medianY = []
        for j in range(2):
            medianX.append(med.get_xdata()[j])
            medianY.append(med.get_ydata()[j])
            plt.plot(medianX, medianY, 'k')
            medians[i] = medianY[0]
        # Finally, overplot the sample averages, with horizontal alignment
        # in the center of each box
        plt.plot([np.average(med.get_xdata())], [np.average(data[i])],
                color='w', marker='*', markeredgecolor='k')

    # Set the axes ranges and axes labels
    ax1.set_xlim(0.5, numBoxes + 0.5)
    top = 40
    bottom = -5
    ax1.set_ylim(bottom, top)
    xtickNames = plt.setp(ax1, xticklabels=np.repeat(randomDists, 2))
    plt.setp(xtickNames, rotation=45, fontsize=8)

    # Due to the Y-axis scale being different across samples, it can be
    # hard to compare differences in medians across the samples. Add upper
    # X-axis tick labels with the sample medians to aid in comparison
    # (just use two decimal places of precision)
    pos = np.arange(numBoxes) + 1
    upperLabels = [str(np.round(s, 2)) for s in medians]
    weights = ['bold', 'semibold']
    for tick, label in zip(range(numBoxes), ax1.get_xticklabels()):
        k = tick % 2
        ax1.text(pos[tick], top - (top*0.05), upperLabels[tick],
                horizontalalignment='center', size='x-small', weight=weights[k],
                color=boxColors[k])

    # Finally, add a basic legend
    plt.figtext(0.80, 0.08, str(N) + ' Random Numbers',
                backgroundcolor=boxColors[0], color='black', weight='roman',
                size='x-small')
    plt.figtext(0.80, 0.045, 'IID Bootstrap Resample',
                backgroundcolor=boxColors[1],
                color='white', weight='roman', size='x-small')
    plt.figtext(0.80, 0.015, '*', color='white', backgroundcolor='silver',
                weight='roman', size='medium')
    plt.figtext(0.815, 0.013, ' Average Value', color='black', weight='roman',
                size='x-small')

    plt.show()