

# Vessels for yearly data calculation.  


1. Yearly Fuel Data Array [YEAR_FUEL_ARRAY]
---------------------------
For every end use creat the following array and store in yearly dict:
    array (Fuel_Type, reg, End_Use, YEARLYDATA)


2. Yearly & Hourly Load Shape for every end_use [LOAD_SHAPE_REGULAR_YEARLY]
---------------------------
For every end use create the following array:

    array: (yearday, hour, % of tot)

--> Assign for every day energy demand (e.g. also only with monthly data)
--> Sum over the full year
--> Calculate hourly of total percentage

3. Peak hourly load shape [LOAD_SHAPE_DAILY_PEAK]
---------------------------
# PEAK: Hourly Load Shape for every end_use for peak day:

    array(hour, % of day)

--> Calculate maximum daily demand of peak day of total yearly regular demand
--> The percentage between total yearly demand and peak day allows to derive peak from any total demand
--> Use peak day distribution
--> Like this daily peak load can be derived.

4. Resulting Array from every Sub-Module
----------------------------------------

array: (fuel_type, reg, enduse, yearday, hour)

A. With scenario driver adapt YEAR_FUEL_ARRAY  
B. Iterate over 







# a.shape --> (3, 2, 2, 2, 24)
iterate over all fuels: a[:, 0, 0, 0]

