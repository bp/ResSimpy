"""Class for handling all Reporting and runcontrol related tasks."""
import warnings
from dataclasses import dataclass

import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType


@dataclass(kw_only=True)
class NexusOutputRequest:
    """Class for handling output requests in Nexus."""
    date: str
    output: str
    output_type: OutputType
    output_frequency: FrequencyEnum
    output_frequency_number: None | float


@dataclass(kw_only=True)
class NexusOutputContents:
    """Class for handling the output that Nexus produces."""
    date: str
    output_contents: list[str]
    output_type: OutputType
    output: str


@dataclass(kw_only=True)
class NexusReporting:
    """Class for handling all Reporting and runcontrol related tasks."""
    __ss_output_requests: list[NexusOutputRequest]
    __array_output_requests: list[NexusOutputRequest]
    __ss_output_contents: list[NexusOutputContents]
    __array_output_contents: list[NexusOutputContents]

    def __init__(self, model) -> None:
        self.__model = model

    @property
    def ss_output_requests(self) -> list[NexusOutputRequest]:
        return self.__ss_output_requests

    @property
    def array_output_requests(self) -> list[NexusOutputRequest]:
        return self.__array_output_requests

    @property
    def ss_output_contents(self) -> list[NexusOutputContents]:
        return self.__ss_output_contents

    @property
    def array_output_contents(self) -> list[NexusOutputContents]:
        return self.__array_output_contents

    def add_map_properties_to_start_of_grid_file(self):
        """Adds 'map' statements to the start of the grid file to ensure standalone outputs all the required \
        properties. Writes out to the same structured grid file path provided.

        Raises:
            ValueError: if no structured grid file path is specified in the class instance
        """
        structured_grid_path = self.__model.structured_grid_path
        if self.__model.structured_grid_path is None:
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
