def invert_nexus_map(nexus_mapping: dict[str, tuple[str, type]]) -> dict[str, str]:
    inverted_nexus_map = {v[0]: k for k, v in nexus_mapping.items()}
    return inverted_nexus_map
