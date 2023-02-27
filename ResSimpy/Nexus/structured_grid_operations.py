
# TODO: Rename
from typing import Optional
from ResSimpy.Nexus.DataModels.StructuredGridFile import VariableEntry
import ResSimpy.Nexus.nexus_file_operations as nfo


def load_token_value_if_present(token: str, modifier: str, token_property: VariableEntry,
                                line: str, file_as_list: list[str],
                                ignore_values: Optional[list[str]] = None) -> None:
    """Gets a token's value if there is one and loads it into the token_property

    Args:
        token (str): the token being searched for. e.g. 'PERMX'
        modifier (str): any modifiers applied to the token e.g. 'MULT'
        token_property (VariableEntry): VariableEntry object to store the modifier and value pair into
        line (str): line to search for the token in
        file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as a new entry
        ignore_values (Optional[list[str]], optional): values to be ignored. Defaults to None.
    Raises:
        ValueError: raises an error if no numerical value can be found after the supplied token modifier pair
    Returns:
        None: stores the value into token_property supplied instead
    """

    if ignore_values is None:
        ignore_values = []
    token_modifier = f"{token} {modifier}"

    if token_modifier in line:
        # If we are loading a multiple, load the two relevant values, otherwise just the next value
        if modifier == 'MULT':
            numerical_value = nfo.get_expected_token_value(token_modifier, line, file_as_list, ignore_values=None)
            if numerical_value is None:
                raise ValueError(
                    f'No numerical value found after {token_modifier} keyword in line: {line}')
            value_to_multiply = nfo.get_token_value(token_modifier, line, file_as_list,
                                                    ignore_values=[numerical_value])
            if numerical_value is not None and value_to_multiply is not None:
                token_property.modifier = 'MULT'
                token_property.value = f"{numerical_value} {value_to_multiply}"
        else:
            value = nfo.get_token_value(token_modifier, line, file_as_list,
                                        ignore_values=ignore_values)
            if value is None:
                raise ValueError(
                    f'No value found after {token_modifier} in line: {line}')
            token_property.value = value
            token_property.modifier = modifier


def replace_value(file_as_list: list[str], old_property: VariableEntry, new_property: VariableEntry,
                  token_name: str) -> None:
    """Replace the value and token + modifier with the new values

    Args:
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
                nfo.get_token_value(old_token_modifier, line, file_as_list, ignore_values=ignore_values,
                                    replace_with=dummy_value)

            nfo.get_token_value(old_token_modifier, line, file_as_list, ignore_values=ignore_values,
                                replace_with=new_property)

            new_line = line.replace(old_token_modifier, new_token_modifier, 1)
            line_index = file_as_list.index(line)
            file_as_list[line_index] = new_line
