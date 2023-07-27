from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataObjectMixin import DataObjectMixin


@dataclass
class Wellbore(DataObjectMixin, ABC):
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    name: Optional[str] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    roughness: Optional[float] = None
