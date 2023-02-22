from io import StringIO
from typing import Optional, Union
import pandas as pd
from ResSimpy.Nexus.DataModels.StructuredGridFile import VariableEntry
from string import Template
import re
from ResSimpy.Nexus.nexus_constants import VALID_NEXUS_KEYWORDS
import os


def nexus_token_found(line_to_check: str) -> bool:
    """
    Checks if a valid Nexus token has been found  in the supplied line

    Args:
        line_to_check (str):  The string to search for a Nexus keyword

    Returns:
        token_found (bool): A boolean value stating whether the token is found or not

    """
    uppercase_line = line_to_check.upper()
    for token in VALID_NEXUS_KEYWORDS:
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


def get_next_value(start_line_index: int, file_as_list: list[str], search_string: str,
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
    value = ""
    while value_found is False:
        character_location = 0
        new_search_string = False
        for character in search_string:
            # move lines once we hit a comment character or new line or are at the end of the search string
            if character == "!" or character == "\n" or \
                    (character_location != 0 and character_location == len(search_string) - 1):
                start_line_index += 1
                # If we've reached the end of the file, return None
                if start_line_index >= len(file_as_list):
                    return None
                # Move to the next line down in file_as_list
                temp_search_string = file_as_list[start_line_index]
                if not isinstance(temp_search_string, str):
                    raise ValueError(f'No valid value found, hit INCLUDE statement instead on line number \
                        {start_line_index}')
                search_string = temp_search_string
                break
            elif character not in invalid_characters:
                value_string = search_string[character_location: len(
                    search_string)]
                for value_character in value_string:
                    # If we've formed a string we're supposed to ignore, ignore it and get the next value
                    if ignore_values is not None and value in ignore_values:
                        search_string = search_string[character_location: len(
                            search_string)]
                        new_search_string = True
                        value = ""
                        break
                    # stop adding to the value once we hit an invalid_character
                    if value_character in invalid_characters:
                        break
                    value += value_character
                    character_location += 1

                if value != "":
                    value_found = True
                    # Replace the original value with the new requested value
                    if replace_with is not None:
                        original_line = file_as_list[start_line_index]
                        if not isinstance(original_line, str):
                            raise ValueError(f'No valid value found, hit INCLUDE statement instead on line number \
                                             {start_line_index}')
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
                        file_as_list[start_line_index] = new_line

                    break

            character_location += 1

            if new_search_string is True:
                break

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
        The value following the supplied token, if it is present.
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
    value = get_next_value(line_index, file_list,
                           search_string, ignore_values, replace_with)
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
        file_content = strip_file_of_comments(
            file_content, strip_str=strip_str)

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
            inc_file_path = get_token_value('INCLUDE', line, [line])
            if inc_file_path is None:
                raise ValueError(
                    f"No value found after INCLUDE keyword in {line}")
            inc_data = load_file_as_list(
                inc_file_path, strip_comments=True, strip_str=True)
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
            expanded_file += old_file_contents[i+1::]
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
        return_path = os.path.join(os.path.dirname(origin), file_path)
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
        df = pd.read_csv(StringIO('\n'.join(cleaned_file_as_list)+'\n'), sep=r'\s+', skip_blank_lines=False)
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
