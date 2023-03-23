from __future__ import annotations
from dataclasses import dataclass, field
import re
from typing import Optional, Union, Generator

import ResSimpy.Nexus.nexus_file_operations as nfo
import warnings

from ResSimpy.Grid import VariableEntry
from ResSimpy.Utils.factory_methods import get_empty_list_str, get_empty_list_nexus_file, get_empty_list_str_nexus_file


@dataclass(kw_only=True)
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
    includes_objects: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    file_content_as_list: Optional[list[Union[str, NexusFile]]] = field(default_factory=get_empty_list_str_nexus_file)

    def __init__(self, location: Optional[str] = None,
                 includes: Optional[list[str]] = field(default_factory=get_empty_list_str),
                 origin: Optional[str] = None,
                 includes_objects: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 file_content_as_list: Optional[list[Union[str, NexusFile]]] =
                 field(default_factory=get_empty_list_str_nexus_file)):
        self.location: Optional[str] = location
        self.includes: Optional[list[str]] = includes
        self.origin: Optional[str] = origin
        self.includes_objects: Optional[list[NexusFile]] = includes_objects
        self.file_content_as_list: Optional[list[Union[str, NexusFile]]] = file_content_as_list

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
            file_as_list = nfo.load_file_as_list(file_path, strip_comments=True)
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
            warnings.warn(UserWarning(f'No file found for: {file_path}'))
            return nexus_file_class

        # prevent python from mutating the lists that its iterating over
        modified_file_as_list: list = []
        # search for the INCLUDE keyword and append to a list:
        inc_file_list: list[str] = []
        includes_objects: Optional[list[NexusFile]] = []
        skip_next_include = False

        for i, line in enumerate(file_as_list):
            # check if the next include should be skipped
            if skip_arrays and nfo.check_token("VALUE", line) and \
                    nfo.get_token_value("VALUE", line, file_as_list) == "INCLUDE":
                skip_next_include = True
            if not nfo.check_token("INCLUDE", line):
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

    @staticmethod
    def iterate_line(file_content_as_list: list[Union[str, NexusFile]], max_depth=None) \
            -> Generator[str, None, None]:
        """Generator object for iterating over a list of strings with nested NexusFile objects in them
        Usage Example: for line in NexusFile.iterate_line(nexus_file.file_content_as_list):

        Yields:
            str: sequential line from the file.
        """
        depth: int = 0
        if max_depth is not None:
            depth = max_depth
        for row in file_content_as_list:
            if isinstance(row, NexusFile):
                if (max_depth is None or depth > 0) and row.file_content_as_list is not None:
                    level_down_max_depth = None if max_depth is None else depth - 1
                    yield from NexusFile.iterate_line(row.file_content_as_list, max_depth=level_down_max_depth)
                else:
                    continue
            else:
                yield row

    def get_flat_list_str_file(self) -> list[str]:
        if self.file_content_as_list is None:
            raise ValueError(f'No file content found for {self.location}')
        flat_list = [x for x in self.iterate_line(self.file_content_as_list)]
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
