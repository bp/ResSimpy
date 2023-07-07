from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID

import numpy as np
import pandas as pd
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nodes import Nodes
from typing import Sequence, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodes(Nodes):
    __nodes: list[NexusNode] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__nodes: list[NexusNode] = []

    def get_nodes(self) -> Sequence[NexusNode]:
        """Returns a list of nodes loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__nodes

    def get_node(self, node_name: str) -> Optional[NexusNode]:
        """Returns a single node with the provided name loaded from the simulator.

        Args:
        ----
            node_name (str): name of the requested node

        Returns:
        -------
            NexusNode: which has the same name as the requested node_name

        """
        nodes_to_return = filter(lambda x: False if x.name is None else x.name.upper() == node_name.upper(),
                                 self.__nodes)
        return next(nodes_to_return, None)

    def get_node_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed node data in a surface file
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
        """Calls load nodes and appends the list of discovered nodes into the NexusNodes object.

        Args:
            surface_file (NexusFile): NexusFile representation of the surface file.
            start_date (str): Starting date of the run
            default_units (UnitSystem): Units used in case not specified by surface file.

        Raises:
            TypeError: if the unit system found in the property check is not a valid enum UnitSystem.

        """
        new_nodes = collect_all_tables_to_objects(surface_file, {'NODES': NexusNode},
                                                  start_date=start_date,
                                                  default_units=default_units)
        cons_list = new_nodes.get('NODES')
        if isinstance(cons_list, dict):
            raise ValueError('Incompatible data format for additional wells. Expected type "list" instead got "dict"')
        self._add_nodes_to_memory(cons_list)

    def _add_nodes_to_memory(self, additional_list: Optional[list[NexusNode]]) -> None:
        """Extends the nodes object by a list of nodes provided to it.

        Args:
        ----
            additional_list (Sequence[NexusNode]): list of nexus nodes to add to the nodes list.

        Returns:
        -------
            None
        """
        if additional_list is None:
            return
        self.__nodes.extend(additional_list)

    def remove_node(self, node_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a node from the network based on the properties matching a dictionary or id.

        Args:
            node_to_remove (UUID | dict[str, None | str | float | int]): UUID of the node to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a node

        """
        # TODO make this method generic!
        network_file = self.__parent_network.model.model_files.surface_files[1]
        if network_file is None:
            raise ValueError(f'No file found for {network_file=}')

        if isinstance(node_to_remove, dict):
            name = node_to_remove.get('name', None)
            if name is None:
                raise ValueError(f'Require node name to remove the node instead got {name=}')
            name = str(name)
            node = self.__parent_network.find_node_with_dict(name, node_to_remove, 'nodes')
            node_id = node.id
        else:
            node_id = node_to_remove

        # remove from memory
        index_to_remove = [x.id for x in self.__nodes].index(node_id)
        self.__nodes.pop(index_to_remove)

        # remove from file
        if network_file.object_locations is None:
            raise ValueError(f'No object locations specified, cannot find node id: {node_id}')
        line_numbers_in_file = network_file.object_locations[node_id]
        if len(line_numbers_in_file) > 0:
            for index in line_numbers_in_file:
                network_file.remove_from_file_as_list(index, [node_id])
        # check there are any nodes left in the specified table
