from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Constraints import Constraints
from ResSimpy.NodeConnections import NodeConnections
from ResSimpy.Nodes import Nodes
from ResSimpy.Targets import Targets


@dataclass(kw_only=True, init=False)
class Network(ABC):
    nodes: Optional[Nodes]
    connections: Optional[NodeConnections]
    constraints: Optional[Constraints]
    targets: Optional[Targets]

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError("Implement this in the derived class")
