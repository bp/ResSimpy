from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils.generic_repr import generic_repr


@dataclass
class Constraint(ABC):
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
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError("Implement this in the derived class")

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each Node object."""
        return self.__id

    def new_id(self):
        """Refreshes the id on the object."""
        self.__id = uuid.uuid4()

    def __repr__(self) -> str:
        return generic_repr(self)
