"""Abstract base class for holding the network data for holding all components of the production networks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Mapping

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

    def get_all_linked_objects(self, object_name: str) -> dict[str, list[Any]]:
        """Gets a list of all the objects in the surface network linked to the specified object name.

        Args:
            object_name(str): The name of the object to search for.
        """
        linked_objects = {}

        if self.nodes is not None:
            linked_nodes = [x for x in self.nodes.get_all() if x.name == object_name]
            linked_objects['NODES'] = linked_nodes

        if self.connections is not None:
            linked_connections = [x for x in self.connections.get_all() if x.name == object_name]
            linked_objects['CONNECTIONS'] = linked_connections

        if self.constraints is not None:
            if isinstance(self.constraints.constraints, Mapping):
                linked_constraints = list(self.constraints.constraints[object_name])
            else:
                linked_constraints = [x for x in self.constraints.constraints if x.name == object_name]
            linked_objects['CONSTRAINTS'] = linked_constraints

        if self.welllists is not None:
            linked_well_lists = [x for x in self.welllists.lists if object_name in x.elements_in_the_list]
            linked_objects['WELLLISTS'] = linked_well_lists

            well_list_names = [x.name for x in linked_well_lists]

            if self.targets is not None:
                linked_targets = [x for x in self.targets.get_all() if x.control_connections in well_list_names]
                linked_objects['TARGETS'] = linked_targets

        if self.well_connections is not None:
            linked_well_connections = [x for x in self.well_connections.get_all() if x.name == object_name]
            linked_objects['WELL_CONNECTIONS'] = linked_well_connections

        if self.wellheads is not None:
            linked_well_heads = [x for x in self.wellheads.get_all() if x.well == object_name]
            linked_objects['WELLHEADS'] = linked_well_heads

        if self.wellbores is not None:
            linked_well_bores = [x for x in self.wellbores.get_all() if x.name == object_name]
            linked_objects['WELLBORES'] = linked_well_bores

        return linked_objects
