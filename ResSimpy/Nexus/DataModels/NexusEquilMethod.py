"""Class storing Nexus Equilibration method properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Optional
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import SUnits, TemperatureUnits, UnitSystem
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_INTSAT_KEYWORDS, EQUIL_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_TABLE_KEYWORDS, EQUIL_SINGLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_COMPOSITION_OPTIONS
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_KEYWORDS
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import EquilUnits

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusEquilMethod(DynamicProperty):
    """Class to hold Nexus Equil properties.

    Attributes:
        file (NexusFile): Nexus equilibration file object
        input_number (int): Equilibration method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific equilibration method. Defaults to empty dictionary.
    """

    # General parameters
    file: NexusFile
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray,
                                pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        """Initialises the NexusEquilMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the equil method.
            input_number (int): method number for the equil method.
            model_unit_system (UnitSystem): unit system used in the model.
            properties: dictionary of key properties for the equil method. Defaults to None.
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
            'PINIT': ('initial_pressure', float),
            'DINIT': ('datum_depth', float),
            'DEPTH': ('depth', float),
            'X': ('x', float),
            'Y': ('y', float),
            'TINIT': ('initial_temperature', float),
            'TEMP': ('temperature', float),
            'GOC': ('gas_oil_contact_depth', float),
            'WOC': ('water_oil_contact_depth', float),
            'GOC_PALEO': ('gas_oil_contact_depth', float),
            'WOC_PALEO': ('water_oil_contact_depth', float),
            'GWC': ('gas_water_contact_depth', float),
            'PCGOC': ('gas_oil_capillary_pressure_at_gas_oil_contact', float),
            'PCWOC': ('water_oil_capillary_pressure_at_water_oil_contact', float),
            'PCGWC': ('gas_water_capillary_pressure_at_gas_water_contact', float),
            'PSAT': ('saturation_pressure', float),
            'API': ('oil_api_gravity', float),
        }
        return keywords

    @property
    def units(self) -> EquilUnits:
        """Returns the attribute to unit map for the Equil method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return EquilUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with equilibration data in Nexus file format."""
        printable_str = ''
        equil_dict = self.properties
        for key, value in equil_dict.items():
            if isinstance(value, pd.DataFrame):
                table_text = f'{key}'
                if key == 'COMPOSITION':
                    if 'X' in equil_dict.keys():
                        table_text += f" X {equil_dict['X']}"
                    if 'Y' in equil_dict.keys():
                        table_text += f" Y {equil_dict['Y']}"
                printable_str += f'{table_text}\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif value == '':
                printable_str += f'{key}\n'
            elif key in ['INTSAT', 'VAITS']:
                if value == 'MOBILE':
                    printable_str += f'{key}\n    MOBILE\n'
                    for mobkey in ['SORWMN', 'SORGMN', 'SGCMN']:
                        if mobkey in equil_dict.keys():
                            printable_str += f'        {mobkey} {equil_dict[mobkey]}\n'
                for vaitkey in ['VAITS_TOLSG', 'VAITS_TOLSW']:
                    if vaitkey in equil_dict.keys():
                        printable_str += f'    {vaitkey} {equil_dict[vaitkey]}\n'
            elif key == 'OVERREAD':
                if isinstance(value, list):
                    printable_str += f"OVERREAD {' '.join(value)}\n"
            elif key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif key not in ['DESC', 'SORWMN', 'SORGMN', 'SGCMN', 'VAITS_TOLSG', 'VAITS_TOLSW',
                             'OVERREAD', 'INTSAT', 'VAITS', 'MOBILE', 'X', 'Y']:
                printable_str += f'{key} {value}\n'
        printable_str += '\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus equilibration file contents and populate NexusEquilMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

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
                        self.properties[key] = float(nfo.get_expected_token_value(key, line, file_as_list))
            if nfo.check_token('AUTOGOC_COMP', line):
                self.properties['AUTOGOC_COMP'] = nfo.get_expected_token_value('AUTOGOC_COMP', line, file_as_list)
            if nfo.check_token('OVERREAD', line):
                overread_vals = line.split('!')[0].split('OVERREAD')[1].split()
                if 'OVERREAD' in self.properties.keys() and isinstance(self.properties['OVERREAD'], list):
                    self.properties['OVERREAD'] += overread_vals
                else:
                    self.properties['OVERREAD'] = overread_vals
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
                        if fo.get_token_value(key, line, file_as_list) == 'MOBILE':
                            self.properties[key] = 'MOBILE'
                        else:
                            self.properties[key] = ''

            # Find starting index of an equil-related table. There is usually only one per equil file
            if [i for i in line.split() if i in EQUIL_TABLE_KEYWORDS]:
                for table_keyword in EQUIL_TABLE_KEYWORDS:
                    if nfo.check_token(table_keyword, line):
                        equil_table_indices[table_keyword] = [line_indx + 1, len(file_as_list)]
                        table_being_read = table_keyword
                        start_reading_table = True
                        if table_keyword == 'COMPOSITION' and [i for i in line.split() if i in
                                                               EQUIL_COMPOSITION_OPTIONS]:
                            for comp_key in EQUIL_COMPOSITION_OPTIONS:
                                if nfo.check_token(comp_key, line):
                                    self.properties[comp_key] = float(nfo.get_expected_token_value(comp_key,
                                                                                                   line, file_as_list))
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
        for key in equil_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                equil_table_indices[key][0]:equil_table_indices[key][1]])
