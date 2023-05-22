from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_TABLE_KEYWORDS, RELPM_KEYWORDS_VALUE_FLOAT
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_SINGLE_KEYWORDS, RELPM_HYSTERESIS_PRIMARY_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_KEYWORDS, RELPM_NONDARCY_KEYWORDS, RELPM_NONDARCY_PARAMS

from ResSimpy.RelPermMethod import RelPermMethod

from ResSimpy.Utils.factory_methods import get_empty_dict_union, get_empty_hysteresis_dict
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass(kw_only=True)  # Doesn't need to write an _init_, _eq_ methods, etc.
class NexusRelPermMethod(RelPermMethod):
    """ Class to hold Nexus relative permeability and capillary pressure properties
    Attributes:
        file_path (str): Path to the Nexus relperm file
        method_number (int): RELPM method number in Nexus fcs file
        properties (dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame, dict[str, pd.DataFrame]]] ):
            Dictionary holding all properties for a specific PVT method. Defaults to empty dictionary.
    """
    # General parameters
    file_path: str
    properties: dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                dict[str, Union[float, pd.DataFrame]]]] \
        = field(default_factory=get_empty_dict_union)
    hysteresis_params: dict[str, Union[str, float, dict[str, Union[str, float, dict[str, Union[str, float]]]]]] \
        = field(default_factory=get_empty_hysteresis_dict)

    def __init__(self, file_path: str, method_number: int,
                 properties: Optional[dict[str, Union[str, int, float, Enum, list[str], pd.DataFrame,
                                                      dict[str, Union[float, pd.DataFrame]]]]] = None,
                 hysteresis_params: Optional[dict[str, Union[str, float,
                                                             dict[str, Union[str, float,
                                                                             dict[str, Union[str, float]]]]]]] = None):
        self.file_path = file_path
        if properties:
            self.properties = properties
        else:
            self.properties = {}
        if hysteresis_params:
            self.hysteresis_params = hysteresis_params
        else:
            self.hysteresis_params = {}
        super().__init__(method_number=method_number)

    def __populate_optional_str_keywords(self, keyword: str, keyword_value_options: list[str], single_line: str,
                                         line_list: list[str]):
        """Utility function to populate rel perm keywords that have optional string values, e.g., IFT, JFUNC, etc.

        Args:
            keyword (str): primary keyword, e.g., IFT or JFUNC
            keyword_value_options (list[str]): primary keyword optional values, e.g., [METHOD1, METHOD2] for IFT
            single_line (str): single line as read from input RELPM file
            line_list (list[str]): list of strings that comprise input RELPM file
        """
        if nfo.check_token(keyword, single_line):
            key_val = nfo.get_token_value(keyword, single_line, line_list)
            if key_val in keyword_value_options:
                self.properties[keyword] = key_val
            else:
                self.properties[keyword] = ''

    def read_properties(self) -> None:
        """Read Nexus rel perm file contents and populate the NexusRelPermMethod object
        """
        file_obj = NexusFile.generate_file_include_structure(self.file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        # Check for common input data
        nfo.check_for_and_populate_common_input_data(file_as_list, self.properties)

        # Initialize flags and containers to use to record properties as we iterate through relperm file contents
        # Dictionary to record start and ending indices for tables
        relpm_table_indices: dict[str, list[int]] = {}
        # Dictionary of flags indicating which tables are being read
        table_being_read: dict[str, bool] = {}
        for table_name in RELPM_TABLE_KEYWORDS:
            table_being_read[table_name] = False
        # Flag to track hysteresis parameters section
        hysteresis_being_read: bool = False
        hysteresis_section_indices: list[int] = []
        # Dictionary to record start and ending indices of nondarcy section
        nondarcy_indices: dict[str, list[int]] = {}
        nondarcy_being_read: bool = False
        # Dictionary and flags for handle tabular reconstruction
        recon_dict: dict[str, Union[float, pd.DataFrame]] = {}
        found_reconstruct = False

        line_indx = 0
        for line in file_as_list:

            # Find standalone relperm keywords
            if [i for i in line.split() if i in RELPM_SINGLE_KEYWORDS]:
                for word in RELPM_SINGLE_KEYWORDS:
                    if nfo.check_token(word, line):
                        self.properties[word] = ''
            # Find relperm key-value pairs, such as SOMOPT2 0.05
            if [i for i in line.split() if i in RELPM_KEYWORDS_VALUE_FLOAT]:
                for key in RELPM_KEYWORDS_VALUE_FLOAT:
                    if nfo.check_token(key, line):
                        self.properties[key] = float(str(nfo.get_token_value(key, line, file_as_list)))
            # Handle JFUNC
            self.__populate_optional_str_keywords('JFUNC', ['KX', 'KY', 'KXKY'], line, file_as_list)
            # Handle endpt scaling
            for key in ['SCALING', 'SCALING_PC']:
                self.__populate_optional_str_keywords(key, ['NONE', 'TWOPOINT', 'THREEPOINT'], line, file_as_list)
            # Handle interfacial tension
            self.__populate_optional_str_keywords('IFT', ['METHOD1', 'METHOD2'], line, file_as_list)
            # Handle near critical adjustment of rel perm
            self.__populate_optional_str_keywords('NEARCRIT', ['HCSCALE'], line, file_as_list)
            # Handle derivatives option
            self.__populate_optional_str_keywords('DERIVATIVES', ['ANALYTICAL', 'NUMERICAL'], line, file_as_list)
            # Handle tabular reconstruction
            if nfo.check_token('RECONSTRUCT', line):
                found_reconstruct = True
            for recon_key in ['NSGDIM', 'NSWDIM']:
                if nfo.check_token(recon_key, line) and found_reconstruct:
                    recon_dict[recon_key] = float(str(nfo.get_token_value(recon_key, line, file_as_list)))
            if found_reconstruct:
                self.properties['RECONSTRUCT'] = recon_dict

            # Find beginning and ending indices of hysteresis section
            if nfo.check_token('HYSTERESIS', line):
                hysteresis_being_read = True
                hysteresis_section_indices = [line_indx, len(file_as_list)]
            if len(line.split()) > 0 and hysteresis_being_read:
                possible_token = line.split()[0]
                if nfo.check_token(possible_token, line) and possible_token not in \
                        ['HYSTERESIS']+RELPM_HYSTERESIS_PRIMARY_KEYWORDS:
                    hysteresis_being_read = False
                    hysteresis_section_indices[1] = line_indx

            # Find beginning and ending indices of nondarcy section
            for nondarcy_key in RELPM_NONDARCY_KEYWORDS:
                if nfo.check_token(nondarcy_key, line):
                    nondarcy_being_read = True
                    nondarcy_indices[nondarcy_key] = [line_indx+1, len(file_as_list)]
                if nondarcy_being_read and nfo.check_token('END'+nondarcy_key, line):
                    nondarcy_being_read = False
                    nondarcy_indices[nondarcy_key][1] = line_indx

            # Find ending index of relperm tables
            # if start_reading_table:
            for table_keyword in RELPM_TABLE_KEYWORDS:
                if table_being_read[table_keyword]:
                    for potential_endkeyword in RELPM_KEYWORDS:
                        if nfo.check_token(potential_endkeyword, line):
                            relpm_table_indices[table_keyword][1] = line_indx
                            # start_reading_table = False
                            table_being_read[table_keyword] = False
                            break
            # Find the starting index of relperm tables
            if [i for i in line.split() if i in RELPM_TABLE_KEYWORDS]:
                for table_keyword in RELPM_TABLE_KEYWORDS:
                    if nfo.check_token(table_keyword, line):
                        relpm_table_indices[table_keyword] = [line_indx+1, len(file_as_list)]
                        table_being_read[table_keyword] = True
                        # start_reading_table = True
                # line_indx += 1
                # continue

            line_indx += 1

        # Read in tables
        for key in relpm_table_indices.keys():
            self.properties[key] = nfo.read_table_to_df(file_as_list[
                                                        relpm_table_indices[key][0]:relpm_table_indices[key][1]])

        # Read nondarcy parameters from nondarcy section, if present:
        for key in nondarcy_indices.keys():
            nondarcy_dict: dict[str, Union[float, pd.DataFrame]] = {}
            for line in file_as_list[nondarcy_indices[key][0]:nondarcy_indices[key][1]]:
                for param in RELPM_NONDARCY_PARAMS:
                    if nfo.check_token(param, line):
                        nondarcy_dict[param] = float(str(nfo.get_token_value(param, line, file_as_list)))
            self.properties[key] = nondarcy_dict

        # Read hysteresis section, if present
        if len(hysteresis_section_indices) > 0:
            for line in file_as_list[hysteresis_section_indices[0]:hysteresis_section_indices[1]]:
                if nfo.check_token('NOCHK_HYS', line):
                    self.hysteresis_params['NOCHK_HYS'] = ''
                if nfo.check_token('KRW', line) and nfo.get_token_value('KRW', line, file_as_list) == 'USER':
                    self.hysteresis_params['KRW'] = 'USER'
                if [i for i in line.split() if i in ['KRG', 'KROW']]:
                    for hyst_keyword in ['KRG', 'KROW']:
                        if nfo.check_token(hyst_keyword, line):
                            hyst_keyword_primary_key = nfo.get_token_value(hyst_keyword, line, file_as_list)
                            if hyst_keyword_primary_key == 'USER':
                                self.hysteresis_params[hyst_keyword] = 'USER'
                            elif hyst_keyword_primary_key in ['LINEAR', 'SCALED', 'CARLSON', 'KILLOUGH']:
                                hyst_dict: dict[str, Union[str, float, dict[str, Union[str, float]]]] = {}
                                hyst_subdict: dict[str, Union[str, float]] = {}
                                if nfo.check_token('MAXTRAP', line):
                                    hyst_subdict['MAXTRAP'] = float(str(nfo.get_token_value('MAXTRAP',
                                                                                            line, file_as_list)))
                                    hyst_dict[hyst_keyword_primary_key] = hyst_subdict
                                if nfo.check_token('EXP', line):
                                    hyst_subdict['EXP'] = float(str(nfo.get_token_value('EXP', line, file_as_list)))
                                    hyst_dict[hyst_keyword_primary_key] = hyst_subdict
                                if nfo.check_token('NOMOD', line):
                                    hyst_subdict['NOMOD'] = ''
                                    hyst_dict[hyst_keyword_primary_key] = hyst_subdict
                                self.hysteresis_params[hyst_keyword] = hyst_dict
                if [i for i in line.split() if i in ['PCWO', 'PCGO', 'WAG']]:
                    for hyst_keyword in ['PCWO', 'PCGO', 'WAG']:
                        if nfo.check_token(hyst_keyword, line):
                            hyst_pc_dict: dict[str, Union[str, float, dict[str, Union[str, float]]]] = {}
                            # Search for options with key-value pairs
                            for hyst_keyword_primary_key in ['MAXSW', 'MINSG', 'ETA', 'LAND', 'ALPHA', 'AFAC']:
                                if nfo.check_token(hyst_keyword_primary_key, line):
                                    hyst_pc_dict[hyst_keyword_primary_key] = \
                                        float(str(nfo.get_token_value(hyst_keyword_primary_key, line, file_as_list)))
                            # Search for single keyword options
                            for hyst_keyword_primary_key in ['TRAPSCALE', 'NOWATHYS', 'NOGASHYS', 'NOOILHYS']:
                                if nfo.check_token(hyst_keyword_primary_key, line):
                                    hyst_pc_dict[hyst_keyword_primary_key] = ''
                            self.hysteresis_params[hyst_keyword] = hyst_pc_dict
                if [i for i in line.split() if i in ['TOLREV', 'TOLHYS']]:
                    for hyst_keyword in ['TOLREV', 'TOLHYS']:
                        if nfo.check_token(hyst_keyword, line):
                            self.hysteresis_params[hyst_keyword] = float(str(nfo.get_token_value(hyst_keyword,
                                                                                                 line, file_as_list)))
