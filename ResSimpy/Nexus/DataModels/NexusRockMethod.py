from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_ALL_TABLE_KEYWORDS, ROCK_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_SINGLE_KEYWORDS, ROCK_KEYWORDS_VALUE_STR
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_KEYWORDS, ROCK_REV_IRREV_OPTIONS
from ResSimpy.RockMethod import RockMethod

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusRockMethod(RockMethod):
    """ Class to hold Nexus Rock properties
    Attributes:
        file_path (str): Path to the Nexus rock properties file
        method_number (int): Rock properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame, dict[str, pd.DataFrame]]] ):
            Dictionary holding all properties for a specific rock properties method. Defaults to empty dictionary.
    """
    # General parameters
    file_path: str
    properties: dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                dict[str, pd.DataFrame]]] = field(default_factory=get_empty_dict_union)

    def __init__(self, file_path: str, method_number: int,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                                      dict[str, pd.DataFrame]]]] = None):
        self.file_path = file_path
        if properties:
            self.properties = properties
        else:
            self.properties = {}
        super().__init__(method_number=method_number)

    def __repr__(self) -> str:
        """Pretty printing rock properties data"""
        printable_str = f'\nFILE_PATH: {self.file_path}\n'
        rock_dict = self.properties
        for key, value in rock_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += f'{key}:\n'
                printable_str += value.to_string()
                printable_str += '\n\n'
            elif isinstance(value, dict):
                for subkey in value.keys():
                    printable_str += f'{key} - {subkey}\n'
                    printable_str += value[subkey].to_string()
                    printable_str += '\n\n'
            elif isinstance(value, Enum):
                printable_str += f'{key}: {value.name}\n'
            elif value == '':
                printable_str += f'{key}\n'
            else:
                printable_str += f'{key}: {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus rock properties file contents and populate NexusRock object
        """
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

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
                        self.properties[key] = float(str(nfo.get_token_value(key, line, file_as_list)))
            # Find standalone rock property keywords, such as COMPR or KPMULT
            if [i for i in line.split() if i in ROCK_SINGLE_KEYWORDS]:
                for word in ROCK_SINGLE_KEYWORDS:
                    if nfo.check_token(word, line):
                        self.properties[word] = ''
            # Handle REVERSIBLE or IRREVERSIBLE keywords
            if [i for i in line.split() if i in ROCK_KEYWORDS_VALUE_STR]:
                for key in ROCK_KEYWORDS_VALUE_STR:
                    if nfo.check_token(key, line):
                        if nfo.get_token_value(key, line, file_as_list) in ROCK_REV_IRREV_OPTIONS:
                            self.properties[key] = str(nfo.get_token_value(key, line, file_as_list))
                        else:
                            self.properties[key] = ''
            # Find starting index of rock compaction table
            if nfo.check_token('CMT', line):
                cmt_indices = [line_indx+1, len(file_as_list)]
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
                swinit_key = str(nfo.get_token_value('SWINIT', line, file_as_list))
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