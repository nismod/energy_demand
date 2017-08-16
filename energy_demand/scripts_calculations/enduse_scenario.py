"""Functions related to scenaric inputs (cascade calulations)
"""
import numpy as np
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_technologies import diffusion_technologies as diffusion

def change_temp_climate_change(data):
    """Change temperature data for every year depending on simple climate change assumptions

    Parameters
    ---------
    data : dict
        Data

    Returns
    -------
    temp_climate_change : dict
        Adapted temperatures for all weather stations depending on climate change assumptions
    """
    temp_climate_change = {}

    # Change weather for all weater stations
    for station_id in data['temperature_data']:
        temp_climate_change[station_id] = {}

        # Iterate over simulation period
        for curr_yr in data['sim_param']['sim_period']:
            temp_climate_change[station_id][curr_yr] = np.zeros((365, 24))

            # Iterate every month and substract
            for yearday in range(365):

                # Create datetime object
                date_object = date_handling.convert_yearday_to_date(
                    data['sim_param']['base_yr'],
                    yearday
                    )

                # Get month of yearday
                month_yearday = date_object.timetuple().tm_mon - 1

                # Get linear diffusion of current year
                temp_by = 0
                temp_ey = data['assumptions']['climate_change_temp_diff_month'][month_yearday]

                lin_diff_f = diffusion.linear_diff(
                    data['sim_param']['base_yr'],
                    curr_yr,
                    temp_by,
                    temp_ey,
                    len(data['sim_param']['sim_period'])
                )

                # Iterate hours of base year
                for hour, temp_old in enumerate(data['temperature_data'][station_id][yearday]):
                    temp_climate_change[station_id][curr_yr][yearday][hour] = temp_old + lin_diff_f

    return temp_climate_change

def apply_elasticity(base_demand, elasticity, price_base, price_curr):
    """Calculate current demand based on demand elasticity
    TESTED_PYTEST
    As an input the base data is provided and price differences and elasticity

    Parameters
    ----------
    base_demand : array_like
        Input with base fuel demand
    elasticity : float
        Price elasticity
    price_base : float
        Fuel price in base year
    price_curr : float
        Fuel price in current year

    Returns
    -------
    current_demand
        Demand of current year considering price elasticity.

    Info
    ------
    Price elasticity is defined as follows:

        price elasticity = (% change in quantity) / (% change in price)
        or
        elasticity       = ((Q_base - Q_curr) / Q_base) / ((P_base - P_curr)/P_base)

    Reformulating to calculate current demand:

        Q_curr = Q_base * (1 - e * ((P_base - P_curr)/ P_base))

    The function prevents demand becoming negative as in extreme cases this
    would otherwise be possibe.
    """
     # New current demand
    current_demand = base_demand * (1 - elasticity * ((price_base - price_curr) / price_base))

    if current_demand < 0:
        return 0
    else:
        return current_demand
