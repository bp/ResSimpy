from io import StringIO
from typing import Optional, Union
import pandas as pd
from ResSimpy.Grid import VariableEntry
from string import Template
import re
from ResSimpy.Nexus.nexus_constants import VALID_NEXUS_KEYWORDS
import os


def nexus_token_found(line_to_check: str, valid_list: list[str] = VALID_NEXUS_KEYWORDS) -> bool:
    """
    Checks if a valid Nexus token has been found  in the supplied line

    Args:
        line_to_check (str):  The string to search for a Nexus keyword
        valid_list (list[str]): list of keywords to search from (e.g. from nexus_constants)

    Returns:
        token_found (bool): A boolean value stating whether the token is found or not

    """
    uppercase_line = line_to_check.upper()
    for token in valid_list:
        if check_token(token, uppercase_line):
            return True

    return False


def check_token(token: str, line: str) -> bool:
    """ Checks if the text line contains the supplied token and is not commented out
    Args:
        token (str): keyword value to search the line for
        line (str): string to search the token in
    Returns:
        bool: True if the text line contains the supplied token, False otherwise
    """
    token_separator_chars = [" ", '\n', '\t', '!']
    uppercase_line = line.upper()
    token_location = uppercase_line.find(token.upper())

    # Not found at all, return false
    if token_location == -1:
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


def get_next_value(start_line_index: int, file_as_list: list[str], search_string: Optional[str] = None,
                   ignore_values: Optional[list[str]] = None,
                   replace_with: Union[str, VariableEntry, None] = None) -> Optional[str]:
    """Gets the next non blank value in a list of lines

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
        for character in search_string:
            # move lines once we hit a comment character or new line character, or are at the end of the search string
            if character == "!" or character == "\n":
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
                    if ignore_values is not None and value in ignore_values:
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
                            new_value = replace_with.value if replace_with.value is not None else ''

                            if replace_with.modifier != 'VALUE':
                                new_line = new_line.replace('INCLUDE ', '')
                            elif 'INCLUDE' not in original_line:
                                new_value = 'INCLUDE ' + replace_with.value if replace_with.value is not None else ''

                            # If we are replacing the first value from a mult, remove the space as well
                            if replace_with.modifier == 'MULT' and replace_with.value == '':
                                value += ' '
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


def get_expected_next_value(start_line_index: int, file_as_list: list[str], search_string: Optional[str] = None,
                            ignore_values: Optional[list[str]] = None,
                            replace_with: Union[str, VariableEntry, None] = None,
                            custom_message: Optional[str] = None) -> str:
    """Gets the next non blank value in a list of lines

    Args:
        start_line_index (int): line number to start reading file_as_list from
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        search_string (str): string to search from within the first indexed line
        ignore_values (Optional[list[str]], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional): a value to replace the existing value with. \
            Defaults to None.
        custom_message Optional[str]: A custom error message if no value is found

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


def get_token_value(token: str, token_line: str, file_list: list[str],
                    ignore_values: Optional[list[str]] = None,
                    replace_with: Union[str, VariableEntry, None] = None) -> Optional[str]:
    """Gets the value following a token if supplied with a line containing the token.

    arguments:
        token (str): the token being searched for.
        token_line (str): string value of the line that the token was found in.
        file_list (list[str]): a list of strings containing each line of the file as a new entry
        ignore_values (list[str], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional):  a value to replace the existing value with. \
            Defaults to None.

    returns:
        Optional[str]: The value following the supplied token, if it is present.
    """

    # If this line is commented out, don't return a value
    if "!" in token_line and token_line.index("!") < token_line.index(token):
        return None

    token_upper = token.upper()
    token_line_upper = token_line.upper()

    search_start = token_line_upper.index(token_upper) + len(token) + 1
    search_string = token_line[search_start: len(token_line)]
    line_index = file_list.index(token_line)

    # If we have reached the end of the line, go to the next line to start our search
    if len(search_string) < 1:
        line_index += 1
        search_string = file_list[line_index]
    if not isinstance(search_string, str):
        raise ValueError
    value = get_next_value(line_index, file_list, search_string, ignore_values, replace_with)
    return value


def get_expected_token_value(token: str, token_line: str, file_list: list[str],
                             ignore_values: Optional[list[str]] = None,
                             replace_with: Union[str, VariableEntry, None] = None,
                             custom_message: Optional[str] = None) -> str:
    """Function that returns the result of get_token_value if a value is found, otherwise it raises a ValueError
     arguments:
        token (str): the token being searched for.
        token_line (str): string value of the line that the token was found in.
        file_list (list[str]): a list of strings containing each line of the file as a new entry
        ignore_values (list[str], optional): a list of values that should be ignored if found. \
            Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional):  a value to replace the existing value with. \
            Defaults to None.
        custom_message Optional[str]: A custom error message if no value is found

    returns:
        str:  The value following the supplied token, if it is present.

    raises: ValueError if a value is not found
    """
    value = get_token_value(token, token_line, file_list, ignore_values, replace_with)

    if value is None:
        if custom_message is None:
            raise ValueError(f"No value found in the line after the expected token ({token}), line: {token_line}")
        else:
            raise ValueError(f"{custom_message} {token_line}")

    return value


def strip_file_of_comments(file_as_list: list[str], strip_str: bool = False) -> list[str]:
    """Strips all of the inline, single and multi line comments out of a file.
    Comment characters assumed are: ! and square brackets. Escaped characters are ones wrapped in quotation marks

    Args:
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        strip_str (bool, optional): if True strips the lines of whitespace. Defaults to False.
    Returns:
        list[str]: a list of strings containing each line of the file as a new entry without comments
    """
    # TODO: support VIP comment out single C character
    # remove any empty lines
    file_as_list = list(filter(None, file_as_list))

    # regex: look back and forward 1 character from an ! and check if its a quotation mark and
    # exclude it from the match if it is
    file_without_comments = [re.split(r'(?<!\")!(?!\")', x)[0] for x in file_as_list if x and x[0] != '!']

    flat_file = '\n'.join(file_without_comments)

    # regex: look back and forward 1 character from a square bracket and check if its a quotation mark and
    # exclude it from the match if it is
    flatfile_minus_square_brackets = re.sub(r"(?<!\")\[.*?\](?!\")", '', flat_file, flags=re.DOTALL)

    file_without_comments = flatfile_minus_square_brackets.splitlines()

    if strip_str:
        file_without_comments = [x.strip() for x in file_without_comments]
    return file_without_comments


def load_file_as_list(file_path: str, strip_comments: bool = False, strip_str: bool = False) -> list[str]:
    """ Reads the text file into a variable
    Args:
        file_path (str): string containing a path pointing towards a text file
        strip_comments (bool, optional): If set to True removes all inline/single line comments from \
            the passed in file. Defaults to False.
        strip_str (bool, optional): if True strips the lines of whitespace. Defaults to False.

    Returns:
        list[str]: list of strings with each line from the file a new entry in the list
     """
    with open(file_path, 'r') as f:
        file_content = list(f)

    if strip_comments:
        file_content = strip_file_of_comments(file_content, strip_str=strip_str)

    return file_content


def create_templated_file(template_location: str, substitutions: dict, output_file_name: str):
    """Creates a new text file at the requested destination substituting the supplied values.

    Args:
        template_location (str): path to the template file
        substitutions (dict): dictionary of substitutions to be made {variable: subsistuted_value,}
        output_file_name (str): path/name of the file to write out to
    """

    class NewTemplate(Template):
        delimiter = '**!'

    with open(template_location, 'r') as template_file:
        template = NewTemplate(template_file.read())

    output_file = template.substitute(substitutions)

    # Create the output file
    with open(output_file_name, 'w') as new_file:
        new_file.write(output_file)


def expand_include(file_as_list: list[str], recursive: bool = True) -> tuple[list[str], Optional[str]]:
    """Expands out include files. If recursive set to True will expand all includes including nested

    Args:
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        recursive (bool): If recursive set to True will expand all includes including nested includes

    Raises:
        ValueError: if no value found after INCLUDE keyword in file

    Returns:
        list[str]: list of strings containing each line of the file as a new entry but with files following includes \
            expanded out
    """
    no_comment_file = strip_file_of_comments(file_as_list, strip_str=True)

    # Initialize iterator variables, if no Include is found then return the prvious file
    old_file_contents = no_comment_file.copy()
    inc_file_path = None
    expanded_file = old_file_contents
    for i, line in enumerate(no_comment_file):
        if "INCLUDE" in line.upper():
            # doesn't necessarily work if the file is a relative reference
            inc_file_path = get_expected_token_value('INCLUDE', line, [line],
                                                     custom_message="No value found after INCLUDE keyword in")
            inc_data = load_file_as_list(inc_file_path, strip_comments=True, strip_str=True)
            inc_data = list(filter(None, inc_data))

            # this won't work with arbitrary whitespace
            prefix_line, suffix_line = re.split(
                'INCLUDE', line, maxsplit=1, flags=re.IGNORECASE)
            suffix_line = suffix_line.lstrip()
            suffix_line = suffix_line.replace(inc_file_path, '', 1)
            expanded_file = old_file_contents[0:i]

            if prefix_line:
                expanded_file += [prefix_line]
            expanded_file += inc_data
            if suffix_line:
                expanded_file += [suffix_line]
            expanded_file += old_file_contents[i + 1::]
            break
    # if INCLUDE is not found in the file provided then inc_file_path is None and so will break recursion
    if recursive:
        while inc_file_path is not None:
            expanded_file, inc_file_path = expand_include(expanded_file)
    return expanded_file, inc_file_path


def get_full_file_path(file_path: str, origin: str):
    """Returns the full file path including the base directories if they aren't present in the string

    Args:
        file_path (str): the initial file path found in a file
        origin (str): the initial origin of the file
    """
    if os.path.isabs(file_path):
        return_path = file_path
    else:
        return_path = str(os.path.join(os.path.dirname(origin), file_path))
    return return_path


def read_table_to_df(file_as_list: list[str], keep_comments: bool = False) -> pd.DataFrame:
    """From a list of strings that represents a table, generate a Pandas dataframe representation of the table

    Args:
        file_as_list (list[str]): List of strings representing a single table to be read
        keep_comments (bool): Boolean to determine if we keep comments as a separate column or not

    Returns:
        pd.DataFrame: Created Pandas DataFrame representation of table to be read
    """
    df = pd.DataFrame()
    if not keep_comments:
        # Clean of comments
        cleaned_file_as_list = strip_file_of_comments(file_as_list, strip_str=True)
        # Create dataframe
        df = pd.read_csv(StringIO('\n'.join(cleaned_file_as_list)), sep=r'\s+')
        df.columns = [col.upper() for col in df.columns if isinstance(col, str)]
    else:  # Going to retain comments as a separate column in dataframe
        # Clean of comments
        cleaned_file_as_list = [re.split(r'(?<!\")!(?!\")', line)[0].strip()
                                if line and line[0] != '!' else line
                                for line in file_as_list]
        cleaned_file_as_list = [line if not line.startswith('!') else '' for line in cleaned_file_as_list]
        # Save comments in a list
        comment_column = [line.split('!', 1)[1].strip() if '!' in line else None for line in file_as_list]
        # Create dataframe
        df = pd.read_csv(StringIO('\n'.join(cleaned_file_as_list) + '\n'), sep=r'\s+', skip_blank_lines=False)
        df.columns = [col.upper() for col in df.columns if isinstance(col, str)]
        if any(x is not None for x in comment_column):  # If comment column isn't a full column of Nones
            df['COMMENT'] = comment_column[1:]
        df = df.convert_dtypes().dropna(axis=0, how='all').reset_index(drop=True)
    return df


def clean_up_string(value: str) -> str:
    """Removes unwanted characters from a string
        unwanted characters: ("\\n", "\\t", "!")
    Args:
        value (str): string to clean up
    Returns:
        str: string with unwanted characters removed
    """
    value = value.replace("\n", "")
    value = value.replace("!", "")
    value = value.replace("\t", "")
    return value


def get_multiple_sequential_tokens(list_of_strings: list[str], number_tokens: int) -> list[str]:
    """Returns a sequential list of tokens as long as the number of tokens requested.

    Args:
        list_of_strings (list[str]): list of strings to represent the file with a new entry per line in the file.
        number_tokens (int): number of tokens to return values of

    Raises:
        ValueError: if too many tokens are requested compared to the file provided

    Returns:
        list[str]: list of strings comprised of the token values in order.
    """
    store_values = []
    filter_list = list_of_strings.copy()
    for i in range(0, number_tokens):
        # TODO: change to get_expected_next_value
        value = get_next_value(0, filter_list, filter_list[0], replace_with='')
        while value is None:
            # if no valid value found in the first line, remove it and try it again
            filter_list.pop(0)
            if len(filter_list) == 0:
                raise ValueError('Too many values requested from the list of strings passed')
            value = get_next_value(0, filter_list, filter_list[0], replace_with='')
        store_values.append(value)

    return store_values


def check_for_common_input_data(file_as_list: list[str], property_dict: dict) -> dict:
    """Loop through lines of Nexus input file content looking for common input data, e.g.,
    units such as ENGLISH or METRIC, temparure units such as FAHR or CELSIUS, DATEFORMAT, etc.,
    as defined in Nexus manual. If any found, include in provided property_dict and return

    Args:
        file_as_list (list[str]): Nexus input file content
        property_dict (dict): Dictionary in which to include common input data if found

    Returns:
        dict: Dictionary including found common input data
    """
    for line in file_as_list:
        # Check for description
        if check_token('DESC', line):
            if 'DESC' in property_dict.keys():
                property_dict['DESC'].append(line.split('DESC')[1].strip())
            else:
                property_dict['DESC'] = [line.split('DESC')[1].strip()]
        # Check for label
        if check_token('LABEL', line):
            property_dict['LABEL'] = get_token_value('LABEL', line, file_as_list)
        # Check for dateformat
        if check_token('DATEFORMAT', line):
            property_dict['DATEFORMAT'] = get_token_value('DATEFORMAT', line, file_as_list)
        # Check unit system specification
        if check_token('ENGLISH', line):
            property_dict['UNIT_SYSTEM'] = 'ENGLISH'
            property_dict['TEMP_UNIT'] = 'FAHR'
        if check_token('METRIC', line):
            property_dict['UNIT_SYSTEM'] = 'METRIC'
            property_dict['TEMP_UNIT'] = 'CELSIUS'
        if check_token('METKG/CM2', line):
            property_dict['UNIT_SYSTEM'] = 'METKG/CM2'
        if check_token('METBAR', line):
            property_dict['UNIT_SYSTEM'] = 'METBAR'
            property_dict['TEMP_UNIT'] = 'CELSIUS'
        if check_token('LAB', line):
            property_dict['UNIT_SYSTEM'] = 'LAB'
            property_dict['TEMP_UNIT'] = 'CELSIUS'
        # Check to see if sality unit is provided
        if check_token('SUNITS', line):
            property_dict['SUNITS'] = get_token_value('SUNITS', line, file_as_list)
        # Check to see if temperature units are provided
        if check_token('KELVIN', line):
            property_dict['TEMP_UNIT'] = 'KELVIN'
        if check_token('RANKINE', line):
            property_dict['TEMP_UNIT'] = 'RANKINE'
        if check_token('FAHR', line):
            property_dict['TEMP_UNIT'] = 'FAHR'
        if check_token('CELSIUS', line):
            property_dict['TEMP_UNIT'] = 'CELSIUS'

    return property_dict


def value_in_file(token: str, file: list[str]) -> bool:
    """Returns true if a token is found in the specified file

    Args:
        token (str): the token being searched for.
        file (list[str]): a list of strings containing each line of the file as a new entry

    Returns:
        bool: True if the token is found and False otherwise
    """
    token_found = False
    for line in file:
        if check_token(token, line):
            token_found = True

    return token_found
