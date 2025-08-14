"""Class for handling all Reporting and runcontrol related tasks."""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Nexus.DataModels.NexusReportingRequests import NexusOutputRequest, NexusOutputContents
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.DataModelBaseClasses.Reporting import Reporting
from ResSimpy.Time.ISODateTime import ISODateTime

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusReporting(Reporting):
    """Class for handling all Reporting and runcontrol related tasks."""
    __ss_output_requests: list[NexusOutputRequest]
    __array_output_requests: list[NexusOutputRequest]
    __ss_output_contents: list[NexusOutputContents]
    __array_output_contents: list[NexusOutputContents]
    __load_status: bool = field(default=False, repr=False, compare=False)

    table_header = 'OUTPUT'
    table_footer = 'ENDOUTPUT'

    def __init__(self, model: NexusSimulator, assume_loaded: bool = False) -> None:
        """Initialises the NexusReporting class.

        Args:
            model (NexusSimulator): The Nexus model to get the reporting information from.
            assume_loaded(bool): Create the object assuming the file has already been loaded into memory.
        """
        super().__init__(model)
        self.__model: NexusSimulator = model
        self.__add_object_operations = AddObjectOperations(NexusOutputRequest, self.table_header, self.table_footer,
                                                           model)
        if assume_loaded:
            self.__load_status = True
        self.__ss_output_requests = []
        self.__ss_output_contents = []
        self.__array_output_requests = []
        self.__array_output_contents = []

    @property
    def ss_output_requests(self) -> list[NexusOutputRequest]:
        """Gets the spreadsheet and tabulated output requests."""
        if not self.__load_status:
            self.load_output_requests()
        return self.__ss_output_requests

    @property
    def ss_output_contents(self) -> list[NexusOutputContents]:
        """Gets the contents requested for spreadsheet and tabulated results."""
        if not self.__load_status:
            self.load_output_requests()
        return self.__ss_output_contents

    @property
    def array_output_requests(self) -> list[NexusOutputRequest]:
        """Gets the array output requests."""
        if not self.__load_status:
            self.load_output_requests()
        return self.__array_output_requests

    @property
    def array_output_contents(self) -> list[NexusOutputContents]:
        """Gets the contents requested to be output for the arrays."""
        if not self.__load_status:
            self.load_output_requests()
        return self.__array_output_contents

    def add_map_properties_to_start_of_grid_file(self) -> None:
        """Adds 'map' statements to the start of the grid file to ensure standalone outputs all the required properties.

        Writes out to the same structured grid file path provided.

        Raises:
            ValueError: if no structured grid file path is specified in the class instance
        """
        structured_grid_path = self.__model.structured_grid_path
        if structured_grid_path is None:
            raise ValueError("No file path given or found for structured grid file path. \
                Please update structured grid file path")
        file = nfo.load_file_as_list(structured_grid_path)

        if not fo.value_in_file('MAPBINARY', file):
            new_file = ['MAPBINARY\n']
        else:
            new_file = []

        if not fo.value_in_file('MAPVDB', file):
            new_file.extend(['MAPVDB\n'])

        if not fo.value_in_file('MAPOUT', file):
            new_file.extend(['MAPOUT ALL\n'])
        else:
            line_counter = 0
            for line in file:
                if nfo.check_token('MAPOUT', line):
                    file[line_counter] = 'MAPOUT ALL\n'
                    break
                line_counter += 1

        new_file.extend(file)

        # Save the new file contents
        new_file_str = "".join(new_file)
        with open(structured_grid_path, "w") as text_file:
            text_file.write(new_file_str)

    def load_output_requests(self) -> None:
        """Loads output requests from the Nexus runcontrol file."""
        if self.__model.model_files.runcontrol_file is None:
            raise ValueError("No file path given or found for runcontrol file path. \
                Please update runcontrol file path")
        file_as_list = self.__model.model_files.runcontrol_file.get_flat_list_str_file

        # Get the output requests
        ss_output_requests: list[NexusOutputRequest] = []
        array_output_requests: list[NexusOutputRequest] = []

        ss_output_contents: list[NexusOutputContents] = []
        array_output_contents: list[NexusOutputContents] = []

        ss_start_index: int = -1
        array_start_index: int = -1
        current_date = self.__model.start_date
        for index, line in enumerate(file_as_list):

            # check for TIME keyword and update the current date
            if nfo.check_token('TIME', line):
                current_date = nfo.get_expected_token_value('TIME', token_line=line, file_list=file_as_list)

            if nfo.check_token('SPREADSHEET', line):
                ss_start_index = index + 1

            if ss_start_index > -1 and nfo.check_token('ENDSPREADSHEET', line):
                ss_end_index = index
                list_of_output_requests = self._get_output_request(file_as_list[ss_start_index:ss_end_index],
                                                                   date=current_date,
                                                                   output_type=OutputType.SPREADSHEET)
                ss_output_requests.extend(list_of_output_requests)

            if nfo.check_token('OUTPUT', line):
                array_start_index = index + 1
            if array_start_index > -1 and nfo.check_token('ENDOUTPUT', line):
                array_end_index = index
                list_of_output_requests = self._get_output_request(file_as_list[array_start_index:array_end_index],
                                                                   date=current_date,
                                                                   output_type=OutputType.ARRAY)
                array_output_requests.extend(list_of_output_requests)

            if nfo.check_token('SSOUT', line):
                ss_start_index = index + 1
            if ss_start_index > -1 and nfo.check_token('ENDSSOUT', line):
                ss_end_index = index
                list_of_output_contents = self._get_output_contents(file_as_list[ss_start_index:ss_end_index],
                                                                    date=current_date,
                                                                    output_type=OutputType.SPREADSHEET)
                ss_output_contents.extend(list_of_output_contents)

            if nfo.check_token('MAPOUT', line) or nfo.check_token('ARRAYOUT', line):
                ss_start_index = index + 1
            if ss_start_index > -1 and nfo.check_token('ENDMAPOUT', line) or nfo.check_token('ENDARRAYOUT', line):
                ss_end_index = index
                list_of_output_contents = self._get_output_contents(file_as_list[ss_start_index:ss_end_index],
                                                                    date=current_date,
                                                                    output_type=OutputType.ARRAY)
                array_output_contents.extend(list_of_output_contents)

        self.__ss_output_requests = ss_output_requests
        self.__array_output_requests = array_output_requests
        self.__ss_output_contents = ss_output_contents
        self.__array_output_contents = array_output_contents
        self.__load_status = True

    @staticmethod
    def _get_output_request(table_file_as_list: list[str], date: str, output_type: OutputType) \
            -> list[NexusOutputRequest]:
        """Gets the output objects from the runcontrol file.

        Args:
            table_file_as_list (list[str]): The table file as a list of strings
            date (str): The date of the output
            output_type (OutputType): The output type as an Enum
        """
        output_request_with_number = ['DT', 'DTTOL', 'FREQ', 'TIMESTEP']

        resulting_output_requests: list[NexusOutputRequest] = []
        for line in table_file_as_list:
            number_defined_float: None | float = None
            element = nfo.get_next_value(start_line_index=0, file_as_list=[line])
            if element is None or element == '':
                continue
            frequency = nfo.get_expected_token_value(element, token_line=line,
                                                     file_list=[line])
            if frequency in output_request_with_number:
                number_defined = nfo.get_expected_token_value(frequency, token_line=line,
                                                              file_list=[line])
                try:
                    number_defined_float = float(number_defined)
                except ValueError:
                    warnings.warn(f'Unable to convert output request number to float: {number_defined}')
                    number_defined_float = None

            frequency_enum = FrequencyEnum[frequency]
            output_request = NexusOutputRequest(date=date, output=element, output_frequency=frequency_enum,
                                                output_frequency_number=number_defined_float, output_type=output_type)
            resulting_output_requests.append(output_request)

        return resulting_output_requests

    @staticmethod
    def _get_output_contents(table_file_as_list: list[str], date: str, output_type: OutputType) \
            -> list[NexusOutputContents]:
        """Gets the output contents from a table.

        Args:
            table_file_as_list (list[str]): The table file as a list of strings
            date (str): The date of the output
            output_type (OutputType): The output type as an Enum
        """
        resulting_output_contents: list[NexusOutputContents] = []
        for line in table_file_as_list:
            element = nfo.get_next_value(start_line_index=0, file_as_list=[line])
            if element is None or element == '':
                continue
            value: None | str = element
            output_contents = []
            filter_line = line
            while value is not None:
                filter_line = filter_line.replace(value, '', 1)
                value = nfo.get_next_value(start_line_index=0, file_as_list=[filter_line])
                if value is not None:
                    output_contents.append(value)

            output_contents_obj = NexusOutputContents(date=date, output_contents=output_contents,
                                                      output_type=output_type,
                                                      output=element)
            resulting_output_contents.append(output_contents_obj)

        return resulting_output_contents

    def add_array_output_request(self, output_request: NexusOutputRequest, add_to_file: bool = True) -> None:
        """Adds an output request to the array output requests list.

        Args:
            output_request (NexusOutputRequest): The output request to add the model and associated in memory files.
            add_to_file (bool): If True, adds the output request to the runcontrol file. If False just adds it to
                memory.
        """
        self.add_array_output_request_to_memory(output_request)

        if not add_to_file:
            return
        if self.__model.model_files.runcontrol_file is None:
            raise ValueError("No file found for runcontrol file path.")

        file_as_list = self.__model.model_files.runcontrol_file.get_flat_list_str_file
        obj_props = output_request.to_dict(add_units=False)
        if output_request.date is None:
            output_request.date = self.__model.start_date
        self.__add_object_operations.add_object_to_file(date=output_request.date,
                                                        file_as_list=file_as_list,
                                                        file_to_add_to=self.__model.model_files.runcontrol_file,
                                                        new_object=output_request,
                                                        object_properties=obj_props,
                                                        skip_reading_headers=True,
                                                        )

    def add_array_output_request_to_memory(self, output_request: NexusOutputRequest) -> None:
        """Adds an output request to the array output requests list in memory.

        Args:
            output_request (NexusOutputRequest): The output request to add to the model and associated in memory files.
        """
        if output_request.date is None:
            raise ValueError(f"No date on NexusOutputRequest object: {output_request}")
        if isinstance(output_request, NexusOutputContents):
            raise TypeError("NexusOutputRequest object should not be an instance of NexusOutputContents."
                            "Use add_array_output_contents_to_memory instead.")
        elif not isinstance(output_request, NexusOutputRequest):
            raise TypeError(f"Expected NexusOutputRequest object, got {type(output_request)}")

        if output_request.output_type == OutputType.ARRAY:
            self.__array_output_requests.append(output_request)
        elif output_request.output_type == OutputType.SPREADSHEET:
            self.__ss_output_requests.append(output_request)
        else:
            raise ValueError(f"Unknown output type: {output_request.output_type}")

    def add_array_output_contents_to_memory(self, output_contents: NexusOutputContents) -> None:
        """Adds an output contents to the array output contents list in memory.

        Args:
            output_contents (NexusOutputContents): The output contents to add to the model and associated in
                memory files.
        """

        if output_contents.date is None:
            raise ValueError(f"No date on NexusOutputContents object: {output_contents}")
        if isinstance(output_contents, NexusOutputRequest):
            raise TypeError("NexusOutputContents object should not be an instance of NexusOutputRequest."
                            "Use add_array_output_request_to_memory instead.")
        elif not isinstance(output_contents, NexusOutputContents):
            raise TypeError(f"Expected NexusOutputContents object, got {type(output_contents)}")

        if output_contents.output_type == OutputType.ARRAY:
            self.__array_output_contents.append(output_contents)
        elif output_contents.output_type == OutputType.SPREADSHEET:
            self.__ss_output_contents.append(output_contents)
        else:
            raise ValueError(f"Unknown output type: {output_contents.output_type}")

    def to_string_for_date(self, date: ISODateTime) -> str:
        """Outputs the reporting requests and content for a given date as a string.

        Args:
            date (ISODateTime): The date to output the contents for.

        Returns:
            str: The string representation of the reporting requests and content for the given date.
        """
        result = ''
        ss_output_requests_for_date = [x for x in self.ss_output_requests if x.iso_date == date]
        if ss_output_requests_for_date:
            result += 'SPREADSHEET\n'
            for request in ss_output_requests_for_date:
                result += request.to_table_line(headers=[])
            result += 'ENDSPREADSHEET\n'

        ss_output_contents_for_date = [x for x in self.ss_output_contents if x.iso_date == date]
        if ss_output_contents_for_date:
            result += 'SSOUT\n'
            for content in ss_output_contents_for_date:
                result += content.to_table_line(headers=[])
            result += 'ENDSSOUT\n'

        array_output_requests_for_date = [x for x in self.array_output_requests if x.iso_date == date]
        if array_output_requests_for_date:
            result += 'OUTPUT\n'
            for request in array_output_requests_for_date:
                result += request.to_table_line(headers=[])
            result += 'ENDOUTPUT\n'

        array_output_contents_for_date = [x for x in self.array_output_contents if x.iso_date == date]
        if array_output_contents_for_date:
            result += 'MAPOUT\n'
            for content in array_output_contents_for_date:
                result += content.to_table_line(headers=[])
            result += 'ENDMAPOUT\n'

        return result

    def get_all_reporting_dates(self) -> set[ISODateTime]:
        """Gets all the reporting dates from the output requests and contents.

        Returns:
            set[ISODateTime]: A set of all unique reporting dates.
        """
        all_dates = set()
        for request in self.ss_output_requests + self.array_output_requests:
            all_dates.add(request.iso_date)
        for content in self.ss_output_contents + self.array_output_contents:
            all_dates.add(content.iso_date)
        return all_dates
