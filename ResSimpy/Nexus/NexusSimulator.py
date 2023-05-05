from __future__ import annotations

import os
import warnings
from typing import Any, Union, Optional

import resqpy.model as rq

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusPVT import NexusPVT
from ResSimpy.Nexus.DataModels.NexusSeparator import NexusSeparator
from ResSimpy.Nexus.DataModels.StructuredGrid.StructuredGridFile import StructuredGridFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.NexusReporting import Reporting
from ResSimpy.Nexus.NexusWells import NexusWells
from ResSimpy.Nexus.runcontrol_operations import Runcontrol
from ResSimpy.Nexus.logfile_operations import Logging
from ResSimpy.Nexus.structured_grid_operations import StructuredGridOperations
from ResSimpy.Simulator import Simulator


class NexusSimulator(Simulator):

    def __init__(self, origin: Optional[str] = None, destination: Optional[str] = None, force_output: bool = False,
                 root_name: Optional[str] = None, nexus_data_name: str = "data", write_times: bool = False,
                 manual_fcs_tidy_call: bool = False, lazy_loading: bool = True) -> None:
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
            date_format (DateFormat): Enum value representing the date format.
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
        self.date_format: DateFormat = DateFormat.MM_DD_YYYY  # Nexus default
        self.__original_fcs_file_path: str = origin.strip()
        self.__new_fcs_file_path: str = origin.strip()
        self.__force_output: bool = force_output
        self.__origin: str = origin.strip()  # this is the fcs file path
        self.__nexus_data_name: str = nexus_data_name
        self.__structured_grid: Optional[StructuredGridFile] = None
        self.__run_units: UnitSystem = UnitSystem.ENGLISH  # The Nexus default
        self.root_name: str = root_name
        self.use_american_run_units: bool = False
        self.use_american_input_units: bool = False
        self.__write_times: bool = write_times
        self.__manual_fcs_tidy_call: bool = manual_fcs_tidy_call
        self.__surface_file_path: Optional[str] = None
        self.Wells: NexusWells = NexusWells()
        self.__default_units: UnitSystem = UnitSystem.ENGLISH  # The Nexus default
        # Model dynamic properties
        self.pvt_methods: dict[int, NexusPVT] = {}
        self.separator_methods: dict[int, NexusSeparator] = {}
        # Nexus operations modules
        self.Runcontrol: Runcontrol = Runcontrol(self)
        self.Reporting: Reporting = Reporting(self)
        self.StructuredGridOperations: StructuredGridOperations = StructuredGridOperations(self)
        self.Logging: Logging = Logging(self)
        self.__lazy_loading: bool = lazy_loading

        # Network file attributes
        self.Network = NexusNetwork(model=self)

        if destination is not None and destination != '':
            self.set_output_path(path=destination.strip())

        # Check the status of any existing or completed runs related to this model
        self.get_simulation_status(from_startup=True)

        self.fcs_file: FcsNexusFile
        # Load in the model
        self.__load_fcs_file()

    def remove_temp_from_properties(self):
        """Updates model values if the files are moved from a temp directory
        Replaces the first instance of temp/ in the file paths in the nexus simulation file paths
        Raises:
            ValueError: if any of [__structured_grid_file_path, __new_fcs_file_path, __surface_file_path] are None
        """
        if self.fcs_file.structured_grid_file.location is None:
            raise ValueError(
                "No structured_grid_file_path found, can't remove temporary properties from file path")
        if self.__new_fcs_file_path is None:
            raise ValueError(
                "No __new_fcs_file_path found, can't remove temporary properties from file path")
        if self.__surface_file_path is None:
            raise ValueError(
                "No __surface_file_path found, can't remove temporary properties from file path")

        self.__origin = self.__origin.replace('temp/', '', 1)
        self.__root_name = self.__root_name.replace('temp/', '', 1)
        self.fcs_file.structured_grid_file.location = self.fcs_file.structured_grid_file.location.replace('temp/', '',
                                                                                                          1)
        self.__new_fcs_file_path = self.__new_fcs_file_path.replace('temp/', '', 1)
        self.__surface_file_path = self.__surface_file_path.replace('temp/', '', 1)

    def get_simulation_status(self, from_startup: bool = False) -> Optional[str]:
        return self.Logging.get_simulation_status(from_startup)

    def get_simulation_progress(self) -> float:
        return self.Logging.get_simulation_progress()

    @property
    def model_location(self):
        """Returns the location of the model"""
        return os.path.dirname(self.__origin)

    @property
    def structured_grid_path(self):
        """Returns the location of the structured grid file"""
        return self.fcs_file.structured_grid_file.location

    @property
    def default_units(self):
        """Returns the default units"""
        return self.__default_units

    @property
    def run_units(self):
        """Returns the run units"""
        return self.__run_units

    @property
    def new_fcs_name(self):
        """Returns the new name for the FCS file without the fcs extension"""
        return self.__root_name

    @property
    def write_times(self) -> bool:
        return self.__write_times

    @property
    def original_fcs_file_path(self):
        return self.__original_fcs_file_path

    @property
    def origin(self):
        return self.__origin

    @property
    def root_name(self):
        return self.__root_name

    @root_name.setter
    def root_name(self, value: str) -> None:
        """ Returns the name of the fcs file without the .fcs extension
        Returns:
            str: string of the fcs file without the .fcs extension
        """
        if value is not None:
            rootname = value
        else:
            rootname = os.path.basename(self.__origin)
            rootname = rootname.split(".fcs")[0]
        self.__root_name = rootname

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
                model_oilfield_default_units = simulator.default_units() == UnitSystem.ENGLISH
                model_oilfield_run_units = simulator.run_units() == UnitSystem.ENGLISH

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
            self.__origin = self.__destination + "/" + os.path.basename(self.__original_fcs_file_path)

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
            if nfo.check_token('DATEFORMAT', line) or nfo.check_token('DATE_FORMAT', line):
                format_token = 'DATEFORMAT' if nfo.check_token('DATEFORMAT', line) else 'DATE_FORMAT'
                value = nfo.get_token_value(format_token, line, fcs_content_with_includes)
                if value is not None:
                    self.date_format = DateFormat.DD_MM_YYYY if value == 'DD/MM/YYYY' else DateFormat.MM_DD_YYYY

                self.Runcontrol.date_format_string = "%m/%d/%Y" if self.date_format is DateFormat.MM_DD_YYYY \
                    else "%d/%m/%Y"
            elif nfo.check_token('RUN_UNITS', line):
                value = nfo.get_token_value('RUN_UNITS', line, fcs_content_with_includes)
                if value is not None:
                    self.__run_units = UnitSystem(value.upper())
            elif nfo.check_token('DEFAULT_UNITS', line):
                value = nfo.get_token_value('DEFAULT_UNITS', line, fcs_content_with_includes)
                if value is not None:
                    self.__default_units = UnitSystem(value.upper())

        # Load in the other files

        # === Load in dynamic properties ===
        # Read in PVT properties from Nexus PVT method files
        if self.fcs_file.pvt_files is not None and \
                len(self.fcs_file.pvt_files) > 0:  # Check if PVT files exist
            for table_num in self.fcs_file.pvt_files.keys():  # For each PVT method
                pvt_file = self.fcs_file.pvt_files[table_num].location
                if pvt_file is None:
                    raise ValueError(f'Unable to find pvt file: {pvt_file}')
                if os.path.isfile(pvt_file):
                    self.pvt_methods[table_num] = NexusPVT(file_path=pvt_file,
                                                           method_number=table_num)  # Create NexusPVT object
                    self.pvt_methods[table_num].read_properties()  # Populate object with PVT properties in file

        # Read in separator properties from Nexus separator method files
        if self.fcs_file.separator_files is not None and \
                len(self.fcs_file.separator_files) > 0:  # Check if separator files exist
            for table_num in self.fcs_file.separator_files.keys():  # For each separator method
                separator_file = self.fcs_file.separator_files[table_num].location
                if separator_file is None:
                    raise ValueError(f'Unable to find separator file: {separator_file}')
                if os.path.isfile(separator_file):
                    self.separator_methods[table_num] = NexusSeparator(
                        file_path=separator_file, method_number=table_num)  # Create NexusSeparator object
                    self.separator_methods[table_num].read_properties()  # Populate object with separator properties

        # Load in Runcontrol
        if self.fcs_file.runcontrol_file is not None:
            self.run_control_file_path = self.fcs_file.runcontrol_file.location
            self.Runcontrol.load_run_control_file()
        if self.fcs_file.surface_files is not None:
            # TODO support multiple surface file paths
            self.__surface_file_path = list(self.fcs_file.surface_files.values())[0].location

        if self.fcs_file.structured_grid_file is not None:
            self.__structured_grid = StructuredGridFile.load_structured_grid_file(self.fcs_file.structured_grid_file,
                                                                                  lazy_loading=self.__lazy_loading)

        # Load in wellspec files
        if self.fcs_file.well_files is not None and \
                len(self.fcs_file.well_files) > 0:
            for well_file in self.fcs_file.well_files.values():
                if well_file.location is None:
                    warnings.warn(f'Well file location has not been found for {well_file}')
                    continue
                self.Wells.load_wells(
                    well_file=well_file, start_date=self.start_date, default_units=self.__default_units)
                self.Wells.wellspec_files.append(well_file)

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
        return self.Runcontrol.get_date_format(self.date_format)

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

    @property
    def StructuredGrid(self) -> Optional[StructuredGridFile]:
        """Pass the structured grid information to the front end"""
        return self.__structured_grid

    def get_structured_grid_dict(self) -> dict[str, Any]:
        """Convert the structured grid info to a dictionary and pass it to the front end"""
        if self.__structured_grid is None:
            return {}
        return self.__structured_grid.to_dict()

    def set_structured_grid(self, structured_grid: StructuredGridFile):
        """Setter method for the structured grid file for use with modifying functions"""
        self.__structured_grid = structured_grid

    def get_abs_structured_grid_path(self, filename: str):
        """Returns the absolute path to the Structured Grid file"""
        if self.fcs_file.structured_grid_file is None:
            raise ValueError(
                f"No structured grid file found within simulator class: {self.fcs_file.structured_grid_file}")
        grid_path = self.fcs_file.structured_grid_file.location
        if grid_path is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        return os.path.dirname(grid_path) + '/' + filename

    def get_surface_file_path(self):
        """Get the surface file path"""
        return self.__surface_file_path

    def load_network(self):
        """ Populates nodes and connections from a surface file  """
        self.Network.load()
