"""Class to hold Nexus relative permeability and capillary pressure properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_TABLE_KEYWORDS, RELPM_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_SINGLE_KEYWORDS, RELPM_HYSTERESIS_PRIMARY_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_KEYWORDS, RELPM_NONDARCY_KEYWORDS, RELPM_NONDARCY_PARAMS
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import RelPermUnits

from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_hysteresis_dict
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusRelPermMethod(DynamicProperty):
    """Class to hold Nexus relative permeability and capillary pressure properties.

    Attributes:
        file (NexusFile): Nexus relperm file object
        input_number (int): RELPM method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific PVT method. Defaults to empty dictionary.
    """

    # General parameters
    file: NexusFile
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                     dict[str, Union[float, pd.DataFrame]]]] = \
        field(default_factory=get_empty_dict_union)
    hysteresis_params: dict[str, Union[str, float, dict[str, Union[str, float, dict[str, Union[str, float]]]]]] \
        = field(default_factory=get_empty_hysteresis_dict)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None,
                 hysteresis_params: Optional[dict[str, Union[str, float, dict[str, Union[str, float,
                                             dict[str, Union[str, float]]]]]]] = None) -> None:
        """Initialises the NexusRelPermMethod class.

        Args:
            file (NexusFile): Nexus file object associated with the relperm method
            input_number (int): method number for the relperm method
            model_unit_system (UnitSystem): unit system from the model
            properties: properties for the relperm method.
            hysteresis_params: hysteresis parameters for the relperm method.
        """
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        if hysteresis_params is not None:
            self.hysteresis_params = hysteresis_params
        else:
            self.hysteresis_params = {}
        self.unit_system = model_unit_system
        super().__init__(input_number=input_number, file=file)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords: dict[str, tuple[str, type]] = {
            'PCWO': ('water_oil_capillary_pressure', float),
            'PCGO': ('gas_oil_capillary_pressure', float),
            'PCGW': ('gas_water_capillary_pressure', float),
            'TENTHR': ('interfacial_tension_threshold_for_relperm_adjustment', float),
            'TENI': ('reference_interfacial_tension_for_capillary_pressure_adjustment', float),
        }
        return keywords

    @property
    def units(self) -> RelPermUnits:
        """Returns the attribute to unit map for the relperm method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return RelPermUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with relative permeability and capillary pressure data, in Nexus file format."""
        printable_str = ''
        # Handle non-hysteresis relperm and capillary pressure parameters
        relperm_dict = self.properties
        stone1_options = {'STONE1': ['SOMOPT1', 'SOMOPT2', 'SOMOPT3', 'ST1EXP', 'ST1EPS', 'ST1NU'],
                          'STONE1_WAT': ['SWMOPT1', 'SWMOPT2']}
        for key, value in relperm_dict.items():
            if isinstance(value, pd.DataFrame):
                table_text = f'{key}'
                if key == 'WOTABLE':
                    if 'LOW_SAL' in relperm_dict.keys():
                        table_text += " LOW_SAL"
                printable_str += f'{table_text}\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n\n'
            elif key in ['STONE1', 'STONE1_WAT']:
                printable_str += f'{key}'
                for stone1_key in stone1_options[key]:
                    if stone1_key in relperm_dict.keys():
                        if relperm_dict[stone1_key] == '':
                            printable_str += f' {stone1_key}'
                        else:
                            printable_str += f' {stone1_key} {relperm_dict[stone1_key]}'
                printable_str += '\n'
            elif key == 'JFUNC':
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
                for jfunc_key in ['PERMBASIS', 'PORBASIS']:
                    if jfunc_key in relperm_dict.keys():
                        printable_str += f'       {jfunc_key} {relperm_dict[jfunc_key]}\n'
            elif key in ['SCALING', 'SCALING_PC', 'IFT', 'NEARCRIT', 'DERIVATIVES']:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
            elif isinstance(value, dict):
                printable_str += f'{key}\n'
                for subkey, subvalue in value.items():
                    printable_str += f'    {subkey} {subvalue}\n'
                if key in RELPM_NONDARCY_KEYWORDS:
                    printable_str += 'END'+key+'\n'
            elif key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key not in ['DESC', 'LOW_SAL', 'STONE1', 'SOMOPT1', 'SOMOPT2', 'SOMOPT3', 'ST1EXP', 'ST1EPS', 'ST1NU',
                             'STONE1_WAT', 'SWMOPT1', 'SWMOPT2', 'PERMBASIS', 'PORBASIS']:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'

        # Handle non-hysteresis relperm and capillary pressure parameters
        hyst_dict = self.hysteresis_params
        key_indx = 0
        for key, value in hyst_dict.items():
            if key_indx == 0:
                printable_str += 'HYSTERESIS'
            else:
                printable_str += '          '
            if value == '':
                printable_str += f' {key}\n'
            elif value == 'USER':
                printable_str += f' {key} USER\n'
            elif isinstance(value, dict):
                printable_str += f' {key}'
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, dict):
                        printable_str += f' {subkey}'
                        for subsubkey, subsubvalue in subvalue.items():
                            if subsubvalue == '':
                                printable_str += f' {subsubkey}'
                            else:
                                printable_str += f' {subsubkey} {subsubvalue}'
                    else:
                        if subvalue == '':
                            printable_str += f' {subkey}'
                        else:
                            printable_str += f' {subkey} {subvalue}'
                printable_str += '\n'
            else:
                printable_str += f' {key} {value}\n'
            key_indx += 1
        return printable_str

    def __populate_optional_str_keywords(self, keyword: str, keyword_value_options: list[str], single_line: str,
                                         line_list: list[str]) -> None:
        """Utility function to populate rel perm keywords that have optional string values, e.g., IFT, JFUNC, etc.

        Args:
        ----
            keyword (str): primary keyword, e.g., IFT or JFUNC
            keyword_value_options (list[str]): primary keyword optional values, e.g., [METHOD1, METHOD2] for IFT
            single_line (str): single line as read from input RELPM file
            line_list (list[str]): list of strings that comprise input RELPM file
        """
        if nfo.check_token(keyword, single_line):
            key_val = fo.get_token_value(keyword, single_line, line_list)
            if key_val in keyword_value_options:
                self.properties[keyword] = key_val
            else:
                self.properties[keyword] = ''

    def read_properties(self) -> None:
        """Read Nexus rel perm file contents and populate the NexusRelPermMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize flags and containers to use to record properties as we iterate through relperm file contents
        # Dictionary to record start and ending indices for tables
        relpm_table_indices: dict[str, list[int]] = {}
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {}
        for table_name in RELPM_TABLE_KEYWORDS:
            table_being_read[table_name] = False
        # Flag to track hysteresis parameters section
        hysteresis_being_read: bool = False
        hysteresis_section_indices: list[int] = []
        # Dictionary to record start and ending indices of nondarcy section
        nondarcy_indices: dict[str, list[int]] = {}
        nondarcy_being_read: bool = False
        # Dictionary and flags for handle tabular reconstruction
        recon_dict: dict[str, Union[float, pd.DataFrame]] = {}
        found_reconstruct = False

        line_indx = 0
        for line in file_as_list:

            # Find standalone relperm keywords
            if [i for i in line.split() if i in RELPM_SINGLE_KEYWORDS]:
                for word in RELPM_SINGLE_KEYWORDS:
                    if nfo.check_token(word, line):
                        self.properties[word] = ''
            # Find relperm key-value pairs, such as SOMOPT2 0.05
            if [i for i in line.split() if i in RELPM_KEYWORDS_VALUE_FLOAT]:
                for key in RELPM_KEYWORDS_VALUE_FLOAT:
                    if nfo.check_token(key, line):
                        self.properties[key] = float(nfo.get_expected_token_value(key, line, file_as_list))
            # Handle certain specific relperm options
            optional_keyword_dict = {
                'JFUNC': ['KX', 'KY', 'KXKY'],
                'SCALING': ['NONE', 'TWOPOINT', 'THREEPOINT'],
                'SCALING_PC': ['NONE', 'TWOPOINT', 'THREEPOINT'],
                'IFT': ['METHOD1', 'METHOD2'],
                'NEARCRIT': ['HCSCALE'],
                'DERIVATIVES': ['ANALYTICAL', 'NUMERICAL']
                }
            for opt_key, opt_vals in optional_keyword_dict.items():
                self.__populate_optional_str_keywords(opt_key, opt_vals, line, file_as_list)
            # Handle tabular reconstruction
            if nfo.check_token('RECONSTRUCT', line):
                found_reconstruct = True
            for recon_key in ['NSGDIM', 'NSWDIM']:
                if nfo.check_token(recon_key, line) and found_reconstruct:
                    recon_dict[recon_key] = int(nfo.get_expected_token_value(recon_key, line, file_as_list))
            if found_reconstruct:
                self.properties['RECONSTRUCT'] = recon_dict

            # Find beginning and ending indices of hysteresis section
            if nfo.check_token('HYSTERESIS', line):
                hysteresis_being_read = True
                hysteresis_section_indices = [line_indx, len(file_as_list)]
            if len(line.split()) > 0 and hysteresis_being_read:
                possible_token = line.split()[0]
                if nfo.check_token(possible_token, line) and possible_token not in \
                        ["HYSTERESIS", *RELPM_HYSTERESIS_PRIMARY_KEYWORDS]:
                    hysteresis_being_read = False
                    hysteresis_section_indices[1] = line_indx

            # Find beginning and ending indices of nondarcy section
            for nondarcy_key in RELPM_NONDARCY_KEYWORDS:
                if nfo.check_token(nondarcy_key, line):
                    nondarcy_being_read = True
                    nondarcy_indices[nondarcy_key] = [line_indx + 1, len(file_as_list)]
                if nondarcy_being_read and nfo.check_token('END' + nondarcy_key, line):
                    nondarcy_being_read = False
                    nondarcy_indices[nondarcy_key][1] = line_indx

            # Find ending index of relperm tables
            # if start_reading_table:
            for table_keyword in RELPM_TABLE_KEYWORDS:
                if table_being_read[table_keyword]:
                    for potential_endkeyword in RELPM_KEYWORDS:
                        if nfo.check_token(potential_endkeyword, line):
                            relpm_table_indices[table_keyword][1] = line_indx
                            table_being_read[table_keyword] = False
                            break
            # Find the starting index of relperm tables
            if [i for i in line.split() if i in RELPM_TABLE_KEYWORDS]:
                for table_keyword in RELPM_TABLE_KEYWORDS:
                    if nfo.check_token(table_keyword, line):
                        relpm_table_indices[table_keyword] = [line_indx + 1, len(file_as_list)]
                        table_being_read[table_keyword] = True

            line_indx += 1

        # Read in tables
        for key in relpm_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                                                        relpm_table_indices[key][0]:relpm_table_indices[key][1]])

        # Read nondarcy parameters from nondarcy section, if present:
        for key in nondarcy_indices.keys():
            nondarcy_dict: dict[str, Union[float, pd.DataFrame]] = {}
            for line in file_as_list[nondarcy_indices[key][0]:nondarcy_indices[key][1]]:
                for param in RELPM_NONDARCY_PARAMS:
                    if nfo.check_token(param, line):
                        nondarcy_dict[param] = float(nfo.get_expected_token_value(param, line, file_as_list))
            self.properties[key] = nondarcy_dict

        # Read hysteresis section, if present
        if len(hysteresis_section_indices) > 0:
            for line in file_as_list[hysteresis_section_indices[0]:hysteresis_section_indices[1]]:
                if [i for i in line.split() if i in ['NONE', 'NOCHK_HYS']]:
                    for hyst_keyword in ['NONE', 'NOCHK_HYS']:
                        if nfo.check_token(hyst_keyword, line):
                            self.hysteresis_params[hyst_keyword] = ''
                if nfo.check_token('KRW', line) and fo.get_token_value('KRW', line, file_as_list) == 'USER':
                    self.hysteresis_params['KRW'] = 'USER'
                if [i for i in line.split() if i in ['KRG', 'KROW']]:
                    for hyst_keyword in ['KRG', 'KROW']:
                        if nfo.check_token(hyst_keyword, line):
                            hyst_keyword_primary_key = fo.get_token_value(hyst_keyword, line, file_as_list)
                            if hyst_keyword_primary_key == 'USER':
                                self.hysteresis_params[hyst_keyword] = 'USER'
                            elif hyst_keyword_primary_key in ['LINEAR', 'SCALED', 'CARLSON', 'KILLOUGH']:
                                hyst_dict: dict[str, Union[str, float, dict[str, Union[str, float]]]] = {}
                                hyst_subdict: dict[str, Union[str, float]] = {}
                                if nfo.check_token('MAXTRAP', line):
                                    hyst_subdict['MAXTRAP'] = float(nfo.get_expected_token_value('MAXTRAP',
                                                                                                 line, file_as_list))
                                    hyst_dict[hyst_keyword_primary_key] = hyst_subdict
                                if nfo.check_token('EXP', line):
                                    hyst_subdict['EXP'] = float(nfo.get_expected_token_value('EXP',
                                                                                             line, file_as_list))
                                    hyst_dict[hyst_keyword_primary_key] = hyst_subdict
                                if nfo.check_token('NOMOD', line):
                                    hyst_subdict['NOMOD'] = ''
                                    hyst_dict[hyst_keyword_primary_key] = hyst_subdict
                                self.hysteresis_params[hyst_keyword] = hyst_dict
                if [i for i in line.split() if i in ['PCWO', 'PCGO', 'WAG']]:
                    for hyst_keyword in ['PCWO', 'PCGO', 'WAG']:
                        if nfo.check_token(hyst_keyword, line):
                            hyst_pc_dict: dict[str, Union[str, float, dict[str, Union[str, float]]]] = {}
                            # Search for options with key-value pairs
                            for hyst_keyword_primary_key in ['MAXSW', 'MINSG', 'ETA', 'LAND', 'ALPHA', 'AFAC']:
                                if nfo.check_token(hyst_keyword_primary_key, line):
                                    hyst_pc_dict[hyst_keyword_primary_key] = \
                                        float(nfo.get_expected_token_value(hyst_keyword_primary_key,
                                                                           line, file_as_list))
                            # Search for single keyword options
                            for hyst_keyword_primary_key in ['TRAPSCALE', 'NOWATHYS', 'NOGASHYS', 'NOOILHYS']:
                                if nfo.check_token(hyst_keyword_primary_key, line):
                                    hyst_pc_dict[hyst_keyword_primary_key] = ''
                            self.hysteresis_params[hyst_keyword] = hyst_pc_dict
                if [i for i in line.split() if i in ['TOLREV', 'TOLHYS']]:
                    for hyst_keyword in ['TOLREV', 'TOLHYS']:
                        if nfo.check_token(hyst_keyword, line):
                            self.hysteresis_params[hyst_keyword] = float(
                                nfo.get_expected_token_value(hyst_keyword, line, file_as_list))
