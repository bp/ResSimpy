"""File object for handling FCS top level files for Nexus."""
from __future__ import annotations
from dataclasses import dataclass, field
import os
import warnings

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from typing import Optional

# Use correct Self type depending upon Python version
import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ResSimpy.Utils.factory_methods import get_empty_dict_int_nexus_file, get_empty_list_str, get_empty_list_file
from ResSimpy.Nexus.NexusKeywords.fcs_keywords import FCS_KEYWORDS
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Utils.generic_repr import generic_str
from datetime import datetime


@dataclass(kw_only=True)
class FcsNexusFile(NexusFile):
    restart_file: Optional[NexusFile] = None
    structured_grid_file: Optional[NexusFile] = None
    options_file: Optional[NexusFile] = None
    runcontrol_file: Optional[NexusFile] = None
    override_file: Optional[NexusFile] = None
    eos_default_file: Optional[NexusFile] = None
    well_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    surface_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    rock_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    relperm_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    pvt_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    water_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    equil_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    tracer_init_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    aquifer_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    hyd_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    valve_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    separator_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    ipr_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    gas_lift_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    pump_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    compressor_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    choke_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    icd_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    esp_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    polymer_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    adsorption_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    flux_in_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    files_info: list[tuple[Optional[str], Optional[str], Optional[datetime]]]

    def __init__(
            self, location: str,
            include_locations: Optional[list[str]] = None,
            origin: Optional[str] = None,
            include_objects: Optional[list[NexusFile]] = None,
            file_content_as_list: Optional[list[str]] = None,
            restart_file: Optional[NexusFile] = None,
            structured_grid_file: Optional[NexusFile] = None,
            options_file: Optional[NexusFile] = None,
            runcontrol_file: Optional[NexusFile] = None,
            override_file: Optional[NexusFile] = None,
            eos_default_file: Optional[NexusFile] = None,
            well_files: Optional[dict[int, NexusFile]] = None,
            surface_files: Optional[dict[int, NexusFile]] = None,
            rock_files: Optional[dict[int, NexusFile]] = None,
            relperm_files: Optional[dict[int, NexusFile]] = None,
            pvt_files: Optional[dict[int, NexusFile]] = None,
            water_files: Optional[dict[int, NexusFile]] = None,
            equil_files: Optional[dict[int, NexusFile]] = None,
            tracer_init_files: Optional[dict[int, NexusFile]] = None,
            aquifer_files: Optional[dict[int, NexusFile]] = None,
            hyd_files: Optional[dict[int, NexusFile]] = None,
            valve_files: Optional[dict[int, NexusFile]] = None,
            separator_files: Optional[dict[int, NexusFile]] = None,
            ipr_files: Optional[dict[int, NexusFile]] = None,
            gas_lift_files: Optional[dict[int, NexusFile]] = None,
            pump_files: Optional[dict[int, NexusFile]] = None,
            compressor_files: Optional[dict[int, NexusFile]] = None,
            choke_files: Optional[dict[int, NexusFile]] = None,
            icd_files: Optional[dict[int, NexusFile]] = None,
            esp_files: Optional[dict[int, NexusFile]] = None,
            polymer_files: Optional[dict[int, NexusFile]] = None,
            adsorption_files: Optional[dict[int, NexusFile]] = None,
            flux_in_files: Optional[dict[int, NexusFile]] = None
    ) -> None:
        """Initialises the FcsNexusFile class.

        Args:
            location: str: The file path to the fcs file.
            include_locations: Optional[list[str]]: list of file paths to the included files.
            origin: Optional[str]: The file path to the file that included this file. None for top level files.
            include_objects: Optional[list[NexusFile]: list of NexusFile objects that are included in this file.
            file_content_as_list: Optional[list[str]]: list of strings representing the content of the file.
            restart_file: Optional[NexusFile]: The restart file for the fcs file.
            structured_grid_file: Optional[NexusFile]: The structured grid file for the fcs file.
            options_file: Optional[NexusFile]: The options file for the fcs file.
            runcontrol_file: Optional[NexusFile]: The runcontrol file for the fcs file.
            override_file: Optional[NexusFile]: The override file for the fcs file.
            eos_default_file: Optional[NexusFile]: The eos default file for the fcs file.
            well_files: Optional[dict[int, NexusFile]: Collection of well files for the fcs file. Indexed by method
            number.
            surface_files: Optional[dict[int, NexusFile]: Collection of surface files for the fcs file. Indexed by
            method number.
            rock_files: Optional[dict[int, NexusFile]: Collection of rock files for the fcs file. Indexed by method
            number.
            relperm_files: Optional[dict[int, NexusFile]: Collection of relperm files for the fcs file. Indexed by
            method number.
            pvt_files: Optional[dict[int, NexusFile]: Collection of pvt files for the fcs file. Indexed by method
            number.
            water_files: Optional[dict[int, NexusFile]: Collection of water files for the fcs file. Indexed by method
            number.
            equil_files: Optional[dict[int, NexusFile]: Collection of equil files for the fcs file. Indexed by method
            number.
            tracer_init_files: Optional[dict[int, NexusFile]: Collection of tracer init files for the fcs file. Indexed
            by method number.
            aquifer_files: Optional[dict[int, NexusFile]: Collection of aquifer files for the fcs file. Indexed by
            method number.
            hyd_files: Optional[dict[int, NexusFile]: Collection of hyd files for the fcs file. Indexed by method
            number.
            valve_files: Optional[dict[int, NexusFile]: Collection of valve files for the fcs file. Indexed by method
            number.
            separator_files: Optional[dict[int, NexusFile]: Collection of separator files for the fcs file. Indexed by
            method number.
            ipr_files: Optional[dict[int, NexusFile]: Collection of ipr files for the fcs file. Indexed by method
            number.
            gas_lift_files: Optional[dict[int, NexusFile]: Collection of gas lift files for the fcs file. Indexed by
            method number.
            pump_files: Optional[dict[int, NexusFile]: Collection of pump files for the fcs file. Indexed by method
            number.
            compressor_files: Optional[dict[int, NexusFile]: Collection of compressor files for the fcs file. Indexed by
            method number.
            choke_files: Optional[dict[int, NexusFile]: Collection of choke files for the fcs file. Indexed by method
            number.
            icd_files: Optional[dict[int, NexusFile]: Collection of icd files for the fcs file. Indexed by method
            number.
            esp_files: Optional[dict[int, NexusFile]: Collection of esp files for the fcs file. Indexed by method
            number.
            polymer_files: Optional[dict[int, NexusFile]: Collection of polymer files for the fcs file. Indexed by
            method number.
            adsorption_files: Optional[dict[int, NexusFile]: Collection of adsorption files for the fcs file. Indexed by
            method number.
            flux_in_files: Optional[dict[int, NexusFile]: Collection of flux in files for the fcs file. Indexed by
            method number.
        """
        self.restart_file = restart_file

        self.structured_grid_file = structured_grid_file
        self.options_file = options_file
        self.runcontrol_file = runcontrol_file
        self.override_file = override_file
        self.eos_default_file = eos_default_file
        self.surface_files = surface_files
        self.well_files = well_files if well_files is not None else get_empty_dict_int_nexus_file()
        self.rock_files = rock_files if rock_files is not None else get_empty_dict_int_nexus_file()
        self.relperm_files = relperm_files if relperm_files is not None else get_empty_dict_int_nexus_file()
        self.pvt_files = pvt_files if pvt_files is not None else get_empty_dict_int_nexus_file()
        self.water_files = water_files if water_files is not None else get_empty_dict_int_nexus_file()
        self.equil_files = equil_files if equil_files is not None else get_empty_dict_int_nexus_file()
        self.tracer_init_files = tracer_init_files if tracer_init_files is not None else get_empty_dict_int_nexus_file()
        self.aquifer_files = aquifer_files if aquifer_files is not None else get_empty_dict_int_nexus_file()
        self.hyd_files = hyd_files if hyd_files is not None else get_empty_dict_int_nexus_file()
        self.valve_files = valve_files if valve_files is not None else get_empty_dict_int_nexus_file()
        self.separator_files = separator_files if separator_files is not None else get_empty_dict_int_nexus_file()
        self.ipr_files = ipr_files if ipr_files is not None else get_empty_dict_int_nexus_file()
        self.gas_lift_files = gas_lift_files if gas_lift_files is not None else get_empty_dict_int_nexus_file()
        self.pump_files = pump_files if pump_files is not None else get_empty_dict_int_nexus_file()
        self.compressor_files = compressor_files if compressor_files is not None else get_empty_dict_int_nexus_file()
        self.choke_files = choke_files if choke_files is not None else get_empty_dict_int_nexus_file()
        self.icd_files = icd_files if icd_files is not None else get_empty_dict_int_nexus_file()
        self.esp_files = esp_files if esp_files is not None else get_empty_dict_int_nexus_file()
        self.polymer_files = polymer_files if polymer_files is not None else get_empty_dict_int_nexus_file()
        self.adsorption_files = adsorption_files if adsorption_files is not None else get_empty_dict_int_nexus_file()
        self.flux_in_files = flux_in_files if flux_in_files is not None else get_empty_dict_int_nexus_file()
        self.files_info = []
        super().__init__(location=location, include_locations=include_locations, origin=origin,
                         include_objects=include_objects, file_content_as_list=file_content_as_list)

    def __repr__(self) -> str:
        printable_str = f'fcs file location: {self.location}\n'
        printable_str += '\tFCS file contains:\n'
        for file_type in self.fcs_keyword_map_single().values():
            if getattr(self, file_type) is not None:
                printable_str += f'\t\t{file_type}: {getattr(self, file_type).location}\n'
        for multi_file_type in self.fcs_keyword_map_multi().values():
            multi_file_list = getattr(self, multi_file_type, None)
            if multi_file_list is not None and len(multi_file_list) > 0:
                printable_str += f'\t\t{multi_file_type}: {len(multi_file_list)}\n'
        return printable_str

    def __str__(self) -> str:
        return generic_str(self)

    @classmethod
    def generate_fcs_structure(cls: type[Self], fcs_file_path: str, recursive: bool = True) -> Self:
        """Creates an instance of the FcsNexusFile, populates it through looking through the different keywords \
            in the FCS and assigning the paths to objects.

        Args:
        ----
            fcs_file_path (str): path to the fcs file of interest
            recursive (bool, optional): Whether the NexusFile structure will be recursively created. Defaults to True.

        Raises:
        ------
            FileNotFoundError: if the fcs file cannot be found
            ValueError: if no content can be found within the fcsfile

        Returns:
        -------
            FcsNexusFile: instance of a FcsNexusFile for a given fcs file path
        """
        fcs_file = cls(location=fcs_file_path)
        fcs_file.include_objects = get_empty_list_file()
        fcs_file.file_content_as_list = get_empty_list_str()
        fcs_file.include_locations = get_empty_list_str()

        # guard against bad links/empty files:
        if not os.path.isfile(fcs_file_path):
            raise FileNotFoundError(f'fcs file not found for path {fcs_file_path}')
        origin_path = fcs_file_path
        fcs_nexus_file = NexusFile.generate_file_include_structure(
            fcs_file_path, origin=None)
        fcs_file.files_info.append((fcs_nexus_file.location, fcs_nexus_file.linked_user,
                                    fcs_nexus_file.last_modified))

        fcs_file.linked_user = fcs_nexus_file.linked_user
        fcs_file.last_modified = fcs_nexus_file.last_modified

        flat_fcs_file_content = fcs_nexus_file.get_flat_list_str_file
        if flat_fcs_file_content is None or fcs_file.file_content_as_list is None:
            raise ValueError(f'FCS file not found, no content for {fcs_file_path=}')
        fcs_file.file_content_as_list = flat_fcs_file_content
        for i, line in enumerate(flat_fcs_file_content):
            if not nfo.nexus_token_found(line, valid_list=FCS_KEYWORDS):
                continue
            key = nfo.get_next_value(start_line_index=i, file_as_list=flat_fcs_file_content, search_string=line)
            if key is None:
                warnings.warn(f'get next value failed to find a suitable token in {line}')
                continue
            key = key.upper()
            value = fo.get_token_value(key, line, flat_fcs_file_content[i::])
            if value is None:
                warnings.warn(f'No value found for {key}, skipping file')
                continue
            # TODO handle methods / sets instead of getting full file path
            if key in cls.fcs_keyword_map_multi():
                # for keywords that have multiple methods we store the value in a dictionary
                # with the method number and the NexusFile object
                _, method_string, method_number, value = (
                    fo.get_multiple_expected_sequential_values(flat_fcs_file_content[i::], 4, ['NORPT'])
                )
                full_file_path = nfo.get_full_file_path(value, origin_path)
                nexus_file = NexusFile.generate_file_include_structure(
                    file_path=value, origin=fcs_file_path, recursive=recursive, top_level_file=True)
                fcs_property = getattr(fcs_file, cls.fcs_keyword_map_multi()[key])
                # manually initialise if the property is still a None after class instantiation
                if fcs_property is None:
                    fcs_property = get_empty_dict_int_nexus_file()
                # shallow copy to maintain list elements pointing to nexus_file that are
                # stored in the file_content_as_list
                fcs_property_list = fcs_property.copy()
                fcs_property_list.update({int(method_number): nexus_file})
                # set the attribute in the FcsNexusFile instance
                setattr(fcs_file, cls.fcs_keyword_map_multi()[key], fcs_property_list)
                fcs_file.include_objects.append(nexus_file)
                fcs_file.include_locations.append(full_file_path)
                fcs_file.files_info.append((nexus_file.location, nexus_file.linked_user,
                                            nexus_file.last_modified))
            elif key in cls.fcs_keyword_map_single():
                full_file_path = nfo.get_full_file_path(value, origin_path)
                skip_arrays = True if key == 'STRUCTURED_GRID' else False
                nexus_file = NexusFile.generate_file_include_structure(
                    file_path=value, origin=fcs_file_path, recursive=recursive, top_level_file=True,
                    skip_arrays=skip_arrays)
                setattr(fcs_file, cls.fcs_keyword_map_single()[key], nexus_file)
                fcs_file.include_objects.append(nexus_file)
                fcs_file.include_locations.append(full_file_path)
                fcs_file.files_info.append((nexus_file.location, nexus_file.linked_user,
                                            nexus_file.last_modified))
            else:
                continue
        return fcs_file

    @staticmethod
    def fcs_keyword_map_single() -> dict[str, str]:
        """Returns mapping of fcs keywords to single file categories."""
        keyword_map = {
            'STRUCTURED_GRID': 'structured_grid_file',
            'OPTIONS': 'options_file',
            'RUNCONTROL': 'runcontrol_file',
            'OVERRIDE': 'override_file',
            'EOS_DEFAULTS': 'eos_default_file',
        }
        return keyword_map

    @staticmethod
    def fcs_keyword_map_multi() -> dict[str, str]:
        """Returns mapping of fcs keywords to file multiple file categories."""
        keyword_map = {
            'EQUIL': 'equil_files',
            'ROCK': 'rock_files',
            'RELPM': 'relperm_files',
            'SURFACE': 'surface_files',
            'WELLS': 'well_files',
            'PVT': 'pvt_files',
            'AQUIFER': 'aquifer_files',
            'HYD': 'hyd_files',
            'VALVE': 'valve_files',
            'WATER': 'water_files',
            'SEPARATOR': 'separator_files',
            'IPR': 'ipr_files',
            'GASLIFT': 'gas_lift_files',
            'PUMP': 'pump_files',
            'COMPRESSOR': 'compressor_files',
            'CHOKE': 'choke_files',
            'ICD': 'icd_files',
            'ESP': 'esp_files',
            'POLYMER': 'polymer_files',
            'ADSORPTION': 'adsorption_files',
            'FLUXIN': 'flux_in_files',
            'TRACER_INIT': 'tracer_init_files',
        }
        return keyword_map

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns mapping of keywords to attribute definitions."""
        single_keywords = {k: (v, type(NexusFile)) for k, v in FcsNexusFile.fcs_keyword_map_single().items()}
        multi_keywords = {k: (v, type(dict)) for k, v in FcsNexusFile.fcs_keyword_map_multi().items()}
        return_dict = dict(single_keywords, **multi_keywords)
        return return_dict

    def move_model_files(self, new_file_path: str, new_include_file_location: str, overwrite_files: bool = False) -> \
            None:
        """Moves all the model files to a new location.

        Args:
            new_file_path (str): new file path for the fcs file e.g. /new_path/new_fcs_file.fcs
            new_include_file_location (str): new location for the included files either absolute or relative
            to the new fcs file path
            overwrite_files (bool): whether to overwrite the files if they already exist in the new location
        """
        # Take the original file, find which files have changed and write out those locations
        # figure out where to store the include files:
        file_directory = os.path.dirname(new_file_path)
        include_dir = new_include_file_location
        if not os.path.isabs(new_include_file_location):
            include_dir = os.path.join(file_directory, new_include_file_location)

        if not os.path.exists(include_dir):
            # make the folders if they don't already exist
            os.makedirs(include_dir)

        # Loop through all files in the model, writing out the contents
        for keyword, attr_name in self.fcs_keyword_map_single().items():
            file: None | NexusFile = getattr(self, attr_name, None)
            if file is None:
                # skip if there is no file
                continue
            include_name = os.path.join(include_dir, os.path.basename(file.location))
            file.write_to_file(include_name, write_includes=True, write_out_all_files=True,
                               overwrite_file=overwrite_files)
            self.change_file_path(include_name, keyword)

        for keyword, attr_name in self.fcs_keyword_map_multi().items():
            file_dict: None | dict[int, NexusFile] = getattr(self, attr_name, None)
            if file_dict is None or len(file_dict) == 0:
                continue
            for method_number, file in file_dict.items():
                include_name = os.path.join(include_dir, os.path.basename(file.location))
                file.write_to_file(include_name, write_includes=True, write_out_all_files=True,
                                   overwrite_file=overwrite_files)
                self.change_file_path(include_name, keyword, method_number)

        # write out the final fcs file
        self.write_to_file(new_file_path, write_includes=False, overwrite_file=overwrite_files)

    def write_out_case(self, new_file_path: str, new_include_file_location: str, case_suffix: str) -> None:
        """Writes out a new simulator with only modified files. For use with creating multiple cases from a base case.

        Args:
            new_file_path (str): new file path for the fcs file e.g. /new_path/new_fcs_file.fcs
            new_include_file_location (str): new location for the included files either absolute or relative
            to the new fcs file path
            case_suffix (str): suffix to append to the end of the file name e.g. case_1
        """

        def new_include_file_name(file_name: str) -> str:
            """Returns the new include file name based on the original file name plus the suffix provided."""
            file_name = os.path.basename(file_name)
            file_name, file_extension = os.path.splitext(file_name)
            file_name = f'{file_name}_{case_suffix}{file_extension}'
            return os.path.join(new_include_file_location, file_name)

        file_directory = os.path.dirname(new_file_path)
        include_dir = new_include_file_location
        if not os.path.isabs(new_include_file_location):
            include_dir = os.path.join(file_directory, new_include_file_location)

        if not os.path.exists(include_dir):
            # make the folders if they don't already exist
            os.makedirs(include_dir)

        # Loop through all files in the model, writing out the contents
        for keyword, attr_name in self.fcs_keyword_map_single().items():
            file: None | NexusFile = getattr(self, attr_name, None)
            if file is None:
                # skip if there is no file
                continue
            include_write_name = file.location
            if file.file_modified:
                include_write_name = new_include_file_name(file.location)
                file.write_to_file(include_write_name, write_includes=True, write_out_all_files=False)
            self.change_file_path(include_write_name, keyword)

        for keyword, attr_name in self.fcs_keyword_map_multi().items():
            file_dict: None | dict[int, NexusFile] = getattr(self, attr_name, None)
            if file_dict is None or len(file_dict) == 0:
                continue
            for method_number, file in file_dict.items():
                include_write_name = file.location
                if file.file_modified:
                    include_write_name = new_include_file_name(file.location)
                    file.write_to_file(include_write_name, write_includes=True, write_out_all_files=False)
                self.change_file_path(include_write_name, keyword, method_number)
        self.write_to_file(new_file_path, write_includes=False)

    def update_model_files(self) -> None:
        """Updates all the modified files in the model. Keeps file names and paths the same.

        Warning: this method overwrites the existing files!
        """
        # Loop through all files in the model, writing out the contents if they have been modified.
        for keyword, attr_name in self.fcs_keyword_map_single().items():
            file: None | NexusFile = getattr(self, attr_name, None)
            if file is None:
                # skip if there is no file
                continue
            if file.file_modified:
                file.write_to_file(write_includes=True, write_out_all_files=False, overwrite_file=True)

        for keyword, attr_name in self.fcs_keyword_map_multi().items():
            file_dict: None | dict[int, NexusFile] = getattr(self, attr_name, None)
            if file_dict is None or len(file_dict) == 0:
                continue
            for method_number, file in file_dict.items():
                if file.file_modified:
                    file.write_to_file(write_includes=True, write_out_all_files=False, overwrite_file=True)

    def change_file_path(self, new_file_path: str, token: str, method_number: int | None = None) -> bool:
        """Switch the file path for a new file_path based on the value of the associated keyword in the fcs.

        Args:
            new_file_path (str): file path to replace the existing file path with.
            token (str): token indicating the
            method_number (int | None): method number for the file to replace.
            If None then will only look for keywords that follow directly after a token
        Returns:
            (bool): representing whether the file was successfully changed
        """
        file_changed = False
        if self.file_content_as_list is None:
            raise ValueError('No file content to change file path on.')
        for index, line in enumerate(self.get_flat_list_str_file):
            if not nfo.check_token(token, line):
                continue

            if method_number is not None:
                token_from_file, intermediate_word, method_num_in_file, path_to_replace \
                    = fo.get_multiple_expected_sequential_values([line], 4, ['NORPT'])
                if int(method_num_in_file) != method_number:
                    continue
            else:
                path_to_replace = nfo.get_expected_token_value(token, line, self.get_flat_list_str_file)
            # edit the file as list
            file_to_edit, index_to_mod = self.find_which_include_file(flattened_index=index)
            if file_to_edit.file_content_as_list is None:
                raise ValueError(f'No content found within {file_to_edit.location}')
            file_to_edit.file_content_as_list[index_to_mod] = line.replace(path_to_replace, new_file_path)
            file_changed = True
            self._file_modified_set(file_changed)
        return file_changed
