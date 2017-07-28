def get_nested_dict_key(nested_dict):
    """Get all keys of nested fu
    """
    all_nested_keys = []
    for entry in nested_dict:
        for value in nested_dict[entry].keys():
            all_nested_keys.append(value)

    return all_nested_keys