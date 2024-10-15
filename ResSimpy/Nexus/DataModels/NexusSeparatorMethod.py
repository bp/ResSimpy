"""Class to hold data input for a Nexus Separator method."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.NexusKeywords.separator_keywords import SEPARATOR_KEYS_INT, SEPARATOR_KEYS_FLOAT
from ResSimpy.Nexus.NexusKeywords.separator_keywords import SEPARATOR_KEYWORDS
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import SeparatorUnits
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.Enums.FluidTypeEnums import SeparatorType


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusSeparatorMethod(DynamicProperty):
    """Class to hold data input for a Nexus Separator method.

    Attributes:
        file (NexusFile): Nexus Separator file object
        input_number (int): Separator method number in Nexus fcs file
        separator_type (Optional[str]): Type of separator method, e.g., BLACKOIL, GASPLANT or EOS. Defaults to None
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific separator method. Defaults to empty dictionary.
    """

    file: NexusFile
    separator_type: Optional[SeparatorType] = None
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray,
                     pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 separator_type: Optional[SeparatorType] = None,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        """Initialises the NexusSeparatorMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the separator method
            input_number (int): method number for the separator method
            model_unit_system (UnitSystem): unit system from the model
            separator_type (Optional[SeparatorType]): type of separator method, e.g., BLACKOIL, GASPLANT or EOS

            properties: dictionary of properties for the separator method.
        """
        if separator_type is not None:
            self.separator_type = separator_type
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
            'TEMP': ('temperature', float),
            'PRES': ('pressure', float),
            'TEMP_STD': ('standard_temperature', float),
            'PRES_STD': ('standard_pressure', float),
        }
        return keywords

    @property
    def units(self) -> SeparatorUnits:
        """Returns the attribute to unit map for the separator method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return SeparatorUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with separator data in Nexus file format."""
        printable_str = ''
        sep_dict = self.properties
        for key, value in sep_dict.items():
            if key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif key == 'SEPARATOR_TABLE' and isinstance(value, pd.DataFrame):
                if self.separator_type == SeparatorType.GASPLANT:
                    printable_str += 'RECFAC_TABLE\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n'
                if self.separator_type == SeparatorType.GASPLANT:
                    printable_str += 'ENDRECFAC_TABLE\n'
                printable_str += '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key == 'KEYCPTLIST' and isinstance(value, list):
                printable_str += f"{key} {' '.join(value)}\n"
            elif value == '':
                printable_str += f'{key}\n'
            else:
                printable_str += f'{key} {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus Separator file contents and populate NexusSeparatorMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize flags and containers used to record properties as we iterate through separator file contents
        # List to record start and ending indices for tables
        sep_table_indices: list[int] = [0, len(file_as_list)]
        # Flag to tell when to start reading a table
        start_reading_table: bool = False

        line_indx = 0
        for line in file_as_list:

            # Determine separator type, i.e., EOS multistage, gas plant data or black oil
            if nfo.check_token('TEMP', line):  # EOS multistage separator table
                self.separator_type = SeparatorType.EOS
                sep_table_indices[0] = line_indx  # Specify EOS multistage separator table starting index
                start_reading_table = True
                line_indx += 1
                continue
            elif nfo.check_token('KEYCPTLIST', line):  # Gas plant data
                self.separator_type = SeparatorType.GASPLANT
                elems = line.split('!')[0].split()
                cpt_index = elems.index('KEYCPTLIST')
                if 'KEYCPTLIST' not in self.properties.keys():
                    self.properties['KEYCPTLIST'] = elems[cpt_index + 1:]
                line_indx += 1
                continue
            elif nfo.check_token('BOSEP', line):  # Black oil separator table
                self.separator_type = SeparatorType.BLACKOIL
                self.properties['BOSEP'] = ''
                line_indx += 1
                continue

            # Find SEPARATOR key-value pairs, such as WATERMETHOD 1 or PRES_STD 14.7
            if [i for i in line.split() if i in SEPARATOR_KEYS_FLOAT]:
                for key in SEPARATOR_KEYS_FLOAT:
                    if nfo.check_token(key, line):
                        self.properties[key] = float(nfo.get_expected_token_value(key, line, file_as_list))
            if [i for i in line.split() if i in SEPARATOR_KEYS_INT]:
                for key in SEPARATOR_KEYS_INT:
                    if nfo.check_token(key, line):
                        self.properties[key] = int(nfo.get_expected_token_value(key, line, file_as_list))

            # Find starting index for black oil separator table
            if self.separator_type == SeparatorType.BLACKOIL:
                if nfo.check_token('KVOIL', line):
                    sep_table_indices[0] = line_indx
                    start_reading_table = True
                    line_indx += 1
                    continue

            # Find ending index for EOS multistage and black oil separator tables
            if start_reading_table:
                if self.separator_type in [SeparatorType.EOS, SeparatorType.BLACKOIL]:
                    for keyword in SEPARATOR_KEYWORDS:
                        if nfo.check_token(keyword, line):
                            sep_table_indices[1] = line_indx
                            start_reading_table = False
                            break

            # Find starting and ending indices for gas plant separator table
            if self.separator_type == SeparatorType.GASPLANT:
                if nfo.check_token('RECFAC_TABLE', line):
                    sep_table_indices[0] = line_indx + 1
                    start_reading_table = True
                if nfo.check_token('ENDRECFAC_TABLE', line):
                    sep_table_indices[1] = line_indx
                    start_reading_table = False

            line_indx += 1

        # Read in separator table
        if self.separator_type is not None:
            self.properties['SEPARATOR_TABLE'] = nfo.read_table_to_df(file_as_list[sep_table_indices[0]:
                                                                                   sep_table_indices[1]])
