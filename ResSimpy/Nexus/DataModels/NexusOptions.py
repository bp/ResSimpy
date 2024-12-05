"""Data structure for holding Nexus options data."""
from dataclasses import dataclass, field
from typing import Optional, Union
import numpy as np
import pandas as pd
from enum import Enum
from ResSimpy.Enums.UnitsEnum import TemperatureUnits, UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.factory_methods import get_empty_dict_union
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import OptionsUnits
from ResSimpy.Nexus.NexusKeywords.options_keywords import OPT_KEYWORDS_VALUE_FLOAT, OPT_SINGLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.options_keywords import OPT_GLOBAL_METHOD_OVERRIDES_KEYWORDS, OPT_ARRAY_KEYWORDS
from ResSimpy.Utils.general_utilities import check_if_string_is_float


@dataclass(kw_only=True, repr=False)
class NexusOptions(DynamicProperty):
    """Class to hold Nexus options data."""
    file: NexusFile
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                dict[str, Union[float, pd.DataFrame]]]] = \
        field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, file: NexusFile, model_unit_system: UnitSystem, input_number: int = 1,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                                      dict[str, Union[float, pd.DataFrame]]]]] = None
                 ) -> None:
        """Initialises the NexusOptions class.

        Args:
            file (NexusFile): Nexus options file object
            model_unit_system (UnitSystem): unit system used in the model
            input_number (int): Always set to 1 as there is always one input file
            properties: Dictionary holding Nexus options information. Defaults to empty dictionary
        """
        self.unit_system = model_unit_system
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        super().__init__(input_number=input_number, file=file)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords: dict[str, tuple[str, type]] = {
            'PSTD': ('standard_pressure', float),
            'TSTD': ('standard_temperature', float),
            'RES_TEMP': ('reservoir_temperature', float)
        }
        return keywords

    @property
    def units(self) -> OptionsUnits:
        """Returns the attribute to unit map for the Nexus options class."""
        if not self.__properties_loaded:
            self.load_nexus_options()
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return OptionsUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with Nexus options data."""
        if not self.__properties_loaded:
            self.load_nexus_options()
        printable_str = ''
        options_dict = self.properties
        for key, value in options_dict.items():
            if key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
            elif key == 'REGDATA' and isinstance(value, dict):
                for regkey, regvalue in value.items():
                    if isinstance(regvalue, pd.DataFrame):
                        printable_str += f"\nREGDATA {regkey}\n"
                        printable_str += regvalue.to_string(na_rep='', index=False) + '\n'
                        printable_str += 'ENDREGDATA\n'
            elif key not in ['REGDATA', *OPT_GLOBAL_METHOD_OVERRIDES_KEYWORDS]:
                if isinstance(value, np.ndarray):
                    printable_str += f"{key} {' '.join([str(val) for val in value])}\n"
                elif value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
        # Work on printing out global method overrides keywords
        found_global_method_overrides_key = False
        for key, value in options_dict.items():
            if key in OPT_GLOBAL_METHOD_OVERRIDES_KEYWORDS:
                if not found_global_method_overrides_key:
                    printable_str += '\nGLOBAL_METHOD_OVERRIDES\n'
                    found_global_method_overrides_key = True
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
        if found_global_method_overrides_key:
            printable_str += 'ENDGLOBAL_METHOD_OVERRIDES\n'
        printable_str += '\n'

        return printable_str

    def load_nexus_options(self) -> None:
        """Read Nexus Options file contents and populate NexusOptions object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize properties
        # Dictionary to record start and ending indices for regdata tables
        regdata_indices: dict[str, list[int]] = {}
        region_group_name = ''
        start_reading_table = False

        line_indx = 0
        for line in file_as_list:

            # Find OPTIONS key-value pairs, such as PSTD 14.65, or RES_TEMP 200
            potential_keyword = nfo.check_list_tokens(OPT_KEYWORDS_VALUE_FLOAT, line)
            if potential_keyword is not None:
                if potential_keyword in ['PSTD', 'TSTD']:
                    next_value = nfo.get_expected_token_value(potential_keyword, line, file_as_list)
                    if check_if_string_is_float(next_value):
                        self.properties[potential_keyword] = float(next_value)
                    else:  # Float should be expected after next value
                        self.properties[potential_keyword] = float(
                            nfo.get_expected_token_value(next_value, line, file_as_list))
                else:
                    self.properties[potential_keyword] = float(
                        nfo.get_expected_token_value(potential_keyword, line, file_as_list))

            # Find standalone options keywords
            potential_keyword = nfo.check_list_tokens(OPT_SINGLE_KEYWORDS, line)
            if potential_keyword is not None:
                self.properties[potential_keyword] = ''

            # Find option keywords with array values, e.g., BOUNDARY_FLUXIN_SECTORS 1 3 4
            potential_keyword = nfo.check_list_tokens(OPT_ARRAY_KEYWORDS, line)
            if potential_keyword is not None:
                line_elems = line.split('!')[0].split()
                keyword_index = line_elems.index(potential_keyword)
                self.properties[potential_keyword] = np.fromstring(' '.join(line_elems[keyword_index + 1:]), sep=' ')

            # Find global method overrides keywords
            potential_keyword = nfo.check_list_tokens(OPT_GLOBAL_METHOD_OVERRIDES_KEYWORDS, line)
            if potential_keyword is not None:
                next_value = nfo.get_expected_token_value(potential_keyword, line, file_as_list)
                if next_value == 'OFF':
                    self.properties[potential_keyword] = 'OFF'
                else:
                    self.properties[potential_keyword] = ''

            # Find starting and ending indices for regdata table
            if nfo.check_token('REGDATA', line):
                region_group_name = nfo.get_expected_token_value('REGDATA', line, file_as_list)
                regdata_indices[region_group_name] = [line_indx + 1, len(file_as_list)]
                start_reading_table = True
            if start_reading_table and nfo.check_token('ENDREGDATA', line):
                regdata_indices[region_group_name][1] = line_indx
                start_reading_table = False

            line_indx += 1

        # Read in regdata tables
        reg_dfs: dict[str, pd.DataFrame] = {}
        for key in regdata_indices.keys():
            reg_dfs[key] = nfo.read_table_to_df(file_as_list[regdata_indices[key][0]:regdata_indices[key][1]])
        if len(reg_dfs.keys()) > 0:
            self.properties['REGDATA'] = reg_dfs

        self.__properties_loaded = True

    def load_nexus_options_if_not_loaded(self) -> None:
        """Ensures we only load once the options file."""

        if not self.__properties_loaded:
            self.load_nexus_options()
            self.__properties_loaded = True

    def look_up_region_number_by_name(self, region_name: str) -> int:
        """Look up the region number by the region name in the REGDATA.

        Args:
        region_name (str): Name of the region to look up.

        Returns:
        int: The region number if found, otherwise -1.
        """
        region_name = region_name.upper()
        reg_data = self.properties.get('REGDATA', None)
        if reg_data is None or not isinstance(reg_data, dict):
            return -1
        for table in reg_data.values():
            upper_names = table['NAME'].str.upper()
            if upper_names.isin([region_name]).sum() > 0:
                return table[upper_names == region_name]['NUMBER'].to_numpy()[0]
        return -1
