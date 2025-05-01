from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Drill(NetworkObject, ABC):

    @property
    @abstractmethod
    def total_drill_time(self) -> float:
        """The total time to drill the well."""
        raise NotImplementedError("Implement this in the derived class")

    def __init__(self, unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 properties_dict: Optional[dict[str, None | int | str | float]] = None) -> None:
        """Initialises the Drill class.

        Args:
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            properties_dict (dict): dict of the properties to set on the object.
        """

        super().__init__(unit_system=unit_system, name=name, date=date, date_format=date_format, start_date=start_date,
                         properties_dict=properties_dict)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the Drill."""
        return NetworkUnits(self.unit_system)
