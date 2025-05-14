"""Abstract base class for holding the network data for holding all components of the production networks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple, Sequence

from ResSimpy.DataModelBaseClasses.NodeConnection import NodeConnection
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

    def get_connected_objects(self, connection_name: str) -> Tuple[list[NodeConnection], list[NodeConnection]]:
        """Returns a list of all objects connected to a node in a surface network.
        x"""

        all_connections = self.connections.get_all()
        connection_to_check = self.connections.get_by_name(connection_name=connection_name)

        connections_directly_before_connection = [x for x in all_connections if
                                                  x.node_out == connection_name and x.name != connection_name]

        # Add the in connection directly referenced by the connection itself if it is missing
        if connection_to_check.node_in != connection_name:
            node_in_connection = self.connections.get_by_name(connection_name=connection_to_check.node_in)
            if node_in_connection is not None and node_in_connection not in connections_directly_before_connection:
                connections_directly_before_connection.append(node_in_connection)

        connections_directly_after_connection = [x for x in all_connections if
                                                 x.node_in == connection_name and x.name != connection_name]

        # Add the out connection directly referenced by the connection itself if it is missing
        if connection_to_check.node_out != connection_name:
            node_out_connection = self.connections.get_by_name(connection_name=connection_to_check.node_out)
            if node_out_connection is not None and node_out_connection not in connections_directly_after_connection:
                connections_directly_after_connection.append(node_out_connection)

        connections_in = self.__get_linked_connections(all_connections=all_connections,
                                                       direct_connections=connections_directly_before_connection,
                                                       search_upwards=True)

        # Reverse the order of the in connections to keep the order from 'top to bottom' in the network
        connections_in = connections_in[::-1]

        connections_out = self.__get_linked_connections(all_connections=all_connections,
                                                        direct_connections=connections_directly_after_connection,
                                                        search_upwards=False)

        return connections_in, connections_out

    def __get_linked_connections(self, all_connections: Sequence[NodeConnection],
                                 direct_connections: list[NodeConnection], search_upwards: bool):

        endpoints = ['GAS', 'SINK', 'WATER', 'IPR-SOURCE', 'IPR-SINK']
        found_connections = []

        for current_node in direct_connections:
            next_node_name = current_node.name
            while next_node_name not in endpoints and next_node_name not in [x.name for x in found_connections]:
                next_node = self.connections.get_by_name(connection_name=next_node_name)
                found_connections.append(next_node)

                if search_upwards:
                    if next_node.node_in != next_node.name:
                        next_node_name = next_node.node_in
                    else:
                        # Find the connection linked to this node via 'node_out' on another connection instead
                        next_node_found = False
                        for connection in all_connections:
                            if connection.node_out == next_node.name:
                                next_node_name = connection.name
                                next_node_found = True
                                break

                        if not next_node_found:
                            break

                else:
                    if next_node.node_out != next_node.name:
                        next_node_name = next_node.node_out
                    else:
                        # Find the connection linked to this node via 'node_in' on another connection instead
                        next_node_found = False
                        for connection in all_connections:
                            if connection.node_in == next_node.name:
                                next_node_name = connection.name
                                next_node_found = True
                                break

                        if not next_node_found:
                            break

        return found_connections
