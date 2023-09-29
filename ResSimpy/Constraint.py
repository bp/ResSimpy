"""Base class object for storing data related to well and node constraints."""

from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.AttributeMappings.ConstraintUnitAttributeMapping import ConstraintUnits


@dataclass(repr=False)
class Constraint(DataObjectMixin, ABC):
    """Base class object for storing data related to well and node constraints."""
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    max_surface_oil_rate: Optional[float] = None
    max_surface_gas_rate: Optional[float] = None
    max_surface_water_rate: Optional[float] = None
    max_surface_liquid_rate: Optional[float] = None
    max_reservoir_oil_rate: Optional[float] = None
    max_reservoir_gas_rate: Optional[float] = None
    max_reservoir_water_rate: Optional[float] = None
    max_reservoir_liquid_rate: Optional[float] = None

    @property
    def attribute_to_unit_map(self) -> AttributeMapBase:
        """Returns the attribute to unit map for the constraint."""
        return ConstraintUnits()
