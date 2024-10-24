"""Holds the NexusNodes class which is used to store and manipulate the nodes in a NexusNetwork.

It is stored as an instance in the NexusNetwork class as "nodes".
"""

from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Sequence, Optional, TYPE_CHECKING

import pandas as pd

from ResSimpy.FileOperations.File import File
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.GenericContainerClasses.Nodes import Nodes
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodes(Nodes):
    """Class to store and manipulate the nodes in a NexusNetwork.

    It is stored as an instance in the NexusNetwork class as "nodes". A list of nodes in the network are stored in
    memory these can be accessed through the get_all method.
    """
    _nodes: list[NexusNode] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusNodes class.

        Args:
            parent_network (NexusNetwork): The network that the nodes are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self._nodes: list[NexusNode] = []
        self.__add_object_operations = AddObjectOperations(NexusNode, self.table_header, self.table_footer,
                                                           self.__parent_network.model)
        self.__remove_object_operations = RemoveObjectOperations(self.__parent_network, self.table_header,
                                                                 self.table_footer)
        self.__modify_object_operations = ModifyObjectOperations(self)

    @property
    def table_header(self) -> str:
        """Start of the Node definition table."""
        return 'NODES'

    @property
    def table_footer(self) -> str:
        """End of the Node definition table."""
        return 'ENDNODES'

    def get_all(self) -> Sequence[NexusNode]:
        """Returns a list of nodes loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self._nodes

    def get_by_name(self, node_name: str) -> Optional[NexusNode]:
        """Returns a single node with the provided name loaded from the simulator.

        Args:
        ----
            node_name (str): name of the requested node

        Returns:
        -------
            NexusNode: which has the same name as the requested node_name

        """
        nodes_to_return = filter(lambda x: False if x.name is None else x.name.upper() == node_name.upper(),
                                 self._nodes)
        return next(nodes_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed node data in a surface file.

        Returns:
            DataFrame: of the properties of the nodes through time with each row representing a node.
        """
        self.__parent_network.get_load_status()
        df_store = obj_to_dataframe(self._nodes)
        return df_store

    def get_overview(self) -> str:
        """Returns overview of the nodes."""
        raise NotImplementedError('To be implemented')

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        """Calls load nodes and appends the list of discovered nodes into the NexusNodes object.

        Args:
            surface_file (File): NexusFile representation of the surface file.
            start_date (str): Starting date of the run
            default_units (UnitSystem): Units used in case not specified by surface file.

        Raises:
            TypeError: if the unit system found in the property check is not a valid enum UnitSystem.

        """
        new_nodes, _ = collect_all_tables_to_objects(surface_file, {'NODES': NexusNode},
                                                     start_date=start_date,
                                                     default_units=default_units,
                                                     date_format=self.__parent_network.model.date_format)
        nodes_list = new_nodes.get('NODES')
        self._add_to_memory(nodes_list)

    def _add_to_memory(self, additional_list: Optional[list[NexusNode]]) -> None:
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
        self._nodes.extend(additional_list)

    def remove(self, node_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a node from the network based on the properties matching a dictionary or id.

        Args:
            node_to_remove (UUID | dict[str, None | str | float | int]): UUID of the node to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a node

        """
        self.__remove_object_operations.remove_object_from_network_main(
            node_to_remove, self._network_element_name, self._nodes)

    def add(self, node_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a node to a network, taking a dictionary with properties for the new node.

        Args:
            node_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the new node.
            Requires date and a node name.
        """
        new_object = self.__add_object_operations.add_network_obj(node_to_add, NexusNode, self.__parent_network)
        self._add_to_memory([new_object])

    def modify(self, node_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing node based on a matching dictionary of properties.

        Partial matches allowed if precisely 1 matching node is found. Updates the properties with properties in the
        new_properties dictionary.

        Args:
            node_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing node set.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new node
        """
        self.__parent_network.get_load_status()

        self.__modify_object_operations.modify_network_object(node_to_modify, new_properties,
                                                              self.__parent_network)
