# This file holds several technology diffusion patterns
# Authors: Sven Eggimann; Scott Thacker; Pranab Baruah

# Imports
import math as m
#from __future__ import division
#import PythonDBase as dbase


def linearDiffusion(ED_model, modelrun_id, whereID, YEAR_CURRENT_SIMULATION, EFFICIENCY_BASE, YEAR_TOTAL):
    """
    This function assumes a linear technology diffusion.

    The function reads:
    EFFICIENCY_END_SIMULATION:    [%] The assumption about the maximum efficiency gain when market is fully saturated.

    Input:
    YEAR_CURRENT_SIMULATION:      [int] The year of the current simulation.   # TODO: check if current Year is 2010 or 0
    EFFICIENCY_BASE:              [%] The efficiency gain of the base year
    YEAR_TOTAL:                   [int] Total number of simulated years.

    Output:
    DIFFUSIONUPTAKE:              [%] The efficiency gain (uptake value) in the simulated year

    """
    # Read in data
    #data = dbase.readData("Inputs", ED_model, whereID, modelrun_id, 0)
    #for row in data:
    #    final_val = row[9] # SCOTT - to check is this is ok!????

    if YEAR_CURRENT_SIMULATION == 0:      # if Baseyear #TODO Check if it is 0 or 2015 or whatever
        DIFFUSIONUPTAKE = EFFICIENCY_BASE
    else:
        DIFFUSIONUPTAKE = EFFICIENCY_BASE + ((EFFICIENCY_END_SIMULATION - EFFICIENCY_BASE) / float(YEAR_TOTAL)) * YEAR_CURRENT_SIMULATION

    return DIFFUSIONUPTAKE

def sigmoidDiffusion(id, d,d, YEAR_TOTAL, YEAR_CURRENT_SIMULATION, YEAR_END_SIMULATION):
    """
    This function assumes "S"-Curve technology diffusion (logistic function).

    The function reads in the following assumptions about the technology to calculate the
    current distribution of the simulated year:

    Read In:
    # Links to table: C:\Users\cenv0553\GIT\NISMOD_OLD\nismod\energy_supply\ED2\Residential-Model\SCEN_PARAM\+Domestic_Strat_Input_ELEC_HEAT.xls
    YEAR_AVAILABLE:             [int] The assumption when a technology comes on the market.
    YEAR_SATURATE:              [int] The assumption when a technology fully saturates the market.

    Input:
    YEAR_TOTAL:                 [int] Total number of simulated years.
    YEAR_CURRENT_SIMULATION:    [int] The year of the current simulation.
    YEAR_END_SIMULATION:        [int] The last year of the simulation period.
    YEAR_START_SIMULATION:      [int] The first year of the simulation period.

    Output:
    diffusion_Efficiency:       [%] Efficiency gain of technology in simulated year.
    """

    # Read in data
    ##YEAR_AVAILABLE = row[]
    ##YEAR_SATURATE = row[]
    ##EFFICIENCY_BASE               # The efficiency gain for the base year
    ##YEAR_INTERMEDIATE             # Year with a defined efficiency gain
    ##EFFICIENCY_INTERMEDIATE_YEAR  # Intermediate efficiency gain for a a defined intermediate year (YEAR_INTERMEDIATE).
    ##EFFICIENCY_END_SIMULATION     # The efficiency gain for the end of the simulation

    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    yearTranslated = -6 + (12/float(YEAR_SATURATE - YEAR_AVAILABLE) * (YEAR_END_SIMULATION - YEAR_AVAILABLE))

    # Convert x-value into y value on sigmoid curve reaching from -6 to 6
    sigmoidMidPoint = 0                         # [float] Can be used to shift curve to the left or right. Standard value is 0
    sigmoidSteepness = 1                        # [float] The steepness of the sigmoid curve. Standard value is 0
    UPTAKE_SIMULATION_YEAR = 1 / (1 + m.exp((-1) * sigmoidSteepness * (yearTranslated - sigmoidMidPoint)))

    # Calculate how many years the technology is beeing used at since the simulation year
    if (YEAR_CURRENT_SIMULATION <= YEAR_AVAILABLE):                    # If the technology is not available in the simulation year
        year_technology_in_use = 0.0
    else:
        if YEAR_CURRENT_SIMULATION > YEAR_SATURATE:                     # When year is past saturation value
            year_technology_in_use =  YEAR_SATURATE - YEAR_AVAILABLE    # Past saturaion. Technology is fully saturated
        else:
            year_technology_in_use = YEAR_CURRENT_SIMULATION - YEAR_AVAILABLE

    # Calculate total efficiency gain considering intermediate defined efficiencies [%]
    # total_possible_change = Das ist der totale Change in Prozent (Moegliche effizientverbesserung in Prozent)
    if YEAR_SATURATE >= YEAR_INTERMEDIATE and YEAR_SATURATE <= YEAR_END_SIMULATION: # if sat year is between 2030 to 2050
        total_possible_change = EFFICIENCY_INTERMEDIATE_YEAR + (EFFICIENCY_END_SIMULATION - EFFICIENCY_INTERMEDIATE_YEAR) / (YEAR_END_SIMULATION - YEAR_INTERMEDIATE) * (YEAR_SATURATE - YEAR_INTERMEDIATE) # e.g. 5% + (10%-5%) / (2050-2030) * (2070-2030)
    elif YEAR_SATURATE < 2030:
        total_possible_change = (EFFICIENCY_INTERMEDIATE_YEAR / (2030 - 2010)) * (YEAR_SATURATE - 2010)
    else:
        total_possible_change = EFFICIENCY_END_SIMULATION # when saturation year is greater than 2050 -- change = change at 2050

    if (EFFICIENCY_BASE <> 999.0): # TODO: ??
        total_possible_change = total_possible_change - EFFICIENCY_BASE

    # Calculate intermediate value
    # Zweite Zeile: Berechnet y wert auf Wikigraph
    # Dritte Zeile: Multipliyiert den y wiki wert (% zwischen 1 und 0) mit dem Totalen moeglichen Effizienzgewinn
    INTER = -6 + (12 / (YEAR_SATURATE - YEAR_AVAILABLE) * year_technology_in_use)                           # Calculates x value of simulation year on sigmoid graph from -6 to +6
    VALUE = 1 / (1 + m.exp((-1) * sigmoidSteepness * (INTER - sigmoidMidPoint))) / UPTAKE_SIMULATION_YEAR  #TODO: Why divide?  # Calculates y value of simulation year on sigmoid graph from -6 6o +6
    INTER_VALUE = VALUE * total_possible_change

    # year is before saturation value
    diffusion_Efficiency = INTER_VALUE

    # Returns efficiency gain of simulated year in % of technology for a sigmoid diffusion assumption
    return diffusion_Efficiency
