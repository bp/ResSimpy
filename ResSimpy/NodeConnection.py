from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class NodeConnection(ABC):
    name: Optional[str] = None
    date: Optional[str] = None
    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None

    def to_dict(self):
        raise NotImplementedError("Implement this in the derived class")
