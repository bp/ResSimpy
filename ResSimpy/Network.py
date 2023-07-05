from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy.Constraints import Constraints
from ResSimpy.NodeConnections import NodeConnections
from ResSimpy.Nodes import Nodes


@dataclass(kw_only=True, init=False)
class Network(ABC):
    nodes: Nodes
    connections: NodeConnections
    constraints: Constraints

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError("Implement this in the derived class")
