""" These functions read in raw csv files to generate load functions """
import numpy as np
import os
import csv
import main_functions as mf
#import datetime
from datetime import date
import unittest

def read_in_non_residential_load_curves():
    """
    Folder with all csv files stored


    """
    # Dictionary: month, daytype, hour
    #
    # 0. Find what day it is (with date function). Then define daytype and month
    # 1. Calculate total demand of every day
    # 2. Assign percentag of total daily demand to each hour

    folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\Community'

    all_csv_in_folder = os.listdir(folder_path) # Get all files in folder
    print(all_csv_in_folder)


    # Initial dict
    dict_results = np.zeros((2, 12, 24), dtype = float) # datyape, month, hours


    # Itreateu folder
    for path_csv_file in all_csv_in_folder:
        path_csv_file = os.path.join(folder_path, path_csv_file)
        print("path: " + str(path_csv_file))

        # Read csv file
        with open(path_csv_file, 'r') as csv_file:               # Read CSV file
            read_lines = csv.reader(csv_file, delimiter=',')   # Read line
            _headings = next(read_lines)                      # Skip first row
            #print("read_lines: " + str(read_lines))

            # Iterate day
            for row in read_lines:
                #print("RO " + str(row))

                #DO SOME TEST TO CHECK FIL FILE CORRECT
                if len(row) != 49:
                    # Skip row
                    continue
                #assert len(row) == 49 #one date plus 48 half hourly data

                day = int(row[0].split("/")[0])
                month = int(row[0].split("/")[1])
                year = int(row[0].split("/")[2])

                date_row = date(year, month, day)

                # Daytype
                daytype = mf.get_weekday_type(date_row)

                # Month Python
                month_python = month - 1 

                # Convert all values except date into float values
                row[1:] = map(float, row[1:])
                # Total daily sum
                daily_sum = sum(row[1:])
                #print("dailyUM: " + str(daily_sum))

                # Iterate hours
                cnt = 0
                h_day = 0
                control_sum = 0

                for half_hour_val in row[1:]: # Skip date
                    cnt += 1
                    if cnt == 2:
                        control_sum += (first_half_hour + half_hour_val)
                        dict_results[daytype][month_python][h_day] = (first_half_hour + half_hour_val) * (100 / daily_sum)
                        cnt = 0
                        h_day += 1

                    first_half_hour = half_hour_val #must be at this position
                
                # Check if 100 %
                assertions = unittest.TestCase('__init__')
                assertions.assertAlmostEqual(control_sum, daily_sum, places=7, msg=None, delta=None)

    return dict_results

out_array = read_in_non_residential_load_curves()


import matplotlib.pyplot as plt


y = []

for row in out_array[0][0]: # daytype = 0, January = 0 
    y.append(list(row))

x = range(len(y))

print("Number of lines: " + str(len(y)))

for i in range(len(y)):
    plt.plot(x, [pt[i] for pt in y])

plt.show()