"""Function related to service or fuel switch
"""
import numpy as np
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_initalisations import initialisations as init
from energy_demand.scripts_technologies import technologies_related

def ss_summarise_fuel_enduse_sectors(ss_fuel_raw_data_enduses, ss_enduses, nr_fueltypes):
    """Aggregated fuel for all sectors according to enduse
    """
    aggregated_fuel_enduse = {}

    # Initialise
    for enduse in ss_enduses:
        aggregated_fuel_enduse[str(enduse)] = np.zeros((nr_fueltypes))

    # Iterate and sum fuel per enduse
    for _, fuels_sector in ss_fuel_raw_data_enduses.items():
        for enduse, fuels_enduse in fuels_sector.items():
            aggregated_fuel_enduse[enduse] += fuels_enduse

    return aggregated_fuel_enduse

def get_technology_services_scenario(service_tech_by_p, share_service_tech_ey_p):
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

    if share_service_tech_ey_p == {}: # If no service switch defined
        tech_increased_service = []
        tech_decreased_share = []
        tech_constant_share = []
    else:
        for enduse in service_tech_by_p:
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
        # Add to data
        #assumptions['rs_tech_increased_service'] = tech_increased_service
        #assumptions['rs_tech_decreased_share'] = tech_decreased_share
        #assumptions['rs_tech_constant_share'] = tech_constant_share
        print("   ")
        #print("tech_increased_service:  " + str(tech_increased_service))
        print("tech_decreased_share:    " + str(tech_decreased_share))
        print("tech_constant_share:     " + str(tech_constant_share))
    return tech_increased_service, tech_decreased_share, tech_constant_share

def get_service_rel_tech_decrease_by(tech_decreased_share, service_tech_by_p):
    """Iterate technologies with future less service demand (replaced tech) and get relative share of service in base year

    Parameters
    ----------
    tech_decreased_share : dict
        Technologies with decreased service
    service_tech_by_p : dict
        Share of service of technologies in by

    Returns
    -------
    relative_share_service_tech_decrease_by : dict
        Relative share of service of replaced technologies
    """
    relative_share_service_tech_decrease_by = {}

    # Summed share of all diminishing technologies
    sum_service_tech_decrease_p = 0
    for tech in tech_decreased_share:
        sum_service_tech_decrease_p += service_tech_by_p[tech]

    # Relative of each diminishing tech
    for tech in tech_decreased_share:
        relative_share_service_tech_decrease_by[tech] = np.divide(1, sum_service_tech_decrease_p) * service_tech_by_p[tech]

    return relative_share_service_tech_decrease_by

def get_service_fueltype_tech(assumptions, fueltypes_lu, fuel_p_tech_by, fuels, tech_stock):
    """Calculate total energy service percentage of each technology and energy service percentage within the fueltype

    This calculation converts fuels into energy services (e.g. heating for fuel into heat demand)
    and then calculated how much an invidual technology contributes in percent to total energy
    service demand.

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.

    Parameters
    ----------
    fueltypes_lu : dict
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
    # Initialise
    service = init.init_nested_dict(fuels, fueltypes_lu.values(), 'brackets') # Energy service per technology for base year
    service_tech_by_p = init.init_dict(fuels, 'brackets') # Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p = init.init_nested_dict(fuels, fueltypes_lu.values(), 'brackets') # Percentage of service per technologies within the fueltypes
    service_fueltype_by_p = init.init_nested_dict(service_tech_by_p.keys(), range(len(fueltypes_lu)), 'zero') # Percentage of service per fueltype

    for enduse, fuel in fuels.items():
        for fueltype, fuel_fueltype in enumerate(fuel):
            tot_service_fueltype = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype].items():
                #print("------------Tech: " + str(tech))

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype

                # Get technology type
                tech_type = technologies_related.get_tech_type(tech, assumptions)

                # Get efficiency depending whether hybrid or regular technology or heat pumps for base year
                if tech_type == 'hybrid_tech':
                    eff_tech = assumptions['technologies']['hybrid_gas_elec']['average_efficiency_national_by'] #TODO: CONTROL
                elif tech_type == 'heat_pump':
                    eff_tech = shape_handling.eff_heat_pump(
                        m_slope=assumptions['hp_slope_assumption'],
                        h_diff=10,
                        intersect=tech_stock[tech]['eff_by']
                        )
                else:
                    eff_tech = tech_stock[tech]['eff_by']

                # Energy service of end use: Service == Fuel of technoloy * efficiency
                service_fueltype_tech = fuel_tech * eff_tech

                # Add energy service demand
                service[enduse][fueltype][tech] = service_fueltype_tech

                # Total energy service demand within a fueltype
                tot_service_fueltype += service_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]:
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = 0
                    service_fueltype_by_p[enduse][fueltype] += 0
                else:
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = np.divide(1, tot_service_fueltype) * service[enduse][fueltype][tech]
                    service_fueltype_by_p[enduse][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_service = init.sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():
                service_tech_by_p[enduse][technology] = np.divide(1, total_service) * service_tech
                #print("Technology_enduse: " + str(technology) + str("  ") + str(service_tech))

        #print("Total Service base year for enduse {}  :  {}".format(enduse, _a))

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:
            service_fueltype_by_p[enduse][fueltype] = np.divide(1, total_service) * service_fueltype_by_p[enduse][fueltype]

    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    '''
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p

'''def calc_service_fueltype(lu_fueltype, service_tech_by_p, technologies_assumptions):
    """Calculate service per fueltype in percentage of total service

    Parameters
    ----------
    service_tech_by_p : dict
        Service demand per technology
    technologies_assumptions : dict
        Technologies with all attributes

    Return
    ------
    energy_service_fueltype : dict
        Percentage of total (iterate over all technologis with this fueltype) service per fueltype

    Example
    -----
    (e.g. 0.5 gas, 0.5 electricity)

    """
    service_fueltype = init_nested_dict(service_tech_by_p.keys(), range(len(lu_fueltype)), 'zero') # Energy service per technology for base year (e.g. heat demand in joules)

    # Iterate technologies for each enduse and their percentage of total service demand
    for enduse in service_tech_by_p:
        for technology in service_tech_by_p[enduse]:

            # Add percentage of total enduse to fueltype
            fueltype = technologies_assumptions[technology]['fuel_type']
            service_fueltype[enduse][fueltype] += service_tech_by_p[enduse][technology]

            # TODO:  Add dependingon fueltype HYBRID --> If hybrid, get base year assumption split--> Assumption how much service for each fueltype
            ##fueltypes_tech = technology]['fuel_type']

            #service_fueltype[enduse][fueltype]

    return service_fueltype

def generate_service_distribution_by(service_tech_by_p, technologies, lu_fueltype):
    """Calculate percentage of service for every fueltype
    """
    service_p = {}

    for enduse in service_tech_by_p:
        service_p[enduse] = {}
        for fueltype in lu_fueltype:
            service_p[enduse][lu_fueltype[fueltype]] = 0

        for tech in service_tech_by_p[enduse]:
            fueltype_tech = technologies[tech]['fuel_type']
            service_p[enduse][fueltype_tech] += service_tech_by_p[enduse][tech]

    return service_p
'''
