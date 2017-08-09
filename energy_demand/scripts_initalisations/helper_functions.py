"""Short diverse helper functions
"""
def get_nested_dict_key(nested_dict):
    """Get all keys of nested fu
    """
    all_nested_keys = []
    for entry in nested_dict:
        for value in nested_dict[entry].keys():
            all_nested_keys.append(value)

    return all_nested_keys

def helper_set_same_eff_all_tech(technologies, eff_achieved_factor=1):
    """Helper function to assing same achieved efficiency

    Parameters
    ----------
    technologies : dict
        Technologies
    eff_achieved_factor : float
        Factor showing the fraction of how much an efficiency is achieved

    Returns
    -------
    technologies : dict
        Adapted technolog
    """ #TODO MAKE FASTER
    for technology in technologies:
        technologies[technology]['eff_achieved'] = eff_achieved_factor
    return technologies
