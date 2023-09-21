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

from ResSimpy.Utils.factory_methods import get_empty_dict_int_nexus_file, get_empty_list_str, \
    get_empty_list_nexus_file
from ResSimpy.Nexus.NexusKeywords.fcs_keywords import FCS_KEYWORDS
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.generic_repr import generic_repr
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
            self, location: Optional[str] = None,
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
        return generic_repr(self)

    @classmethod
    def generate_fcs_structure(cls, fcs_file_path: str, recursive: bool = True) -> Self:
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
        fcs_file.include_objects = get_empty_list_nexus_file()
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
            value = nfo.get_token_value(key, line, flat_fcs_file_content[i::])
            if value is None:
                warnings.warn(f'No value found for {key}, skipping file')
                continue
            # TODO handle methods / sets instead of getting full file path
            if key in cls.fcs_keyword_map_multi():
                # for keywords that have multiple methods we store the value in a dictionary
                # with the method number and the NexusFile object
                _, method_string, method_number, value = (
                    nfo.get_multiple_sequential_values(flat_fcs_file_content[i::], 4)
                )
                full_file_path = nfo.get_full_file_path(value, origin_path)
                nexus_file = NexusFile.generate_file_include_structure(
                    value, origin=fcs_file_path, recursive=recursive, top_level_file=True)
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
                nexus_file = NexusFile.generate_file_include_structure(
                    value, origin=fcs_file_path, recursive=recursive, top_level_file=True)
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
        single_keywords = {k: (v, type(NexusFile)) for k, v in FcsNexusFile.fcs_keyword_map_single().items()}
        multi_keywords = {k: (v, type(dict)) for k, v in FcsNexusFile.fcs_keyword_map_multi().items()}
        return_dict = dict(single_keywords, **multi_keywords)
        return return_dict

    def update_model_files(self, new_file_path: None | str = None, new_include_file_location: None | str = None,
                           write_out_all_files: bool = False, preserve_file_names: bool = False,
                           overwrite_include_files: bool = False) -> None:
        """Updates all the modified files as well as the fcs file if a new file has been created.

        Args:
            new_file_path (None | str): Defaults to None. If None overwrites the original file.
            If string it will save the file in the path provided.
            new_include_file_location (None | str): Defaults to None. If None saves in the same directory as the fcs \
            file. Otherwise saves it to a path either absolute or relative to the file path provided.
            write_out_all_files (bool): Defaults to False. If False writes out only changed files.
            If False writes out all files.
            preserve_file_names (bool): Defaults to False. If True will derive names from the existing fcs_file.
            If False will derive new names from the new fcs file name and the property it represents in Nexus.
            overwrite_include_files (bool): Defaults to False. If True will overwrite the included files.
        """
        # Take the original file, find which files have changed and write out those locations

        if new_file_path is not None:
            file_location = new_file_path
            new_fcs_name = os.path.basename(new_file_path).replace('.fcs', '')
        else:
            file_location = self.location if self.location is not None else 'new_fcs.fcs'
            new_fcs_name = os.path.basename(file_location).replace('.fcs', '')

        # figure out where to store the include files:
        # by default store it in the same directory as the new fcs file.
        file_directory = os.path.dirname(file_location)
        if new_include_file_location is not None:
            file_directory = new_include_file_location
        # Loop through all files in the model, writing out the contents if they have been modified.
        for keyword, attr_name in self.fcs_keyword_map_single().items():
            file: None | NexusFile = getattr(self, attr_name, None)
            if file is None:
                # skip if there is no file
                continue
            self.write_out_included_file(file, attr_name, file_directory, keyword, new_fcs_name,
                                         method_number=None, write_out_all_files=write_out_all_files,
                                         preserve_file_names=preserve_file_names,
                                         overwrite_file=overwrite_include_files)

        for keyword, attr_name in self.fcs_keyword_map_multi().items():
            file_dict: None | dict[int, NexusFile] = getattr(self, attr_name, None)
            if file_dict is None or len(file_dict) == 0:
                continue
            for method_number, file in file_dict.items():
                self.write_out_included_file(file, attr_name, file_directory, keyword, new_fcs_name, method_number,
                                             write_out_all_files, preserve_file_names,
                                             overwrite_file=overwrite_include_files)

        # write out the final fcs file
        self.write_to_file(file_location, write_includes=False)

    def write_out_included_file(self, file: NexusFile, attr_name: str, file_directory: str, keyword: str,
                                new_fcs_name: str, method_number: None | int = None, write_out_all_files: bool = False,
                                preserve_file_names: bool = False, overwrite_file: bool = False) -> None:
        """Writes out the included file and prepares to switch out the path in the fcs file.

        Args:
            file (NexusFile): file to write out
            attr_name (str): attribute name of the method to be replaced
            file_directory (str): path to directory the file should be stored in
            keyword (str): Nexus keyword for the type of method.
            new_fcs_name (str): new file name for the fcs
            method_number (None | int): method number to include in the file name (defaults to None)
            preserve_file_names (bool): Defaults to False. If True will derive names from the existing fcs_file.
            If False will derive new names from the new fcs file name and the property it represents in Nexus.
            overwrite_file (bool): Defaults to False. If True will overwrite the file.
        """
        if not file.file_modified and not write_out_all_files:
            return
            # write the modified files out
        if method_number is not None:
            attr_name += f'_{str(method_number)}'
            attr_name = attr_name.replace('files', 'method')
        if overwrite_file and file.location is not None:
            file_path_to_write_to = file.location
        elif preserve_file_names and file.location is not None:
            new_file_name = os.path.basename(file.location)
            file_path_to_write_to = os.path.join(file_directory, new_file_name)
        else:
            new_file_name = f"{new_fcs_name}_{attr_name}.dat"
            file_path_to_write_to = os.path.join(file_directory, new_file_name)

        file.write_to_file(file_path_to_write_to, write_includes=True, write_out_all_files=write_out_all_files)
        # update them in the fcs file_as_list
        fcs_changed = self.change_file_path(file_path_to_write_to, keyword, method_number)
        self._file_modified_set(fcs_changed)

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
                    = nfo.get_multiple_sequential_values([line], 4)
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
        return file_changed
