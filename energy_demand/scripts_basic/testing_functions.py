"""TEsting functions
"""
import sys
import numpy as np
# pylint: disable=I0011,C0301,C0103, C0325

def test_function_fuel_sum(data):
    """ Sum raw disaggregated fuel data """
    fuel_in = 0
    for region in data['rs_fueldata_disagg']:
        for enduse in data['rs_fueldata_disagg'][region]:
            fuel_in += np.sum(data['rs_fueldata_disagg'][region][enduse])

    for region in data['ss_fueldata_disagg']:
        for sector in data['ss_fueldata_disagg'][region]:
            for enduse in data['ss_fueldata_disagg'][region][sector]:
                fuel_in += np.sum(data['ss_fueldata_disagg'][region][sector][enduse])
    
    for region in data['is_fueldata_disagg']:
            for enduse in data['rs_fueldata_disagg'][region]:
                fuel_in += np.sum(data['ss_fueldata_disagg'][region][enduse])
    
    fuel_in += 385 #transport
    return fuel_in

def testing_all_defined_tech_in_tech_stock(technologies, all_specified_tech_enduse_by):
    """Test if all defined technologies of fuels are also defined in technology stock
    """
    for enduse in all_specified_tech_enduse_by:
        for tech in all_specified_tech_enduse_by[enduse]:
            if tech not in technologies:
                sys.exit("Error: The technology '{}' for which fuel was attributed is not defined in technology stock".format(tech))
    return

def testing_all_defined_tech_in_switch_in_fuel_definition(testing_hybrid_tech, fuel_enduse_tech_p_by, share_service_tech_ey_p, technologies, assumptions):
    """Test if there is a technology share defined in end year which is not listed in technology fuel stock definition
    """
    for enduse, technology_enduse in share_service_tech_ey_p.items():
        for technology in technology_enduse:
            # If hybrid tech
            if technology in testing_hybrid_tech:
                tech_high = testing_hybrid_tech[technology]['tech_high_temp']
                tech_low = testing_hybrid_tech[technology]['tech_low_temp']
                fueltype_tech_low = technologies[tech_low]['fuel_type']
                fueltype_tech_high = technologies[tech_high]['fuel_type']

                if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech_low].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
                if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech_high].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
            else:
                fueltype_tech = technologies[technology]['fuel_type']

                if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
    return

def testing_correct_service_switch_entered(tech_stock_definition, switches):
    """
    """
    for enduse in tech_stock_definition:

        #get all switchess
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
    #if self.enduse not in data_shapes_yd and self.technologies_enduse == []:
    #    sys.exit("Error: The enduse is not defined with technologies and no generic yd shape is provided for the enduse '{}' ".format(self.enduse))

    return
