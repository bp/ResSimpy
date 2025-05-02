from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class DrillSite(NetworkObject, ABC):
    max_rigs: Optional[int]

    def __init__(self, date: Optional[str] = None, date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None, unit_system: Optional[UnitSystem] = None, name: Optional[str] = None,
                 max_rigs: Optional[int] = None,
                 properties_dict: Optional[dict[str, None | int | str | float]] = None) -> None:
        """Initialises the DrillSite class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            max_rigs (Optional[int]): The maximum number of rigs allowed at the drill site.
        """
        self.max_rigs = max_rigs

        super().__init__(properties_dict=properties_dict, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=name)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the DrillSite."""
        return NetworkUnits(self.unit_system)

    @property
    def site_name(self) -> Optional[str]:
        """Returns the site name of the drill site."""
        return self.name
