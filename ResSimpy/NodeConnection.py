"""Base class object for storing data related to nodeconnections."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.AttributeMappings.NetworkUnitAttributeMapping import NetworkUnits


@dataclass(repr=False)
class NodeConnection(DataObjectMixin, ABC):
    """Base class object for storing data related to nodeconnections."""
    name: Optional[str] = None
    date: Optional[str] = None
    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None

    @property
    def attribute_to_unit_map(self) -> AttributeMapBase:
        """Returns the attribute to unit map for the constraint."""
        return NetworkUnits()
