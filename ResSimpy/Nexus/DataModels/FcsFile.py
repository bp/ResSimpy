from dataclasses import Field, dataclass, field
import os
import warnings

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from typing import Optional, Union
from ResSimpy.Utils.factory_methods import get_empty_dict_int_nexus_file, get_empty_list_str,\
    get_empty_list_nexus_file, get_empty_list_str_nexus_file
from ResSimpy.Nexus.nexus_constants import FCS_KEYWORDS
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)
class FcsNexusFile(NexusFile):
    restart_file: Optional[NexusFile] = None
    structured_grid_file: Optional[NexusFile] = None
    options_file: Optional[NexusFile] = None
    runcontrol_file: Optional[NexusFile] = None
    override_file: Optional[NexusFile] = None
    eos_default_file: Optional[NexusFile] = None
    well_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    surface_file: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    rock_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    relperm_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    pvt_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    water_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    equil_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    aquifer_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
    hyd_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)
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
    tracer_init_file: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file)

    def __init__(
        self, location: Optional[str] = None,
        includes: Optional[list[str]] = field(default_factory=get_empty_list_str),
        origin: Optional[str] = None,
        includes_objects: Optional[list[NexusFile]] = field(default_factory=get_empty_list_nexus_file),
        file_content_as_list: Optional[list[Union[str, NexusFile]]] = field(
            default_factory=get_empty_list_str_nexus_file),
        restart_file: Optional[NexusFile] = None,
        structured_grid_file: Optional[NexusFile] = None,
        options_file: Optional[NexusFile] = None,
        runcontrol_file: Optional[NexusFile] = None,
        override_file: Optional[NexusFile] = None,
        eos_default_file: Optional[NexusFile] = None,
        well_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        surface_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        rock_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        relperm_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        pvt_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        water_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        equil_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        aquifer_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        hyd_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        separator_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        ipr_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        gas_lift_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        pump_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        compressor_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        choke_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        icd_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        esp_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        polymer_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        adsorption_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        flux_in_files: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
        tracer_init_file: Optional[dict[int, NexusFile]] = field(default_factory=get_empty_dict_int_nexus_file),
    ):
        self.restart_file = restart_file
        self.structured_grid_file = structured_grid_file
        self.options_file = options_file
        self.runcontrol_file = runcontrol_file
        self.override_file = override_file
        self.eos_default_file = eos_default_file
        self.surface_file = surface_files
        self.well_files = well_files
        self.rock_files = rock_files
        self.relperm_files = relperm_files
        self.pvt_files = pvt_files
        self.water_files = water_files
        self.equil_files = equil_files
        self.aquifer_files = aquifer_files
        self.hyd_files = hyd_files
        self.separator_files = separator_files
        self.ipr_files = ipr_files
        self.gas_lift_files = gas_lift_files
        self.pump_files = pump_files
        self.compressor_files = compressor_files
        self.choke_files = choke_files
        self.icd_files = icd_files
        self.esp_files = esp_files
        self.polymer_files = polymer_files
        self.adsorption_files = adsorption_files
        self.flux_in_files = flux_in_files
        self.tracer_init_file = tracer_init_file
        super().__init__(location=location, includes=includes, origin=origin, includes_objects=includes_objects,
                         file_content_as_list=file_content_as_list)

    @classmethod
    def generate_fcs_structure(cls, fcs_file_path: str, recursive: bool = True):
        fcs_file = cls(location=fcs_file_path)
        fcs_file.includes_objects = get_empty_list_nexus_file()
        fcs_file.file_content_as_list = get_empty_list_str_nexus_file()

        fcs_keyword_map_single = {
            'STRUCTURED_GRID': 'structured_grid_file',
            'OPTIONS': 'options_file',
            'RUNCONTROL': 'runcontrol_file',
            'OVERRIDE': 'override_file',
            'EOS_DEFAULTS': 'eos_default_file',
        }
        fcs_keyword_map_multi = {
            'EQUIL': 'equil_files',
            'ROCK': 'rock_files',
            'RELPM': 'relperm_files',
            'SURFACE': 'surface_files',
            'WELLS': 'well_files',
            'PVT': 'pvt_files',
            'AQUIFER': 'aquifer_files',
            'HYD': 'hyd_files',
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

        # guard against bad links/empty files:
        if not os.path.isfile(fcs_file_path):
            raise FileNotFoundError(f'fcs file not found for path {fcs_file_path}')
        flat_fcs_file_content = NexusFile.generate_file_include_structure(
            fcs_file_path, origin=None).get_flat_list_str_file()
        if flat_fcs_file_content is None:
            raise ValueError(f'FCS file not found, no content for {fcs_file_path=}')
        # for key, item in fcs_keyword_map_single.items():
        for i, line in enumerate(flat_fcs_file_content):
            if nfo.nexus_token_found(line, valid_list=FCS_KEYWORDS):
                key = nfo.get_next_value(start_line_index=i, file_as_list=flat_fcs_file_content, search_string=line)
                if key is None:
                    warnings.warn(f'get next value failed to find a suitable token in {line}')
                    continue
                value = nfo.get_token_value(key, line, flat_fcs_file_content[i::])
                if value is None:
                    warnings.warn(f'No value found for {key}, skipping file')
                    continue
                # TODO handle methods / sets instead of getting full file path
                if key in fcs_keyword_map_multi:
                    # for keywords that have multiple methods we store the value in a dictionary
                    # with the method number and the NexusFile object
                    _, method_string, method_number, value = (
                        nfo.get_multiple_sequential_tokens(flat_fcs_file_content[i::], 4)
                    )
                    sub_file_path = nfo.get_full_file_path(value, fcs_file_path)
                    nexus_file = NexusFile.generate_file_include_structure(
                        sub_file_path, origin=fcs_file_path)
                    fcs_property = getattr(fcs_file, fcs_keyword_map_multi[key])
                    if isinstance(fcs_property, Field):
                        fcs_property = get_empty_dict_int_nexus_file()
                    # shallow copy to maintain list elements pointing to nexus_file that are
                    # stored in the file_content_as_list
                    fcs_property_list = fcs_property.copy()
                    fcs_property_list.update({int(method_number): nexus_file})
                    # set the attribute in the fcs_file instance
                    setattr(fcs_file, fcs_keyword_map_multi[key], fcs_property_list)
                    fcs_file.file_content_as_list.extend(cls.line_as_nexus_list(line, value, nexus_file))
                    fcs_file.includes_objects.append(nexus_file)
                elif key in fcs_keyword_map_single:
                    sub_file_path = nfo.get_full_file_path(value, fcs_file_path)
                    nexus_file = NexusFile.generate_file_include_structure(
                        sub_file_path, origin=fcs_file_path)
                    setattr(fcs_file, fcs_keyword_map_single[key], nexus_file)
                    fcs_file.file_content_as_list.extend(cls.line_as_nexus_list(line, value, nexus_file))
                    fcs_file.includes_objects.append(nexus_file)

                # handle include files:
                elif nfo.check_token('INCLUDE', line):
                    sub_file_path = nfo.get_full_file_path(value, fcs_file_path)
                    nexus_file = NexusFile.generate_file_include_structure(
                        sub_file_path, origin=fcs_file_path)
                    fcs_file.includes_objects.append(nexus_file)
                    fcs_file.file_content_as_list.extend(cls.line_as_nexus_list(line, value, nexus_file))
                else:
                    fcs_file.file_content_as_list.append(line.replace('\n', ''))
                    continue
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
