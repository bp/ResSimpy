from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataObjectMixin import DataObjectMixin


@dataclass
class Node(DataObjectMixin, ABC):
    name: Optional[str] = None
    type: Optional[str] = None
    depth: Optional[float] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
