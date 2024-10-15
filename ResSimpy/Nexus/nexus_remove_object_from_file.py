"""A class built for removing an object from a file and from the list of objects."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Literal, TypeVar, Optional
from uuid import UUID

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
T = TypeVar('T', bound=DataObjectMixin)

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


class RemoveObjectOperations:
    def __init__(self, network: Optional[NexusNetwork], table_header: str, table_footer: str) -> None:
        """Initialises the RemoveObjectOperations class.

        Args:
            network (Optional[NexusNetwork]): NexusNetwork object to remove the object from.
            table_header (str): The string that represents the start of the table in the file.
            table_footer (str): The string that represents the end of the table in the file.
        """
        self.table_header = table_header
        self.table_footer = table_footer
        self.__network = network

    @staticmethod
    def remove_object_from_memory_by_id(list_obj: list[T], id_to_remove: UUID) -> tuple[Any, list[Any]]:
        """Directly removes an object from a list of objects based on the id attribute of that object."""
        if len(list_obj) == 0:
            raise ValueError('Tried to remove object from empty list. Cannot remove object.')

        if not hasattr(list_obj[0], 'id'):
            raise AttributeError(f'Objects provided in {list_obj} has no attribute id.')

        index_to_remove = [x.id for x in list_obj].index(id_to_remove)
        object_removed = list_obj.pop(index_to_remove)
        return object_removed, list_obj

    def check_for_empty_table(self, file: NexusFile, line_numbers_in_file_to_remove: list[int], obj_id: UUID) \
            -> list[int]:
        """Identifies the lines needed to be removed if the table is empty.

        Args:
            file (NexusFile): file to check
            line_numbers_in_file_to_remove (list[int]): list of line indices for the object being removed
            obj_id (UUID): id of the object being removed

        Returns:
            A list of integers with the lines to remove from the file if the resulting table is empty after the lines\
             associated with the removed object is removed
        """
        first_obj_index = line_numbers_in_file_to_remove[0]
        last_obj_index = line_numbers_in_file_to_remove[-1]
        additional_indices_to_remove = []
        remove_table = True
        # get all the indices for the tables:
        file_content = file.get_flat_list_str_file
        start_node_keyword_index_to_remove = max([i for i, x in enumerate(file_content) if self.table_header in x and
                                                  i < first_obj_index])
        end_node_keyword_index_to_remove = min([i for i, x in enumerate(file_content) if self.table_footer in x and
                                                i > last_obj_index])
        # check there are any nodes left in the specified table
        if file.object_locations is None:
            raise ValueError(f'No object locations specified, cannot find id: {obj_id} in {file.object_locations}')

        for obj_uuid, line_locations_list in file.object_locations.items():
            if obj_uuid == obj_id:
                # ignore the uuid's for the node that we want to remove
                continue
            for value in line_locations_list:
                # if we find an object in the middle of the table then don't remove it
                if start_node_keyword_index_to_remove <= value <= end_node_keyword_index_to_remove:
                    remove_table = False
                    break
        if remove_table:
            additional_indices_to_remove = list(range(start_node_keyword_index_to_remove,
                                                      end_node_keyword_index_to_remove + 1))
        return additional_indices_to_remove

    def remove_lines_from_file(self, line_numbers_in_file_to_remove: list[int], file: NexusFile, obj_id: UUID) -> None:
        """Removes lines from the file content and removes any references to the object in the line locations in the \
        file.

        Args:
            line_numbers_in_file_to_remove (list[int]): line indices to be removed. Relative to the flattened file.
            file (NexusFile): NexusFile to remove the lines from. Lines nested in files will be resolved correctly.
            obj_id (UUID): id of the object being removed
        """
        # get unique line numbers + sort them in descending order
        line_numbers_in_file_to_remove = list(set(line_numbers_in_file_to_remove))
        line_numbers_in_file_to_remove.sort(reverse=True)
        # remove the lines
        for index, line_in_file in enumerate(line_numbers_in_file_to_remove):
            if index == 0:
                file.remove_from_file_as_list(line_in_file, [obj_id])
            else:
                file.remove_from_file_as_list(line_in_file)

    def remove_object_by_id(self, file: NexusFile, obj_id: UUID, obj_list: list[T]) -> None:
        """Remove an object from a file and from the list of stored objects.

        Args:
            file (NexusFile): file to remove the lines associated with the obj from.
            obj_id (UUID): id of the object being removed.
            obj_list (list[Any]): list of corresponding objects.
        """
        # remove from memory
        self.remove_object_from_memory_by_id(obj_list, id_to_remove=obj_id)
        # remove from file
        line_numbers_in_file_to_remove = file.get_object_locations_for_id(obj_id)
        # get table_header and footers
        remove_empty_table_indices = self.check_for_empty_table(
            file, line_numbers_in_file_to_remove, obj_id)
        # remove the table if there aren't any more remaining
        line_numbers_in_file_to_remove.extend(remove_empty_table_indices)
        self.remove_lines_from_file(line_numbers_in_file_to_remove, file, obj_id)

    def remove_object_from_network_main(self, obj_to_remove: dict[str, None | str | float | int] | UUID,
                                        network_element_name: Literal['nodes', 'connections', 'well_connections',
                                                                      'wellheads', 'wellbores', 'constraints',
                                                                      'targets'],
                                        existing_objects: list[T]) -> None:
        """Removes object from file and from the list of objects based on matching a set of attributes provided in a \
        dictionary or a unique id.

        Args:
            obj_to_remove (dict[str, None | str | float | int] | UUID): dictionary of properties for identifying which
            object to remove. Can also take an object id.
            network_element_name (str): One of: 'nodes', 'connections', 'well_connections', 'wellheads', 'wellbores',
            'constraints'. Identifies the attribute name of the element inside the network
            existing_objects (list[T]): list of all existing network objects for the network element. e.g. self.__nodes
        """
        if self.__network is None:
            raise ValueError('No network provided for removing objects from.'
                             'Cannot remove an object from something that does not exist')
        self.__network.get_load_status()
        network_file = self.__network.get_network_file()
        if isinstance(obj_to_remove, dict):
            name = obj_to_remove.get('name', None)
            if name is None:
                raise ValueError(f'Require node name to remove the node instead got {name=}')
            name = str(name)
            obj_in_network = self.__network.find_network_element_with_dict(name, obj_to_remove,
                                                                           network_element_name)
            obj_id = obj_in_network.id
        else:
            obj_id = obj_to_remove
        self.remove_object_by_id(network_file, obj_id, existing_objects)
