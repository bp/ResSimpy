from functools import partial
from typing import Optional, Union

from ResSimpy.Grid import VariableEntry


def get_next_value(start_line_index: int, file_as_list: list[str], search_string: Optional[str] = None,
                   ignore_values: Optional[list[str]] = None,
                   replace_with: Union[str, VariableEntry, None] = None) -> Optional[str]:
    """Gets the next non blank value in a list of lines.

    Args:
        start_line_index (int): line number to start reading file_as_list from
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        search_string (str): string to search from within the first indexed line
        ignore_values (Optional[list[str]], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional): a value to replace the existing value with. \
            Defaults to None.

    Returns:
        Optional[str]: Next non blank value from the list, if none found returns None
    """
    invalid_characters = ["\n", "\t", " ", "!", ","]
    value_found = False
    value = ''
    if search_string is None:
        search_string = file_as_list[start_line_index]
    line_index = start_line_index
    while value_found is False and line_index <= len(file_as_list):
        character_location = 0
        new_search_string = False
        line_already_skipped = False
        if len(search_string) > 2 and search_string.startswith("\"") and search_string.endswith("\""):
            value += search_string[1:len(search_string) - 1]
            value_found = True
        else:
            for character in search_string:
                # move lines once we hit a comment character or new line character,or are at the end of search string
                if character == "!" or character == "\n" or (character_location == 0 and character == "C" and
                                                             (len(search_string) == 1 or search_string[
                                                                 character_location + 1] == ' ')):
                    line_index += 1
                    line_already_skipped = True
                    # If we've reached the end of the file, return None
                    if line_index >= len(file_as_list):
                        return None
                    # Move to the next line down in file_as_list
                    temp_search_string = file_as_list[line_index]
                    if not isinstance(temp_search_string, str):
                        raise ValueError(f'No valid value found, hit INCLUDE statement instead on line number \
                            {line_index}')
                    search_string = temp_search_string
                    break
                elif character not in invalid_characters:
                    value_string = search_string[character_location: len(search_string)]
                    for value_character in value_string:
                        # If we've formed a string we're supposed to ignore, ignore it and get the next value
                        if ignore_values is not None and (value in ignore_values or value.upper() in ignore_values):
                            search_string = search_string[character_location: len(search_string)]
                            new_search_string = True
                            value = ""

                        if value_character not in invalid_characters:
                            value += value_character

                        character_location += 1

                        # stop adding to the value once we hit an invalid_character
                        if value_character in invalid_characters and value != '':
                            break

                    if value != "":
                        value_found = True
                        # Replace the original value with the new requested value
                        if replace_with is not None:
                            original_line = file_as_list[line_index]
                            if not isinstance(original_line, str):
                                raise ValueError(f'No valid value found, hit INCLUDE statement instead on line number \
                                                {line_index}')
                            new_line = original_line

                            if isinstance(replace_with, str):
                                new_value = replace_with
                            elif isinstance(replace_with, VariableEntry):
                                new_line, new_value, value = __replace_with_variable_entry(new_line, original_line,
                                                                                           replace_with, value)
                            if new_value is None:
                                raise ValueError(f'Value for replacing has returned a null value,\
                                check replace_with input, {replace_with=}')
                            new_line = new_line.replace(value, new_value, 1)
                            file_as_list[line_index] = new_line

                        break

                if new_search_string is True:
                    break

                character_location += 1
        if not line_already_skipped:
            line_index += 1
        if line_index <= len(file_as_list) - 1:
            search_string = file_as_list[line_index]

    if not value_found:
        return None

    return value


def __replace_with_variable_entry(new_line: str, original_line: str, replace_with: VariableEntry, value: str):
    new_value = replace_with.value if replace_with.value is not None else ''
    if replace_with.modifier != 'VALUE':
        new_line = new_line.replace('INCLUDE ', '')
    elif 'INCLUDE' not in original_line:
        new_value = 'INCLUDE ' + replace_with.value if replace_with.value is not None else ''
    # If we are replacing the first value from a mult, remove the space as well
    if replace_with.modifier == 'MULT' and replace_with.value == '':
        value += ' '
    return new_line, new_value, value


# def __replace_multiple_entry():


def check_token(token: str, line: str) -> bool:
    """Checks if the text line contains the supplied token and is not commented out
    Args:
        token (str): keyword value to search the line for
        line (str): string to search the token in
    Returns:
        bool: True if the text line contains the supplied token, False otherwise.
    """
    token_separator_chars = [" ", '\n', '\t', '!']
    uppercase_line = line.upper()
    token_location = uppercase_line.find(token.upper())

    # Not found at all, return false
    if token_location == -1:
        return False

    if line.startswith('C '):
        return False

    comment_character_location = line.find("!")

    # Check if the line is commented out before the token appears
    if comment_character_location != -1 and comment_character_location < token_location:
        return False

    # Check if the character before the token is a separator such as space, tab etc and not another alphanumeric char
    if token_location != 0 and line[token_location - 1] not in token_separator_chars:
        return False

    # Check if the character after the token is a separator such as space, tab etc and not another alphanumeric char
    if token_location + len(token) != len(line) and line[token_location + len(token)] not in token_separator_chars:
        return False

    return True


def value_in_file(token: str, file: list[str]) -> bool:
    """Returns true if a token is found in the specified file.

    Args:
        token (str): the token being searched for.
        file (list[str]): a list of strings containing each line of the file as a new entry

    Returns:
        bool: True if the token is found and False otherwise
    """
    token_found = any(map(partial(check_token, token), file))

    return token_found


def get_token_value(token: str, token_line: str, file_list: list[str],
                    ignore_values: Optional[list[str]] = None,
                    replace_with: Union[str, VariableEntry, None] = None) -> Optional[str]:
    """Gets the value following a token if supplied with a line containing the token.

    Arguments:
        token (str): the token being searched for.
        token_line (str): string value of the line that the token was found in.
        file_list (list[str]): a list of strings containing each line of the file as a new entry
        ignore_values (list[str], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional):  a value to replace the existing value with. \
            Defaults to None.

    Returns:
        Optional[str]: The value following the supplied token, if it is present.
    """

    token_upper = token.upper()
    token_line_upper = token_line.upper()

    # If this line is commented out, don't return a value
    if "!" in token_line_upper and token_line_upper.index("!") < token_line_upper.index(token_upper):
        return None

    search_start = token_line_upper.index(token_upper) + len(token) + 1
    search_string = token_line[search_start: len(token_line)]
    line_index = file_list.index(token_line)

    # If we have reached the end of the line, go to the next line to start our search
    if len(search_string) < 1:
        line_index += 1
        if line_index >= len(file_list):
            return None
        search_string = file_list[line_index]
    if not isinstance(search_string, str):
        raise ValueError
    value = get_next_value(line_index, file_list, search_string, ignore_values, replace_with)
    return value


def get_expected_token_value(token: str, token_line: str, file_list: list[str],
                             ignore_values: Optional[list[str]] = None,
                             replace_with: Union[str, VariableEntry, None] = None,
                             custom_message: Optional[str] = None) -> str:
    """Function that returns the result of get_token_value if a value is found, otherwise it raises a ValueError.

    Args:
        token (str): the token being searched for.
        token_line (str): string value of the line that the token was found in.
        file_list (list[str]): a list of strings containing each line of the file as a new entry
        ignore_values (list[str], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional):  a value to replace the existing value with. \
            Defaults to None.
        custom_message Optional[str]: A custom error message if no value is found.

    Returns:
        str:  The value following the supplied token, if it is present.

    Raises:
        ValueError if a value is not found
    """
    value = get_token_value(token, token_line, file_list, ignore_values, replace_with)

    if value is None:
        if custom_message is None:
            raise ValueError(f"No value found in the line after the expected token ({token}), line: {token_line}")
        else:
            raise ValueError(f"{custom_message} {token_line}")

    return value
