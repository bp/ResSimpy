from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional
import uuid

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class Wellhead(ABC):
    well: Optional[str] = None
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    wellhead_type: Optional[str] = None
    depth: Optional[float] = None
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each Node object."""
        return self.__id

    def to_dict(self):
        raise NotImplementedError("Implement this in the derived class")
