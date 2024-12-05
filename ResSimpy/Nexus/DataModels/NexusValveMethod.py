"""Class to hold Nexus Valve properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.valve_keywords import VALVE_TABLE_KEYWORDS, VALVE_RATE_KEYWORDS
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import HydraulicsUnits
from ResSimpy.Enums.UnitsEnum import UnitSystem, TemperatureUnits
from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusValveMethod(DynamicProperty):
    """Class to hold Nexus Valve properties.

    Attributes:
        file (NexusFile): Nexus valve properties file object
        input_number (int): Valve properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific valve properties method. Defaults to empty dictionary.
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
        """Initialises the NexusValveMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the valve method.
            input_number (int): method number for the valve method.
            model_unit_system (UnitSystem): unit system used in the model.
            properties: The properties found in the valve method.
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
            'VC': ('valve_coefficient', float),
        }
        return keywords

    @property
    def units(self) -> HydraulicsUnits:
        """Returns the attribute to unit map for the Valve method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return HydraulicsUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with valve data in Nexus file format."""
        printable_str = ''
        valve_dict = self.properties
        for key, value in valve_dict.items():
            if key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif isinstance(value, pd.DataFrame):
                table_text = f'{key}'
                if key in ['VALVE', 'ICV']:
                    for rate_key in VALVE_RATE_KEYWORDS:
                        if 'DP_RATE' in valve_dict.keys() and rate_key == valve_dict['DP_RATE']:
                            table_text += f' {rate_key}'
                printable_str += f'{table_text}\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n'
                printable_str += 'END'+key+'\n'
                printable_str += '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
            elif key not in ['DP_RATE']:
                printable_str += f'{key} {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus valve file contents and populate the NexusValveMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize flags and containers to use to record properties as we iterate through valve file contents
        # Dictionary to record start and ending indices for tables
        valve_table_indices: dict[str, list[int]] = {}
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {}
        for table_name in VALVE_TABLE_KEYWORDS:
            table_being_read[table_name] = False

        line_indx = 0
        for line in file_as_list:

            # Find beginning and ending indices of tables
            for table_key in VALVE_TABLE_KEYWORDS:
                if nfo.check_token(table_key, line):
                    table_being_read[table_key] = True
                    valve_table_indices[table_key] = [line_indx + 1, len(file_as_list)]
                    # Find rate keyword if present
                    for rate_key in VALVE_RATE_KEYWORDS:
                        if nfo.check_token(rate_key, line):
                            self.properties['DP_RATE'] = rate_key  # Rate used to determine pressure drop across valve
                if table_being_read[table_key] and nfo.check_token('END' + table_key, line):
                    table_being_read[table_key] = False
                    valve_table_indices[table_key][1] = line_indx

            line_indx += 1

        # Read in tables
        for key in valve_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                                                        valve_table_indices[key][0]:valve_table_indices[key][1]])
