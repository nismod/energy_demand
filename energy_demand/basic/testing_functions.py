"""TEsting functions
"""
import numpy as np
from energy_demand.basic import basic_functions

def test_if_minus_value_in_array(arraytotest):
    """Test if array has negative value
    """
    only_neg_elements = arraytotest[arraytotest < 0]

    if len(only_neg_elements) > 0:
        return True
    else:
        False

def switch_testing(fuel_switches, service_switches, capacity_switches):
    """Test if swithes defined for same enduse

    Arguments
    ---------
    fuel_switches : list
        Switches
    service_switches : list
        Switches
    capacity_switches : list
        Switches
    """
    all_switches_incl_sectors = {}

    enduses_service_switch = set([])

    for switch in service_switches:
        enduses_service_switch.add(switch.enduse)

        # Collect all enduses and affected sectors
        if switch.enduse not in all_switches_incl_sectors:
            all_switches_incl_sectors[switch.enduse] = set([])

            if not switch.sector:
                all_switches_incl_sectors[switch.enduse] = None
            else:
                all_switches_incl_sectors[switch.enduse].add(switch.sector)
        else:
            if not switch.sector:
                pass
            else:
                all_switches_incl_sectors[switch.enduse].add(switch.sector)

    enduses_capacity_switch = set([])

    for switch in capacity_switches:
        enduses_capacity_switch.add(switch.enduse)

        # Collect all enduses and affected sectors
        if switch.enduse not in all_switches_incl_sectors:
            all_switches_incl_sectors[switch.enduse] = set([])

            if not switch.sector:
                all_switches_incl_sectors[switch.enduse] = None
            else:
                all_switches_incl_sectors[switch.enduse].add(switch.sector)
        else:
            if not switch.sector:
                pass
            else:
                all_switches_incl_sectors[switch.enduse].add(switch.sector)

    enduses_service_switch = list(enduses_service_switch)
    enduses_capacity_switch = list(enduses_capacity_switch)

    for enduse in all_switches_incl_sectors:
        if all_switches_incl_sectors[enduse] != None:
            all_switches_incl_sectors[enduse] = list(all_switches_incl_sectors[enduse])

    return all_switches_incl_sectors

def testing_fuel_tech_shares(fuel_tech_fueltype_p):
    """Test if assigned fuel share add up to 1 within each fueltype

    Paramteres
    ----------
    fuel_tech_fueltype_p : dict
        Fueltype fraction of technologies
    """
    for enduse in fuel_tech_fueltype_p:

        sector_crit = basic_functions.test_if_sector(
            fuel_tech_fueltype_p[enduse])

        if sector_crit:
            for sector in fuel_tech_fueltype_p[enduse]:
                for fueltype in fuel_tech_fueltype_p[enduse][sector]:
                    if fuel_tech_fueltype_p[enduse][sector][fueltype] != {}:
                        if round(sum(fuel_tech_fueltype_p[enduse][sector][fueltype].values()), 3) != 1.0:
                            raise Exception(
                                "The fuel shares assumptions are wrong for enduse {} and fueltype {} SUM: {}".format(
                                    enduse, fueltype, sum(fuel_tech_fueltype_p[enduse][sector][fueltype].values())))
        else:
            for fueltype in fuel_tech_fueltype_p[enduse]:
                if fuel_tech_fueltype_p[enduse][fueltype] != {}:
                    if round(sum(fuel_tech_fueltype_p[enduse][fueltype].values()), 3) != 1.0:
                        raise Exception(
                            "The fuel shares assumptions are wrong for enduse {} and fueltype {} SUM: {}".format(
                                enduse, fueltype, sum(fuel_tech_fueltype_p[enduse][fueltype].values())))

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
                raise Exception(
                    "Error: '{}' is not defined in technology_definition.csv".format(
                        tech))

def test_function_fuel_sum(data, fuel_disagg, mode_constrained, space_heating_enduses):
    """ Sum raw disaggregated fuel data
    """
    fuel_in = 0
    fuel_in_solid_fuel = 0
    fuel_in_gas = 0
    fuel_in_elec = 0
    fuel_in_oil = 0
    fuel_in_heat = 0
    fuel_in_hydrogen = 0
    fuel_in_biomass = 0
    tot_heating = 0

    for region in fuel_disagg['residential']:
        for enduse in fuel_disagg['residential'][region]:
            fuel_in += np.sum(fuel_disagg['residential'][region][enduse])
            fuel_in_heat += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['heat']])

            if mode_constrained == False and enduse in space_heating_enduses: #Exclude inputs for heating
                tot_heating += np.sum(fuel_disagg['residential'][region][enduse])
            else:
                fuel_in_elec += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['electricity']])
                fuel_in_gas += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['gas']])
                fuel_in_hydrogen += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['hydrogen']])
                fuel_in_oil += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['oil']])
                fuel_in_solid_fuel += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['solid_fuel']])
                fuel_in_biomass += np.sum(fuel_disagg['residential'][region][enduse][data['lookups']['fueltypes']['biomass']])

    for region in fuel_disagg['service']:
        for enduse in fuel_disagg['service'][region]:
            for sector in fuel_disagg['service'][region][enduse]:
                fuel_in += np.sum(fuel_disagg['service'][region][enduse][sector])
                fuel_in_heat += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['heat']])

                if mode_constrained == False and enduse in space_heating_enduses:
                    tot_heating += np.sum(fuel_disagg['service'][region][enduse][sector])
                else:
                    fuel_in_elec += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['electricity']])
                    fuel_in_gas += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['gas']])
                    fuel_in_hydrogen += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['hydrogen']])
                    fuel_in_oil += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['oil']])
                    fuel_in_solid_fuel += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['solid_fuel']])
                    fuel_in_biomass += np.sum(fuel_disagg['service'][region][enduse][sector][data['lookups']['fueltypes']['biomass']])
                
    for region in fuel_disagg['industry']:
        for enduse in fuel_disagg['industry'][region]:
            for sector in fuel_disagg['industry'][region][enduse]:
                fuel_in += np.sum(fuel_disagg['industry'][region][enduse][sector])
                fuel_in_heat += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['heat']])

                if mode_constrained == False and enduse in space_heating_enduses:
                    tot_heating += np.sum(fuel_disagg['industry'][region][enduse][sector])
                else:
                    fuel_in_elec += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['electricity']])
                    fuel_in_gas += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['gas']])
                    fuel_in_hydrogen += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['hydrogen']])
                    fuel_in_oil += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['oil']])
                    fuel_in_solid_fuel += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['solid_fuel']])
                    fuel_in_biomass += np.sum(fuel_disagg['industry'][region][enduse][sector][data['lookups']['fueltypes']['biomass']])

    out_dict = {
        "fuel_in": fuel_in,
        "fuel_in_biomass": fuel_in_biomass,
        "fuel_in_elec": fuel_in_elec,
        "fuel_in_gas": fuel_in_gas,
        "fuel_in_heat": fuel_in_heat,
        "fuel_in_hydrogen": fuel_in_hydrogen,
        "fuel_in_solid_fuel": fuel_in_solid_fuel,
        "fuel_in_oil": fuel_in_oil,
        "tot_heating": tot_heating}

    return out_dict

def control_disaggregation(fuel_disagg, national_fuel, enduses, sectors=False):
    """Check if disaggregation is correct

    Arguments
    ---------
    fuel_disagg : dict
        Disaggregated fuel to regions
    national_fuel : dict
        National fuel
    enduses : list
        Enduses
    sectors : list, bool=False
        Sectors
    """
    control_sum_disagg, control_sum_national = 0, 0

    if not sectors:
        for reg in fuel_disagg:
            for enduse in fuel_disagg[reg]:
                control_sum_disagg += np.sum(fuel_disagg[reg][enduse])

        for enduse in enduses:
            control_sum_national += np.sum(national_fuel[enduse])

        #The loaded floor area must correspond to provided fuel sectors numers
        np.testing.assert_almost_equal(
            control_sum_disagg,
            control_sum_national,
            decimal=2, err_msg="disagregation error ss {} {}".format(
                control_sum_disagg, control_sum_national))
    else:
        for reg in fuel_disagg:
            for enduse in fuel_disagg[reg]:
                for sector in fuel_disagg[reg][enduse]:
                    control_sum_disagg += np.sum(fuel_disagg[reg][enduse][sector])

        for sector in sectors:
            for enduse in enduses:
                control_sum_national += np.sum(national_fuel[enduse][sector])

        #The loaded floor area must correspond to provided fuel sectors numers
        np.testing.assert_almost_equal(
            control_sum_disagg,
            control_sum_national,
            decimal=2, err_msg="disagregation error ss {} {}".format(
                control_sum_disagg, control_sum_national))
