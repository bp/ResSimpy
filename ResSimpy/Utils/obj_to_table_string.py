from __future__ import annotations
from abc import abstractmethod

from ResSimpy.Utils.invert_nexus_map import nexus_keyword_to_attribute_name
from typing import Protocol, Sequence, TYPE_CHECKING

from ResSimpy.Utils.to_dict_generic import to_dict

if TYPE_CHECKING:
    from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixinDictType


class SupportsKeywordMapping(Protocol):
    @staticmethod
    @abstractmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns a mapping of keywords.

        The values in dict can be of the following types:[str, tuple[str, type]].

        """
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def to_dict(self) -> DataObjectMixinDictType:
        """Writes a dictionary with the following types:[str, None | str | int | float | dict[int | float]]."""
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
        elif attribute_value is True:
            attribute_value = 'YES'
        elif attribute_value is False:
            attribute_value = 'NO'
        constructed_values.append(attribute_value)
    return ' '.join([str(x) for x in constructed_values]) + '\n'


def get_column_headers_required(obj_list: Sequence[SupportsKeywordMapping]) -> list[str]:
    """Returns the column headers required to represent all non None attributes of the Nexus objects.

    Args:
        obj_list (list[SupportsKeywordMapping]): List of Nexus objects with a get_keyword_mapping method.

    Returns:
        list[str] representing the column headers in Nexus keyword format.
    """
    if not obj_list:
        return []
    headers: set[str] = set()
    for obj in obj_list:
        attr_as_dict = to_dict(obj, keys_in_nexus_style=True, include_nones=False, add_date=False, add_units=False)
        headers.update(attr_as_dict.keys())

    keyword_mapping = obj_list[0].get_keyword_mapping()
    headers_ordered_by_keyword_mapping = [x for x in keyword_mapping.keys() if x in headers]
    return headers_ordered_by_keyword_mapping
