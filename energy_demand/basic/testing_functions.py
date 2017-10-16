"""TEsting functions
"""
import sys
import numpy as np

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

def testing_switch_technologies(hybrid_technologies, fuel_tech_p_by, share_service_tech_ey_p, technologies):
    """Test if end_year service switch technology is
    not assigned in base year and test if fuel share
    of hybrid tech is assigned

    Arguments
    ----------
    hybrid_technologies : list
        Hybrid technologies
    fuel_tech_p_by : dict
        Fuel assigneement base year
    share_service_tech_ey_p : dict
        End year service fraction definition
    technologies : dict
        Technologies
    """
    for enduse, technology_enduse in share_service_tech_ey_p.items():

        for technology in technology_enduse:

            # Test if the fuel share of the hybrid technology is assigned
            if technology in hybrid_technologies:
                tech_high = hybrid_technologies[technology]['tech_high_temp']
                fueltype_tech_high = technologies[tech_high]['fuel_type']
                if technology not in fuel_tech_p_by[enduse][fueltype_tech_high].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
            else:
                fueltype_tech = technologies[technology]['fuel_type']

                if technology not in fuel_tech_p_by[enduse][fueltype_tech].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))

def testing_service_switch_insert(tech_stock_definition, switches):
    """Test switches
    """
    for enduse in tech_stock_definition:

        #get all switches
        switches_enduse_tech_defined = []
        for switch in switches:
            if switch['enduse'] == enduse:
                switches_enduse_tech_defined.append(switch['tech'])

        if len(switches) >= 1:
            # Test if all defined tech are defined in switch
            for fueltype in tech_stock_definition[enduse]:
                for tech in tech_stock_definition[enduse][fueltype]:
                    if tech not in switches_enduse_tech_defined:
                        sys.exit("ERROR: IN service switch the technology {} is not defined".format(tech))

def testing_switch_criteria(crit_switch_fuel, crit_switch_service, enduse):
    """Test if fuel switch and service switch is implemented at the same time
    """
    if crit_switch_fuel and crit_switch_service:
        sys.exit("Error: Can't define service switch and fuel switch for enduse '{}' {}   {}".format(enduse, crit_switch_fuel, crit_switch_service))

def test_function_fuel_sum(data):
    """ Sum raw disaggregated fuel data
    """
    fuel_in = 0
    fuel_in_elec = 0

    for region in data['rs_fuel_disagg']:
        for enduse in data['rs_fuel_disagg'][region]:
            fuel_in += np.sum(data['rs_fuel_disagg'][region][enduse])
            fuel_in_elec += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltype']['electricity']])

    for region in data['ss_fuel_disagg']:
        for sector in data['ss_fuel_disagg'][region]:
            for enduse in data['ss_fuel_disagg'][region][sector]:
                fuel_in += np.sum(data['ss_fuel_disagg'][region][sector][enduse])
                fuel_in_elec += np.sum(data['ss_fuel_disagg'][region][sector][enduse][data['lookups']['fueltype']['electricity']])

    for region in data['is_fuel_disagg']:
        for sector in data['is_fuel_disagg'][region]:
            for enduse in data['is_fuel_disagg'][region][sector]:
                fuel_in += np.sum(data['is_fuel_disagg'][region][sector][enduse])
                fuel_in_elec += np.sum(data['is_fuel_disagg'][region][sector][enduse][data['lookups']['fueltype']['electricity']])

    return fuel_in, fuel_in_elec
