from __future__ import annotations
import copy
from typing import TYPE_CHECKING
from uuid import UUID

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
import ResSimpy.Nexus.nexus_file_operations as nfo
if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


class AddObjectOperations:
    def __init__(self, model: NexusSimulator) -> None:
        self.__model = model

    def find_which_file_from_id(self, id: UUID, file_type_to_search: str) -> NexusFile:
        """Finds a file based on the presence of an object in the file.

        Args:
            id (UUID): object id to match on
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
            all_files = [files_to_search] if files_to_search.object_locations is not None and \
                                             id in files_to_search.object_locations else []
        else:
            all_files = [x for x in files_to_search.values() if x.object_locations is not None and
                         id in x.object_locations]
        if len(all_files) == 0:
            raise FileNotFoundError(f'No {file_type_to_search} found with and object with id: {id}')
        elif len(all_files) > 1:
            raise ValueError(f'Too many files found containing that object id.'
                             f'Check if there are conflicts in where the objects are being stored.'
                             f'Files found matching: {[x.location for x in all_files]}')
        file_found = all_files[0]
        if file_found.file_content_as_list is None:
            raise FileNotFoundError(
                f'No well file content found for specified wellfile at location: {file_found.location}')
        return file_found

    def __get_wellspec_header(self, additional_headers: list[str],
                              completion_properties: dict,
                              file_content: list[str], index: int, inverted_nexus_map: dict[str, str],
                              nexus_mapping: dict[str, tuple[str, type]], wellspec_file: NexusFile) -> \
            tuple[int, list[str], list[str]]:
        """Gets the wellspec header and works out if any additional headers should be added."""
        keyword_map = {x: y[0] for x, y in nexus_mapping.items()}
        wellspec_table = file_content[index::]
        header_index, headers = nfo.get_table_header(file_as_list=wellspec_table, header_values=keyword_map)
        header_index += index
        headers_original = copy.copy(headers)
        # work out if there are any headers that are not in the new completion
        for key in completion_properties:
            if key == 'date':
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
            file_to_write_to, index_in_file = wellspec_file.find_which_include_file(header_index)
            if file_to_write_to.file_content_as_list is None:
                raise ValueError(
                    f'No file content found in {file_to_write_to.location}. Cannot write to index {index_in_file}')
            file_to_write_to.file_content_as_list[index_in_file] = new_header_line
        return header_index, headers, headers_original

    def __fill_in_nas(self, additional_headers: list[str], headers_original: list[str], index: int, line: str,
                      wellspec_file: NexusFile, file_content: list[str]) -> int:
        """Check the validity of the line, if its valid add as many NA's as required for the new columns."""
        valid_line, _ = nfo.table_line_reader(keyword_store={}, headers=headers_original, line=line)
        if valid_line and len(additional_headers) > 0:
            additional_na_values = ['NA'] * len(additional_headers)
            additional_column_string = ' '.join(additional_na_values)
            split_comments = file_content[index].split('!', 1)
            if len(split_comments) == 1:
                new_completion_line = split_comments[0].replace('\n', '', 1) + ' ' + additional_column_string + '\n'
            else:
                new_completion_line = split_comments[0] + additional_column_string + ' !' + split_comments[1]

            nexusfile_to_write_to, index_in_file = wellspec_file.find_which_include_file(index)
            if nexusfile_to_write_to.file_content_as_list is None:
                raise ValueError(f'No file content to write to in file: {nexusfile_to_write_to}')
            nexusfile_to_write_to.file_content_as_list[index_in_file] = new_completion_line
        if valid_line:
            return index
        else:
            return -1
    #
    # def __write_out_existing_wellspec(self, completion_date: str,
    #                                   completion_properties: dict,
    #                                   date_found: bool, index: int, new_completion_index: int,
    #                                   preserve_previous_completions: bool, well: NexusWell, well_name: str) -> \
    #         tuple[list[str], int, list[str], bool]:
    #     """Writes out the existing wellspec for a well at a new time stamp."""
    #     nexus_mapping = NexusCompletion.get_nexus_mapping()
    #     completion_table_as_list = ['\n']
    #     if not date_found:
    #         completion_table_as_list += ['TIME ' + completion_date + '\n']
    #     completion_table_as_list += ['WELLSPEC ' + well_name + '\n']
    #     headers = [k for k, v in nexus_mapping.items() if v[0] in completion_properties]
    #     if preserve_previous_completions:
    #         # get all the dates for that well
    #         date_list = well.dates_of_completions
    #         previous_dates = [x for x in date_list if
    #                           self.__model._sim_controls.compare_dates(x, completion_date) < 0]
    #         if len(previous_dates) == 0:
    #             # if no dates that are smaller than the completion date then only add the perforation
    #             # at the current index with a new wellspec card.
    #             warnings.warn(f'No previous completions found for {well_name} at date: {completion_date}')
    #             new_completion_index = index
    #             write_out_headers = [' '.join(headers) + '\n']
    #             completion_table_as_list += write_out_headers
    #             return headers, new_completion_index, completion_table_as_list, False
    #
    #         # get the most recent date that is earlier than the new completion date
    #         previous_dates = sorted(previous_dates, key=cmp_to_key(self.__model._sim_controls.compare_dates))
    #         last_date = str(previous_dates[-1])
    #         completion_to_find: NexusCompletion.InputDictionary = {'date': last_date}
    #         # find all completions at this date
    #         previous_completion_list = well.find_completions(completion_to_find)
    #         if len(previous_completion_list) > 0:
    #             prev_completion_properties = {k: v for k, v in previous_completion_list[0].to_dict().items() if
    #                                           v is not None}
    #             for key in prev_completion_properties:
    #                 if key == 'date':
    #                     continue
    #                 header_key = attribute_name_to_nexus_keyword(nexus_mapping, key)
    #                 if header_key not in headers:
    #                     headers.append(header_key)
    #
    #         write_out_headers = [' '.join(headers) + '\n']
    #         completion_table_as_list += write_out_headers
    #         # run through the existing completions to duplicate the completion at the new time
    #         for completion in previous_completion_list:
    #             completion_table_as_list += completion.completion_to_wellspec_row(headers)
    #     else:
    #         write_out_headers = [' '.join(headers) + '\n']
    #         completion_table_as_list += write_out_headers
    #     return headers, new_completion_index, completion_table_as_list, True
