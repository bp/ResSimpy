"""Class for handling adding objects to a nexus file and memory."""
from __future__ import annotations
import copy
from typing import TYPE_CHECKING, Any, TypeVar, Optional
from uuid import UUID

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.FileOperations.File import File
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork

T = TypeVar('T', bound=DataObjectMixin)
U = TypeVar('U', bound=NetworkObject)


class AddObjectOperations:
    """Class for handling adding objects to a nexus file and memory."""

    def __init__(self, obj_type: Optional[type[T]], table_header: str, table_footer: str,
                 model: NexusSimulator) -> None:
        """Initialises the AddObjectOperations class.

        Args:
            obj_type (Optional[type[T]]): type of object to add to the file.
            table_header (str): The string that represents the start of the table in the file.
            table_footer (str): The string that represents the end of the table in the file.
            model (NexusSimulator): model to add the object to.
        """
        self.__model = model
        self.table_header = table_header
        self.table_footer = table_footer
        self.obj_type = obj_type

    def find_which_file_from_id(self, obj_id: UUID, file_type_to_search: str) -> NexusFile:
        """Finds a file based on the presence of an object in the file.

        Args:
            obj_id (UUID): object id to match on
            file_type_to_search (str): file type from within the fcsfile. e.g. 'well_files'

        Returns:
            NexusFile that contains the object of interest in the object_locations attribute.
        """
        # find the correct wellspec file in the model by looking at the ids

        if self.__model.model_files is None:
            raise ValueError(f'File found in fcs file at: {self.__model.model_files}')
        files_to_search = getattr(self.__model.model_files, file_type_to_search, None)
        if files_to_search is None:
            raise FileNotFoundError(f'No files of type {files_to_search} found in model.')
        elif isinstance(files_to_search, NexusFile):
            # handling only 1 file returned of the file_type_to_search
            all_files = [files_to_search] if files_to_search.object_locations is not None and \
                                             obj_id in files_to_search.object_locations else []
        else:
            # handle case of multiple files of the same type.
            all_files = [x for x in files_to_search.values() if x.object_locations is not None and
                         obj_id in x.object_locations]
        if len(all_files) == 0:
            raise FileNotFoundError(f'No {file_type_to_search} found with and object with id: {obj_id}')
        elif len(all_files) > 1:
            raise ValueError(f'Too many files found containing that object id.'
                             f'Check if there are conflicts in where the objects are being stored.'
                             f'Files found matching: {[x.location for x in all_files]}')
        file_found = all_files[0]
        if file_found.file_content_as_list is None:
            raise FileNotFoundError(
                f'No well file content found for specified wellfile at location: {file_found.location}')
        return file_found

    @staticmethod
    def get_and_write_new_header(additional_headers: list[str],
                                 object_properties: dict[str, None | str | float | int],
                                 file_content: list[str], index: int,
                                 nexus_mapping: dict[str, tuple[str, type]], file: File) -> \
            tuple[int, list[str], list[str]]:
        """Gets the header and works out if any additional headers should be added based on the new obj attributes\
        being added.

        Args:
            additional_headers (list[str]): New headers required for the objects new columns.
            object_properties (dict[str, None | str | float | int]): dictionary containing new attributes of the object.
            file_content (list[str]): flattened file content as a list of strings.
            index (int): index to start reading the new headers from.
            nexus_mapping (dict[str, tuple[str, type]]): dictionary controlling the mapping from keyword to attribute.
            file (NexusFile): file to write the new header to.

        Returns:
            tuple[int, list[str], list[str]]: index of the new headers, a list of the headers,
            the original set of headers.
        """
        # TODO move out the additional headers mutability to a separate method that explicitly sets it
        keyword_map = {x: y[0] for x, y in nexus_mapping.items()}
        inverted_nexus_map = invert_nexus_map(nexus_mapping)
        table = file_content[index::]
        header_index, headers = nfo.get_table_header(file_as_list=table, header_values=keyword_map)
        header_index += index
        headers_original = copy.copy(headers)

        keys_to_skip = ['date', 'unit_system', 'date_format', 'start_date', 'iso_date']

        for key in object_properties:
            if key in keys_to_skip:
                continue
            if inverted_nexus_map[key] not in headers:
                headers.append(inverted_nexus_map[key])
                additional_headers.append(inverted_nexus_map[key])
        additional_column_string = ' '.join(additional_headers)
        split_comments = str(file_content[header_index]).split('!', 1)
        if len(split_comments) == 1:
            new_header_line = split_comments[0].replace('\n', '', 1) + ' ' + additional_column_string + '\n'
        else:
            new_header_line = split_comments[0] + additional_column_string + ' !' + split_comments[1]
        if len(additional_headers) > 0:
            file_to_write_to, index_in_file = file.find_which_include_file(header_index)
            if file_to_write_to.file_content_as_list is None:
                raise ValueError(
                    f'No file content found in {file_to_write_to.location}. Cannot write to index {index_in_file}')
            file_to_write_to.file_content_as_list[index_in_file] = new_header_line
        return header_index, headers, headers_original

    @staticmethod
    def fill_in_nas(additional_headers: list[str], headers_original: list[str], index: int, line: str,
                    file: File, file_content: list[str]) -> int:
        """Check the validity of the line, if its valid add as many NAs as required for the new columns.

        Args:
            additional_headers (list[str]): New headers added to the table.
            headers_original (list[str]): headers from the original table in the file.
            index (int): index of the line to start filling NAs from.
            line (str): line to add additional NAs to.
            file (NexusFile): file to add NAs to
            file_content (list[str]): flattened content of the file being read

        Returns:
            int: index of the line if a valid line has been found otherwise returns -1.
        """
        valid_line, _ = nfo.table_line_reader(keyword_store={}, headers=headers_original, line=line)
        if valid_line and len(additional_headers) > 0:
            additional_na_values = ['NA'] * len(additional_headers)
            additional_column_string = ' '.join(additional_na_values)
            split_comments = file_content[index].split('!', 1)
            if len(split_comments) == 1:
                new_completion_line = split_comments[0].replace('\n', '', 1) + ' ' + additional_column_string + '\n'
            else:
                new_completion_line = split_comments[0] + additional_column_string + ' !' + split_comments[1]

            nexusfile_to_write_to, index_in_file = file.find_which_include_file(index)
            if nexusfile_to_write_to.file_content_as_list is None:
                raise ValueError(f'No file content to write to in file: {nexusfile_to_write_to}')
            nexusfile_to_write_to.file_content_as_list[index_in_file] = new_completion_line
        if valid_line:
            return index
        else:
            return -1

    def write_out_new_table_containing_object(self, obj_date: str,
                                              object_properties: dict[str, None | str | float | int],
                                              date_found: bool, new_obj: Any) -> tuple[list[str], int]:
        """Writes out the existing table for an object being added at a new time stamp.

        Args:
            obj_date (str): date for the object to be added at.
            object_properties (dict[str, None | str | float | int]): dictionary containing new attributes of the object.
            date_found (bool): Whether a new TIME card is required or not.
            new_obj (Any): The object getting added that requires the new table to represent it.

        Returns:
            list[str], int: first return arg in a new table containing the requested object and \
            the second representing the line location of the new object within the table.
        """
        nexus_mapping = new_obj.get_keyword_mapping()

        new_table_as_list = ['']
        if not date_found:
            new_table_as_list.append('TIME ' + obj_date)
        new_table_as_list += [self.table_header]
        headers = [k for k, v in nexus_mapping.items() if v[0] in object_properties]
        if headers:
            write_out_headers = ' '.join(headers)
            new_table_as_list.append(write_out_headers)
        new_table_as_list.append(new_obj.to_table_line(headers=headers))
        new_table_as_list.append(self.table_footer)
        new_table_as_list = [x + '\n' if not x.endswith('\n') else x for x in new_table_as_list]
        new_table_as_list.append('\n')
        new_obj_index = len(new_table_as_list) - 1
        return new_table_as_list, new_obj_index

    @staticmethod
    def check_name_date(object_properties: dict[str, None | str | float | int]) -> tuple[str, str]:
        """Checks for the presence of a name and a date in the additional object properties provided."""
        name = object_properties.get('name', None)
        if name is None:
            raise AttributeError(
                'Adding an object requires a name, please provide a "name" entry in the input dictionary.')
        date = object_properties.get('date', None)
        if date is None:
            raise AttributeError(
                'Adding an object requires a date, please provide a "date" entry in the input dictionary.')
        name = str(name)
        date = str(date)

        return name, date

    def add_object_to_file(self, date: str, file_as_list: list[str], file_to_add_to: File, new_object: T,
                           object_properties: dict[str, None | str | float | int], skip_reading_headers: bool = False) \
            -> None:
        """Finds where the object should be added based on the date and existing tables.

        Args:
            date (str): date to add the node at.
            file_as_list (list[str]): flattened file as a list of strings.
            file_to_add_to (NexusFile): file to add the new text to.
            new_object (Any): an object with a to_dict, table_header, table_footer, get_keyword_mapping and to_string
            methods.
            object_properties (dict[str, None | str | float | int]): dictionary containing new attributes of the object.
            skip_reading_headers (bool): if True skips reading the headers and just adds the new object to the file.
            Used for when objects do not have header tables.
        """
        # initialise some useful variables
        additional_content: list[str] = []
        date_comparison: int = -1
        date_index: int = -1
        insert_line_index: int = -1
        id_line_locs: list[int] = []
        headers: list[str] = []
        additional_headers: list[str] = []
        header_index: int = -1
        last_valid_line_index: int = -1
        headers_original: list[str] = []
        date_found = False
        nexus_mapping = new_object.get_keyword_mapping()
        for index, line in enumerate(file_as_list):
            # check for the dates
            if nfo.check_token('TIME', line):
                date_found_in_file = nfo.get_expected_token_value('TIME', line, [line])
                date_comparison = self.__model._sim_controls.compare_dates(
                    date_found_in_file, date)
                if date_comparison == 0:
                    date_index = index
                    date_found = True
                    continue

            # find a table that exists in that date
            if nfo.check_token(self.table_header, line) and date_index != -1:
                # get the header of the table
                if skip_reading_headers:
                    header_index = index
                    headers = headers_original
                else:
                    header_index, headers, headers_original = self.get_and_write_new_header(
                        additional_headers, object_properties, file_as_list, index, nexus_mapping, file_to_add_to
                    )
                    continue

            if header_index != -1 and index > header_index:
                # check for valid rows + fill extra columns with NA
                line_valid_index = self.fill_in_nas(additional_headers, headers_original, index,
                                                    line, file_to_add_to, file_as_list)
                # set the line to insert the new completion at to be the one after the last valid line
                last_valid_line_index = line_valid_index if line_valid_index > 0 else last_valid_line_index

            # if we've found an existing table then just insert the new object
            if nfo.check_token(self.table_footer, line) and date_comparison == 0:
                insert_line_index = index
                additional_content.append(new_object.to_table_line(headers=headers))
                id_line_locs = [insert_line_index]

            # if we have passed the date or if we're at the end of the file write out the table
            if date_comparison > 0 or nfo.check_token('STOP', line):
                new_table, obj_in_table_index = self.write_out_new_table_containing_object(
                    obj_date=date, object_properties=object_properties, date_found=date_found, new_obj=new_object)
                additional_content.extend(new_table)
                insert_line_index = index
                id_line_locs = [obj_in_table_index + index - 1]

            if insert_line_index >= 0:
                break
        else:
            # if we've finished the loop normally that means we haven't added any additional objects or lines
            # This means we have to add the date and a new table to the end of the file.
            new_table, obj_in_table_index = self.write_out_new_table_containing_object(
                obj_date=date, object_properties=object_properties, date_found=date_found, new_obj=new_object)
            additional_content.extend(new_table)
            insert_line_index = len(file_as_list)
            id_line_locs = [obj_in_table_index + insert_line_index - 1]
        if len(additional_content) == 0:
            raise ValueError('Could not find place to add the additional table lines.')
        # write out to the file_content_as_list
        new_object_ids = {
            new_object.id: id_line_locs
        }
        file_to_add_to.add_to_file_as_list(additional_content=additional_content, index=insert_line_index,
                                           additional_objects=new_object_ids)

    def add_network_obj(self, node_to_add: dict[str, None | str | float | int], obj_type: type[U],
                        network: NexusNetwork) -> U:
        """Add new node to the nexus network file.

        Args:
            node_to_add(dict[str, None | str | float | int]): dictionary taking all the properties for the new node.
            obj_type(type [U]): type of object to add to the file.
            network(NexusNetwork): network that the new nodes are part of.
        """
        network.get_load_status()
        file_to_add_to = network.get_network_file()
        name, date = self.check_name_date(node_to_add)
        date_format = network.model.date_format
        new_obj_type = obj_type
        new_object = new_obj_type(node_to_add, date_format=date_format)
        file_as_list = file_to_add_to.get_flat_list_str_file
        if file_as_list is None:
            raise ValueError(f'No file content found in the surface file specified at {file_to_add_to.location}')
        self.add_object_to_file(date, file_as_list, file_to_add_to, new_object, node_to_add)
        return new_object
