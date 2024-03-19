from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from ResSimpy.Grid import VariableEntry
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo

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
    def load_token_value_if_present(token: str, modifier: str, token_property: VariableEntry,
                                    line: str, file_as_list: list[str],
                                    ignore_values: Optional[list[str]] = None) -> None:
        """Gets a token's value if there is one and loads it into the token_property.

        Args:
        ----
            token (str): the token being searched for. e.g. 'PERMX'
            modifier (str): any modifiers applied to the token e.g. 'MULT'
            token_property (VariableEntry): VariableEntry object to store the modifier and value pair into
            line (str): line to search for the token in
            ignore_values (Optional[list[str]], optional): values to be ignored. Defaults to None.

        Raises:
        ------
            ValueError: raises an error if no numerical value can be found after the supplied token modifier pair
        Returns:
            None: stores the value into token_property supplied instead
        """

        if ignore_values is None:
            ignore_values = []
        token_modifier = f"{token} {modifier}"

        if nfo.check_token(token, line) and fo.get_token_value(token, line, file_as_list) == modifier:
            # If we are loading a multiple, load the two relevant values, otherwise just the next value
            if modifier == 'MULT':
                numerical_value = nfo.get_expected_token_value(token_modifier, line, file_as_list, ignore_values=None)
                if numerical_value is None:
                    raise ValueError(
                        f'No numerical value found after {token_modifier} keyword in line: {line}')
                value_to_multiply = fo.get_token_value(token_modifier, line, file_as_list,
                                                       ignore_values=[numerical_value])
                if numerical_value is not None and value_to_multiply is not None:
                    token_property.modifier = 'MULT'
                    token_property.value = f"{numerical_value} {value_to_multiply}"
            else:
                value = fo.get_token_value(token_modifier, line, file_as_list, ignore_values=ignore_values)
                if value is None:
                    # Could be 'cut short' by us excluding the rest of a file
                    token_property.value = None
                    token_property.modifier = modifier
                token_property.value = value
                token_property.modifier = modifier

    @staticmethod
    def replace_value(file_as_list: list[str], old_property: VariableEntry, new_property: VariableEntry,
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
                    dummy_value = VariableEntry('MULT', '')
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
