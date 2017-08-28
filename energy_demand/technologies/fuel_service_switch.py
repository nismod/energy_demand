"""Function related to service or fuel switch
"""
import numpy as np
from energy_demand.initalisations import initialisations as init
from energy_demand.technologies import technologies_related

def get_service_rel_tech_decr_by(tech_decreased_share, service_tech_by_p):
    """Iterate technologies with future less service demand (replaced tech)
    and get relative share of service in base year

    Parameters
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
    sum_service_tech_decrease_p = 0 #TODO: FASTER
    for tech in tech_decreased_share:
        sum_service_tech_decrease_p += service_tech_by_p[tech]

    # Relative of each diminishing tech
    for tech in tech_decreased_share:
        rel_share_service_tech_decr_by[tech] = (1 / sum_service_tech_decrease_p) * service_tech_by_p[tech]

    return rel_share_service_tech_decr_by