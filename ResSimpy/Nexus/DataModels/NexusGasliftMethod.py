from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.gaslift_keywords import GL_ARRAY_KEYWORDS, GASLIFT_KEYWORDS, GL_TABLE_HEADER_COLS
from ResSimpy.GasliftMethod import GasliftMethod

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusGasliftMethod(GasliftMethod):
    """Class to hold Nexus gaslift properties
    Attributes:
        file_path (str): Path to the Nexus gaslift properties file
        method_number (int): Gaslift properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific gaslift properties method. Defaults to empty dictionary.
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
        """Pretty printing gaslift data."""
        printable_str = f'\nFILE_PATH: {self.file_path}\n'
        gl_dict = self.properties
        for key, value in gl_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += f'{key}:\n'
                printable_str += value.to_string(na_rep='')
                printable_str += '\n\n'
            elif isinstance(value, Enum):
                printable_str += f'{key}: {value.name}\n'
            elif value == '':
                printable_str += f'{key}\n'
            else:
                printable_str += f'{key}: {value}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus gaslift file contents and populate the NexusGasliftMethod object."""
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

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
