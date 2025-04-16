from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.hyd_keywords import HYD_ARRAY_KEYWORDS, HYD_TABLE_HEADER_COLS, HYD_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.hyd_keywords import HYD_PRESSURE_KEYWORDS, HYD_SINGLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.hyd_keywords import HYD_KEYWORDS_VALUE_FLOAT, HYD_WATINJ_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.hyd_keywords import HYD_ALQ_KEYWORD, HYD_ALQ_OPTIONS
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import HydraulicsUnits

from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusHydraulicsMethod(DynamicProperty):
    """Class to hold Nexus Hydraulics properties.

    Attributes:
        file (NexusFile): Nexus hydraulics properties file object
        input_number (int): Hydraulics properties method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific hydraulics properties method. Defaults to empty dictionary.
    """

    # General parameters
    file: NexusFile
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                     dict[str, Union[float, pd.DataFrame]]]] = \
        field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem
    ratio_thousands: bool

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 ratio_thousands: bool = True,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        """Initialises the NexusHydraulicsMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the hydraulics method.
            input_number (int): method number for the hydraulics method.
            model_unit_system (UnitSystem): unit system used in the model.
            ratio_thousands (bool): ??
            properties: dictionary of key properties for the hydraulics method. Defaults to None.
        """
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        self.unit_system = model_unit_system
        self.ratio_thousands = ratio_thousands
        super().__init__(input_number=input_number, file=file)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords: dict[str, tuple[str, type]] = {
            'QOIL': ('surface_oil_rate', float),
            'QLIQ': ('surface_liquid_rate', float),
            'QWAT': ('surface_water_rate', float),
            'QGAS': ('surface_gas_rate', float),
            'QWGAS': ('surface_wet_gas_rate', float),
            'MMW': ('mean_molecular_weight', float),
            'WCUT': ('watercut', float),
            'OCUT': ('oilcut', float),
            'PIN': ('inlet_pressure', float),
            'POUT': ('outlet_pressure', float),
            'BHP': ('bottomhole_pressure', float),
            'THP': ('tubinghead_pressure', float),
            'GLR': ('gas_liquid_ratio', float),
            'GOR': ('gas_oil_ratio', float),
            'OGR': ('oil_gas_ratio', float),
            'WGR': ('water_gas_ratio', float),
            'GWR': ('gas_water_ratio', float),
            'WWGR': ('water_wet_gas_ratio', float),
            'LENGTH': ('length', float),
            'DATUM': ('datum_depth', float),
            'DZ': ('depth_change', float),
            'DZW': ('hydraulic_table_vertical_distance', float),
            'GRAD': ('injected_fluid_pressure_gradient', float),
            'VISC': ('viscosity', float),
            'DIAM': ('diameter', float),
            'ROUGHNESS': ('roughness', float),
        }
        return keywords

    @property
    def units(self) -> HydraulicsUnits:
        """Returns the attribute to unit map for the Hydraulics method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return HydraulicsUnits(unit_system=self.unit_system, ratio_thousands=self.ratio_thousands)

    def to_string(self) -> str:
        """Create string with hydraulics data in Nexus file format."""
        printable_str = ''
        hyd_dict = self.properties
        for key, value in hyd_dict.items():
            if isinstance(value, pd.DataFrame):
                if key not in ['HYD_TABLE']:
                    printable_str += f'{key}\n'
                printable_str += value.to_string(na_rep='', index=False) + '\n'
                if key == 'LIMITS':
                    printable_str += 'ENDLIMITS\n'
                printable_str += '\n'
            elif key == 'DESC' and isinstance(value, list):
                for desc_line in value:
                    printable_str += 'DESC ' + desc_line + '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key == 'ALQ':
                printable_str += f'{key}'
                if 'ALQ_PARAM' in hyd_dict.keys():
                    printable_str += f" {hyd_dict['ALQ_PARAM']}"
                if isinstance(value, np.ndarray):
                    printable_str += f" {' '.join([str(val) for val in value])}\n"
                else:
                    printable_str += f' {value}\n'
            elif key == 'WATINJ' and isinstance(value, dict):
                printable_str += f'{key}\n'
                for watinj_key in value.keys():
                    printable_str += f'    {watinj_key} {value[watinj_key]}\n'
            elif key not in ['ALQ', 'ALQ_PARAM', 'WATINJ']:
                if isinstance(value, np.ndarray):
                    printable_str += f"{key} {' '.join([str(val) for val in value])}\n"
                elif value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
        printable_str += '\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus hydraulics file contents and populate the NexusHydraulicsMethod object."""
        file_as_list0 = self.file.get_flat_list_str_file

        # Loop through file_as_list and fix any line continuations that use '>' at the end of the line
        file_as_list: list[str] = []
        if len(file_as_list0) > 0:
            file_as_list = [file_as_list0[0]]
            line_indx = 1
            while line_indx < len(file_as_list0):
                prev_line = file_as_list[-1]
                line = file_as_list0[line_indx]
                if prev_line.rstrip().endswith(('>', '>\n')):
                    file_as_list[-1] = prev_line.split('>')[0] + ' ' + line.strip()
                else:
                    file_as_list.append(line)
                line_indx += 1

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize flags and containers to use to record properties as we iterate through aquifer file contents
        # Dictionary to record start and ending indices for tables
        hyd_table_indices: dict[str, list[int]] = {}
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {'HYD_TABLE': False, 'LIMITS': False}
        start_reading_table = False
        # Containers for handling WATERINJ data
        watinj_dict: dict[str, float] = {}
        found_waterinj = False

        line_indx = 0
        for line in file_as_list:

            # Find arrays of parameters, e.g., QOIL 1.0 10. 100., or GOR 0.0 0.5 1.0
            potential_keyword = nfo.check_list_tokens(HYD_ARRAY_KEYWORDS + HYD_ALQ_KEYWORD, line)
            if potential_keyword is not None and not table_being_read['LIMITS']:
                line_elems = line.split('!')[0].split()
                next_val = nfo.get_expected_token_value(potential_keyword, line, file_as_list)
                if potential_keyword == 'ALQ' and next_val in HYD_ALQ_OPTIONS:
                    self.properties['ALQ_PARAM'] = next_val
                    keyword_index = line_elems.index(next_val)
                else:
                    keyword_index = line_elems.index(potential_keyword)
                self.properties[potential_keyword] = np.fromstring(' '.join(line_elems[keyword_index+1:]), sep=' ')

            # Create WATINJ property if needed
            if nfo.check_token('WATINJ', line):
                found_waterinj = True

            # Handle DATGRAD property
            if nfo.check_token('DATGRAD', line):
                self.properties['DATGRAD'] = nfo.get_expected_token_value('DATGRAD', line, file_as_list)

            # Find HYD key-value pairs, such as LENGTH 3000, DATUM 7000 or DATGRAD GRAD
            potential_keyword = nfo.check_list_tokens(HYD_KEYWORDS_VALUE_FLOAT + HYD_WATINJ_KEYWORDS_VALUE_FLOAT, line)
            if potential_keyword is not None:
                if found_waterinj and potential_keyword in HYD_WATINJ_KEYWORDS_VALUE_FLOAT:
                    watinj_dict[potential_keyword] = float(
                        nfo.get_expected_token_value(potential_keyword, line, file_as_list))
                elif potential_keyword in HYD_KEYWORDS_VALUE_FLOAT:
                    self.properties[potential_keyword] = float(
                        nfo.get_expected_token_value(potential_keyword, line, file_as_list))

            # Find standalone hydraulics keywords
            potential_keyword = nfo.check_list_tokens(HYD_SINGLE_KEYWORDS, line)
            if potential_keyword is not None:
                self.properties[potential_keyword] = ''

            # Find starting and ending indices for hydraulic limits table
            if nfo.check_token('LIMITS', line):
                hyd_table_indices['LIMITS'] = [line_indx+1, len(file_as_list)]
                table_being_read['LIMITS'] = True
                start_reading_table = True
            if nfo.check_token('ENDLIMITS', line):
                hyd_table_indices['LIMITS'][1] = line_indx
                table_being_read['LIMITS'] = False
                start_reading_table = False

            # Find ending index of hydraulics table
            if start_reading_table and table_being_read['HYD_TABLE']:
                for potential_endkeyword in HYD_KEYWORDS:
                    if nfo.check_token(potential_endkeyword, line):
                        hyd_table_indices['HYD_TABLE'][1] = line_indx
                        start_reading_table = False
                        table_being_read['HYD_TABLE'] = False
                        break
            # Find starting index of hydraulics table
            for header_keyword in HYD_TABLE_HEADER_COLS:
                if nfo.check_token(header_keyword, line):
                    hyd_table_indices['HYD_TABLE'] = [line_indx, len(file_as_list)]
                    table_being_read['HYD_TABLE'] = True
                    start_reading_table = True

            line_indx += 1

        # Read in hydraulics tables
        for key in hyd_table_indices.keys():
            if key == 'HYD_TABLE':
                # Get hydraulic table data
                hyd_df: pd.DataFrame = nfo.read_table_to_df(file_as_list[
                    hyd_table_indices[key][0]+1:hyd_table_indices[key][1]], noheader=True)
                # Resolve hydraulic table header
                hyd_df_header_names = [header_name for header_name in file_as_list[
                    hyd_table_indices[key][0]].split('!')[0].split() if not re.search('BHP', header_name)]
                pressure_keyword_map = {'PIN': 'POUT', 'POUT': 'PIN', 'THP': 'BHP'}
                hyd_table_pressure_key = ''  # Determines what type of pressures are in table, i.e., PIN, POUT or BHP
                for pkey in HYD_PRESSURE_KEYWORDS:
                    if pkey in self.properties.keys():
                        if pkey == 'THP':
                            # For VIP compatibility, indicates units
                            # for GOR/GLR are SCF/STB rather than MSCF/STB
                            self.ratio_thousands = False
                        hyd_table_pressure_key = pressure_keyword_map[pkey]
                        break
                hyd_df_header_names = hyd_df_header_names + \
                    [hyd_table_pressure_key+str(i) for i in range(hyd_df.shape[1] - len(hyd_df_header_names))]
                hyd_df.columns = hyd_df_header_names
                # Set appropriate hydraulic table property
                self.properties[key] = hyd_df
            else:
                self.properties[key] = nfo.read_table_to_df(file_as_list[
                    hyd_table_indices[key][0]:hyd_table_indices[key][1]])

        # Correctly set WATINJ properties, if needed
        if found_waterinj:
            self.properties['WATINJ'] = watinj_dict
