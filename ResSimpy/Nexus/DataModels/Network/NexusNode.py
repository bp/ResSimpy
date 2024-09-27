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

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None) -> None:
        """Initialises the NexusNode class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
        """
        super().__init__(properties_dict=properties_dict, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system)

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
