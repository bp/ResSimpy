from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.DataObjectMixin import DataObjectMixin


@dataclass
class NodeConnection(DataObjectMixin, ABC):
    name: Optional[str] = None
    date: Optional[str] = None
    node_in: Optional[str] = None
    node_out: Optional[str] = None
    con_type: Optional[str] = None
    depth: Optional[float] = None
