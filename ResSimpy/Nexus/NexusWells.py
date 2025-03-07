"""A class for collecting all NexusWell objects in a NexusSimulator.

Handles adding and removing completions as well as rescheduling wells.
"""
from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Sequence, Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.Enums.HowEnum import OperationEnum
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusKeywords.wells_keywords import WELLS_KEYWORDS
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.GenericContainerClasses.Wells import Wells
from ResSimpy.Nexus.load_wells import load_wells
import ResSimpy.FileOperations.file_operations as fo
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.invert_nexus_map import attribute_name_to_nexus_keyword

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator
    from ResSimpy.Nexus.DataModels.NexusWell import NexusWell


@dataclass(kw_only=True)
class NexusWells(Wells):
    """A class for collecting all NexusWell objects in a NexusSimulator.

    Handles adding and removing completions as well as rescheduling wells. This is usually accessed through the
    model.wells property.

    Arguments:
        model (Simulator): NexusSimulator object that has the instance of wells on.
    """
    __model: NexusSimulator = field(compare=False, repr=False)
    __date_format: DateFormat = DateFormat.MM_DD_YYYY
    _wells: list[NexusWell] = field(default_factory=list)

    def __init__(self, model: NexusSimulator) -> None:
        """Initialises the NexusWells class.

        Args:
            model (NexusSimulator): The model object that contains this NexusWells instance.
        """
        self.__model = model
        self.__add_object_operations = AddObjectOperations(NexusCompletion, self.table_header, self.table_footer, model)
        super().__init__()

    @property
    def model(self) -> NexusSimulator:
        """The model object that contains this NexusWells instance."""
        return self.__model

    @property
    def start_date(self) -> str:
        """Returns start date of the model."""
        return self.__model.start_date

    @property
    def date_format(self) -> DateFormat:
        """Returns date format of the loads wells."""
        # If we haven't loaded in the wells file, load it in case date format is specified there.
        if not self._wells_loaded:
            self._load()
        return self.__date_format

    @property
    def table_header(self) -> str:
        """Returns string representing the start of the table in the wellspec file."""
        return 'WELLSPEC'

    @property
    def table_footer(self) -> str:
        """Returns string representing the end of the table in the file."""
        return ''

    def get_all(self) -> Sequence[NexusWell]:
        """Returns list of all loaded wells in the Nexus file."""
        if not self._wells_loaded:
            self._load()
        return self._wells

    def get(self, well_name: str) -> Optional[NexusWell]:
        """Returns a specific well requested, or None if that well cannot be found."""
        if not self._wells_loaded:
            self._load()

        wells_to_return = filter(lambda x: x.well_name.upper() == well_name.upper(), self._wells)

        return next(wells_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Returns data frame representing all processed completions data in the Nexus file."""
        # loop through wells and completions to output a table
        if not self._wells_loaded:
            self._load()

        store_dictionaries = []
        for well in self._wells:
            for completion in well.completions:
                completion_props: dict[str, None | float | int | str] = {
                    'well_name': well.well_name,
                    'units': well.unit_system.name,
                }
                completion_props.update(completion.to_dict())
                store_dictionaries.append(completion_props)
        df_store = pd.DataFrame(store_dictionaries)
        df_store = df_store.dropna(axis=1, how='all')
        return df_store

    def _load(self) -> None:
        if self.__model.model_files.well_files is None:
            raise FileNotFoundError('No wells files found for current model.')
        for method_number, well_file in self.__model.model_files.well_files.items():
            if well_file.location is None:
                warnings.warn(f'Well file location has not been found for {well_file}')
                continue
            wells, date_format = load_wells(nexus_file=well_file, start_date=self.__model.start_date,
                                            default_units=self.__model.default_units, parent_wells_instance=self,
                                            model_date_format=self.__model.date_format)

            self._wells = wells
            self.__date_format = date_format
        self._wells_loaded = True
        # Ensure the newly added wells have additional information populated from the surface file.
        self.model.network.get_load_status()

    def modify(self, well_name: str, completion_properties_list: list[dict[str, None | float | int | str]],
               how: OperationEnum = OperationEnum.ADD) -> None:
        """Modify the existing wells in memory using a dictionary of properties.

        Args:
        ----
            well_name (str): name of the well to modify
            completion_properties_list (list[InputDict]): a dictionary containing the properties to modify with the \
                attribute as keys and the values as the updated property value. If remove will remove perforation that \
                matches the values in the dictionary.
            how (OperationEnum): operation enum taking the values OperationEnum.ADD, OperationEnum.REMOVE. \
                Specifies how to modify the existing wells perforations.
            remove_all_that_match (bool): If True will remove all wells that partially match the completion_properties\
                provided. If False will remove perforation if only one matches, if several match throws a warning and \
                does not remove them.
            write_to_file (bool): If True writes directly to file. (Currently not in use)
        """
        well = self.get(well_name)
        if well is None:
            raise ValueError(f'No well named {well_name} found in simulator')
        for perf in completion_properties_list:
            if how == OperationEnum.ADD:
                try:
                    date = perf.get('date')
                except AttributeError:
                    raise AttributeError(
                        f'No date provided in perf: {perf}, please provide a date to add the perforation at.')
                if date is None:
                    raise AttributeError(
                        f'No date provided in perf: {perf}, please provide a date to add the perforation at.')
                self.add_completion(well_name=well_name, completion_properties=perf)
            elif how == OperationEnum.REMOVE:
                completions_to_remove = well.find_completions(perf)
                well._remove_completions_from_memory(completions_to_remove)
            elif how == OperationEnum.MODIFY:
                raise NotImplementedError('Modify in place not yet available. Please choose one of ADD/REMOVE')
            else:
                raise ValueError('Please select one of the valid OperationEnum values: e.g. OperationEnum.ADD')

    def add_completion(self, well_name: str, completion_properties: dict[str, None | float | int | str],
                       preserve_previous_completions: bool = True, comments: Optional[str] = None) -> None:
        """Adds a completion to an existing wellspec file.

        Args:
            well_name (str): well name to update
            completion_properties (dict[str, float | int | str]): properties of the completion you want to update.
            Must contain date of the completion to be added.
            preserve_previous_completions (bool): if true a new perforation added on a TIME card without a \
            wellspec card for that well will preserve the previous completions from the closest TIME card in addition \
            to the new completion
            comments (Optional[str]): Comments to add to the object line in the file.
        """
        basic_dict: dict[str, float | int | str | None] = {'name': well_name}
        _, completion_date = self.__add_object_operations.check_name_date(basic_dict | completion_properties)
        well = self.get(well_name)
        if well is None:
            # TODO could make this not raise an error and instead initialize a NexusWell and add it to NexusWells
            raise ValueError(
                f"No well found named: {well_name}. Cannot add completion to a well that doesn't exist")
        well_id = well.completions[0].id

        # add completion in memory
        new_completion = well._add_completion_to_memory(date=completion_date,
                                                        completion_properties=completion_properties,
                                                        date_format=self.date_format)

        if self.__model.model_files.well_files is None:
            raise FileNotFoundError('No well file found, cannot modify ')

        wellspec_file = self.__add_object_operations.find_which_file_from_id(obj_id=well_id,
                                                                             file_type_to_search='well_files')

        # initialise some storage variables
        nexus_mapping = NexusCompletion.get_keyword_mapping()
        new_completion_time_index = -1
        header_index = -1
        headers: list[str] = []
        headers_original: list[str] = []
        additional_headers: list[str] = []
        file_content = wellspec_file.get_flat_list_str_file
        date_found = False
        new_completion_index = len(file_content)
        new_completion_string: list[str] = []
        last_valid_line_index: int = -1
        writing_new_wellspec_table = False
        date_comp = 0
        # if no time cards present in the file just find the name of the well instead
        if not fo.value_in_file('TIME', file_content):
            new_completion_time_index = 0

        for index, line in enumerate(file_content):
            if header_index == -1 and fo.check_token('TIME', line):
                wellspec_date = fo.get_expected_token_value('TIME', line, [line])
                date_comp = self.__model._sim_controls.compare_dates(wellspec_date, completion_date)
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

            if fo.check_token('WELLSPEC', line) and fo.get_token_value('WELLSPEC', line, [line]) == well_name \
                    and new_completion_time_index != -1:
                # get the header of the wellspec table
                header_index, headers, headers_original = self.__add_object_operations.get_and_write_new_header(
                    additional_headers, completion_properties, file_content, index, nexus_mapping, wellspec_file
                )
                continue

            if header_index != -1 and nfo.nexus_token_found(line, WELLS_KEYWORDS) and index > header_index:
                # if we hit the end of the wellspec table for the given well set the index for the new completion
                if last_valid_line_index != -1:
                    new_completion_index = last_valid_line_index + 1
                break

            elif header_index != -1 and index > header_index:
                # check for valid rows + fill extra columns with NA
                line_valid_index = self.__add_object_operations.fill_in_nas(additional_headers, headers_original, index,
                                                                            line, wellspec_file, file_content)
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
        new_completion_string += [new_completion.to_table_line(headers)]
        new_completion_additional_lines = len(new_completion_string)
        if writing_new_wellspec_table:
            new_completion_string += ['\n']
        # write out to the file_content_as_list
        new_completion_object_ids = {new_completion.id: [new_completion_index + new_completion_additional_lines - 1]}
        wellspec_file.add_to_file_as_list(additional_content=new_completion_string, index=new_completion_index,
                                          additional_objects=new_completion_object_ids, comments=comments)

    def __write_out_existing_wellspec(self, completion_date: str,
                                      completion_properties: dict[str, None | float | int | str],
                                      date_found: bool, index: int, new_completion_index: int,
                                      preserve_previous_completions: bool, well: NexusWell, well_name: str) -> \
            tuple[list[str], int, list[str], bool]:
        """Writes out the existing wellspec for a well at a new time stamp."""
        nexus_mapping = NexusCompletion.get_keyword_mapping()
        completion_table_as_list = ['\n']
        if not date_found:
            completion_table_as_list += ['TIME ' + completion_date + '\n']
        completion_table_as_list += ['WELLSPEC ' + well_name + '\n']
        headers = [k for k, v in nexus_mapping.items() if v[0] in completion_properties]
        if preserve_previous_completions:
            # get all the dates for that well
            date_list = well.dates_of_completions
            previous_dates = [x for x in date_list if
                              self.__model._sim_controls.compare_dates(x, completion_date) < 0]
            if len(previous_dates) == 0:
                # if no dates that are smaller than the completion date then only add the perforation
                # at the current index with a new wellspec card.
                warnings.warn(f'No previous completions found for {well_name} at date: {completion_date}')
                new_completion_index = index
                write_out_headers = [' '.join(headers) + '\n']
                completion_table_as_list += write_out_headers
                return headers, new_completion_index, completion_table_as_list, False

            # get the most recent date that is earlier than the new completion date
            previous_dates = sorted(previous_dates, key=cmp_to_key(self.__model._sim_controls.compare_dates))
            last_date = str(previous_dates[-1])
            completion_to_find: dict[str, None | float | int | str] = {'date': last_date}
            # find all completions at this date
            previous_completion_list = well.find_completions(completion_to_find)
            if len(previous_completion_list) > 0:
                prev_completion_properties = {k: v for k, v in previous_completion_list[0].to_dict().items() if
                                              v is not None}
                for key in prev_completion_properties:
                    if key == 'date' or key == 'iso_date':
                        continue
                    header_key = attribute_name_to_nexus_keyword(nexus_mapping, key)
                    if header_key not in headers:
                        headers.append(header_key)

            write_out_headers = [' '.join(headers) + '\n']
            completion_table_as_list += write_out_headers
            # run through the existing completions to duplicate the completion at the new time
            for completion in previous_completion_list:
                completion_table_as_list += [completion.to_table_line(headers)]
        else:
            write_out_headers = [' '.join(headers) + '\n']
            completion_table_as_list += write_out_headers
        return headers, new_completion_index, completion_table_as_list, True

    def remove_completion(self, well_name: str,
                          completion_properties: Optional[dict[str, None | float | int | str]] = None,
                          completion_id: Optional[UUID] = None) -> None:
        """Removes well completion from wellspec file.

        Args:
            well_name(str): Name of the well
            completion_properties(Optional[dict[str, None | float | int | str]]): The completion properties.
            completion_id(Optional[UUID) = None): Completion unique identifier or ID.
        """

        well = self.get(well_name)
        if well is None:
            raise ValueError(f'No well found with name: {well_name}')

        if completion_properties is None and completion_id is None:
            raise ValueError('Must provide one of completion_properties dictionary or completion_id.')

        # check for a date:
        if completion_properties is not None:
            completion_date = completion_properties.get('date', 'NO_DATE_PROVIDED')
            if completion_date == 'NO_DATE_PROVIDED':
                raise AttributeError('Completion requires a date. '
                                     'Please provide a date in the completion_properties_list dictionary.')
            if completion_id is None:
                completion_id = well.find_completion(completion_properties).id
        if completion_id is None:
            raise ValueError('No completion found for completion_properties')
        # find which wellspec file we should edit
        wellspec_file = self.__add_object_operations.find_which_file_from_id(obj_id=completion_id,
                                                                             file_type_to_search='well_files')

        # remove from the well object/wells class
        completion_date = well.get_completion_by_id(completion_id).date
        well._remove_completion_from_memory(completion_to_remove=completion_id)

        # drop it from the wellspec file or include file if stored in include file
        if wellspec_file.object_locations is None:
            raise ValueError(f'No object locations specified, cannot find completion id: {completion_id}')
        completion_indices = wellspec_file.object_locations[completion_id]
        if len(completion_indices) > 0:
            for comp_index in completion_indices:
                wellspec_file.remove_from_file_as_list(comp_index, [completion_id])

        # check that we have completions left:
        find_completions_dict: dict[str, None | float | int | str] = {'date': completion_date}
        remaining_completions = well.find_completions(find_completions_dict)
        if len(remaining_completions) == 0:
            # if there are no more completions remaining for that time stamp then remove the wellspec header!
            self.__remove_wellspec_header(str(completion_date), well_name, wellspec_file)

    def __remove_wellspec_header(self, completion_date: str, well_name: str, wellspec_file: NexusFile) -> None:
        """Removes the wellspec and header if the wellspec table is empty.

        Must first check for whether the well has any remaining completions in the wellspec table.
        """
        nexus_mapping = NexusCompletion.get_keyword_mapping()
        completion_date_found = False
        file_content = wellspec_file.get_flat_list_str_file
        wellspec_index = -1
        header_index = -1
        if not fo.value_in_file('TIME', file_content):
            # if we have no completion date in the file then we have effectively found the right TIME
            completion_date_found = True
        for index, line in enumerate(file_content):
            if fo.check_token('TIME', line) and fo.get_expected_token_value('TIME', line, [line]) == \
                    completion_date:
                completion_date_found = True
            if completion_date_found and fo.check_token('WELLSPEC', line) and \
                    fo.get_token_value('WELLSPEC', line, [line]) == well_name:
                # get the index in the list as string
                wellspec_index = index
                keyword_map = {x: y[0] for x, y in nexus_mapping.items()}
                wellspec_table = file_content[wellspec_index::]
                header_index, _ = nfo.get_table_header(file_as_list=wellspec_table, header_values=keyword_map)
                header_index += wellspec_index
                break
        wellspec_file.remove_from_file_as_list(header_index)
        wellspec_file.remove_from_file_as_list(wellspec_index)

    def modify_completion(self, well_name: str, properties_to_modify: dict[str, None | float | int | str],
                          completion_to_change: Optional[dict[str, None | float | int | str]] = None,
                          completion_id: Optional[UUID] = None,
                          comments: Optional[str] = None) -> None:
        """Modify an existing matching completion, preserves attributes and modifies only additional properties \
        found within the provided properties to modify dictionary.

        Args:
            well_name (str): Name of the well with the completion to be modified.
            properties_to_modify (dict[str, None | float | int | str]): attributes to change to.
            completion_to_change (Optional[dict[str, None | float | int | str]]): properties of the existing completion.
            User must provide enough to uniquely identify the completion.
            completion_id (Optional[UUID]): If provided will match against a known UUID for the completion.
            comments (Optional[str]): Comments to add to the object line in the file.
        """
        well = self.get(well_name)
        if well is None:
            raise ValueError(f'No well found with name: {well_name}')

        if completion_to_change is not None:
            completion = well.find_completion(completion_to_change)
            completion_id = completion.id
        elif completion_id is not None:
            completion = well.get_completion_by_id(completion_id)
        else:
            raise ValueError('Must provide one of completion_to_change dictionary or completion_id')

        # start with the existing properties
        update_completion_properties: dict[str, None | float | int | str] = \
            {k: v for k, v in completion.to_dict().items() if v is not None}

        update_completion_properties.update(properties_to_modify)

        self.remove_completion(well_name, completion_id=completion_id)
        self.add_completion(well_name, update_completion_properties, preserve_previous_completions=True,
                            comments=comments)
