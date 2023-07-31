from typing import Any

from ResSimpy.Utils.invert_nexus_map import nexus_keyword_to_attribute_name


def to_table_line(obj: Any, headers: list[str]) -> str:
    """Takes a generic Nexus object and returns the attribute values as a string in the order of headers provided.
    Requires an implemented to_dict method and get_nexus_mapping() method.

    Args:
        obj (Any): a NexusObject with a to_dict and get_nexus_mapping method.
        headers (list[str]): list of header values in Nexus keyword format

    Returns:
        string of the values in the order of the headers provided.

    """
    nexus_mapping = obj.get_nexus_mapping()
    properties = obj.to_dict()

    constructed_values = []
    for header in headers:
        attribute_name = nexus_keyword_to_attribute_name(nexus_mapping, header)
        attribute_value = properties[attribute_name]
        if attribute_value is None:
            attribute_value = 'NA'
        constructed_values.append(attribute_value)
    return ' '.join([str(x) for x in constructed_values]) + '\n'
