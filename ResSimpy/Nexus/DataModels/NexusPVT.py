from dataclasses import dataclass, field
from typing import Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Utils.factory_methods import get_empty_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.nexus_constants import VALID_NEXUS_KEYWORDS


@dataclass
class NexusPVT():
    """ Class to hold Nexus PVT properties
    Attributes:
        properties (dict[str, Union[str, dict, int, float, pd.DataFrame]]): Dictionary holding all properties for
        a specific PVT method. Defaults to empty dictionary.
    """
    properties: dict[str, Union[str, int, float, pd.DataFrame, dict[str, pd.DataFrame]]] \
        = field(default_factory=get_empty_dict_union)

    def read_properties_from_file(self, file_path: str):
        """Read Nexus pvt file contents and populate the NexusPVT properties object

        Args:
            file_path (str): path to PVT file
        """
        file_obj = NexusFile.generate_file_include_structure(file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        # Record PVT filepath
        self.properties['FILEPATH'] = file_path
        # Check for common input data
        self.properties = nfo.check_for_common_input_data(file_as_list, self.properties)

        # Initialize flags and containers used to record properties as we iterate through pvt file contents
        # Dictionary to record start and ending indices for tables
        pvt_table_indices: dict[str, list[int]] = {}
        pvt_table_indices_dict: dict[str, dict[str, list[int]]] = {}
        start_reading_table: bool = False  # Flag to tell when to start reading a table
        sat_table: bool = False  # Flag indicating SATURATED table is to be read
        oil_table: bool = False  # Flag indicating OIL table is to be read
        gas_table: bool = False  # Flag indicating GAS table is to be read
        unsatoil_table: bool = False  # Flag indicating UNSATOIL table is to be read
        unsatgas_table: bool = False  # Flag indicating UNSATGAS table is to be read
        # List to track saturation pressures from which undersaturated branches emanate
        psat_values: list[str] = []
        p_values: list[str] = []
        # List to track saturation Rs from which undersaturated branches emanate
        rs_values: list[str] = []

        # List of potential pvt types
        potential_pvt_types = ['BLACKOIL', 'WATEROIL', 'GASWATER', 'EOS']
        # List of potential fluid density parameters
        potential_fluid_density_params = ['DENOIL', 'API', 'GOR', 'OGR', 'DENGAS', 'SPECG', 'MWOR']

        line_indx = 0
        for line in file_as_list:

            # Determine PVT type, i.e., BLACKOIL, WATEROIL, EOS, etc.
            for pvt_type in potential_pvt_types:
                if nfo.check_token(pvt_type, line):
                    self.properties['PVT_TYPE'] = pvt_type

            # Extract fluid density parameters
            for fluid_param in potential_fluid_density_params:
                if nfo.check_token(fluid_param, line):
                    if nfo.get_token_value(fluid_param, line, file_as_list) is None:
                        raise ValueError(f"Property {fluid_param} does not have a numerical value.")
                    self.properties[fluid_param] = float(str(nfo.get_token_value(fluid_param, line, file_as_list)))
            if nfo.check_token('DRYGAS_MFP', line):
                self.properties['DRYGAS_MFP'] = True

            # Identify beginning and ending line indices for saturated, oil or gas tables, and unsaturated tables
            if start_reading_table:  # Figure out ending line indices
                if 'SATURATED' in pvt_table_indices.keys() and \
                        [i for i in line.split() if i in VALID_NEXUS_KEYWORDS] and sat_table:
                    pvt_table_indices['SATURATED'][1] = line_indx
                    start_reading_table = False
                    sat_table = False
                if 'OIL' in pvt_table_indices.keys() and \
                        [i for i in line.split() if i in VALID_NEXUS_KEYWORDS] and oil_table:
                    pvt_table_indices['OIL'][1] = line_indx
                    start_reading_table = False
                    oil_table = False
                if 'GAS' in pvt_table_indices.keys() and \
                        [i for i in line.split() if i in VALID_NEXUS_KEYWORDS] and gas_table:
                    pvt_table_indices['GAS'][1] = line_indx
                    start_reading_table = False
                    gas_table = False
                if 'UNSATOIL_PSAT' in pvt_table_indices_dict.keys() and \
                        [i for i in line.split() if i in VALID_NEXUS_KEYWORDS] and unsatoil_table:
                    pvt_table_indices_dict['UNSATOIL_PSAT'][psat_values[-1]][1] = line_indx
                    start_reading_table = False
                    unsatoil_table = False
                if 'UNSATOIL_RSSAT' in pvt_table_indices_dict.keys() and \
                        [i for i in line.split() if i in VALID_NEXUS_KEYWORDS] and unsatoil_table:
                    pvt_table_indices_dict['UNSATOIL_RSSAT'][rs_values[-1]][1] = line_indx
                    start_reading_table = False
                    unsatoil_table = False
                if 'UNSATGAS' in pvt_table_indices_dict.keys() and \
                        [i for i in line.split() if i in VALID_NEXUS_KEYWORDS] and unsatgas_table:
                    pvt_table_indices_dict['UNSATGAS'][p_values[-1]][1] = line_indx
                    start_reading_table = False
                    unsatgas_table = False
            # Figure out beginning line indices
            if nfo.check_token('SATURATED', line):
                pvt_table_indices['SATURATED'] = [line_indx + 1, len(file_as_list)]
                sat_table = True
                line_indx += 1
                continue
            if nfo.check_token('OIL', line):
                pvt_table_indices['OIL'] = [line_indx + 1, len(file_as_list)]
                oil_table = True
                line_indx += 1
                continue
            if nfo.check_token('GAS', line):
                pvt_table_indices['GAS'] = [line_indx + 1, len(file_as_list)]
                gas_table = True
                line_indx += 1
                continue
            if nfo.check_token('UNSATOIL', line):
                if nfo.check_token('PSAT', line):
                    if nfo.get_token_value('PSAT', line, file_as_list) is None:
                        raise ValueError("Property PSAT does not have a numerical value.")
                    psat_values.append(str(nfo.get_token_value('PSAT', line, file_as_list)))
                    if 'UNSATOIL_PSAT' in pvt_table_indices_dict.keys():
                        pvt_table_indices_dict['UNSATOIL_PSAT'][psat_values[-1]] = [line_indx + 1, len(file_as_list)]
                    else:
                        pvt_table_indices_dict['UNSATOIL_PSAT'] = {psat_values[-1]: [line_indx + 1, len(file_as_list)]}
                if nfo.check_token('RSSAT', line):
                    if nfo.get_token_value('RSSAT', line, file_as_list) is None:
                        raise ValueError("Property RSSAT does not have a numerical value.")
                    rs_values.append(str(nfo.get_token_value('RSSAT', line, file_as_list)))
                    if 'UNSATOIL_RSSAT' in pvt_table_indices_dict.keys():
                        pvt_table_indices_dict['UNSATOIL_RSSAT'][rs_values[-1]] = [line_indx + 1, len(file_as_list)]
                    else:
                        pvt_table_indices_dict['UNSATOIL_RSSAT'] = {rs_values[-1]: [line_indx + 1, len(file_as_list)]}
                unsatoil_table = True
                line_indx += 1
                continue
            if nfo.check_token('UNSATGAS', line):
                if nfo.check_token('PRES', line):
                    if nfo.get_token_value('PRES', line, file_as_list) is None:
                        raise ValueError("Property PRES does not have a numerical value.")
                    p_values.append(str(nfo.get_token_value('PRES', line, file_as_list)))
                    if 'UNSATGAS' in pvt_table_indices_dict.keys():
                        pvt_table_indices_dict['UNSATGAS'][p_values[-1]] = [line_indx + 1, len(file_as_list)]
                    else:
                        pvt_table_indices_dict['UNSATGAS'] = {p_values[-1]: [line_indx + 1, len(file_as_list)]}
                unsatgas_table = True
                line_indx += 1
                continue
            # Check if this line represents the header of a PVT table
            if (sat_table or oil_table or gas_table or unsatoil_table or unsatgas_table) and \
                not start_reading_table and \
                    (nfo.check_token('PRES', line) or nfo.check_token('DP', line) or nfo.check_token('RV', line)):
                start_reading_table = True  # If header row, start reading

            line_indx += 1

        # Read in tables
        for key in pvt_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                pvt_table_indices[key][0]:pvt_table_indices[key][1]])
        for key in pvt_table_indices_dict.keys():
            self.properties[key] = {}
            for subkey in pvt_table_indices_dict[key].keys():
                if not isinstance(self.properties[key], dict):
                    raise ValueError(f"Property is not a dictionary: {str(self.properties[key])}")
                self.properties[key][subkey] = nfo.read_table_to_df(file_as_list[
                    pvt_table_indices_dict[key][subkey][0]:pvt_table_indices_dict[key][subkey][1]])
