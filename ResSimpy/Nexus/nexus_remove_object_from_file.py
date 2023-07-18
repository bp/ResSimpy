from typing import Any
from uuid import UUID


class RemoveObjectOperations:

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
