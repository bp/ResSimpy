"""Class that is used to represent a nexus node in the network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Node import Node


@dataclass(kw_only=True, repr=False)
class NexusNode(Node):
    """Class that is used to represent a nexus node in the network."""
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    number: Optional[int] = None
    temp: Optional[float] = None
    station: Optional[str] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float], date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None) -> None:
        """Initialises the NexusNode class.

        Args:
            properties_dict (dict): A dictionary of properties to set on the node.
        """
        super().__init__()

        protected_attributes = ['date', 'date_format', 'start_date', 'unit_system']

        self._start_date = start_date
        self._date_format = date_format
        self._date = date
        self._unit_system = unit_system

        # Loop through the properties dict if one is provided and set those attributes
        for key, prop in properties_dict.items():
            if key in protected_attributes:
                key = '_' + key
            self.__setattr__(key, prop)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
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

    def update(self, input_dictionary: dict[str, None | float | int | str]) -> None:
        """Updates a node based on a dictionary of attributes."""
        for k, v in input_dictionary.items():
            if v is None:
                continue
            if hasattr(self, '_NexusNode__' + k):
                setattr(self, '_NexusNode__' + k, v)
            elif hasattr(super(), '_Node__' + k):
                setattr(self, '_Node__' + k, v)
