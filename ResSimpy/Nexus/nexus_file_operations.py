from datetime import datetime
from typing import Dict, Optional, Union

from ResSimpy.Nexus.DataModels.StructuredGridFile import VariableEntry
from string import Template


def check_token(token: str, line: str) -> bool:
    """ Checks if the text line contains the supplied token
    Args:
        token (str): keyword value to search the line for
        line (str): string to search the token in
    Returns:
        bool: boolean with whether the text line contains the supplied token
    """    
    line_start_chars = ["", '\t', "\n"]
    token_end_chars = [" ", '\n', '\t']
    token_location = line.find(token)

    if token_location == -1:
        return False

    if token_location + len(token) == len(line):
        return True

    if line[token_location + len(token)] not in token_end_chars:
        return False

    if token_location == 0 or line[token_location - 1] in line_start_chars:
        return True
    return False


def get_next_value(start_line_index: int, file_as_list: list[str], search_string: str, ignore_values: Optional[list[str]] = None,
                   replace_with: Union[str, VariableEntry, None] = None) -> Optional[str]:
    """Gets the next non blank value in a list of lines

    Args:
        start_line_index (int): line number to start reading file_as_list from
        file_as_list (list[str]):  a list of strings containing each line of the file as a new entry
        search_string (str): string to search from within the first indexed line
        ignore_values (Optional[list[str]], optional): a list of values that should be ignored if found. Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional): a value to replace the existing value with. Defaults to None.

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
                search_string = file_as_list[start_line_index]
                break
            elif character not in invalid_characters:
                value_string = search_string[character_location: len(search_string)]
                for value_character in value_string:
                    # If we've formed a string we're supposed to ignore, ignore it and get the next value
                    if ignore_values is not None and value in ignore_values:
                        search_string = search_string[character_location: len(search_string)]
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
                        new_line = original_line

                        if isinstance(replace_with, str):
                            new_value = replace_with
                        else:
                            new_value = replace_with.value

                            if replace_with.modifier != 'VALUE':
                                new_line = new_line.replace('INCLUDE ', '')
                            elif 'INCLUDE' not in original_line:
                                new_value = 'INCLUDE ' + replace_with.value

                            # If we are replacing the first value from a mult, remove the space as well
                            if replace_with.modifier == 'MULT' and replace_with.value == '':
                                value += ' '

                        new_line = new_line.replace(value, new_value, 1)
                        file_as_list[start_line_index] = new_line

                    break

            character_location += 1

            if new_search_string is True:
                break

    return value


def get_token_value(token: str, token_line: str, file_list: list[str], ignore_values: Optional[list[str]] = None,
                    replace_with: Union[str, VariableEntry, None] = None) -> Optional[str]:
    """Gets the value following a token if supplied with a line containing the token.

    arguments:
        token (str): the token being searched for.
        token_line (str): string value of the line that the token was found in.
        file_list (list[str]): a list of strings containing each line of the file as a new entry
        ignore_values (list[str], optional): a list of values that should be ignored if found. Defaults to None.
        replace_with (Union[str, VariableEntry, None], optional):  a value to replace the existing value with. Defaults to None.

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

    value = get_next_value(line_index, file_list, search_string, ignore_values, replace_with)
    return value


def get_times(times_file: list[str]) -> list[str]:
    """Retrieves a list of TIMES from the supplied Runcontrol / Include file

    Args:
        times_file (list[str]): list of strings with each line from the file a new entry in the list

    Returns:
        list[str]: list of all the values following the TIME keyword in supplied file
    """    
    times = []
    for line in times_file:
        if check_token('TIME', line):
            value = get_token_value('TIME', line, times_file)
            if value is not None:
                times.append(value)

    return times


def delete_times(file_content: list[str]) -> list[str]:
    """ Deletes times from file contents
    Args:
        file_content (list[str]):  list of strings with each line from the file a new entry in the list

    Returns:
        list[str]: the modified file without any TIME cards in
    """
    new_file = []
    previous_line_is_time = False
    for line in file_content:
        if "TIME " not in line and (previous_line_is_time is False or line != '\n'):
            new_file.append(line)
            previous_line_is_time = False
        elif "TIME " in line:
            previous_line_is_time = True
        else:
            previous_line_is_time = False
    return new_file


def load_file_as_list(file_path: str) -> list[str]:
    """ Reads the text file into a variable
    Args:
        file_path: (str): string containing a path pointing towards a text file
    
    Returns:
        list[str]: list of strings with each line from the file a new entry in the list
    
     """
    with open(file_path, 'r') as f:
        file_content = list(f)

    return file_content


def load_token_value_if_present(token: str, modifier: str, token_property: VariableEntry, 
        line: str, file_as_list: list[str], ignore_values: Optional[list[str]]=None) -> None:
    """Gets a token's value if there is one and loads it into the token_property

    Args:
        token (str): the token being searched for.
        modifier (str): any modifiers applied to the token
        token_property (VariableEntry): VariableEntry object to store the modifier and value pair into
        line (str): line to search for the token in 
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        ignore_values (Optional[list[str]], optional): values to be ignored. Defaults to None.
    
    Returns:
        None: stores the value into token_property supplied instead
    """    

    if ignore_values is None:
        ignore_values = []
    token_modifier = f"{token} {modifier}"

    if token_modifier in line:
        # If we are loading a multiple, load the two relevant values, otherwise just the next value
        if modifier == 'MULT':
            numerical_value = get_token_value(token_modifier, line, file_as_list,
                                              ignore_values=[])
            value_to_multiply = get_token_value(token_modifier, line, file_as_list,
                                                ignore_values=[numerical_value])
            if numerical_value is not None and value_to_multiply is not None:
                token_property.modifier = 'MULT'
                token_property.value = f"{numerical_value} {value_to_multiply}"
        else:
            value = get_token_value(token_modifier, line, file_as_list,
                                    ignore_values=ignore_values)
            if value is not None:
                token_property.value = value
                token_property.modifier = modifier


def get_simulation_time(line):
    value_found = False
    value = ''
    line_string = line
    while value_found is False:
        next_value = get_next_value(0, [line_string], line_string)
        if next_value == 'on':
            line_string = line_string.replace(next_value, '', 1)
            next_value = get_next_value(0, [line_string], line_string)

            for c in range(6):
                line_string = line_string.replace(next_value, '', 1)
                next_value = get_next_value(0, [line_string], line_string)
                value += next_value + (' ' if c < 5 else '')
            value_found = True
        line_string = line_string.replace(next_value, '', 1)
    return value


def replace_value(file, old_property, new_property, string_name):
    """ Replace the value and token + modifier with the new values """
    for line in file:
        old_token_modifier = f"{string_name} {old_property.modifier}"
        new_token_modifier = f"{string_name} {new_property.modifier}"
        ignore_values = ['INCLUDE'] if old_property.modifier == 'VALUE' else []
        if old_token_modifier in line:
            # If we are replacing a mult, replace the first value with a blank
            if old_property.modifier == 'MULT':
                dummy_value = VariableEntry('MULT', '')
                get_token_value(old_token_modifier, line, file, ignore_values=ignore_values,
                                replace_with=dummy_value)

            get_token_value(old_token_modifier, line, file, ignore_values=ignore_values,
                            replace_with=new_property)

            new_line = line.replace(old_token_modifier, new_token_modifier, 1)
            line_index = file.index(line)
            file[line_index] = new_line


def clean_up_string(value: str):
    """ Removes unwanted characters from a string """
    value = value.replace("\n", "")
    value = value.replace("!", "")
    value = value.replace("\t", "")
    return value


def convert_server_date(original_date):
    """Convert a date read in from Nexus to a strptime object"""
    date_format = '%a %b %d %X %Z %Y'
    converted_date = original_date

    # Convert CDT and CST timezones as Python doesn't work with CDT for some reason
    if 'CDT' in original_date:
        converted_date = converted_date.replace('CDT', '-0500', 1)
        date_format = '%a %b %d %X %z %Y'
    elif 'CST' in original_date:
        converted_date = converted_date.replace('CST', '-0600', 1)
        date_format = '%a %b %d %X %z %Y'

    return datetime.strptime(converted_date, date_format)


def get_errors_warnings_string(log_file_line_list):
    """ Retrieves the number of warnings and errors from the simulation log output, and formats them as a string """
    error_warning = ""
    for line in log_file_line_list:
        line = line.lower()
        if "errors" in line and "warnings" in line:
            error_warning = line

    error_warning_list = [x for x in error_warning.split(" ") if x != ""]

    error_warning_list = [clean_up_string(x) for x in error_warning_list]

    if len(error_warning_list) < 4:
        return None

    errors = error_warning_list[1]
    warnings = error_warning_list[3]

    error_warning_str = f"Simulation complete - Errors: {errors} and Warnings: {warnings}"
    return error_warning_str


def create_templated_file(template_location: str, substitutions: dict, output_file_name: str):
    """Creates a new text file at the requested destination substituting the supplied values."""

    class NewTemplate(Template):
        delimiter = '**!'

    with open(template_location) as template_file:
        template = NewTemplate(template_file.read())

    output_file = template.substitute(substitutions)

    # Create the output file
    with open(output_file_name, 'w') as new_file:
        new_file.write(output_file)


def get_relperm_combined_fluid_column_heading(table_heading: str) -> str:
    """Returns the combined fluid heading for a Nexus Relperm table"""
    if table_heading == 'WOTABLE':
        column_heading = 'KROW'
    elif table_heading == 'GOTABLE':
        column_heading = 'KROG'
    else:
        column_heading = 'KRWG'

    return column_heading


def get_relperm_single_fluid_column_heading(table_heading: str) -> str:
    """Returns the single fluid heading for a Nexus Relperm table"""
    if table_heading == 'GOTABLE':
        column_heading = 'KRG'
    else:
        column_heading = 'KRW'

    return column_heading


def get_relperm_base_saturation_column_heading(table_heading: str) -> str:
    """Returns the column heading for the base saturation column"""
    if table_heading == 'GOTABLE':
        column_heading = 'SG'
    else:
        column_heading = 'SW'

    return column_heading


def load_nexus_relperm_table(relperm_file_path: str) -> dict[str, list[tuple[float, float]]]:
    """ Loads in a Nexus relperm table and returns a dictionary with two lists, one with the relperm values for the
    single fluid, and the other with the values for combined fluids """
    file_as_list = load_file_as_list(relperm_file_path)

    # Find the column headings line (assume it is the first non-commented out line after the table heading)
    possible_table_headings = ['GWTABLE', 'WOTABLE', 'GOTABLE']
    header_index = None
    table_heading = None

    for index, line in enumerate(file_as_list):
        first_value_in_line = get_next_value(0, [line], line)
        if first_value_in_line in possible_table_headings:
            table_heading = first_value_in_line
            header_index = index + 1
            break

    if header_index is None or table_heading is None:
        raise ValueError("Cannot find the header for this relperm table")

    # Read in the header line to get the column order
    header_line = file_as_list[header_index]
    columns: list[str] = []

    next_column_heading = get_next_value(0, [header_line], header_line)
    next_line = header_line
    while next_column_heading is not None:
        columns.append(next_column_heading)
        next_line = next_line.replace(next_column_heading, "", 1)
        next_column_heading = get_next_value(0, [next_line], next_line)

    # Load in each row from the table
    all_values: list[Optional[Dict[str, str]]] = []

    for line in file_as_list[header_index + 1:]:
        trimmed_line = line
        line_values: Optional[Dict[str, str]] = {}
        for column in columns:
            value = get_next_value(0, [trimmed_line], trimmed_line)

            # If we hit a comment or blank line, assume that we've reached the end of our table
            if value is None:
                line_values = None
                break

            trimmed_line = trimmed_line.replace(value, "", 1)

            if line_values is not None:
                line_values[column] = value
        if line_values is not None:
            all_values.append(line_values)
        elif len(all_values) > 0:
            # We've reached the end of the table, finish reading the lines now
            break

    # Retrieve the water and gas values, and return them
    single_fluid_relperms = []  # E.g. Water
    combined_fluid_relperms = []  # E.g. Water-Oil

    single_fluid_column_heading = get_relperm_single_fluid_column_heading(table_heading)
    combined_fluid_column_heading = get_relperm_combined_fluid_column_heading(table_heading)
    base_saturation_heading = get_relperm_base_saturation_column_heading(table_heading)

    for index, row in enumerate(all_values):
        if row is None:
            continue
        single_fluid_relperms.append((float(row[base_saturation_heading]), float(row[single_fluid_column_heading])))
        combined_fluid_relperms.append((float(row[base_saturation_heading]), float(row[combined_fluid_column_heading])))

    return {'single_fluid': single_fluid_relperms, 'combined_fluids': combined_fluid_relperms}
