from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID

import pandas as pd
from typing import Sequence, Optional, TYPE_CHECKING

from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
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

    @property
    def table_header(self) -> str:
        """Start of the Node definition table."""
        return 'NODECON'

    @property
    def table_footer(self) -> str:
        """End of the Node definition table."""
        return 'END' + self.table_header

    def get_connections(self) -> Sequence[NexusNodeConnection]:
        self.__parent_network.get_load_status()
        return self.__connections

    def get_connection(self, connection_name: str) -> Optional[NodeConnection]:
        self.__parent_network.get_load_status()
        connections_to_return = filter(lambda x: False if x.name is None else x.name.upper() == connection_name.upper(),
                                       self.__connections)
        return next(connections_to_return, None)

    def get_connection_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed node connection data in a surface file
        Returns:
            DataFrame: of the properties of the connections through time with each row representing a node.
        """
        self.__parent_network.get_load_status()
        return obj_to_dataframe(self.__connections)

    def get_connections_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_connections(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        """Calls load connections and appends the list of discovered NodeConnections into the NexusNodeConnection \
            object.
        """
        new_connections = collect_all_tables_to_objects(surface_file, {self.table_header: NexusNodeConnection},
                                                        start_date=start_date, default_units=default_units)
        cons_list = new_connections.get(self.table_header)
        if isinstance(cons_list, dict):
            raise ValueError(
                'Incompatible data format for additional nodecons. Expected type "list" instead got "dict"')
        self._add_connections_to_memory(cons_list)

    def _add_connections_to_memory(self, additional_list: Optional[list[NexusNodeConnection]]):
        """Extends the nodes object by a list of nodes provided to it.

        Args:
        ----
            additional_list (Sequence[NexusNodeConnection]): list of nexus connections to add to the connection list.

        Returns:
        -------
            None
        """
        if additional_list is None:
            return
        self.__connections.extend(additional_list)

    def add_connection(self, connection_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a nodeconnection to a network, taking a dictionary with properties for the new node.

        Args:
            connection_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the
            new node connections. Requires date and a node name.
        """
        self.__parent_network.get_load_status()
        name, date = self.__add_object_operations.check_name_date(connection_to_add)

        new_object = NexusNodeConnection(connection_to_add)

        self._add_connections_to_memory([new_object])

        file_to_add_to = self.__parent_network.get_network_file()

        file_as_list = file_to_add_to.get_flat_list_str_file
        if file_as_list is None:
            raise ValueError(f'No file content found in the surface file specified at {file_to_add_to.location}')

        self.__add_object_operations.add_object_to_file(date, file_as_list, file_to_add_to, new_object,
                                                        connection_to_add)

    def remove_connection(self, node_to_remove: UUID | dict[str, None | str | float | int]) -> None:
        pass
