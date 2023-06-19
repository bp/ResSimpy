from __future__ import annotations

import os.path
import uuid
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
import warnings
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_OPERATION_KEYWORDS, GRID_ARRAY_FORMAT_KEYWORDS
from ResSimpy.Utils.factory_methods import get_empty_list_str, get_empty_list_nexus_file, \
    get_empty_dict_uuid_list_int


@dataclass(kw_only=True, repr=True)
class NexusFile:
    """Class to deal with origin and structure of Nexus files and preserve origin of include files.

    Attributes:
        location (Optional[str]): Path to the original file being opened. Defaults to None.
        include_locations (Optional[list[str]]): list of file paths that the file contains. Defaults to None.
        origin (Optional[str]): Where the file was opened from. Defaults to None.
        include_objects (Optional[list[NexusFile]]): The include files but generated as a NexusFile instance. \
            Defaults to None.
    """

    location: Optional[str] = None
    include_locations: Optional[list[str]] = field(default=None)
    origin: Optional[str] = None
    include_objects: Optional[list[NexusFile]] = field(default=None, repr=False)
    file_content_as_list: Optional[list[str]] = field(default=None, repr=False)
    object_locations: Optional[dict[UUID, list[int]]] = None
    line_locations: Optional[list[tuple[int, UUID]]] = None

    def __init__(self, location: Optional[str] = None,
                 include_locations: Optional[list[str]] = None,
                 origin: Optional[str] = None,
                 include_objects: Optional[list[NexusFile]] = None,
                 file_content_as_list: Optional[list[str]] = None) -> None:

        if origin is not None and location is not None:
            self.location = nfo.get_full_file_path(location, origin)
        else:
            self.location = location
        self.input_file_location: Optional[str] = location
        self.include_locations: Optional[list[str]] = get_empty_list_str() if include_locations is None else \
            include_locations
        self.origin: Optional[str] = origin
        self.include_objects: Optional[list[NexusFile]] = get_empty_list_nexus_file() \
            if include_objects is None else include_objects
        self.file_content_as_list: Optional[list[str]] = get_empty_list_str() \
            if file_content_as_list is None else file_content_as_list
        if self.object_locations is None:
            self.object_locations: dict[UUID, list[int]] = get_empty_dict_uuid_list_int()
        if self.line_locations is None:
            self.line_locations = []
        self.file_id = uuid.uuid4()

    @classmethod
    def generate_file_include_structure(cls, file_path: str, origin: Optional[str] = None, recursive: bool = True,
                                        skip_arrays: bool = True) -> Self:
        """Generates a nexus file instance for a provided text file with information storing the included files.

        Args:
            file_path (str): path to a file
            origin (Optional[str], optional): Where the file was opened from. Defaults to None.
            recursive (bool): Whether the method should recursively drill down multiple layers of include_locations.
            skip_arrays (bool): If set True skips the INCLUDE arrays that come after property array and VALUE

        Returns:
            NexusFile: a class instance for NexusFile with knowledge of include files
        """

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
                                   file_content_as_list=None)
            warnings.warn(UserWarning(f'No file found for: {file_path} while loading {origin}'))
            return nexus_file_class

        # prevent python from mutating the lists that its iterating over
        modified_file_as_list: list[str] = []
        # search for the INCLUDE keyword and append to a list:
        inc_file_list: list[str] = []
        includes_objects: Optional[list[NexusFile]] = []
        skip_next_include = False
        previous_line: str

        for i, line in enumerate(file_as_list):
            if len(modified_file_as_list) >= 1:
                previous_line = modified_file_as_list[len(modified_file_as_list)-1].rstrip('\n')
                if previous_line.endswith('>'):
                    modified_file_as_list[len(modified_file_as_list)-1] = previous_line[:-1] + line
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

            else:
                continue
            inc_file_path = nfo.get_token_value('INCLUDE', line, file_as_list)
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
                               file_content_as_list=None)
                if includes_objects is None:
                    raise ValueError('include_objects is None - recursion failure.')
                includes_objects.append(inc_file)
                skip_next_include = False
            else:
                inc_file = cls.generate_file_include_structure(inc_file_path, origin=full_file_path, recursive=True,
                                                               skip_arrays=skip_arrays)
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
                     parent: Optional[NexusFile] = None, prefix_line: Optional[str] = None) -> \
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

        new_entry = (file_index.index, self.file_id)
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
                incfile_location = nfo.get_token_value('INCLUDE', row, self.file_content_as_list)
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

                    yield from include_file.iterate_line(file_index=file_index, max_depth=level_down_max_depth,
                                                         parent=parent, prefix_line=prefix_line)

                    new_entry = (file_index.index, self.file_id)
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
        flat_list = list(self.iterate_line(file_index=None))
        return flat_list

    # TODO write an output function using the iterate_line method
    def get_full_network(self, max_depth: Optional[int] = None) -> tuple[list[str | None], list[str | None]]:
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
                if (max_depth is None or depth > 0):
                    level_down_max_depth = None if max_depth is None else depth - 1
                    temp_from_list, temp_to_list = row.export_network_lists()
                    from_list.extend(temp_from_list)
                    to_list.extend(temp_to_list)
                    temp_from_list, temp_to_list = row.get_full_network(max_depth=level_down_max_depth)
                    from_list.extend(temp_from_list)
                    to_list.extend(temp_to_list)
        return from_list, to_list

    def add_object_locations(self, obj_uuid: UUID, line_index: int) -> None:
        """Adds a uuid to the object_locations dictionary. Used for storing the line numbers where objects are stored
        within the flattened file_as_list.

        Args:
            obj_uuid (UUID): unique identifier of the object being created/stored.
            line_index (int): line number in the flattened file_content_as_list
                (i.e. from the get_flat_list_str_file method).
        """
        if self.object_locations is None:
            self.object_locations: dict[UUID, list[int]] = get_empty_dict_uuid_list_int()
        existing_line_locations = self.object_locations.get(obj_uuid, None)
        if existing_line_locations is not None:
            existing_line_locations.append(line_index)
        else:
            self.object_locations[obj_uuid] = [line_index]

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

    def find_which_include_file(self, flattened_index: int) -> tuple[NexusFile, int]:
        """Given a line index that relates to a position within the flattened file_as_list from the method
        get_flat_file_as_list.

        Args:
            flattened_index (int): index in the flattened file as list structure

        Returns:
            tuple[NexusFile, int] where the first element is the file that the relevant line is in and the second
            element is the relative index in that file.
        """
        if self.line_locations is None:
            # call get_flat_list_str_file to ensure line locations are updated
            self.get_flat_list_str_file
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

        if uuid_index == self.file_id or self.include_objects is None:
            return self, index_in_included_file

        nexus_file = None
        for file in self.include_objects:
            if file.file_id == uuid_index:
                nexus_file = file
            elif file.include_objects is not None:
                # CURRENTLY THIS ONLY SUPPORTS 2 LEVELS OF INCLUDES
                for lvl_2_include in file.include_objects:
                    if lvl_2_include.file_id == uuid_index:
                        nexus_file = lvl_2_include
        if nexus_file is None:
            raise ValueError(f'No file with {uuid_index=} found within include objects')

        return nexus_file, index_in_included_file

    def add_to_file_as_list(self, additional_content: list[str], index: int,
                            additional_objects: Optional[dict[UUID, int]] = None) -> None:
        """To add content to the file as list, also updates object numbers and optionally allows user \
        to add several additional new objects.

        Args:
            additional_content (list[str]): Additional lines as a list of strings to be added.
            index (int): index to insert the new lines at in the calling flat_file_as_list
            additional_objects (Optional[dict[UUID, int]]): defaults to None. Otherwise, a dictionary keyed with the \
            UUID of the new objects to add as well as the corresponding index of the object in the original \
            calling NexusFile
        """
        nexusfile_to_write_to, relative_index = self.find_which_include_file(index)
        if nexusfile_to_write_to.file_content_as_list is None:
            raise ValueError(f'No file content to write to in file: {nexusfile_to_write_to}')
        nexusfile_to_write_to.file_content_as_list = \
            nexusfile_to_write_to.file_content_as_list[:relative_index] + \
            additional_content + nexusfile_to_write_to.file_content_as_list[relative_index:]
        # write straight to file
        nexusfile_to_write_to.write_to_file()
        # update object locations
        self.__update_object_locations(line_number=index, number_additional_lines=len(additional_content))

        if additional_objects is None:
            return
        for object_id, line_index in additional_objects.items():
            self.add_object_locations(obj_uuid=object_id, line_index=line_index)

    def remove_object_from_file_as_list(self, objects_to_remove: list[UUID]) -> None:
        """Removes all associated lines relating to an object"""
        for obj_to_remove in objects_to_remove:
            obj_locs = self.object_locations.get(obj_to_remove, None)
            if obj_locs is None:
                continue
            sorted_obj_locs = sorted(obj_locs, reverse=True)
            for index in sorted_obj_locs:
                self.remove_from_file_as_list(index, objects_to_remove=[obj_to_remove])

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

        nexusfile_to_write_to.write_to_file()

    def write_to_file(self) -> None:
        """Writes back to the original file location of the nexusfile."""
        if self.location is None:
            raise ValueError(f'No file path to write to, instead found {self.location}')
        if self.file_content_as_list is None:
            raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')
        file_str = ''.join(self.file_content_as_list)
        with open(self.location, 'w') as fi:
            fi.write(file_str)
