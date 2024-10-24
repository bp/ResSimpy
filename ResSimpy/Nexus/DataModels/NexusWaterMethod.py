"""Class to hold Nexus Water properties."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import numpy as np
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_list_nexus_water_params
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import WaterUnits


@dataclass  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusWaterParams:
    """Class to represent a single set of water property parameters, i.e., density, compressibility, etc.

    Attributes:
        temperature (Optional[float]): Temperature at which the rest of the water property parameters apply
        salinity (Optional[float]): Salinity at which the rest of the water property parameters apply
        density (Optional[float]): Water density at standard conditions
        compressibility (float): Water compressibility
        formation_volume_factor (float): Water formation volume factor at the given temperature and reference pressure
        viscosity (float): Water viscosity at the given temperature and reference pressure
        viscosity_compressibility (Optional[float]): Water viscosity compressibility.
    """

    # General parameters
    water_compressibility: Optional[float] = None
    water_formation_volume_factor: Optional[float] = None
    water_viscosity: Optional[float] = None
    water_viscosity_compressibility: Optional[float] = None
    temperature: Optional[float] = None
    salinity: Optional[float] = None
    water_density: Optional[float] = None


@dataclass(kw_only=True, repr=False)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusWaterMethod(DynamicProperty):
    """Class to hold Nexus Water properties.

    Attributes:
        file (NexusFile): Nexus water file object
        input_number (int): Water method number in Nexus fcs file
        reference_pressure (float): Reference pressure for BW and, if CVW is present, for VISW
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                    dict[str, Union[float, pd.DataFrame]]]]):
            Dictionary holding properties for generic dynamic method. Defaults to empty dictionary.
        parameters (list[NexusWaterParams]): list of water parameters, such as density, viscosity, etc.
    """

    file: NexusFile
    reference_pressure: Optional[float] = None
    properties: dict[str, Union[str, int, float, Enum, list[str], np.ndarray,
                     pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)
    parameters: list[NexusWaterParams] = field(default_factory=get_empty_list_nexus_water_params)
    unit_system: UnitSystem

    def __init__(self, file: NexusFile, input_number: int, model_unit_system: UnitSystem,
                 reference_pressure: Optional[float] = None,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                                      dict[str, Union[float, pd.DataFrame]]]]] = None,
                 parameters: Optional[list[NexusWaterParams]] = None) -> None:
        """Initialises the NexusWaterMethod class.

        Args:
            file (NexusFile): Nexus water file object
            input_number (int): Water method number in Nexus fcs file
            reference_pressure (float): Reference pressure for BW and, if CVW is present, for VISW
            properties: Dictionary holding properties for generic dynamic method. Defaults to empty dictionary.
            parameters (list[NexusWaterParams]): list of water parameters, such as density, viscosity, etc.
            model_unit_system (UnitSystem): unit system used in the model.
        """
        self.reference_pressure = reference_pressure
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        if parameters is not None:
            self.parameters = parameters
        else:
            self.parameters = []
        self.unit_system = model_unit_system
        super().__init__(input_number=input_number, file=file)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords: dict[str, tuple[str, type]] = {
            'TEMP': ('temperature', float),
            'PREF': ('reference_pressure', float),
            'DENW': ('water_density', float),
            'CW': ('water_compressibility', float),
            'BW': ('water_formation_volume_factor', float),
            'VISW': ('water_viscosity', float),
            'CVW': ('water_viscosity_compressibility', float)
            }
        return keywords

    @property
    def units(self) -> WaterUnits:
        """Returns the attribute to unit map for the Water method."""
        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']
        return WaterUnits(unit_system=self.unit_system)

    def to_string(self) -> str:
        """Create string with water data, in Nexus file format."""
        param_to_nexus_keyword_map = invert_nexus_map(NexusWaterMethod.get_keyword_mapping())

        printable_str = ''
        water_dict = self.properties
        # Print description if present
        if 'DESC' in water_dict.keys() and isinstance(water_dict['DESC'], list):
            for desc_line in water_dict['DESC']:
                printable_str += 'DESC ' + desc_line + '\n'
        if self.reference_pressure is not None:
            printable_str += f'PREF {self.reference_pressure}\n'
        for key, value in water_dict.items():
            if isinstance(value, Enum):
                if isinstance(value, UnitSystem) or isinstance(value, TemperatureUnits):
                    printable_str += f'{value.value}\n'
                elif isinstance(value, SUnits):
                    printable_str += f'SUNITS {value.value}\n'
            elif key not in ['DESC']:
                if value == '':
                    printable_str += f'{key}\n'
                else:
                    printable_str += f'{key} {value}\n'
        water_params = self.parameters
        temp_val = None
        sal_val = None
        for i in range(len(water_params)):
            water_param_dict = water_params[i].__dict__
            space_prefix = ''
            if water_param_dict['temperature']:
                if water_param_dict['temperature'] != temp_val:
                    printable_str += f"TEMP {water_param_dict['temperature']}\n"
                    temp_val = water_param_dict['temperature']
                space_prefix += '    '
            if water_param_dict['salinity']:
                if water_param_dict['salinity'] != sal_val:
                    printable_str += f"{space_prefix}SALINITY {water_param_dict['salinity']}\n"
                    sal_val = water_param_dict['salinity']
                space_prefix += '    '
            for key in param_to_nexus_keyword_map.keys():
                if key in water_param_dict and water_param_dict[key] is not None and key != 'temperature':
                    printable_str += f'{space_prefix}{param_to_nexus_keyword_map[key]} {water_param_dict[key]}\n'
        return printable_str

    def read_properties(self) -> None:
        """Read Nexus Water file contents and populate NexusWaterMethod object."""
        file_as_list = self.file.get_flat_list_str_file

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Specify unit system, if provided
        if 'UNIT_SYSTEM' in self.properties.keys() and isinstance(self.properties['UNIT_SYSTEM'], UnitSystem):
            self.unit_system = self.properties['UNIT_SYSTEM']

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
                                          water_density=water_props_dict['DENW'],
                                          water_compressibility=water_props_dict['CW'],
                                          water_formation_volume_factor=water_props_dict['BW'],
                                          water_viscosity=water_props_dict['VISW'],
                                          water_viscosity_compressibility=water_props_dict['CVW']
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
                                      water_density=water_props_dict['DENW'],
                                      water_compressibility=water_props_dict['CW'],
                                      water_formation_volume_factor=water_props_dict['BW'],
                                      water_viscosity=water_props_dict['VISW'],
                                      water_viscosity_compressibility=water_props_dict['CVW']
                                      )
            self.parameters.append(params)
