from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.Node import Node


@dataclass
class NodeConnection(ABC):
    name: str
    node_in: Optional[Node] = None
    node_out: Optional[Node] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None
