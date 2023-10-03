from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class WellConnection(DataObjectMixin, ABC):
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None

    bhdepth: Optional[float] = None
    datum_depth: Optional[float] = None
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    length: Optional[float] = None
    temperature: Optional[float] = None
    diameter: Optional[float] = None
    roughness: Optional[float] = None
    inner_diameter: Optional[float] = None
    productivity_index: Optional[float] = None

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
