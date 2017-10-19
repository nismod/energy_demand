"""Function related to service or fuel switch
"""

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
    sum_service_tech_decrease_p = sum(
        [service_tech_by_p[tech] for tech in tech_decreased_share])

    # Relative of each diminishing tech
    for tech in tech_decreased_share:
        try:
            rel_share_service_tech_decr_by[tech] = service_tech_by_p[tech] / float(sum_service_tech_decrease_p)
        except ZeroDivisionError:
            rel_share_service_tech_decr_by[tech] = 0

    return rel_share_service_tech_decr_by
