from __future__ import annotations
import uuid
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional
from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Target(DataObjectMixin, ABC):
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None

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
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
