from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Node import Node
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr


@dataclass(kw_only=True)
class NexusNode(Node):
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    number: Optional[int] = None
    temp: Optional[float] = None
    station: Optional[str] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float]):
        super().__init__()
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    def __repr__(self):
        return generic_repr(self)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
        """gets the mapping of nexus keywords to attribute definitions"""
        keywords = {
            'NAME': ('name', str),
            'TYPE': ('type', str),
            'DEPTH': ('depth', float),
            'TEMP': ('temp', float),
            'X': ('x_pos', float),
            'Y': ('y_pos', float),
            'NUMBER': ('number', int),
            'STATION': ('station', str),
        }
        return keywords

    def to_dict(self, keys_in_nexus_style: bool = False) -> dict[str, None | str | int | float]:
        """
            Returns a dictionary of the attributes of the Node
        Args:
            keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the \
                attribute name as stored by ressimpy

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_nexus_style, add_date=True, add_units=True)
        return result_dict
