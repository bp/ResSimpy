def invert_nexus_map(nexus_mapping: dict[str, tuple[str, type]]) -> dict[str, str]:
    r"""Takes a nexus map of the form {NEXUS KEYWORD: ('attribute_name', type), ...} and reverses it to
    give a map from attribute names to Nexus Keywords.

    Args:
    ----
        nexus_mapping (dict[str, tuple[str, type]]): dictionary of the form \n
        {NEXUS KEYWORD: ('attribute_name', type), ...}

    Returns:
    -------
        dict[str, str] of the form {'attribute_name': 'NEXUS_KEYWORD'}

    """
    inverted_nexus_map = {v[0]: k for k, v in nexus_mapping.items()}
    return inverted_nexus_map


def nexus_keyword_to_attribute_name(nexus_mapping: dict[str, tuple[str, type]], nexus_keyword: str) -> str:
    """Takes a Nexus Keyword and maps to the corresponding attribute name from a given nexus mapping."""
    attribute_name_tuple = nexus_mapping.get(nexus_keyword.upper(), None)
    if attribute_name_tuple is None:
        raise AttributeError(f'No nexus keyword found named "{nexus_keyword.upper()}" in the provided nexus mapping')
    return attribute_name_tuple[0]


def attribute_name_to_nexus_keyword(nexus_mapping: dict[str, tuple[str, type]], attribute_name: str) -> str:
    """Takes an attribute name and maps to the corresponding nexus keyword from a given nexus mapping."""

    invert_map = invert_nexus_map(nexus_mapping)
    nexus_keyword = invert_map.get(attribute_name.lower(), None)
    if nexus_keyword is None:
        raise AttributeError(f'No attribute found with name {attribute_name.lower()} in the provided nexus mapping')
    return nexus_keyword
