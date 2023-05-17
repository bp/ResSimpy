from __future__ import annotations

import uuid
from dataclasses import dataclass, field
import re
from typing import Optional, Union, Generator
from uuid import UUID

import ResSimpy.Nexus.nexus_file_operations as nfo
import warnings

from ResSimpy.Grid import VariableEntry
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_OPERATION_KEYWORDS, GRID_ARRAY_FORMAT_KEYWORDS
from ResSimpy.Utils.factory_methods import get_empty_list_str, get_empty_list_nexus_file, \
    get_empty_list_str_nexus_file, get_empty_dict_uuid_int


@dataclass(kw_only=True, repr=True)
class NexusFile:
    """ Class to deal with origin and structure of Nexus files and preserve origin of include files
    Attributes:
        location (Optional[str]): Path to the original file being opened. Defaults to None.
        includes (Optional[list[str]]): list of file paths that the file contains. Defaults to None.
        origin (Optional[str]): Where the file was opened from. Defaults to None.
        includes_objects (Optional[list[NexusFile]]): The include files but generated as a NexusFile instance. \
            Defaults to None.
    """
    location: Optional[str] = None
    includes: Optional[list[str]] = field(default_factory=get_empty_list_str)
    origin: Optional[str] = None
    includes_objects: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file, repr=False)
    file_content_as_list: Optional[list[Union[str, NexusFile]]] = field(default_factory=get_empty_list_str_nexus_file,
                                                                        repr=False)
    object_locations: Optional[dict[UUID, int]] = None
    line_locations: Optional[list[tuple[int, UUID]]] = None

    def __init__(self, location: Optional[str] = None,
                 includes: Optional[list[str]] = None,
                 origin: Optional[str] = None,
                 includes_objects: Optional[list[NexusFile]] = None,
                 file_content_as_list: Optional[list[Union[str, NexusFile]]] = None):
        self.location: Optional[str] = location
        self.includes: Optional[list[str]] = get_empty_list_str() if includes is None else includes
        self.origin: Optional[str] = origin
        self.includes_objects: Optional[list[NexusFile]] = get_empty_list_nexus_file() \
            if includes_objects is None else includes_objects
        self.file_content_as_list: Optional[list[Union[str, NexusFile]]] = get_empty_list_str_nexus_file() \
            if file_content_as_list is None else file_content_as_list
        if self.object_locations is None:
            self.object_locations: dict[UUID, int] = get_empty_dict_uuid_int()
        if self.line_locations is None:
            self.line_locations = []
        self.file_id = uuid.uuid4()

    @classmethod
    def generate_file_include_structure(cls, file_path: str, origin: Optional[str] = None, recursive: bool = True,
                                        skip_arrays: bool = True) -> NexusFile:
        """generates a nexus file instance for a provided text file with information storing the included files

        Args:
            file_path (str): path to a file
            origin (Optional[str], optional): Where the file was opened from. Defaults to None.
            recursive (bool): Whether the method should recursively drill down multiple layers of includes.
            skip_arrays (bool): If set True skips the INCLUDE arrays that come after property array and VALUE

        Returns:
            NexusFile: a class instance for NexusFile with knowledge of include files
        """
        # load file as list and clean up file
        # if skip_arrays and nfo.looks_like_grid_array(file_path):
        #     location = file_path
        #     nexus_file_class = cls(location=location,
        #                            includes=None,
        #                            origin=origin,
        #                            includes_objects=None,
        #                            file_content_as_list=None, )
        #     warnings.warn(UserWarning(f'File skipped due to looking like an array {file_path}'))
        #     return nexus_file_class

        try:
            file_as_list = nfo.load_file_as_list(file_path)
        except FileNotFoundError:
            # handle if a file can't be found
            location = file_path
            if origin is not None:
                location = nfo.get_full_file_path(file_path, origin)
            nexus_file_class = cls(location=location,
                                   includes=None,
                                   origin=origin,
                                   includes_objects=None,
                                   file_content_as_list=None, )
            warnings.warn(UserWarning(f'No file found for: {file_path} while loading {origin}'))
            return nexus_file_class

        # prevent python from mutating the lists that its iterating over
        modified_file_as_list: list = []
        # search for the INCLUDE keyword and append to a list:
        inc_file_list: list[str] = []
        includes_objects: Optional[list[NexusFile]] = []
        skip_next_include = False

        for i, line in enumerate(file_as_list):
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
                modified_file_as_list.append(line)
                continue
            inc_file_path = nfo.get_token_value('INCLUDE', line, file_as_list)
            if inc_file_path is None:
                modified_file_as_list.append(line)
                continue
            inc_full_path = nfo.get_full_file_path(inc_file_path, origin=file_path)
            # store the included files as files inside the object
            inc_file_list.append(inc_full_path)
            if not recursive:
                modified_file_as_list.append(line)
            elif skip_arrays and skip_next_include:
                inc_file = cls(location=inc_full_path,
                               includes=None,
                               origin=file_path,
                               includes_objects=None,
                               file_content_as_list=None, )
                if includes_objects is None:
                    raise ValueError('includes_objects is None - recursion failure.')
                includes_objects.append(inc_file)
                try:
                    prefix_line, suffix_line = re.split(inc_file_path, line, maxsplit=1, flags=re.IGNORECASE)
                    suffix_line = suffix_line.lstrip()
                except ValueError:
                    prefix_line = line.replace(inc_file_path, '')
                    suffix_line = None

                if prefix_line:
                    if not suffix_line:
                        prefix_line += '\n'
                    modified_file_as_list.append(prefix_line)
                modified_file_as_list.append(inc_file)
                if suffix_line:
                    modified_file_as_list.append(suffix_line)
                skip_next_include = False
            else:
                # TODO also store the full file paths
                inc_file = cls.generate_file_include_structure(inc_full_path, origin=file_path, recursive=True,
                                                               skip_arrays=skip_arrays)
                if includes_objects is None:
                    raise ValueError('includes_objects is None - recursion failure.')
                includes_objects.append(inc_file)
                try:
                    prefix_line, suffix_line = re.split(inc_file_path, line, maxsplit=1, flags=re.IGNORECASE)
                    suffix_line = suffix_line.lstrip()
                except ValueError:
                    prefix_line = line.replace(inc_file_path, '')
                    suffix_line = None

                if prefix_line:
                    if not suffix_line:
                        prefix_line += '\n'
                    modified_file_as_list.append(prefix_line)
                modified_file_as_list.append(inc_file)
                if suffix_line:
                    modified_file_as_list.append(suffix_line)

        includes_objects = None if not includes_objects else includes_objects

        nexus_file_class = cls(
            location=file_path,
            includes=inc_file_list,
            origin=origin,
            includes_objects=includes_objects,
            file_content_as_list=modified_file_as_list,
            )

        return nexus_file_class

    def export_network_lists(self):
        """ Exports lists of connections from and to for use in network graphs

        Raises:
            ValueError: If the from and to lists are not the same length
        Returns:
            tuple[list]: list of to and from file paths where the equivalent indexes relate to a connection
        """
        from_list = [self.origin]
        to_list = [self.location]
        if not [self.origin]:
            to_list = []
        if self.includes is not None:
            from_list += [self.location] * len(self.includes)
            to_list += self.includes
        if len(from_list) != len(to_list):
            raise ValueError(
                f"{from_list=} and {to_list=} are not the same length")

        return from_list, to_list

    @dataclass
    class FileIndex:
        index: int

    def iterate_line(self, file_index: Optional[FileIndex] = None, max_depth: Optional[int] = None,
                     parent: Optional[NexusFile] = None) -> Generator[str, None, None]:
        """Generator object for iterating over a list of strings with nested NexusFile objects in them

        Yields:
            str: sequential line from the file.
        """

        if file_index is None:
            file_index = NexusFile.FileIndex(index=0)
        if parent is None:
            parent = self
            parent.line_locations = []

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
            if isinstance(row, NexusFile):
                if (max_depth is None or depth > 0) and row.file_content_as_list is not None:
                    level_down_max_depth = None if max_depth is None else depth - 1

                    yield from row.iterate_line(file_index=file_index, max_depth=level_down_max_depth,
                                                parent=parent)
                    new_entry = (file_index.index, self.file_id)
                    if new_entry not in parent.line_locations:
                        parent.line_locations.append(new_entry)
                else:
                    continue
            else:
                file_index.index += 1
                yield row

    def get_flat_list_str_file(self) -> list[str]:
        if self.file_content_as_list is None:
            raise ValueError(f'No file content found for {self.location}')
        flat_list = [x for x in self.iterate_line(file_index=None)]
        return flat_list

    def get_flat_list_str_until_file(self, start_line_index: int) -> tuple[list[str], Optional[NexusFile]]:
        flat_list: list[str] = []
        if self.file_content_as_list is None:
            raise ValueError(f'No file content found for {self.location=}')
        for row in self.file_content_as_list[start_line_index::]:
            if isinstance(row, NexusFile):
                return flat_list, row
            flat_list.append(row)
        return flat_list, None

    # TODO write an output function using the iterate_line method
    def get_full_network(self, max_depth: Optional[int] = None) -> tuple[list[str | None], list[str | None]]:
        """ recursively constructs two lists of from and to nodes representing the connections between files.

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

    def get_next_value_nexus_file(self, start_line_index: int, search_string: Optional[str] = None,
                                  ignore_values: Optional[list[str]] = None,
                                  replace_with: Union[str, VariableEntry, None] = None) -> Optional[str | NexusFile]:

        file_as_list, nexus_file = self.get_flat_list_str_until_file(start_line_index)
        value = nfo.get_next_value(0, file_as_list, search_string, ignore_values, replace_with)
        if value is None:
            return nexus_file
        else:
            return value

    def get_token_value_nexus_file(self, token: str, token_line: str,
                                   ignore_values: Optional[list[str]] = None,
                                   replace_with: Union[str, VariableEntry, None] = None) -> None | str | NexusFile:
        """Gets the next value after a given token within the NexusFile's content as list.
        If no token is found and the next item in the list is a NexusFile it will then return the NexusFile.

        Args:
            token (str): the token being searched for.
            token_line (str): string value of the line that the token was found in.
            ignore_values (Optional[list[str]]): a list of values that should be ignored if found. \
                Defaults to None.
            replace_with (Union[str, VariableEntry, None]): a value to replace the existing value with. \
                Defaults to None.
        Raises:
            ValueError: if no file content is found in the NexusFile or if the search string is not found
        Returns:
            None | str | NexusFile: value of the string if a string is found, the next NexusFile in the list after the \
                        token if no value is found. Else returns None.
        """
        token_upper = token.upper()
        token_line_upper = token_line.upper()
        if "!" in token_line_upper and token_line_upper.index("!") < token_line_upper.index(token_upper):
            return None

        search_start = token_line_upper.index(token_upper) + len(token) + 1
        search_string: Union[str, NexusFile] = token_line[search_start: len(token_line)]
        if self.file_content_as_list is None:
            raise ValueError(f'No file content to scan for tokens in {self.location}')
        line_index = self.file_content_as_list.index(token_line)

        # If we have reached the end of the line, go to the next line to start our search
        if not isinstance(search_string, str):
            # if search string isn't a string it will be a nexus file therefore return it.
            return search_string
        if len(search_string) < 1:
            line_index += 1
            search_string = self.file_content_as_list[line_index]
        if isinstance(search_string, self.__class__):
            return search_string
        if not isinstance(search_string, str):
            raise ValueError(f'{search_string=} was not class or subclass of type NexusFile and not a string.')
        value = self.get_next_value_nexus_file(line_index, search_string, ignore_values, replace_with)
        return value

    def add_object_locations(self, uuid: UUID, line_index: int):
        if self.object_locations is None:
            self.object_locations: dict[UUID, int] = get_empty_dict_uuid_int()
        self.object_locations[uuid] = line_index

    def update_object_locations(self, line_number: int, number_additional_lines: int):
        if self.object_locations is None:
            return
        for object_id, index in self.object_locations.items():
            if index >= line_number:
                self.object_locations[object_id] = index + number_additional_lines

    def remove_object_locations(self, uuid: UUID):
        if self.object_locations.get(uuid, None) is None:
            raise ValueError(f'No object with {uuid=} found within the object locations')
        self.object_locations.pop(uuid, None)

    def find_which_include_file(self, index: int) -> tuple[NexusFile, int]:
        if self.line_locations is None:
            self.get_flat_list_str_file()
            if self.line_locations is None:
                raise ValueError("No include line locations found.")

        line_locations = [x[0] for x in self.line_locations]
        line_locations.sort()
        uuid_index = 0
        index_in_file = index - line_locations[-1]

        for i, x in enumerate(line_locations):
            if x <= index:
                index_in_file = index - x
                uuid_index = i
            if x >= index:
                break

        file_uuid = self.line_locations[uuid_index][1]
        if file_uuid == self.file_id or self.includes_objects is None:
            return self, index_in_file

        nexus_file = None
        for file in self.includes_objects:
            if file.file_id == file_uuid:
                nexus_file = file
            elif file.includes_objects is not None:
                # CURRENTLY THIS ONLY SUPPORTS 2 LEVELS OF INCLUDES
                for lvl_2_include in file.includes_objects:
                    if lvl_2_include.file_id == file_uuid:
                        nexus_file = lvl_2_include
        if nexus_file is None:
            raise ValueError(f'No file with {file_uuid=} found within include objects')

        return nexus_file, index_in_file

    def write_to_file(self):
        file_str = ''.join(self.file_content_as_list_str)
        with open(self.location, 'w') as fi:
            fi.write(file_str)

    @property
    def file_content_as_list_str(self):
        file_content_as_list_str = []
        for line in self.file_content_as_list:
            if isinstance(line, str):
                file_content_as_list_str.append(line)
            else:
                file_content_as_list_str.append(line.location)
        return file_content_as_list_str
