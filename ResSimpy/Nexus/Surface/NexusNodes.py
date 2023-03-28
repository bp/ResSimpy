from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Surface.NexusNode import NexusNode
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.Surface.load_nodes import load_nodes
from ResSimpy.Nodes import Nodes
from typing import Sequence, Optional


@dataclass(kw_only=True)
class NexusNodes(Nodes):
    __nodes: list[NexusNode] = field(default_factory=lambda: [])

    def get_nodes(self) -> Sequence[NexusNode]:
        """ Returns a list of nodes loaded from the simulator"""
        return self.__nodes

    def get_node(self, node_name: str) -> Optional[NexusNode]:
        """

        Args:
            node_name (str): name of the requested node

        Returns:
            NexusNode: which has the same name as the requested node_name

        """
        nodes_to_return = filter(lambda x: False if x.name is None else x.name.upper() == node_name.upper(),
                                 self.__nodes)
        return next(nodes_to_return, None)

    def get_node_df(self) -> pd.DataFrame:
        """ Creates a dataframe representing all processed node data in a surface file
        Returns:
            DataFrame: of the properties of the nodes through time with each row representing a node.
        """
        df_store = pd.DataFrame()
        for node in self.__nodes:
            df_row = pd.DataFrame(node.to_dict(), index=[0])
            df_store = pd.concat([df_store, df_row], axis=0, ignore_index=True)
        df_store = df_store.fillna(value=np.nan)
        df_store = df_store.dropna(axis=1, how='all')
        return df_store

    def get_nodes_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_nodes(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        """ Loads all nodes from a given surface file.

        Args:
            surface_file (NexusFile): NexusFile representation of the surface file.
            start_date (str): Starting date of the run
            default_units (UnitSystem): Units used in case not specified by surface file.
        Raises:
            TypeError: if the unit system found in the property check is not a valid enum UnitSystem

        """
        new_nodes = load_nodes(surface_file, start_date, default_units)
        self.__nodes += new_nodes
