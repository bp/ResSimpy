from functools import partial
from typing import Optional, Union
import re
from string import whitespace

from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition


def strip_file_of_comments(file_as_list: list[str], strip_str: bool = False,
                           comment_characters: Optional[list[str]] = None,
                           square_bracket_comments: bool = False) -> list[str]:
    """Strips all of the inline, single and multi line comments out of a file.

    Comment characters assumed are: ! and square brackets. Escaped characters are ones wrapped in quotation marks.

    Args:
        square_bracket_comments (bool): whether to also remove text contained in square brackets ([])
        comment_characters (Optional[list[str]]): A list of characters that are considered comments. Defaults to the
                                                  Nexus format (!)
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        strip_str (bool, optional): if True strips the lines of whitespace. Defaults to False.

    Returns:
        list[str]: a list of strings containing each line of the file as a new entry without comments
    """
    if comment_characters is None:
        comment_characters = ['!']
    file_as_list = list(filter(None, file_as_list))

    file_without_comments = file_as_list

    for comment_character in comment_characters:
        if comment_character == 'C':  # handle VIP comment with single C character at the start of a line
            file_without_comments = [line for line in file_without_comments if not line.startswith('C ') and not
                                     line.strip() == 'C']
        else:
            # remove any empty lines
            # regex: look back and forward 1 character from an ! and check if it's a quotation mark and
            # exclude it from the match if it is
            file_without_comments = [re.split(fr'(?<!\"){comment_character}(?!\")', x)[0]
                                     for x in file_without_comments if x and x[0] != comment_character]

    flat_file = '\n'.join(file_without_comments)

    if square_bracket_comments:
        # regex: look back and forward 1 character from a square bracket and check if it's a quotation mark and
        # exclude it from the match if it is
        flatfile_minus_square_brackets = flat_file
        for comment_character in comment_characters:
            flatfile_minus_square_brackets = re.sub(fr"(?<!\")\[.*?](?{comment_character}\")", '',
                                                    flatfile_minus_square_brackets, flags=re.DOTALL)

        file_without_comments = flatfile_minus_square_brackets.splitlines()

    if strip_str:
        file_without_comments = [x.strip() for x in file_without_comments]
    return file_without_comments


def load_file_as_list(file_path: str, strip_comments: bool = False, strip_str: bool = False,
                      comment_characters: Optional[list[str]] = None) -> list[str]:
    """Reads the text file into a variable.

    Args:
        file_path (str): string containing a path pointing towards a text file
        strip_comments (bool, optional): If set to True removes all inline/single line comments from \
            the passed in file. Defaults to False.
        strip_str (bool, optional): if True strips the lines of whitespace. Defaults to False.
        comment_characters (list[str], optional): A list of characters that are considered comments.

    Returns:
        list[str]: list of strings with each line from the file a new entry in the list
    """
    try:
        with open(file_path, 'r') as f:
            file_content = list(f)
    except UnicodeDecodeError:
        with open(file_path, 'r', errors='replace') as f:
            file_content = list(f)

    if strip_comments:
        file_content = strip_file_of_comments(file_content, strip_str=strip_str,
                                              comment_characters=comment_characters)
        file_content = list(filter(None, file_content))

    return file_content


def get_next_value(start_line_index: int, file_as_list: list[str], search_string: None | str = None,
                   ignore_values: None | list[str] = None,
                   replace_with: str | GridArrayDefinition | None = None,
                   comment_characters: None | list[str] = None,
                   single_c_acts_as_comment: bool = True) -> Optional[str]:
    """Gets the next non blank value in a list of lines.

    Args:
        start_line_index (int): line number to start reading file_as_list from
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        search_string (str): string to search from within the first indexed line
        ignore_values (Optional[list[str]], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (str | VariableEntry | None], optional): a value to replace the existing value with. \
            Defaults to None.
        comment_characters (Optional[list[str]], optional): a list of characters that are considered inline comments.
            Defaults to the Nexus format (!)
        single_c_acts_as_comment: (bool): whether a single C character at the start of a line should be treated as a
            comment. Defaults to Nexus setting which is True.

    Returns:
        Optional[str]: Next non blank value from the list, if none found returns None
    """
    if comment_characters is None:
        comment_characters = ['!']
    invalid_characters = ["\n", "\t", " ", ","]
    invalid_characters.extend(comment_characters)
    if ignore_values is None:
        ignore_values = []
    ignore_values = [x.upper() for x in ignore_values]

    value_found = False
    value = ''
    if search_string is None:
        search_string = file_as_list[start_line_index]
    line_index = start_line_index
    while value_found is False and line_index <= len(file_as_list):
        character_location = 0
        new_search_string = False
        line_already_skipped = False

        # If the string is wrapped in quotation marks, return the full string (including invalid characters)
        if len(search_string) > 2 and search_string.startswith("\"") and search_string.endswith("\""):
            value += search_string[1:len(search_string) - 1]
            value_found = True
            break

        for character in search_string:
            # move lines once we hit a comment character or new line character,or are at the end of search string
            starts_with_c_only = (single_c_acts_as_comment and
                                  (character_location == 0 and character == "C" and
                                   (len(search_string) == 1 or search_string[character_location + 1] == ' ')))
            if character in comment_characters or character == "\n" or starts_with_c_only:
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
                ignore_value_found = True  # Initialise as True because Python doesn't want to implement a do loop...
                while ignore_value_found:
                    character_location, new_search_string, search_string, value = (
                        __extract_substring_until_next_invalid_character(character_location=character_location,
                                                                         invalid_characters=invalid_characters,
                                                                         new_search_string=new_search_string,
                                                                         search_string=search_string,
                                                                         comment_characters=comment_characters))

                    ignore_value_found = value.upper() in ignore_values

                # if the substring is a not an empty string, we've found a value
                if value != "":
                    value_found = True
                    # Replace the original value with the new requested value
                    if replace_with is not None:
                        value = __replace_value_in_file_as_list(file_as_list, line_index, replace_with, value)
                    break

            if new_search_string:
                break

            character_location += 1
        if not line_already_skipped:
            line_index += 1
        if line_index <= len(file_as_list) - 1:
            search_string = file_as_list[line_index]

    if not value_found:
        return None

    return value


def __replace_value_in_file_as_list(file_as_list: list[str], line_index: int, replace_with: str | GridArrayDefinition,
                                    value: str) -> str:
    """Replaces a value in a file_as_list with a new value.

    Args:
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        line_index (int): line number from file_as_list to replace the value in.
        replace_with (str | VariableEntry): a value to replace the existing value with.
        value (str): the value to be replaced.

    Returns:
        str: the value that has been replaced.
    """
    original_line = file_as_list[line_index]
    if not isinstance(original_line, str):
        raise ValueError(f'No valid value found, hit INCLUDE statement instead on line number \
                                            {line_index}')
    new_line = original_line
    if isinstance(replace_with, str):
        new_value = replace_with
    elif isinstance(replace_with, GridArrayDefinition):
        new_line, new_value, value = __replace_with_variable_entry(new_line, original_line,
                                                                   replace_with, value)
    if new_value is None:
        raise ValueError(f'Value for replacing has returned a null value,\
                            check replace_with input, {replace_with=}')
    new_line = new_line.replace(value, new_value, 1)
    file_as_list[line_index] = new_line
    return value


def __extract_substring_until_next_invalid_character(character_location: int,
                                                     invalid_characters: list[str],
                                                     new_search_string: bool,
                                                     search_string: str,
                                                     comment_characters: list[str]) \
        -> tuple[int, bool, str, str]:
    """Extracts a substring from the search_string until an invalid character is found.

    Args:
        character_location (int): current location in the search_string
        invalid_characters (list[str]): list of characters that are considered invalid
        new_search_string (bool): whether we are starting a new search string
        search_string (str): string to search from within the first indexed line
        comment_characters (list[str]): A list of the comment characters for the current simulator
    Returns:
        int: new character location in the search_string
        bool: whether we are starting a new search string
        str: new search string if a value has been ignored
        str: the value that has been built up, or blank if a value has been ignored
    """
    value_string = search_string[character_location: len(search_string)]
    value = ''
    for value_character in value_string:
        if value_character.upper() in comment_characters:
            character_location = len(search_string)
            return character_location, new_search_string, search_string, value

        # stop adding to the value once we hit an invalid_character
        if value_character in invalid_characters and value != '':
            break

        if value_character not in invalid_characters:
            value += value_character

        character_location += 1

    return character_location, new_search_string, search_string, value


def __replace_with_variable_entry(new_line: str, original_line: str, replace_with: GridArrayDefinition, value: str) \
        -> tuple[str, str, str]:
    new_value = replace_with.value if replace_with.value is not None else ''
    if replace_with.modifier != 'VALUE':
        new_line = new_line.replace('INCLUDE ', '')
    elif 'INCLUDE' not in original_line:
        new_value = 'INCLUDE ' + replace_with.value if replace_with.value is not None else ''
    # If we are replacing the first value from a mult, remove the space as well
    if replace_with.modifier == 'MULT' and replace_with.value == '':
        value += ' '
    return new_line, new_value, value


def check_token(token: str, line: str) -> bool:
    """Checks if the text line contains the supplied token and is not commented out.

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
                    replace_with: Union[str, GridArrayDefinition, None] = None) -> Optional[str]:
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
                             replace_with: Union[str, GridArrayDefinition, None] = None,
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
        custom_message (Optional[str]): A custom error message if no value is found.

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


def load_in_three_part_date(initial_token: str, token_line: str, file_as_list: list[str], start_index: int) -> str:
    """Function that reads in a three part date separated by spaces e.g. 1 JAN 2024.

    Args:
    initial_token (str): The token that will appear before the start of the date e.g. DATE
    token_line (str): Line in the file that the token has been found.
    file_as_list (list[str]): The whole file as a list of strings.
    start_index (int): The index in file_as_list where the token can be found.

    Returns:
    str:  The three part date as a string.
    """

    # Get the three parts of the date
    first_date_part = get_expected_token_value(token=initial_token, token_line=token_line,
                                               file_list=file_as_list)

    snipped_string = token_line.replace(initial_token, '')
    snipped_string = snipped_string.replace(first_date_part, '', 1)

    second_date_part = get_expected_next_value(start_line_index=start_index, file_as_list=file_as_list,
                                               search_string=snipped_string)

    snipped_string = snipped_string.replace(second_date_part, '', 1)

    third_date_part = get_next_value(start_line_index=start_index, file_as_list=file_as_list,
                                     search_string=snipped_string)

    full_date = f"{first_date_part} {second_date_part} {third_date_part}"
    return full_date


def get_expected_next_value(start_line_index: int, file_as_list: list[str], search_string: Optional[str] = None,
                            ignore_values: Optional[list[str]] = None,
                            replace_with: Union[str, GridArrayDefinition, None] = None,
                            custom_message: Optional[str] = None) -> str:
    """Gets the next non blank value in a list of lines.

    Args:
        start_line_index (int): line number to start reading file_as_list from
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        search_string (str): string to search from within the first indexed line
        ignore_values (Optional[list[str]], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional): a value to replace the existing value with. \
            Defaults to None.
        custom_message (Optional[str]): A custom error message if no value is found

    Returns:
        str: Next non blank value from the list, if none found raises ValueError
    """
    value = get_next_value(start_line_index, file_as_list, search_string, ignore_values, replace_with)

    if value is None:
        if custom_message is None:
            raise ValueError(f"No value found in the line, line: {file_as_list[start_line_index]}")
        else:
            raise ValueError(f"{custom_message} {file_as_list[start_line_index]}")

    return value


def get_multiple_expected_sequential_values(list_of_strings: list[str], number_tokens: int,
                                            ignore_values: list[str]) -> list[str]:
    """Returns a sequential list of values as long as the number of tokens requested.

    Args:
        list_of_strings (list[str]): list of strings to represent the file with a new entry per line in the file.
        number_tokens (int): number of tokens to return values of
        ignore_values (list[str]): list of values to ignore if found

    Raises:
        ValueError: if too many tokens are requested compared to the file provided

    Returns:
        list[str]: list of strings comprised of the token values in order.
    """
    store_values: list[str] = []
    filter_list = list_of_strings.copy()
    for i in range(number_tokens):
        value = get_next_value(0, filter_list, filter_list[0], replace_with='',
                               ignore_values=ignore_values)
        if value is None:
            # if no valid value found, raise an error
            raise ValueError('Too many values requested from the list of strings passed,'
                             f' instead found: {len(store_values)} values, out of the requested {number_tokens}')
        store_values.append(value)

    return store_values


def get_nth_value(list_of_strings: list[str], value_number: int, ignore_values: list[str]) -> Optional[str]:
    """Returns the Nth value from a list of strings.

    Args:
        list_of_strings (list[str]): list of strings to represent the file with a new entry per line in the file.
        value_number (int): the index of the value that should be returned.One-based rather than zero-based.
        ignore_values (list[str]): list of values to ignore if found.

    Returns:
        Optional[str]: the value found at that location, if one is found
    """
    found_value: Optional[str] = None
    filter_list = list_of_strings.copy()

    if len(filter_list) == 0:
        return None

    for i in range(value_number):
        found_value = get_next_value(0, filter_list, filter_list[0], replace_with='',
                                     ignore_values=ignore_values)
        if found_value is None:
            return None

    return found_value


def split_lines_for_long_string(long_string: str, max_length: int) -> str:
    """Splits a long string into a list of strings with a maximum length.

    Args:
        long_string (str): The long string to be split.
        max_length (int): The maximum length of each string in the list.

    Returns:
        list[str]: A list of strings split from the long string.
    """
    # find the indices of whitespace characters

    whitespace_indices = [i for i, char in enumerate(long_string) if char in whitespace]
    compiled_string = ''
    for i in range(len(whitespace_indices) - 1):
        if whitespace_indices[i + 1] > max_length:
            compiled_string += long_string[:whitespace_indices[i]] + '\n'
            length_of_short_line = len(long_string[:whitespace_indices[i] + 1])
            long_string = long_string[whitespace_indices[i] + 1:]
            # adjust the indices for the newly created line and check the line length again
            whitespace_indices = [x - length_of_short_line for x in whitespace_indices]
    compiled_string += long_string
    return compiled_string


def split_list_of_strings_by_length(list_of_strings: list[str], max_length: int) -> list[str]:
    """Splits a list of strings into a new list of strings with a maximum length.

    Args:
        list_of_strings (list[str]): The list of strings to be split.
        max_length (int): The maximum length of each string in the new list.

    Returns:
        list[str]: A new list of strings split from the original list.
    """
    return [split_lines_for_long_string(string, max_length) for string in list_of_strings]
