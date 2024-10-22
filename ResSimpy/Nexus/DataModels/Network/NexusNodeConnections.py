"""Holds all the node connections in a network.

This class is responsible for loading, modifying and removing
connections from a network. It also holds the list of connections in memory.
An instance is held within the NexusNetwork class as "connections".
"""
from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID

import pandas as pd
from typing import Sequence, Optional, TYPE_CHECKING

from ResSimpy.FileOperations.File import File
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects

from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.DataModelBaseClasses.NodeConnection import NodeConnection
from ResSimpy.GenericContainerClasses.NodeConnections import NodeConnections
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodeConnections(NodeConnections):
    """Holds all the node connections in a network.

    This class is responsible for loading, modifying and removing connections from a network. It also holds the list
    of connections in memory.
    """
    _connections: list[NexusNodeConnection] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusNodeConnections class.

        Args:
            parent_network (NexusNetwork): The network that the connections are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self._connections: list[NexusNodeConnection] = []
        self.__add_object_operations = AddObjectOperations(NexusNodeConnection, self.table_header, self.table_footer,
                                                           self.__parent_network.model)
        self.__remove_object_operations = RemoveObjectOperations(self.__parent_network, self.table_header,
                                                                 self.table_footer)
        self.__modify_object_operations = ModifyObjectOperations(self)

    @property
    def table_header(self) -> str:
        """Start of the Node definition table."""
        return 'NODECON'

    @property
    def table_footer(self) -> str:
        """End of the Node definition table."""
        return 'END' + self.table_header

    def get_all(self) -> Sequence[NexusNodeConnection]:
        """Returns a collection of Nexus node connections."""
        self.__parent_network.get_load_status()
        return self._connections

    def get_by_name(self, connection_name: str) -> Optional[NodeConnection]:
        """Returns the node connection name.

        Args:
            connection_name(str): Node connection name
        """
        self.__parent_network.get_load_status()
        connections_to_return = filter(lambda x: False if x.name is None else x.name.upper() == connection_name.upper(),
                                       self._connections)
        return next(connections_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed node connection data in a surface file.

        Returns:
            DataFrame: of the properties of the connections through time with each row representing a node.
        """
        self.__parent_network.get_load_status()
        return obj_to_dataframe(self._connections)

    def get_overview(self) -> str:
        """Returns overview of Node connections."""
        raise NotImplementedError('To be implemented')

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        """Calls load connections and appends the list of discovered NodeConnections into the NexusNodeConnection \
            object.
        """
        new_connections, _ = collect_all_tables_to_objects(surface_file, {self.table_header: NexusNodeConnection},
                                                           start_date=start_date, default_units=default_units,
                                                           date_format=self.__parent_network.model.date_format)
        cons_list = new_connections.get(self.table_header)
        self._add_to_memory(cons_list)

    def _add_to_memory(self, additional_list: Optional[Sequence[NexusNodeConnection]]) -> None:
        """Extends the nodes object by a list of nodes provided to it.

        Args:
            additional_list (Sequence[NexusNodeConnection]): list of connections to add to the connection list.
        """
        if additional_list is None:
            return
        self._connections.extend(additional_list)

    def remove(self, obj_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a wellbore from the network based on the properties matching a dictionary or id.

        Args:
            obj_to_remove (UUID | dict[str, None | str | float | int]): UUID of the wellbore to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a wellbore

        """
        self.__remove_object_operations.remove_object_from_network_main(
            obj_to_remove, self._network_element_name, self._connections)

    def add(self, obj_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a connection to a network, taking a dictionary with properties for the new connection.

        Args:
            obj_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the new
            connection.
            Requires date and a name.
        """
        new_object = self.__add_object_operations.add_network_obj(obj_to_add, NexusNodeConnection,
                                                                  self.__parent_network)
        self._add_to_memory([new_object])

    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing connection based on a matching dictionary of properties.

        Partial matches allowed if precisely 1 matching node is found.
        Updates the properties with properties in the new_properties dictionary.

        Args:
            obj_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing connections.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new connection
        """
        self.__parent_network.get_load_status()
        self.__modify_object_operations.modify_network_object(obj_to_modify, new_properties,
                                                              self.__parent_network)
