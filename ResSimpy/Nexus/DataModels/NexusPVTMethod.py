"""Class to hold Nexus PVT properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_BLACKOIL_PRIMARY_KEYWORDS, PVT_TYPE_KEYWORDS, PVT_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOS_METHODS, PVT_EOSOPTIONS_PRIMARY_WORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_PRIMARY_KEYS_INT, PVT_TABLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_TABLES_WITH_ENDWORDS, PVT_TABLES_WITHOUT_ENDWORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT, PVT_EOSOPTIONS_TRANS_KEYS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_TRANS_TEST_KEYS, PVT_EOSOPTIONS_PHASEID_KEYS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_TERTIARY_KEYS, PVT_ALL_TABLE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_UNSAT_TABLE_INDICES
from ResSimpy.Enums.FluidTypeEnums import PvtType
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import PVTUnits

from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_list_str
from ResSimpy.Utils.factory_methods import get_empty_eosopt_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo


@dataclass(kw_only=True, repr=False)
class NexusPVTMethod(DynamicProperty):
    """Class to hold Nexus PVT properties.

    Attributes:
        file (NexusFile): Nexus PVT file object
        input_number (int): PVT method number in Nexus fcs file
        pvt_type (Optional[str]): Type of PVT method, e.g., BLACKOIL, GASWATER or EOS. Defaults to None
        eos_nhc (Optional[int]): Number of hydrocarbon components. Defaults to None
        eos_temp (Optional[float]): Default temperature for EOS method. Defaults to None
        eos_components (Optional[list[str]]): Specifies component names
        eos_options (dict[str, Union[str, int, float, pd.DataFrame, list[str], dict[str, float],
            tuple[str, dict[str, float]], dict[str, pd.DataFrame]]]): Dictionary containing various EOS options
            as specified in the PVT file. Defaults to empty dictionary.
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding all properties for a specific PVT method. Defaults to empty dictionary.
    """

    # General parameters
    file: NexusFile
    pvt_type: Optional[PvtType] = None
    eos_nhc: Optional[int] = None  # Number of hydrocarbon components
    eos_temp: Optional[float] = None  # Default temperature for EOS method
    eos_components: Optional[list[str]] = field(default_factory=get_empty_list_str)
    eos_options: dict[str, Union[
        str, int, float, pd.DataFrame, list[str], dict[str, float], tuple[str, dict[str, float]], dict[
            str, pd.DataFrame]]] \
        = field(default_factory=get_empty_eosopt_dict_union)
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray,
                                pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 pvt_type: Optional[PvtType] = None,
                 eos_nhc: Optional[int] = None, eos_temp: Optional[float] = None,
                 eos_components: Optional[list[str]] = None,
                 eos_options: Optional[dict[str, Union[str, int, float, pd.DataFrame, list[str], dict[str, float],
                                       tuple[str, dict[str, float]], dict[str, pd.DataFrame]]]] = None,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None) -> None:
        """Initialises the NexusGasliftMethod class.

        Args:
            file (NexusFile): NexusFile object associated with the PVT method.
            input_number (int): method number for the PVT method.
            model_unit_system (UnitSystem): unit system from the model.
            pvt_type (Optional[PvtType]): Type of PVT method, e.g., BLACKOIL, GASWATER or EOS. Defaults to None.
            eos_nhc (Optional[int]): Number of hydrocarbon components for EOS method. Defaults to None.
            eos_temp (Optional[float]): Default temperature for EOS method. Defaults to None.
            eos_components (Optional[list[str]]): Specifies component names for EOS method. Defaults to None.
            eos_options: Dictionary containing various EOS options as specified in the PVT file. Defaults to None.
            properties: dictionary of properties for the PVT method.
        """
        if pvt_type is not None:
            self.pvt_type = pvt_type
        if eos_nhc is not None:
            self.eos_nhc = eos_nhc
        if eos_temp is not None:
            self.eos_temp = eos_temp
        if eos_components is not None:
            self.eos_components = eos_components
        else:
            self.eos_components = []
        if eos_options is not None:
            self.eos_options = eos_options
        else:
            self.eos_options = {}
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
            'PRES': ('pressure', float),
            'TEMP': ('temperature', float),
            'DP': ('delta_pressure', float),
            'DENOIL': ('oil_density', float),
            'DENGAS': ('gas_density', float),
            'API': ('oil_api_gravity', float),
            'SPECG': ('gas_specific_gravity', float),
            'MWOR': ('molecular_weight_of_residual_oil', float),
            'VO': ('oil_viscosity', float),
            'VG': ('gas_viscosity', float),
            'BO': ('oil_formation_volume_factor', float),
            'BG': ('gas_formation_volume_factor', float),
            'RS': ('solution_gas_oil_ratio', float),
            'RV': ('solution_oil_gas_ratio', float),
            'PSAT': ('saturation_pressure', float),
            'GOR': ('gas_oil_ratio', float),
            'OGR': ('oil_gas_ratio', float),
            'CV': ('gas_heat_capacity_at_constant_volume', float),
            'CP': ('gas_heat_capacity_at_constant_pressure', float),
            'BOFAC': ('oil_fvf_over_oil_fvf_at_saturation_pressure', float),
            'VOFAC': ('oil_viscosity_over_oil_viscosity_at_saturation_pressure', float),
            'BGFAC': ('gas_fvf_over_gas_fvf_at_saturation_pressure', float),
            'VGFAC': ('gas_viscosity_over_gas_viscosity_at_saturation_pressure', float),
            'CVFAC': ('gas_heat_capacity_at_constant_volume_over_cv_at_saturation_pressure', float),
            'CPFAC': ('gas_heat_capacity_at_constant_pressure_over_cp_at_saturation_pressure', float),
            'PC': ('critical_pressure', float),
            'TC': ('critical_temperature', float),
            'VC': ('critical_volume', float),
        }
        return keywords

    @property
    def units(self) -> PVTUnits:
        """Returns the attribute to unit map for the PVT method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return PVTUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with PVT data in Nexus file format."""
        printable_str = ''
        pvt_dict = self.properties
        # Print description if present
        if 'DESC' in pvt_dict.keys() and isinstance(pvt_dict['DESC'], list):
            for desc_line in pvt_dict['DESC']:
                printable_str += 'DESC ' + desc_line + '\n'
        # Print PVT type and associated properties
        printable_str += '' if self.pvt_type is None else f'{self.pvt_type.value}'
        if self.eos_nhc is not None:
            printable_str += f' NHC {self.eos_nhc}'
        for pvt_key in PVT_BLACKOIL_PRIMARY_KEYWORDS:
            if pvt_key in pvt_dict.keys():
                printable_str += f' {pvt_key} {pvt_dict[pvt_key]}'
        printable_str += '\n'
        if 'DRYGAS_MFP' in pvt_dict.keys():
            printable_str += 'DRYGAS_MFP\n'
        # Print EOS-specific required parameters, if present
        if self.eos_components is not None:
            if len(self.eos_components) > 0:
                printable_str += f"COMPONENTS {' '.join(self.eos_components)}\n"
        if self.eos_temp is not None:
            printable_str += f'TEMP {self.eos_temp}\n'
        for key, value in pvt_dict.items():
            if isinstance(value, pd.DataFrame):
                printable_str += f'{key}\n'
                if key == 'IGS_CP':
                    printable_str += value.to_string(na_rep='', index=False, header=False) + '\n'
                else:
                    printable_str += value.to_string(na_rep='', index=False,
                                                     float_format=lambda x: f'{x:.9f}') + '\n'
                if key in PVT_TABLES_WITH_ENDWORDS:
                    printable_str += 'END'+key+'\n'
                printable_str += '\n'
            elif isinstance(value, dict):
                for subkey in value.keys():
                    printable_str += f"{key.replace('_', ' ')} {subkey}\n"
                    df = value[subkey]
                    if isinstance(df, pd.DataFrame):
                        printable_str += df.to_string(na_rep='', index=False,
                                                      float_format=lambda x: f'{x:.9f}') + '\n'
                    printable_str += '\n'
            elif isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key not in [*PVT_BLACKOIL_PRIMARY_KEYWORDS, 'NHC', 'DESC', 'DRYGAS_MFP']:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
        if len(self.eos_options.keys()) > 0:
            pvt_dict = self.eos_options
            printable_str += 'EOSOPTIONS'
            if 'EOS_METHOD' in pvt_dict.keys():
                printable_str += f" {pvt_dict['EOS_METHOD']}"
            printable_str += '\n'
            for key, value in pvt_dict.items():
                if key == 'EOS_OPT_PRIMARY_LIST' and isinstance(value, list):
                    for token in value:
                        printable_str += f'    {token}\n'
                elif isinstance(value, tuple):
                    printable_str += f'    {key} {value[0]}'
                    val_dict: dict[str, float] = value[1]
                    for val_key, val_val in val_dict.items():
                        printable_str += f' {val_key} {val_val}'
                    printable_str += '\n'
                elif isinstance(value, dict):
                    printable_str += f'    {key}'
                    for subkey, subvalue in value.items():
                        printable_str += f' {subkey} {subvalue}'
                    printable_str += '\n'
                elif key not in ['EOS_METHOD']:
                    printable_str += f'    {key} {value}\n'
        return printable_str

    def __populate_eos_opts_to_tertiary_keys(self, primary_key: str, primary_key_default_val: str, single_line: str,
                                             line_list: list[str], list_of_secondary_keys: list[str]) -> None:
        """Utility function to populate complex EOS options structures, from primary to tertiary keyword level.

        Applies to TRANSITION, TRANS_TEST and PHASEID Nexus EOS options.

        Args:
            primary_key (str): primary keyword, e.g., TRANSITION or PHASEID
            primary_key_default_val (str): default secondary keyword, or primary key value, e.g., TEST
            single_line (str): single line as read from input PVT file
            line_list (list[str]): list of strings that comprise input PVT file
            list_of_secondary_keys (list[str]): list of secondary keywords associated with the given primary keyword
        """
        if nfo.check_token(primary_key, single_line):
            self.eos_options[primary_key] = primary_key_default_val  # Set default value
            if nfo.get_expected_token_value(primary_key, single_line, line_list) in list_of_secondary_keys:
                self.eos_options[primary_key] = nfo.get_expected_token_value(primary_key, single_line, line_list)
        if [i for i in single_line.split() if i in list_of_secondary_keys]:
            for secondary_key in list_of_secondary_keys:
                if nfo.check_token(secondary_key, single_line):
                    self.eos_options[primary_key] = secondary_key
                    for tertiary_key in PVT_EOSOPTIONS_TERTIARY_KEYS:
                        if nfo.check_token(tertiary_key, single_line):
                            if isinstance(self.eos_options[primary_key], str):  # Convert to tuple
                                self.eos_options[primary_key] = (secondary_key, {})

                            secondary_eos_option = self.eos_options[primary_key]
                            if not isinstance(secondary_eos_option, tuple) or \
                                    not isinstance(secondary_eos_option[1], dict):
                                raise ValueError(f"EOS secondary key invalid: {secondary_key}")
                            secondary_eos_option[1][tertiary_key] = float(
                                nfo.get_expected_token_value(tertiary_key, single_line, line_list))

    def __find_pvt_table_starting_index(self, table_key: str, single_line: str, line_list: list[str],
                                        table_indices: dict[str, list[int]],
                                        table_indices_dict: dict[str, dict[str, list[int]]],
                                        table_flag: dict[str, bool], l_index: int,
                                        unsat_obj: dict[str, list[str]] | None = None) -> Optional[int]:
        """Utility function to find the starting line index of a specified PVT table.

        Args:
            table_key (str): specified PVT table name or undersaturated index, such as, PSAT or RSSAT or PRES
            single_line (str): single line as read from input PVT file
            line_list (list[str]): list of strings that comprise input PVT file
            table_indices ([dict[str, list[int]]): dictionary to store the
                starting and ending line index of tables
            table_indices_dict (dict[str, dict[str, list[int]]]): dictionary to store the
                starting and ending line index of tables, for undersaturated tables
            table_flag (bool): flag to tell if a table is currently being read (True) or not (False)
            l_index (int): current line index
            unsat_obj (dict[str, list[str]]): track saturation pressures from which undersaturated branches emanate

        Raises:
            ValueError: If a property table key does not have a numerical value

        Returns:
            int: Updated line index
        """
        if unsat_obj is None:
            unsat_obj = {}
        if table_key not in PVT_UNSAT_TABLE_INDICES:  # All tables except undersaturated tables
            if nfo.check_token(table_key, single_line):
                table_indices[table_key] = [l_index + 1, len(line_list)]
                table_flag[table_key] = True
                return l_index + 1
        else:  # Handle undersaturated tables
            if table_key == 'PRES':
                table_name = 'UNSATGAS'
                full_table_name = table_name + '_PRES'
            else:
                table_name = 'UNSATOIL'
                full_table_name = table_name + '_' + table_key
            if nfo.check_token(table_name, single_line) and nfo.check_token(table_key, single_line):
                if fo.get_token_value(table_key, single_line, line_list) is None:
                    raise ValueError(f'Property {table_key} does not have a numerical value.')
                unsat_obj[table_key].append(nfo.get_expected_token_value(table_key, single_line, line_list))
                if full_table_name in table_indices_dict.keys():
                    table_indices_dict[full_table_name][unsat_obj[table_key][-1]] = [l_index + 1, len(line_list)]
                else:
                    table_indices_dict[full_table_name] = {unsat_obj[table_key][-1]: [l_index + 1, len(line_list)]}
                table_flag[table_name] = True
                return l_index + 1
        return None

    def __find_pvt_table_ending_index(self, table_key: str, single_line: str,
                                      table_indices: dict[str, list[int]],
                                      table_indices_dict: dict[str, dict[str, list[int]]],
                                      l_index: int, table_flag: dict[str, bool],
                                      table_has_endkeyword: bool, reading_flag: bool,
                                      unsat_obj: dict[str, list[str]] = {}) -> bool:
        """Utility function to find the ending line index of a specified PVT table.

        Args:
            table_key (str): specified PVT table name or undersaturated index, such as, PSAT or RSSAT or PRES
            single_line (str): single line as read from input PVT file
            table_indices ([dict[str, list[int]]): dictionary to store the
                starting and ending line index of tables
            table_indices_dict (dict[str, dict[str, list[int]]]): dictionary to store the
                starting and ending line index of tables, for undersaturated tables
            l_index (int): current line index
            table_flag (dict[str, bool]): flag to tell if a table is currently being read (True) or not (False)
            table_has_endkeyword (bool): True if table name, e.g., PROPS, has end keyword, i.e., ENDPROPS, else False
            reading_flag (bool): True if any table is being read, otherwise False
            unsat_obj (dict[str, list[str]]): track saturation pressures from which undersaturated branches emanate

        Returns:
            bool: True if still reading table, but if identified the ending line index, return False
        """
        end_flag_found = False
        if table_key not in PVT_UNSAT_TABLE_INDICES:  # All tables except undersaturated tables
            table_name = table_key
            full_table_name = table_key
        else:  # Handle undersaturated tables
            if table_key == 'PRES':
                table_name = 'UNSATGAS'
                full_table_name = table_name + '_PRES'
            else:
                table_name = 'UNSATOIL'
                full_table_name = table_name + '_' + table_key
        # if not table_has_endkeyword and [i for i in single_line.split() if i in PVT_KEYWORDS]:
        if not table_has_endkeyword:
            for keyword in PVT_KEYWORDS:
                if nfo.check_token(keyword, single_line):
                    end_flag_found = True
        if table_has_endkeyword and nfo.check_token('END' + table_name, single_line):
            end_flag_found = True
        if (full_table_name in table_indices.keys() or full_table_name in table_indices_dict.keys()) and \
                end_flag_found and table_flag[table_name]:
            if table_key not in PVT_UNSAT_TABLE_INDICES:  # All tables except undersaturated tables
                table_indices[table_name][1] = l_index
            else:  # Handle undersaturated tables
                table_indices_dict[full_table_name][unsat_obj[table_key][-1]][1] = l_index
            table_flag[table_name] = False
            reading_flag = False
        return reading_flag

    def read_properties(self) -> None:
        """Read Nexus PVT file contents and populate the NexusPVTMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

        # Initialize flags and containers used to record properties as we iterate through pvt file contents
        # Dictionary to record start and ending indices for tables
        pvt_table_indices: dict[str, list[int]] = {}
        pvt_table_indices_dict: dict[str, dict[str, list[int]]] = {}
        # Flag to tell when to start reading a table
        start_reading_table: bool = False
        trans_flag = False
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {}
        for table_name in PVT_ALL_TABLE_KEYWORDS:
            table_being_read[table_name] = False
        # Dictionary of lists to track saturation pressures from which undersaturated branches emanate
        pvt_unsat_keys: dict[str, list[str]] = {}
        for indx in PVT_UNSAT_TABLE_INDICES:
            pvt_unsat_keys[indx] = []

        line_indx = 0
        for line in file_as_list:

            # Determine PVT type, i.e., BLACKOIL, WATEROIL, EOS, etc.
            for pvt_type in PVT_TYPE_KEYWORDS:
                if nfo.check_token(pvt_type, line):
                    self.pvt_type = PvtType[pvt_type]

            # Extract blackoil fluid density parameters
            for fluid_param in PVT_BLACKOIL_PRIMARY_KEYWORDS:
                if nfo.check_token(fluid_param, line):
                    self.properties[fluid_param] = float(nfo.get_expected_token_value(
                        fluid_param, line, file_as_list, custom_message=f"Property {fluid_param} does \
                        not have a numerical value."))
            if nfo.check_token('DRYGAS_MFP', line):
                self.properties['DRYGAS_MFP'] = True

            # For EOS or compositional models, get required parameters
            if nfo.check_token('NHC', line):  # Get number of components
                self.eos_nhc = int(nfo.get_expected_token_value('NHC', line,
                                                                file_as_list,
                                                                custom_message="Property NHC does not \
                                                                have a numerical value."))
            if nfo.check_token('COMPONENTS', line):  # Get NHC components
                elems = line.split()
                components_index = elems.index('COMPONENTS')
                if self.eos_nhc and self.eos_nhc > 0:
                    self.eos_components = elems[components_index + 1:components_index + 1 + int(self.eos_nhc)]
            if nfo.check_token('TEMP', line):  # Get default EOS temperature
                self.eos_temp = float(nfo.get_expected_token_value(
                    'TEMP', line, file_as_list, custom_message="Property TEMP does not have a numerical value."))

            # Check for EOS options
            if nfo.check_token('EOSOPTIONS', line):
                if nfo.get_expected_token_value('EOSOPTIONS', line, file_as_list) in PVT_EOS_METHODS:
                    self.eos_options['EOS_METHOD'] = nfo.get_expected_token_value('EOSOPTIONS', line, file_as_list)
                else:
                    self.eos_options['EOS_METHOD'] = 'PR'
            # Find EOS single-word options, like CAPILLARYFLASH and add to list
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PRIMARY_WORDS]:
                if 'EOS_OPT_PRIMARY_LIST' not in self.eos_options.keys():
                    self.eos_options['EOS_OPT_PRIMARY_LIST'] = []
                if not isinstance(self.eos_options['EOS_OPT_PRIMARY_LIST'], list):
                    raise ValueError(f"EOS_OPT_PRIMARY_LIST should be a list, instead \
                                     got {self.eos_options['EOS_OPT_PRIMARY_LIST']}")
                self.eos_options['EOS_OPT_PRIMARY_LIST'].extend([i for i in line.split() if i
                                                                 in PVT_EOSOPTIONS_PRIMARY_WORDS])
            # Find EOS key-value pairs, like LI_FACT 0.9 or FUGERR 5
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT]:
                for key in PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT:
                    if nfo.check_token(key, line):
                        self.eos_options[key] = float(nfo.get_expected_token_value(key, line, file_as_list))
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PRIMARY_KEYS_INT]:
                for key in PVT_EOSOPTIONS_PRIMARY_KEYS_INT:
                    if nfo.check_token(key, line):
                        self.eos_options[key] = int(nfo.get_expected_token_value(key, line, file_as_list))
            # Read TRANSITION, TRANS_TEST and PHASEID eos options, if present
            primary_keys2populate = ['TRANSITION', 'TRANS_TEST', 'PHASEID']
            primary_keys2populate_defaults = ['TEST', 'INCRP', '']
            secondary_keys = [PVT_EOSOPTIONS_TRANS_KEYS, PVT_EOSOPTIONS_TRANS_TEST_KEYS, PVT_EOSOPTIONS_PHASEID_KEYS]
            if [i for i in line.split() if i in primary_keys2populate]:
                trans_flag = True
            if trans_flag:
                for index in range(len(primary_keys2populate)):
                    pkey = primary_keys2populate[index]
                    p2key = primary_keys2populate_defaults[index]
                    sec_key = secondary_keys[index]
                    self.__populate_eos_opts_to_tertiary_keys(pkey, p2key, line, file_as_list, sec_key)
            # Read TRANS_OPTIMIZATION eos options, if present
            if nfo.check_token('TRANS_OPTIMIZATION', line):
                new_dict: dict[str, float] = {}
                for tert_key in PVT_EOSOPTIONS_TERTIARY_KEYS:
                    if nfo.check_token(tert_key, line):
                        potential_value = float(nfo.get_expected_token_value(tert_key, line, file_as_list))
                        if isinstance(potential_value, float):
                            new_dict[tert_key] = potential_value
                            self.eos_options['TRANS_OPTIMIZATION'] = new_dict

            # Identify beginning and ending line indices for different kinds tables in PVT file
            if start_reading_table:  # Figure out ending line indices for tables
                for table in PVT_TABLES_WITHOUT_ENDWORDS:
                    start_reading_table = self.__find_pvt_table_ending_index(table, line, pvt_table_indices,
                                                                             pvt_table_indices_dict,
                                                                             line_indx, table_being_read, False,
                                                                             start_reading_table)
                for table in PVT_TABLES_WITH_ENDWORDS:
                    start_reading_table = self.__find_pvt_table_ending_index(table, line, pvt_table_indices,
                                                                             pvt_table_indices_dict,
                                                                             line_indx, table_being_read, True,
                                                                             start_reading_table)
                for table in PVT_UNSAT_TABLE_INDICES:
                    start_reading_table = self.__find_pvt_table_ending_index(table, line, pvt_table_indices,
                                                                             pvt_table_indices_dict,
                                                                             line_indx, table_being_read, False,
                                                                             start_reading_table, pvt_unsat_keys)
            # Figure out beginning line indices for tables
            table_found = False
            for table in PVT_TABLE_KEYWORDS + PVT_UNSAT_TABLE_INDICES:
                if table in PVT_UNSAT_TABLE_INDICES:  # Work on undersaturated tables
                    new_line_indx = self.__find_pvt_table_starting_index(table, line, file_as_list, pvt_table_indices,
                                                                         pvt_table_indices_dict, table_being_read,
                                                                         line_indx, pvt_unsat_keys)
                else:  # All other tables
                    new_line_indx = self.__find_pvt_table_starting_index(table, line, file_as_list, pvt_table_indices,
                                                                         pvt_table_indices_dict, table_being_read,
                                                                         line_indx)
                if new_line_indx is not None:
                    line_indx = new_line_indx
                    table_found = True
                    break
            if table_found:
                continue
            # Check if this line represents the header of a PVT table
            table_header_row_options = ['PRES', 'DP', 'RV', 'INDEX', 'COMPONENT']
            header_row_flag = False
            for hr in table_header_row_options:
                if nfo.check_token(hr, line):
                    header_row_flag = True
            reading_a_table_flag = False
            for table_name in PVT_ALL_TABLE_KEYWORDS:
                if table_being_read[table_name]:
                    reading_a_table_flag = True
            if header_row_flag and reading_a_table_flag and not start_reading_table:
                start_reading_table = True  # If header row, start reading

            line_indx += 1

        # Read in tables
        for key in pvt_table_indices.keys():
            if key == 'IGS_CP':
                self.properties[key] = nfo.read_table_to_df(file_as_list[
                    pvt_table_indices[key][0]:pvt_table_indices[key][1]], noheader=True)
            else:
                self.properties[key] = nfo.read_table_to_df(file_as_list[
                    pvt_table_indices[key][0]:pvt_table_indices[key][1]])
        for key in pvt_table_indices_dict.keys():
            self.properties[key] = {}
            for subkey in pvt_table_indices_dict[key].keys():
                property_key = self.properties[key]
                if not isinstance(property_key, dict):
                    raise ValueError(f"Property is not a dictionary: {str(self.properties[key])}")
                property_key[subkey] = nfo.read_table_to_df(file_as_list[
                                                            pvt_table_indices_dict[key][subkey][0]:
                                                            pvt_table_indices_dict[key][subkey][1]])
