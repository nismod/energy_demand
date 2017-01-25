# ----------------------------------------------------------------
# Description: Main class for running individual model elements
# Authors: 
# Pranab Baruah, Scott Thacker, Sisi Hu, Matt Ives
# ----------------------------------------------------------------

# Imports
import sys, os

# Load modules
import transition_module    # Module containing different technology diffusion methods


# Global variables
YearCurrent = 0          # [int] Current year in current simulation
YearBase =  2015         # [int] First year of the simulation period 
YearEnd =   2050         # [int] Last year of the simulation period 

def national_summary():
    """
    YearCurrent:    [int] Current year in current simulation
    YearEnd:        [int] Last year of the simulation period   

    """

    # Run different sector models
    import residential_model
    residential_model.run(modelrun_id, year, YearBase, YearCurrent, total_yr, cur_yr)

    import transport
    transport.run(modelrun_id, year, YearBase, YearCurrent, total_yr, cur_yr)

    import Industry_model
    Industry_model.run(modelrun_id, year, YearBase, YearCurrent, total_yr, cur_yr)

    import Service_sector_model
    Service_sector_model.run(modelrun_id, year, YearBase, YearCurrent, total_yr, cur_yr)

    import Peak_main as Peak
    Peak.run(modelrun_id, year, YearBase, YearCurrent, total_yr, cur_yr)

    # run the national_summary update

