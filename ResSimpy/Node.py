from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from ResSimpy import NodeConnection


@dataclass
class Node(ABC):
    name: str
    node_type: Optional[str] = None
    depth: Optional[float] = None
    connection: Optional[list[NodeConnection]] = None
