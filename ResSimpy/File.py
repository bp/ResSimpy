"""This module contains the abstract base class for file manipulations for simulator files."""
from __future__ import annotations
import os
from uuid import uuid4, UUID
from dataclasses import dataclass, field
from typing import Optional
import warnings
from ResSimpy.FileBase import FileBase
import uuid

from ResSimpy.Utils.factory_methods import get_empty_list_file


@dataclass
class File(FileBase):
    """The abstract base class for simulator files.

    Attributes:
        location (str): Full path to file location
        file_content_as_list (list[str]): List of lines in the file
    """

    location: str
    file_content_as_list: Optional[list[str]] = field(default=None, repr=False)
    include_objects: Optional[list[File]] = field(default=None, repr=False)
    __id: UUID = field(default_factory=lambda: uuid4(), compare=False)
    __file_modified: bool = False

    def __init__(self, location: str,
                 file_content_as_list: Optional[list[str]] = None,
                 include_objects: Optional[list[File]] = None, create_as_modified: bool = False) -> None:

        self.location = location
        self.include_objects: Optional[list[File]] = get_empty_list_file() \
            if include_objects is None else include_objects
        if file_content_as_list is None:
            self.file_content_as_list = []
        else:
            self.file_content_as_list = file_content_as_list
        self.__id = uuid.uuid4()
        self.__file_modified = create_as_modified

    # def write_to_file(self, new_file_path: None | str = None) -> None:
    #     """Writes to file specified in self.location the strings contained in the list self.file_content_as_list.

    #     Args:
    #         new_file_path (None | str): writes to self.location if left as None. Otherwise writes to new_file_name.
    #     """
    #     if new_file_path is not None:
    #         self.location = new_file_path
    #     if self.location is None:
    #         raise ValueError(f'No file path to write to, instead found {self.location}')
    #     if self.file_content_as_list is None:
    #         raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')
    #     file_str = ''.join(self.file_content_as_list)

    #     with open(self.location, 'w') as fi:
    #         fi.write(file_str)

    #     # reset the modified file state
    #     self.__file_modified = False

    def update_include_location_in_file_as_list(self, new_path: str, include_file: File) -> None:
        raise NotImplementedError("Implement this in the derived class.")

    def write_to_file(self, new_file_path: None | str = None, write_includes: bool = False,
                      write_out_all_files: bool = False, overwrite_file: bool = False) -> None:
        """Writes to file specified in self.location the strings contained in the list self.file_content_as_list.

        Args:
            new_file_path (None | str): writes to self.location if left as None. Otherwise writes to new_file_name.
            write_includes (bool): If True will write out all include files within the file. Defaults to False.
            write_out_all_files (bool): If False will write only modified files. Otherwise will write all files.
            overwrite_file (bool): If True will overwrite the file at the location specified by new_file_path. \
            Otherwise will raise an error if the file already exists.
        """
        # overwrite File base class method to allow for write_includes
        if overwrite_file:
            self._file_modified_set(True)

        if new_file_path is None and overwrite_file:
            # In this case just overwrite the file with the existing path:
            new_file_path = self.location
        elif new_file_path is None and not overwrite_file:
            raise ValueError('No file path to write to, and overwrite_file set to False')
        if self.file_content_as_list is None:
            raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')

        if new_file_path is None:
            raise ValueError('No file path to write to.')
        if os.path.exists(new_file_path) and not overwrite_file:
            raise ValueError(f'File already exists at {new_file_path} and overwrite_file set to False')

        # create directories that do not exist
        if not os.path.exists(os.path.dirname(new_file_path)):
            os.makedirs(os.path.dirname(new_file_path))

        if write_includes and self.include_objects is not None:
            for file in self.include_objects:
                write_file: bool = file.file_modified or write_out_all_files
                write_file = write_file or (new_file_path != self.location and not os.path.isabs(file.location))
                if file.file_content_as_list is None:
                    warnings.warn(f'No content found for file: {file}. Not writing file.')
                    continue
                new_root_name = f'{os.path.basename(new_file_path).split(".")[0]}_{os.path.basename(file.location)}'
                # write the include file to the same directory.
                include_file_name = os.path.join(os.path.dirname(new_file_path), new_root_name)
                if write_file:
                    self.update_include_location_in_file_as_list(include_file_name, file)
                    file.write_to_file(include_file_name, write_includes=True, write_out_all_files=write_out_all_files,
                                       overwrite_file=overwrite_file)

        file_str = ''.join(self.file_content_as_list)

        # update the location:
        if self.file_modified or write_out_all_files:
            self.location = new_file_path
            with open(new_file_path, 'w') as fi:
                fi.write(file_str)
            # reset the modified file state
            self._file_modified_set(False)

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
