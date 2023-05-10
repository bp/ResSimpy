from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_list_nexus_water_params
import ResSimpy.Nexus.nexus_file_operations as nfo


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


@dataclass  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusWater():
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
    method_number: int
    reference_pressure: Optional[float] = None
    properties: dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame, dict[str, pd.DataFrame]]] \
        = field(default_factory=get_empty_dict_union)
    parameters: list[NexusWaterParams] = field(default_factory=get_empty_list_nexus_water_params)

    def read_properties(self) -> None:
        """Read Nexus Water file contents and populate NexusWater object
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
                self.reference_pressure = float(str(nfo.get_token_value('PREF', line, file_as_list)))

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
                temp = float(str(nfo.get_token_value('TEMP', line, file_as_list)))
            if nfo.check_token('SALINITY', line):
                sal = float(str(nfo.get_token_value('SALINITY', line, file_as_list)))
            for key in water_props_dict.keys():
                if nfo.check_token(key, line):
                    found_params = True
                    water_props_dict[key] = float(str(nfo.get_token_value(key, line, file_as_list)))

            line_indx += 1

        # if not found_temp_or_sal:  # If no temperature or salinity repeats
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
