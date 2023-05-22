from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Optional
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_INTSAT_KEYWORDS, EQUIL_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_TABLE_KEYWORDS, EQUIL_SINGLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_OVERREAD_VALUES, EQUIL_COMPOSITION_OPTIONS
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_KEYWORDS
from ResSimpy.EquilMethod import EquilMethod

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusEquilMethod(EquilMethod):
    """ Class to hold Nexus Equil properties
    Attributes:
        file_path (str): Path to the Nexus equilibration file
        method_number (int): Equilibration method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame, dict[str, pd.DataFrame]]] ):
            Dictionary holding all properties for a specific equilibration method. Defaults to empty dictionary.
    """
    # General parameters
    file_path: str
    properties: dict[str, Union[str, int, float, Enum, list[str],
                                pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)

    def __init__(self, file_path: str, method_number: int,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                                      dict[str, Union[float, pd.DataFrame]]]]] = None):
        self.file_path = file_path
        if properties:
            self.properties = properties
        else:
            self.properties = {}
        super().__init__(method_number=method_number)

    def __repr__(self) -> str:
        """Pretty printing equilibration data"""
        printable_str = f'\nFILE_PATH: {self.file_path}\n'
        equil_dict = self.properties
        for key, value in equil_dict.items():
            if isinstance(value, pd.DataFrame):
                table_text = f'{key}:'
                if key == 'COMPOSITION':
                    if 'X' in equil_dict.keys():
                        table_text += f" X {equil_dict['X']}"
                    if 'Y' in equil_dict.keys():
                        table_text += f" Y {equil_dict['Y']}"
                printable_str += f'{table_text}\n'
                printable_str += value.to_string(na_rep='')
                printable_str += '\n\n'
            elif isinstance(value, Enum):
                printable_str += f'{key}: {value.name}\n'
            elif value == '':
                printable_str += f'{key}\n'
            elif key in ['INTSAT', 'VAITS']:
                if value == 'MOBILE':
                    printable_str += f'{key}: MOBILE\n'
                    for mobkey in ['SORWMN', 'SORGMN', 'SGCMN']:
                        if mobkey in equil_dict.keys():
                            printable_str += f'        {mobkey}: {equil_dict[mobkey]}\n'
                for vaitkey in ['VAITS_TOLSG', 'VAITS_TOLSW']:
                    if vaitkey in equil_dict.keys():
                        printable_str += f'    {vaitkey}: {equil_dict[vaitkey]}\n'
            elif key == 'OVERREAD':
                if isinstance(value, list):
                    printable_str += f"OVERREAD: {' '.join(value)}\n"
            elif key not in ['SORWMN', 'SORGMN', 'SGCMN', 'VAITS_TOLSG', 'VAITS_TOLSW',
                             'OVERREAD', 'INTSAT', 'VAITS', 'MOBILE', 'X', 'Y']:
                printable_str += f'{key}: {value}\n'

        return printable_str

    def read_properties(self) -> None:
        """Read Nexus equilibration file contents and populate NexusEquilMethod object
        """
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Initialize properties
        equil_table_indices: dict[str, list[int]] = {}
        # Flag to tell when to start reading a table
        start_reading_table: bool = False
        # Indicator of which of equilibration tables are being read
        table_being_read = ''

        line_indx = 0
        for line in file_as_list:

            # Find EQUIL key-value pairs, such as PINIT 3000, WOC 7000 or OVERREAD SW (list, multiple OVERREADs)
            if [i for i in line.split() if i in EQUIL_KEYWORDS_VALUE_FLOAT]:
                for key in EQUIL_KEYWORDS_VALUE_FLOAT:
                    if nfo.check_token(key, line) and 'DEPTH' not in line.split():  # Ensure not a table header
                        self.properties[key] = float(str(nfo.get_token_value(key, line, file_as_list)))
            if nfo.check_token('AUTOGOC_COMP', line):
                self.properties['AUTOGOC_COMP'] = str(nfo.get_token_value('AUTOGOC_COMP', line, file_as_list))
            if nfo.check_token('OVERREAD', line):
                overread_val = str(nfo.get_token_value('OVERREAD', line, file_as_list))
                if 'OVERREAD' in self.properties.keys() and isinstance(self.properties['OVERREAD'], list):
                    self.properties['OVERREAD'] += [overread_val]
                else:
                    self.properties['OVERREAD'] = [overread_val]
                while str(nfo.get_token_value(overread_val, line, file_as_list)) in EQUIL_OVERREAD_VALUES:
                    overread_val = str(nfo.get_token_value(overread_val, line, file_as_list))
                    if isinstance(self.properties['OVERREAD'], list):
                        prop_list: list[str] = self.properties['OVERREAD']
                        prop_list += [overread_val]
            if nfo.check_token('VIP_INIT', line):
                self.properties['VIP_INIT'] = ' '.join(line.split('!')[0].split()[1:])
            # Find standalone equilibration keywords
            if [i for i in line.split() if i in EQUIL_SINGLE_KEYWORDS]:
                for word in EQUIL_SINGLE_KEYWORDS:
                    if nfo.check_token(word, line):
                        self.properties[word] = ''
            # Handle integrated saturation initialization options
            if [i for i in line.split() if i in EQUIL_INTSAT_KEYWORDS]:
                for key in EQUIL_INTSAT_KEYWORDS:
                    if nfo.check_token(key, line):
                        if nfo.get_token_value(key, line, file_as_list) == 'MOBILE':
                            self.properties[key] = 'MOBILE'
                        else:
                            self.properties[key] = ''

            # Find starting index of an equil-related table. There is usually only one per equil file
            if [i for i in line.split() if i in EQUIL_TABLE_KEYWORDS]:
                for table_keyword in EQUIL_TABLE_KEYWORDS:
                    if nfo.check_token(table_keyword, line):
                        equil_table_indices[table_keyword] = [line_indx+1, len(file_as_list)]
                        table_being_read = table_keyword
                        start_reading_table = True
                        if table_keyword == 'COMPOSITION' and [i for i in line.split() if i in
                                                               EQUIL_COMPOSITION_OPTIONS]:
                            for comp_key in EQUIL_COMPOSITION_OPTIONS:
                                if nfo.check_token(comp_key, line):
                                    self.properties[comp_key] = float(str(nfo.get_token_value(comp_key, line,
                                                                                              file_as_list)))
                line_indx += 1
                continue
            # Find ending index of an equil-related table. There is usually only one per equil file
            if start_reading_table and 'DEPTH' not in line.split():
                for potential_endkeyword in EQUIL_KEYWORDS:
                    if nfo.check_token(potential_endkeyword, line):
                        equil_table_indices[table_being_read][1] = line_indx
                        start_reading_table = False
                        break

            line_indx += 1

        # Read in table if there is one
        if len(equil_table_indices.keys()) > 0:
            self.properties[table_being_read] = nfo.read_table_to_df(file_as_list[
                equil_table_indices[table_being_read][0]:equil_table_indices[table_being_read][1]])
