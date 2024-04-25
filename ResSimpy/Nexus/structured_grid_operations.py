from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import pandas as pd
from ResSimpy.Grid import GridArrayDefinition
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS, STRUCTURED_GRID_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_FORMAT_KEYWORDS
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Utils.general_utilities import check_if_string_is_float

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


class StructuredGridOperations:
    def __init__(self, model: NexusSimulator) -> None:
        """Initialises the StructuredGridOperations class.

        Args:
            model (NexusSimulator): Parent model object which the StructuredGridOperations class is associated with.
        """
        self.__model: NexusSimulator = model

    @staticmethod
    def load_token_value_if_present(token: str, modifier: str,
                                    token_property: GridArrayDefinition | dict[str, GridArrayDefinition],
                                    line: str, file_as_list: list[str], line_indx: int,
                                    ignore_values: Optional[list[str]] = None) -> None:
        """Gets a token's value if there is one and loads it into the token_property.

        Args:
        ----
            token (str): the token being searched for. e.g. 'PERMX'
            modifier (str): any modifiers applied to the token e.g. 'MULT'
            token_property (GridArrayDefinition | dict[str, GridArrayDefinition]):
                GridArrayDefinition or dict of GridArrayDefinition object to store the modifier and value pair into
            line (str): line to search for the token in
            line_indx (int): index of line in file_as_list
            file_as_list (list[str]): a list of strings containing each line of the file as a new entry
            ignore_values (Optional[list[str]]): values to be ignored. Defaults to None.

        Raises:
        ------
            ValueError: raises an error if no numerical value can be found after the supplied token modifier pair
        Returns:
            None: stores the value into token_property supplied instead
        """

        if ignore_values is None:
            ignore_values = []
        region_name: str = ''
        modifier_found = False
        token_found = nfo.check_token(token, line)
        found_modifier = line.strip().split()[-1]
        token_modifier: str = ''

        if token_found:
            token_next_value = fo.get_token_value(token, line, file_as_list, ignore_values=ignore_values)
        else:
            return
        if token_next_value == found_modifier:
            modifier_found = token_next_value == modifier
            token_modifier = f"{token} {modifier}"
        # If IREGION and the region_group is named
        elif token == 'IREGION' and found_modifier in GRID_ARRAY_FORMAT_KEYWORDS and len(line.strip().split()) == 3:
            region_name = line.strip().split()[1]
            modifier_found = found_modifier == modifier
            token_modifier = f"{token} {region_name} {modifier}"
        if token == 'IREGION' and isinstance(token_property, dict):
            if region_name == '':
                region_name = f"IREG{len(token_property.keys())+1}"

        if token_found and modifier_found:
            # If we are loading a multiple, load the two relevant values, otherwise just the next value
            # once we have the region_name, modifier_found, and token_modifier we can break it up in three pieces
            # piece one: make the grid definition array
            # piece two: find out if we have any MOD cards to deal with
            # piece three: make the mod table and add it to the grid array
            StructuredGridOperations.__make_grid_def(file_as_list, ignore_values, line, line_indx, modifier,
                                                     region_name, token_modifier, token_property)

            mod_start_end = StructuredGridOperations.__extract_mod_positions(line_indx, file_as_list)
            StructuredGridOperations.__make_mod_table(mod_start_end, file_as_list,
                                                      line, token_property, region_name, token_modifier)

    @staticmethod
    def __make_grid_def(file_as_list: list[str], ignore_values: list[str], line: str, line_indx: int, modifier: str,
                        region_name: str, token_modifier: str,
                        token_property: GridArrayDefinition | dict[str, GridArrayDefinition]) -> None:
        """A function that begins the process of populating the grid away."""

        if modifier == 'MULT':
            numerical_value = nfo.get_expected_token_value(modifier, line, file_as_list, ignore_values=ignore_values)
            if numerical_value is None:
                raise ValueError(
                    f'No numerical value found after {token_modifier} keyword in line: {line}')
            value_to_multiply = fo.get_token_value(modifier, line, file_as_list,
                                                   ignore_values=[numerical_value, *ignore_values])
            if numerical_value is not None and value_to_multiply is not None:
                if not isinstance(token_property, dict):
                    token_property.modifier = 'MULT'
                    token_property.value = f"{numerical_value} {value_to_multiply}"
                elif region_name != '':  # IREGION
                    token_property[region_name] = GridArrayDefinition()
                    token_property[region_name].modifier = 'MULT'
                    token_property[region_name].value = f"{numerical_value} {value_to_multiply}"
        else:
            value = fo.get_token_value(modifier, line, file_as_list, ignore_values=ignore_values)
            if value is None:
                # Could be 'cut short' by us excluding the rest of a file.
                if not isinstance(token_property, dict):
                    token_property.value = None
                    token_property.modifier = modifier
                elif region_name != '':  # IREGION
                    token_property[region_name] = GridArrayDefinition()
                    token_property[region_name].modifier = modifier
                    token_property[region_name].value = None
            else:
                # Check if VALUE modifier is followed by a numeric string or an INCLUDE file
                line_to_check = file_as_list[line_indx + 1]
                # Check next couple of lines in case next line contains one of ignore_values
                for i in range(line_indx+1, min(line_indx+3, len(file_as_list))):
                    if value in file_as_list[i]:
                        line_to_check = file_as_list[i]
                if 'INCLUDE' in line_to_check:
                    if not isinstance(token_property, dict):
                        token_property.value = value
                        token_property.modifier = modifier
                    elif region_name != '':  # IREGION
                        token_property[region_name] = GridArrayDefinition()
                        token_property[region_name].modifier = modifier
                        token_property[region_name].value = value
                elif check_if_string_is_float(value[0]) or value[0] == '.':
                    start_indx = line_indx + 1
                    end_indx = len(file_as_list)
                    found_end_value = False
                    for i in range(start_indx, len(file_as_list)):
                        for keyword in STRUCTURED_GRID_KEYWORDS + GRID_ARRAY_KEYWORDS:
                            if nfo.check_token(keyword, file_as_list[i]):
                                end_indx = i
                                found_end_value = True
                                break
                        if found_end_value:
                            break
                    if not isinstance(token_property, dict):
                        token_property.modifier = modifier
                        token_property.value = '\n'.join([line.strip()
                                                          for line in file_as_list[start_indx:end_indx]]).strip()
                    elif region_name != '':  # IREGION
                        token_property[region_name] = GridArrayDefinition()
                        token_property[region_name].modifier = modifier
                        token_property[region_name].value = '\n'.join([line.strip() for line in
                                                                       file_as_list[start_indx:end_indx]]).strip()
                else:  # The grid array keyword is likely inside an include file, presented on previous line
                    if 'INCLUDE' in file_as_list[line_indx - 1]:
                        if not isinstance(token_property, dict):
                            token_property.modifier = modifier
                            token_property.value = file_as_list[line_indx - 1].split('INCLUDE')[1].strip()
                            token_property.keyword_in_include_file = True
                        elif region_name != '':  # IREGION
                            token_property[region_name] = GridArrayDefinition()
                            token_property[region_name].modifier = modifier
                            token_property[region_name].value \
                                = file_as_list[line_indx - 1].split('INCLUDE')[1].strip()
                            token_property[region_name].keyword_in_include_file = True
                    else:
                        raise ValueError(
                            f'No suitable value found after {token_modifier} keyword in line: {line}')

    @staticmethod
    def replace_value(file_as_list: list[str], old_property: GridArrayDefinition, new_property: GridArrayDefinition,
                      token_name: str) -> None:
        """Replace the value and token + modifier with the new values.

        Args:
        ----
            file_as_list (list[str]): a list of strings containing each line of the file as a new entry
            old_property (VariableEntry): property found in the original file to be replaced
            new_property (VariableEntry): new property to replace the old property with
            token_name (str): name of the token being replaced
        Returns:
            None: modifies the file_as_list with the new property
        """

        for line in file_as_list:
            old_token_modifier = f"{token_name} {old_property.modifier}"
            new_token_modifier = f"{token_name} {new_property.modifier}"
            ignore_values = ['INCLUDE'] if old_property.modifier == 'VALUE' else []
            if nfo.check_token(old_token_modifier, line):
                # If we are replacing a mult, replace the first value with a blank
                if old_property.modifier == 'MULT':
                    dummy_value = GridArrayDefinition('MULT', '')
                    fo.get_token_value(old_token_modifier, line, file_as_list, ignore_values=ignore_values,
                                       replace_with=dummy_value)

                fo.get_token_value(old_token_modifier, line, file_as_list, ignore_values=ignore_values,
                                   replace_with=new_property)

                new_line = line.replace(old_token_modifier, new_token_modifier, 1)
                line_index = file_as_list.index(line)
                file_as_list[line_index] = new_line

    @staticmethod
    def append_include_to_grid_file(include_file_location: str, structured_grid_file_path: str) -> None:
        # TODO: change append to be an optional parameter
        """Appends an include file to the end of a grid for adding LGRs.

        Args:
        ----
            include_file_location (str): path to a file to include in the grid
            structured_grid_file_path (str): file path to the structured grid.

        Raises:
        ------
            ValueError: if no structured grid file path is specified in the class instance
        """
        # Get the existing file as a list
        if structured_grid_file_path is None:
            raise ValueError("No file path given or found for structured grid file path. \
                Please update structured grid file path")
        file = nfo.load_file_as_list(structured_grid_file_path)

        file.append(f"\nINCLUDE {include_file_location}\n")
        file.append("TOLPV LGR1 0\n")

        # Save the new file contents
        new_file_str = "".join(file)
        with open(structured_grid_file_path, "w") as text_file:
            text_file.write(new_file_str)

    @staticmethod
    def get_grid_file_as_3d_list(path: str) -> Optional[list]:
        """Converts a grid file to a 3D list.

        Args:
        ----
            path (str): path to a grid file

        Returns:
        -------
            Optional[list[str]]: Returns None if no file is found, returns the grid as a 3d array otherwise
        """
        try:
            with open(path) as f:
                grid_file_list = list(f)
        except FileNotFoundError:
            return None

        sub_lists = []

        new_list_str = ""
        for sub_list in grid_file_list[4:]:
            if sub_list == '\n':
                new_list_split = [x.split("\t") for x in new_list_str.split("\n")]
                new_list_split_cleaned = []
                for x_list in new_list_split:
                    float_list_split = [float(x) for x in x_list if x != ""]
                    new_list_split_cleaned.append(float_list_split)
                sub_lists.append(new_list_split_cleaned)
                new_list_str = ""
            else:
                new_list_str = new_list_str + sub_list
        return sub_lists

    def view_command(self, field: str, previous_lines: int = 3, following_lines: int = 3) -> Optional[str]:
        """Displays how the property is declared in the structured grid file.

        Args:
        ----
            field (str): property as written in the structured grid (e.g. KX)
            previous_lines (int, optional): how many lines to look back from the field searched for. Defaults to 3.
            following_lines (int, optional): how many lines to look forward from the field searched for. Defaults to 3.

        Raises:
        ------
            ValueError: if no structured grid file path is specified in the class instance

        Returns:
        -------
            Optional[str]: the string associated with the supplied property from within the structured grid. \
                If the field is not found in the structured grid returns None.
        """
        structured_grid_dict = self.__model.get_structured_grid_dict()
        structured_grid_path = self.__model.structured_grid_path
        command_token = f"{field.upper()} {structured_grid_dict[field.lower()].modifier}"
        if structured_grid_path is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        file_as_list = nfo.load_file_as_list(structured_grid_path)

        for line in file_as_list:
            if nfo.check_token(command_token, line):
                start_index = file_as_list.index(line) - previous_lines \
                    if file_as_list.index(line) - previous_lines > 0 else 0
                end_index = file_as_list.index(line) + following_lines \
                    if file_as_list.index(line) + following_lines < len(file_as_list) else len(file_as_list) - 1

                new_array = file_as_list[start_index: end_index]
                new_array = [x.strip("'") for x in new_array]
                value = "".join(new_array)
                return value
        return None

    @staticmethod
    def __extract_mod_positions(line_indx: int, file_as_list: list[str]) -> dict[str, list[list[int]]]:
        """Finds the positions where MOD exists."""

        mod_start_end: dict[str, list[list[int]]] = {}
        break_flag = False
        for i in range(line_indx + 1, len(file_as_list)):
            if nfo.check_token('MODX', file_as_list[i]):
                mod_start_end['MODX'] = [[i + 1, i + 2]]
            if nfo.check_token('MODY', file_as_list[i]):
                mod_start_end['MODY'] = [[i + 1, i + 2]]
            if nfo.check_token('MODZ', file_as_list[i]):
                mod_start_end['MODZ'] = [[i + 1, i + 2]]
            if nfo.check_token('MOD', file_as_list[i]):
                if 'MOD' in mod_start_end.keys():  # Already found a prior mod for this token, append
                    mod_start_end['MOD'].append([i + 1, len(file_as_list)])
                else:
                    mod_start_end['MOD'] = [[i + 1, len(file_as_list)]]
                found_end_of_mod_table = False
                for j in range(i + 1, len(file_as_list)):
                    for keyword in STRUCTURED_GRID_KEYWORDS + GRID_ARRAY_KEYWORDS:
                        if nfo.check_token(keyword, file_as_list[j]):
                            mod_start_end['MOD'][-1][1] = j
                            found_end_of_mod_table = True
                            break
                    if found_end_of_mod_table:
                        break
            for keyword in GRID_ARRAY_KEYWORDS:
                if nfo.check_token(keyword, file_as_list[i]):
                    break_flag = True
                    break
            if break_flag:
                break

        return mod_start_end

    @staticmethod
    def __make_mod_table(mod_start_end: dict[str, list[list[int]]], file_as_list: list[str], line: str,
                         token_property: GridArrayDefinition | dict[str, GridArrayDefinition], region_name: str,
                         token_modifier: str) -> None:
        """A function that creates the mod table."""

        for key in mod_start_end.keys():
            for i in range(len(mod_start_end[key])):
                if mod_start_end[key][i][1] > mod_start_end[key][i][0]:
                    mod_table = nfo.read_table_to_df(
                        file_as_list[mod_start_end[key][i][0]:mod_start_end[key][i][1]], noheader=True)
                    if len(mod_table.columns) == 7:
                        mod_table.columns = ['i1', 'i2', 'j1', 'j2', 'k1', 'k2', '#v']
                    elif len(mod_table.columns) == 8:
                        mod_table[8] = mod_table[6].astype(str) + mod_table[7].astype(str)
                        mod_table = mod_table.drop([6, 7], axis=1)
                        mod_table.columns = ['i1', 'i2', 'j1', 'j2', 'k1', 'k2', '#v']
                    else:
                        raise ValueError(
                            f'Unsuitable mod card for {token_modifier} keyword in line: {line}')
                    if not isinstance(token_property, dict):
                        if token_property.mods is not None:
                            if key in token_property.mods.keys():
                                orig_mod_tab = token_property.mods[key].copy()
                                token_property.mods[key] = \
                                    pd.concat([orig_mod_tab, mod_table]).reset_index(drop=True)
                            else:
                                token_property.mods[key] = mod_table
                        else:
                            token_property.mods = {key: mod_table}
                    else:  # IREGION
                        if token_property[region_name].mods is not None:
                            tmp_dict = token_property[region_name].mods
                            if isinstance(tmp_dict, dict):
                                if key in tmp_dict.keys():
                                    orig_mod_tab = tmp_dict[key].copy()
                                    tmp_dict[key] = \
                                        pd.concat([orig_mod_tab, mod_table]).reset_index(drop=True)
                        else:
                            token_property[region_name].mods = {key: mod_table}
