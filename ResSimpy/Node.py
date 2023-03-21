from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem


@dataclass
class Node(ABC):
    name: str
    type: Optional[str] = None
    depth: Optional[float] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
