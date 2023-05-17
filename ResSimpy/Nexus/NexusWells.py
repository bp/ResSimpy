from __future__ import annotations

import copy
import warnings
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Sequence, Optional, TYPE_CHECKING

import pandas as pd

from ResSimpy.Enums.HowEnum import OperationEnum
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusKeywords.wells_keywords import WELLS_KEYWORDS
from ResSimpy.Wells import Wells
from ResSimpy.Nexus.load_wells import load_wells
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map, attribute_name_to_nexus_keyword

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusWells(Wells):
    model: NexusSimulator
    __wells: list[NexusWell] = field(default_factory=lambda: [])

    def __init__(self, model: NexusSimulator):
        self.model = model
        self.__wells = []
        super().__init__()

    def get_wells(self) -> Sequence[NexusWell]:
        return self.__wells

    def get_well(self, well_name: str) -> Optional[NexusWell]:
        """Returns a specific well requested, or None if that well cannot be found"""
        wells_to_return = filter(lambda x: x.well_name.upper() == well_name.upper(), self.__wells)

        return next(wells_to_return, None)

    def get_wells_df(self) -> pd.DataFrame:
        # loop through wells and completions to output a table
        store_dictionaries = []
        for well in self.__wells:
            for completion in well.completions:
                completion_props: dict[str, None | float | int | str] = {
                    'well_name': well.well_name,
                    'units': well.units.name,
                    }
                completion_props.update(completion.to_dict())
                store_dictionaries.append(completion_props)
        df_store = pd.DataFrame(store_dictionaries)
        df_store = df_store.dropna(axis=1, how='all')
        return df_store

    def load_wells(self, ) -> None:
        if self.model.fcs_file.well_files is None:
            raise FileNotFoundError('No wells files found for current model.')
        for method_number, well_file in self.model.fcs_file.well_files.items():
            if well_file.location is None:
                warnings.warn(f'Well file location has not been found for {well_file}')
                continue
            new_wells = load_wells(nexus_file=well_file, start_date=self.model.start_date,
                                   default_units=self.model.default_units)
            self.__wells += new_wells

    def get_wells_overview(self) -> str:
        overview: str = ''
        for well in self.__wells:
            overview += well.printable_well_info

        return overview

    def get_wells_dates(self) -> set[str]:
        """Returns a set of the unique dates in the wellspec file over all wells"""
        set_dates: set[str] = set()
        for well in self.__wells:
            set_dates.update(set(well.dates_of_completions))

        return set_dates

    def modify_well(self, well_name: str, perforations_properties: list[NexusCompletion.InputDictionary],
                    how: OperationEnum = OperationEnum.ADD, remove_all_that_match: bool = False,
                    write_to_file: bool = True, ) -> None:
        """ Modify the existing wells in memory using a dictionary of properties.

        Args:
            well_name (str): name of the well to modify
            perforations_properties (list[InputDict]): a dictionary containing the properties to modify with the \
                attribute as keys and the values as the updated property value. If remove will remove perforation that \
                matches the values in the dictionary.
            how (OperationEnum): operation enum taking the values OperationEnum.ADD, OperationEnum.REMOVE. \
                Specifies how to modify the existing wells perforations.
            remove_all_that_match (bool): If True will remove all wells that partially match the completion_properties\
                provided. If False will remove perforation if only one matches, if several match throws a warning and \
                does not remove them.
            write_to_file (bool): If True writes directly to file. (Currently not in use)
        """
        well = self.get_well(well_name)
        if well is None:
            raise ValueError(f'No well named {well_name} found in simulator')
        for perf in perforations_properties:
            if how == OperationEnum.ADD:
                try:
                    date = perf.get('date')
                except AttributeError:
                    raise AttributeError(
                        f'No date provided in perf: {perf}, please provide a date to add the perforation at.')
                if date is None:
                    raise AttributeError(
                        f'No date provided in perf: {perf}, please provide a date to add the perforation at.')
                well.add_completion(date=date, completion_properties=perf)
            elif how == OperationEnum.REMOVE:
                completions_to_remove = well.find_completions(perf)
                well.remove_completions(completions_to_remove)
            elif how == OperationEnum.MODIFY:
                raise NotImplementedError('Modify in place not yet available. Please choose one of ADD/REMOVE')
            else:
                raise ValueError('Please select one of the valid OperationEnum values: e.g. OperationEnum.ADD')

    def add_completion(self, well_name: str, completion_properties: NexusCompletion.InputDictionary,
                       preserve_previous_completions: bool = True) -> None:
        """ Adds a completion to an existing wellspec file.

        Args:
            well_name (str): well name to update
            completion_properties (dict[str, float | int | str): properties of the completion you want to update.
            Must contain date of the completion to be added.
            preserve_previous_completions (bool): if true a new perforation added on a TIME card without a \
            wellspec card for that well will preserve the previous completions from the closest TIME card in addition \
            to the new completion
        """
        completion_date = completion_properties.get('date', None)
        if completion_date is None:
            raise AttributeError('Completion requires a date. '
                                 'Please provide a date in the completion_properties dictionary.')

        for well_coord in ['i', 'j', 'k']:
            if well_coord not in completion_properties:
                raise ValueError(f'Requires value {well_coord} for new perforation')

        well = self.get_well(well_name)
        if well is None:
            # TODO could make this not raise an error and instead initialize a NexusWell and add it to NexusWells
            raise ValueError(
                f"No well found named: {well_name}. Cannot add completion to a well that doesn't exist")
        well_id = well.completions[0].id

        # add completion in memory
        new_completion = well.add_completion(completion_date, completion_properties)

        if self.model.fcs_file.well_files is None:
            raise FileNotFoundError('No well file found, cannot modify ')

        # find the correct wellspec file in the model by looking at the ids
        wellspec_files = [x for x in self.model.fcs_file.well_files.values() if x.object_locations is not None and
                          well_id in x.object_locations]
        if len(wellspec_files) == 0:
            raise FileNotFoundError(f'No well file found with an existing well that has completion id: {well_id}')
        wellspec_file = wellspec_files[0]
        if wellspec_file.file_content_as_list is None:
            raise FileNotFoundError(
                f'No well file content found for specified wellfile at location: {wellspec_file.location}')

        # initialise some storage variables
        nexus_mapping = NexusCompletion.nexus_mapping()
        inverted_nexus_map = invert_nexus_map(nexus_mapping)
        new_completion_time_index = -1
        header_index = -1
        headers: list[str] = []
        headers_original: list[str] = []
        additional_headers: list[str] = []
        file_content = wellspec_file.get_flat_list_str_file()
        date_found = False
        new_completion_index = len(file_content)
        new_completion_string: list[str] = []
        last_valid_line_index = -1
        writing_new_wellspec_table = False
        date_comp = 0
        # if no time cards present in the file just find the name of the well instead
        if not nfo.value_in_file('TIME', file_content):
            new_completion_time_index = 0

        for index, line in enumerate(file_content):
            if header_index == -1 and nfo.check_token('TIME', line):
                wellspec_date = nfo.get_expected_token_value('TIME', line, [line])
                date_comp = self.model.Runcontrol.compare_dates(wellspec_date, completion_date)
                if date_comp == 0:
                    # if we've found the date we're looking for start looking for a wellspec and name card
                    new_completion_time_index = index
                    date_found = True
                    continue
                elif date_comp > 0 and header_index == -1:
                    # if no date is found that is equal and we've found a date that is greater than the specified date
                    # start to compile a wellspec table from scratch and add in the time cards
                    new_completion_index = index
                    header_index = index - 1
                    headers, new_completion_index, new_completion_string, found_completion_at_previous_date = \
                        self.__write_out_existing_wellspec(
                            completion_date, completion_properties, date_found, index,
                            new_completion_index, preserve_previous_completions, well, well_name)
                    writing_new_wellspec_table = True
                    if not found_completion_at_previous_date:
                        break
                else:
                    continue

            if nfo.check_token('WELLSPEC', line) and nfo.get_token_value('WELLSPEC', line, [line]) == well_name \
                    and new_completion_time_index != -1:
                # get the header of the wellspec table
                header_index, headers, headers_original = self.get_wellspec_header(
                    additional_headers, completion_properties, file_content, index,
                    inverted_nexus_map, nexus_mapping, wellspec_file
                    )
                continue

            if header_index != -1 and nfo.nexus_token_found(line, WELLS_KEYWORDS) and index > header_index:
                # if we hit the end of the wellspec table for the given well set the index for the new completion
                if last_valid_line_index != -1:
                    new_completion_index = last_valid_line_index + 1
                break

            elif header_index != -1 and index > header_index:
                # check for valid rows + fill extra columns with NA
                self.fill_in_nas(additional_headers, headers_original, index, line,
                                 wellspec_file, file_content)
                line_valid_index = self.fill_in_nas(additional_headers, headers_original, index, line,
                                                    wellspec_file, file_content)
                # set the line to insert the new completion at to be the one after the last valid line
                last_valid_line_index = line_valid_index if line_valid_index > 0 else last_valid_line_index
        # If we haven't found a TIME card after the for loop then we haven't got a valid date so add it at the end
        if date_comp < 0:
            new_completion_index = len(file_content)
            headers, new_completion_index, new_completion_string, found_completion_at_previous_date = \
                self.__write_out_existing_wellspec(
                    completion_date, completion_properties, date_found, new_completion_index,
                    new_completion_index, preserve_previous_completions, well, well_name)
            writing_new_wellspec_table = True

        # construct the new completion and ensure the order of the values is in the same order as the headers
        new_completion_string += new_completion.completion_to_wellspec_row(headers)
        new_completion_additional_lines = len(new_completion_string)
        if writing_new_wellspec_table:
            new_completion_string += ['\n']
            wellspec_file.update_object_locations(line_number=new_completion_index,
                                                  number_additional_lines=new_completion_additional_lines + 1)
        else:
            wellspec_file.update_object_locations(line_number=new_completion_index,
                                                  number_additional_lines=new_completion_additional_lines)

        wellspec_file.add_object_locations(uuid=new_completion.id,
                                           line_index=new_completion_index + new_completion_additional_lines - 1)
        # write out to the file_content_as_list
        nexusfile_to_write_to, index_in_file = wellspec_file.find_which_include_file(new_completion_index)
        if nexusfile_to_write_to.file_content_as_list is None:
            raise ValueError(f'No file content to write to in file: {nexusfile_to_write_to}')
        nexusfile_to_write_to.file_content_as_list = \
            nexusfile_to_write_to.file_content_as_list[:index_in_file] + \
            new_completion_string + nexusfile_to_write_to.file_content_as_list[index_in_file:]

        # write straight to file
        nexusfile_to_write_to.write_to_file()

    def fill_in_nas(self, additional_headers: list[str], headers_original: list[str], index: int, line: str,
                    wellspec_file: NexusFile, file_content: list[str]) -> int:
        """ check the validity of the line, if its valid add as many NA's as required for the new columns """
        valid_line, _ = nfo.table_line_reader(keyword_store={}, headers=headers_original, line=line)
        if valid_line and len(additional_headers) > 0:
            additional_na_values = ['NA'] * len(additional_headers)
            additional_column_string = ' '.join(additional_na_values)
            split_comments = file_content[index].split('!', 1)
            if len(split_comments) == 1:
                new_completion_line = split_comments[0] + ' ' + additional_column_string
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

    def get_wellspec_header(self, additional_headers: list[str], completion_properties: NexusCompletion.InputDictionary,
                            file_content: list[str], index: int, inverted_nexus_map: dict[str, str],
                            nexus_mapping: dict[str, tuple[str, type]], wellspec_file: NexusFile) -> \
            tuple[int, list[str], list[str]]:
        """Gets the wellspec header and works out if any additional headers should be added"""
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
            new_header_line = split_comments[0] + ' ' + additional_column_string
        else:
            new_header_line = split_comments[0] + additional_column_string + ' !' + split_comments[1]
        if len(additional_headers) > 0:
            file_to_write_to, index_in_file = wellspec_file.find_which_include_file(header_index)
            if file_to_write_to.file_content_as_list is None:
                raise ValueError(
                    f'No file content found in {file_to_write_to.location}. Cannot write to index {index_in_file}')
            file_to_write_to.file_content_as_list[index_in_file] = new_header_line
        return header_index, headers, headers_original

    def __write_out_existing_wellspec(self, completion_date: str,
                                      completion_properties: NexusCompletion.InputDictionary,
                                      date_found: bool, index: int, new_completion_index: int,
                                      preserve_previous_completions: bool, well: NexusWell, well_name: str) -> \
            tuple[list[str], int, list[str], bool]:
        """writes out the existing wellspec for a well at a new time stamp"""
        nexus_mapping = NexusCompletion.nexus_mapping()
        completion_table_as_list = ['\n']
        if not date_found:
            completion_table_as_list += ['TIME ' + completion_date + '\n']
        completion_table_as_list += ['WELLSPEC ' + well_name + '\n']
        headers = [k for k, v in nexus_mapping.items() if v[0] in completion_properties]
        if preserve_previous_completions:
            # get all the dates for that well
            date_list = well.dates_of_completions
            previous_dates = [x for x in date_list if
                              self.model.Runcontrol.compare_dates(x, completion_date) < 0]
            if len(previous_dates) == 0:
                # if no dates that are smaller than the completion date then only add the perforation
                # at the current index with a new wellspec card.
                warnings.warn(f'No previous completions found for {well_name} at date: {completion_date}')
                new_completion_index = index
                write_out_headers = [' '.join(headers) + '\n']
                completion_table_as_list += write_out_headers
                return headers, new_completion_index, completion_table_as_list, False

            # get the most recent date that is earlier than the new completion date
            previous_dates = sorted(previous_dates, key=cmp_to_key(self.model.Runcontrol.compare_dates))
            last_date = str(previous_dates[-1])
            completion_to_find: NexusCompletion.InputDictionary = {'date': last_date}
            # find all completions at this date
            previous_completion_list = well.find_completions(completion_to_find)
            if len(previous_completion_list) > 0:
                prev_completion_properties = {k: v for k, v in previous_completion_list[0].to_dict().items() if
                                              v is not None}
                for key in prev_completion_properties:
                    if key == 'date':
                        continue
                    header_key = attribute_name_to_nexus_keyword(nexus_mapping, key)
                    if header_key not in headers:
                        headers.append(header_key)

            write_out_headers = [' '.join(headers) + '\n']
            completion_table_as_list += write_out_headers
            # run through the existing completions to duplicate the completion at the new time
            for completion in previous_completion_list:
                completion_table_as_list += completion.completion_to_wellspec_row(headers)
        else:
            write_out_headers = [' '.join(headers) + '\n']
            completion_table_as_list += write_out_headers
        return headers, new_completion_index, completion_table_as_list, True
