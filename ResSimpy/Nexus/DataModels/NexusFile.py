"""Handle Nexus files and preserve origin of include files."""
from __future__ import annotations

import os.path
from dataclasses import dataclass, field
from typing import Optional, Generator

# Use correct Self type depending upon Python version
import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from uuid import UUID
import re
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
import warnings
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_OPERATION_KEYWORDS, GRID_ARRAY_FORMAT_KEYWORDS, \
    GRID_ARRAY_KEYWORDS
from ResSimpy.Utils.factory_methods import get_empty_list_str, get_empty_list_nexus_file, \
    get_empty_dict_uuid_list_int
from ResSimpy.File import File
import pathlib
import os
from datetime import datetime, timezone


@dataclass(kw_only=True, repr=True)
class NexusFile(File):
    """Class to deal with origin and structure of Nexus files and preserve origin of include files.

    Attributes:
        location (Optional[str]): Path to the original file being opened. Defaults to None.
        include_locations (Optional[list[str]]): list of file paths that the file contains. Defaults to None.
        origin (Optional[str]): Where the file was opened from. Defaults to None.
        include_objects (Optional[list[NexusFile]]): The include files but generated as a NexusFile instance. \
            Defaults to None.
        linked_user (Optional[str]): user or owner of the file. Defaults to None
        last_modified (Optional[datetime]): last modified date of the file
    """

    include_locations: Optional[list[str]] = field(default=None)
    origin: Optional[str] = None
    include_objects: Optional[list[NexusFile]] = field(default=None, repr=False)
    object_locations: Optional[dict[UUID, list[int]]] = field(default=None, repr=False)
    line_locations: Optional[list[tuple[int, UUID]]] = field(default=None, repr=False)
    linked_user: Optional[str] = field(default=None)
    last_modified: Optional[datetime] = field(default=None)

    def __init__(self, location: str,
                 include_locations: Optional[list[str]] = None,
                 origin: Optional[str] = None,
                 include_objects: Optional[list[NexusFile]] = None,
                 file_content_as_list: Optional[list[str]] = None,
                 linked_user: Optional[str] = None,
                 last_modified: Optional[datetime] = None,
                 array_skipped: bool = False) -> None:
        super().__init__(location=location, file_content_as_list=file_content_as_list)
        if origin is not None:
            self.location = nfo.get_full_file_path(location, origin)
        else:
            self.location = location
        self.input_file_location: Optional[str] = location
        self.include_locations: Optional[list[str]] = get_empty_list_str() if include_locations is None else \
            include_locations
        self.origin: Optional[str] = origin
        self.include_objects: Optional[list[NexusFile]] = get_empty_list_nexus_file() \
            if include_objects is None else include_objects
        if self.object_locations is None:
            self.object_locations: dict[UUID, list[int]] = get_empty_dict_uuid_list_int()
        if self.line_locations is None:
            self.line_locations = []
        self.linked_user = linked_user
        self.last_modified = last_modified
        self.__array_skipped = array_skipped

    @classmethod
    def generate_file_include_structure(cls, file_path: str, origin: Optional[str] = None, recursive: bool = True,
                                        skip_arrays: bool = True, top_level_file: bool = True) -> Self:
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
        def __get_pathlib_path_details(full_file_path: str):
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

        def __get_datetime_from_os_stat(full_file_path: str):
            if full_file_path == "" or full_file_path is None:
                return None
            stat_obj = os.stat(full_file_path)
            timestamp = stat_obj.st_mtime
            if timestamp is None:
                return None
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)

        full_file_path = file_path
        if origin is not None:
            full_file_path = nfo.get_full_file_path(file_path, origin)

        try:
            file_as_list = nfo.load_file_as_list(full_file_path)
        except FileNotFoundError:
            # handle if a file can't be found
            location = file_path

            nexus_file_class = cls(location=location,
                                   include_locations=None,
                                   origin=origin,
                                   include_objects=None,
                                   file_content_as_list=None,
                                   linked_user=None,
                                   last_modified=None)
            warnings.warn(UserWarning(f'No file found for: {file_path} while loading {origin}'))
            return nexus_file_class

        # check last modified and user for the file
        user = __get_pathlib_path_details(full_file_path)
        last_changed = __get_datetime_from_os_stat(full_file_path)

        # prevent python from mutating the lists that it's iterating over
        modified_file_as_list: list[str] = []
        # search for the INCLUDE keyword and append to a list:
        inc_file_list: list[str] = []
        includes_objects: Optional[list[NexusFile]] = []
        skip_next_include = False
        previous_line: str

        for i, line in enumerate(file_as_list):
            if len(modified_file_as_list) >= 1:
                previous_line = modified_file_as_list[len(modified_file_as_list) - 1].rstrip('\n')
                if previous_line.endswith('>'):
                    modified_file_as_list[len(modified_file_as_list) - 1] = previous_line[:-1] + line
                else:
                    modified_file_as_list.append(line)
            else:
                modified_file_as_list.append(line)
            if line.rstrip('\n').endswith('>'):
                continue
            if nfo.check_token("INCLUDE", line):
                # Include found, check if we should skip loading it in (e.g. if it is a large array file)
                ignore_keywords = ['NOLIST']
                previous_value = nfo.get_previous_value(file_as_list=file_as_list[0: i + 1], search_before='INCLUDE',
                                                        ignore_values=ignore_keywords)

                keywords_to_skip_include = GRID_ARRAY_FORMAT_KEYWORDS + GRID_OPERATION_KEYWORDS + ["CORP"]
                if previous_value is None:
                    skip_next_include = False

                elif previous_value.upper() in keywords_to_skip_include:
                    skip_next_include = True

            elif nfo.check_token("VALUE", line) and not top_level_file:
                # Check if this is an 'embedded' grid array file. If it is, return this file with only the content up
                # to this point to help with performance when analysing the files.
                previous_value = nfo.get_previous_value(file_as_list=file_as_list[0: i + 1], search_before='VALUE')
                next_value = nfo.get_next_value(start_line_index=0, file_as_list=file_as_list[i:],
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
            inc_full_path = nfo.get_full_file_path(inc_file_path, origin=full_file_path)
            # store the included files as files inside the object
            inc_file_list.append(inc_full_path)
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
                               array_skipped=True)
                if includes_objects is None:
                    raise ValueError('include_objects is None - recursion failure.')
                skip_next_include = False
            else:
                inc_file = cls.generate_file_include_structure(inc_file_path, origin=full_file_path, recursive=True,
                                                               skip_arrays=skip_arrays, top_level_file=False)
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

    def export_network_lists(self):
        """Exports lists of connections from and to for use in network graphs.

        Raises:
            ValueError: If the from and to lists are not the same length

        Returns:
            tuple[list]: list of to and from file paths where the equivalent indexes relate to a connection
        """
        from_list = [self.origin]
        to_list = [self.location]
        if not [self.origin]:
            to_list = []
        if self.include_locations is not None:
            from_list += [self.location] * len(self.include_locations)
            to_list += self.include_locations
        if len(from_list) != len(to_list):
            raise ValueError(
                f"{from_list=} and {to_list=} are not the same length")

        return from_list, to_list

    @dataclass
    class FileIndex:
        index: int

    def iterate_line(self, file_index: Optional[FileIndex] = None, max_depth: Optional[int] = None,
                     parent: Optional[NexusFile] = None, prefix_line: Optional[str] = None,
                     keep_include_references=False) -> \
            Generator[str, None, None]:
        """Generator object for iterating over a list of strings with nested NexusFile objects in them.

        Yields:
            str: sequential line from the file.
        """

        if file_index is None:
            file_index = NexusFile.FileIndex(index=0)
        if parent is None:
            parent = self
            parent.line_locations = []
        if parent.line_locations is None:
            parent.line_locations = []
        if prefix_line is not None and prefix_line != ' ':
            file_index.index += 1
            yield prefix_line

        new_entry = (file_index.index, self.id)
        if new_entry not in parent.line_locations:
            parent.line_locations.append(new_entry)
        depth: int = 0
        if max_depth is not None:
            depth = max_depth
        if self.file_content_as_list is None:
            warnings.warn(f'No file content found for file: {self.location}')
            return
        for row in self.file_content_as_list:
            if nfo.check_token('INCLUDE', row):
                incfile_location = fo.get_token_value('INCLUDE', row, self.file_content_as_list)
                if incfile_location is None:
                    continue
                split_line = re.split(incfile_location, row, maxsplit=1, flags=re.IGNORECASE)
                if len(split_line) == 2:
                    prefix_line, suffix_line = split_line
                    prefix_line = re.sub('INCLUDE', '', prefix_line, flags=re.IGNORECASE)
                    prefix_line = prefix_line.rstrip() + ' '
                    suffix_line = suffix_line.lstrip()
                else:
                    prefix_line = row.replace(incfile_location, '')
                    suffix_line = None

                include_file = None
                if self.include_objects is None:
                    raise ValueError(f'No include objects found in the nexusfile to expand over for file: '
                                     f'{self.location}')
                for obj in self.include_objects:
                    if obj.location == incfile_location:
                        include_file = obj
                        break
                    if self.origin is not None and \
                            obj.location == nfo.get_full_file_path(incfile_location, self.origin):
                        include_file = obj
                        break
                    if obj.location is not None and \
                            os.path.basename(obj.location) == os.path.basename(incfile_location):
                        include_file = obj
                        break

                if (max_depth is None or depth > 0) and include_file is not None:
                    level_down_max_depth = None if max_depth is None else depth - 1

                    if keep_include_references:
                        yield row

                    yield from include_file.iterate_line(file_index=file_index, max_depth=level_down_max_depth,
                                                         parent=parent, prefix_line=prefix_line)

                    new_entry = (file_index.index, self.id)
                    if new_entry not in parent.line_locations:
                        parent.line_locations.append(new_entry)
                    if suffix_line:
                        file_index.index += 1
                        # Add in space between include location and the rest of the line
                        suffix_line = ' ' + suffix_line
                        yield suffix_line
                else:
                    continue
            else:
                file_index.index += 1
                yield row

    @property
    def get_flat_list_str_file(self) -> list[str]:
        if self.file_content_as_list is None:
            raise ValueError(f'No file content found for {self.location}')
        flat_list = list(self.iterate_line(file_index=None, keep_include_references=False))
        return flat_list

    @property
    def get_flat_list_str_file_including_includes(self) -> list[str]:
        if self.file_content_as_list is None:
            raise ValueError(f'No file content found for {self.location}')
        flat_list = list(self.iterate_line(file_index=None, keep_include_references=True))
        return flat_list

    # TODO write an output function using the iterate_line method
    def get_full_network(self, max_depth: Optional[int] = None) -> tuple[list[str | None], list[str]]:
        """Recursively constructs two lists of from and to nodes representing the connections between files.

        Args:
            max_depth (Optional[int], optional): depth of the iteration to construct the network down to. \
                Defaults to None.

        Returns:
            tuple[list[str | None], list[str | None]]: two lists of from and to nodes where corresponding \
                indices create an edge within a graph network. e.g. (from_list[i], to_list[i]) \
                is a connection between two files.
        """
        depth: int = 0
        from_list = [self.origin]
        to_list = [self.location]
        if max_depth is not None:
            depth = max_depth
        if self.file_content_as_list is None:
            return from_list, to_list
        for row in self.file_content_as_list:
            if isinstance(row, NexusFile):
                if max_depth is None or depth > 0:
                    level_down_max_depth = None if max_depth is None else depth - 1
                    temp_from_list, temp_to_list = row.export_network_lists()
                    from_list.extend(temp_from_list)
                    to_list.extend(temp_to_list)
                    temp_from_list, temp_to_list = row.get_full_network(max_depth=level_down_max_depth)
                    from_list.extend(temp_from_list)
                    to_list.extend(temp_to_list)
        return from_list, to_list

    def add_object_locations(self, obj_uuid: UUID, line_indices: list[int]) -> None:
        """Adds a uuid to the object_locations dictionary. Used for storing the line numbers where objects are stored
        within the flattened file_as_list.

        Args:
            obj_uuid (UUID): unique identifier of the object being created/stored.
            line_indices (list[int]): line number in the flattened file_content_as_list
                (i.e. from the get_flat_list_str_file method).
        """
        if self.object_locations is None:
            self.object_locations: dict[UUID, list[int]] = get_empty_dict_uuid_list_int()
        existing_line_locations = self.object_locations.get(obj_uuid, None)
        if existing_line_locations is not None:
            existing_line_locations.extend(line_indices)
            existing_line_locations.sort()
        else:
            self.object_locations[obj_uuid] = line_indices

    def __update_object_locations(self, line_number: int, number_additional_lines: int) -> None:
        """Updates the object locations in a nexusfile by the additional lines. Used when files have been modified and
        an addition/removal of lines has occurred. Ensures that the object locations are correct to the actual lines
        in the file_as_list.

        Args:
            line_number (int): Line number at which the new lines have been added
            number_additional_lines (int): number of new lines added.
        """
        if self.object_locations is None:
            return
        for object_id, list_indices in self.object_locations.items():
            for i, obj_index in enumerate(list_indices):
                if obj_index >= line_number:
                    self.object_locations[object_id][i] = obj_index + number_additional_lines

    def __remove_object_locations(self, obj_uuid: UUID) -> None:
        """Removes an object location based on the obj_uuid provided. Used when removing objects in the file_as_list.

        Args:
            obj_uuid (UUID): id of the removed object.
        """
        if self.object_locations is None:
            raise ValueError(f'No object locations found for file {self.location}')

        if self.object_locations.get(obj_uuid, None) is None:
            raise ValueError(f'No object with {obj_uuid=} found within the object locations')
        self.object_locations.pop(obj_uuid, None)

    def find_which_include_file(self, flattened_index: int) -> tuple[File, int]:
        """Given a line index that relates to a position within the flattened file_as_list from the method
        get_flat_file_as_list.

        Args:
            flattened_index (int): index in the flattened file as list structure

        Returns:
            tuple[File, int] where the first element is the file that the relevant line is in and the second
            element is the relative index in that file.
        """
        if self.line_locations is None:
            # call get_flat_list_str_file to ensure line locations are updated
            _ = self.get_flat_list_str_file
            if self.line_locations is None:
                raise ValueError("No include line locations found.")

        line_locations = [x[0] for x in self.line_locations]
        line_locations.sort()
        uuid_index: Optional[UUID] = None
        index_in_included_file = 0

        # Find the Nexusfile containing the line we are looking for
        for numlines, obj_id in self.line_locations:
            if numlines <= flattened_index:
                uuid_index = obj_id
            if numlines >= flattened_index:
                break

        get_next_line_count = False
        lines_already_included = 0
        previous_lines_value = 0

        # Add the previously included lines from the file (if any) to the location after it has been split
        for numlines, obj_id in self.line_locations:
            if obj_id == uuid_index:
                get_next_line_count = True
                previous_lines_value = numlines
                continue
            else:
                # If we have gone beyond where the line is, calculate the location in the relevant file
                if numlines >= flattened_index:
                    lines_already_included += flattened_index - previous_lines_value
                    break

                if get_next_line_count:
                    lines_already_included += numlines - previous_lines_value
                    get_next_line_count = False
                previous_lines_value = numlines

        if flattened_index > line_locations[-1]:
            lines_already_included += flattened_index - line_locations[-1]

        index_in_included_file += lines_already_included

        if uuid_index == self.id or self.include_objects is None:
            return self, index_in_included_file

        nexus_file = None
        for file in self.include_objects:
            if file.id == uuid_index:
                nexus_file = file
            elif file.include_objects is not None:
                # CURRENTLY THIS ONLY SUPPORTS 2 LEVELS OF INCLUDES
                for lvl_2_include in file.include_objects:
                    if lvl_2_include.id == uuid_index:
                        nexus_file = lvl_2_include
        if nexus_file is None:
            raise ValueError(f'No file with {uuid_index=} found within include objects')

        return nexus_file, index_in_included_file

    def add_to_file_as_list(self, additional_content: list[str], index: int,
                            additional_objects: Optional[dict[UUID, list[int]]] = None,
                            comments: Optional[str] = None) -> None:
        """To add content to the file as list, also updates object numbers and optionally allows user \
        to add several additional new objects.

        Args:
            additional_content (list[str]): Additional lines as a list of strings to be added.
            index (int): index to insert the new lines at in the calling flat_file_as_list
            additional_objects (Optional[dict[UUID, int]]): defaults to None. Otherwise, a dictionary keyed with the \
            UUID of the new objects to add as well as the corresponding index of the object in the original \
            calling NexusFile
            comments (str | None): defaults to None. Comments to add in-line to the file.
        """
        if comments is not None:
            additional_content = NexusFile.insert_comments(additional_content, comments)

        nexusfile_to_write_to, relative_index = self.find_which_include_file(index)
        if nexusfile_to_write_to.file_content_as_list is None:
            raise ValueError(f'No file content to write to in file: {nexusfile_to_write_to}')
        nexusfile_to_write_to.file_content_as_list = \
            nexusfile_to_write_to.file_content_as_list[:relative_index] + \
            additional_content + nexusfile_to_write_to.file_content_as_list[relative_index:]

        self._file_modified_set(True)

        # update object locations
        self.__update_object_locations(line_number=index, number_additional_lines=len(additional_content))

        if additional_objects is None:
            return
        for object_id, line_index in additional_objects.items():
            self.add_object_locations(obj_uuid=object_id, line_indices=line_index)

    def remove_object_from_file_as_list(self, objects_to_remove: list[UUID]) -> None:
        """Removes all associated lines in the file as well as the object locations relating to a list of objects."""
        if self.object_locations is None:
            raise ValueError('Cannot remove object from object_locations as object_locations is None. '
                             'Check object locations is being populated properly.')
        for obj_to_remove in objects_to_remove:
            # find all locations in the code that relate to the object
            obj_locs = self.object_locations.get(obj_to_remove, None)
            if obj_locs is None:
                continue
            # sort from highest to lowest to ensure line indices are not affected by removal of lines
            sorted_obj_locs = sorted(obj_locs, reverse=True)
            for i, index in enumerate(sorted_obj_locs):
                if i == 0:
                    # for the first removal remove the object location
                    self.remove_from_file_as_list(index, objects_to_remove=[obj_to_remove])
                else:
                    # the remaining iterations remove just the lines
                    self.remove_from_file_as_list(index)
        self._file_modified_set(True)

    def remove_from_file_as_list(self, index: int, objects_to_remove: Optional[list[UUID]] = None,
                                 string_to_remove: Optional[str] = None) -> None:
        """Remove an entry from the file as list. Also updates existing object locations and removes any \
        specified objects from the object locations dictionary.

        Args:
            index (int): index n the calling flat_file_as_list to remove the entry from
            objects_to_remove (Optional[list[UUID]]): list of object id's to remove from the object locations. \
            Defaults to None
            string_to_remove (Optional[str]): if specified will only remove the listed string from the entry \
            at the index. Defaults to None, which removes the entire entry.

        """
        nexusfile_to_write_to, relative_index = self.find_which_include_file(index)

        # remove the line in the file:
        if nexusfile_to_write_to.file_content_as_list is None:
            raise ValueError(
                f'No file content in the file attempting to remove line from {nexusfile_to_write_to.location}')

        if string_to_remove is None:
            nexusfile_to_write_to.file_content_as_list.pop(relative_index)
            self.__update_object_locations(line_number=index, number_additional_lines=-1)
        else:
            entry_to_replace = nexusfile_to_write_to.file_content_as_list[relative_index]
            if isinstance(entry_to_replace, str):
                nexusfile_to_write_to.file_content_as_list[relative_index] = \
                    entry_to_replace.replace(string_to_remove, '', 1)
            else:
                raise ValueError(
                    f'Tried to replace at non string value at index: {relative_index} in '
                    f'file_as_list instead got {entry_to_replace}')

        if objects_to_remove is not None:
            for object_id in objects_to_remove:
                self.__remove_object_locations(object_id)
        self._file_modified_set(True)

    @staticmethod
    def insert_comments(additional_content: list[str], comments: str) -> list[str]:
        """Adds comments alongside additional content.

        Args:
            additional_content (list[str]): additional lines of the file to be added with a new entry per line.
            comments (str): comments to be added to all lines

        Returns:
            list of strings within the content.
        """
        for index, element in enumerate(additional_content):
            newline_index = element.find('\n')
            if newline_index != -1:
                modified_text = element[:newline_index] + ' ! ' + comments + element[newline_index:]
                additional_content[index] = modified_text
                return additional_content

        additional_content[-1] += ' ! ' + comments + '\n'
        return additional_content

    def get_object_locations_for_id(self, id: UUID) -> list[int]:
        """Gets the number of object locations for a specified id."""
        if self.object_locations is None or len(self.object_locations[id]) == 0:
            raise ValueError(f'No object locations specified, cannot find id: {id} in {self.object_locations}')
        return self.object_locations[id]

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
        if new_file_path is None and overwrite_file:
            # In this case just overwrite the file with the existing path:
            new_file_path = self.location
        elif new_file_path is None and not overwrite_file:
            raise ValueError('No file path to write to, and overwrite_file set to False')
        if self.file_content_as_list is None:
            raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')

        if new_file_path is None:
            raise ValueError('No file path to write to.')

        # create directories that do not exist
        if not os.path.exists(os.path.dirname(new_file_path)):
            os.makedirs(os.path.dirname(new_file_path))

        if write_includes and self.include_objects is not None:
            for file in self.include_objects:
                write_file: bool = file.file_modified or write_out_all_files
                write_file = write_file or (new_file_path != self.location and not os.path.isabs(file.location))
                # if the array was previously skipped then load the file as list
                if file.__array_skipped:
                    file.file_content_as_list = nfo.load_file_as_list(file.location)

                if file.file_content_as_list is None:
                    warnings.warn(f'No content found for file: {file}. Not writing file.')
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

    def update_include_location_in_file_as_list(self, new_path: str, include_file: NexusFile) -> None:
        """Updates the path of an include file within this file's file_as_list.

        Args:
            new_path (str): Updates the path in the file as list to point towards the new include location.
            include_file (NexusFile): include object whose path is being modified
        """
        # try and find the path of the file that should be replaced (i.e. how it is currently written in the file)
        if self.include_locations is None or not self.include_locations or include_file.input_file_location is None:
            raise ValueError('No include locations found and therefore cannot update include path')
        file_path_to_replace = include_file.input_file_location
        file_content = self.file_content_as_list
        if file_content is None or not file_content:
            raise ValueError(f'No file content found within file {self.location}')

        for line in file_content:
            if not nfo.check_token('INCLUDE', line):
                continue
            # if the right path to replace is found then replace it
            if nfo.get_expected_token_value('INCLUDE', line, file_content) == file_path_to_replace:
                nfo.get_expected_token_value('INCLUDE', line, file_content, replace_with=new_path)
                self._file_modified_set(True)
        # replace the location in the include locations list using the original path

        index_of_path_to_replace = self.include_locations.index(include_file.location)
        # get the full path and update it in the include file object
        # TODO maybe include this in a setter attr for the location.
        include_file.location = nfo.get_full_file_path(new_path, self.location)

        self.include_locations[index_of_path_to_replace] = include_file.location
        # update the new path
        include_file.input_file_location = new_path
