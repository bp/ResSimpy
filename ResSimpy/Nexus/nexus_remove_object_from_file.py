from typing import Any
from uuid import UUID

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile


class RemoveObjectOperations:
    def __init__(self, table_header: str, table_footer: str) -> None:
        self.table_header = table_header
        self.table_footer = table_footer

    @staticmethod
    def remove_object_from_memory_by_id(list_obj: list[Any], id_to_remove: UUID) -> tuple[Any, list[Any]]:
        """Directly removes an object from a list of objects based on the id attribute of that object."""
        if len(list_obj) == 0:
            raise ValueError('Tried to remove object from empty list. Cannot remove object.')

        if not hasattr(list_obj[0], 'id'):
            raise AttributeError(f'Objects provided in {list_obj} has no attribute id.')

        index_to_remove = [x.id for x in list_obj].index(id_to_remove)
        object_removed = list_obj.pop(index_to_remove)
        return object_removed, list_obj

    def check_for_empty_table(self, file: NexusFile, first_obj_index: int,
                              last_object_index: int, id: UUID) -> list[int]:
        """Identifies the lines needed to be removed if the table is empty.

        Args:
            file ():
            first_obj_index ():
            last_object_index ():
            id ():

        Returns:
            A list of integers with the lines to remove from the file if the resulting table is empty after the lines\
             associated with the removed object is removed
        """
        additional_indices_to_remove = []
        remove_table = True
        # get all the indices for the tables:
        file_content = file.get_flat_list_str_file
        start_node_keyword_index_to_remove = max([i for i, x in enumerate(file_content) if self.table_header in x and
                                                  i < first_obj_index])
        end_node_keyword_index_to_remove = min([i for i, x in enumerate(file_content) if self.table_footer in x and
                                                i > last_object_index])
        # check there are any nodes left in the specified table
        if file.object_locations is None:
            raise ValueError(f'No object locations specified, cannot find id: {id} in {file.object_locations}')

        for obj_uuid, line_locations_list in file.object_locations.items():
            if obj_uuid == id:
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
