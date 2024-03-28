"""Abstract base class for holding the network data for holding all components of the production networks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Constraints import Constraints
from ResSimpy.NodeConnections import NodeConnections
from ResSimpy.Nodes import Nodes
from ResSimpy.Targets import Targets
from ResSimpy.WellConnections import WellConnections
from ResSimpy.WellLists import WellLists
from ResSimpy.Wellbores import Wellbores
from ResSimpy.Wellheads import Wellheads


@dataclass(kw_only=True, init=False)
class Network(ABC):
    """Abstract base class for holding the network data for holding all components of the production networks."""
    nodes: Optional[Nodes]
    connections: Optional[NodeConnections]
    constraints: Optional[Constraints]
    targets: Optional[Targets] = None
    well_connections: Optional[WellConnections] = None
    wellheads: Optional[Wellheads] = None
    wellbores: Optional[Wellbores] = None
    welllists: Optional[WellLists] = None
    __has_been_loaded: bool = False

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def get_load_status(self) -> bool:
        """Checks load status and loads the network if it hasn't already been loaded."""
        if not self.__has_been_loaded:
            self.load()
        return self.__has_been_loaded
