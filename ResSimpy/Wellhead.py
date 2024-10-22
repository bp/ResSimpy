from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Wellhead(NetworkObject, ABC):
    well: Optional[str] = None
    wellhead_type: Optional[str] = None
    depth: Optional[float] = None
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, well: Optional[str] = None,
                 wellhead_type: Optional[str] = None, depth: Optional[float] = None, x_pos: Optional[float] = None,
                 y_pos: Optional[float] = None) -> None:
        """Initialises the Wellhead class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            well (Optional[str]): Associates the wellhead to the well.
            wellhead_type (Optional[str]): The type of well.
            depth (Optional[float]): The depth of the wellhead
            x_pos (Optional[float]): The x-coordinate of the wellhead (x).
            y_pos (Optional[float]): The y-coordinate of the wellhead (y).
        """

        self.well = well
        self.wellhead_type = wellhead_type
        self.depth = depth
        self.x_pos = x_pos
        self.y_pos = y_pos

        super().__init__(properties_dict=properties_dict, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=name)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
