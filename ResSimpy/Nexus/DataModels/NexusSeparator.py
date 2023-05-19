from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.NexusKeywords.separator_keywords import SEPARATOR_KEYS_INT, SEPARATOR_KEYS_FLOAT, SEPARATOR_KEYWORDS


@dataclass  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusSeparator():
    """Class to hold data input for a Nexus Separator method
    Attributes:
        file_path (str): Path to the Nexus Separator file
        method_number (int): Separator method number in Nexus fcs file
    """
    file_path: str
    method_number: int
    separator_type: Optional[str] = None
    properties: dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame, dict[str, pd.DataFrame]]] \
        = field(default_factory=get_empty_dict_union)

    def __repr__(self) -> str:
        """Pretty printing separator data"""
        printable_str = ''
        printable_str += '\n--------------------------------\n'
        printable_str += f'Separator method {self.method_number}\n'
        printable_str += '--------------------------------\n'
        printable_str += f'FILE_PATH: {self.file_path}\n'
        printable_str += f'SEPARATOR_TYPE: {self.separator_type}\n'
        sep_dict = self.properties
        for key, value in sep_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += f'{key}: \n'
                printable_str += value.to_string()
                printable_str += '\n\n'
            elif isinstance(value, Enum):
                printable_str += f'{key}: {value.name}\n'
            else:
                printable_str += f'{key}: {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus Separator file contents and populate NexusSeparator object
        """
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Initialize flags and containers used to record properties as we iterate through separator file contents
        # List to record start and ending indices for tables
        sep_table_indices: list[int] = [0, len(file_as_list)]
        # Flag to tell when to start reading a table
        start_reading_table: bool = False

        line_indx = 0
        for line in file_as_list:

            # Determine separator type, i.e., EOS multistage, gas plant data or black oil
            if nfo.check_token('TEMP', line):  # EOS multistage separator table
                self.separator_type = 'EOS'
                sep_table_indices[0] = line_indx  # Specify EOS multistage separator table starting index
                start_reading_table = True
                line_indx += 1
                continue
            elif nfo.check_token('KEYCPTLIST', line):  # Gas plant data
                self.separator_type = 'GASPLANT'
                elems = line.split('!')[0].split()
                cpt_index = elems.index('KEYCPTLIST')
                if 'KEYCPTLIST' not in self.properties.keys():
                    self.properties['KEYCPTLIST'] = elems[cpt_index+1:]
                line_indx += 1
                continue
            elif nfo.check_token('BOSEP', line):  # Black oil separator table
                self.separator_type = 'BLACKOIL'
                line_indx += 1
                continue

            # Find SEPARATOR key-value pairs, such as WATERMETHOD 1 or PRES_STD 14.7
            if [i for i in line.split() if i in SEPARATOR_KEYS_FLOAT]:
                for key in SEPARATOR_KEYS_FLOAT:
                    if nfo.check_token(key, line):
                        self.properties[key] = float(str(nfo.get_token_value(key, line, file_as_list)))
            if [i for i in line.split() if i in SEPARATOR_KEYS_INT]:
                for key in SEPARATOR_KEYS_INT:
                    if nfo.check_token(key, line):
                        self.properties[key] = int(str(nfo.get_token_value(key, line, file_as_list)))

            # Find starting index for black oil separator table
            if self.separator_type == 'BLACKOIL':
                if nfo.check_token('KVOIL', line):
                    sep_table_indices[0] = line_indx
                    start_reading_table = True
                    line_indx += 1
                    continue

            # Find ending index for EOS multistage and black oil separator tables
            if start_reading_table:
                if self.separator_type in ['EOS', 'BLACKOIL']:
                    for keyword in SEPARATOR_KEYWORDS:
                        if nfo.check_token(keyword, line):
                            sep_table_indices[1] = line_indx
                            start_reading_table = False
                            break

            # Find starting and ending indices for gas plant separator table
            if self.separator_type == 'GASPLANT':
                if nfo.check_token('RECFAC_TABLE', line):
                    sep_table_indices[0] = line_indx+1
                    start_reading_table = True
                if nfo.check_token('ENDRECFAC_TABLE', line):
                    sep_table_indices[1] = line_indx
                    start_reading_table = False

            line_indx += 1

        # Read in separator table
        if self.separator_type is not None:
            self.properties['SEPARATOR_TABLE'] = nfo.read_table_to_df(file_as_list[sep_table_indices[0]:
                                                                                   sep_table_indices[1]])
