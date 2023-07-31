from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID

import pandas as pd
from typing import Sequence, Optional, TYPE_CHECKING

from ResSimpy.File import File
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects

from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.NodeConnection import NodeConnection
from ResSimpy.NodeConnections import NodeConnections
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodeConnections(NodeConnections):
    __connections: list[NexusNodeConnection] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__connections: list[NexusNodeConnection] = []
        self.__add_object_operations = AddObjectOperations(self.__parent_network.model, self.table_header,
                                                           self.table_footer)
        self.__remove_object_operations = RemoveObjectOperations(self.table_header, self.table_footer)
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
        self.__parent_network.get_load_status()
        return self.__connections

    def get_by_name(self, connection_name: str) -> Optional[NodeConnection]:
        self.__parent_network.get_load_status()
        connections_to_return = filter(lambda x: False if x.name is None else x.name.upper() == connection_name.upper(),
                                       self.__connections)
        return next(connections_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed node connection data in a surface file
        Returns:
            DataFrame: of the properties of the connections through time with each row representing a node.
        """
        self.__parent_network.get_load_status()
        return obj_to_dataframe(self.__connections)

    def get_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        """Calls load connections and appends the list of discovered NodeConnections into the NexusNodeConnection \
            object.
        """
        new_connections = collect_all_tables_to_objects(surface_file, {self.table_header: NexusNodeConnection},
                                                        start_date=start_date, default_units=default_units)
        cons_list = new_connections.get(self.table_header)
        if isinstance(cons_list, dict):
            raise ValueError(
                'Incompatible data format for additional nodecons. Expected type "list" instead got "dict"')
        self._add_to_memory(cons_list)

    def _add_to_memory(self, additional_list: Optional[Sequence[NexusNodeConnection]]):
        """Extends the nodes object by a list of nodes provided to it.

        Args:
            additional_list (Sequence[NexusNodeConnection]): list of connections to add to the connection list.
        """
        if additional_list is None:
            return
        self.__connections.extend(additional_list)

    def add(self, connection_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a nodeconnection to a network, taking a dictionary with properties for the new node.

        Args:
            connection_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the
            new node connections. Requires date and a node name.
        """
        self.__parent_network.get_load_status()
        name, date = self.__add_object_operations.check_name_date(connection_to_add)

        new_object = NexusNodeConnection(connection_to_add)

        self._add_to_memory([new_object])

        file_to_add_to = self.__parent_network.get_network_file()

        file_as_list = file_to_add_to.get_flat_list_str_file
        if file_as_list is None:
            raise ValueError(f'No file content found in the surface file specified at {file_to_add_to.location}')

        self.__add_object_operations.add_object_to_file(date, file_as_list, file_to_add_to, new_object,
                                                        connection_to_add)

    def remove(self, connection_to_remove: UUID | dict[str, None | str | float | int]) -> None:
        """Remove a connection from the network based on the properties matching a dictionary or id.

        Args:
            connection_to_remove (UUID | dict[str, None | str | float | int]): UUID of the connection to remove
            or a dictionary with sufficient matching parameters to uniquely identify a node.
        """
        self.__parent_network.get_load_status()

        network_file = self.__parent_network.get_network_file()

        if isinstance(connection_to_remove, dict):
            name = connection_to_remove.get('name', None)
            if name is None:
                raise ValueError(f'Require connection name to remove the connection instead got {name=}')
            name = str(name)
            network_element = self.__parent_network.find_network_element_with_dict(name, connection_to_remove,
                                                                                   self._network_element_name)
            network_element_id = network_element.id
        else:
            network_element_id = connection_to_remove

        self.__remove_object_operations.remove_object_by_id(network_file, network_element_id, self.__connections)

    def modify(self, connection_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing connection based on a matching dictionary of properties (partial matches allowed if
        precisely 1 matching connection is found).
        Updates the properties with properties in the new_properties dictionary.

        Args:
            connection_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing connection set.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new connection
        """
        self.__parent_network.get_load_status()

        self.__modify_object_operations.modify_network_object(connection_to_modify, new_properties,
                                                              self.__parent_network)
