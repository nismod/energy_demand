# ----------------------------------------------------------------
# Description: This is the residential model
# Authors: 
# ----------------------------------------------------------------

# Imports
import numpy as np
import math as m

def run():
    """
    Main function of residential model.

    Main steps:

    A. Residential electriciy demand

    Input:

    Output:
    """

    # Load all Scenario variables (fuel switch etc)
    # Load all demographic data of all catchments
    # Load all technlogical effiencies
    # Load socio-economic data
    # Load floor area...
    # Load climate data...

    
    # Load Base Year household energy load profiels
    load_profile_typA = energyLoadProfile('Detached', 24, [1,2,3,4,5,6,7])  # Typoloy Type, numer of hours, List with days [0 = 1 Jan, 365 = 31.Dez]
    
    # Generate time arrays. (e.g. 1 day per month of simulation year)
    generate_Time_Array()

    # Read in houshold load curves from HES dataset
    loadCurveA, loadCurveB = read_Housholdtypology_load_Curves()

    # Generate Base Distribution of households etc.
    generateBaseDistribution()




    return
