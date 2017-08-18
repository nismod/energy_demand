"""Function related to service or fuel switch
"""
import numpy as np
from energy_demand.profiles import load_profile
from energy_demand.initalisations import initialisations as init
from energy_demand.technologies import technologies_related

def ss_sum_fuel_enduse_sectors(ss_fuel_raw_data_enduses, ss_enduses, nr_fueltypes):
    """Aggregated fuel for all sectors according to enduse
    """
    aggregated_fuel_enduse = {}

    for enduse in ss_enduses:
        aggregated_fuel_enduse[str(enduse)] = np.zeros((nr_fueltypes))

    # Iterate and sum fuel per enduse
    for _, fuels_sector in ss_fuel_raw_data_enduses.items():
        for enduse, fuels_enduse in fuels_sector.items():
            aggregated_fuel_enduse[enduse] += fuels_enduse

    return aggregated_fuel_enduse

def get_tech_future_service(service_tech_by_p, share_service_tech_ey_p):
    """Get all those technologies with increased service in future

    Parameters
    ----------
    service_tech_by_p : dict
        Share of service per technology of base year of total service
    share_service_tech_ey_p : dict
        Share of service per technology of end year of total service

    Returns
    -------
    assumptions : dict
        assumptions

    Info
    -----
    tech_increased_service : dict
        Technologies with increased future service
    tech_decreased_share : dict
        Technologies with decreased future service
    tech_decreased_share : dict
        Technologies with unchanged future service

    The assumptions are always relative to the simulation end year
    """
    tech_increased_service = {}
    tech_decreased_share = {}
    tech_constant_share = {}

    for enduse in service_tech_by_p:

        # If no service switch defined
        if share_service_tech_ey_p[enduse] == {}:
            tech_increased_service[enduse] = []
            tech_decreased_share[enduse] = []
            tech_constant_share[enduse] = []
        else:
            tech_increased_service[enduse] = []
            tech_decreased_share[enduse] = []
            tech_constant_share[enduse] = []

            # Calculate fuel for each tech
            for tech in service_tech_by_p[enduse]:

                # If future larger share
                if service_tech_by_p[enduse][tech] < share_service_tech_ey_p[enduse][tech]:
                    tech_increased_service[enduse].append(tech)

                # If future smaller service share
                elif service_tech_by_p[enduse][tech] > share_service_tech_ey_p[enduse][tech]:
                    tech_decreased_share[enduse].append(tech)
                else:
                    tech_constant_share[enduse].append(tech)

    return tech_increased_service, tech_decreased_share, tech_constant_share

def get_service_rel_tech_decr_by(tech_decreased_share, service_tech_by_p):
    """Iterate technologies with future less service demand (replaced tech) and get relative share of service in base year

    Parameters
    ----------
    tech_decreased_share : dict
        Technologies with decreased service
    service_tech_by_p : dict
        Share of service of technologies in by

    Returns
    -------
    rel_share_service_tech_decrease_by : dict
        Relative share of service of replaced technologies
    """
    rel_share_service_tech_decrease_by = {}

    # Summed share of all diminishing technologies
    sum_service_tech_decrease_p = 0
    for tech in tech_decreased_share:
        sum_service_tech_decrease_p += service_tech_by_p[tech]

    # Relative of each diminishing tech
    for tech in tech_decreased_share:
        rel_share_service_tech_decrease_by[tech] = (1 / sum_service_tech_decrease_p) * service_tech_by_p[tech]

    return rel_share_service_tech_decrease_by

def get_service_fueltype_tech(assumptions, lu_fueltypes, fuel_p_tech_by, fuels, tech_stock):
    """Calculate total energy service percentage of each technology and energy service percentage within the fueltype

    This calculation converts fuels into energy services (e.g. heating for fuel into heat demand)
    and then calculated how much an invidual technology contributes in percent to total energy
    service demand.

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.

    Parameters
    ----------
    lu_fueltypes : dict
        Fueltypes
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    tech_stock : object
        Technology stock of base year (region dependent)

    Return
    ------
    service_tech_by_p : dict
        Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p : dict
        Percentage of energy service witin a fueltype for all technologies with this fueltype for base year
    service_fueltype_by_p : dict
        Percentage of energy service per fueltype

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region.
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.

    Because regional efficiencies may differ within regions, the fuel distribution within
    the fueltypes may also differ
    """
    # Energy service per technology for base year
    service = init.init_nested_dict_brackets(fuels, lu_fueltypes.values())
    service_tech_by_p = init.init_dict_brackets(fuels) # Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p = init.init_nested_dict_brackets(fuels, lu_fueltypes.values()) # Percentage of service per technologies within the fueltypes
    service_fueltype_by_p = init.init_nested_dict_zero(service_tech_by_p.keys(), range(len(lu_fueltypes))) # Percentage of service per fueltype

    for enduse, fuel in fuels.items():

        for fueltype, fuel_fueltype in enumerate(fuel):
            tot_service_fueltype = 0

            #Initiate NEW
            for tech in fuel_p_tech_by[enduse][fueltype]:
                service[enduse][fueltype][tech] = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype].items():

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype
                #print("------------Tech: {}  {} ".format(fuel_alltech_by, fuel_fueltype))

                # Get technology type
                tech_type = technologies_related.get_tech_type(tech, assumptions['technology_list'])

                # Get efficiency depending whether hybrid or regular technology or heat pumps for base year
                if tech_type == 'hybrid_tech':
                    eff_tech = assumptions['hybrid_technologies'][tech]['average_efficiency_national_by']
                elif tech_type == 'heat_pump':
                    eff_tech = technologies_related.eff_heat_pump(
                        temp_diff=10,
                        efficiency_intersect=tech_stock[tech]['eff_by']
                        )
                elif tech_type == 'dummy_tech':
                    eff_tech = 1
                else:
                    eff_tech = tech_stock[tech]['eff_by']

                # Energy service of end use: Service == Fuel of technoloy * efficiency
                service_fueltype_tech = fuel_tech * eff_tech
                print("SERVICE NATIONA LCALCUATION: {} {} {}  {}  {}".format(enduse, tech, fuel_tech, eff_tech, service_fueltype_tech))

                # Add energy service demand
                service[enduse][fueltype][tech] += service_fueltype_tech

                # Total energy service demand within a fueltype
                tot_service_fueltype += service_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]:
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = 0
                    service_fueltype_by_p[enduse][fueltype] += 0
                else:
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = (1 / tot_service_fueltype) * service[enduse][fueltype][tech]
                    service_fueltype_by_p[enduse][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_service = init.sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():
                service_tech_by_p[enduse][technology] = (1 / total_service) * service_tech
                #print("Technology_enduse: " + str(technology) + str("  ") + str(service_tech))

        print("Total Service base year for enduse {}  :  {}".format(enduse, total_service))

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:
            service_fueltype_by_p[enduse][fueltype] = (1.0 / total_service) * service_fueltype_by_p[enduse][fueltype]

    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    '''
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p
