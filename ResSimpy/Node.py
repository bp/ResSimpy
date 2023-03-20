from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node(ABC):
    name: str
    type: Optional[str] = None
    depth: Optional[float] = None
