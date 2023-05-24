from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.WaterMethod import WaterMethod

from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_list_nexus_water_params
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map


@dataclass  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusWaterParams():
    """Class to hold a single set of water property parameters, i.e., density, compressibility, etc.
    Attributes:
        temperature (Optional[float]): Temperature at which the rest of the water property parameters apply
        salinity (Optional[float]): Salinity at which the rest of the water property parameters apply
        density (Optional[float]): Water density at standard conditions
        compressibility (float): Water compressibility
        formation_volume_factor (float): Water formation volume factor at the given temperature and reference pressure
        viscosity (float): Water viscosity at the given temperature and reference pressure
        viscosity_compressibility (Optional[float]): Water viscosity compressibility
    """
    # General parameters
    compressibility: Optional[float] = None
    formation_volume_factor: Optional[float] = None
    viscosity: Optional[float] = None
    viscosity_compressibility: Optional[float] = None
    temperature: Optional[float] = None
    salinity: Optional[float] = None
    density: Optional[float] = None


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusWaterMethod(WaterMethod):
    """ Class to hold Nexus Water properties
    Attributes:
        file_path (str): Path to the Nexus water file
        method_number (int): Water method number in Nexus fcs file
        reference_pressure (float): Reference pressure for BW and, if CVW is present, for VISW
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame, dict[str, pd.DataFrame]]]):
            Dictionary holding properties for generic dynamic method. Defaults to empty dictionary.
        parameters (list[NexusWaterParams]): list of water parameters, such as density, viscosity, etc.
    """
    file_path: str
    reference_pressure: Optional[float] = None
    properties: dict[str, Union[str, int, float, Enum, list[str],
                                pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)
    parameters: list[NexusWaterParams] = field(default_factory=get_empty_list_nexus_water_params)

    def __init__(self, file_path: str, method_number: int, reference_pressure: Optional[float] = None,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                                      dict[str, Union[float, pd.DataFrame]]]]] = None,
                 parameters: Optional[list[NexusWaterParams]] = None):
        self.file_path = file_path
        self.reference_pressure = reference_pressure
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        if parameters is not None:
            self.parameters = parameters
        else:
            self.parameters = []
        super().__init__(method_number=method_number)

    @staticmethod
    def nexus_mapping() -> dict[str, tuple[str, type]]:
        """returns a dictionary of mapping from nexus keyword to attribute name"""

        nexus_mapping: dict[str, tuple[str, type]] = {
            'DENW': ('density', float),
            'CW': ('compressibility', float),
            'BW': ('formation_volume_factor', float),
            'VISW': ('viscosity', float),
            'CVW': ('viscosity_compressibility', float)
        }
        return nexus_mapping

    def __repr__(self) -> str:
        """Pretty printing water data"""
        param_to_nexus_keyword_map = invert_nexus_map(NexusWaterMethod.nexus_mapping())

        printable_str = f'\nFILE_PATH: {self.file_path}\n'
        printable_str += f'PREF: {self.reference_pressure}\n'
        water_dict = self.properties
        for key, value in water_dict.items():
            if isinstance(value, Enum):
                printable_str += f'{key}: {value.name}\n'
            else:
                printable_str += f'{key}: {value}\n'
        water_params = self.parameters
        temp_val = None
        sal_val = None
        for i in range(len(water_params)):
            water_param_dict = water_params[i].__dict__
            space_prefix = ''
            if water_param_dict['temperature']:
                if water_param_dict['temperature'] != temp_val:
                    printable_str += f"TEMP: {water_param_dict['temperature']}\n"
                    temp_val = water_param_dict['temperature']
                space_prefix += '    '
            if water_param_dict['salinity']:
                if water_param_dict['salinity'] != sal_val:
                    printable_str += f"{space_prefix}SALINITY: {water_param_dict['salinity']}\n"
                    sal_val = water_param_dict['salinity']
                space_prefix += '    '
            for key in param_to_nexus_keyword_map.keys():
                if water_param_dict[key]:
                    printable_str += f'{space_prefix}{param_to_nexus_keyword_map[key]}: {water_param_dict[key]}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus Water file contents and populate NexusWaterMethod object
        """
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Initialize properties
        water_props_dict_none: dict[str, Optional[float]] = {'DENW': None, 'CW': None, 'BW': None,
                                                             'VISW': None, 'CVW': None}
        water_props_dict: dict[str, Optional[float]] = water_props_dict_none.copy()

        line_indx = 0
        reading_props = False  # Flag indicating if actively reading a property section
        found_params = False  # Flag inidicating if identified any WATER keywords
        temp: Optional[float] = None  # Variable to hold temperature for property section
        sal: Optional[float] = None  # Variable to hold salinity for property section
        for line in file_as_list:

            # Read in reference pressure
            if nfo.check_token('PREF', line):  # Reference pressure
                self.reference_pressure = float(nfo.get_expected_token_value('PREF', line, file_as_list))

            # Check if reading properties
            if nfo.check_token('CW', line):
                reading_props = True
                found_params = True

            # If found a new property section based on TEMP or SALINITY repeat
            if reading_props and (nfo.check_token('TEMP', line) or nfo.check_token('SALINITY', line)):
                reading_props = False
                # Append new parameters to list of water parameters
                params = NexusWaterParams(temperature=temp,
                                          salinity=sal,
                                          density=water_props_dict['DENW'],
                                          compressibility=water_props_dict['CW'],
                                          formation_volume_factor=water_props_dict['BW'],
                                          viscosity=water_props_dict['VISW'],
                                          viscosity_compressibility=water_props_dict['CVW']
                                          )
                self.parameters.append(params)
                # Reset property dictionary
                water_props_dict = water_props_dict_none.copy()  # Reset

            # Read in relevant water properties in line
            if nfo.check_token('TEMP', line):
                temp = float(nfo.get_expected_token_value('TEMP', line, file_as_list))
            if nfo.check_token('SALINITY', line):
                sal = float(nfo.get_expected_token_value('SALINITY', line, file_as_list))
            for key in water_props_dict.keys():
                if nfo.check_token(key, line):
                    found_params = True
                    water_props_dict[key] = float(nfo.get_expected_token_value(key, line, file_as_list))

            line_indx += 1

        if found_params:
            # Append new parameters to list of water parameters
            params = NexusWaterParams(temperature=temp,
                                      salinity=sal,
                                      density=water_props_dict['DENW'],
                                      compressibility=water_props_dict['CW'],
                                      formation_volume_factor=water_props_dict['BW'],
                                      viscosity=water_props_dict['VISW'],
                                      viscosity_compressibility=water_props_dict['CVW']
                                      )
            self.parameters.append(params)
