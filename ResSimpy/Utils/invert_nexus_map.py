def invert_nexus_map(nexus_mapping: dict[str, tuple[str, type]]) -> dict[str, str]:
    """ takes a nexus map of the form {NEXUS KEYWORD: ('attribute_name', type), ...} and reverses it to \
    give a map from attribute names to Nexus Keywords

    Args:
        nexus_mapping (dict[str, tuple[str, type]]): dictionary of the form \n
        {NEXUS KEYWORD: ('attribute_name', type), ...}

    Returns:
        dict[str, str] of the form {'attribute_name': 'NEXUS_KEYWORD'}

    """
    inverted_nexus_map = {v[0]: k for k, v in nexus_mapping.items()}
    return inverted_nexus_map
