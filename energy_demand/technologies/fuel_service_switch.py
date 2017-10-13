"""Function related to service or fuel switch
"""
import numpy as np
from energy_demand.initalisations import initialisations as init
from energy_demand.technologies import tech_related

def get_service_rel_tech_decr_by(tech_decreased_share, service_tech_by_p):
    """Iterate technologies with future less service demand (replaced tech)
    and get relative share of service in base year

    Arguments
    ----------
    tech_decreased_share : dict
        Technologies with decreased service
    service_tech_by_p : dict
        Share of service of technologies in by

    Returns
    -------
    rel_share_service_tech_decr_by : dict
        Relative share of service of replaced technologies
    """
    rel_share_service_tech_decr_by = {}

    # Summed share of all diminishing technologies
    sum_service_tech_decrease_p = 0
    for tech in tech_decreased_share:
        sum_service_tech_decrease_p += service_tech_by_p[tech]
    #Faster but less readible
    #sum_service_tech_decrease_p = sum([service_tech_by_p[tech] for tech in tech_decreased_share]) 

    # Relative of each diminishing tech
    for tech in tech_decreased_share:
        try:
            rel_share_service_tech_decr_by[tech] = (1.0 / float(sum_service_tech_decrease_p)) * service_tech_by_p[tech]
        except ZeroDivisionError:
            rel_share_service_tech_decr_by[tech] = 0

    return rel_share_service_tech_decr_by
