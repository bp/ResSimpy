from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Wellhead(DataObjectMixin, ABC):
    well: Optional[str] = None
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    wellhead_type: Optional[str] = None
    depth: Optional[float] = None
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
