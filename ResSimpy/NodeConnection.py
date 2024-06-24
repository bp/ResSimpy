"""Base class object for storing data related to nodeconnections."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class NodeConnection(DataObjectMixin, ABC):
    """Base class object for storing data related to nodeconnections."""
    name: Optional[str] = None

    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None
    hyd_method: Optional[str | int] = None
    pvt_method: Optional[int] = None
    water_method: Optional[int] = None

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the constraint."""
        return NetworkUnits(self.unit_system)
