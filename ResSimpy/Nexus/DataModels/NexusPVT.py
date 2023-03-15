from dataclasses import dataclass, field
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_BLACKOIL_PRIMARY_KEYWORDS, PVT_TYPE_KEYWORDS, PVT_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOS_METHODS, PVT_EOSOPTIONS_PRIMARY_WORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_PRIMARY_KEYS_INT
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT, PVT_EOSOPTIONS_TRANS_KEYS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_TRANS_TEST_KEYS, PVT_EOSOPTIONS_PHASEID_KEYS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_EOSOPTIONS_TERTIARY_KEYS
from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_list_str, get_empty_eosopt_dict_union
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusPVT():
    """ Class to hold Nexus PVT properties
    Attributes:
        properties (dict[str, Union[str, dict, int, float, pd.DataFrame]]): Dictionary holding all properties for
        a specific PVT method. Defaults to empty dictionary.
    """
    # General parameters
    file_path: str
    pvt_type: Optional[str] = None
    eos_nhc: int = 0  # Number of hydrocarbon components
    eos_temp: float = 60.0  # Default temperature for EOS method
    eos_components: Optional[list[str]] = field(default_factory=get_empty_list_str)
    eos_options: dict[str, Union[str, int, float, pd.DataFrame, list[str], dict[str, float],
                                 tuple[str, dict[str, float]], dict[str, pd.DataFrame]]] \
        = field(default_factory=get_empty_eosopt_dict_union)
    properties: dict[str, Union[str, int, float, pd.DataFrame, dict[str, pd.DataFrame]]] \
        = field(default_factory=get_empty_dict_union)

    def read_properties(self):
        """Read Nexus pvt file contents and populate the NexusPVT properties object

        Args:
            file_path (str): path to PVT file
        """
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

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
        props_table: bool = False  # Flag indicating EOS component property table is to be read
        bina_table: bool = False  # Flag indicating EOS binary interaction table is to be read
        pedtune_table: bool = False  # Flag indicating Pedersen viscosity tuning parameters table to be read
        viskj_table: bool = False  # Flag indicating j coefficients of Pedersen viscosity table to be read
        viskk_table: bool = False  # Flag indicating k coefficients of Pedersen viscosity table to be read
        viskkij_table: bool = False  # Flag indicating interaction coefficients of Pedersen viscosity table to be read
        # List to track saturation pressures from which undersaturated branches emanate
        psat_values: list[str] = []
        p_values: list[str] = []
        # List to track saturation Rs from which undersaturated branches emanate
        rs_values: list[str] = []

        line_indx = 0
        for line in file_as_list:

            # Determine PVT type, i.e., BLACKOIL, WATEROIL, EOS, etc.
            for pvt_type in PVT_TYPE_KEYWORDS:
                if nfo.check_token(pvt_type, line):
                    self.pvt_type = pvt_type

            # Extract blackoil fluid density parameters
            for fluid_param in PVT_BLACKOIL_PRIMARY_KEYWORDS:
                if nfo.check_token(fluid_param, line):
                    if nfo.get_token_value(fluid_param, line, file_as_list) is None:
                        raise ValueError(f"Property {fluid_param} does not have a numerical value.")
                    self.properties[fluid_param] = float(str(nfo.get_token_value(fluid_param, line, file_as_list)))
            if nfo.check_token('DRYGAS_MFP', line):
                self.properties['DRYGAS_MFP'] = True

            # For EOS or compositional models, get required parameters
            if nfo.check_token('NHC', line):  # Get number of components
                if nfo.get_token_value('NHC', line, file_as_list) is None:
                    raise ValueError("Property NHC does not have a numerical value.")
                self.eos_nhc = int(str(nfo.get_token_value('NHC', line, file_as_list)))
            if nfo.check_token('COMPONENTS', line):  # Get NHC components
                elems = line.split()
                components_index = elems.index('COMPONENTS')
                self.eos_components = elems[components_index+1:components_index+1+int(self.eos_nhc)]
            if nfo.check_token('TEMP', line):  # Get default EOS temperature
                if nfo.get_token_value('TEMP', line, file_as_list) is None:
                    raise ValueError("Property TEMP does not have a numerical value.")
                self.eos_temp = float(str(nfo.get_token_value('TEMP', line, file_as_list)))

            # Check for EOS options
            if nfo.check_token('EOSOPTIONS', line):
                if str(nfo.get_token_value('EOSOPTIONS', line, file_as_list)) in PVT_EOS_METHODS:
                    self.eos_options['EOS_METHOD'] = str(nfo.get_token_value('EOSOPTIONS', line, file_as_list))
                else:
                    self.eos_options['EOS_METHOD'] = 'PR'
            # Find EOS single-word options, like CAPILLARYFLASH and add to list
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PRIMARY_WORDS]:
                if 'EOS_OPT_PRIMARY_LIST' not in self.eos_options.keys():
                    self.eos_options['EOS_OPT_PRIMARY_LIST'] = []
                self.eos_options['EOS_OPT_PRIMARY_LIST'].extend([i for i in line.split() if i  # type: ignore
                                                                 in PVT_EOSOPTIONS_PRIMARY_WORDS])
            # Find EOS key-value pairs, like LI_FACT 0.9 or FUGERR 5
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT]:
                for key in PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT:
                    if nfo.check_token(key, line):
                        self.eos_options[key] = float(str(nfo.get_token_value(key, line, file_as_list)))
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PRIMARY_KEYS_INT]:
                for key in PVT_EOSOPTIONS_PRIMARY_KEYS_INT:
                    if nfo.check_token(key, line):
                        self.eos_options[key] = int(str(nfo.get_token_value(key, line, file_as_list)))
            # Read TRANSITION eos options, if present
            if nfo.check_token('TRANSITION', line):
                self.eos_options['TRANSITION'] = 'TEST'
                if str(nfo.get_token_value('TRANSITION', line, file_as_list)) in PVT_EOSOPTIONS_TRANS_KEYS:
                    self.eos_options['TRANSITION'] = str(nfo.get_token_value('TRANSITION', line, file_as_list))
            if [i for i in line.split() if i in PVT_EOSOPTIONS_TRANS_KEYS]:
                for trans_key in PVT_EOSOPTIONS_TRANS_KEYS:
                    if nfo.check_token(trans_key, line):
                        self.eos_options['TRANSITION'] = trans_key
                        for tert_key in PVT_EOSOPTIONS_TERTIARY_KEYS:
                            if nfo.check_token(tert_key, line):
                                if type(self.eos_options['TRANSITION']) == str:
                                    self.eos_options['TRANSITION'] = (trans_key, {})
                                self.eos_options['TRANSITION'][1][tert_key] = float(  # type: ignore
                                    str(nfo.get_token_value(tert_key, line, file_as_list)))
            # Read TRANS_OPTIMIZATION eos options, if present
            if nfo.check_token('TRANS_OPTIMIZATION', line):
                self.eos_options['TRANS_OPTIMIZATION'] = {}
                for tert_key in PVT_EOSOPTIONS_TERTIARY_KEYS:
                    if nfo.check_token(tert_key, line):
                        self.eos_options['TRANS_OPTIMIZATION'][tert_key] = float(
                            str(nfo.get_token_value(tert_key, line, file_as_list)))
            # Read TRANS_TEST eos options, if present
            if nfo.check_token('TRANS_TEST', line):
                self.eos_options['TRANS_TEST'] = 'INCRP'
                if str(nfo.get_token_value('TRANS_TEST', line, file_as_list)) in PVT_EOSOPTIONS_TRANS_TEST_KEYS:
                    self.eos_options['TRANS_TEST'] = str(nfo.get_token_value('TRANS_TEST', line, file_as_list))
            if [i for i in line.split() if i in PVT_EOSOPTIONS_TRANS_TEST_KEYS]:
                for trans_key in PVT_EOSOPTIONS_TRANS_TEST_KEYS:
                    if nfo.check_token(trans_key, line):
                        self.eos_options['TRANS_TEST'] = trans_key
                        for tert_key in PVT_EOSOPTIONS_TERTIARY_KEYS:
                            if nfo.check_token(tert_key, line):
                                if type(self.eos_options['TRANS_TEST']) == str:
                                    self.eos_options['TRANS_TEST'] = (trans_key, {})
                                self.eos_options['TRANS_TEST'][1][tert_key] = float(  # type: ignore
                                    str(nfo.get_token_value(tert_key, line, file_as_list)))
            # Read PHASEID eos options, if present
            if nfo.check_token('PHASEID', line):
                self.eos_options['PHASEID'] = ''
                if str(nfo.get_token_value('PHASEID', line, file_as_list)) in PVT_EOSOPTIONS_PHASEID_KEYS:
                    self.eos_options['PHASEID'] = str(nfo.get_token_value('PHASEID', line, file_as_list))
            if [i for i in line.split() if i in PVT_EOSOPTIONS_PHASEID_KEYS]:
                for trans_key in PVT_EOSOPTIONS_PHASEID_KEYS:
                    if nfo.check_token(trans_key, line):
                        self.eos_options['PHASEID'] = trans_key
                        for tert_key in PVT_EOSOPTIONS_TERTIARY_KEYS:
                            if nfo.check_token(tert_key, line):
                                if type(self.eos_options['PHASEID']) == str:
                                    self.eos_options['PHASEID'] = (trans_key, {})
                                self.eos_options['PHASEID'][1][tert_key] = float(  # type: ignore
                                    str(nfo.get_token_value(tert_key, line, file_as_list)))

            # Identify beginning and ending line indices for saturated, oil or gas tables, and unsaturated tables
            if start_reading_table:  # Figure out ending line indices
                if 'SATURATED' in pvt_table_indices.keys() and \
                        [i for i in line.split() if i in PVT_KEYWORDS] and sat_table:
                    pvt_table_indices['SATURATED'][1] = line_indx
                    start_reading_table = False
                    sat_table = False
                if 'OIL' in pvt_table_indices.keys() and \
                        [i for i in line.split() if i in PVT_KEYWORDS] and oil_table:
                    pvt_table_indices['OIL'][1] = line_indx
                    start_reading_table = False
                    oil_table = False
                if 'GAS' in pvt_table_indices.keys() and \
                        [i for i in line.split() if i in PVT_KEYWORDS] and gas_table:
                    pvt_table_indices['GAS'][1] = line_indx
                    start_reading_table = False
                    gas_table = False
                if 'PROPS' in pvt_table_indices.keys() and nfo.check_token('ENDPROPS', line) and props_table:
                    pvt_table_indices['PROPS'][1] = line_indx
                    start_reading_table = False
                    props_table = False
                if 'BINA' in pvt_table_indices.keys() and nfo.check_token('ENDBINA', line) and bina_table:
                    pvt_table_indices['BINA'][1] = line_indx
                    start_reading_table = False
                    bina_table = False
                if 'PEDTUNE' in pvt_table_indices.keys() and nfo.check_token('ENDPEDTUNE', line) and pedtune_table:
                    pvt_table_indices['PEDTUNE'][1] = line_indx
                    start_reading_table = False
                    pedtune_table = False
                if 'VISKJ' in pvt_table_indices.keys() and nfo.check_token('ENDVISKJ', line) and viskj_table:
                    pvt_table_indices['VISKJ'][1] = line_indx
                    start_reading_table = False
                    viskj_table = False
                if 'VISKK' in pvt_table_indices.keys() and nfo.check_token('ENDVISKK', line) and viskk_table:
                    pvt_table_indices['VISKK'][1] = line_indx
                    start_reading_table = False
                    viskk_table = False
                if 'VISKKIJ' in pvt_table_indices.keys() and nfo.check_token('ENDVISKKIJ', line) and viskkij_table:
                    pvt_table_indices['VISKKIJ'][1] = line_indx
                    start_reading_table = False
                    viskkij_table = False
                if 'UNSATOIL_PSAT' in pvt_table_indices_dict.keys() and \
                        [i for i in line.split() if i in PVT_KEYWORDS] and unsatoil_table:
                    pvt_table_indices_dict['UNSATOIL_PSAT'][psat_values[-1]][1] = line_indx
                    start_reading_table = False
                    unsatoil_table = False
                if 'UNSATOIL_RSSAT' in pvt_table_indices_dict.keys() and \
                        [i for i in line.split() if i in PVT_KEYWORDS] and unsatoil_table:
                    pvt_table_indices_dict['UNSATOIL_RSSAT'][rs_values[-1]][1] = line_indx
                    start_reading_table = False
                    unsatoil_table = False
                if 'UNSATGAS' in pvt_table_indices_dict.keys() and \
                        [i for i in line.split() if i in PVT_KEYWORDS] and unsatgas_table:
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
            if nfo.check_token('PROPS', line):
                pvt_table_indices['PROPS'] = [line_indx + 1, len(file_as_list)]
                props_table = True
                line_indx += 1
                continue
            if nfo.check_token('BINA', line):
                pvt_table_indices['BINA'] = [line_indx + 1, len(file_as_list)]
                bina_table = True
                line_indx += 1
                continue
            if nfo.check_token('PEDTUNE', line):
                pvt_table_indices['PEDTUNE'] = [line_indx + 1, len(file_as_list)]
                pedtune_table = True
                line_indx += 1
                continue
            if nfo.check_token('VISKJ', line):
                pvt_table_indices['VISKJ'] = [line_indx + 1, len(file_as_list)]
                viskj_table = True
                line_indx += 1
                continue
            if nfo.check_token('VISKK', line):
                pvt_table_indices['VISKK'] = [line_indx + 1, len(file_as_list)]
                viskk_table = True
                line_indx += 1
                continue
            if nfo.check_token('VISKKIJ', line):
                pvt_table_indices['VISKKIJ'] = [line_indx + 1, len(file_as_list)]
                viskkij_table = True
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
            if (sat_table or oil_table or gas_table or props_table or bina_table or pedtune_table
                or viskj_table or viskk_table or viskkij_table or unsatoil_table or unsatgas_table) \
                and not start_reading_table and \
                    (nfo.check_token('PRES', line) or
                     nfo.check_token('DP', line) or
                     nfo.check_token('RV', line) or
                     nfo.check_token('INDEX', line) or
                     nfo.check_token('COMPONENT', line)):
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
                self.properties[key][subkey] = nfo.read_table_to_df(file_as_list[  # type: ignore
                    pvt_table_indices_dict[key][subkey][0]:pvt_table_indices_dict[key][subkey][1]])
