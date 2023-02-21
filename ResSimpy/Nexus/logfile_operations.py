from datetime import datetime, timedelta
from typing import Optional, Union
import ResSimpy.Nexus.nexus_file_operations as nfo


def get_simulation_time(line: str) -> str:
    """searches for the simulation time in a line

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


def convert_server_date(original_date: str) -> datetime:
    """Convert a datetime string from the server for when the simulation was started to a strptime object

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


def get_errors_warnings_string(log_file_line_list: list[str]) -> Optional[str]:
    """Retrieves the number of warnings and errors from the simulation log output,
    and formats them as a string

    Args:
        log_file_line_list (list[str]): log file formatted as a list of strings with \
            a new list entry per line

    Returns:
        Optional[str]: string containing the errors and warnings from the simulation log. \
            None if error/warning set is too short
    """
    error_warning = ""
    for line in log_file_line_list:
        line = line.lower()
        if "errors" in line and "warnings" in line:
            error_warning = line

    error_warning_list = [x for x in error_warning.split(" ") if x != ""]

    error_warning_list = [nfo.clean_up_string(x) for x in error_warning_list]

    if len(error_warning_list) < 4:
        return None

    errors = error_warning_list[1]
    warnings = error_warning_list[3]

    error_warning_str = f"Simulation complete - Errors: {errors} and Warnings: {warnings}"
    return error_warning_str


def __convert_date_to_number(self, date: Union[str, int, float]) -> float:
    """Converts a date to a number designating number of days from the start date

    Args:
        date (Union[str, int, float]): a date or time stamp from a Nexus simulation

    Raises:
        ValueError: if supplied incorrect type for 'date' parameter

    Returns:
        float: the difference between the supplied date and the start date of the simulator
    """
    # If we can retrieve a number of days from date, use that, otherwise convert the string date to a number of days
    try:
        converted_date: Union[str, float] = float(date)
    except ValueError:
        if not isinstance(date, str):
            raise ValueError(
                "__convert_date_to_number: Incorrect type for 'date' parameter")
        converted_date = date

    if isinstance(converted_date, float):
        date_format = self.__date_format_string
        if len(self.start_date) == self.DATE_WITH_TIME_LENGTH:
            date_format += "(%H:%M:%S)"
        start_date_as_datetime = datetime.strptime(
            self.start_date, date_format)
        date_as_datetime = start_date_as_datetime + \
            timedelta(days=converted_date)
    else:
        start_date_format = self.__date_format_string
        if len(self.start_date) == self.DATE_WITH_TIME_LENGTH:
            start_date_format += "(%H:%M:%S)"
        end_date_format = self.__date_format_string
        if len(converted_date) == self.DATE_WITH_TIME_LENGTH:
            end_date_format += "(%H:%M:%S)"
        date_as_datetime = datetime.strptime(converted_date, end_date_format)
        start_date_as_datetime = datetime.strptime(
            self.start_date, start_date_format)

    difference = date_as_datetime - start_date_as_datetime
    return difference.total_seconds() / timedelta(days=1).total_seconds()
