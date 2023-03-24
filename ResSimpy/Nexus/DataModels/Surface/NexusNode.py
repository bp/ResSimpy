from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Node import Node


@dataclass(kw_only=True)
class NexusNode(Node):
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    number: Optional[int] = None
    temp: Optional[float] = None
    station: Optional[str] = None

    @staticmethod
    def get_node_nexus_mapping() -> dict[str, tuple[str, type]]:
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
        """Returns a dictionary of the key properties of a node"""
        mapping_dict = self.get_node_nexus_mapping()
        if keys_in_nexus_style:
            result_dict = {x: self.__getattribute__(y[0]) for x, y in mapping_dict.items()}

        else:
            result_dict = {y[0]: self.__getattribute__(y[0]) for y in mapping_dict.values()}
        extra_attributes = {'date': self.date, }
        if self.unit_system is not None:
            extra_attributes.update({'unit_system': self.unit_system.value})
        result_dict.update(extra_attributes)
        return result_dict
