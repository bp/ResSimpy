from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class Node(ABC):
    name: Optional[str] = None
    type: Optional[str] = None
    depth: Optional[float] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    def to_dict(self) -> dict:
        raise NotImplementedError("Implement this in the derived class")

    def to_table_line(self, headers: list[str]) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each Node object."""
        return self.__id
