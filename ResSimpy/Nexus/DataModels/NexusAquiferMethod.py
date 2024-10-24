"""Class to hold Nexus Aquifer properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_SINGLE_KEYWORDS, AQUIFER_TABLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_KEYWORDS_VALUE_FLOAT, AQUIFER_KEYWORDS_VALUE_INT
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_KEYWORDS, AQUIFER_TYPE_KEYWORDS
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import AquiferUnits

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusAquiferMethod(DynamicProperty):
    """Class to hold Nexus Aquifer properties.

    Attributes:
        file (NexusFile): Nexus aquifer properties file object
        input_number (int): Aquifer properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific aquifer properties method. Defaults to empty dictionary.
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
        """Initialises the NexusAquiferMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the aquifer method.
            input_number (int): method number for the aquifer method.
            model_unit_system (UnitSystem): unit system used in the model.
            properties: dictionary of properties for the aquifer method. Defaults to None.
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
            'BAQ': ('carter_tracy_constant', float),
            'CT': ('total_compressibility', float),
            'POR': ('porosity', float),
            'H': ('thickness', float),
            'RO': ('radius_to_inner_perimeter', float),
            'RE': ('radius_to_exterior_perimeter', float),
            'S': ('fraction_of_circular_boundary', float),
            'W': ('linear_aquifer_width', float),
            'L': ('linear_aquifer_length', float),
            'TC': ('time_conversion_factor', float),
            'VISC': ('viscosity', float),
            'K': ('permeability', float),
            'PAQI': ('initial_aquifer_pressure', float),
            'DAQI': ('datum_depth', float),
            'PI': ('productivity_index', float),
            'WEI': ('initial_encroachable_water_volume', float),
            'WAQI': ('initial_aquifer_volume', float),
        }
        return keywords

    @property
    def units(self) -> AquiferUnits:
        """Returns the attribute to unit map for the Aquifer method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return AquiferUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with aquifer data in Nexus file format."""
        printable_str = ''
        aquifer_dict = self.properties
        for key, value in aquifer_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += f'{key}\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n'
                if key == 'TRACER':
                    printable_str += 'ENDTRACER\n'
                printable_str += '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif key not in ['DESC']:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
        printable_str += '\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus aquifer file contents and populate the NexusValveMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

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
