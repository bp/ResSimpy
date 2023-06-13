from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_SINGLE_KEYWORDS, AQUIFER_TABLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_KEYWORDS_VALUE_FLOAT, AQUIFER_KEYWORDS_VALUE_INT
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_KEYWORDS, AQUIFER_TYPE_KEYWORDS
from ResSimpy.DynamicProperty import DynamicProperty

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusAquiferMethod(DynamicProperty):
    """Class to hold Nexus Aquifer properties.

    Attributes:
        file_path (str): Path to the Nexus aquifer properties file
        input_number (int): Aquifer properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific aquifer properties method. Defaults to empty dictionary.
    """

    # General parameters
    file_path: str
    properties: dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                dict[str, Union[float, pd.DataFrame]]]] = field(default_factory=get_empty_dict_union)

    def __init__(self, file_path: str, input_number: int,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        self.file_path = file_path
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        super().__init__(input_number=input_number)

    def __repr__(self) -> str:
        """Pretty printing aquifer data."""
        printable_str = f'\nFILE_PATH: {self.file_path}\n'
        aquifer_dict = self.properties
        for aq_type in AQUIFER_TYPE_KEYWORDS:
            if aq_type in aquifer_dict.keys():
                printable_str += f'\n{aq_type}\n'
        for key, value in aquifer_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += f'{key}:\n'
                printable_str += value.to_string(na_rep='')
                printable_str += '\n\n'
            elif isinstance(value, Enum):
                printable_str += f'{key}: {value.name}\n'
            elif key not in AQUIFER_TYPE_KEYWORDS:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key}: {value}\n'
        printable_str += '\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus aquifer file contents and populate the NexusValveMethod object."""
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Initialize flags and containers to use to record properties as we iterate through aquifer file contents
        # Dictionary to record start and ending indices for tables
        aquifer_table_indices: dict[str, list[int]] = {}
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {}
        for table_name in AQUIFER_TABLE_KEYWORDS:
            table_being_read[table_name] = False

        line_indx = 0
        for line in file_as_list:

            # Find standalone aquifer keywords, such as CARTER_TRACY or LINEAR
            if [i for i in line.split() if i in AQUIFER_TYPE_KEYWORDS + AQUIFER_SINGLE_KEYWORDS]:
                for word in AQUIFER_TYPE_KEYWORDS + AQUIFER_SINGLE_KEYWORDS:
                    if nfo.check_token(word, line):
                        self.properties[word] = ''
            # Find AQUIFER key-float value pairs, such as LINFAC 0.8 or BAQ 20.
            if [i for i in line.split() if i in AQUIFER_KEYWORDS_VALUE_FLOAT]:
                for key in AQUIFER_KEYWORDS_VALUE_FLOAT:
                    if nfo.check_token(key, line):
                        self.properties[key] = float(nfo.get_expected_token_value(key, line, file_as_list))
            # Find AQUIFER key-int value pairs, such as ITDPD 1 or IWATER 2
            if [i for i in line.split() if i in AQUIFER_KEYWORDS_VALUE_INT]:
                for key in AQUIFER_KEYWORDS_VALUE_INT:
                    if nfo.check_token(key, line):
                        self.properties[key] = int(nfo.get_expected_token_value(key, line, file_as_list))

            # Find beginning and ending indices of tables
            for table_key in AQUIFER_TABLE_KEYWORDS:
                if (table_key == 'TRACER' and table_being_read[table_key] and nfo.check_token('END' + table_key,
                                                                                              line)) \
                        or (table_key == 'TDPD' and table_being_read[table_key] and
                            [i for i in line.split() if nfo.check_token(i, line) and i in AQUIFER_KEYWORDS]):
                    table_being_read[table_key] = False
                    aquifer_table_indices[table_key][1] = line_indx
                if nfo.check_token(table_key, line):
                    table_being_read[table_key] = True
                    aquifer_table_indices[table_key] = [line_indx + 1, len(file_as_list)]

            line_indx += 1

        # Read in tables
        for key in aquifer_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                                                        aquifer_table_indices[key][0]:aquifer_table_indices[key][1]])
