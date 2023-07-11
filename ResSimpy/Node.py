from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class Node(ABC):
    name: Optional[str] = None
    type: Optional[str] = None
    depth: Optional[float] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None

    def to_dict(self) -> dict:
        raise NotImplementedError("Implement this in the derived class")

    def to_string(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
