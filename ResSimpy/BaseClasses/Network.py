from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy.BaseClasses.Constraints import Constraints
from ResSimpy.BaseClasses.NodeConnections import NodeConnections
from ResSimpy.BaseClasses.Nodes import Nodes
from ResSimpy.BaseClasses.Targets import Targets


@dataclass(kw_only=True, init=False)
class Network(ABC):
    nodes: Nodes
    connections: NodeConnections
    constraints: Constraints
    targets: Targets

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError("Implement this in the derived class")
