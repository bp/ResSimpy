from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional
import uuid

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class Wellbore(ABC):
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    name: Optional[str] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    roughness: Optional[float] = None

    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    def to_dict(self):
        raise NotImplementedError("Implement this in the derived class")

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each Node object."""
        return self.__id
