from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from typing import Sequence, Optional, TYPE_CHECKING

from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
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
        new_connections = collect_all_tables_to_objects(surface_file, {'NODECON': NexusNodeConnection},
                                                        start_date=start_date, default_units=default_units)
        cons_list = new_connections.get('NODECON')
        if isinstance(cons_list, dict):
            raise ValueError(
                'Incompatible data format for additional nodecons. Expected type "list" instead got "dict"')
        self.add_connections(cons_list)

    def add_connections(self, additional_list: Optional[list[NexusNodeConnection]]):
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
