"""Class to hold Nexus Rock properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_ALL_TABLE_KEYWORDS, ROCK_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_SINGLE_KEYWORDS, ROCK_KEYWORDS_VALUE_STR
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_KEYWORDS, ROCK_REV_IRREV_OPTIONS
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import RockUnits
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusRockMethod(DynamicProperty):
    """Class to hold Nexus Rock properties.

    Attributes:
        file (NexusFile): Nexus rock properties file object
        input_number (int): Rock properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific rock properties method. Defaults to empty dictionary.
    """

    # General parameters
    file: NexusFile
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                dict[str, Union[float, pd.DataFrame]]]] = \
        field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        """Initialises the NexusRockMethod class.

        Args:
            file (NexusFile): Nexus file containing the rock method.
            input_number (int): method number for the rock method
            model_unit_system (UnitSystem): unit system from the model
            properties: dictionary of the properties for the rock method. Defaults to None.
        """
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        self.unit_system = model_unit_system
        super().__init__(input_number=input_number, file=file)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords: dict[str, tuple[str, type]] = {
            'CR': ('rock_compressibility', float),
            'KP': ('rock_permeability_compressibility', float),
            'PREF': ('reference_pressure', float),
            'P': ('pressure', float),
            'DP': ('delta_pressure', float),
        }
        return keywords

    @property
    def units(self) -> RockUnits:
        """Returns the attribute to unit map for the rock method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return RockUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with rock properties data, in Nexus file format."""
        printable_str = ''
        rock_dict = self.properties
        for key, value in rock_dict.items():
            if key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif isinstance(value, pd.DataFrame):
                printable_str += f'{key}\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n\n'
            elif isinstance(value, dict):
                printable_str += f"{key.replace('_', ' ')}\n"
                for subkey in value.keys():
                    printable_str += f"SWINIT {subkey}\n"
                    df = value[subkey]
                    if isinstance(df, pd.DataFrame):
                        printable_str += df.to_string(na_rep='', index=False) + '\n'
                    printable_str += '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif value == '':
                printable_str += f'{key}\n'
            else:
                printable_str += f'{key} {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus rock properties file contents and populate NexusRockMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize properties
        cmt_indices: list[int] = []
        wirct_indices_dict: dict[str, dict[str, list[int]]] = {}
        # Flag to tell when to start reading a table
        start_reading_table: bool = False
        swinit_key = ''
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {}
        for table_name in ROCK_ALL_TABLE_KEYWORDS:
            table_being_read[table_name] = False

        line_indx = 0
        for line in file_as_list:

            # Find ROCK key-value pairs, such as PREF 2000 or CR 1e-6
            if [i for i in line.split() if i in ROCK_KEYWORDS_VALUE_FLOAT]:
                for key in ROCK_KEYWORDS_VALUE_FLOAT:
                    if nfo.check_token(key, line):
                        self.properties[key] = float(nfo.get_expected_token_value(key, line, file_as_list))
            # Find standalone rock property keywords, such as COMPR or KPMULT
            if [i for i in line.split() if i in ROCK_SINGLE_KEYWORDS]:
                for word in ROCK_SINGLE_KEYWORDS:
                    if nfo.check_token(word, line):
                        self.properties[word] = ''
            # Handle REVERSIBLE or IRREVERSIBLE keywords
            if [i for i in line.split() if i in ROCK_KEYWORDS_VALUE_STR]:
                for key in ROCK_KEYWORDS_VALUE_STR:
                    if nfo.check_token(key, line):
                        if fo.get_token_value(key, line, file_as_list) in ROCK_REV_IRREV_OPTIONS:
                            self.properties[key] = nfo.get_expected_token_value(key, line, file_as_list)
                        else:
                            self.properties[key] = ''
            # Find starting index of rock compaction table
            if nfo.check_token('CMT', line):
                cmt_indices = [line_indx + 1, len(file_as_list)]
                table_being_read['CMT'] = True
                start_reading_table = True
                line_indx += 1
                continue
            # Find ending index of rock compaction table
            if start_reading_table and table_being_read['CMT']:
                for potential_endkeyword in ROCK_KEYWORDS:
                    if nfo.check_token(potential_endkeyword, line):
                        cmt_indices[1] = line_indx
                        start_reading_table = False
                        table_being_read['CMT'] = False
                        break
            # Find ending index of a water-induced rock compaction table
            if start_reading_table and table_being_read['WIRCT']:
                for potential_endkeyword in ROCK_KEYWORDS:
                    if nfo.check_token(potential_endkeyword, line):
                        wirct_indices_dict['WIRCT'][swinit_key][1] = line_indx
                        start_reading_table = False
                        table_being_read['WIRCT'] = False
                        break
            # Find starting index of a water-induced rock compaction table
            if nfo.check_token('WIRCT', line):
                wirct_indices_dict['WIRCT'] = {}
            if nfo.check_token('SWINIT', line):
                swinit_key = nfo.get_expected_token_value('SWINIT', line, file_as_list)
                wirct_indices_dict['WIRCT'][swinit_key] = [line_indx+1, len(file_as_list)]
                table_being_read['WIRCT'] = True
                start_reading_table = True

            line_indx += 1

        # Read in compaction table(s) if there are any
        if len(cmt_indices) > 0:
            self.properties['CMT'] = nfo.read_table_to_df(file_as_list[cmt_indices[0]:cmt_indices[1]])
        for key in wirct_indices_dict.keys():
            self.properties[key] = {}
            for subkey in wirct_indices_dict[key].keys():
                property_key = self.properties[key]
                if not isinstance(property_key, dict):
                    raise ValueError(f"Property is not a dictionary: {str(self.properties[key])}")
                property_key[subkey] = nfo.read_table_to_df(file_as_list[
                                                            wirct_indices_dict[key][subkey][0]:
                                                            wirct_indices_dict[key][subkey][1]])
