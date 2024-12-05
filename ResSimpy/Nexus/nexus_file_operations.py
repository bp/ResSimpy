"""A collection of Utility functions for handling parsing Nexus files."""
from __future__ import annotations

import os
import re
from enum import Enum
from io import StringIO
from string import Template
from typing import Optional, Union, Any
import fnmatch

import numpy as np
import pandas as pd

from ResSimpy.Enums.UnitsEnum import UnitSystem, TemperatureUnits, SUnits
from ResSimpy.FileOperations.file_operations import get_next_value, check_token, get_expected_token_value, \
    strip_file_of_comments, load_file_as_list
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusKeywords.nexus_keywords import VALID_NEXUS_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS


def nexus_token_found(line_to_check: str, valid_list: list[str] = VALID_NEXUS_KEYWORDS) -> bool:
    """Checks if a valid Nexus token has been found  in the supplied line.

    Args:
        line_to_check (str):  The string to search for a Nexus keyword
        valid_list (list[str]): list of keywords to search from (e.g. from nexus_constants)

    Returns:
        token_found (bool): A boolean value stating whether the token is found or not

    """
    valid_set = set(valid_list)
    uppercase_line = line_to_check.upper()
    strip_comments = strip_file_of_comments([uppercase_line], square_bracket_comments=True)
    if len(strip_comments) == 0:
        return False
    split_line = set(strip_comments[0].split())

    return not valid_set.isdisjoint(split_line)


def get_previous_value(file_as_list: list[str], search_before: Optional[str] = None,
                       ignore_values: Optional[list[str]] = None) -> Optional[str]:
    """Gets the previous non-blank value in a list of lines.

    Starts from the last instance of search_before, working backwards.

    Args:
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry,
        ending with the line to start searching from.
        search_before (Optional[str]): The string to start the search from in a backwards direction
        ignore_values (Optional[list[str]], optional): a list of values that should be ignored if found. \
                    Defaults to None.

    Returns:
        Optional[str]: Next non-blank value from the list, if none found returns None
    """

    # Reverse the order of the lines
    file_as_list.reverse()

    # If we are searching before a specific token, remove that and the rest of the line.
    if search_before is not None:
        search_before_location = file_as_list[0].upper().rfind(search_before)
        file_as_list[0] = file_as_list[0][0: search_before_location]

    previous_value: str = ''
    first_line = True
    for line in file_as_list:
        string_to_search: str = line
        # Retrieve all of the values in the line, then return the last one found if one is found.
        # Otherwise search the next line
        next_value = get_next_value(0, [string_to_search], ignore_values=ignore_values)

        while next_value is not None and (search_before != next_value or not first_line):
            previous_value = next_value
            string_to_search = string_to_search.replace(next_value, '')
            next_value = get_next_value(0, [string_to_search], ignore_values=ignore_values)

        if previous_value != '':
            return previous_value

        # If we are not on the first line, we can search the whole line
        first_line = False

    # Start of file reached, no values found
    return None


def create_templated_file(template_location: str, substitutions: dict, output_file_name: str) -> None:
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
    """Expands out include files. If recursive set to True will expand all include_locations including nested.

    Args:
        file_as_list (list[str]): a list of strings containing each line of the file as a new entry
        recursive (bool): If recursive set to True will expand all include_locations including nested include_locations

    Raises:
        ValueError: if no value found after INCLUDE keyword in file

    Returns:
        list[str]: list of strings containing each line of the file as a new entry but with files following \
            include_locations expanded out
    """
    no_comment_file = strip_file_of_comments(file_as_list, strip_str=True, square_bracket_comments=True)

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


def get_full_file_path(file_path: str, origin: str) -> str:
    """Returns the full file path including the base directories if they aren't present in the string.

    Args:
        file_path (str): the initial file path found in a file
        origin (str): the initial origin of the file
    """
    if os.path.isabs(file_path):
        return_path = file_path
    else:
        return_path = os.path.join(os.path.dirname(origin), file_path)
    return return_path


def read_table_to_df(file_as_list: list[str], keep_comments: bool = False, noheader: bool = False) -> pd.DataFrame:
    """From a list of strings that represents a table, generate a Pandas dataframe representation of the table.

    Args:
        file_as_list (list[str]): List of strings representing a single table to be read
        keep_comments (bool): Boolean to determine if we keep comments as a separate column or not
        noheader (bool): Boolean signaling if the input has a header or not

    Returns:
        pd.DataFrame: Created Pandas DataFrame representation of table to be read
    """
    df = pd.DataFrame()
    header: Union[str, None] = 'infer'
    if noheader:
        header = None
    if not keep_comments:
        # Clean of comments
        cleaned_file_as_list = strip_file_of_comments(file_as_list, strip_str=True, square_bracket_comments=True)
        # Create dataframe
        df = pd.read_csv(StringIO('\n'.join(cleaned_file_as_list)), sep=r'\s+', header=header)
        if header is not None:
            df.columns = [col.upper() for col in df.columns if isinstance(col, str)]
    else:  # Going to retain comments as a separate column in dataframe
        # Clean of comments
        cleaned_file_as_list = [re.split(r'(?<!\")!(?!\")', line)[0].strip() if line and line[0] != '!' else line
                                for line in file_as_list]
        cleaned_file_as_list = [line if not line.startswith('!') else '' for line in cleaned_file_as_list]
        # Save comments in a list
        comment_column = [line.split('!', 1)[1].strip() if '!' in line else None for line in file_as_list]
        # Create dataframe
        df = pd.read_csv(StringIO('\n'.join(cleaned_file_as_list) + '\n'), sep=r'\s+', skip_blank_lines=False,
                         header=header)
        if header is not None:
            df.columns = [col.upper() for col in df.columns if isinstance(col, str)]
        if any(x is not None for x in comment_column):  # If comment column isn't a full column of Nones
            df['COMMENT'] = comment_column[1:]
        df = df.convert_dtypes().dropna(axis=0, how='all').reset_index(drop=True)
    return df


def clean_up_string(value: str) -> str:
    r"""Removes unwanted characters from a string.

        unwanted characters: ("\\n", "\\t", "!").

    Args:
        value (str): string to clean up
    Returns:
        str: string with unwanted characters removed.
    """
    value = value.replace("\n", "")
    value = value.replace("!", "")
    value = value.replace("\t", "")
    return value


def check_for_and_populate_common_input_data(
        file_as_list: list[str],
        property_dict: dict[
        str, Union[str, int, float, Enum, list[
        str], np.ndarray, pd.DataFrame,
        dict[
        str, Union[float, pd.DataFrame]]]]) -> None:
    """Loop through lines of Nexus input file content looking for common input data.

    e.g., units such as ENGLISH or METRIC, temperature units such as FAHR or CELSIUS, DATEFORMAT, etc.,
    as defined in Nexus manual. If any found, include in provided property_dict and return.

    Args:
        file_as_list (list[str]): Nexus input file content
        property_dict (dict): Dictionary in which to include common input data if found

    Returns:
        dict: Dictionary including found common input data
    """
    for line in file_as_list:
        # Check for description
        check_property_in_line(line, property_dict, file_as_list)


def check_property_in_line(
        line: str,
        property_dict: dict[
        str, Union[str, int, float, Enum, list[
        str], np.ndarray, pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]], file_as_list: list[str]) -> None:
    """Given a line of Nexus input file content looking for common input data.

    e.g., units such as ENGLISH or METRIC, temperature units such as FAHR or CELSIUS, DATEFORMAT, etc.,
    as defined in Nexus manual. If any found, include in provided property_dict and return.

    Args:
    line (str): line to search for the common input data
    file_as_list (list[str]): Nexus input file content
    property_dict (dict): Dictionary in which to include common input data if found

    Returns:
    dict: Dictionary including found common input data
    """
    if check_token('DESC', line):
        if 'DESC' in property_dict.keys():
            if isinstance(property_dict['DESC'], list):
                property_dict['DESC'].append(line.split('DESC')[1].strip())
        else:
            property_dict['DESC'] = [line.split('DESC')[1].strip()]
    # Check for label
    if check_token('LABEL', line):
        property_dict['LABEL'] = get_expected_token_value('LABEL', line, file_as_list,
                                                          custom_message='Invalid file: LABEL value not provided')
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
    if check_token('METRIC', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.METRIC
    if check_token('METKG/CM2', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.METKGCM2
    if check_token('METBAR', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.METBAR
    if check_token('LAB', line):
        property_dict['UNIT_SYSTEM'] = UnitSystem.LAB
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


def looks_like_grid_array(file_path: str, lines2check: int = 10) -> bool:
    """Returns true if a Nexus include file begins with one of the Nexus grid array keywords.

    Args:
        file_path (str): Path to Nexus include file
        lines2check (int): First number of lines in file to check, looking for
        a Nexus grid array keyword. Default: first 10 lines of file

    Returns:
        bool: True if file begins with one of Nexus grid array keywords
    """
    with open(file_path, 'r') as f:

        for i in range(lines2check):
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
    """Gets the table headers for a given line in a file.

    Args:
        file_as_list (list[str]): file represented as a list of strings
        header_values (dict[str, str]): dictionary of column headings to populate from the table
    Raises:
        ValueError: if no headers belonging to the header_values dict is found
    Returns:
        int, list[str]: index in the file provided for the header, list of headers as Nexus keyword format.
    """
    headers = []
    header_index = -1
    for index, line in enumerate(file_as_list):
        for key in header_values:
            if check_token(key, line):
                header_line = line.upper()
                header_index = index
                # Map the headers
                next_column_heading = get_next_value(start_line_index=0, file_as_list=[header_line])
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
    """Reads in a line from a nexus table with a given set of headers and populates each of those values into a \
    corresponding dictionary.

    Args:
        keyword_store (dict[str, None | int | float | str]): place to store the value from the given column
        headers (list[str]): list of headers to read values into
        line (str): line to read the data from.

    Returns:
        tuple[bool, dict[str, None | int | float | str]]: a dictionary with the found set of objects and lines
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
                          date_format: DateFormat, current_date: Optional[str] = None,
                          unit_system: Optional[UnitSystem] = None,
                          constraint_obj_dict: Optional[dict[str, list[Any]]] = None,
                          preserve_previous_object_attributes: bool = False,
                          well_names: Optional[list[str]] = None,
                          welllists: Optional[list[NexusWellList]] = None,
                          start_date: Optional[str] = None) -> list[tuple[Any, int]]:
    """Loads a table row by row to an object provided in the row_object.

    Args:
        file_as_list (list[str]): file represented as a list of strings.
        row_object (Any): class to populate, should take a dictionary of attributes as an argument to the __init__
        property_map (dict[str, tuple[str, type]]): map of the Nexus keywords as keys to the dictionary and the names\
            of the object attribute and the type of that attribute as a tuple in the values.
            e.g. {'NAME': ('name', str)} for the object obj with attribute obj.name
        current_date (Optional[str]): date/time at which the object was found within a recurrent file
        unit_system (Optional[UnitSystem): most recent UnitSystem enum of the file where the object was found
        constraint_obj_dict (Optional[dict[str, list[Any]]]): list of objects to append to. \
            If None creates an empty list to populate.
        preserve_previous_object_attributes (bool): If True the code will find the latest object with a matching name\
            attribute and will update the object to reflect the latest additional attributes and overriding all \
            matching attributes. Must have a .update() method implemented and a name
        date_format (Optional[DateFormat]): The date format of the object.
        well_names (Optional[str]): A list of all the network object names.
        welllists (Optional[list[WellList]]): A list of all the WELLLISTs loaded in so far.
        start_date (Optional[str]): The start date of the simulation.

    Returns:
        list[obj]: list of tuples containing instances of the class provided for the row_object,
        populated with attributes from the property map dictionary and the line index where it was found
    """
    keyword_map = {x: y[0] for x, y in property_map.items()}
    header_index, headers = get_table_header(file_as_list, keyword_map)
    table_as_list = file_as_list[header_index + 1::]
    if constraint_obj_dict is None:
        constraint_obj_dict = {}

    return_objects = []
    welllist_names = [] if welllists is None else [x.name for x in welllists]
    for index, line in enumerate(table_as_list, start=header_index + 1):
        keyword_store: dict[str, None | int | float | str] = {x: None for x in property_map.keys()}
        valid_line, keyword_store = table_line_reader(keyword_store, headers, line)
        if not valid_line:
            continue
        # cast the values to the correct typing
        keyword_store = {x: correct_datatypes(y, property_map[x][1]) for x, y in keyword_store.items()}

        # generate an object using the properties stored in the keyword dict
        # Use the map to create a kwargs dict for passing to the object
        keyword_store = {keyword_map[x]: y for x, y in keyword_store.items()}
        row_name = keyword_store.get('name', None)
        if row_name is None:
            # if there is no name try and get it from the well_name instead and align well_name and name
            row_name = keyword_store.get('well_name', None)
            keyword_store['name'] = row_name

        if row_name is None:
            row_name = keyword_store.get('connection', None)
            keyword_store['name'] = row_name

        if not isinstance(keyword_store['name'], str):
            raise ValueError(f'Cannot find valid well name for object: {keyword_store}')

        constraining_object_name = keyword_store['name']

        if constraining_object_name.__contains__('*') and well_names is not None:
            # Wildcard found, apply these properties to all objects with a name that matches the name predicate.
            object_well_names = [x for x in well_names if fnmatch.fnmatch(x, constraining_object_name)]
        elif constraining_object_name in welllist_names and welllists is not None:
            # If the name refers to a welllist, apply the constraints to all of the wells in that.
            welllist_for_constraining = next(x for x in welllists if x.name == constraining_object_name)
            wellnames_in_welllist = welllist_for_constraining.wells
            object_well_names = wellnames_in_welllist
        else:
            object_well_names = [constraining_object_name]

        for name in object_well_names:
            keyword_store['name'] = name

            if preserve_previous_object_attributes:
                all_matching_existing_constraints = constraint_obj_dict.get(name, None)
                if all_matching_existing_constraints is not None:
                    # use the previous object to update this
                    existing_constraint = all_matching_existing_constraints[-1]
                    new_object_date = getattr(existing_constraint, 'date', None)
                    if new_object_date is not None and new_object_date == current_date:
                        # otherwise just update the object inplace and don't add it to the return list
                        existing_constraint.update(keyword_store)
                        # add just the id back in to track the lines where it came from in the file
                        return_objects.append((existing_constraint.id, index))
                        continue
                    else:
                        new_object = row_object(properties_dict=keyword_store, date=current_date,
                                                unit_system=unit_system, date_format=date_format,
                                                start_date=start_date)
                else:
                    new_object = row_object(properties_dict=keyword_store, date=current_date, unit_system=unit_system,
                                            date_format=date_format, start_date=start_date)
            else:
                new_object = row_object(properties_dict=keyword_store, date=current_date, unit_system=unit_system,
                                        date_format=date_format, start_date=start_date)

            # If we are creating a PIPEGRAD connection of some kind, set hyd_method to None for now, as this column has
            # a different meaning in the Nexus format for such connections.
            if isinstance(new_object, NexusWellConnection) or isinstance(new_object, NexusNodeConnection):
                if new_object.con_type == 'PIPEGRAD':
                    new_object.hyd_method = None

            return_objects.append((new_object, index))
    return return_objects


def check_list_tokens(list_tokens: list[str], line: str) -> Optional[str]:
    """Checks a list of tokens for whether it exists in a string and returns the token that matched.

    Args:
        list_tokens (list[str]): list of tokens to search for within the line
        line (str): line to search for tokens

    Returns:
        Optional[str]: returns the token which was found otherwise returns None.

    """
    for x in list_tokens:
        token_found = check_token(x, line)
        if token_found:
            return x
    return None


def correct_datatypes(value: None | float | str, dtype: type,
                      na_to_none: bool = True) -> None | str | float:
    """Takes a value and returns the value but converted to specified type.

    If na_to_none True then will reduce a lot of values to none.

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
        case 'OFF':
            if dtype is str:
                return 'OFF'
            else:
                return None
        case _:
            return dtype(value)


def split_line(line: str, upper: bool = True) -> list[str]:
    """Splits a line into a list of strings through sequential application of get_next_value.
    Does not include comments. A line with no valid tokens will return an empty list.
    """
    stored_values: list[str] = []
    value = get_next_value(0, [line])
    if value is None:
        return stored_values
    trimmed_line = line
    while value is not None:
        if upper:
            stored_values.append(value.upper())
        else:
            stored_values.append(value)
        trimmed_line = trimmed_line.replace(value, "", 1)
        value = get_next_value(0, [trimmed_line])

    return stored_values
