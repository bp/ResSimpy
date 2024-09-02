"""Class for dealing with logfiles produced from the nexus simulation engine."""
from __future__ import annotations

import os
import warnings
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import ResSimpy.Nexus.nexus_file_operations as nfo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


class Logging:
    def __init__(self, model: NexusSimulator) -> None:
        """Class for controlling all logging and logfile (*.log) related functionality.

        Args:
            model: NexusSimulator instance
            __job_id (int): Run job ID for executed runs
            __simulation_start_time (Optional[str]): Execution start time of the simulation when submitted \
                to calculation engine
            __simulation_end_time (Optional[str]): Execution end time of the last time the simulation was run
            __previous_run_time (Optional[str]): Difference between simulation execution start time and end time.
        """
        self.__model = model
        self.__job_id: int = -1
        self.__simulation_start_time: Optional[str] = None
        self.__simulation_end_time: Optional[str] = None
        self.__previous_run_time: Optional[str] = None

    @staticmethod
    def get_simulation_time(line: str) -> str:
        """Searches for the simulation time in a line.

        Args:
            line (str): line to search for the simulation time

        Raises:
            ValueError: Throws error if get_next_value doesn't find any subsequent value in the line

        Returns:
            str: value found after TIME card in a line
        """
        value_found = False
        value = ''
        line_string = line
        while value_found is False:
            next_value = nfo.get_next_value(0, [line_string], line_string)
            if next_value is None:
                raise ValueError(
                    f'No next value found in the line supplied, line: {line_string}')
            if next_value == 'on':
                line_string = line_string.replace(next_value, '', 1)
                next_value = nfo.get_next_value(0, [line_string], line_string)
                if next_value is None:
                    raise ValueError(
                        f'No next value found in the line supplied, line: {line_string}')
                for c in range(6):
                    line_string = line_string.replace(next_value, '', 1)
                    next_value = nfo.get_next_value(0, [line_string], line_string)
                    if next_value is None:
                        raise ValueError(
                            f'No next value found in the line supplied, line: {line_string}')
                    value += next_value + (' ' if c < 5 else '')
                value_found = True
            line_string = line_string.replace(next_value, '', 1)
        return value

    @staticmethod
    def convert_server_date(original_date: str) -> datetime:
        """Convert a datetime string from the server for when the simulation was started to a strptime object.

        Args:
            original_date (str): string of a date with format: "Mon Jan 01 00:00:00 CST 2020"

        Returns:
            datetime: datetime object derived from the input string
        """

        date_format = '%a %b %d %X %Z %Y'
        converted_date = original_date

        # Convert CDT and CST timezones as Python doesn't work with CDT for some reason
        if 'CDT' in original_date:
            converted_date = converted_date.replace('CDT', '-0500', 1)
            date_format = '%a %b %d %X %z %Y'
        elif 'CST' in original_date:
            converted_date = converted_date.replace('CST', '-0600', 1)
            date_format = '%a %b %d %X %z %Y'

        return datetime.strptime(converted_date, date_format)

    @staticmethod
    def get_errors_warnings_string(log_file_line_list: list[str]) -> Optional[str]:
        """Retrieves the number of warnings and errors from the simulation log output, and formats them as a string.

        Args:
            log_file_line_list (list[str]): log file formatted as a list of strings with \
                a new list entry per line

        Returns:
            Optional[str]: string containing the errors and warnings from the simulation log. \
                None if error/warning set is too short
        """
        error_warning = ""
        for line in log_file_line_list:
            modified_line = line.lower()
            if "errors" in modified_line and "warnings" in modified_line:
                error_warning = modified_line

        error_warning_list = [x for x in error_warning.split(" ") if x != ""]

        error_warning_list = [nfo.clean_up_string(x) for x in error_warning_list]

        if len(error_warning_list) < 4:
            return None

        errors = error_warning_list[1]
        warnings = error_warning_list[3]

        error_warning_str = f"Simulation complete - Errors: {errors} and Warnings: {warnings}"
        return error_warning_str

    def get_simulation_start_time(self) -> str:
        """Get the start time of an executed simulation run, if no simulation start time returns '-'."""
        self.get_simulation_status()
        if self.__simulation_start_time is not None:
            return self.__simulation_start_time
        else:
            return '-'

    def get_simulation_end_time(self) -> str:
        """Get the end time of an executed simulation run if it has completed, if no simulation end time returns '-'."""
        self.get_simulation_status()
        if self.__simulation_end_time is not None:
            return self.__simulation_end_time
        else:
            return '-'

    def get_job_id(self) -> int:
        """Get the job Id of a simulation run."""
        return self.__job_id

    def __get_log_path(self, from_startup: bool = False) -> Optional[str]:
        """Returns the path of the log file for the simulation.

        Args:
            from_startup (bool, optional): Searches the same directory as the original_fcs_file_path if True. \
            Otherwise searches the destination folder path, failing this then searches the \
            original_fcs_file_path if False. Defaults to False.

        Returns:
            Optional[str]: The path of the .log file from the simulation if found. If not found returns None.
        """
        folder_path = os.path.dirname(
            self.__model.original_fcs_file_path) if from_startup else os.path.dirname(self.__model.origin)
        try:
            files = os.listdir(folder_path)
        except FileNotFoundError:
            warnings.warn(f"Folder not found for logging details: {folder_path}")
            return None
        original_fcs_file_location = os.path.basename(self.__model.original_fcs_file_path)
        log_file_name = os.path.splitext(original_fcs_file_location)[0] + ".log" if from_startup \
            or self.__model.root_name is None else self.__model.root_name + ".log"

        if log_file_name in files:
            if from_startup:
                file_location = folder_path
            else:
                file_location = self.__model.destination if self.__model.destination is not None else folder_path

            log_file_path = file_location + "/" + log_file_name
            return log_file_path
        else:
            return None

    def __update_simulation_start_and_end_times(self, log_file_line_list: list[str]) -> None:
        """Updates the stored simulation execution start and end times from the log files.

        Args:
            log_file_line_list (list[str]): log file information represented with a new entry per line of the file.
        """
        for line in log_file_line_list:
            if nfo.check_token('start generic pdsh   prolog', line):
                value = self.get_simulation_time(line)
                self.__simulation_start_time = value

            if nfo.check_token('end generic pdsh   epilog', line):
                value = self.get_simulation_time(line)
                self.__simulation_end_time = value

    def get_simulation_status(self, from_startup: bool = False) -> Optional[str]:
        """Gets the run status of the latest simulation run.

        Args:
            from_startup (bool, optional): Searches the same directory as the original_fcs_file_path if True. \
            Otherwise searches the destination folder path, failing this then searches the \
            original_fcs_file_path if False. Defaults to False.

        Raises:
            NotImplementedError: If log file is not found - only supporting simulation status from log files

        Returns:
            Optional[str]: the error/warning string if the simulation has finished, otherwise \
                returns the running job ID. Empty string if a logfile is not found and from_start up is True
        """
        log_file = self.__get_log_path(from_startup)
        if log_file is None:
            if from_startup:
                return ''
            raise NotImplementedError(
                "Only retrieving status from a log file is supported at the moment")
        else:
            log_file_line_list = nfo.load_file_as_list(log_file)
            self.__update_simulation_start_and_end_times(log_file_line_list)
            job_finished = 'Nexus finished\n' in log_file_line_list
            if job_finished:
                self.__previous_run_time = self.__get_start_end_difference() if from_startup \
                    else self.__previous_run_time
                return self.get_errors_warnings_string(log_file_line_list=log_file_line_list)
            else:
                job_number_line = [
                    x for x in log_file_line_list if 'Job number:' in x]
                if len(job_number_line) > 0:
                    self.__job_id = int(job_number_line[0].split(":")[1])
                    return f"Job Running, ID: {self.__job_id}"
        return None

    def __get_start_end_difference(self) -> Optional[str]:
        """Returns a string with the previous time taken when the base case was run.

        Returns:
            Optional[str]: returns a human readable string of how long the simulation took to run
        """
        if self.__simulation_start_time is None or self.__simulation_end_time is None:
            return None

        start_date = self.convert_server_date(self.__simulation_start_time)
        end_date = self.convert_server_date(self.__simulation_end_time)

        total_difference = (end_date - start_date)
        days = int(total_difference.days)
        hours = int(total_difference.seconds / (60 * 60))
        minutes = int((total_difference.seconds / 60) - (hours * 60))
        seconds = int(total_difference.seconds -
                      (hours * 60 * 60) - (minutes * 60))

        return f"{days} Days, {hours} Hours, {minutes} Minutes {seconds} Seconds"

    def get_base_case_run_time(self) -> str:
        """Get the time taken for the base case to run. Returns '-' if no run time found."""
        if self.__previous_run_time is not None:
            return self.__previous_run_time
        else:
            return '-'

    def get_simulation_progress(self) -> float:
        """Returns the simulation progress from log files.

        Raises:
            NotImplementedError: Only retrieving status from a log file is supported at the moment
            ValueError: if no times from the runcontrol file are read in

        Returns:
            Optional[float]: how long through a simulation run as a proportion of the number of days \
                simulated as stated in the runcontrol
        """
        log_file_path = self.__get_log_path()
        if log_file_path is None:
            raise NotImplementedError("Only retrieving status from a log file is supported at the moment")
        log_file = nfo.load_file_as_list(log_file_path)

        read_in_times = False
        time_heading_location = None
        last_time = None
        for line in log_file:
            case_name_string = f"Case Name = {self.__model.root_name}"
            if case_name_string in line:
                read_in_times = True
                continue
            if read_in_times and nfo.check_token('TIME', line):
                heading_location = 0
                line_string = line
                while len(line_string) > 0:
                    next_value = nfo.get_next_value(0, [line_string], line_string)
                    if next_value is None:
                        break

                    line_string = line_string.replace(next_value, '', 1)
                    if next_value == 'TIME':
                        time_heading_location = heading_location
                    heading_location += 1

            if read_in_times and time_heading_location is not None:
                line_string = line
                next_value = nfo.get_next_value(0, [line_string], line_string)
                if next_value is not None and next_value.replace('.', '', 1).isdigit():
                    if time_heading_location == 0 and (last_time is None or float(next_value) > float(last_time)):
                        last_time = next_value
                    for x in range(time_heading_location):
                        line_string = line_string.replace(next_value, '', 1)
                        next_value = nfo.get_next_value(0, [line_string], line_string)
                        if next_value is None:
                            break
                        # When we reach the time column, read in the time value.
                        if x == (time_heading_location - 1) and \
                                (last_time is None or float(next_value) > float(last_time)):
                            last_time = next_value

        if last_time is not None:
            days_completed = self.__model._sim_controls.convert_date_to_number(last_time)
            if self.__model._sim_controls.times is None:
                raise ValueError("No times provided in the instance - please read them in from runcontrol file")
            total_days = self.__model._sim_controls.convert_date_to_number(self.__model._sim_controls.times[-1])
            return round((days_completed / total_days) * 100, 1)

        return 0
