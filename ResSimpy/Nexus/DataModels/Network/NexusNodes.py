from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Sequence, Optional, TYPE_CHECKING

import pandas as pd

from ResSimpy.File import File
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.Nodes import Nodes
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodes(Nodes):
    __nodes: list[NexusNode] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__nodes: list[NexusNode] = []
        self.__add_object_operations = AddObjectOperations(self.__parent_network.model, self.table_header,
                                                           self.table_footer)
        self.__remove_object_operations = RemoveObjectOperations(self.table_header, self.table_footer)
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
        return self.__nodes

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
                                 self.__nodes)
        return next(nodes_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed node data in a surface file
        Returns:
            DataFrame: of the properties of the nodes through time with each row representing a node.
        """
        df_store = obj_to_dataframe(self.__nodes)
        return df_store

    def get_overview(self) -> str:
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
        new_nodes = collect_all_tables_to_objects(surface_file, {'NODES': NexusNode},
                                                  start_date=start_date,
                                                  default_units=default_units)
        cons_list = new_nodes.get('NODES')
        if isinstance(cons_list, dict):
            raise ValueError('Incompatible data format for additional wells. Expected type "list" instead got "dict"')
        self._add_to_memory(cons_list)

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
        self.__nodes.extend(additional_list)

    def remove(self, node_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a node from the network based on the properties matching a dictionary or id.

        Args:
            node_to_remove (UUID | dict[str, None | str | float | int]): UUID of the node to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a node

        """
        self.__parent_network.get_load_status()

        network_file = self.__parent_network.get_network_file()

        if isinstance(node_to_remove, dict):
            name = node_to_remove.get('name', None)
            if name is None:
                raise ValueError(f'Require node name to remove the node instead got {name=}')
            name = str(name)
            node = self.__parent_network.find_network_element_with_dict(name, node_to_remove,
                                                                        self._network_element_name)
            node_id = node.id
        else:
            node_id = node_to_remove

        self.__remove_object_operations.remove_object_by_id(network_file, node_id, self.__nodes)

    def add(self, node_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a node to a network, taking a dictionary with properties for the new node.

        Args:
            node_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the new node.
            Requires date and a node name.
        """
        self.__parent_network.get_load_status()
        name, date = self.__add_object_operations.check_name_date(node_to_add)

        new_object = NexusNode(node_to_add)

        self._add_to_memory([new_object])

        file_to_add_to = self.__parent_network.get_network_file()

        file_as_list = file_to_add_to.get_flat_list_str_file
        if file_as_list is None:
            raise ValueError(f'No file content found in the surface file specified at {file_to_add_to.location}')

        self.__add_object_operations.add_object_to_file(date, file_as_list, file_to_add_to, new_object, node_to_add)

    def modify(self, node_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing node based on a matching dictionary of properties (partial matches allowed if precisely
         1 matching node is found). Updates the properties with properties in the new_properties dictionary.

        Args:
            node_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing node set.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new node
        """
        self.__parent_network.get_load_status()

        self.__modify_object_operations.modify_network_object(node_to_modify, new_properties,
                                                              self.__parent_network)
