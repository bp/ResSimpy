from __future__ import annotations
from dataclasses import Field
import os
import copy
from typing import Any, Final, Union, Optional
import warnings
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusPVT import NexusPVT

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.StructuredGridFile import StructuredGridFile, PropertyToLoad, VariableEntry
import ResSimpy.Nexus.nexus_file_operations as nfo
import resqpy.model as rq

from ResSimpy.Nexus.NexusWells import NexusWells
from ResSimpy.Simulator import Simulator
from ResSimpy.Nexus.runcontrol_operations import Runcontrol
import ResSimpy.Nexus.logfile_operations as logfile_operations
import ResSimpy.Nexus.structured_grid_operations as structured_grid_operations


class NexusSimulator(Simulator):
    # Constants
    DATE_WITH_TIME_LENGTH: Final[int] = 20

    def __init__(self, origin: Optional[str] = None, destination: Optional[str] = None, force_output: bool = False,
                 root_name: Optional[str] = None, nexus_data_name: str = "data", write_times: bool = True,
                 manual_fcs_tidy_call: bool = False) -> None:
        """Nexus simulator class. Inherits from the Simulator super class

        Args:
            origin (Optional[str], optional): file path to the fcs file. Defaults to None.
            force_output (bool, optional): sets force_output parameter - unused. Defaults to False.
            root_name (Optional[str], optional): Root file name of the fcs. Defaults to None.
            nexus_data_name (str, optional): Folder name for the nexus data files to be stored in. Defaults to "data".
            write_times (bool, optional): Sets whether the runcontrol file will expand the include files with time \
                cards in. Defaults to True.
            manual_fcs_tidy_call (bool, optional): Determines whether fcs_tidy should be called - Currently not used. \
                Defaults to False.
        Attributes:
            run_control_file_path (Optional[str]): file path to the run control file - derived from the fcs file
            __destination (Optional[str]): output path for the simulation. Currently not used.
            use_american_date_format (bool): True if the simulation uses 'MM/DD/YYYY' date format.
            __job_id (int): Run job ID for executed runs
            __original_fcs_file_path (str): Path to the original fcs file path supplied
            __new_fcs_file_path (str): Where the new fcs will be saved to
            __force_output (bool): private attribute of force_output
            __origin (str): private attribute of origin. File path to the fcs file.
            __root_name (str): private attribute of root_name. Root file name of the fcs.
            __nexus_data_name (str): private attribute of nexus_data_name. Folder name for the nexus data files to be \
                stored in.
            __structured_grid_file_path (Optional[str]): file path to the structured grid.
            __structured_grid_file (Optional[StructuredGridFile]): StructuredGridFile object representing the \
                structured grid used in Nexus
            __simulation_start_time (Optional[str]): Execution start time of the simulation when submitted \
                to calculation engine
            __simulation_end_time (Optional[str]): Execution end time of the last time the simulation was run
            __previous_run_time (Optional[str]): Difference between simulation execution start time and end time
            __run_units (Optional[str]): Unit system used in the Nexus model
            use_american_run_units (bool): True if an American unit system is used equivalent to 'ENGLISH'. \
                False otherwise. For the RUN_UNITS keyword.
            use_american_input_units (bool): True if an American unit system is used equivalent to 'ENGLISH'. \
                False otherwise. For the DEFAULT_UNITS keyword.
            __write_times (bool): private attribute for write_times. Sets whether the runcontrol file will expand \
                the include files with time cards in.
            __manual_fcs_tidy_call (bool): private attribute for manual_fcs_tidy_call. Determines whether fcs_tidy \
                should be called
            __surface_file_path (Optional[str]): File path to the surface file. Derived from the fcs file.
        Raises:
            ValueError: If the FCS file path is not given
        """
        if origin is None:
            raise ValueError("FCS File Path is required")

        super().__init__()

        self.run_control_file_path: Optional[str] = ''
        self.__destination: Optional[str] = None
        self.use_american_date_format: bool = False
        self.__job_id: int = -1
        self.__original_fcs_file_path: str = origin.strip()
        self.__new_fcs_file_path: str = origin.strip()
        self.__force_output: bool = force_output
        self.__origin: str = origin.strip()  # this is the fcs file path
        self.__root_name: str = root_name if root_name is not None else self.get_rootname()
        self.__nexus_data_name: str = nexus_data_name
        self.__structured_grid_file_path: Optional[str] = None
        self.__structured_grid_file: Optional[StructuredGridFile] = None
        # run execution start time from the log file
        self.__simulation_start_time: Optional[str] = None
        # run execution finish time from the log file
        self.__simulation_end_time: Optional[str] = None
        # run execution finish time from the log file
        self.__previous_run_time: Optional[str] = None
        self.__run_units: UnitSystem = UnitSystem.ENGLISH  # The Nexus default
        self.use_american_run_units: bool = False
        self.use_american_input_units: bool = False
        self.__write_times: bool = write_times
        self.__manual_fcs_tidy_call: bool = manual_fcs_tidy_call
        self.__surface_file_path: Optional[str] = None
        self.Wells: NexusWells = NexusWells()
        self.__default_units: UnitSystem = UnitSystem.ENGLISH  # The Nexus default
        # Model dynamic properties
        self.pvt_methods: dict[int, NexusPVT] = {}

        self.Runcontrol = Runcontrol(self)

        if destination is not None and destination != '':
            self.set_output_path(path=destination.strip())

        # Check the status of any existing or completed runs related to this model
        self.get_simulation_status(from_startup=True)

        # Load in the model
        self.__load_fcs_file()

    def remove_temp_from_properties(self):
        """Updates model values if the files are moved from a temp directory
        Replaces the first instance of temp/ in the file paths in the nexus simulation file paths
        Raises:
            ValueError: if any of [__structured_grid_file_path, __new_fcs_file_path, __surface_file_path] are None
        """
        if self.__structured_grid_file_path is None:
            raise ValueError(
                "No __structured_grid_file_path found, can't remove temporary properties from file path")
        if self.__new_fcs_file_path is None:
            raise ValueError(
                "No __new_fcs_file_path found, can't remove temporary properties from file path")
        if self.__surface_file_path is None:
            raise ValueError(
                "No __surface_file_path found, can't remove temporary properties from file path")

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

    def get_default_units(self):
        """Returns the default units"""
        return self.__default_units

    def get_run_units(self):
        """Returns the run units"""
        return self.__run_units

    def get_new_fcs_name(self):
        """Returns the new name for the FCS file without the fcs extension"""
        return self.__root_name

    def get_write_times(self) -> bool:
        return self.__write_times

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
        oilfield_run_units: Optional[bool] = None
        oilfield_default_units: Optional[bool] = None

        for model in models:
            # If we're checking the units of a RESQML model, read it in and get the units. Otherwise, read the units
            # from the fcs file
            if os.path.splitext(model)[1] == '.epc':
                resqpy_model = rq.Model(epc_file=model)

                # Load in the RESQML grid
                grid = resqpy_model.grid()

                # Check the grid units
                grid_length_unit = grid.xy_units()
                model_oilfield_default_units = grid_length_unit == 'ft'
                model_oilfield_run_units = grid_length_unit == 'ft'
            else:
                simulator = NexusSimulator(origin=model)
                model_oilfield_default_units = simulator.get_default_units() == UnitSystem.ENGLISH
                model_oilfield_run_units = simulator.get_run_units() == UnitSystem.ENGLISH

            # If not defined, assign it to model_oilfield_default_units
            if oilfield_default_units is None:
                oilfield_default_units = model_oilfield_default_units
            # Raise ValueError if default units are inconsistent with the other models
            elif model_oilfield_default_units != oilfield_default_units:
                raise ValueError(f"Model at {model} using inconsistent default units")

            # If not defined, assign it to model_oilfield_run_units
            if oilfield_run_units is None:
                oilfield_run_units = model_oilfield_run_units
            # Raise ValueError if run units are inconsistent with the other models
            elif model_oilfield_run_units != oilfield_run_units:
                raise ValueError(f"Model at {model} using inconsistent run units")

        return oilfield_run_units, oilfield_default_units

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
            fcs_file = NexusFile.generate_file_include_structure(model).get_flat_list_str_file()
            surface_filename = None
            if fcs_file is None:
                warnings.warn(UserWarning(f'No file found for {model}'))
                continue
            for line in fcs_file:
                if nfo.check_token("SURFACE Network 1", line):
                    surface_filename = nfo.get_expected_token_value(token="SURFACE Network 1", token_line=line,
                                                                    file_list=fcs_file)
                    break

            if surface_filename is not None:
                surface_filename = surface_filename if os.path.isabs(surface_filename) else \
                    os.path.dirname(model) + "/" + surface_filename
                model_fluid_type = NexusSimulator.get_fluid_type(
                    surface_file_name=surface_filename)

            if fluid_type is None:
                fluid_type = model_fluid_type
            elif fluid_type != model_fluid_type:
                raise ValueError(
                    f"Inconsistent Oil / Gas types: {model_fluid_type} found for {model}")

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
            if nfo.check_token("EOS", line):
                eos_string += line
                eos_found = True
            elif eos_found:
                eos_string += line
            if nfo.check_token("COMPONENTS", line):
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
        surface_file = nfo.load_file_as_list(surface_file_name)
        fluid_type = None

        for line in surface_file:
            if nfo.check_token("BLACKOIL", line):
                fluid_type = "BLACKOIL"
                break
            elif nfo.check_token("WATEROIL", line):
                fluid_type = "WATEROIL"
                break
            elif nfo.check_token("GASWATER", line):
                fluid_type = "GASWATER"
                break
            elif nfo.check_token("EOS", line):
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

    def check_output_path(self) -> None:
        """ Confirms that the output path has been set (used to stop accidental writing operations in the original
        directory)
        Raises:
            ValueError: if the destination provided is set to None
        """
        if self.__destination is None:
            raise ValueError("Destination is required for this operation. Currently set to: ", self.__destination)

    @property
    def destination(self) -> Optional[str]:
        return self.__destination

    def set_output_path(self, path: str) -> None:
        """ Initialises the output to the declared output location. \
            If the file is a different directory to the origin path location the function will set the origin \
            to the new destination.
        """
        self.__destination = path
        if self.__destination is not None and os.path.dirname(self.__origin) != os.path.dirname(self.__destination):
            self.__origin = self.__destination + "/" + \
                            os.path.basename(self.__original_fcs_file_path)

    def __load_fcs_file(self):
        """ Loads in the information from the supplied FCS file into the class instance.
            Loads in the paths for runcontrol, structured grid and the first surface network.
            Loads in the values for dateformat and run units.
            Attempts to load the run_control_file.
            Loads the wellspec and dynamic property files.
        """
        # self.get_simulation_status(True)
        # fcs_content_with_includes is used to scan only the fcs file and files specifically called with the INCLUDE
        # token in front of it to prevent it from reading through all the other files. We need this here to extract the
        # fcs properties only. The FcsFile structure is then generated and stored in the object (with all the nesting of
        # the NexusFiles as self.fcs_file (e.g. STRUCTURED_GRID, RUNCONTROL etc)
        fcs_content_with_includes = NexusFile.generate_file_include_structure(
            self.__new_fcs_file_path).get_flat_list_str_file()
        self.fcs_file = FcsNexusFile.generate_fcs_structure(self.__new_fcs_file_path)
        if fcs_content_with_includes is None:
            raise ValueError(f'FCS file not found, no content for {self.__new_fcs_file_path}')
        for line in fcs_content_with_includes:
            if nfo.check_token('DATEFORMAT', line):
                value = nfo.get_token_value('DATEFORMAT', line, fcs_content_with_includes)
                if value is not None:
                    self.use_american_date_format = value == 'MM/DD/YYYY'
                self.Runcontrol.date_format_string = "%m/%d/%Y" if self.use_american_date_format else "%d/%m/%Y"
            elif nfo.check_token('RUN_UNITS', line):
                value = nfo.get_token_value('RUN_UNITS', line, fcs_content_with_includes)
                if value is not None:
                    self.__run_units = UnitSystem(value.upper())
            elif nfo.check_token('DEFAULT_UNITS', line):
                value = nfo.get_token_value('DEFAULT_UNITS', line, fcs_content_with_includes)
                if value is not None:
                    self.__default_units = UnitSystem(value.upper())

        # Load in the other files

        # === Load in dynamic properties
        # Read in PVT properties from Nexus PVT method files
        if not isinstance(self.fcs_file.pvt_files, Field) and self.fcs_file.pvt_files is not None and \
                len(self.fcs_file.pvt_files) > 0:  # Check if PVT files exist
            for table_num in self.fcs_file.pvt_files.keys():  # For each PVT method
                pvt_file = self.fcs_file.pvt_files[table_num].location
                if pvt_file is None:
                    raise ValueError(f'Unable to find pvt file: {pvt_file}')
                if os.path.isfile(pvt_file):
                    self.pvt_methods[table_num] = NexusPVT(file_path=pvt_file)  # Create NexusPVT object
                    self.pvt_methods[table_num].read_properties()  # Populate object with PVT properties in file

        # Load in Runcontrol
        if not isinstance(self.fcs_file.runcontrol_file, Field) and self.fcs_file.runcontrol_file is not None:
            self.run_control_file_path = self.fcs_file.runcontrol_file.location
            self.Runcontrol.load_run_control_file()
        if not isinstance(self.fcs_file.surface_files, Field) and self.fcs_file.surface_files is not None:
            # TODO support multiple surface file paths
            self.__surface_file_path = list(self.fcs_file.surface_files.values())[0].location

        if not isinstance(self.fcs_file.structured_grid_file, Field) and self.fcs_file.structured_grid_file is not None:
            self.__structured_grid_file_path = self.fcs_file.structured_grid_file.location
            self.load_structured_grid_file()

        # Load in wellspec files
        if not isinstance(self.fcs_file.well_files, Field) and self.fcs_file.well_files is not None and \
                len(self.fcs_file.well_files) > 0:
            for well_file in self.fcs_file.well_files.values():
                if well_file.location is None:
                    warnings.warn(f'Well file location has not been found for {well_file}')
                    continue
                self.Wells.load_wells(
                    well_file=well_file.location, start_date=self.start_date, default_units=self.__default_units)
                self.Wells.wellspec_paths.append(well_file.location)

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

        file = nfo.load_file_as_list(file_path)

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
                current_value = nfo.get_next_value(0, [line], line_after_token[len(token) + 1:])
                if current_value is None:
                    raise ValueError(f"No value found after the supplied {token=}, \
                        please check the following line for that token: {line}")
                new_line_after = line_after_token.replace(
                    current_value, new_value, 1)
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
        file = nfo.load_file_as_list(file_path)

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
        return self.Runcontrol.get_date_format(self.use_american_date_format)

    def modify(self, operation: str, section: str, keyword: str, content: list[str]):
        """Generic modify method to modify part of the input deck. \
        Operations are dependent on the section being modified

        Args:
            operation (str): operation to perform on the section of the input deck (e.g. 'merge')
            section (str): file type from the input deck provided (e.g. RUNCONTROL)
            keyword (str): which keyword/token to find within the deck provided (e.g. TIME)
            content (list[str]): The content to modify using the above operation, \
            represented as a list of strings with a new entry per line of the file

        Raises:
            NotImplementedError: if the functionality is not yet implemented
        """
        section = section.upper()
        keyword = keyword.upper()
        operation = operation.lower()

        if section == "RUNCONTROL":
            if keyword == "TIME":
                self.Runcontrol.modify_times(content=content, operation=operation)
            else:
                raise NotImplementedError(keyword, "not yet implemented")
        else:
            raise NotImplementedError(section, "not yet implemented")

    def get_content(self, section: str, keyword: str) -> Union[list[str], None]:
        """Returns the requested input information

        Args:
            section (str): Section to retreive information from
            keyword (str): Keyword/token to retrieve the information for

        Raises:
            NotImplementedError: if the functionality is not yet implemented

        Returns:
            Union[list[str], None]: the requested information
        """
        section = section.upper()
        keyword = keyword.upper()
        if section == "RUNCONTROL":
            if keyword == "TIME":
                return self.Runcontrol.times
            else:
                raise NotImplementedError(keyword, "not yet implemented")
        else:
            raise NotImplementedError(section, "not yet implemented")

    def change_force_output(self, force_output: bool = True) -> None:
        """Sets the force output parameter to the supplied value

        Args:
            force_output (bool, optional): sets the force_output parameter in the class instance. Defaults to True.
        """
        self.__force_output = force_output

    def __get_log_path(self, from_startup: bool = False) -> Optional[str]:
        """Returns the path of the log file for the simulation

        Args:
            from_startup (bool, optional): Searches the same directory as the original_fcs_file_path if True. \
            Otherwise searches the destination folder path, failing this then searches the \
            original_fcs_file_path if False. Defaults to False.

        Returns:
            Optional[str]: The path of the .log file from the simulation if found. If not found returns None.
        """
        folder_path = os.path.dirname(
            self.__original_fcs_file_path) if from_startup else os.path.dirname(self.__origin)
        files = os.listdir(folder_path)
        original_fcs_file_location = os.path.basename(
            self.__original_fcs_file_path)
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

    def __update_simulation_start_and_end_times(self, log_file_line_list: list[str]) -> None:
        """Updates the stored simulation execution start and end times from the log files

        Args:
            log_file_line_list (list[str]): log file information represented with a new entry per line of the file.
        """
        for line in log_file_line_list:
            if nfo.check_token('start generic pdsh   prolog', line):
                value = logfile_operations.get_simulation_time(line)
                self.__simulation_start_time = value

            if nfo.check_token('end generic pdsh   epilog', line):
                value = logfile_operations.get_simulation_time(line)
                self.__simulation_end_time = value

    def __get_start_end_difference(self) -> Optional[str]:
        """Returns a string with the previous time taken when the base case was run

        Returns:
            Optional[str]: returns a human readable string of how long the simulation took to run
        """
        if self.__simulation_start_time is None or self.__simulation_end_time is None:
            return None

        start_date = logfile_operations.convert_server_date(self.__simulation_start_time)
        end_date = logfile_operations.convert_server_date(self.__simulation_end_time)

        total_difference = (end_date - start_date)
        days = int(total_difference.days)
        hours = int((total_difference.seconds / (60 * 60)))
        minutes = int((total_difference.seconds / 60) - (hours * 60))
        seconds = int(total_difference.seconds -
                      (hours * 60 * 60) - (minutes * 60))

        return f"{days} Days, {hours} Hours, {minutes} Minutes {seconds} Seconds"

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
                return logfile_operations.get_errors_warnings_string(log_file_line_list=log_file_line_list)
            else:
                job_number_line = [
                    x for x in log_file_line_list if 'Job number:' in x]
                if len(job_number_line) > 0:
                    self.__job_id = int(job_number_line[0].split(":")[1])
                    # self.__get_job_status()
                    return f"Job Running, ID: {self.__job_id}"
        return None

    def load_structured_grid_file(self):
        """Loads in a structured grid file including all grid properties and modifiers.
        Currently loading in grids with FUNCTIONS included are not supported.

        Raises:
            AttributeError: if no value is found for the structured grid file path
            ValueError: if when loading the grid no values can be found for the NX NY NZ line.
        """
        if self.__structured_grid_file_path is None:
            raise ValueError("No file path given or found for structured grid file path. \
                Please update structured grid file path")
        file_as_list = nfo.load_file_as_list(self.__structured_grid_file_path)
        structured_grid_file = StructuredGridFile()

        def move_next_value(next_line: str) -> tuple[str, str]:
            """finds the next value and then strips out the value from the line.

            Args:
                next_line (str): the line to search through for the value

            Raises:
                ValueError: if no value is found within the line provided

            Returns:
                tuple[str, str]: the next value found in the line, the line with the value stripped out.
            """
            value = nfo.get_next_value(0, [next_line], next_line)
            if value is None:
                raise ValueError(f"No value found within the provided line: {next_line}")
            next_line = next_line.replace(value, "", 1)
            return value, next_line

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
                    structured_grid_operations.load_token_value_if_present(token_property.token, modifier,
                                                                           token_property.property, line,
                                                                           file_as_list, ['INCLUDE'])

            # Load in grid dimensions
            if nfo.check_token('NX', line):
                # Check that the format of the grid is NX followed by NY followed by NZ
                current_line = file_as_list[file_as_list.index(line)]
                remaining_line = current_line[current_line.index('NX') + 2:]
                if nfo.get_next_value(0, [remaining_line], remaining_line) != 'NY':
                    continue
                remaining_line = remaining_line[remaining_line.index('NY') + 2:]
                if nfo.get_next_value(0, [remaining_line], remaining_line) != 'NZ':
                    continue

                # Avoid loading in a comment
                if "!" in line and line.index("!") < line.index('NX'):
                    continue
                next_line = file_as_list[file_as_list.index(line) + 1]
                first_value, next_line = move_next_value(next_line)
                second_value, next_line = move_next_value(next_line)
                third_value, next_line = move_next_value(next_line)

                structured_grid_file.range_x = int(first_value)
                structured_grid_file.range_y = int(second_value)
                structured_grid_file.range_z = int(third_value)

        self.__structured_grid_file = structured_grid_file

    def get_structured_grid(self) -> Optional[StructuredGridFile]:
        """Pass the structured grid information to the front end"""
        return self.__structured_grid_file

    def get_structured_grid_dict(self) -> dict[str, Any]:
        """Convert the structured grid info to a dictionary and pass it to the front end"""
        return self.__structured_grid_file.__dict__

    def get_simulation_start_time(self) -> str:
        """Get the start time of an executed simulation run, if no simulation start time returns '-'"""
        self.get_simulation_status()
        if self.__simulation_start_time is not None:
            return self.__simulation_start_time
        else:
            return '-'

    def get_simulation_end_time(self) -> str:
        """Get the end time of an executed simulation run if it has completed, if no simulation end time returns '-'"""
        self.get_simulation_status()
        if self.__simulation_end_time is not None:
            return self.__simulation_end_time
        else:
            return '-'

    def get_job_id(self) -> int:
        """Get the job Id of a simulation run"""
        return self.__job_id

    def update_structured_grid_file(self, grid_dict: dict[str, Union[VariableEntry, int]]) -> None:
        """Save values passed from the front end to the structured grid file and update the class

        Args:
            grid_dict (dict[str, Union[VariableEntry, int]]): dictionary containing grid properties to be replaced

        Raises:
            ValueError: If no structured grid file is in the instance of the Simulator class
        """
        if self.__structured_grid_file is None:
            raise ValueError("No structured grid file found. Please provide data for structured grid \
                e.g. through load_structured_grid_file method")
        # Convert the dictionary back to a class, and update the properties on our class
        original_structured_grid_file = copy.deepcopy(self.__structured_grid_file)
        self.__structured_grid_file = StructuredGridFile(grid_dict)

        # Get the existing file as a list
        if self.__structured_grid_file_path is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        # TODO move the loading of structured grid file to fcs_reader
        file = nfo.load_file_as_list(self.__structured_grid_file_path)
        # Update each value in the file
        structured_grid_operations.replace_value(file, original_structured_grid_file.netgrs,
                                                 self.__structured_grid_file.netgrs, 'NETGRS')
        structured_grid_operations.replace_value(file, original_structured_grid_file.porosity,
                                                 self.__structured_grid_file.porosity, 'POROSITY')
        structured_grid_operations.replace_value(file, original_structured_grid_file.sw,
                                                 self.__structured_grid_file.sw, 'SW')
        structured_grid_operations.replace_value(file, original_structured_grid_file.kx,
                                                 self.__structured_grid_file.kx, 'KX')
        structured_grid_operations.replace_value(file, original_structured_grid_file.ky,
                                                 self.__structured_grid_file.ky, 'KY')
        structured_grid_operations.replace_value(file, original_structured_grid_file.kz,
                                                 self.__structured_grid_file.kz, 'KZ')

        # Save the new file contents
        new_file_str = "".join(file)
        with open(self.__structured_grid_file_path, "w") as text_file:
            text_file.write(new_file_str)

    @staticmethod
    def get_grid_file_as_3d_list(path: str) -> Optional[list]:
        """Converts a grid file to a 3D list

        Args:
            path (str): path to a grid file

        Returns:
            Optional[list[str]]: Returns None if no file is found, returns the grid as a 3d array otherwise
        """
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
                    float_list_split = [float(x) for x in x_list if x != ""]
                    new_list_split_cleaned.append(float_list_split)
                sub_lists.append(new_list_split_cleaned)
                new_list_str = ""
            else:
                new_list_str = new_list_str + sub_list
        return sub_lists

    def view_command(self, field: str, previous_lines: int = 3, following_lines: int = 3) -> Optional[str]:
        """Displays how the property is declared in the structured grid file

        Args:
            field (str): property as written in the structured grid (e.g. KX)
            previous_lines (int, optional): how many lines to look back from the field searched for. Defaults to 3.
            following_lines (int, optional): how many lines to look forward from the field searched for. Defaults to 3.

        Raises:
            ValueError: if no structured grid file path is specified in the class instance

        Returns:
            Optional[str]: the string associated with the supplied property from within the structured grid. \
                If the field is not found in the structured grid returns None.
        """
        structured_grid_dict = self.get_structured_grid_dict()
        command_token = f"{field.upper()} {structured_grid_dict[field.lower()].modifier}"
        if self.__structured_grid_file_path is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        file_as_list = nfo.load_file_as_list(self.__structured_grid_file_path)

        for line in file_as_list:
            if nfo.check_token(command_token, line):
                start_index = file_as_list.index(line) - previous_lines \
                    if file_as_list.index(line) - previous_lines > 0 else 0
                end_index = file_as_list.index(line) + following_lines \
                    if file_as_list.index(line) + following_lines < len(file_as_list) else len(file_as_list) - 1

                new_array = file_as_list[start_index: end_index]
                new_array = [x.strip("'") for x in new_array]
                value = "".join(new_array)
                return value
        return None

    def get_abs_structured_grid_path(self, filename: str):
        """Returns the absolute path to the Structured Grid file"""
        if self.__structured_grid_file_path is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        return os.path.dirname(self.__structured_grid_file_path) + '/' + filename

    def get_surface_file_path(self):
        """Get the surface file path"""
        return self.__surface_file_path

    def get_base_case_run_time(self) -> str:
        """Get the time taken for the base case to run. Returns '-' if no run time found."""
        if self.__previous_run_time is not None:
            return self.__previous_run_time
        else:
            return '-'

    def get_simulation_progress(self) -> float:
        """Returns the simulation progress from log files

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
            case_name_string = f"Case Name = {self.__root_name}"
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
                    for x in range(0, time_heading_location):
                        line_string = line_string.replace(next_value, '', 1)
                        next_value = nfo.get_next_value(0, [line_string], line_string)
                        if next_value is None:
                            break
                        # When we reach the time column, read in the time value.
                        if x == (time_heading_location - 1) and \
                                (last_time is None or float(next_value) > float(last_time)):
                            last_time = next_value

        if last_time is not None:
            days_completed = self.Runcontrol.convert_date_to_number(last_time)
            if self.Runcontrol.times is None:
                raise ValueError("No times provided in the instance - please read them in from runcontrol file")
            total_days = self.Runcontrol.convert_date_to_number(self.Runcontrol.times[-1], )
            return round((days_completed / total_days) * 100, 1)

        return 0

    # TODO: move to 'Reporting' module
    def add_map_properties_to_start_of_grid_file(self):
        """Adds 'map' statements to the start of the grid file to ensure standalone outputs all the required \
        properties. Writes out to the same structured grid file path provided.

        Raises:
            ValueError: if no structured grid file path is specified in the class instance
        """
        if self.__structured_grid_file_path is None:
            raise ValueError("No file path given or found for structured grid file path. \
                Please update structured grid file path")
        file = nfo.load_file_as_list(self.__structured_grid_file_path)

        if not nfo.value_in_file('MAPBINARY', file):
            new_file = ['MAPBINARY\n']
        else:
            new_file = []

        if not nfo.value_in_file('MAPVDB', file):
            new_file.extend(['MAPVDB\n'])

        if not nfo.value_in_file('MAPOUT', file):
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
        with open(self.__structured_grid_file_path, "w") as text_file:
            text_file.write(new_file_str)

        # def export_fcs_file_graph(self):
        #     from_main_lists = []
        #     to_main_lists = []
        #     from_list, to_list = self.runcontrol_file.export_network_lists()
        #     from_main_lists.extend(from_list)
        #     to_main_lists.extend(to_list)
