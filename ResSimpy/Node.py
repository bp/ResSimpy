from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.AttributeMappings.NetworkUnitAttributeMapping import NetworkUnits


@dataclass(repr=False)
class Node(DataObjectMixin, ABC):
    name: Optional[str] = None
    type: Optional[str] = None
    depth: Optional[float] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None

    @property
    def attribute_to_unit_map(self) -> AttributeMapBase:
        """Returns the attribute to unit map for the constraint."""
        return NetworkUnits()
