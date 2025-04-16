"""The Nexus Simulator class is the main class for interacting with Nexus models."""
from __future__ import annotations

import os
import warnings
from typing import Any, Union, Optional, Sequence

import resqpy.model as rq
from datetime import datetime
from ResSimpy.Nexus.DataModels.NexusOptions import NexusOptions
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusPVTMethods import NexusPVTMethods
from ResSimpy.Nexus.NexusSeparatorMethods import NexusSeparatorMethods
from ResSimpy.Nexus.NexusWaterMethods import NexusWaterMethods
from ResSimpy.Nexus.NexusEquilMethods import NexusEquilMethods
from ResSimpy.Nexus.NexusRockMethods import NexusRockMethods
from ResSimpy.Nexus.NexusRelPermMethods import NexusRelPermMethods
from ResSimpy.Nexus.NexusValveMethods import NexusValveMethods
from ResSimpy.Nexus.NexusAquiferMethods import NexusAquiferMethods
from ResSimpy.Nexus.NexusHydraulicsMethods import NexusHydraulicsMethods
from ResSimpy.Nexus.NexusGasliftMethods import NexusGasliftMethods
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.NexusReporting import NexusReporting
from ResSimpy.Nexus.NexusWells import NexusWells
from ResSimpy.Nexus.runcontrol_operations import SimControls
from ResSimpy.Nexus.logfile_operations import Logging
from ResSimpy.Nexus.structured_grid_operations import StructuredGridOperations
from ResSimpy.DataModelBaseClasses.Simulator import Simulator


class NexusSimulator(Simulator):

    def __init__(self, origin: Optional[str] = None, destination: Optional[str] = None,
                 root_name: Optional[str] = None, nexus_data_name: str = "data", write_times: bool = False,
                 manual_fcs_tidy_call: bool = False, lazy_loading: bool = True) -> None:
        """Nexus simulator class. Inherits from the Simulator super class.

        Args:
            origin (Optional[str], optional): file path to the fcs file. Defaults to None.
            destination (Optional[str], optional): The location to move the model to.
            root_name (Optional[str], optional): Root file name of the fcs. Defaults to None.
            nexus_data_name (str, optional): Folder name for the nexus data files to be stored in. Defaults to "data".
            write_times (bool, optional): Sets whether the runcontrol file will expand the include files with time \
                cards in. Defaults to True.
            manual_fcs_tidy_call (bool, optional): Determines whether fcs_tidy should be called - Currently not used. \
                Defaults to False.
            lazy_loading(bool): If set to True, parts of the model will only be loaded in when requested via \
                properties on the object.

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
            __structured_grid_file (Optional[NexusGrid]): StructuredGridFile object representing the \
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

        Raises:
            ValueError: If the FCS file path is not given

        Examples:
            Example of calling a NexusSimulator with a file path to an fcs file:

            >>> from ResSimpy.Nexus.NexusSimulator import NexusSimulator
            >>> model = NexusSimulator(origin="/path/to/fcs_file.fcs")

        """
        if origin is None:
            raise ValueError(f'Origin path to model fcs file is required. Instead got {origin}.')
        self.origin: str = origin

        self._start_date: str = ''
        self.run_control_file_path: Optional[str] = ''
        self.__destination: Optional[str] = None
        self.date_format: DateFormat = DateFormat.MM_DD_YYYY  # Nexus default
        self.__original_fcs_file_path: str = self.origin
        self.__new_fcs_file_path: str = self.origin
        self.__nexus_data_name: str = nexus_data_name
        self.__run_units: UnitSystem = UnitSystem.ENGLISH  # The Nexus default
        self.root_name: str = root_name
        self.use_american_run_units: bool = False
        self.use_american_input_units: bool = False
        self.__write_times: bool = write_times
        self.__manual_fcs_tidy_call: bool = manual_fcs_tidy_call

        self._default_units: UnitSystem = UnitSystem.ENGLISH  # The Nexus default

        self._network: NexusNetwork = NexusNetwork(model=self)
        self._wells: NexusWells = NexusWells(self)
        self._grid: Optional[NexusGrid] = None
        self._options: Optional[NexusOptions] = None
        # Model dynamic properties
        self._pvt: NexusPVTMethods = NexusPVTMethods(model_unit_system=self.default_units)
        self._separator: NexusSeparatorMethods = NexusSeparatorMethods(model_unit_system=self.default_units)
        self._water: NexusWaterMethods = NexusWaterMethods(model_unit_system=self.default_units)
        self._equil: NexusEquilMethods = NexusEquilMethods(model_unit_system=self.default_units)
        self._rock: NexusRockMethods = NexusRockMethods(model_unit_system=self.default_units)
        self._relperm: NexusRelPermMethods = NexusRelPermMethods(model_unit_system=self.default_units)
        self._valve: NexusValveMethods = NexusValveMethods(model_unit_system=self.default_units)
        self._aquifer: NexusAquiferMethods = NexusAquiferMethods(model_unit_system=self.default_units)
        self._hydraulics: NexusHydraulicsMethods = NexusHydraulicsMethods(model_unit_system=self.default_units)
        self._gaslift: NexusGasliftMethods = NexusGasliftMethods(model_unit_system=self.default_units)
        # Nexus operations modules
        self.logging: Logging = Logging(self)
        self.reporting: NexusReporting = NexusReporting(self)
        self._structured_grid_operations: StructuredGridOperations = StructuredGridOperations(self)
        self.__lazy_loading: bool = lazy_loading
        self._sim_controls: SimControls = SimControls(self)

        if destination is not None and destination != '':
            self.set_output_path(path=destination.strip())

        # Check the status of any existing or completed runs related to this model
        self.get_simulation_status(from_startup=True)

        self._model_files: FcsNexusFile
        # Load in the model
        self.__load_fcs_file()

    def __repr__(self) -> str:
        """Pretty printing NexusSimulator data."""
        printable_str = f'Simulation name: {self.root_name}\n'
        printable_str += super().__repr__()
        printable_str += f'Run units: {str(self.default_units)}\n'
        # add details from the fcsfile
        printable_str += self.model_files.__repr__()
        return printable_str

    @staticmethod
    def _attr_info_to_tuple(sim_attr: Union[dict, Sequence]) \
            -> tuple[tuple[tuple[str, Union[str, bool, float]], ...], ...]:
        """Convert the network constraints/wells completions attribute to a tuple of tuples so that it is hashable.

        Args: sim_attr (Union[dict, Sequence]): dict of {well name: [NexusConstraint]} for
        self.network.constraints.get_all(), list of [NexusWell objects] for self.wells.get_all()

        Returns: Tuple[Tuple[Tuple[str, Union[str, float, bool]], ...], ...]: tuple of tuples
        """
        lst_of_tuples = []
        if isinstance(sim_attr, dict):
            for wells, nexus_constraint in sim_attr.items():
                for constraints in nexus_constraint:
                    network_dict = constraints.to_dict(add_units=False, include_nones=False)
                    lst_of_tuples.append(tuple(network_dict.items()))

        elif isinstance(sim_attr, list):
            for nexus_completion in sim_attr:
                for el in nexus_completion.completions:
                    well_dict = el.to_dict(add_units=False, include_nones=False)
                    lst_of_tuples.append(tuple(well_dict.items()))

        return tuple(lst_of_tuples)

    def network_wells_tuple(self) -> tuple:
        """Returns a tuple of the network constraints and wells completions attributes.

        Returns:
            tuple: tuple of the network constraints and wells completions attributes
        """
        network_attr = self.network.constraints.get_all()
        wells_attr = self.wells.get_all()

        network_tuple = self._attr_info_to_tuple(network_attr)
        wells_tuple = self._attr_info_to_tuple(wells_attr)
        return network_tuple, wells_tuple

    def hash_network_wells(self) -> int:
        """Hashes the network constraints and wells completions attributes.

        Returns:
            int: hash value of the network constraints and wells completions attributes
        """
        hash_attr_tuple = self.network_wells_tuple()
        return hash(hash_attr_tuple)

    def wells_and_network_equal(self, other: NexusSimulator) -> bool:
        """Compares the network constraints and wells completions of two NexusSimulator objects.

        Args:
            other (NexusSimulator): NexusSimulator object to compare with

        Returns:
            Union[bool]: Returns True if the network constraints and wells completions are equal, False otherwise.

        Raises:
            ValueError: if both models have no network constraints or wells completions.
            TypeError: if the other object is not a NexusSimulator object.
        """
        if isinstance(other, NexusSimulator):
            base_class_tuple = self.network_wells_tuple()
            other_class_tuple = other.network_wells_tuple()
            if base_class_tuple == ((), ()) and other_class_tuple == ((), ()):
                # if base_class_tuple and other_class_tuple both return empty tuple, that means both of them /
                # have no network constraints or wells completions
                raise ValueError("Both models have empty network constraints or wells completions. Unable to compare.")
            return self.network_wells_tuple() == other.network_wells_tuple()
        raise TypeError(f"Unable to compare {type(self)} with {other}. Ensure that {other} is of type NexusSimulator. "
                        f"{other} has {type(other)}")

    def remove_temp_from_properties(self) -> None:
        """Updates model values if the files are moved from a temp directory.

        Replaces the first instance of temp/ in the file paths in the nexus simulation file paths.

        Raises:
            ValueError: if any of [__structured_grid_file_path, __new_fcs_file_path, __surface_file_path] are None.
        """
        if self.model_files.structured_grid_file is None or self.model_files.structured_grid_file.location is None:
            raise ValueError(
                "No structured_grid_file_path found, can't remove temporary properties from file path")
        if self.__new_fcs_file_path is None:
            raise ValueError(
                "No __new_fcs_file_path found, can't remove temporary properties from file path")
        if self.model_files.surface_files is None or self.model_files.surface_files[1] is None \
                or self.model_files.surface_files[1].location is None:
            raise ValueError(
                "No __surface_file_path found, can't remove temporary properties from file path")

        self._origin = self._origin.replace('temp/', '', 1)
        self.__root_name = '' if self.root_name is None else self.root_name.replace('temp/', '', 1)
        self.model_files.structured_grid_file.location = \
            self.model_files.structured_grid_file.location.replace('temp/', '', 1)
        self.__new_fcs_file_path = self.__new_fcs_file_path.replace('temp/', '', 1)
        self.model_files.surface_files[1].location = self.model_files.surface_files[1].location.replace('temp/', '', 1)

    def get_simulation_status(self, from_startup: bool = False) -> Optional[str]:
        """Returns run status from the latest simulation run.

        Args:
            from_startup(bool = False): Searches the same directory as the original_fcs_file_path if true.
            Otherwise searches the destination folder path, failing this then searches the original_fcs_file_path
            if false. Defaults to false.
        """
        return self.logging.get_simulation_status(from_startup)

    def get_simulation_progress(self) -> float:
        """Returns simulation progress from log files."""
        return self.logging.get_simulation_progress()

    def get_users_linked_with_files(self) -> Optional[list[tuple[Optional[str], Optional[str], Optional[datetime]]]]:
        """Returns list of users linked with each model file."""
        return self.model_files.files_info

    @property
    def model_files(self) -> FcsNexusFile:
        """Returns model files associated with instance of 'FcsNexusfile'."""
        return self._model_files

    @property
    def network(self) -> NexusNetwork:
        """Returns an instance of Nexus network class."""
        return self._network

    @property
    def structured_grid_path(self) -> Optional[str]:
        """Returns the location of the structured grid file."""
        return None if self.model_files.structured_grid_file is None else self.model_files.structured_grid_file.location

    @property
    def default_units(self) -> UnitSystem:
        """Returns the default units."""
        return self._default_units

    @staticmethod
    def sim_default_unit_system() -> UnitSystem:
        """Returns the default unit system used by the Simulator."""
        return UnitSystem.ENGLISH

    @property
    def run_units(self) -> UnitSystem:
        """Returns the run units."""
        return self.__run_units

    @property
    def new_fcs_name(self) -> Optional[str]:
        """Returns the new name for the FCS file without the fcs extension."""
        return self.__root_name

    @property
    def write_times(self) -> bool:
        """Sets whether the runcontrol file will expand the include files with time cards in."""
        return self.__write_times

    @property
    def original_fcs_file_path(self) -> str:
        """Returns path to the original fcs file path supplied."""
        return self.__original_fcs_file_path

    @property
    def root_name(self) -> Optional[str]:
        """Returns root file name of the fcs."""
        return self.__root_name

    @root_name.setter
    def root_name(self, value: Optional[str]) -> None:
        """Returns the name of the fcs file without the .fcs extension.

        Returns:
            str: string of the fcs file without the .fcs extension.
        """
        if value is not None:
            rootname = value
        else:
            rootname = os.path.basename(self._origin)
            rootname = rootname.split(".fcs")[0]
        self.__root_name = rootname

    @staticmethod
    def get_check_run_input_units_for_models(models: list[str]) -> tuple[Optional[bool], Optional[bool]]:
        # TODO: add LAB units
        """Returns the run and input unit formats for all the supplied models.

        Supported model formats:
            RESQML type epc files ending in ".epc"
            Nexus files containing a line identifying the "RUN_UNITS" or "DEFAULT_UNITS".

        Supported units: ENGLISH, METRIC

        Args:
            models (list[str]): list of paths to supported reservoir models

        Raises:
            ValueError: if a model in the list is using inconcistent run/default units

        Returns:
            Tuple[Optional[Bool], Optional[Bool]]: If all units are consistent between models,
                Returns (True, True) if 'ft' is the length unit in an epc or Nexus specifies "ENGLISH" as the
                (RUN_UNITS,DEFAULT_UNITS) respectively and False, False otherwise.
                Returns (None, None) if it can't find a (RUN_UNITS, DEFAULT_UNITS) in the supplied files.
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
                model_oilfield_default_units = simulator.default_units == UnitSystem.ENGLISH
                model_oilfield_run_units = simulator.run_units == UnitSystem.ENGLISH

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

        Currently limited to checking for the first SURFACE network in a file.

        Args:
            models (list[str]): a list of paths to models to check for fluid types.

        Raises:
            ValueError: If fluid types are inconsistent between models

        Returns:
            Optional[str]: The fluid type used for the model for the first surface network
        """
        fluid_type = None
        for model in models:
            model_obj = NexusSimulator(origin=model)
            model_fluid_type = None
            # get the first surface method and expand out all include files
            if model_obj.model_files.surface_files is None or model_obj.model_files.surface_files[1].location is None:
                raise ValueError(f"No surface file found for {model}")
            surface_file_content = model_obj.model_files.surface_files[1].get_flat_list_str_file
            if surface_file_content is not None:
                model_fluid_type = NexusSimulator.get_fluid_type(
                    surface_file_content=surface_file_content)

            if fluid_type is None:
                fluid_type = model_fluid_type
            elif fluid_type != model_fluid_type:
                raise ValueError(
                    f"Inconsistent Oil / Gas types: {model_fluid_type} found for {model}")

        return fluid_type

    @staticmethod
    def get_eos_details(surface_file: list[str]) -> str:
        """Gets all the information about an EOS from a Nexus model.

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
            elif eos_found and nfo.get_next_value(0, [line]) is not None:
                eos_string += line
            if nfo.check_token("COMPONENTS", line):
                break

        return eos_string

    @staticmethod
    def get_fluid_type(surface_file_content: list[str]) -> str:
        """Gets the fluid type for a single model from a surface file.

        Defaults to BLACKOIL if no explicit fluid type is found.

        Args:
            surface_file_content (str): list of strings with a new line per entry from the surface file

        Returns:
            str: fluid type as one of [BLACKOIL, WATEROIL, GASWATER, API] or the full details from an EOS model
        """
        fluid_type = None

        for line in surface_file_content:
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
                fluid_type = NexusSimulator.get_eos_details(surface_file_content)
            elif nfo.check_token("API", line):
                fluid_type = "API"
        if fluid_type is None:
            warnings.warn("No explicit fluid type found in the file. Defaulting to BLACKOIL", UserWarning)
            fluid_type = "BLACKOIL"
        return fluid_type

    def get_model_oil_type(self) -> str:
        """Returns the get_fluid_type method on the existing NexusSimulator instance.

        Raises:
            ValueError: If no file path is provided for the surface file path

        Returns:
            str: fluid type as one of [BLACKOIL, WATEROIL, GASWATER,] or the full details from an EOS model
        """
        if self.model_files.surface_files is None or self.model_files.surface_files[1].location is None:
            raise ValueError("No value found for the path to the surface file")
        return NexusSimulator.get_fluid_type(self.model_files.surface_files[1].get_flat_list_str_file)

    def check_output_path(self) -> None:
        """Confirms that the output path has been set.

        (used to stop accidental writing operations in the original directory).

        Raises:
            ValueError: if the destination provided is set to None.
        """
        if self.__destination is None:
            raise ValueError("Destination is required for this operation. Currently set to: ", self.__destination)

    @property
    def destination(self) -> Optional[str]:
        """Returns the destination to move the model to (either as a string or none)."""
        return self.__destination

    def set_output_path(self, path: str) -> None:
        """Initialises the output to the declared output location.

        If the file is a different directory to the origin path location the function will set the origin
        to the new destination.
        """
        self.__destination = path
        if self.__destination is not None and os.path.dirname(self._origin) != os.path.dirname(self.__destination):
            self._origin = self.__destination + "/" + os.path.basename(self.__original_fcs_file_path)

    def __load_fcs_file(self) -> None:
        """Loads in the information from the supplied FCS file into the class instance.

        Loads in the paths for runcontrol, structured grid and the first surface network.
        Loads in the values for dateformat and run units.
        Attempts to load the run_control_file.
        Loads the wellspec and dynamic property files.
        """
        # fcs_content_with_includes is used to scan only the fcs file and files specifically called with the INCLUDE
        # token in front of it to prevent it from reading through all the other files. We need this here to extract the
        # fcs properties only. The FcsFile structure is then generated and stored in the object (with all the nesting of
        # the NexusFiles as self.model_files (e.g. STRUCTURED_GRID, RUNCONTROL etc.)
        fcs_content_with_includes = (NexusFile.generate_file_include_structure(origin=self.origin,
                                                                               file_path=self.__new_fcs_file_path)
                                     .get_flat_list_str_file)
        self._model_files = FcsNexusFile.generate_fcs_structure(self.__new_fcs_file_path)
        if fcs_content_with_includes is None:
            raise ValueError(f'FCS file not found, no content for {self.__new_fcs_file_path}')
        for line in fcs_content_with_includes:
            if nfo.check_token('DATEFORMAT', line) or nfo.check_token('DATE_FORMAT', line):
                format_token = 'DATEFORMAT' if nfo.check_token('DATEFORMAT', line) else 'DATE_FORMAT'
                value = fo.get_token_value(format_token, line, fcs_content_with_includes)
                if value is not None:
                    self.date_format = DateFormat.DD_MM_YYYY if value == 'DD/MM/YYYY' else DateFormat.MM_DD_YYYY

                self._sim_controls.date_format_string = "%m/%d/%Y" if self.date_format is DateFormat.MM_DD_YYYY \
                    else "%d/%m/%Y"
            elif nfo.check_token('RUN_UNITS', line):
                value = fo.get_token_value('RUN_UNITS', line, fcs_content_with_includes)
                if value is not None:
                    self.__run_units = UnitSystem(value.upper())
            elif nfo.check_token('DEFAULT_UNITS', line):
                value = fo.get_token_value('DEFAULT_UNITS', line, fcs_content_with_includes)
                if value is not None:
                    self._default_units = UnitSystem(value.upper())
            elif nfo.check_token(token='RESERVOIR', line=line):
                raise NotImplementedError('Multiple reservoir models are not currently supported by ResSimpy.')

        # Load in the Nexus options information
        if self.model_files.options_file is not None:
            self._options = NexusOptions(file=self.model_files.options_file,
                                         model_unit_system=self.default_units)

        # === Load in dynamic properties ===
        # Read in PVT properties from Nexus PVT method files
        if self.model_files.pvt_files is not None and \
                len(self.model_files.pvt_files) > 0:
            self._pvt = NexusPVTMethods(files=self.model_files.pvt_files,
                                        model_unit_system=self.default_units)

        # Read in separator properties from Nexus separator method files
        if self.model_files.separator_files is not None and \
                len(self.model_files.separator_files) > 0:
            self._separator = NexusSeparatorMethods(files=self.model_files.separator_files,
                                                    model_unit_system=self.default_units)

        # Read in water properties from Nexus water method files
        if self.model_files.water_files is not None and \
                len(self.model_files.water_files) > 0:
            self._water = NexusWaterMethods(files=self.model_files.water_files,
                                            model_unit_system=self.default_units)

        # Read in equilibration properties from Nexus equil method files
        if self.model_files.equil_files is not None and \
                len(self.model_files.equil_files) > 0:
            self._equil = NexusEquilMethods(files=self.model_files.equil_files,
                                            model_unit_system=self.default_units)

        # Read in rock properties from Nexus rock method files
        if self.model_files.rock_files is not None and \
                len(self.model_files.rock_files) > 0:
            self._rock = NexusRockMethods(files=self.model_files.rock_files,
                                          model_unit_system=self.default_units)

        # Read in relative permeability and capillary pressure properties from Nexus relperm method files
        if self.model_files.relperm_files is not None and \
                len(self.model_files.relperm_files) > 0:
            self._relperm = NexusRelPermMethods(files=self.model_files.relperm_files,
                                                model_unit_system=self.default_units)

        # Read in valve and choke properties from Nexus valve method files
        if self.model_files.valve_files is not None and \
                len(self.model_files.valve_files) > 0:
            self._valve = NexusValveMethods(files=self.model_files.valve_files,
                                            model_unit_system=self.default_units)

        # Read in aquifer properties from Nexus aquifer method files
        if self.model_files.aquifer_files is not None and \
                len(self.model_files.aquifer_files) > 0:
            self._aquifer = NexusAquiferMethods(files=self.model_files.aquifer_files,
                                                model_unit_system=self.default_units)

        # Read in hydraulics properties from Nexus hyd method files
        if self.model_files.hyd_files is not None and \
                len(self.model_files.hyd_files) > 0:
            self._hydraulics = NexusHydraulicsMethods(files=self.model_files.hyd_files,
                                                      model_unit_system=self.default_units)

        # Read in gaslift properties from Nexus gaslift method files
        if self.model_files.gas_lift_files is not None and \
                len(self.model_files.gas_lift_files) > 0:
            self._gaslift = NexusGasliftMethods(files=self.model_files.gas_lift_files,
                                                model_unit_system=self.default_units)

        # === End of dynamic properties loading ===

        # Load in Runcontrol
        if self.model_files.runcontrol_file is not None:
            self.run_control_file_path = self.model_files.runcontrol_file.location
            self._sim_controls.load_run_control_file()

        if self.model_files.structured_grid_file is not None:
            self._grid = NexusGrid.load_structured_grid_file(self.model_files.structured_grid_file,
                                                             lazy_loading=self.__lazy_loading,
                                                             model_unit_system=self.default_units)

        # Load in wellspec files
        if self.model_files.well_files is not None and \
                len(self.model_files.well_files) > 0:
            for well_file in self.model_files.well_files.values():
                if well_file.location is None:
                    warnings.warn(f'Well file location has not been found for {well_file}')
                    continue

    @staticmethod
    def update_file_value(file_path: str, token: str, new_value: str, add_to_start: bool = False) -> None:
        """Updates a value in a file if it is present and in the format {TOKEN} {VALUE}.

        If the token isn't present, it will add the token + value to either the start or end of the file.

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

    def update_fcs_file_value(self, token: str, new_value: str, add_to_start: bool = False) -> None:
        """Updates a value in the FCS file."""
        self.update_file_value(self.__new_fcs_file_path, token=token, new_value=new_value, add_to_start=add_to_start)

    @staticmethod
    def comment_out_file_value(token: str, file_path: str) -> None:
        """Comments out an uncommented line containing the specified token.

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
        """Returns the date format being used by the model.

        formats used: ('MM/DD/YYYY', 'DD/MM/YYYY').
        """
        return self._sim_controls.get_date_format(self.date_format)

    def modify(self, operation: str, section: str, keyword: str, content: list[str]) -> None:
        """Generic modify method to modify part of the input deck.

        Operations are dependent on the section being modified.

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
                self._sim_controls.modify_times(content=content, operation=operation)
            else:
                raise NotImplementedError(keyword, "not yet implemented")
        else:
            raise NotImplementedError(section, "not yet implemented")

    def get_content(self, section: str, keyword: str) -> Union[list[str], None]:
        """Returns the requested input information.

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
                return self._sim_controls.times
            else:
                raise NotImplementedError(keyword, "not yet implemented")
        else:
            raise NotImplementedError(section, "not yet implemented")

    def get_structured_grid_dict(self) -> dict[str, Any]:
        """Convert the structured grid info to a dictionary and pass it to the front end."""
        if self._grid is None:
            return {}
        return self._grid.to_dict()

    def get_abs_structured_grid_path(self, filename: str) -> str:
        """Returns the absolute path to the Structured Grid file."""
        if self.model_files.structured_grid_file is None:
            raise ValueError(
                f"No structured grid file found within simulator class: {self.model_files.structured_grid_file}")
        grid_path = self.model_files.structured_grid_file.location
        if grid_path is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        return os.path.dirname(grid_path) + '/' + filename

    def get_surface_file_path(self) -> str:
        """Get the surface file path."""
        if self.model_files.surface_files is None or self.model_files.surface_files[1] is None:
            raise ValueError('No path found for surface file.')
        return self.model_files.surface_files[1].location

    def load_network(self) -> None:
        """Populates nodes and connections from a surface file."""
        self._network.load()

    def write_out_case(self, new_file_path: str, new_include_file_location: str = 'include_files',
                       case_suffix: str = '') -> None:
        """Creates a new case of a simulator run by writing out the modified include files to a new file.

        Args:
            new_file_path (str): Path to save the new simulator to.
            new_include_file_location (str): Saves included files to a path either absolute or relative to the
            file path provided.
            case_suffix (str): Suffix to append to the case name. Defaults to ''.
        """

        self.model_files.write_out_case(new_file_path=new_file_path,
                                        new_include_file_location=new_include_file_location,
                                        case_suffix=case_suffix)

    def update_simulator_files(self) -> None:
        """Updates the simulator with any changes to the included files. Overwrites existing files.

        IMPORTANT: No changes to the model will be saved until this method is called!
        """

        self.model_files.update_model_files()

    def move_simulator_files(self, new_file_path: str, new_include_file_location: str,
                             overwrite_files: bool = False) -> None:
        """Creates a set of simulator files.

        Args:
            new_file_path (str): Path to save the new simulator to.
            new_include_file_location (str): Saves included files to a path either absolute or relative to the
            file path provided.
            overwrite_files (bool): Overwrite files if they already exist. Defaults to False.
        """

        self.model_files.move_model_files(new_file_path, new_include_file_location, overwrite_files)

    def write_out_new_model(self, new_location: str, new_model_name: str) -> None:
        """Not implemented for Nexus yet."""
        raise NotImplementedError("Not Implemented Yet")

    @property
    def summary(self) -> str:
        """Returns a summary of the model contents."""

        # Initialize 'fluid_type' to an empty string.
        fluid_type = ''

        # Verify if 'surface_file' is a dictionary.
        if (isinstance(self.model_files.surface_files, dict) and
                # Checks if the first item in 'surface_files'(at index 0) has a valid value and is not none.
                self.model_files.surface_files[0].file_content_as_list is not None):
            # If conditions in lines 857 and 859 are met, get_fluid_type is called to retrieve the fluid type.
            fluid_type = self.get_fluid_type(
                surface_file_content=self.model_files.surface_files[0].file_content_as_list
            )
        list_of_wells = self.wells.get_all()
        list_of_well_names = [well.well_name for well in list_of_wells]
        completions = [len(well.completions) for well in list_of_wells]
        well_summary = [f'{y} has: {z} completions' for y, z in zip(list_of_well_names, completions)]
        model_reporting_date = self.sim_controls.times[-1]
        range_x = None
        range_y = None
        range_z = None
        if self.grid is not None:
            range_x = self.grid.range_x
            range_y = self.grid.range_y
            range_z = self.grid.range_z

        relperm_summary = self.relperm.summary
        pvt_summary = self.pvt.summary
        equil_summary = self.equil.summary
        hyd_summary = self.hydraulics.summary
        model_summary = f"""    Start Date: {self.start_date}
    Last reporting date: {model_reporting_date}
    Grid Dimensions (x y z) : {range_x} x {range_y} x {range_z}
    Well summary: Well names: {well_summary}
    Fluid type: {fluid_type}
    Relperm:
        {relperm_summary.strip()}
    PVT:
        {pvt_summary.strip()}
    Hydraulics:
        {hyd_summary.strip()}
    Equil:
        {equil_summary.strip()}
    """
        return model_summary

    @property
    def sim_controls(self) -> SimControls:
        """Returns an instance of Sim controls class."""
        return self._sim_controls

    @property
    def options(self) -> NexusOptions | None:
        """Returns an instance of Nexus options class."""
        return self._options
