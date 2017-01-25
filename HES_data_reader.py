# Imports
import math as m 
import sys, os
import pandas as pd
import csv
import numpy as np
from operator import itemgetter
print("Finished imports from HES_data_reader.py")

# -----------------------------
# This file imports HES data...
# 
# -----------------------------

# Paths
pathToAllCSVFilesFolder = r'C:\_Data\HES\UKDA-7874-csv\csv\FolderAllFiles'
pathwriteOutAggregatedCSVFile = r'C:\_Data\HES\UKDA-7874-csv\csv\summaryFile.csv'
pathwriteOutTemperatureCSVFile = r'C:\_Data\HES\UKDA-7874-csv\csv\TemperatureFile.csv'
pathToHouseholdINfo = r'C:\_Data\HES\UKDA-7874-csv\csv\anonhes\ipsos-anonymised-corrected_310713.csv'


# appliance_types_codes.csv  [Code, Name]
appliance_types_codes = [[1001, 'Cold appliances'], [1002, 'Cooking'], [1003, 'Lighting'], [1004, 'Audiovisual'], [1005, 'ICT'], [1006, 'Washing/drying/dishwasher'], [1007, 'Water heating'], [1008, 'Heating'], [1009, 'Other'], [1010, 'Unknown'], [1011, 'Sockets'], [1012, 'Mains'], [1013, 'Showers']]

# appliance_codes.csv
codes_appliance = [[0, 'upright freezer 1'], [1, 'upright freezer 2'], [2, 'chest freezer 1'], [3, 'chest freezer 2'], [4, 'fridge 1'], [5, 'fridge 2'], [6, 'fridge freezer 1'], [7, 'fridge freezer 2'], [8, 'wine cooler 1'], [9, 'fridge+freezer 1'], [10, 'Unknown kitchen'], [11, 'To be defined 11'], [12, 'To be defined 12'], [13, 'To be defined 13'], [14, 'To be defined 14'], [15, 'Unknown'], [16, 'cooker 1'], [17, 'kettle 1'], [18, 'microwave 1'], [19, 'oven 1'], [20, 'toaster 1'], [21, 'frier 1'], [22, 'hob 1'], [23, 'microwave+grill 1'], [24, 'bread maker 1'], [25, 'coffee maker 1'], [26, 'kettle 2'], [27, 'oven+cooker 1'], [28, 'food mixer 1'], [29, 'cooker 2'], [30, 'fryer 1'], [31, 'grill 1'], [32, 'extractor hood 1'], [33, 'coffee maker 2'], [34, 'microwave 2'], [35, 'food steamer 1'], [36, 'bottle warmer 1'], [37, 'toaster 2'], [38, 'cooker 3'], [39, 'hob 2'], [40, 'oven 2'], [41, 'Other cooking'], [42, 'Slow cooker 1'], [43, 'To be defined 43'], [44, 'To be defined 44'], [45, 'To be defined 45'], [46, 'To be defined 46'], [47, 'Spin Dryer 1'], [48, 'dishwasher 1'], [49, 'tumble dryer 1'], [50, 'washing/drying machine 1'], [51, 'washing machine 1'], [52, 'tumble dryer 2'], [53, 'washing/drying machine 2'], [54, 'tv 5'], [55, 'tv crt 2'], [56, 'tv crt 3'], [57, 'dvd+xbox360 1'], [58, 'aerial 1'], [59, 'dvd+vcr 2'], [60, 'audiovisual site 2'], [61, 'audiovisual site 3'], [62, 'audiovisual site 4'], [63, 'video center 1'], [64, 'central heating 1'], [65, 'heater 1'], [66, 'heater 2'], [67, 'heater 3'], [68, 'heater 4'], [69, 'heater 5'], [70, 'shower 1'], [71, 'water heater 1'], [72, 'floor heating 1'], [73, 'shower 2'], [74, 'hot tub 1'], [75, 'circulation pump 1'], [76, 'heater 6'], [77, 'air conditionning 1'], [78, 'To be defined 78'], [79, 'To be defined 79'], [80, 'audiovisual site 1'], [81, 'dvd 1'], [82, 'dvd recorder 1'], [83, 'fax/printer 1'], [84, 'hi-fi 1'], [85, 'ps2 1'], [86, 'xbox360 1'], [87, 'game cube 1'], [88, 'wii 1'], [89, 'xbox 1'], [90, 'ps3 1'], [91, 'game console 1'], [92, 'game console+hifi 1'], [93, 'set top box 1'], [94, 'sky box 1'], [95, 'tv 1'], [96, 'tv crt 1'], [97, 'tv lcd 1'], [98, 'tv plasma 1'], [99, 'tv+vcr 1'], [100, 'tv+dvd 1'], [101, 'tv+settopbox 1'], [102, 'vcr 1'], [103, 'dvd+vcr 1'], [104, 'tv+vcr+dvd 1'], [105, 'tv+dvd+set top box 1'], [106, 'blueray player 1'], [107, 'av receiver 1'], [108, 'home cinema sound 1'], [109, 'cd player 1'], [110, 'radio 1'], [111, 'tv booster 1'], [112, 'tv+vcr 2'], [113, 'tv 2'], [114, 'tv 3'], [115, 'tv lcd 2'], [116, 'tv+dvd 2'], [117, 'dvd 2'], [118, 'game console 2'], [119, 'set top box 2'], [120, 'tv lcd 3'], [121, 'vcr 2'], [122, 'vcr 3'], [123, 'tv+dvd+hifi 1'], [124, 'dvd/vcr+settopbox+router 1'], [125, 'hi-fi 2'], [126, 'set top box 3'], [127, 'tv 4'], [128, 'laptop 1'], [129, 'desktop 1'], [130, 'monitor+printer 1'], [131, 'monitor 1'], [132, 'printer 1'], [133, 'router 1'], [134, 'computer equipment 1'], [135, 'multifunction printer 1'], [136, 'wordprocessor 1'], [137, 'computer site 1'], [138, 'scanner 1'], [139, 'speakers 1'], [140, 'modem 1'], [141, 'desktop 2'], [142, 'monitor+printer 2'], [143, 'monitor 2'], [144, 'printer 2'], [145, 'laptop 2'], [146, 'laptop 3'], [147, 'monitor crt 1'], [148, 'harddrive 1'], [149, 'media player 1'], [150, 'ups 1'], [151, 'harddrive 2'], [152, 'multifunction printer + router 1'], [153, 'computer site 2'], [154, 'router 2'], [155, 'multifunction printer 2'], [156, 'multifunction printer 3'], [157, 'computer site 3'], [158, 'computer site 4'], [159, 'Not monitored'], [160, 'light 1'], [161, 'light 2'], [162, 'light 3'], [163, 'light 4'], [164, 'light 5'], [165, 'light 6'], [166, 'light 7'], [167, 'light 8'], [168, 'light 9'], [169, 'light 10'], [170, 'light 11'], [171, 'light 12'], [172, 'light distribution 1'], [173, 'light distribution 2'], [174, 'light distribution 3'], [175, 'light distribution 4'], [176, 'hair dryer 1'], [177, 'hair straightener 1'], [178, 'immersion heater 1'], [179, 'picture frame 1'], [180, 'hair dryer+hair straightener 1'], [181, 'iron 1'], [182, 'trouser press 1'], [183, 'vaccum cleaner 1'], [184, 'aviary 1'], [185, 'clock radio 1'], [186, 'vaccum cleaner 2'], [187, 'sunbed 1'], [188, 'charger 1'], [189, 'unknown appliance(s) previously listed as garage 1'], [190, 'aquarium 1'], [191, 'pond pump 1'], [192, 'alarm 1'], [193, 'electric chair 1'], [194, 'alarm+other 1'], [195, 'fan 1'], [196, 'electric blanket 1'], [197, 'door bell 1'], [198, 'organ 1'], [199, 'sewing machine 1'], [200, 'massage bed 1'], [201, 'other 1'], [202, 'paper shredder 1'], [203, 'hair dryer 2'], [204, 'other 2'], [205, 'sewing machine 2'], [206, 'sewing machine 3'], [207, 'steriliser 1'], [208, 'sockets 1'], [209, 'sockets 2'], [210, 'sockets 3'], [211, 'sockets 4'], [212, 'sockets 5'], [213, 'sockets 6'], [214, 'sockets 7'], [215, 'sockets 8'], [216, 'sockets 9'], [217, 'sockets 10'], [218, 'vaccum cleaner 3'], [219, 'light distribution 5'], [220, 'immersion heater 2'], [221, 'light distribution 6'], [222, 'sockets 11'], [223, 'other 3'], [224, 'baby monitor 1'], [225, 'fire 1'], [226, 'steriliser 2'], [227, 'vivarium 1'], [228, 'vivarium 2'], [229, 'yoghurt maker 1'], [230, 'smoke detectors 1'], [231, 'aquarium 2'], [232, 'dehumidifier 1'], [233, 'cordless phone 1'], [234, 'motorhome 1'], [235, 'jacuzzi 1'], [236, 'aquarium 3'], [237, 'aquarium 4'], [238, 'electric blanket 2'], [239, 'iron 2'], [240, 'main 1'], [241, 'main 2'], [242, 'audiovisual equipment 1'], [243, 'tv+settopbox 1'], [244, 'audiovisual site 5'], [245, 'audiovisual site 6'], [246, 'video sender 1'], [247, 'cordless phone 2'], [248, 'fan 2'], [249, 'fan 3'], [250, 'fan 4'], [251, 'Outside T degrees 1'], [252, 'Inside T degrees 1'], [253, 'Inside T degrees 2'], [254, 'Inside T degrees 3'], [255, 'Inside T degrees 4']]

# make dictionary
listA, listB = [],[]
for i in codes_appliance:
    listA.append(i[0])
    listB.append(i[1])
dict_list = zip(listA, listB)
appliance_types_codes_Dictionary = dict(dict_list)


#ipsos-anonymised-corrected_310713.csv [ApplianceCode, GroupCode]
appliance_types = [[0, 1001], [1, 1001], [2, 1001], [3, 1001], [4, 1001], [5, 1001], [6, 1001], [7, 1001], [8, 1001], [9, 1001], [10, 1001], [15, 1010], [16, 1002], [17, 1002], [18, 1002], [19, 1002], [20, 1002], [21, 1002], [22, 1002], [23, 1002], [24, 1002], [25, 1002], [26, 1002], [27, 1002], [28, 1002], [29, 1002], [30, 1002], [31, 1002], [32, 1002], [33, 1002], [34, 1002], [35, 1002], [36, 1002], [37, 1002], [38, 1002], [39, 1002], [40, 1002], [41, 1002], [42, 1002], [47, 1006], [48, 1006], [49, 1006], [50, 1006], [51, 1006], [52, 1006], [53, 1006], [54, 1004], [55, 1004], [56, 1004], [57, 1004], [58, 1004], [59, 1004], [60, 1004], [61, 1004], [62, 1004], [63, 1004], [64, 1008], [65, 1008], [66, 1008], [67, 1008], [68, 1008], [69, 1008], [70, 1013], [71, 1007], [72, 1008], [73, 1013], [74, 1007], [75, 1008], [76, 1008], [77, 1009], [80, 1004], [81, 1004], [82, 1004], [83, 1005], [84, 1004], [85, 1004], [86, 1004], [87, 1004], [88, 1004], [89, 1004], [90, 1004], [91, 1004], [92, 1004], [93, 1004], [94, 1004], [95, 1004], [96, 1004], [97, 1004], [98, 1004], [99, 1004], [100, 1004], [101, 1004], [102, 1004], [103, 1004], [104, 1004], [105, 1004], [106, 1004], [107, 1004], [108, 1004], [109, 1004], [110, 1004], [111, 1004], [112, 1004], [113, 1004], [114, 1004], [115, 1004], [116, 1004], [117, 1004], [118, 1004], [119, 1004], [120, 1004], [121, 1004], [122, 1004], [123, 1004], [124, 1004], [125, 1004], [126, 1004], [127, 1004], [128, 1005], [129, 1005], [130, 1005], [131, 1005], [132, 1005], [133, 1005], [134, 1005], [135, 1005], [136, 1005], [137, 1005], [138, 1005], [139, 1005], [140, 1005], [141, 1005], [142, 1005], [143, 1005], [144, 1005], [145, 1005], [146, 1005], [147, 1005], [148, 1005], [149, 1005], [150, 1005], [151, 1005], [152, 1005], [153, 1005], [154, 1005], [155, 1005], [156, 1005], [157, 1005], [158, 1005], [159, 1010], [160, 1003], [161, 1003], [162, 1003], [163, 1003], [164, 1003], [165, 1003], [166, 1003], [167, 1003], [168, 1003], [169, 1003], [170, 1003], [171, 1003], [172, 1003], [173, 1003], [174, 1003], [175, 1003], [176, 1009], [177, 1009], [178, 1007], [179, 1009], [180, 1009], [181, 1009], [182, 1009], [183, 1009], [184, 1009], [185, 1009], [186, 1009], [187, 1009], [188, 1009], [189, 1009], [190, 1009], [191, 1009], [192, 1009], [193, 1009], [194, 1009], [195, 1009], [196, 1009], [197, 1009], [198, 1009], [199, 1009], [200, 1009], [201, 1009], [202, 1009], [203, 1009], [204, 1009], [205, 1009], [206, 1009], [207, 1009], [208, 1011], [209, 1011], [210, 1011], [211, 1011], [212, 1011], [213, 1011], [214, 1011], [215, 1011], [216, 1011], [217, 1011], [218, 1009], [219, 1003], [220, 1007], [221, 1003], [222, 1011], [223, 1009], [224, 1009], [225, 1009], [226, 1009], [227, 1009], [228, 1009], [229, 1002], [230, 1009], [231, 1009], [232, 1009], [233, 1009], [234, 1009], [235, 1009], [236, 1009], [237, 1009], [238, 1009], [239, 1009], [240, 1012], [241, 1012], [242, 1004], [243, 1004], [244, 1004], [245, 1004], [246, 1004], [247, 1009], [248, 1009], [249, 1009], [250, 1009]]

# make dictionary
listA, listB = [],[]
for i in appliance_types:
    listA.append(i[0])
    listB.append(i[1])
dict_list = zip(listA, listB)
appliance_types_Dictionary = dict(dict_list)

# -------------------------------------------------------------------
# Read in Household Properties (ipsos-anonymised-corrected_310713.csv)
# -------------------------------------------------------------------
with open(pathToHouseholdINfo, 'rb') as csvfile:
    HOUSEHOLD_LIST = []
    LINEREAD = csv.reader(csvfile, delimiter=',')

    # Headings
    for row in LINEREAD:
        colum_headings = row
        break

    # Rows
    for row in LINEREAD:
        HOUSEHOLD_LIST.append(row)

HOUSEHOLD_ARRAY = np.array(HOUSEHOLD_LIST)                              # Convert list into array
HOUSEHOLD_ARRAY = pd.DataFrame(HOUSEHOLD_ARRAY, columns=colum_headings) # Assing column names 
#df.to_csv('df.csv', index=True, header=True, sep=' ')                  

'''# -------------------------------------------------------------------------------------------
# Generate Table summarising appliance_types_codes, appliance_codes and ipsos-anonymised-corrected_310713
# -------------------------------------------------------------------------------------------
appliance_Information = []

for i in appliance_types:

    # Get appliance description
    for b in codes_appliance:
        if i[0] == b[0]:
            code_appliance = b[1]
            break
    
    # Get appliance type
    for c in appliance_types_codes:
        if i[1] == c[0]:
            appliance_type = c[1]
            break
    
    appliance_Information.append([i[0], i[1], code_appliance, appliance_type]) # e.g. [246, 1004, 'video sender 1', 'Audiovisual']

    #scrap
    print appliance_Information
    break
'''

# -------------------------------------------------------------------------------------------
# Get all csv files in folder and aggregate and reout out all data in the following form:

# aggregatedDict = [[HOUSEHOLD_ID, month, day, hour, appliance_type, ENERGYDATA],...]
# -------------------------------------------------------------------------------------------
FOLDERLIST = os.listdir(pathToAllCSVFilesFolder)        # Get all files in folder
TEMPERATURES = []

# Iterate all files containgin all measurements
for csvFileName in FOLDERLIST:
    aggregatedDict = {}                                    # Dictionary with aggregated result
    csvFileFullPath = pathToAllCSVFilesFolder + r'\\' + csvFileName

    # Read in single .csv file line per line
    with open(csvFileFullPath, 'rb') as csvfile:
        LINEREAD = csv.reader(csvfile, delimiter=' ', quotechar='|')

        for row in LINEREAD:
            #print("row: " + str(row))
            entries = row[0].split(',')

            HOUSEHOLD_ID = int(entries[1])
            APPLIANCE = int(entries[2])
            DATE_RECORDED = entries[3]
            DATA = float(entries[4])           # in kwh/10 TODO: TEST and check float
            TIME_RECORDED = entries[5]

            # Convert date
            year = DATE_RECORDED[0:3]       # TODO: Check if more than one year
            month = str(DATE_RECORDED[5:7])
            day = str(DATE_RECORDED[8:10])
            hour = str(TIME_RECORDED[0:2])

            # Above 250 the number represent TEMPERATURES ane not appliances
            # # Todo: Calculate average TEMPERATURES for each hour....so far all entries are put in seperate list.
            if APPLIANCE > 250:
                TEMPERATURES.append([HOUSEHOLD_ID, month, day, hour, np.nan, DATA])
            else:
                # Get category for appliance
                APPLIANCE_TYPE = str(appliance_types_Dictionary[APPLIANCE])
                #print(APPLIANCE_TYPE)

            # Create unique number for dictionary
            dictNr = int(str(HOUSEHOLD_ID + str(mont) + str(day) + str(hour) + str(APPLIANCE_TYPE))
            # Summarise according to HOUSEHOLD_ID

            try:
                aggregatedDict[dictNr] = [HOUSEHOLD_ID, month, day, hour, APPLIANCE_TYPE, DATA]
            except KeyError:
                aggregatedDict[dictNr][5] += DATA       # Summarise data
            
            #Scrap
            break
            
        outList = []     # scrap

        # Write aggregated hours to .csv file
        with open(pathwriteOutAggregatedCSVFile, 'wb') as csvfile:
            _spam = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in aggregatedDict:
                _spam.writerow(aggregatedDict[i])

                # Scrap
                outList.append(aggregatedDict[i])

        # Write aggregated TEMPERATURES to .csv file
        with open(pathwriteOutTemperatureCSVFile, 'wb') as csvfile:
            _spam = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in TEMPERATURES:
                _spam.writerow(i)
        
        #------------------------
        # Test: Read out one day
        #------------------------


        daySElection = []
        for i in outList:
            if i[1] == 6 and i[2] == 17:  # read out for 17 of june for all times
                print(i)
                daySElection.append(i)
        
        print(daySElection)
        new = daySElection.sort(key=itemgetter(3))
        print(len(new))
        for i in new:
            print i

        print("Length of TEMPERATURES: " + str(TEMPERATURES))
        prnt("..")