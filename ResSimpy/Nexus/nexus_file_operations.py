from __future__ import annotations

from enum import Enum
from functools import partial
from io import StringIO
from typing import Optional, Union, Any, TYPE_CHECKING, Sequence
import pandas as pd
from ResSimpy.Grid import VariableEntry
from string import Template
import re
import os

from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem, TemperatureUnits, SUnits
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.nexus_keywords import VALID_NEXUS_KEYWORDS

if TYPE_CHECKING:
    from ResSimpy.Nexus.DataModels.NexusFile import NexusFile


def nexus_token_found(line_to_check: str, valid_list: list[str] = VALID_NEXUS_KEYWORDS) -> bool:
    """
    Checks if a valid Nexus token has been found  in the supplied line

    Args:
        line_to_check (str):  The string to search for a Nexus keyword
        valid_list (list[str]): list of keywords to search from (e.g. from nexus_constants)

    Returns:
        token_found (bool): A boolean value stating whether the token is found or not

    """
    valid_set = set(valid_list)
    uppercase_line = line_to_check.upper()
    strip_comments = strip_file_of_comments([uppercase_line])
    if len(strip_comments) == 0:
        return False
    split_line = set(strip_comments[0].split())

    return not valid_set.isdisjoint(split_line)


def value_in_file(token: str, file: list[str]) -> bool:
    """Returns true if a token is found in the specified file

    Args:
        token (str): the token being searched for.
        file (list[str]): a list of strings containing each line of the file as a new entry

    Returns:
        bool: True if the token is found and False otherwise
    """
    token_found = any(map(partial(check_token, token), file))

    return token_found


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
    try:
        with open(file_path, 'r') as f:
            file_content = list(f)
    except UnicodeDecodeError:
        with open(file_path, 'r', errors='replace') as f:
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


def get_multiple_sequential_values(list_of_strings: list[str], number_tokens: int) -> list[str]:
    """Returns a sequential list of values as long as the number of tokens requested.

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
        value = get_expected_next_value(0, filter_list, filter_list[0], replace_with='')
        while value is None:
            # if no valid value found in the first line, remove it and try it again
            filter_list.pop(0)
            if len(filter_list) == 0:
                raise ValueError('Too many values requested from the list of strings passed')
            value = get_next_value(0, filter_list, filter_list[0], replace_with='')
        store_values.append(value)

    return store_values


def check_for_common_input_data(file_as_list: list[str], property_dict: dict) -> dict[str, str | list[str] | Enum]:
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
        check_property_in_line(line, property_dict, file_as_list)

    return property_dict


def check_property_in_line(line: str, property_dict: dict, file_as_list: list[str]) -> dict:
    """Given a line of Nexus input file content looking for common input data, e.g.,
        units such as ENGLISH or METRIC, temperature units such as FAHR or CELSIUS, DATEFORMAT, etc.,
        as defined in Nexus manual. If any found, include in provided property_dict and return

        Args:
            line (str): line to search for the common input data
            file_as_list (list[str]): Nexus input file content
            property_dict (dict): Dictionary in which to include common input data if found

        Returns:
            dict: Dictionary including found common input data
        """
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
        date_format_value = get_expected_token_value('DATEFORMAT', line, file_as_list)
        if date_format_value == 'MM/DD/YYYY':
            property_dict['DATEFORMAT'] = DateFormat.MM_DD_YYYY
        else:
            property_dict['DATEFORMAT'] = DateFormat.DD_MM_YYYY
    # Check unit system specification
    if check_token('ENGLISH', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.ENGLISH
        property_dict['TEMP_UNIT'] = TemperatureUnits.FAHR
    if check_token('METRIC', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.METRIC
        property_dict['TEMP_UNIT'] = TemperatureUnits.CELSIUS
    if check_token('METKG/CM2', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.METKGCM2
    if check_token('METBAR', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.METBAR
        property_dict['TEMP_UNIT'] = TemperatureUnits.CELSIUS
    if check_token('LAB', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.LAB
        property_dict['TEMP_UNIT'] = TemperatureUnits.CELSIUS
    # Check to see if salinity unit is provided
    if check_token('SUNITS', line):
        s_units_value = get_expected_token_value('SUNITS', line, file_as_list)
        if s_units_value == 'PPM':
            property_dict['SUNITS'] = SUnits.PPM
        else:
            property_dict['SUNITS'] = SUnits.MEQ_ML
    # Check to see if temperature units are provided
    if check_token('KELVIN', line):
        property_dict['TEMP_UNIT'] = TemperatureUnits.KELVIN
    if check_token('RANKINE', line):
        property_dict['TEMP_UNIT'] = TemperatureUnits.RANKINE
    if check_token('FAHR', line):
        property_dict['TEMP_UNIT'] = TemperatureUnits.FAHR
    if check_token('CELSIUS', line):
        property_dict['TEMP_UNIT'] = TemperatureUnits.CELSIUS
    return property_dict


def looks_like_grid_array(file_path: str, lines2check: int = 10) -> bool:
    """Returns true if a Nexus include file begins with one of the
    Nexus grid array keywords.

    Args:
        file_path (str): Path to Nexus include file
        lines2check (int): First number of lines in file to check, looking for
        a Nexus grid array keyword. Default: first 10 lines of file

    Returns:
        bool: True if file begins with one of Nexus grid array keywords
    """
    with open(file_path, 'r') as f:

        for i in range(0, lines2check):
            line = f.readline()
            line_elems = line.split()
            found_keywords = [word for word in line_elems if (word in GRID_ARRAY_KEYWORDS) and
                              check_token(word, line)]
            if found_keywords:
                for word in found_keywords:
                    if (line_elems.index(word) < len(line_elems) - 1 and
                            line_elems[line_elems.index(word) + 1].upper() == 'VALUE'):
                        return True
    return False


def get_table_header(file_as_list: list[str], header_values: dict[str, str]) -> tuple[int, list[str]]:
    """ Gets the table headers for a given line in a file.
    Args:
        file_as_list (list[str]): file represented as a list of strings
        header_values (dict[str, str]): dictionary of column headings to populate from the table
    Raises:
        ValueError: if no headers belonging to the header_values dict is found
    Returns:
        int, list[str]: index in the file provided for the header, list of headers
    """
    headers = []
    header_index = -1
    for index, line in enumerate(file_as_list):
        for key in header_values:
            if check_token(key, line):
                header_line = line.upper()
                header_index = index
                # Map the headers
                next_column_heading = get_next_value(start_line_index=0, file_as_list=[line])
                trimmed_line = header_line

                while next_column_heading is not None:
                    headers.append(next_column_heading)
                    trimmed_line = trimmed_line.replace(next_column_heading, "", 1)
                    next_column_heading = get_next_value(0, [trimmed_line], trimmed_line)

                if len(headers) > 0:
                    break
        if len(headers) > 0:
            break
    if header_index == -1:
        raise ValueError('No headers belonging to the header_values dictionary found within the provided file')
    return header_index, headers


def table_line_reader(keyword_store: dict[str, None | int | float | str], headers: list[str], line: str) -> \
        tuple[bool, dict[str, None | int | float | str]]:
    """ reads in a line from a nexus table with a given set of headers and populates each of those values into a \
    corresponding dictionary

    Args:
        keyword_store (dict[str, None | int | float | str]):
        headers (list[str]):
        line (str):

    Returns:
        tuple[bool, dict[str, None | int | float | str]]: a dictionary with the found set of
    """
    trimmed_line = line
    valid_line = True
    for column in headers:
        value = get_next_value(0, [trimmed_line], trimmed_line)
        if value is None:
            valid_line = False
            break

        keyword_store[column] = value
        trimmed_line = trimmed_line.replace(value, "", 1)
    return valid_line, keyword_store


def load_table_to_objects(file_as_list: list[str], row_object: Any, property_map: dict[str, tuple[str, type]],
                          current_date: Optional[str] = None, unit_system: Optional[UnitSystem] = None,
                          list_of_objects: Optional[list[Any]] = None) -> list[Any]:
    """ Loads a table row by row to an object provided in the row_object.

    Args:
        file_as_list (list[str]): file represented as a list of strings.
        row_object (Any): class to populate, should take a dictionary of attributes as an argument to the __init__
        property_map (dict[str, tuple[str, type]]): map of the Nexus keywords as keys to the dictionary and the names\
            of the object attribute and the type of that attribute as a tuple in the values.
            e.g. {'NAME': ('name', str)} for the object obj with attribute obj.name
        current_date (Optional[str]): date/time at which the object was found within a recurrent file
        unit_system (Optional[UnitSystem): most recent UnitSystem enum of the file where the object was found
        list_of_objects (Optional[list[Any]]): list of objects to append to. If None creates an empty list to populate.

    Returns:
        list[obj]: list of instances of the class provided for the row_object, populated with attributes from the\
            property map dictionary.
    """
    keyword_map = {x: y[0] for x, y in property_map.items()}
    header_index, headers = get_table_header(file_as_list, keyword_map)
    table_as_list = file_as_list[header_index + 1::]
    if list_of_objects is None:
        list_of_objects = []
    for line in table_as_list:
        keyword_store: dict[str, None | int | float | str] = {x: None for x in property_map.keys()}
        valid_line, keyword_store = table_line_reader(keyword_store, headers, line)
        if not valid_line:
            continue
        # cast the values to the correct typing
        keyword_store = {x: correct_datatypes(y, property_map[x][1]) for x, y in keyword_store.items()}

        # generate an object using the properties stored in the keyword dict
        # Use the map to create a kwargs dict for passing to the object
        keyword_store = {keyword_map[x]: y for x, y in keyword_store.items()}
        new_object = row_object(keyword_store)
        setattr(new_object, 'date', current_date)
        setattr(new_object, 'unit_system', unit_system)
        list_of_objects.append(new_object)
    return list_of_objects


def collect_all_tables_to_objects(nexus_file: NexusFile, row_object: Any, table_names_list: list[str],
                                  start_date: Optional[str],
                                  default_units: Optional[UnitSystem], ) -> Sequence[Any]:
    """ Loads all tables from a given file.

        Args:
            nexus_file (NexusFile): NexusFile representation of the file.
            row_object (Type(Storage_Object)): object type to store the data from each row into
            start_date (str): Starting date of the run
            default_units (UnitSystem): Units used in case not specified by file.
            table_names_list (list[str]): list of possible table header names
        Raises:
            TypeError: if the unit system found in the property check is not a valid enum UnitSystem
        Returns:
            Sequence[Storage_Object]: a list of arbitrary objects populated with properties from the file provided
        """
    current_date = start_date
    nexus_object_list: list[Any] = []
    file_as_list = nexus_file.get_flat_list_str_file()
    property_map = row_object.get_nexus_mapping()
    table_start = -1
    table_end = -1
    property_dict: dict = {}
    for index, line in enumerate(file_as_list):
        # check for changes in unit system
        check_property_in_line(line, property_dict, file_as_list)
        unit_system = property_dict.get('UNIT_SYSTEM', default_units)
        if not isinstance(unit_system, UnitSystem):
            raise TypeError(f"Value found for {unit_system=} of type {type(unit_system)} \
                                not compatible, expected type UnitSystem Enum")
        if check_token('TIME', line):
            current_date = get_expected_token_value(
                token='TIME', token_line=line, file_list=file_as_list,
                custom_message=f"Cannot find the date associated with the TIME card in {line=} at line number {index}")

        if any([check_token(x, line) for x in table_names_list]):
            table_start = index + 1
        if table_start > 0 and any([check_token('END' + x, line) for x in table_names_list]):
            table_end = index
        if 0 < table_start < table_end:
            list_objects = load_table_to_objects(file_as_list=file_as_list[table_start:table_end],
                                                 row_object=row_object,
                                                 property_map=property_map, current_date=current_date,
                                                 unit_system=unit_system)
            nexus_object_list.extend(list_objects)
            # reset indices for further tables
            table_start = -1
            table_end = -1
    return nexus_object_list


def correct_datatypes(value: None | int | float | str, dtype: type,
                      na_to_none: bool = True) -> None | int | str | float:
    """ takes a value and returns the value but converted to specified type. if na_to_none True then

    Args:
        value (None | int | float | str): value to convert
        dtype (type): one of (int, float, str)
        na_to_none (bool): if True NA strings are sent to None

    Returns:
        None | int | str | float: value but cast to the requested type
    """
    if value is None:
        return None
    check_value = value
    if isinstance(value, str):
        check_value = value.upper()
    match check_value:
        case 'NA':
            if na_to_none:
                return None
            else:
                return value
        case '#':
            return None
        case 'NONE':
            return None
        case _:
            return dtype(value)
