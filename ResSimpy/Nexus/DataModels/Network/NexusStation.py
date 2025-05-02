"""Class that is used to represent a nexus node in the network."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True, repr=False)
class NexusStation(NetworkObject):
    """Class that is used to represent a nexus station in the network."""

    number: Optional[int] = None
    level: Optional[int] = None
    parent: Optional[str] = None

    def __init__(
        self,
        properties_dict: Optional[dict[str, None | int | str | float]] = None,
        date: Optional[str] = None,
        date_format: Optional[DateFormat] = None,
        start_date: Optional[str] = None,
        unit_system: Optional[UnitSystem] = None,
        name: Optional[str] = None,
        number: Optional[int] = None,
        level: Optional[int] = None,
        parent: Optional[str] = None,
    ) -> None:
        """Initialises the NexusStation class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            number (Optional[int]): Index associated with station for at a given level.
            level (Optional[int]): Level associated with the station. Parents are assigned the highest level values.
            parent (Optional[str]): The parent of the station, if applicable.
        """
        self.number = number
        self.level = level
        self.parent = parent

        super().__init__(
            properties_dict=properties_dict,
            date=date,
            date_format=date_format,
            start_date=start_date,
            unit_system=unit_system,
            name=name,
        )

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords = {
            "NAME": ("name", str),
            "NUMBER": ("number", int),
            "LEVEL": ("level", int),
            "PARENT": ("parent", str),
        }
        return keywords

    def update(self, input_dictionary: dict[str, None | float | int | str]) -> None:
        """Updates a node based on a dictionary of attributes."""
        for k, v in input_dictionary.items():
            if v is None:
                continue
            if hasattr(self, "_NexusStation__" + k):
                setattr(self, "_NexusStation__" + k, v)
            elif hasattr(super(), "_Station__" + k):
                setattr(self, "_Station__" + k, v)

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)
