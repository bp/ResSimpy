"""Base class object for storing data related to nodeconnections."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class NodeConnection(DataObjectMixin, ABC):
    """Base class object for storing data related to nodeconnections."""
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None

    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the constraint."""
        return NetworkUnits(self.unit_system)
