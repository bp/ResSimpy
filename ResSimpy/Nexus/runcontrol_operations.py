from __future__ import annotations

import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cmp_to_key
from typing import Sequence, TYPE_CHECKING

import pandas as pd

import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat

from ResSimpy.Nexus.NexusSolverParameters import NexusSolverParameters
from ResSimpy.Nexus.constants import DATE_WITH_TIME_LENGTH
from ResSimpy.DataModelBaseClasses.SolverParameter import SolverParameter

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass
class GridToProc:
    """Class for storing the GRIDTOPROC table information from the Options file."""
    grid_to_proc_table: None | pd.DataFrame = None
    auto_distribute: None | str = None

    @property
    def table_header(self) -> str:
        """Start of the GRIDTOPROC definition table."""
        return 'GRIDTOPROC'

    @property
    def table_footer(self) -> str:
        """End of the GRIDTOPROC definition table."""
        return 'END' + self.table_header

    def get_number_of_processors(self) -> int:
        """Returns the number of processors to use for the simulation.

        Returns:
        -------
            int: number of processors to use for the simulation
        """
        if self.grid_to_proc_table is None:
            return 0
        if 'PROCESS' in self.grid_to_proc_table.columns:
            return self.grid_to_proc_table['PROCESS'].max()
        else:
            return 0


class SimControls:
    """Class for controlling all runcontrol and time related functionality."""

    def __init__(self, model: NexusSimulator) -> None:
        """Class for controlling all runcontrol and time related functionality.

        Args:
            model: NexusSimulator instance
            __times (None | list[str]): list of times to be included in the runcontrol file
            __date_format_string (str): How the dates should be formatted based on date_format.
            __number_of_processors (int): number of processors to use for the simulation. Comes from Options file in
            Nexus. Defaults to None when not specified in a GRIDTOPROC table.
        """
        self.__model = model
        self.__times: None | list[str] = None
        self.__date_format_string: str = "%m/%d/%Y"
        self.__number_of_processors: None | int = None
        self.__grid_to_proc: None | GridToProc = None
        self.__solver_parameters: NexusSolverParameters = NexusSolverParameters(model)

    @property
    def date_format_string(self) -> str:
        """Returns how dates should be formatted in the run control file as a string."""
        return self.__date_format_string

    @date_format_string.setter
    def date_format_string(self, value: str) -> None:
        self.__date_format_string = value

    @property
    def times(self) -> list[str]:
        """Returns list of times, if value is not provided it will return none."""
        return self.__times if self.__times is not None else []

    @staticmethod
    def get_times(times_file: list[str]) -> list[str]:
        """Retrieves a list of TIMES from the supplied Runcontrol / Include file.

        Args:
        ----
            times_file (list[str]): list of strings with each line from the file a new entry in the list
        Returns:
            list[str]: list of all the values following the TIME keyword in supplied file, \
                empty list if no values found
        """
        times = []

        for line in times_file:

            if fo.check_token('TIME', line):
                value = fo.get_token_value('TIME', line, times_file)
                if value is not None:
                    times.append(value)
            if fo.check_token('STOP', line):
                break

        return times

    @staticmethod
    def delete_times(file_content: list[str]) -> list[str]:
        """Deletes times from file contents.

        Args:
            file_content (list[str]):  list of strings with each line from the file a new entry in the list.

        Returns:
            list[str]: the modified file without any TIME cards in
        """
        new_file: list[str] = []
        previous_line_is_time = False
        for line in file_content:
            if "TIME " not in line and (previous_line_is_time is False or line != '\n'):
                new_file.append(line)
                previous_line_is_time = False
            elif "TIME " in line:
                previous_line_is_time = True
            else:
                previous_line_is_time = False
        return new_file

    @staticmethod
    def remove_times_from_file(file_content: list[str], output_file_path: str) -> None:
        """Removes the times from a file - used for replacing with new times.

        Args:
            file_content (list[str]): a list of strings containing each line of the file as a new entry
            output_file_path (str): path to the file to output to.
        """
        new_file_content = SimControls.delete_times(file_content)

        new_file_str = "".join(new_file_content)

        with open(output_file_path, "w") as text_file:
            text_file.write(new_file_str)

    def convert_date_to_number(self, date: str | float) -> float:
        """Converts a date to a number designating number of days from the start date.

        Args:
        ----
            date (str | float): a date or time stamp from a Nexus simulation
        Raises:
            ValueError: if supplied incorrect type for 'date' parameter

        Returns:
        -------
            float: the difference between the supplied date and the start date of the simulator
        """
        # If we can retrieve a number of days from date, use that, otherwise convert the string date to a number of days
        try:
            converted_date: str | float = float(date)
        except ValueError:
            if not isinstance(date, str):
                raise ValueError("convert_date_to_number: Incorrect type for 'date' parameter")
            converted_date = date

        if isinstance(converted_date, float):
            date_format = self.date_format_string
            if len(self.__model.start_date) == DATE_WITH_TIME_LENGTH:
                date_format += "(%H:%M:%S)"
            start_date_as_datetime = datetime.strptime(self.__model.start_date, date_format)
            date_as_datetime = start_date_as_datetime + timedelta(days=converted_date)
        else:
            start_date_format = self.date_format_string
            if len(self.__model.start_date) == DATE_WITH_TIME_LENGTH:
                start_date_format += "(%H:%M:%S)"
            end_date_format = self.date_format_string
            if len(converted_date) == DATE_WITH_TIME_LENGTH:
                end_date_format += "(%H:%M:%S)"
            date_as_datetime = datetime.strptime(converted_date, end_date_format)
            start_date_as_datetime = datetime.strptime(self.__model.start_date, start_date_format)

        difference = date_as_datetime - start_date_as_datetime
        return difference.total_seconds() / timedelta(days=1).total_seconds()

    def compare_dates(self, x: str | float, y: str | float) -> int:
        """Comparator for two supplied dates or numbers.

        Args:
        ----
            x (str | float): first date to compare
            y (str | float): second date to compare

        Returns:
        -------
            int: -1 if y > x, 0 if y == x, 1 if y < x
        """
        date_comp = self.convert_date_to_number(x) - self.convert_date_to_number(y)
        if date_comp < 0:
            date_comp_int = -1
        elif date_comp == 0:
            date_comp_int = 0
        else:
            date_comp_int = 1

        return date_comp_int

    def sort_remove_duplicate_times(self, times: list[str]) -> list[str]:
        """Removes duplicates and nans from the times list, then sorts them.

        Args:
        ----
            times (list[str]): list of times to remove duplicates from

        Returns:
        -------
            list[str]: list of times without duplicates
        """
        new_times = []
        for i in times:
            i_value = i.strip()
            if i != i or i_value in new_times:
                continue
            new_times.append(i_value)
        new_times = sorted(new_times, key=cmp_to_key(self.compare_dates))
        return new_times

    def check_date_format(self, date: str | float) -> None:
        """Checks that a supplied date is in the correct format.

        Args:
        ----
            date (str | float): date to check the format of
        Raises:
            ValueError: If a date provided isn't in a date format that the model expects
        """
        try:
            float(date)
        except ValueError:
            # Value isn't a float - attempt to extract date from value
            try:
                date_format = self.date_format_string
                if len(str(date)) == DATE_WITH_TIME_LENGTH:
                    date_format += "(%H:%M:%S)"
                datetime.strptime(str(date), date_format)
            except ValueError:
                current_date_format = self.get_date_format(self.__model.date_format)
                raise ValueError(
                    "Invalid date format " + str(date) + " the model is using " + current_date_format + " date format.")

    @staticmethod
    def get_date_format(date_format: DateFormat) -> str:
        """Returns the date format being used by the model.

        formats used: ('MM/DD/YYYY', 'DD/MM/YYYY').
        """

        if date_format is DateFormat.MM_DD_YYYY:
            return 'MM/DD/YYYY'
        else:
            return 'DD/MM/YYYY'

    def __update_times_in_file(self) -> None:
        """Updates the list of times in the Runcontrol file to the current stored values in __times.

        Returns:
            None: writes out a file at the same path as the existing runcontrol file
        """
        self.__model.check_output_path()
        if self.__model.model_files.runcontrol_file is None or \
                self.__model.model_files.runcontrol_file.location is None:
            raise ValueError(f"No file path found for {self.__model.model_files}")
        file_content = self.__model.model_files.runcontrol_file.get_flat_list_str_file
        filename = self.__model.model_files.runcontrol_file.location

        new_file_content = self.__model._sim_controls.delete_times(file_content)

        time_list = self.times
        stop_string = 'STOP\n'
        if stop_string in new_file_content:
            new_file_content.remove(stop_string)

        def prepend_time(s: str) -> str:
            return "TIME " + s

        time_list = [prepend_time(x) for x in time_list]
        num_times = len(time_list)

        new_line_list = ["\n\n"] * num_times
        zipped_list = list(zip(time_list, new_line_list))
        flat_list = [item for sublist in zipped_list for item in sublist]
        flat_list.append(stop_string)
        new_file_content.extend(flat_list)
        new_file_str = "".join(new_file_content)

        with open(filename, "w") as text_file:
            text_file.write(new_file_str)

    def load_run_control_file(self) -> None:
        """Loads the run control information into the class instance.

            If the write_times attribute is True then it expands out any INCLUDE files with the times found within
        Raises:
            ValueError: if the run_control_file attribute is None.
        """
        if self.__model.model_files.runcontrol_file is None:
            warnings.warn(f"Run control file path not found for {self.__model.model_files.location}")
            return
        run_control_file_content = self.__model.model_files.runcontrol_file.get_flat_list_str_file

        if (run_control_file_content is None) or (self.__model.model_files.runcontrol_file.location is None):
            raise ValueError(f"No file path provided for {self.__model.model_files.runcontrol_file.location=}")

        # set the start date
        for line in run_control_file_content:
            if nfo.check_token('START', line):
                value = nfo.get_expected_token_value('START', line, run_control_file_content)
                if value is not None:
                    self.__model.start_date = value

        times = []
        run_control_times = self.get_times(run_control_file_content)
        times.extend(run_control_times)
        if self.__model.start_date is None or self.__model.start_date == '':
            try:
                self.__model.start_date = times[0]
            except IndexError:
                for line in run_control_file_content:
                    if nfo.check_token('TIME', line):
                        value = nfo.get_expected_token_value('TIME', line, run_control_file_content)
                        self.__model.start_date = value
                        warnings.warn(f'Setting start date to first time card found in the runcontrol file as: {value}')
                        break
                warnings.warn('No value found for start date explicitly with START or TIME card')

        self.__times = self.sort_remove_duplicate_times(times)

        # If we don't want to write the times, return here.
        if not self.__model.write_times:
            return
        if self.__model.model_files.runcontrol_file.include_locations is None:
            warnings.warn(f'No includes files found in {self.__model.model_files.runcontrol_file.location}')
            return
        for file in self.__model.model_files.runcontrol_file.include_locations:
            if self.__model.destination is not None:
                self.remove_times_from_file(run_control_file_content, file)

        self.modify_times(content=times, operation='replace')

    def modify_times(self, content: None | list[str] = None, operation: str = 'merge') -> None:
        """Modifies the output times in the simulation.

        Args:
        ----
            content (list[str]], optional): The content to modify using the above operation, \
            represented as a list of strings with a new entry per line of the file. Defaults to None.
            operation (str, optional): operation to perform on the content provided (e.g. 'merge'). Defaults to 'merge'.

        Raises:
        ------
            ValueError: if the supplied dates are before the start date of the simulation
        """
        if content is None:
            content = []
        for time in content:
            self.check_date_format(time)

        new_times = self.sort_remove_duplicate_times(content)
        if len(new_times) > 0 > self.compare_dates(new_times[0], self.__model.start_date):
            raise ValueError(
                f"The supplied date of {new_times[0]} precedes the start date of {self.__model.start_date}")
        operation = operation.lower()
        self.__times = self.__times if self.__times is not None else []

        if operation == 'merge':
            self.__times.extend(content)
        elif operation == 'replace':
            self.__times = content
        elif operation == 'reset':
            self.__times = []
        elif operation == 'remove':
            for time in content:
                if time in self.__times:
                    self.__times.remove(time)

        self.__times = self.sort_remove_duplicate_times(self.__times)

        if self.__model.destination is not None:
            self.__update_times_in_file()

    @property
    def number_of_processors(self) -> int | None:
        """Returns the number of processors to use for the simulation.

        Returns:
        -------
            int: number of processors to use for the simulation
        """
        if self.__number_of_processors is None and self.grid_to_proc is None:
            self._load_options_file()
        if self.__number_of_processors is None:
            # if not explicitly set in a GRIDTOPROC table, return 0
            return 0
        return self.__number_of_processors

    def _load_grid_to_procs(self, options_file_as_list: list[str]) -> GridToProc | None:
        """Loads the GRIDTOPROC table from the Options file.

        Args:
            options_file_as_list (list[str]): list of strings with each line from the file a new entry in the list

        Returns:
            None
        """
        grid_to_procs = GridToProc()
        start_index = None
        end_index = None
        read_table = True
        for i, line in enumerate(options_file_as_list):
            if nfo.check_token(grid_to_procs.table_header, line):
                start_index = i + 1
            if start_index is not None and nfo.check_token('AUTO', line):
                grid_to_procs.auto_distribute = nfo.get_expected_token_value('AUTO', line, options_file_as_list)
                read_table = False
            if nfo.check_token(grid_to_procs.table_footer, line):
                end_index = i
                break
        if start_index is None or end_index is None or not read_table:
            return grid_to_procs

        # read table into the object
        grid_to_procs.grid_to_proc_table = nfo.read_table_to_df(options_file_as_list[start_index:end_index],
                                                                keep_comments=False)
        # get the number of processors
        self.__number_of_processors = grid_to_procs.get_number_of_processors()

        return grid_to_procs

    def _load_options_file(self) -> None:
        """Load components of the options file to Objects."""
        # get the options file:
        if self.__model.model_files.options_file is None:
            raise ValueError(f"No options file found for {self.__model.model_files.location=}")
        options_file_content = self.__model.model_files.options_file.get_flat_list_str_file
        if options_file_content is None:
            raise ValueError(f"No file content found in options file {self.__model.model_files.options_file.location=}")
        self.__grid_to_proc = self._load_grid_to_procs(options_file_content)

    @property
    def grid_to_proc(self) -> GridToProc | None:
        """Returns the GridToProc object.

        Returns:
        -------
            GridToProc: GridToProc object
        """
        if self.__grid_to_proc is None:
            self._load_options_file()
        return self.__grid_to_proc

    @property
    def solver_parameters(self) -> Sequence[SolverParameter]:
        """Returns the NexusSolverParameters object.

        Returns:
        -------
            NexusSolverParameters: NexusSolverParameters object
        """
        return self.__solver_parameters.solver_parameters
