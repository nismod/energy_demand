"""TEsting functions
"""
import sys
import numpy as np

def test_region_selection(ed_fueltype_regs_yh):
    """function to see whether if only some days are selected
    the sum makes sense
    """
    modelled_days = 1
    hours_modelled = modelled_days * 24
    len_dict = 0
    _sum_day_selection = 0
    for fuels in ed_fueltype_regs_yh:
        for region_fuel in fuels:
            _sum_day_selection += np.sum(region_fuel[: hours_modelled])
            len_dict = region_fuel.shape[0]

    _sum_all = 0
    for fuels in ed_fueltype_regs_yh:
        for region_fuel in fuels:
            _sum_all += np.sum(region_fuel)
    #print("_sum_day_selection")
    ##print(_sum_day_selection)
    #print("_sum_all: " + str(_sum_all))
    return

def testing_fuel_tech_shares(fuel_tech_fueltype_p):
    """Test if assigned fuel share add up to 1 within each fuletype

    Paramteres
    ----------
    fuel_tech_fueltype_p : dict
        Fueltype fraction of technologies
    """
    for enduse in fuel_tech_fueltype_p:
        for fueltype in fuel_tech_fueltype_p[enduse]:
            if fuel_tech_fueltype_p[enduse][fueltype] != {}:
                if round(sum(fuel_tech_fueltype_p[enduse][fueltype].values()), 3) != 1.0:
                    sys.exit("Error: The fuel shares assumptions are wrong for enduse {} and fueltype {} SUM: {}".format(enduse, fueltype, sum(fuel_tech_fueltype_p[enduse][fueltype].values())))

def testing_tech_defined(technologies, all_tech_enduse):
    """Test if all technologies are defined for assigned fuels

    Arguments
    ----------
    technologies : dict
        Technologies
    all_tech_enduse : dict
        All technologies per enduse with assigned fuel shares
    """
    for enduse in all_tech_enduse:
        for tech in all_tech_enduse[enduse]:
            if tech not in technologies:
                sys.exit("Error: The technology '{}' for which fuel was attributed is not defined in technology stock".format(tech))

def test_function_fuel_sum(data):
    """ Sum raw disaggregated fuel data
    """
    fuel_in = 0
    fuel_in_elec = 0
    fuel_in_gas = 0

    for region in data['rs_fuel_disagg']:
        for enduse in data['rs_fuel_disagg'][region]:
            fuel_in += np.sum(data['rs_fuel_disagg'][region][enduse])
            fuel_in_elec += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltype']['electricity']])
            fuel_in_gas += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltype']['gas']])

    for region in data['ss_fuel_disagg']:
        for sector in data['ss_fuel_disagg'][region]:
            for enduse in data['ss_fuel_disagg'][region][sector]:
                fuel_in += np.sum(data['ss_fuel_disagg'][region][sector][enduse])
                fuel_in_elec += np.sum(data['ss_fuel_disagg'][region][sector][enduse][data['lookups']['fueltype']['electricity']])
                fuel_in_gas += np.sum(data['ss_fuel_disagg'][region][sector][enduse][data['lookups']['fueltype']['gas']])

    for region in data['is_fuel_disagg']:
        for sector in data['is_fuel_disagg'][region]:
            for enduse in data['is_fuel_disagg'][region][sector]:
                fuel_in += np.sum(data['is_fuel_disagg'][region][sector][enduse])
                fuel_in_elec += np.sum(data['is_fuel_disagg'][region][sector][enduse][data['lookups']['fueltype']['electricity']])
                fuel_in_gas += np.sum(data['is_fuel_disagg'][region][sector][enduse][data['lookups']['fueltype']['gas']])

    return fuel_in, fuel_in_elec, fuel_in_gas
