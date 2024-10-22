from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import SUnits, TemperatureUnits, UnitSystem
from ResSimpy.Nexus.NexusKeywords.gaslift_keywords import GL_ARRAY_KEYWORDS, GASLIFT_KEYWORDS, GL_TABLE_HEADER_COLS
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import HydraulicsUnits

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusGasliftMethod(DynamicProperty):
    """Class to hold Nexus gaslift properties.

    Attributes:
        file (NexusFile): Nexus gaslift properties file object
        input_number (int): Gaslift properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific gaslift properties method. Defaults to empty dictionary.
    """

    # General parameters
    file: NexusFile
    properties: dict[str,
                     Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                           dict[str, Union[float, pd.DataFrame]]]] = \
        field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        """Initialises the NexusGasliftMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the gaslift method
            input_number (int): method number for the gaslift method
            model_unit_system (UnitSystem): unit system from the model.
            properties: dictionary of properties for the gaslift. Defaults to None.
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
            'QOIL': ('surface_oil_rate', float),
            'QLIQ': ('surface_liquid_rate', float),
            'PRESSURE': ('pressure', float),
            'WCUT': ('watercut', float),
            'GLR': ('gas_liquid_ratio', float),
            'GOR': ('gas_oil_ratio', float),
        }
        return keywords

    @property
    def units(self) -> HydraulicsUnits:
        """Returns the attribute to unit map for the Gaslift method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return HydraulicsUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with gaslift data in Nexus file format."""
        printable_str = ''
        gl_dict = self.properties
        for key, value in gl_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += value.to_string(na_rep='', index=False) + '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem | TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif value == '':
                printable_str += f'{key}\n'
            else:
                printable_str += f'{key} {value}\n'
        printable_str += '\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus gaslift file contents and populate the NexusGasliftMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize flags and containers to use to record properties as we iterate through aquifer file contents
        # Dictionary to record start and ending indices for tables
        gl_table_indices: dict[str, list[int]] = {}
        # Dictionary of flags indicating which tables are being read
        start_reading_table = False

        line_indx = 0
        for line in file_as_list:

            # Find arrays of parameters, e.g., QOIL 1.0 10. 100., or WCUT 0.0 0.1 0.2
            potential_keyword = nfo.check_list_tokens(GL_ARRAY_KEYWORDS, line)
            if potential_keyword is not None:
                line_elems = line.split('!')[0].split()
                keyword_index = line_elems.index(potential_keyword)
                self.properties[potential_keyword] = ' '.join(line_elems[keyword_index+1:])

            # Find ending index of gaslift table
            if start_reading_table:
                for potential_endkeyword in GASLIFT_KEYWORDS:
                    if nfo.check_token(potential_endkeyword, line):
                        gl_table_indices['GL_TABLE'][1] = line_indx
                        start_reading_table = False
                        break
            # Find starting index of gaslift table
            for header_keyword in GL_TABLE_HEADER_COLS:
                if nfo.check_token(header_keyword, line):
                    gl_table_indices['GL_TABLE'] = [line_indx, len(file_as_list)]
                    start_reading_table = True

            line_indx += 1

        # Read in gaslift tables
        for key in gl_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                gl_table_indices[key][0]:gl_table_indices[key][1]])
