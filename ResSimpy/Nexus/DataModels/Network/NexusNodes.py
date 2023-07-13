from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID

import numpy as np
import pandas as pd

from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nodes import Nodes
from typing import Sequence, Optional, TYPE_CHECKING
import ResSimpy.Nexus.nexus_file_operations as nfo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodes(Nodes):
    __nodes: list[NexusNode] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__nodes: list[NexusNode] = []
        self.__add_object_operations = AddObjectOperations(self.__parent_network.model)

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
        self.__parent_network.get_load_status()
        if self.__parent_network.model.model_files.surface_files is None:
            raise ValueError('No files found for the surface network')
        network_file = self.__parent_network.model.model_files.surface_files[1]
        if network_file is None:
            raise ValueError(f'No file found for {network_file=}')

        if isinstance(node_to_remove, dict):
            name = node_to_remove.get('name', None)
            if name is None:
                raise ValueError(f'Require node name to remove the node instead got {name=}')
            name = str(name)
            node = self.__parent_network.find_network_element_with_dict(name, node_to_remove, 'nodes')
            node_id = node.id
        else:
            node_id = node_to_remove

        # remove from memory
        index_to_remove = [x.id for x in self.__nodes].index(node_id)
        self.__nodes.pop(index_to_remove)
        # remove from file
        if network_file.object_locations is None:
            raise ValueError(f'No object locations specified, cannot find node id: {node_id}')
        line_numbers_in_file_to_remove = network_file.object_locations[node_id]

        # check there are any nodes left in the specified table
        if len(line_numbers_in_file_to_remove) == 0:
            raise ValueError('error msg')
        # remove the table if there aren't any more remaining
        file_content = network_file.get_flat_list_str_file
        start_node_table_indices = [i for i, x in enumerate(file_content) if "NODES" in x and
                                    i < line_numbers_in_file_to_remove[0]]
        end_node_table_indices = [i for i, x in enumerate(file_content) if "ENDNODES" in x and
                                  i > line_numbers_in_file_to_remove[-1]]
        start_node_keyword_index_to_remove = start_node_table_indices[-1]
        end_node_keyword_index_to_remove = end_node_table_indices[0]

        remove_table = True

        for obj_uuid, line_locations_list in network_file.object_locations.items():
            if obj_uuid == node_id:
                # ignore the uuid's for the node that we want to remove
                continue
            for value in line_locations_list:
                if start_node_keyword_index_to_remove <= value <= end_node_keyword_index_to_remove:
                    remove_table = False

        if remove_table:
            line_numbers_in_file_to_remove.extend(list(
                range(start_node_keyword_index_to_remove, end_node_keyword_index_to_remove + 1)))

        line_numbers_in_file_to_remove = list(set(line_numbers_in_file_to_remove))
        line_numbers_in_file_to_remove.sort(reverse=True)
        for index, line_in_file in enumerate(line_numbers_in_file_to_remove):
            if index == 0:
                network_file.remove_from_file_as_list(line_in_file, [node_id])
            else:
                network_file.remove_from_file_as_list(line_in_file)

    def add_node(self, node_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a node to a network, taking a dictionary with properties for the new node.

        Args:
            node_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the new node.
            Requires date and a node name.
        """
        self.__parent_network.get_load_status()
        name, date = self.__add_object_operations.check_name_date(node_to_add)

        new_object = NexusNode(node_to_add)

        self._add_nodes_to_memory([new_object])

        # add to the file
        if self.__parent_network.model.model_files.surface_files is None:
            raise FileNotFoundError('No well file found, cannot modify a deck with an empty surface file.')
        file_to_add_to = self.__parent_network.model.model_files.surface_files[1]

        file_as_list = file_to_add_to.get_flat_list_str_file
        if file_as_list is None:
            raise ValueError(f'No file content found in the surface file specified at {file_to_add_to.location}')

        # get the start and end table names
        table_start_token = new_object.table_header
        table_ending_token = new_object.table_footer

        additional_content: list[str] = []
        date_comparison: int = -1
        date_index: int = -1
        insert_line_index: int = -1
        id_line_locs: list[int] = []
        headers: list[str] = []
        additional_headers: list[str] = []
        header_index: int = -1
        last_valid_line_index: int = -1
        headers_original: list[str] = []
        date_found = False
        nexus_mapping = new_object.get_nexus_mapping()

        for index, line in enumerate(file_as_list):
            # check for the dates
            if nfo.check_token('TIME', line):
                date_found_in_file = nfo.get_expected_token_value('TIME', line, [line])
                date_comparison = self.__parent_network.model._sim_controls.compare_dates(
                    date_found_in_file, date)
                if date_comparison == 0:
                    date_index = index
                    date_found = True
                    continue

            # find a table that exists in that date
            if nfo.check_token(table_start_token, line) and date_index != -1:
                # get the header of the table
                header_index, headers, headers_original = self.__add_object_operations.get_and_write_new_header(
                    additional_headers, node_to_add, file_as_list, index, nexus_mapping, file_to_add_to
                    )
                continue

            if header_index != -1 and index > header_index:
                # check for valid rows + fill extra columns with NA
                line_valid_index = self.__add_object_operations.fill_in_nas(additional_headers, headers_original, index,
                                                                            line, file_to_add_to, file_as_list)
                # set the line to insert the new completion at to be the one after the last valid line
                last_valid_line_index = line_valid_index if line_valid_index > 0 else last_valid_line_index

            # if we've found an existing table then just insert the new object
            if nfo.check_token(table_ending_token, line) and date_comparison == 0:
                insert_line_index = index
                additional_content.append(new_object.to_string(headers=headers))
                id_line_locs = [insert_line_index]

            # if we have passed the date or if we're at the end of the file write out the table
            if date_comparison > 0:
                new_table, obj_in_table_index = self.__add_object_operations.write_out_new_table_containing_object(
                    obj_date=date, object_properties=node_to_add, date_found=date_found, new_obj=new_object)
                additional_content.extend(new_table)
                insert_line_index = index
                id_line_locs = [obj_in_table_index + index-1]

            if insert_line_index >= 0:
                break
        else:
            # if we've finished the loop normally that means we haven't added any additional objects or lines
            # This means we have to add the date and a new table to the end of the file.
            new_table, obj_in_table_index = self.__add_object_operations.write_out_new_table_containing_object(
                obj_date=date, object_properties=node_to_add, date_found=date_found, new_obj=new_object)
            additional_content.extend(new_table)
            insert_line_index = len(file_as_list)
            id_line_locs = [obj_in_table_index + insert_line_index - 1]
        # write out to the file_content_as_list
        new_object_ids = {
            new_object.id: id_line_locs
            }
        file_to_add_to.add_to_file_as_list(additional_content=additional_content, index=insert_line_index,
                                           additional_objects=new_object_ids)
