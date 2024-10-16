"""This module contains the abstract base class for file manipulations for simulator files."""
from __future__ import annotations
import os
from uuid import uuid4, UUID
from dataclasses import dataclass, field
from typing import Optional, Sequence
import warnings
from ResSimpy.FileOperations.FileBase import FileBase
import ResSimpy.FileOperations.file_operations as fo
import uuid

from ResSimpy.Utils.factory_methods import get_empty_list_file


@dataclass(kw_only=True)
class File(FileBase):
    """The abstract base class for simulator files.

    Attributes:
        location (str): Full path to file location
        file_content_as_list (list[str]): List of lines in the file
    """

    location: str
    _location_in_including_file: str
    include_objects: Optional[Sequence[File]]
    include_locations: Optional[list[str]] = None
    file_content_as_list: Optional[list[str]] = field(default=None, repr=False)
    __id: UUID = field(default_factory=lambda: uuid4(), compare=False)
    __file_modified: bool = False
    __file_loading_skipped: bool = False

    def __init__(self, location: str,
                 file_content_as_list: Optional[list[str]] = None,
                 include_objects: Optional[Sequence[File]] = None, create_as_modified: bool = False,
                 file_loading_skipped: bool = False) -> None:
        """Initialises the File class.

        Args:
            location (str): The location of the file on disk.
            file_content_as_list (Optional[list[str]]): The file content as a list of strings.
            include_objects (Optional[Sequence[File]]): The files included in the file.
            create_as_modified (bool): Set the object to modified.
            file_loading_skipped (bool): Whether the file loading was skipped due to the file being too large an array.
        """
        self.location = location
        self._location_in_including_file = location
        self.include_objects: Optional[list[File]] = get_empty_list_file() \
            if include_objects is None else include_objects
        if file_content_as_list is None:
            self.file_content_as_list = []
        else:
            self.file_content_as_list = file_content_as_list
        self.__id = uuid.uuid4()
        self.__file_modified = create_as_modified
        self.__file_loading_skipped = file_loading_skipped

    @property
    def id(self) -> UUID:
        """Unique identifier for each Node object."""
        return self.__id

    @property
    def file_modified(self) -> bool:
        """Whether the file has been modified since the last file write."""
        return self.__file_modified

    @property
    def file_loading_skipped(self) -> bool:
        """Whether loading the file contents has been skipped due to it being to large e.g. for array files."""
        return self.__file_loading_skipped

    @property
    def location_in_including_file(self) -> str:
        """The location of the file as it is written after the INCLUDE token in the file including it."""
        return self._location_in_including_file

    def update_include_location_in_file_as_list(self, new_path: str, include_file: File) -> None:
        """update_include_location_in_file_as_list.

        Args:
            new_path(str): Updates the path in the file as list to point towards the new include location.
            include_file(file): include object whose path is being modified.
        """
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
        if new_file_path is None:
            if overwrite_file:
                # In this case just overwrite the file with the existing path:
                new_file_path = self.location
            else:
                raise ValueError('No file path to write to, and overwrite_file set to False')

        if self.file_content_as_list is None:
            raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')

        # create directories that do not exist
        if not os.path.exists(os.path.dirname(new_file_path)):
            os.makedirs(os.path.dirname(new_file_path))

        if write_includes and self.include_objects is not None:
            for file in self.include_objects:
                write_file: bool = file.file_modified or write_out_all_files
                write_file = write_file or (new_file_path != self.location and not os.path.isabs(file.location))

                # if the array was previously skipped then load the file as list
                if file.file_loading_skipped:
                    file.file_content_as_list = fo.load_file_as_list(file.location)

                if file.file_content_as_list is None:
                    warnings.warn(f'No content found for file: {file.location}. Not writing file.')
                    continue
                # this distinguishes the include file name from other includes in other files.
                # this could be moved to a folder name instead rather than affecting the include file name?
                new_root_name = f'{os.path.basename(new_file_path).split(".")[0]}_{os.path.basename(file.location)}'
                # write the include file to the same directory.
                # TODO add a fix for the name above and a check for whether the file exists as exactly the same name
                include_file_name = os.path.join(os.path.dirname(new_file_path), new_root_name)

                if write_file:
                    self.update_include_location_in_file_as_list(include_file_name, file)

                if os.path.exists(include_file_name):
                    # if the file is already copied across then move on to the next file
                    continue

                if write_file:
                    file.write_to_file(include_file_name, write_includes=True, write_out_all_files=write_out_all_files,
                                       overwrite_file=overwrite_file)

        # check if the file already exists so we aren't accidentally overwriting it
        if os.path.exists(new_file_path) and not overwrite_file:
            raise ValueError(f'File already exists at {new_file_path} and overwrite_file set to False')

        file_str = ''.join(self.file_content_as_list)

        # update the location:
        if self.file_modified or write_out_all_files:
            self.location = new_file_path

        # write the file to the new location
        with open(new_file_path, 'w') as fi:
            fi.write(file_str)
        # reset the modified file state
        self._file_modified_set(False)

    def _file_modified_set(self, value: bool) -> None:
        """Set the modified file status.

        Args:
            value(bool): True if the file is modified, False otherwise.
        """
        self.__file_modified = value

    @property
    def get_flat_list_str_file(self) -> list[str]:
        """Returns flat list of strings from file."""
        raise NotImplementedError("Implement this in the derived class")

    def add_object_locations(self, obj_uuid: UUID, line_indices: list[int]) -> None:
        """Adds a uuid to the object_locations dictionary.

        Args:
            obj_uuid(UUID): Unique identifier of the object being created/stored.
            line_indices(list[int]): line number in the flattened file_content_as_list
            (i.e. from the get_flat_list_str_file method).
        """
        raise NotImplementedError("Implement this in the derived class")

    @staticmethod
    def insert_comments(additional_content: list[str], comments: str) -> list[str]:
        """Adds comments alongside additional content.

        Args:
            additional_content(list[str]): additional lines of the file to be added with a new entry per line.
            comments(str): comments to be added to all lines list of strings within the content.
        """
        raise NotImplementedError("Implement this in the derived class")

    def get_object_locations_for_id(self, obj_id: UUID) -> list[int]:
        """Returns the list of line numbers associated with the object ID.

        Args:
            obj_id(UUID): Unique identifier for each node object.
        """
        raise NotImplementedError("Implement this in the derived class")

    def remove_object_from_file_as_list(self, objects_to_remove: list[UUID]) -> None:
        """Removes all associated lines in the file as well as the object locations relating to a list of objects.

        Args:
            objects_to_remove(list[UUID]):  list of object ids to remove from the object locations. Defaults to None
        """
        raise NotImplementedError("Implement this in the derived class")

    def add_to_file_as_list(self, additional_content: list[str], index: int,
                            additional_objects: Optional[dict[UUID, list[int]]] = None,
                            comments: Optional[str] = None) -> None:
        """To add content to the file as list, also updates object numbers
        and optionally allows user to add several additional new objects.

        Args:
            additional_content(list[str]):  Additional lines as a list of strings to be added.
            index(int): index to insert the new lines at in the calling flat_file_as_list
            additional_objects(Optional[dict[UUID, list[int]]]): defaults to None. Otherwise,
            a dictionary keyed with the UUID of the new objects to add as well as
            the corresponding index of the object in the original calling NexusFile.
            comments(Optional[str]): defaults to None. Comments to add in-line to the file.
        """
        raise NotImplementedError("Implement this in the derived class")

    def remove_from_file_as_list(self, index: int, objects_to_remove: Optional[list[UUID]] = None,
                                 string_to_remove: Optional[str] = None) -> None:
        """Remove an entry from the file as list.

        Args:
            index(int): index n the calling flat_file_as_list to remove the entry from.
            objects_to_remove(Optional[list[UUID]): list of object ids to
            remove from the object locations. Defaults to None.
            string_to_remove(Optional[str]):if specified will only remove the listed string from the entry at the index.
             Defaults to None, which removes the entire entry.
        """
        raise NotImplementedError("Implement this in the derived class")

    def find_which_include_file(self, flattened_index: int) -> tuple[File, int]:
        """Given a line index that relates to a position within the flattened
        file_as_list from the method get_flat_file_as_list.

        Args:
            flattened_index(int): index in the flattened file as list structure.
        """
        raise NotImplementedError("Implement this in the derived class")

    def __repr__(self) -> str:
        """A more readable representation of the NexusFile object file data."""
        repr_string = ''

        repr_string += f'FILE PATH: {self.location}\n\n'
        repr_string += f'Include files: {self.include_locations}\n\n'

        repr_string += 'FILE CONTENTS:\n\n'
        repr_string += self.pretty_print_contents()
        return repr_string

    def pretty_print_contents(self) -> str:
        """Pretty print the file contents."""
        if self.file_content_as_list is None:
            return ''
        return ''.join(self.file_content_as_list)
