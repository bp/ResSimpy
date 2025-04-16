"""Base class object for storing data related to well and node constraints."""

from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.ConstraintUnitMapping import ConstraintUnits


@dataclass(repr=False)
class Constraint(DataObjectMixin, ABC):
    """Base class object for storing data related to well and node constraints."""
    # TODO: Add docstrings for this class
    name: Optional[str] = None
    max_surface_oil_rate: Optional[float] = None
    max_surface_gas_rate: Optional[float] = None
    max_surface_water_rate: Optional[float] = None
    max_surface_liquid_rate: Optional[float] = None
    max_reservoir_oil_rate: Optional[float] = None
    max_reservoir_gas_rate: Optional[float] = None
    max_reservoir_water_rate: Optional[float] = None
    max_reservoir_liquid_rate: Optional[float] = None
    min_surface_oil_rate: Optional[float] = None
    min_surface_gas_rate: Optional[float] = None
    min_surface_water_rate: Optional[float] = None
    min_surface_liquid_rate: Optional[float] = None
    bottom_hole_pressure: Optional[float] = None
    tubing_head_pressure: Optional[float] = None
    max_reservoir_total_fluids_rate: Optional[float] = None
    max_avg_comp_dp: Optional[float] = None
    max_comp_dp: Optional[float] = None

    # attributes below here are also used on eclipse end
    # to determine proper workover strategy in WECON
    max_watercut: Optional[float] = None
    max_watercut_plug: Optional[float] = None
    max_watercut_plugplus: Optional[float] = None
    max_watercut_perf: Optional[float] = None
    max_watercut_perfplus: Optional[float] = None
    max_wor: Optional[float] = None
    max_wor_plug: Optional[float] = None
    max_wor_plug_plus: Optional[float] = None
    max_wor_perf: Optional[float] = None
    max_wor_perfplus: Optional[float] = None
    max_gor: Optional[float] = None
    max_gor_plug: Optional[float] = None
    max_gor_plug_plus: Optional[float] = None
    max_gor_perf: Optional[float] = None
    max_gor_perfplus: Optional[float] = None
    max_lgr: Optional[float] = None
    max_lgr_plug: Optional[float] = None
    max_lgr_plug_plus: Optional[float] = None
    max_lgr_perf: Optional[float] = None
    max_lgr_perfplus: Optional[float] = None
    convert_qmult_to_reservoir_barrels: Optional[bool] = None
    active_node: Optional[bool] = None
    gor_limit: Optional[float] = None

    @property
    def units(self) -> ConstraintUnits:
        """Returns the attribute to unit map for the constraint."""
        return ConstraintUnits(self.unit_system)
