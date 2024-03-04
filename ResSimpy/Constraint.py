"""Base class object for storing data related to well and node constraints."""

from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.ConstraintUnitMapping import ConstraintUnits


@dataclass(repr=False)
class Constraint(DataObjectMixin, ABC):
    """Base class object for storing data related to well and node constraints."""
    # TODO: Add docstrings for this class
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
    bottom_hole_pressure: Optional[float] = None
    tubing_head_pressure: Optional[float] = None
    max_reservoir_total_fluids_rate: Optional[float] = None

    @property
    def units(self) -> ConstraintUnits:
        """Returns the attribute to unit map for the constraint."""
        return ConstraintUnits(self.unit_system)
