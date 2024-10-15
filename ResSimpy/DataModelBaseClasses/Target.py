from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Target(NetworkObject, ABC):
    control_quantity: Optional[str] = None
    control_conditions: Optional[str] = None
    control_connections: Optional[str] = None
    control_method: Optional[str] = None
    calculation_method: Optional[str] = None
    calculation_conditions: Optional[str] = None
    calculation_connections: Optional[str] = None
    value: Optional[float] = None
    add_value: Optional[float] = None
    region: Optional[str] = None
    priority: Optional[int] = None
    minimum_rate: Optional[str] = None
    minimum_rate_no_shut: Optional[float] = None
    guide_rate: Optional[str] = None
    max_change_pressure: Optional[float] = None
    rank_dt: Optional[float] = None
    control_type: Optional[str] = None
    calculation_type: Optional[str] = None
    region_number: Optional[int] = None

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None) -> None:
        """Initialises the Target class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
        """
        super().__init__(properties_dict=properties_dict, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=name)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
