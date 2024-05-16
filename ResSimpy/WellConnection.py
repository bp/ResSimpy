from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class WellConnection(DataObjectMixin, ABC):
    name: Optional[str] = None

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
    hyd_method: Optional[str] = None
    crossflow: Optional[str] = None
    crossshut: Optional[str] = None
    inj_mobility: Optional[str] = None
    polymer: Optional[str] = None
    stream: Optional[str] = None
    group: Optional[str] = None
    i: Optional[int] = None
    j: Optional[int] = None
    drainage_radius: Optional[float] = None
    pvt_method: Optional[int] = None

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
