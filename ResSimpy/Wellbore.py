from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Wellbore(DataObjectMixin, ABC):
    name: Optional[str] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    roughness: Optional[float] = None

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
