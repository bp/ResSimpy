from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from typing import Sequence, Optional

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.Surface.load_connections import load_connections
from ResSimpy.NodeConnection import NodeConnection
from ResSimpy.NodeConnections import NodeConnections


@dataclass(kw_only=True)
class NexusNodeConnections(NodeConnections):
    __connections: list[NodeConnection] = field(default_factory=lambda: [])

    def get_connections(self) -> Sequence[NodeConnection]:
        return self.__connections

    def get_connection(self, connection_name: str) -> Optional[NodeConnection]:
        connections_to_return = filter(lambda x: False if x.name is None else x.name.upper() == connection_name.upper(),
                                       self.__connections)
        return next(connections_to_return, None)

    def get_connection_df(self) -> pd.DataFrame:
        """ Creates a dataframe representing all processed node connection data in a surface file
        Returns:
            DataFrame: of the properties of the Connections through time with each row representing a node.
        """
        df_store = pd.DataFrame()
        for connection in self.__connections:
            df_row = pd.DataFrame(connection.to_dict(), index=[0])
            df_store = pd.concat([df_store, df_row], axis=0, ignore_index=True)
        df_store = df_store.fillna(value=np.nan)
        df_store = df_store.dropna(axis=1, how='all')
        return df_store

    def get_connections_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_connections(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        """ Calls load connections and appends the list of discovered NodeConnections into the NexusNodeConnection \
            object
        """
        new_connections = load_connections(surface_file, start_date, default_units)
        self.__connections += new_connections
