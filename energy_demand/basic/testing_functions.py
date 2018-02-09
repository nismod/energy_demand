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

    _sum_day_selection = 0
    for fuels in ed_fueltype_regs_yh:
        for region_fuel in fuels:
            _sum_day_selection += np.sum(region_fuel[: hours_modelled])
            len_dict = region_fuel.shape[0]

    _sum_all = 0
    for fuels in ed_fueltype_regs_yh:
        for region_fuel in fuels:
            _sum_all += np.sum(region_fuel)

    return

def testing_fuel_tech_shares(fuel_tech_fueltype_p):
    """Test if assigned fuel share add up to 1 within each fueltype

    Paramteres
    ----------
    fuel_tech_fueltype_p : dict
        Fueltype fraction of technologies
    """
    for enduse in fuel_tech_fueltype_p:
        for fueltype in fuel_tech_fueltype_p[enduse]:
            if fuel_tech_fueltype_p[enduse][fueltype] != {}:
                if round(sum(fuel_tech_fueltype_p[enduse][fueltype].values()), 3) != 1.0:
                    sys.exit(
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
                sys.exit(
                    "The technology '{}' for which fuel was attributed isn't defined in tech stock".format(
                        tech))

def test_function_fuel_sum(data, mode_constrained, space_heating_enduses):
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

    fuel_heating_all_fueltypes = 0
    fuel_heating_gas = 0
    tot_heating = 0
    #mode_constrained = True #SCRAP

    for region in data['rs_fuel_disagg']:
        for enduse in data['rs_fuel_disagg'][region]:
            fuel_in += np.sum(data['rs_fuel_disagg'][region][enduse])
            fuel_in_heat += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['heat']])

            if mode_constrained == False and enduse in space_heating_enduses: #Exclude inputs for heating
                tot_heating += np.sum(data['rs_fuel_disagg'][region][enduse])
                #pass
            else:
                fuel_in_elec += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['electricity']])
                fuel_in_gas += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['gas']])
                fuel_in_hydrogen += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['hydrogen']])
                fuel_in_oil += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['oil']])
                fuel_in_solid_fuel += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['solid_fuel']])
                fuel_in_biomass += np.sum(data['rs_fuel_disagg'][region][enduse][data['lookups']['fueltypes']['biomass']])
            
    for region in data['ss_fuel_disagg']:
        for enduse in data['ss_fuel_disagg'][region]:
            for sector in data['ss_fuel_disagg'][region][enduse]:
                fuel_in += np.sum(data['ss_fuel_disagg'][region][enduse][sector])
                fuel_in_heat += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['heat']])

                if mode_constrained == False and enduse in space_heating_enduses:
                    tot_heating += np.sum(data['ss_fuel_disagg'][region][enduse][sector])
                else:
                    fuel_in_elec += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['electricity']])
                    fuel_in_gas += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['gas']])
                    fuel_in_hydrogen += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['hydrogen']])
                    fuel_in_oil += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['oil']])
                    fuel_in_solid_fuel += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['solid_fuel']])
                    fuel_in_biomass += np.sum(data['ss_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['biomass']])
                
    for region in data['is_fuel_disagg']:
        for enduse in data['is_fuel_disagg'][region]:
            for sector in data['is_fuel_disagg'][region][enduse]:
                fuel_in += np.sum(data['is_fuel_disagg'][region][enduse][sector])
                fuel_in_heat += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['heat']])

                if mode_constrained == False and enduse in space_heating_enduses:
                    tot_heating += np.sum(data['is_fuel_disagg'][region][enduse][sector])
                else:
                    fuel_in_elec += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['electricity']])
                    fuel_in_gas += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['gas']])
                    fuel_in_hydrogen += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['hydrogen']])
                    fuel_in_oil += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['oil']])
                    fuel_in_solid_fuel += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['solid_fuel']])
                    fuel_in_biomass += np.sum(data['is_fuel_disagg'][region][enduse][sector][data['lookups']['fueltypes']['biomass']])
                
    return fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydrogen, fuel_in_solid_fuel, fuel_in_oil, tot_heating

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
