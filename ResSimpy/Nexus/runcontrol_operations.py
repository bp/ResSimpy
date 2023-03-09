from datetime import datetime, timedelta
from functools import cmp_to_key
from typing import Union, Final, Optional
import ResSimpy.Nexus.nexus_file_operations as nfo


class Runcontrol:
    def __init__(self, use_american_date_format: bool = False, start_date: str = '',
                 date_format_string: str = '', date_with_time_length: Final[int] = 20):
        self.use_american_date_format: bool = use_american_date_format
        self.date_format_string: str = date_format_string
        self.DATE_WITH_TIME_LENGTH: Final[int] = date_with_time_length
        self.start_date: str = start_date

    @staticmethod
    def get_times(times_file: list[str]) -> list[str]:
        """Retrieves a list of TIMES from the supplied Runcontrol / Include file

        Args:
            times_file (list[str]): list of strings with each line from the file a new entry in the list

        Returns:
            list[str]: list of all the values following the TIME keyword in supplied file, \
                empty list if no values found
        """
        times = []
        for line in times_file:
            if nfo.check_token('TIME', line):
                value = nfo.get_token_value('TIME', line, times_file)
                if value is not None:
                    times.append(value)

        return times

    @staticmethod
    def delete_times(file_content: list[str]) -> list[str]:
        """ Deletes times from file contents
        Args:
            file_content (list[str]):  list of strings with each line from the file a new entry in the list

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
    def remove_times_from_file(file_content: list[str], output_file_path: str):
        """Removes the times from a file - used for replacing with new times
        Args:
            file_content (list[str]): a list of strings containing each line of the file as a new entry
            output_file_path (str): path to the file to output to
        """
        new_file_content = Runcontrol.delete_times(file_content)

        new_file_str = "".join(new_file_content)

        with open(output_file_path, "w") as text_file:
            text_file.write(new_file_str)

    def convert_date_to_number(self, date: Union[str, int, float]) -> float:
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
                raise ValueError("convert_date_to_number: Incorrect type for 'date' parameter")
            converted_date = date

        if isinstance(converted_date, float):
            date_format = self.date_format_string
            if len(self.start_date) == self.DATE_WITH_TIME_LENGTH:
                date_format += "(%H:%M:%S)"
            start_date_as_datetime = datetime.strptime(self.start_date, date_format)
            date_as_datetime = start_date_as_datetime + timedelta(days=converted_date)
        else:
            start_date_format = self.date_format_string
            if len(self.start_date) == self.DATE_WITH_TIME_LENGTH:
                start_date_format += "(%H:%M:%S)"
            end_date_format = self.date_format_string
            if len(converted_date) == self.DATE_WITH_TIME_LENGTH:
                end_date_format += "(%H:%M:%S)"
            date_as_datetime = datetime.strptime(converted_date, end_date_format)
            start_date_as_datetime = datetime.strptime(self.start_date, start_date_format)

        difference = date_as_datetime - start_date_as_datetime
        return difference.total_seconds() / timedelta(days=1).total_seconds()

    def compare_dates(self, x: Union[str, float], y: Union[str, float]) -> int:
        """Comparator for two supplied dates or numbers

        Args:
            x (Union[str, float]): first date to compare
            y (Union[str, float]): second date to compare

        Returns:
            int: the difference between the first and second dates to compare
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
        """ Removes duplicates and nans from the times list, then sorts them

        Args:
            times (list[str]): list of times to remove duplicates from

        Returns:
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

    def check_date_format(self, date: Union[str, float]) -> None:
        """Checks that a supplied date is in the correct format

        Args:
            date (Union[str, float]): date to check the format of
        Raises:
            ValueError: If a date provided isn't in a date format that the model expects
        """
        try:
            float(date)
        except ValueError:
            # Value isn't a float - attempt to extract date from value
            try:
                date_format = self.date_format_string
                if len(str(date)) == self.DATE_WITH_TIME_LENGTH:
                    date_format += "(%H:%M:%S)"
                datetime.strptime(str(date), date_format)
            except Exception:
                current_date_format = self.get_date_format(self.use_american_date_format)
                raise ValueError(
                    "Invalid date format " + str(date) + " the model is using " + current_date_format + " date format.")

    @staticmethod
    def get_date_format(use_american_date_format) -> str:
        """Returns the date format being used by the model
        formats used: ('MM/DD/YYYY', 'DD/MM/YYYY')
        """

        if use_american_date_format:
            return 'MM/DD/YYYY'
        else:
            return 'DD/MM/YYYY'

    def __update_times_in_file(self) -> None:
        """Updates the list of times in the Runcontrol file to the current stored values in __times

        Returns:
            None: writes out a file at the same path as the existing runcontrol file
        """
        self.__check_output_path()
        if self.fcs_file.runcontrol_file is None or self.fcs_file.runcontrol_file.location is None:
            raise ValueError(f"No file path found for {self.fcs_file}")
        file_content = self.fcs_file.runcontrol_file.get_flat_list_str_file()
        filename = self.fcs_file.runcontrol_file.location

        new_file_content = self.Runcontrol.delete_times(file_content)

        time_list = self.__times if self.__times is not None else []
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
