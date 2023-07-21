from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class NodeConnection(ABC):
    name: Optional[str] = None
    date: Optional[str] = None
    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    def to_dict(self):
        raise NotImplementedError("Implement this in the derived class")

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each Node object."""
        return self.__id
