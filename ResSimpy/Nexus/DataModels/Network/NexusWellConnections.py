from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import numpy as np
import pandas as pd

from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
import ResSimpy.Nexus.nexus_file_operations as nfo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusWellConnections:
    __well_connections: list[NexusWellConnection] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork):
        self.parent_network: NexusNetwork = parent_network
        self.__well_connections: list[NexusWellConnection] = []

    def get_well_connections(self) -> list[NexusWellConnection]:
        """ Returns a list of well connections loaded from the simulator"""
        self.parent_network.get_load_status()
        return self.__well_connections

    def get_well_connection(self, name: str) -> Optional[NexusWellConnection]:
        """ Returns a single well connection with the provided name loaded from the simulator

        Args:
            name (str): name of the requested well connection

        Returns:
            NexusWellConnection: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self.__well_connections)
        return next(to_return, None)

    def get_well_connections_df(self) -> pd.DataFrame:
        """ Creates a dataframe representing all processed well connections data in a surface file
        Returns:
            DataFrame: of the properties of the well connections through time with each row representing a single well \
            connection
        """
        df_store = pd.DataFrame()
        for node in self.__well_connections:
            df_row = pd.DataFrame(node.to_dict(), index=[0])
            df_store = pd.concat([df_store, df_row], axis=0, ignore_index=True)
        df_store = df_store.fillna(value=np.nan)
        df_store = df_store.dropna(axis=1, how='all')
        return df_store

    def get_well_connections_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_well_connections(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        new_well_connections = nfo.collect_all_tables_to_objects(surface_file, {'WELLS': NexusWellConnection, },
                                                                 start_date=start_date,
                                                                 default_units=default_units)
        self.add_connections(new_well_connections.get('WELLS'))

    def add_connections(self, additional_list: Optional[list[NexusWellConnection]]) -> None:
        """ extends the nodes object by a list of nodes provided to it.

        Args:
            additional_list (Sequence[NexusWellConnection]): list of nexus nodes to add to the nodes list.

        Returns:
            None
        """
        if additional_list is None:
            return
        self.__well_connections.extend(additional_list)
