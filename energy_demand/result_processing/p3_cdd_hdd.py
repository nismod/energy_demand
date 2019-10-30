"""Read HDD and CDD
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import pylab
import numpy as np

statistics_to_print = []

path_same = "C:/HIRE/_results_hdd_cdd/same_weather"
path_diff = "C:/HIRE/_results_hdd_cdd/diff_weather"

for path in [path_same, path_diff]:
    files = os.listdir(path)
    all_scenarios = []

    hdd_2050 = []
    cdd_2050 = []
    hdd_2020 = []
    cdd_2020 = []

    for file in files:
        f = open(os.path.join(path, file), "r")
        number = float(f.read())
        if file.startswith("ccd") and file.endswith("2020.txt"):
            cdd_2020.append(number)
        if file.startswith("hdd") and file.endswith("2020.txt"):
            hdd_2020.append(number)
        if file.startswith("ccd") and file.endswith("2050.txt"):
            cdd_2050.append(number)
        if file.startswith("hdd") and file.endswith("2050.txt"):
            hdd_2050.append(number)

    print("----  {}  ----".format(path))
    print(" ")
    print("SUM")
    print("cdd_2020: {}".format(sum(cdd_2020)))
    print("cdd_2050: {}".format(sum(cdd_2050)))
    print("--")
    print("hdd_2020: {}".format(sum(hdd_2020)))
    print("hdd_2050: {}".format(sum(hdd_2050)))

    print("MIN")
    print("cdd_2020: {}".format(min(cdd_2020)))
    try:
        print("cdd_2050: {}".format(min(cdd_2050)))
    except:
        print("cdd_2050: NICHTS")
    print("--")
    print("hdd_2020: {}".format(min(hdd_2020)))
    try:
        print("hdd_2050: {}".format(min(hdd_2050)))
    except:
        print("hdd_2050: NICHTS")

    print("MAX")
    print("cdd_2020: {}".format(max(cdd_2020)))
    try:
        print("cdd_2050: {}".format(max(cdd_2050)))
    except:
        print("cdd_2050: NICHTS")
    print("--")
    print("hdd_2020: {}".format(max(hdd_2020)))
    try:
        print("hdd_2050: {}".format(max(hdd_2050)))
    except:
        print("hdd_2050: NICHTS")
    print(" ")

    print("Average")
    print("cdd_2020: {}".format(np.mean(cdd_2020)))
    print("cdd_2050: {}".format(np.mean(cdd_2050)))
    print("--")
    print("hdd_2020: {}".format(np.mean(hdd_2020)))
    print("hdd_2050: {}".format(np.mean(hdd_2050)))
    print(" ")

print("__________FINISH___________")