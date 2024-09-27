"""Base class object for storing data related to nodeconnections."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class NodeConnection(NetworkObject, ABC):
    """Base class object for storing data related to nodeconnections."""
    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None
    hyd_method: Optional[str | int] = None
    pvt_method: Optional[int] = None
    water_method: Optional[int] = None

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None) -> None:
        """Initialises the NodeConnection class.

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
        """Returns the attribute to unit map for the constraint."""
        return NetworkUnits(self.unit_system)
