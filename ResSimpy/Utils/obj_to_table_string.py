from abc import abstractmethod
from ResSimpy.Utils.invert_nexus_map import nexus_keyword_to_attribute_name
from typing import Protocol


class SupportsKeywordMapping(Protocol):
    @staticmethod
    @abstractmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns a mapping of keywords.

        The values in dict can be of the following types:[str, tuple[str, type]].

        """
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def to_dict(self) -> dict[str, None | str | int | float]:
        """Writes a dictionary with the following types:[str, None | str | int | float]."""
        raise NotImplementedError("Implement this in the derived class")


def to_table_line(obj: SupportsKeywordMapping, headers: list[str]) -> str:
    """Takes a generic Nexus object and returns the attribute values as a string in the order of headers provided.

    Requires an implemented to_dict method and get_keyword_mapping() method.

    Args:
        obj (Any): a NexusObject with a to_dict and get_keyword_mapping method.
        headers (list[str]): list of header values in Nexus keyword format

    Returns:
        string of the values in the order of the headers provided.

    """
    nexus_mapping = obj.get_keyword_mapping()
    properties = obj.to_dict()

    constructed_values = []
    for header in headers:
        attribute_name = nexus_keyword_to_attribute_name(nexus_mapping, header)
        attribute_value = properties[attribute_name]
        if attribute_value is None:
            attribute_value = 'NA'
        constructed_values.append(attribute_value)
    return ' '.join([str(x) for x in constructed_values]) + '\n'
