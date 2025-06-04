"""This module contains the abstract base class for file manipulations for simulator files."""
from __future__ import annotations
import os
import pathlib
from datetime import datetime, timezone
from uuid import uuid4, UUID
from dataclasses import dataclass, field
from typing import Optional, Sequence, TypeVar, Self
import warnings
from ResSimpy.FileOperations.FileBase import FileBase
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Utils.general_utilities import is_number
import uuid

from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_FORMAT_KEYWORDS, GRID_OPERATION_KEYWORDS, \
    GRID_ARRAY_KEYWORDS
from ResSimpy.Utils.factory_methods import get_empty_list_file

T = TypeVar("T", bound='File')

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

    def __get_pathlib_path_details(full_file_path: str) -> None | str:
        if full_file_path == "" or full_file_path is None:
            return None
        pathlib_path = pathlib.Path(full_file_path)
        owner: str = ''
        group: str = ''
        try:
            owner = pathlib_path.owner()  # type: ignore
            group = pathlib_path.group()  # type: ignore
        except NotImplementedError:
            # owner or group not supported on this system, continue without filling out that information
            pass
        except PermissionError:
            # user doesn't have permission to access the file, continue without filling out that information
            warnings.warn(f'PermissionError when trying to access file at {full_file_path}')
        except FileNotFoundError:
            # file not found, continue without filling out that information
            warnings.warn(f'FileNotFoundError when trying to access file at {full_file_path}')
        except KeyError:
            # Group or owner doesn't exist on this system, continue without filling out that information
            warnings.warn(f'Unable to find the group for the file at {full_file_path}')

        if owner is not None and group is not None:
            return f"{owner}:{group}"
        elif owner is not None:
            return owner
        return None

    def __get_datetime_from_os_stat(full_file_path: str) -> None | datetime:
        if full_file_path == "" or full_file_path is None:
            return None
        stat_obj = os.stat(full_file_path)
        timestamp = stat_obj.st_mtime
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    @staticmethod
    def generate_file_include_structure(cls: type[T], file_path: str, origin: Optional[str] = None,
                                        recursive: bool = True, skip_arrays: bool = True,
                                        top_level_file: bool = True) -> T:
        """Generates a nexus file instance for a provided text file with information storing the included files.

        Args:
            file_path (str): path to a file
            origin (Optional[str], optional): Where the file was opened from. Defaults to None.
            recursive (bool): Whether the method should recursively drill down multiple layers of include_locations.
            skip_arrays (bool): If set True skips the INCLUDE arrays that come after property array and VALUE
            top_level_file (bool): If set to True, the code assumes this is a 'top level' file rather than an included
            one.

        Returns:
            NexusFile: a class instance for NexusFile with knowledge of include files
        """

        full_file_path = file_path
        if origin is not None:
            full_file_path = fo.get_full_file_path(file_path, origin)

        try:
            file_as_list = fo.load_file_as_list(full_file_path)
        except FileNotFoundError:
            # handle if a file can't be found
            nexus_file_class = cls(location=file_path,
                                   include_locations=None,
                                   origin=origin,
                                   include_objects=None,
                                   file_content_as_list=None,
                                   linked_user=None,
                                   last_modified=None)
            warnings.warn(UserWarning(f'No file found for: {full_file_path} while loading {origin}'))
            return nexus_file_class

        # check last modified and user for the file
        user = File.__get_pathlib_path_details(full_file_path)
        last_changed = File.__get_datetime_from_os_stat(full_file_path)

        # prevent python from mutating the lists that it's iterating over
        modified_file_as_list: list[str] = []
        # search for the INCLUDE keyword and append to a list:
        inc_file_list: list[str] = []
        includes_objects: Optional[list[T]] = []
        skip_next_include = False
        previous_line: str

        for i, line in enumerate(file_as_list):
            if len(modified_file_as_list) >= 1:
                previous_line = modified_file_as_list[len(modified_file_as_list) - 1].rstrip('\n')
                # Handle lines continued with the '>' character
                if previous_line.endswith('>'):
                    modified_file_as_list[len(modified_file_as_list) - 1] = previous_line[:-1] + line
                else:
                    if not top_level_file:
                        converted_line = cls.convert_line_to_full_file_path(line=line,
                                                                            full_base_file_path=full_file_path)
                    else:
                        converted_line = line
                    modified_file_as_list.append(converted_line)
            else:
                if not top_level_file:
                    converted_line = cls.convert_line_to_full_file_path(line=line,
                                                                        full_base_file_path=full_file_path)
                else:
                    converted_line = line
                modified_file_as_list.append(converted_line)

            if line.rstrip('\n').endswith('>'):
                continue
            if fo.check_token("INCLUDE", line):
                # Include found, check if we should skip loading it in (e.g. if it is a large array file)
                ignore_keywords = ['NOLIST']
                previous_value = fo.get_previous_value(file_as_list=file_as_list[0: i + 1], search_before='INCLUDE',
                                                        ignore_values=ignore_keywords)

                keywords_to_skip_include = GRID_ARRAY_FORMAT_KEYWORDS + GRID_OPERATION_KEYWORDS + ["CORP"]
                if previous_value is None:
                    skip_next_include = False

                elif previous_value.upper() in keywords_to_skip_include:
                    skip_next_include = True

            elif fo.check_token("VALUE", line) and not top_level_file:
                # Check if this is an 'embedded' grid array file. If it is, return this file with only the content up
                # to this point to help with performance when analysing the files.
                previous_value = fo.get_previous_value(file_as_list=file_as_list[0: i + 1], search_before='VALUE')
                next_value = fo.get_next_value(start_line_index=0, file_as_list=file_as_list[i:],
                                                search_string=line.upper().split('VALUE')[1])

                if previous_value is None or next_value is None:
                    continue

                if next_value.upper() != 'INCLUDE' and previous_value.upper() in GRID_ARRAY_KEYWORDS:
                    nexus_file_class = cls(
                        location=file_path,
                        include_locations=inc_file_list,
                        origin=origin,
                        include_objects=includes_objects,
                        file_content_as_list=modified_file_as_list
                    )

                    return nexus_file_class
                else:
                    continue

            else:
                continue
            inc_file_path = fo.get_token_value('INCLUDE', line, file_as_list)
            if inc_file_path is None:
                continue
            inc_full_path = fo.get_full_file_path(inc_file_path, origin=full_file_path)
            # store the included files as files inside the object
            inc_file_list.append(inc_full_path)

            # test the include to see if the first few lines have only array data
            # limit number of lines loaded here in future?
            if skip_arrays:
                try:
                    inc_file_as_list = fo.load_file_as_list(inc_full_path)
                except FileNotFoundError:
                    # handle files not found - this is handled in an exception in the main loop
                    pass
                else:
                    all_numeric = False
                    for inc_file_line in inc_file_as_list[0:50]:
                        split_line = fo.split_line(inc_file_line, upper=False)
                        # check if it is numeric data
                        # this won't work if the array has scientific notation.
                        if any(not is_number(x) for x in split_line):
                            # don't set skip_next_include if the line is not entirely numeric
                            all_numeric = False
                            break
                        all_numeric = True
                    if all_numeric:
                        skip_next_include = True

            if not recursive:
                continue
            elif skip_arrays and skip_next_include:
                inc_file = cls(location=inc_file_path,
                               include_locations=None,
                               origin=full_file_path,
                               include_objects=None,
                               file_content_as_list=None,
                               linked_user=user,
                               last_modified=last_changed,
                               file_loading_skipped=True)
                if includes_objects is None:
                    raise ValueError('include_objects is None - recursion failure.')
                skip_next_include = False
            else:
                inc_file = cls.generate_file_include_structure(cls=cls, file_path=inc_file_path, origin=full_file_path,
                                                               recursive=True, skip_arrays=skip_arrays,
                                                               top_level_file=False)
                if includes_objects is None:
                    raise ValueError('include_objects is None - recursion failure.')

            includes_objects.append(inc_file)

        includes_objects = None if not includes_objects else includes_objects

        nexus_file_class = cls(
            location=file_path,
            include_locations=inc_file_list,
            origin=origin,
            include_objects=includes_objects,
            file_content_as_list=modified_file_as_list,
            linked_user=user,
            last_modified=last_changed
        )

        return nexus_file_class

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
