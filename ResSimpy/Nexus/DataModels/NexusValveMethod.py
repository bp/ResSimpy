from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.valve_keywords import VALVE_TABLE_KEYWORDS, VALVE_RATE_KEYWORDS
from ResSimpy.ValveMethod import ValveMethod

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusValveMethod(ValveMethod):
    """Class to hold Nexus Valve properties
    Attributes:
        file_path (str): Path to the Nexus valve properties file
        method_number (int): Valve properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific valve properties method. Defaults to empty dictionary.
    """

    # General parameters
    file_path: str
    properties: dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                     dict[str, Union[float, pd.DataFrame]]]] = field(default_factory=get_empty_dict_union)

    def __init__(self, file_path: str, method_number: int,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        self.file_path = file_path
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        super().__init__(method_number=method_number)

    def __repr__(self) -> str:
        """Pretty printing valve data."""
        printable_str = f'\nFILE_PATH: {self.file_path}\n'
        valve_dict = self.properties
        for key, value in valve_dict.items():
            if isinstance(value, pd.DataFrame):
                table_text = f'{key}:'
                if key in ['VALVE', 'ICV']:
                    for rate_key in VALVE_RATE_KEYWORDS:
                        if 'DP_RATE' in valve_dict.keys() and rate_key == valve_dict['DP_RATE']:
                            table_text += f' {rate_key}'
                printable_str += f'{table_text}\n'
                printable_str += value.to_string(na_rep='')
                printable_str += '\n\n'
            elif key not in ['DP_RATE']:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key}: {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus valve file contents and populate the NexusValveMethod object."""
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

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
