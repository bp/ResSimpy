from dataclasses import dataclass, field
import os

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from typing import Optional, Union, Generator
from ResSimpy.Utils.factory_methods import get_empty_list_str, get_empty_list_nexus_file, get_empty_list_str_nexus_file
from ResSimpy.Nexus.nexus_constants import INTERMEDIATE_KEYWORDS, STARTING_KEYWORDS, FCS_KEYWORDS
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)
class FcsNexusFile(NexusFile):
    restart_file: Optional[NexusFile] = None
    structured_grid_file: Optional[NexusFile] = None
    options_file: Optional[NexusFile] = None
    runcontrol_file: Optional[NexusFile] = None
    surface_file: Optional[NexusFile] = None
    well_file: Optional[NexusFile] = None
    rock_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    relperm_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    pvt_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    water_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    equil_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    aquifer_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)
    hyd_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file)

    def __init__(self, location: Optional[str] = None,
                 includes: Optional[list[str]] = field(default_factory=get_empty_list_str),
                 origin: Optional[str] = None,
                 includes_objects: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 file_content_as_list: Optional[list[Union[str, NexusFile]]] =
                 field(default_factory=get_empty_list_str_nexus_file),
                 restart_file: Optional[NexusFile] = None,
                 structured_grid_file: Optional[NexusFile] = None,
                 options_file: Optional[NexusFile] = None,
                 runcontrol_file: Optional[NexusFile] = None,
                 surface_file: Optional[NexusFile] = None,
                 well_file: Optional[NexusFile] = None,
                 rock_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 relperm_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 pvt_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 water_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 equil_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 aquifer_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 hyd_files: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
                 ):
        self.restart_file = restart_file
        self.structured_grid_file = structured_grid_file
        self.options_file = options_file
        self.runcontrol_file = runcontrol_file
        self.surface_file = surface_file
        self.well_file = well_file
        self.rock_files = rock_files
        self.relperm_files = relperm_files
        self.pvt_files = pvt_files
        self.water_files = water_files
        self.equil_files = equil_files
        self.aquifer_files = aquifer_files
        self.hyd_files = hyd_files
        super().__init__(location=location, includes=includes, origin=origin, includes_objects=includes_objects,
                         file_content_as_list=file_content_as_list)

    @classmethod
    def generate_fcs_structure(cls, fcs_file_path: str, recursive: bool = True):
        fcs_tokens = FCS_KEYWORDS
        fcs_file = cls(location=fcs_file_path)
        fcs_file.includes_objects = get_empty_list_nexus_file()
        fcs_file.file_content_as_list = get_empty_list_str_nexus_file()
        equil = None
        structured_grid_file = None
        options = None
        rock = None
        relpms = None

        fcs_keyword_map = {
            'EQUIL': equil,
            'STRUCTURED_GRID': structured_grid_file,
            'OPTIONS': options,
            'ROCK': rock,
            'RELPM': relpms,
        }

        if not os.path.isfile(fcs_file_path):
            raise FileNotFoundError(f'fcs file not found for path {fcs_file_path}')
        flat_fcs_file_content = NexusFile.generate_file_include_structure(
            fcs_file_path, origin=None).get_flat_list_str_file()
        if flat_fcs_file_content is None:
            raise ValueError(f'FCS file not found, no content for {fcs_file_path=}')
        for line in flat_fcs_file_content:
            if nfo.check_token('STRUCTURED_GRID', line):
                value = nfo.get_token_value('STRUCTURED_GRID', line, flat_fcs_file_content)
                if value is not None:
                    structured_grid_path = nfo.get_full_file_path(value, fcs_file_path)
                    fcs_file.structured_grid_file = NexusFile.generate_file_include_structure(
                        structured_grid_path, origin=fcs_file_path)
                    fcs_file.includes_objects.append(fcs_file.structured_grid_file)
                    fcs_file.file_content_as_list.extend(cls.line_as_nexus_list(
                        line, value, fcs_file.structured_grid_file))
            elif nfo.check_token('OPTIONS', line):
                value = nfo.get_token_value('OPTIONS', line, flat_fcs_file_content)
                if value is not None:
                    options_path = nfo.get_full_file_path(value, fcs_file_path)
                    fcs_file.options_file = NexusFile.generate_file_include_structure(
                        options_path, origin=fcs_file_path,)
                    fcs_file.includes_objects.append(fcs_file.options_file)
                    fcs_file.file_content_as_list.extend(cls.line_as_nexus_list(
                        line, value, fcs_file.options_file))
            else:
                fcs_file.file_content_as_list.append(line.replace('\n', ''))
        return fcs_file

    @staticmethod
    def line_as_nexus_list(line: str, path: str, nexus_obj: NexusFile) -> list[Union[str, NexusFile]]:
        """split out a line into the start and finish and inserts a NexusFile object into the place of the path.

        Args:
            line (str): line to split apart (containing path)
            path (str): path to remove from the line
            nexus_obj (NexusFile): NexusFile instance to replace the path with

        Returns:
            list[Union[str, NexusFile]]: list of the format [prefix, NexusFile, suffix] where the NexusFile object is \
            in place of the path provided
        """
        new_list = []
        prefix = line.split(path, 1)[0]
        new_list.append(prefix)
        new_list.append(nexus_obj)
        suffix = line.split(path, 1)[-1]
        new_list.append(suffix.replace('\n', ''))
        return new_list
