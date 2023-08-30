from __future__ import annotations
from uuid import uuid4, UUID
from dataclasses import dataclass, field
from typing import Optional
from ResSimpy.FileBase import FileBase
import uuid


@dataclass
class File(FileBase):
    """The abstract base class for simulator files.

    Attributes:
        location (str): Full path to file location
        file_content_as_list (list[str]): List of lines in the file
    """

    location: Optional[str] = None
    file_content_as_list: Optional[list[str]] = field(default=None, repr=False)
    __id: UUID = field(default_factory=lambda: uuid4(), compare=False)
    __file_modified: bool = False

    def __init__(self, location: Optional[str] = None,
                 file_content_as_list: Optional[list[str]] = None) -> None:

        self.location = location
        if file_content_as_list is None:
            self.file_content_as_list = []
        else:
            self.file_content_as_list = file_content_as_list
        self.__id = uuid.uuid4()
        self.__file_modified = False

    def write_to_file(self, new_file_path: None | str = None) -> None:
        """Writes to file specified in self.location the strings contained in the list self.file_content_as_list.

        Args:
            new_file_path (None | str): writes to self.location if left as None. Otherwise writes to new_file_name.
        """
        if new_file_path is not None:
            self.location = new_file_path
        if self.location is None:
            raise ValueError(f'No file path to write to, instead found {self.location}')
        if self.file_content_as_list is None:
            raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')
        file_str = ''.join(self.file_content_as_list)

        with open(self.location, 'w') as fi:
            fi.write(file_str)

        # reset the modified file state
        self.__file_modified = False

    @property
    def id(self) -> UUID:
        """Unique identifier for each Node object."""
        return self.__id

    @property
    def file_modified(self) -> bool:
        return self.__file_modified

    def _file_modified_set(self, value: bool) -> None:
        self.__file_modified = value

    @property
    def get_flat_list_str_file(self) -> list[str]:
        raise NotImplementedError("Implement this in the derived class")

    def add_object_locations(self, obj_uuid: UUID, line_indices: list[int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @staticmethod
    def insert_comments(additional_content: list[str], comments) -> list[str]:
        raise NotImplementedError("Implement this in the derived class")

    def get_object_locations_for_id(self, obj_id: UUID) -> list[int]:
        raise NotImplementedError("Implement this in the derived class")

    def remove_object_from_file_as_list(self, objects_to_remove: list[UUID]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def add_to_file_as_list(self, additional_content: list[str], index: int,
                            additional_objects: Optional[dict[UUID, list[int]]] = None,
                            comments: Optional[str] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def remove_from_file_as_list(self, index: int, objects_to_remove: Optional[list[UUID]] = None,
                                 string_to_remove: Optional[str] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def find_which_include_file(self, flattened_index: int) -> tuple[File, int]:
        raise NotImplementedError("Implement this in the derived class")
