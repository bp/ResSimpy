from datetime import datetime
import os
import copy
from functools import cmp_to_key
from datetime import timedelta
from typing import Union, Optional

from ResSimpy.Nexus.DataModels.StructuredGridFile import StructuredGridFile, PropertyToLoad
import ResSimpy.Nexus.nexus_file_operations as nexus_file_operations
import resqpy.model as rq

from ResSimpy.Simulator import Simulator


class NexusSimulator(Simulator):
    # Constants
    DATE_WITH_TIME_LENGTH = 20

    def __init__(self, origin: Optional[str] = None, destination: Optional[str] = None, force_output: bool = False,
                 root_name: Optional[str] = None, nexus_data_name: str = "data", write_times: bool = True,
                 manual_fcs_tidy_call: bool = False) -> None:

        if origin is None:
            raise ValueError("FCS File Path is required")

        super().__init__()

        self.run_control_file: Optional[str] = ''
        self.__times: Optional[list[str]] = None
        self.__destination: Optional[str] = None
        self.use_american_date_format: bool = False
        self.__job_id: int = -1  # maybe a float?
        self.__date_format_string: str = ''
        self.__original_fcs_file_path: str = origin.strip()
        self.__new_fcs_file_path: str = origin.strip()
        self.__force_output: bool = force_output
        self.__origin: str = origin.strip()  # this is the fcs file path
        self.__root_name: str = root_name if root_name is not None else self.get_rootname()
        self.__nexus_data_name: str = nexus_data_name
        self.__structured_grid_file_path: Optional[str] = None
        self.__structured_grid_file: Optional[StructuredGridFile] = None
        self.__simulation_start_time: Optional[str] = None  # run execution start time from the log file
        self.__simulation_end_time: Optional[str] = None  # run execution finish time from the log file
        self.__previous_run_time: Optional[str] = None  # run execution finish time from the log file
        self.__run_units: Optional[str] = None
        self.use_american_run_units: bool = False
        self.use_american_input_units: bool = False
        self.__write_times: bool = write_times
        self.__manual_fcs_tidy_call: bool = manual_fcs_tidy_call
        self.__surface_file_path: Optional[str] = None

        if destination is not None and destination != '':
            self.set_output_path(path=destination.strip())

        # Check the status of any existing or completed runs related to this model
        self.get_simulation_status(from_startup=True)

        self.__load_fcs_file()

    def remove_temp_from_properties(self):
        """Updates model values if the files are moved from a temp directory
        Replaces the first instance of temp/ in the file paths in the nexus simulation file paths
        Raises:
            ValueError: if any of [__structured_grid_file_path, __new_fcs_file_path, __surface_file_path] are None
        """
        if self.__structured_grid_file_path is None:
            raise ValueError("No __structured_grid_file_path found, can't remove temporary properties from file path")
        if self.__new_fcs_file_path is None:
            raise ValueError("No __new_fcs_file_path found, can't remove temporary properties from file path")
        if self.__surface_file_path is None:
            raise ValueError("No __surface_file_path found, can't remove temporary properties from file path")

        self.__origin = self.__origin.replace('temp/', '', 1)
        self.__root_name = self.__root_name.replace('temp/', '', 1)
        self.__structured_grid_file_path = self.__structured_grid_file_path.replace('temp/', '', 1)
        self.__new_fcs_file_path = self.__new_fcs_file_path.replace('temp/', '', 1)
        self.__surface_file_path = self.__surface_file_path.replace('temp/', '', 1)

    def get_model_location(self):
        """Returns the location of the model"""
        return os.path.dirname(self.__origin)

    def get_structured_grid_path(self):
        """Returns the location of the structured grid file"""
        return self.__structured_grid_file_path

    def get_new_fcs_name(self):
        """Returns the new name for the FCS file without the fcs extension"""
        return self.__root_name

    @staticmethod
    def get_check_run_input_units_for_models(models: list[str]) -> tuple[Optional[bool], Optional[bool]]:
        # TODO: add LAB units
        """Returns the run and input unit formats for all the supplied models.
        Supported model formats:
            RESQML type epc files ending in ".epc"
            Nexus files containing a line identifying the "RUN_UNITS" or "DEFAULT_UNITS"
        Supported units: ENGLISH, METRIC
        Args:
            models (list[str]): list of paths to supported reservoir models
        Raises:
            ValueError: if a model in the list is using inconcistent run/default units
        Returns:
            Tuple[Optional[Bool], Optional[Bool]]: If all units are consistent between models, 
                Returns (True, True) if 'ft' is the length unit in an epc or Nexus specifies "ENGLISH" as the \
                (RUN_UNITS,DEFAULT_UNITS) respectively and False, False otherwise. \
                Returns (None, None) if it can't find a (RUN_UNITS, DEFAULT_UNITS) in the supplied files\
        """
        american_run_units: Optional[bool] = None
        american_input_units: Optional[bool] = None

        for model in models:
            # If we're checking the units of a RESQML model, read it in and get the units. Otherwise, read the units
            # from the fcs file
            if os.path.splitext(model)[1] == '.epc':
                resqpy_model = rq.Model(epc_file=model)

                # Load in the RESQML grid
                grid = resqpy_model.grid()

                # Check the grid units
                grid_length_unit = grid.xy_units()
                american_input_units = grid_length_unit == 'ft'
                american_run_units = grid_length_unit == 'ft'
            else:
                fcs_file = nexus_file_operations.load_file_as_list(model)

                for line in fcs_file:
                    if 'RUN_UNITS' in line:
                        value = nexus_file_operations.get_token_value('RUN_UNITS', line, fcs_file)
                        if value is not None:
                            model_american_run_units = value == 'ENGLISH'
                            if american_run_units is None:
                                american_run_units = model_american_run_units
                            elif model_american_run_units != american_run_units:
                                raise ValueError(f"Model at {model} using inconsistent run units")
                    elif 'DEFAULT_UNITS' in line:
                        value = nexus_file_operations.get_token_value('DEFAULT_UNITS', line, fcs_file)
                        if value is not None:
                            model_american_input_units = value == 'ENGLISH'
                            if american_input_units is None:
                                american_input_units = model_american_input_units
                            elif american_run_units != american_input_units:
                                raise ValueError(f"Model at {model} using inconsistent default units")

        return american_run_units, american_input_units

    @staticmethod
    def get_check_oil_gas_types_for_models(models: list[str]) -> Optional[str]:
        """Checks for fluid types within a list of paths to models.
        Currently limited to checking for the first SURFACE network in a file
        Args:
            models (list[str]): a list of paths to models to check for fluid types

        Raises:
            ValueError: If fluid types are inconsistent between models

        Returns:
            Optional[str]: The fluid type used for the model for the first surface network
        """
        fluid_type = None
        for model in models:
            model_fluid_type = None
            fcs_file = nexus_file_operations.load_file_as_list(model)
            surface_filename = None

            for line in fcs_file:
                if "SURFACE Network 1" in line:
                    surface_filename = nexus_file_operations.get_token_value(token="SURFACE Network 1", token_line=line,
                                                                             file_list=fcs_file)
                    break

            if surface_filename is not None:
                surface_filename = surface_filename if os.path.isabs(surface_filename) else \
                    os.path.dirname(model) + "/" + surface_filename
                model_fluid_type = NexusSimulator.get_fluid_type(surface_file_name=surface_filename)

            if fluid_type is None:
                fluid_type = model_fluid_type
            elif fluid_type != model_fluid_type:
                raise ValueError(f"Inconsistent Oil / Gas types: {model_fluid_type} found for {model}")

        return fluid_type

    @staticmethod
    def get_eos_details(surface_file: list[str]) -> str:
        """Gets all the information about an EOS from a Nexus model

        Args:
            surface_file (list[str]): path to the surface file in a Nexus model

        Returns:
            str: a concatenated string of EOS components
        """
        eos_string: str = ''
        eos_found: bool = False
        for line in surface_file:
            if "EOS" in line:
                eos_string += line
                eos_found = True
            elif eos_found:
                eos_string += line
            if "COMPONENTS" in line:
                break

        return eos_string

    @staticmethod
    def get_fluid_type(surface_file_name: str) -> str:
        """gets the fluid type for a single model from a surface file

        Args:
            surface_file_name (str): path to the surface file in a Nexus model

        Raises:
            ValueError: if no fluid type is found within the provided file path

        Returns:
            str: fluid type as one of [BLACKOIL, WATEROIL, GASWATER,] or the full details from an EOS model
        """
        surface_file = nexus_file_operations.load_file_as_list(surface_file_name)
        fluid_type = None

        for line in surface_file:
            if "BLACKOIL" in line:
                fluid_type = "BLACKOIL"
                break
            elif "WATEROIL" in line:
                fluid_type = "WATEROIL"
                break
            elif "GASWATER" in line:
                fluid_type = "GASWATER"
                break
            elif "EOS" in line:
                fluid_type = NexusSimulator.get_eos_details(surface_file)

        if fluid_type is None:
            raise ValueError("No Oil / Gas type detected")

        return fluid_type

    def get_model_oil_type(self) -> str:
        """Returns the get_fluid_type method on the existing NexusSimulator instance

        Raises:
            ValueError: If no file path is provided for the surface file path

        Returns:
            str: fluid type as one of [BLACKOIL, WATEROIL, GASWATER,] or the full details from an EOS model
        """
        if self.__surface_file_path is None:
            raise ValueError("No value provided for the __surface_file_path")
        return NexusSimulator.get_fluid_type(self.__surface_file_path)

    def get_rootname(self) -> str:
        """ Returns the name of the fcs file without the .fcs extension
        Returns:
            str: string of the fcs file without the .fcs extension
        """
        rootname = os.path.basename(self.__origin)
        rootname = rootname.split(".fcs")[0]
        return rootname

    def __check_output_path(self) -> None:
        """ Confirms that the output path has been set (used to stop accidental writing operations in the original
        directory)
        Raises:
            ValueError: if the destination provided is set to None
        """
        if self.__destination is None:
            raise ValueError("Destination is required for this operation. Currently set to: ", self.__destination)

    def set_output_path(self, path: str) -> None:
        """ Initialises the output to the declared output location. \
            If the file is a different directory to the origin path location the function will set the origin \
            to the new destination.
        """
        self.__destination = path
        if self.__destination is not None and os.path.dirname(self.__origin) != os.path.dirname(self.__destination):
            # if self.__manual_fcs_tidy_call:
            #     self.call_fcstidy(fcs_files=[self.__origin], output_dir=self.__destination, options='--pathkeep 0')
            # else:
            #     self.__output_to_new_directory()

            self.__origin = self.__destination + "/" + os.path.basename(self.__original_fcs_file_path)

    def __load_fcs_file(self):
        """ Loads in the information from the supplied FCS file into the class instance.
            Loads in the paths for runcontrol, strucutured grid and the first surface network.
            Loads in the values for dateformat and run units.
            Attempts to load the run_control_file.
        """
        # self.get_simulation_status(True)

        fcs_file = nexus_file_operations.load_file_as_list(self.__new_fcs_file_path)

        for line in fcs_file:
            uppercase_line = line.upper()
            if 'RUNCONTROL' in uppercase_line:
                runcontrol_path = nexus_file_operations.get_token_value('RUNCONTROL', line, fcs_file)
                if runcontrol_path is not None:
                    self.run_control_file = runcontrol_path if os.path.isabs(runcontrol_path) else \
                        os.path.dirname(self.__origin) + "/" + runcontrol_path
            elif 'DATEFORMAT' in uppercase_line:
                value = nexus_file_operations.get_token_value('DATEFORMAT', line, fcs_file)
                if value is not None:
                    self.use_american_date_format = value == 'MM/DD/YYYY'
                self.__date_format_string = "%m/%d/%Y" if self.use_american_date_format else "%d/%m/%Y"
            elif 'STRUCTURED_GRID' in uppercase_line:
                value = nexus_file_operations.get_token_value('STRUCTURED_GRID', line, fcs_file)
                if value is not None:
                    self.__structured_grid_file_path = value if os.path.isabs(value) else \
                        os.path.dirname(self.__origin) + "/" + value
                    self.load_structured_grid_file()
            elif 'RUN_UNITS' in uppercase_line:
                value = nexus_file_operations.get_token_value('RUN_UNITS', line, fcs_file)
                if value is not None:
                    self.__run_units = value
                    self.use_american_run_units = value == 'ENGLISH'
            elif 'DEFAULT_UNITS' in uppercase_line:
                value = nexus_file_operations.get_token_value('DEFAULT_UNITS', line, fcs_file)
                if value is not None:
                    self.__run_units = value
                    self.use_american_input_units = value == 'ENGLISH'
            elif "SURFACE NETWORK 1" in uppercase_line:
                value = nexus_file_operations.get_token_value(token="SURFACE Network 1", token_line=line,
                                                              file_list=fcs_file)
                if value is not None:
                    self.__surface_file_path = value if os.path.isabs(value) else \
                        os.path.dirname(self.__origin) + "/" + value
                break

        if self.run_control_file != '':
            self.__load_run_control_file()

    @staticmethod
    def update_file_value(file_path: str, token: str, new_value: str, add_to_start: bool = False):
        """Updates a value in a file if it is present and in the format {TOKEN} {VALUE}. If the token
        isn't present, it will add the token + value to either the start or end of the file

        Args:
            file_path (str): path to a file to update the token/value pair in
            token (str): Keyword token to find in the given file (e.g. KX)
            new_value (str): Value following the TOKEN to be replaced
            add_to_start (bool, optional): Inserts the token/value pair to the start of the file. Defaults to False.

        Raises:
            ValueError: If no value is found after the token
        """

        file = nexus_file_operations.load_file_as_list(file_path)

        line_counter = 0
        token_found = False
        for line in file:
            modified_line = line.lower().replace('/t', ' ')
            modified_line = ' '.join(modified_line.split())
            if token.lower() in modified_line:
                # We've found the token, now replace the value
                token_location = modified_line.find(token.lower())
                line_before_token_value = line[0: token_location]
                line_after_token = line[token_location:]
                current_value = nexus_file_operations.get_next_value(0, [line], line_after_token[len(token) + 1:])
                if current_value is None:
                    raise ValueError(f"No value found after the supplied {token=}, \
                        please check the following line for that token: {line}")
                new_line_after = line_after_token.replace(current_value, new_value, 1)
                file[line_counter] = line_before_token_value + new_line_after
                token_found = True
                break
            line_counter += 1

        if token_found is False:
            token_line = f"{token} {new_value}"
            if add_to_start:
                file.insert(0, token_line + '\n')
            else:
                file.append('\n' + token_line)

        new_file_str = "".join(file)

        with open(file_path, "w") as text_file:
            text_file.write(new_file_str)

    def update_fcs_file_value(self, token, new_value, add_to_start=False):
        """Updates a value in the FCS file"""
        self.update_file_value(self.__new_fcs_file_path, token=token, new_value=new_value, add_to_start=add_to_start)

    @staticmethod
    def comment_out_file_value(token: str, file_path: str) -> None:
        """Comments out an uncommented line containing the specified token

        Args:
            token (str): Keyword token to find in the given file (e.g. KX)
            file_path (str): path to a file containing the token
        """
        file = nexus_file_operations.load_file_as_list(file_path)

        line_counter = 0
        for line in file:
            modified_line = line.lower().replace('/t', ' ')
            modified_line = ' '.join(modified_line.split())
            # If we've found the token, and it isn't already commented, comment it out
            if token.lower() in modified_line and \
                    (modified_line.find(token.lower()) < modified_line.find("!") or modified_line.find("!") == -1):
                file[line_counter] = f"! {file[line_counter]}"
                break
            line_counter += 1

        new_file_str = "".join(file)

        with open(file_path, "w") as text_file:
            text_file.write(new_file_str)

    def get_date_format(self) -> str:
        """Returns the date format being used by the model
        formats used: ('MM/DD/YYYY', 'DD/MM/YYYY')
        """

        if self.use_american_date_format:
            return 'MM/DD/YYYY'
        else:
            return 'DD/MM/YYYY'

    def __load_run_control_file(self):
        """Loads the run control information into the class instance. \
            If the write_times attribute is True then it expands out any INCLUDE files with the times found within
        Raises:
            ValueError: if the run_control_file attribute is None
        """
        if self.run_control_file is None:
            raise ValueError(f"No file path provided for {self.run_control_file=}")
        run_control_file = nexus_file_operations.load_file_as_list(self.run_control_file)
        include_file_path = ''

        for line in run_control_file:
            if nexus_file_operations.check_token('START', line):
                value = nexus_file_operations.get_token_value('START', line, run_control_file)
                if value is not None:
                    self.start_date_set(value)
            elif 'INCLUDE' in line:
                value = nexus_file_operations.get_token_value('INCLUDE', line, run_control_file)
                if value is not None:
                    include_file_path = value

        times = []
        run_control_times = nexus_file_operations.get_times(run_control_file)
        times.extend(run_control_times)

        # If we don't want to write the times, return here.
        if not self.__write_times:
            return

        if include_file_path != '':
            full_file_path = include_file_path if os.path.isabs(include_file_path) else os.path.dirname(
                self.run_control_file) + "/" + include_file_path

            include_file = nexus_file_operations.load_file_as_list(full_file_path)
            include_times = nexus_file_operations.get_times(include_file)
            times.extend(include_times)
            if self.__destination is not None:
                self.__remove_times_from_file(include_file, full_file_path)

        self.__modify_times(content=times, operation='replace')

    def __remove_times_from_file(self, file_content: list[str], output_file_path: str):
        """Removes the times from a file - used for replacing with new times
        Args:
            file_content (list[str]): a list of strings containing each line of the file as a new entry
            output_file_path (str): path to the file of 
        """
        self.__check_output_path()
        new_file_content = nexus_file_operations.delete_times(file_content)

        new_file_str = "".join(new_file_content)

        with open(output_file_path, "w") as text_file:
            text_file.write(new_file_str)

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
                raise ValueError("__convert_date_to_number: Incorrect type for 'date' parameter")
            converted_date = date

        if isinstance(converted_date, float):
            date_format = self.__date_format_string
            if len(self.start_date) == self.DATE_WITH_TIME_LENGTH:
                date_format += "(%H:%M:%S)"
            start_date_as_datetime = datetime.strptime(self.start_date, date_format)
            date_as_datetime = start_date_as_datetime + timedelta(days=converted_date)
        else:
            start_date_format = self.__date_format_string
            if len(self.start_date) == self.DATE_WITH_TIME_LENGTH:
                start_date_format += "(%H:%M:%S)"
            end_date_format = self.__date_format_string
            if len(converted_date) == self.DATE_WITH_TIME_LENGTH:
                end_date_format += "(%H:%M:%S)"
            date_as_datetime = datetime.strptime(converted_date, end_date_format)
            start_date_as_datetime = datetime.strptime(self.start_date, start_date_format)

        difference = date_as_datetime - start_date_as_datetime
        return difference.total_seconds() / timedelta(days=1).total_seconds()

    def __compare_dates(self, x: Union[str, float], y: Union[str, float]) -> float:
        """Comparator for two supplied dates or numbers

        Args:
            x (Union[str, float]): first date to compare
            y (Union[str, float]): second date to compare

        Returns:
            float: the difference between the first and second dates to compare
        """
        return self.__convert_date_to_number(x) - self.__convert_date_to_number(y)

    def __sort_remove_duplicate_times(self, times: list[str]) -> list[str]:
        """ Removes duplicates and nans from the times list, then sorts them """
        new_times = []
        for i in times:
            i_value = i.strip()
            if i != i or i_value in new_times:
                continue
            new_times.append(i_value)
        new_times = sorted(new_times, key=cmp_to_key(self.__compare_dates))
        return new_times

    def __check_date_format(self, date: Union[str, float]) -> None:
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
                date_format = self.__date_format_string
                if len(str(date)) == self.DATE_WITH_TIME_LENGTH:
                    date_format += "(%H:%M:%S)"
                datetime.strptime(str(date), date_format)
            except Exception:
                current_date_format = self.get_date_format()
                raise ValueError(
                    "Invalid date format " + str(date) + " the model is using " + current_date_format + " date format.")

    def modify(self, operation, section, keyword, content):
        """
        Generic modify method to modify part of the input deck
        args:
            operation
            section
            keyword
            content
        """
        section = section.upper()
        keyword = keyword.upper()
        operation = operation.lower()

        if section == "RUNCONTROL":
            if keyword == "TIME":
                self.__modify_times(content=content, operation=operation)
            else:
                raise NotImplementedError(keyword, "not yet implemented")
        else:
            raise NotImplementedError(section, "not yet implemented")

    def get_content(self, section, keyword):
        """ Returns the requested input information """
        section = section.upper()
        keyword = keyword.upper()
        if section == "RUNCONTROL":
            if keyword == "TIME":
                return self.__times
            else:
                raise NotImplementedError(keyword, "not yet implemented")
        else:
            raise NotImplementedError(section, "not yet implemented")

    def __modify_times(self, content=None, operation='merge'):
        """ Modifies the output times in the simulation """
        if content is None:
            content = []
        for time in content:
            self.__check_date_format(time)

        new_times = self.__sort_remove_duplicate_times(times=content)
        if len(new_times) > 0 > self.__compare_dates(new_times[0], self.start_date):
            raise ValueError(f"The supplied date of {new_times[0]} precedes the start date of {self.start_date}")

        if operation.lower() == 'merge':
            self.__times.extend(content)
        elif operation.lower() == 'replace':
            self.__times = content
        elif operation.lower() == 'reset':
            self.__times = []
        elif operation.lower() == 'remove':
            for time in content:
                if time in self.__times:
                    self.__times.remove(time)

        self.__times = self.__sort_remove_duplicate_times(self.__times)

        if self.__destination is not None:
            self.__update_times_in_file()

    def __update_times_in_file(self):
        """ Updates the list of times in the Runcontrol file """
        self.__check_output_path()

        file_content = nexus_file_operations.load_file_as_list(self.run_control_file)

        new_file_content = nexus_file_operations.delete_times(file_content)

        time_list = self.__times
        stop_string = 'STOP\n'
        if stop_string in new_file_content:
            new_file_content.remove(stop_string)

        def prepend_time(s):
            return "TIME " + s

        time_list = [prepend_time(x) for x in time_list]
        num_times = len(time_list)

        new_line_list = ["\n\n"] * num_times
        zipped_list = list(zip(time_list, new_line_list))
        flat_list = [item for sublist in zipped_list for item in sublist]
        flat_list.append(stop_string)
        new_file_content.extend(flat_list)
        new_file_str = "".join(new_file_content)

        filename = self.run_control_file
        with open(filename, "w") as text_file:
            text_file.write(new_file_str)

    def change_force_output(self, force_output=True):
        """ Sets the force output parameter to the supplied value """
        self.__force_output = force_output

    def __get_log_path(self, from_startup=False):
        """ Returns the path of the log file for the simulation """
        folder_path = os.path.dirname(self.__original_fcs_file_path) if from_startup else os.path.dirname(self.__origin)
        files = os.listdir(folder_path)
        original_fcs_file_location = os.path.basename(self.__original_fcs_file_path)
        log_file_name = os.path.splitext(original_fcs_file_location)[
                            0] + ".log" if from_startup else self.__root_name + ".log"

        if log_file_name in files:
            if from_startup:
                file_location = folder_path
            else:
                file_location = self.__destination if self.__destination is not None else folder_path

            log_file_path = file_location + "/" + log_file_name
            return log_file_path
        else:
            return None

    def __update_simulation_start_and_end_times(self, log_file_line_list):
        """Updates the stored simulation start and end times"""
        for line in log_file_line_list:
            if 'start generic pdsh   prolog' in line:
                value = nexus_file_operations.get_simulation_time(line)
                self.__simulation_start_time = value

            if 'end generic pdsh   epilog' in line:
                value = nexus_file_operations.get_simulation_time(line)
                self.__simulation_end_time = value

    def __get_start_end_difference(self):
        """Returns a string with the previous time taken when the base case was run"""
        if self.__simulation_start_time is None or self.__simulation_end_time is None:
            return None

        start_date = nexus_file_operations.convert_server_date(self.__simulation_start_time)
        end_date = nexus_file_operations.convert_server_date(self.__simulation_end_time)

        total_difference = (end_date - start_date)
        days = int(total_difference.days)
        hours = int((total_difference.seconds / (60 * 60)))
        minutes = int((total_difference.seconds / 60) - (hours * 60))
        seconds = int(total_difference.seconds - (hours * 60 * 60) - (minutes * 60))

        return f"{days} Days, {hours} Hours, {minutes} Minutes {seconds} Seconds"

    def get_simulation_status(self, from_startup=False):
        """ Gets the status of the latest simulation run """

        log_file = self.__get_log_path(from_startup)
        if log_file is None:
            if from_startup:
                return ''
            raise NotImplementedError("Only retrieving status from a log file is supported at the moment")
        else:
            log_file_line_list = nexus_file_operations.load_file_as_list(log_file)
            self.__update_simulation_start_and_end_times(log_file_line_list)
            job_finished = 'Nexus finished\n' in log_file_line_list
            if job_finished:
                self.__previous_run_time = self.__get_start_end_difference() if from_startup \
                    else self.__previous_run_time
                return nexus_file_operations.get_errors_warnings_string(log_file_line_list=log_file_line_list)
            else:
                job_number_line = [x for x in log_file_line_list if 'Job number:' in x]
                if len(job_number_line) > 0:
                    self.__job_id = int(job_number_line[0].split(":")[1])
                    return f"Job Running, ID: {self.__job_id}"  # self.__get_job_status()

    def load_structured_grid_file(self):
        """Loads in a structured grid file"""
        file_as_list = nexus_file_operations.load_file_as_list(self.__structured_grid_file_path)
        structured_grid_file = StructuredGridFile()
        for line in file_as_list:
            # Load in the basic properties
            properties_to_load = [
                PropertyToLoad('NETGRS', ['VALUE', 'CON'], structured_grid_file.netgrs),
                PropertyToLoad('POROSITY', ['VALUE', 'CON'], structured_grid_file.porosity),
                PropertyToLoad('SW', ['VALUE', 'CON'], structured_grid_file.sw),
                PropertyToLoad('KX', ['VALUE', 'MULT', 'CON'], structured_grid_file.kx),
                PropertyToLoad('PERMX', ['VALUE', 'MULT', 'CON'], structured_grid_file.kx),
                PropertyToLoad('PERMI', ['VALUE', 'MULT', 'CON'], structured_grid_file.kx),
                PropertyToLoad('KI', ['VALUE', 'MULT', 'CON'], structured_grid_file.kx),
                PropertyToLoad('KY', ['VALUE', 'MULT', 'CON'], structured_grid_file.ky),
                PropertyToLoad('PERMY', ['VALUE', 'MULT', 'CON'], structured_grid_file.ky),
                PropertyToLoad('PERMJ', ['VALUE', 'MULT', 'CON'], structured_grid_file.ky),
                PropertyToLoad('KJ', ['VALUE', 'MULT', 'CON'], structured_grid_file.ky),
                PropertyToLoad('KZ', ['VALUE', 'MULT', 'CON'], structured_grid_file.kz),
                PropertyToLoad('PERMZ', ['VALUE', 'MULT', 'CON'], structured_grid_file.kz),
                PropertyToLoad('PERMK', ['VALUE', 'MULT', 'CON'], structured_grid_file.kz),
                PropertyToLoad('KK', ['VALUE', 'MULT', 'CON'], structured_grid_file.kz),
            ]

            for token_property in properties_to_load:
                for modifier in token_property.modifiers:
                    nexus_file_operations.load_token_value_if_present(token_property.token, modifier,
                                                                      token_property.property, line,
                                                                      file_as_list, ['INCLUDE'])

            # Load in grid dimensions
            if 'NX' in line:
                # Check that the format of the grid is NX followed by NY followed by NZ
                current_line = file_as_list[file_as_list.index(line)]
                remaining_line = current_line[current_line.index('NX') + 2:]
                if nexus_file_operations.get_next_value(0, [remaining_line], remaining_line) != 'NY':
                    continue
                remaining_line = remaining_line[remaining_line.index('NY') + 2:]
                if nexus_file_operations.get_next_value(0, [remaining_line], remaining_line) != 'NZ':
                    continue

                # Avoid loading in a comment
                if "!" in line and line.index("!") < line.index('NX'):
                    continue
                next_line = file_as_list[file_as_list.index(line) + 1]
                first_value = nexus_file_operations.get_next_value(0, [next_line], next_line)
                next_line = next_line.replace(first_value, "", 1)
                second_value = nexus_file_operations.get_next_value(0, [next_line], next_line)
                next_line = next_line.replace(second_value, "", 1)
                third_value = nexus_file_operations.get_next_value(0, [next_line], next_line)

                structured_grid_file.range_x = int(first_value)
                structured_grid_file.range_y = int(second_value)
                structured_grid_file.range_z = int(third_value)

        self.__structured_grid_file = structured_grid_file

    def get_structured_grid(self):
        """Pass the structured grid information to the front end"""
        return self.__structured_grid_file

    def get_structured_grid_dict(self):
        """Convert the structured grid info to a dictionary and pass it to the front end"""
        return self.__structured_grid_file.__dict__

    def get_simulation_start_time(self):
        """Get the start time of a simulation run"""
        self.get_simulation_status()
        if self.__simulation_start_time is not None:
            return self.__simulation_start_time
        else:
            return '-'

    def get_simulation_end_time(self):
        """Get the end time of a simulation run if it has completed"""
        self.get_simulation_status()
        if self.__simulation_end_time is not None:
            return self.__simulation_end_time
        else:
            return '-'

    def get_job_id(self):
        """Get the job Id of a simulation run"""
        return self.__job_id

    def update_structured_grid_file(self, grid_dict):
        """Save values passed from the front end to the structured grid file and update the class"""
        # Convert the dictionary back to a class, and update the properties on our class
        original_structured_grid_file = copy.deepcopy(self.__structured_grid_file)
        self.__structured_grid_file = StructuredGridFile(grid_dict)

        # Get the existing file as a list
        file = nexus_file_operations.load_file_as_list(self.__structured_grid_file_path)

        # Update each value in the file
        nexus_file_operations.replace_value(file, original_structured_grid_file.netgrs,
                                            self.__structured_grid_file.netgrs, 'NETGRS')
        nexus_file_operations.replace_value(file, original_structured_grid_file.porosity,
                                            self.__structured_grid_file.porosity,
                                            'POROSITY')
        nexus_file_operations.replace_value(file, original_structured_grid_file.sw, self.__structured_grid_file.sw,
                                            'SW')
        nexus_file_operations.replace_value(file, original_structured_grid_file.kx, self.__structured_grid_file.kx,
                                            'KX')
        nexus_file_operations.replace_value(file, original_structured_grid_file.ky, self.__structured_grid_file.ky,
                                            'KY')
        nexus_file_operations.replace_value(file, original_structured_grid_file.kz, self.__structured_grid_file.kz,
                                            'KZ')

        # Save the new file contents
        new_file_str = "".join(file)
        with open(self.__structured_grid_file_path, "w") as text_file:
            text_file.write(new_file_str)

    @staticmethod
    def get_grid_file_as_3d_list(path):
        """Converts a grid file to a 3D list"""
        try:
            with open(path) as f:
                grid_file_list = list(f)
        except FileNotFoundError:
            return None

        sub_lists = []

        new_list_str = ""
        for sub_list in grid_file_list[4:]:
            if sub_list == '\n':
                new_list_split = [x.split("\t") for x in new_list_str.split("\n")]
                new_list_split_cleaned = []
                for x_list in new_list_split:
                    new_list_split = [float(x) for x in x_list if x != ""]
                    new_list_split_cleaned.append(new_list_split)
                sub_lists.append(new_list_split_cleaned)
                new_list_str = ""
            else:
                new_list_str = new_list_str + sub_list
        return sub_lists

    def view_command(self, field, previous_lines=3, following_lines=3):
        """Displays how the property is declared in the structured grid file"""
        structured_grid_dict = self.get_structured_grid_dict()
        command_token = f"{field.upper()} {structured_grid_dict[field.lower()].modifier}"
        file_as_list = nexus_file_operations.load_file_as_list(self.__structured_grid_file_path)

        for line in file_as_list:
            if command_token in line and ('!' not in line or line.index(command_token) < line.index('!')):
                start_index = file_as_list.index(line) - previous_lines \
                    if file_as_list.index(line) - previous_lines > 0 else 0
                end_index = file_as_list.index(line) + following_lines \
                    if file_as_list.index(line) + following_lines < len(file_as_list) else len(file_as_list) - 1

                new_array = file_as_list[start_index: end_index]
                new_array = [x.strip("'") for x in new_array]
                value = "".join(new_array)
                return value

    def get_abs_structured_grid_path(self, filename):
        """Returns the absolute path to the Structured Grid file"""
        return os.path.dirname(self.__structured_grid_file_path) + '/' + filename

    def get_surface_file_path(self):
        return self.__surface_file_path

    def get_base_case_run_time(self):
        """Get the time taken for the base case to run"""
        if self.__previous_run_time is not None:
            return self.__previous_run_time
        else:
            return '-'

    def get_simulation_progress(self):
        """Returns the simulation progress"""
        log_file_path = self.__get_log_path()
        if log_file_path is not None:
            log_file = nexus_file_operations.load_file_as_list(log_file_path)

            read_in_times = False
            time_heading_location = None
            last_time = None
            for line in log_file:
                case_name_string = f"Case Name = {self.__root_name}"
                if case_name_string in line:
                    read_in_times = True
                    continue
                if read_in_times and 'TIME' in line:
                    heading_location = 0
                    line_string = line
                    while len(line_string) > 0:
                        next_value = nexus_file_operations.get_next_value(0, [line_string], line_string)
                        if next_value is None:
                            break

                        line_string = line_string.replace(next_value, '', 1)
                        if next_value == 'TIME':
                            time_heading_location = heading_location
                        heading_location += 1

                if read_in_times and time_heading_location is not None:
                    line_string = line
                    next_value = nexus_file_operations.get_next_value(0, [line_string], line_string)
                    if next_value is not None and next_value.replace('.', '', 1).isdigit():
                        if time_heading_location == 0 and (last_time is None or float(next_value) > float(last_time)):
                            last_time = next_value
                        for x in range(0, time_heading_location):
                            line_string = line_string.replace(next_value, '', 1)
                            next_value = nexus_file_operations.get_next_value(0, [line_string], line_string)
                            # When we reach the time column, read in the time value.
                            if x == (time_heading_location - 1) and \
                                    (last_time is None or float(next_value) > float(last_time)):
                                last_time = next_value

            if last_time is not None:
                days_completed = self.__convert_date_to_number(last_time)
                total_days = self.__convert_date_to_number(self.__times[-1])
                return round((days_completed / total_days) * 100, 1)

        return 0

    def append_include_to_grid_file(self, include_file_location):
        # Get the existing file as a list
        file = nexus_file_operations.load_file_as_list(self.__structured_grid_file_path)

        file.append(f"\nINCLUDE {include_file_location}\n")
        file.append("TOLPV LGR1 0\n")

        # Save the new file contents
        new_file_str = "".join(file)
        with open(self.__structured_grid_file_path, "w") as text_file:
            text_file.write(new_file_str)

    def __value_in_file(self, token: str, file: list):
        """Returns true if a token is found in the specified file"""
        token_found = False
        for line in file:
            if token in line:
                token_found = True

        return token_found

    def add_map_properties_to_start_of_grid_file(self):
        """Adds 'map' statements to the start of the grid file to ensure standalone outputs all the required
        properties """
        file = nexus_file_operations.load_file_as_list(self.__structured_grid_file_path)

        if not self.__value_in_file('MAPBINARY', file):
            new_file = ['MAPBINARY\n']
        else:
            new_file = []

        if not self.__value_in_file('MAPVDB', file):
            new_file.extend(['MAPVDB\n'])

        if not self.__value_in_file('MAPOUT', file):
            new_file.extend(['MAPOUT ALL\n'])
        else:
            line_counter = 0
            for line in file:
                if 'MAPOUT' in line:
                    file[line_counter] = 'MAPOUT ALL\n'
                    break
                line_counter += 1

        new_file.extend(file)

        # Save the new file contents
        new_file_str = "".join(new_file)
        with open(self.__structured_grid_file_path, "w") as text_file:
            text_file.write(new_file_str)
