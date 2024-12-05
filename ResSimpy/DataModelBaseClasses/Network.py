"""Abstract base class for holding the network data for holding all components of the production networks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ResSimpy.GenericContainerClasses.Constraints import Constraints
from ResSimpy.GenericContainerClasses.NetworkLists import NetworkLists
from ResSimpy.GenericContainerClasses.NodeConnections import NodeConnections
from ResSimpy.GenericContainerClasses.Nodes import Nodes
from ResSimpy.GenericContainerClasses.Targets import Targets
from ResSimpy.GenericContainerClasses.WellConnections import WellConnections
from ResSimpy.GenericContainerClasses.Wellbores import Wellbores
from ResSimpy.GenericContainerClasses.Wellheads import Wellheads


@dataclass(kw_only=True, init=False)
class Network(ABC):
    """Abstract base class for holding the network data, holding all components of the production networks."""
    nodes: Optional[Nodes]
    connections: Optional[NodeConnections]
    constraints: Optional[Constraints]
    targets: Optional[Targets] = None
    well_connections: Optional[WellConnections] = None
    wellheads: Optional[Wellheads] = None
    wellbores: Optional[Wellbores] = None
    welllists: Optional[NetworkLists] = None
    _has_been_loaded: bool = False

    def __init__(self, nodes: Optional[Nodes] = None, connections: Optional[NodeConnections] = None,
                 constraints: Optional[Constraints] = None, targets: Optional[Targets] = None,
                 well_connections: Optional[WellConnections] = None, wellheads: Optional[Wellheads] = None,
                 wellbores: Optional[Wellbores] = None, welllists: Optional[NetworkLists] = None,
                 assume_loaded: bool = False) -> None:
        """Initialising the Network Abstract Base class."""
        self._has_been_loaded = assume_loaded
        self.nodes = nodes
        self.connections = connections
        self.constraints = constraints
        self.well_connections = well_connections
        self.targets = targets
        self.wellbores = wellbores
        self.wellheads = wellheads
        self.welllists = welllists

    @abstractmethod
    def load(self) -> None:
        """Loads Network data."""
        raise NotImplementedError("Implement this in the derived class")

    def get_load_status(self) -> bool:
        """Checks load status and loads the network if it hasn't already been loaded."""
        if not self._has_been_loaded:
            self.load()
        return self._has_been_loaded
