from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Node import Node


@dataclass(kw_only=True)
class NexusNode(Node):
    pass
