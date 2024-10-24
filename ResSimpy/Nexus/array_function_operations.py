"""A collection of functions for handling grid functions from Nexus."""
from __future__ import annotations
import ResSimpy.Nexus.nexus_file_operations as nfo
import pandas as pd
from typing import Optional, Union
import warnings

from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS, STRUCTURED_GRID_KEYWORDS


def collect_all_function_blocks(file_as_list: list[str]) -> list[list[str]]:
    """Collects all the function blocks within a grid file.

    Args:
    file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,

    Returns:
    list[list[str]]: list of function block lines as a list of strings.
    """
    function_list = []
    function_body: list[str] = []
    reading_function = False
    look_for_table_end = False
    analyt_flag = False  # boolean to determine if specific function is of analytical or tabular form

    for i, line in enumerate(file_as_list):
        if nfo.check_token('FUNCTION', line):
            function_body = []
            reading_function = True
            analyt_flag = False
            look_for_table_end = False
        if reading_function:
            # remove all comments following the first '!' in a line.
            if nfo.check_token('ANALYT', line):
                analyt_flag = True
            modified_line = line.split('!', 1)[0]
            function_body.append(modified_line.strip())
            if analyt_flag:
                if nfo.check_token('OUTPUT', modified_line) and not nfo.check_token('RANGE', modified_line):
                    function_list.append(function_body)
                    reading_function = False
            else:  # tabular form
                if nfo.check_token('OUTPUT', modified_line) and not nfo.check_token('RANGE', modified_line):
                    look_for_table_end = True
                    continue
                if i < len(file_as_list) - 1 and look_for_table_end:
                    end_function = False
                    for keyword in STRUCTURED_GRID_KEYWORDS + GRID_ARRAY_KEYWORDS + ['INCLUDE']:
                        if nfo.check_token(keyword, file_as_list[i+1]):
                            end_function = True
                    if end_function:
                        function_list.append(function_body)
                        reading_function = False

    # remove null values
    function_list = [list(filter(None, x)) for x in function_list]

    return function_list


def create_function_parameters_df(function_list_to_parse: list[list[str]]) -> pd.DataFrame:
    """Creates a dataframe to hold all the function properties and parameters.

    Args:
        function_list_to_parse (list[list[str]]): list of functions extracted as list of lines.

    Returns:
        pandas.DataFrame: a dataframe holding each function's parameters in a row.
    """

    functions_df = pd.DataFrame(
        columns=['FUNCTION #', 'blocks [i1,i2,j1,j2,k1,k2]', 'region_type',
                 'region_numbers',
                 'func_type', 'func_coeff', 'grid', 'range_input', 'range_output', 'drange',
                 'input_arrays', 'output_arrays', 'i1', 'i2', 'j1', 'j2', 'k1', 'k2'])

    for b, block in enumerate(function_list_to_parse):

        # set the empty default values for the parameters,
        # so if they don't exist in dataframe they won't appear as NaN or give error,
        # or repeat the last value for each row.
        i1 = i2 = j1 = j2 = k1 = k2 = region_type = function_type = grid_name = ''
        # set the lists as empty strings as well, otherwise they show up as [] on the dataframe.
        region_number_list: Union[str, list[str], list[int]] = ''
        function_coefficients: Union[str, list[str], list[float]] = ''
        input_arrays_min_max_list: Union[str, list[str], list[float]] = ''
        output_arrays_min_max_list: Union[str, list[str], list[float]] = ''
        input_array_list: Union[str, list[str]] = ''
        output_array_list: Union[str, list[str]] = ''
        drange_list: Union[str, list[str]] = ''
        blocks_list: Union[str, list[str], list[int]] = ''

        for li, line in enumerate(block):
            modified_line = line.upper()
            words = modified_line.split()
            if nfo.check_token('BLOCKS', modified_line):
                i1 = words[1]
                i2 = words[2]
                j1 = words[3]
                j2 = words[4]
                k1 = words[5]
                k2 = words[6]
                blocks_list = words[1:7]
                blocks_list = [round(float(i)) for i in blocks_list]

            if nfo.check_token('FUNCTION', modified_line):
                if len(words) == 1:
                    continue
                if len(words) == 2:
                    if words[1] not in GRID_ARRAY_KEYWORDS:
                        warnings.warn(f'Function {b + 1}:  Function table entries will be excluded from summary df.')
                        function_type = 'function table'
                    else:
                        region_type = words[1]
                        region_number_list = block[li + 1].split()
                        try:
                            region_number_list = [round(float(i)) for i in region_number_list]
                        except ValueError:
                            warnings.warn(f'ValueError at function {b + 1}: could not convert string to integer.')

                if len(words) > 2:  # TODO: deal with tabular function option keywords
                    warnings.warn(f'Function {b + 1}:  Function table entries will be excluded from summary df.')
                    function_type = 'function table'
            if nfo.check_token('ANALYT', modified_line):
                function_type = words[1]
                if len(words) > 2:
                    # remove the first 2 words in line, and set the rest to coefficients
                    function_coefficients = words[2:]
                    # convert string coefficient values to numerical, if possible:
                    try:
                        function_coefficients = [float(i) for i in function_coefficients]
                    except ValueError:
                        warnings.warn(f'ValueError at function {b + 1}: could not convert string to float.')

            if nfo.check_token('GRID', modified_line):
                grid_name = words[1]
            if nfo.check_token('RANGE', modified_line) and nfo.check_token('INPUT', modified_line):
                input_arrays_min_max_list = words[2:]
                # convert string range_input values to numerical, if possible:
                try:
                    input_arrays_min_max_list = [float(i) for i in input_arrays_min_max_list]
                except ValueError:
                    warnings.warn(f'ValueError at function {b + 1}: could not convert string to float.')
            if nfo.check_token('RANGE', modified_line) and nfo.check_token('OUTPUT', modified_line):
                output_arrays_min_max_list = words[2:]
                # convert string range_input values to numerical, if possible:
                try:
                    output_arrays_min_max_list = [float(i) for i in output_arrays_min_max_list]
                except ValueError:
                    warnings.warn(f'ValueError at function {b + 1}: could not convert string to float.')
            if nfo.check_token('DRANGE', modified_line):
                warnings.warn(f'Function {b + 1}: Function table entries will be excluded from summary df.')
                drange_list = words[1:]
                function_type = 'function table'
            if nfo.check_token('OUTPUT', modified_line) and not nfo.check_token('RANGE', modified_line):
                input_array_list = words[:words.index('OUTPUT')]
                output_array_list = words[words.index('OUTPUT') + 1:]
        # Create the row that holds function data
        function_row = [b + 1, blocks_list, region_type, region_number_list, function_type,
                        function_coefficients,
                        grid_name, input_arrays_min_max_list, output_arrays_min_max_list, drange_list, input_array_list,
                        output_array_list, i1, i2, j1, j2, k1, k2]
        # Append the function row to the dataframe
        functions_df.loc[len(functions_df)] = function_row
    return functions_df


def summarize_model_functions(function_list_to_parse: list[list[str]]) -> pd.DataFrame:
    """Extracts all function parameters into a df, with an added column of human-readable notations for each function.

    Args:
        function_list_to_parse (list[list[str]]): list of functions extracted as list of lines.

    Returns:
        pandas.DataFrame: a dataframe holding each function's translation/summary in a row.
    """

    # get the df from create_function_parameters_df, add a new column, and populate based on ANALYT function type:

    function_summary_df = create_function_parameters_df(function_list_to_parse)
    function_summary_df['notation'] = ''

    for index, row in function_summary_df.iterrows():

        formula = row['output_arrays'][0] + ' = '

        match row['func_type'].upper():
            # ANALYT POLYN
            case 'POLYN':
                # get number of coefficients, n
                n = len(row['func_coeff'])

                # For each coefficient (c), calculate the corresponding exponent -or power (p)
                # Create polynomial function notation, term by term, for any number of coefficients (n)
                # using the first item in input arrays list (arr),
                # and the position (x) of the function term/portion we are creating.
                for x in range(n):
                    c = row['func_coeff'][x]
                    p = n - x - 1
                    arr = row['input_arrays'][0]

                    if n == 1:
                        f_portion = f'{c}'

                    if p == 0 and x > 0:
                        if c > 0:
                            f_portion = f' +{c}'
                        elif c < 0:
                            f_portion = f'{c}'
                        else:
                            continue

                    if p == 1 and x > 0:
                        if c > 0:
                            f_portion = f' +{c}*{arr}'
                        elif c < 0:
                            f_portion = f'{c}*{arr}'
                        else:
                            continue

                    if p == 1 and x == 0:
                        if c != 0:
                            f_portion = f'{c}*{arr}'
                        else:
                            continue

                    if p > 1 and x > 0:
                        if c > 0:
                            f_portion = f' +{c}*({arr}^{p})'
                        elif c < 0:
                            f_portion = f'{c}*({arr}^{p})'
                        else:
                            continue

                    if p > 1 and x == 0:
                        if c != 0:
                            f_portion = f'{c}*({arr}^{p})'
                        else:
                            continue

                    formula += f_portion

            # ANALYT ABS
            case 'ABS':
                formula += f"| {row['input_arrays'][0]} |"

            # ANALYT EXP
            case 'EXP':
                formula += f"e^{row['input_arrays'][0]}"

            # ANALYT EXP10
            case 'EXP10':
                formula += f"10^{row['input_arrays'][0]}"

            # ANALYT LOG
            case 'LOG':
                formula += f"ln|{row['input_arrays'][0]}|"

            # ANALYT LOG10
            case 'LOG10':
                formula += f"log10|{row['input_arrays'][0]}|"

            # ANALYT SQRT
            case 'SQRT':
                formula += f"SQRT|{row['input_arrays'][0]}|"

            # ANALYT GE
            case 'GE':
                formula += f"({row['input_arrays'][0]} if {row['input_arrays'][0]} >= {row['func_coeff'][0]}; " \
                           f"{row['func_coeff'][1]} otherwise)"

            # ANALYT LE
            case 'LE':
                formula += f"({row['input_arrays'][0]} if {row['input_arrays'][0]} <= {row['func_coeff'][0]}; " \
                           f"{row['func_coeff'][1]} otherwise)"

            # ANALYT ADD
            case 'ADD':
                formula += f"{row['input_arrays'][0]} + {row['input_arrays'][1]}"

            # ANALYT SUBT
            case 'SUBT':
                formula += f"{row['input_arrays'][0]} - {row['input_arrays'][1]}"

            # ANALYT DIV
            case 'DIV':
                formula += f"({row['input_arrays'][0]} / {row['input_arrays'][1]} if {row['input_arrays'][1]} != 0; " \
                           f"{row['input_arrays'][0]} otherwise)"

            # ANALYT MULT
            case 'MULT':
                formula += f"{row['input_arrays'][0]} * {row['input_arrays'][1]}"

            # ANALYT MIN
            case 'MIN':
                formula += f"min({row['input_arrays'][0]}, {row['input_arrays'][1]})"

            # ANALYT MAX
            case 'MAX':
                formula += f"max({row['input_arrays'][0]}, {row['input_arrays'][1]})"

        # fill in the notation value for the row
        function_summary_df.loc[index, 'notation'] = formula

    # move notation column to the beginning of table:
    second_column = function_summary_df.pop('notation')
    function_summary_df.insert(1, 'notation', second_column)

    # set FUNCTION number as the index colum:
    function_summary_df = function_summary_df.set_index('FUNCTION #')

    return function_summary_df


def create_grid_array_function_objects(array_functions_as_list: list[list[str]]) -> list[NexusGridArrayFunction]:
    """Function that creates a list of grid array function objects, from a list of functions as a list of strings \
    output from collect_all_function_blocks.

    Args:
        array_functions_as_list (list[list[str]]): List of function blocks, each represented as a list of strings

    Returns:
        list[NexusGridArrayFunction]: List of grid array function objects
    """
    store_array_functions: list[NexusGridArrayFunction] = []
    # Enumerate functions, with second argument specifying the index value from which the counter is to be started
    for function_number, array_function in enumerate(array_functions_as_list, 1):
        new_grid_array_function_obj = object_from_array_function_block(array_function, function_number)
        store_array_functions.append(new_grid_array_function_obj)
    return store_array_functions


def object_from_array_function_block(array_function: list[str], function_number: int) -> NexusGridArrayFunction:
    """Function to transform function attributes in a list, as output from collect_all_function_blocks, to a
    NexusGridArrayFunction object.

    Args:
        array_function (list[str]): List of function block lines as a list of strings
        function_number (int): function counter (order of function in Nexus grid inputs)

    Returns:
        NexusGridArrayFunction: _Object holding grid array function attributes, such as region type, blocks, etc.
    """
    region_type: Optional[str] = None
    region_number_list: Optional[list[int]] = None
    input_array_list: Optional[list[str]] = None
    output_array_list: Optional[list[str]] = None
    function_coefficients: Optional[list[float]] = None
    block_array: Optional[list[int]] = None
    grid_name: Optional[str] = None
    input_range_list: Optional[list[tuple[float, float]]] = None
    output_range_list: Optional[list[tuple[float, float]]] = None
    drange_list: Optional[list[float]] = None
    function_type_enum: Optional[GridFunctionTypeEnum] = None
    function_table: Optional[pd.DataFrame] = None
    function_table_m: Optional[int] = None
    function_table_p_list: Optional[list[float]] = None

    output_line_headers: list[str] = []
    for li, line in enumerate(array_function):
        modified_line = line.upper()
        words = modified_line.split()
        if nfo.check_token('FUNCTION', modified_line):
            if len(words) == 1:  # When FUNCTION is the only word in the line
                continue
            if len(words) == 2:  # When FUNCTION reg_type are the only words on the line
                if words[1] not in GRID_ARRAY_KEYWORDS:
                    function_type_enum = GridFunctionTypeEnum.FUNCTION_TABLE
                    try:
                        function_table_m = int(words[1])
                    except ValueError:
                        warnings.warn(f'ValueError at function {function_number}: '
                                      'could not convert string to int.')
                else:
                    region_type = words[1]
                    region_number_list0 = array_function[li + 1].replace(',', ' ').split()
                    try:
                        region_number_list = [round(float(i)) for i in region_number_list0]
                    except ValueError:
                        warnings.warn(f'ValueError at function {function_number}: '
                                      'could not convert string to integer.')
            if len(words) > 2:
                if words[1] in GRID_ARRAY_KEYWORDS:
                    region_type = words[1]
                    region_number_list0 = array_function[li + 1].replace(',', ' ').split()
                    try:
                        region_number_list = [round(float(i)) for i in region_number_list0]
                    except ValueError:
                        warnings.warn(f'ValueError at function {function_number}: '
                                      'could not convert string to integer.')
                    try:
                        function_table_m = int(words[2])
                    except ValueError:
                        warnings.warn(f'ValueError at function {function_number}: '
                                      'could not convert string to int.')
                    if len(words) > 3:
                        try:
                            function_table_p_list = [float(i) for i in words[3:]]
                        except ValueError:
                            warnings.warn(f'ValueError at function {function_number}: '
                                          'could not convert string to float.')
                else:
                    try:
                        function_table_m = int(words[1])
                    except ValueError:
                        warnings.warn(f'ValueError at function {function_number}: '
                                      'could not convert string to int.')
                    if len(words) > 2:
                        try:
                            function_table_p_list = [float(i) for i in words[2:]]
                        except ValueError:
                            warnings.warn(f'ValueError at function {function_number}: '
                                          'could not convert string to float.')

        if nfo.check_token('BLOCKS', modified_line):
            block_array = [int(x) for x in words[1:7]]

        if nfo.check_token('GRID', modified_line):
            grid_indx = words.index('GRID')
            if len(words) > grid_indx+1:
                grid_name = words[grid_indx+1]

        if nfo.check_token('RANGE', modified_line) and nfo.check_token('INPUT', modified_line):
            split_range_input = modified_line.split('INPUT')[1].split()
            if len(split_range_input) % 2 == 1:  # Should be an even number of entries
                # Remove the last entry, which is not a pair
                dropped_range_input = split_range_input.pop()
                warnings.warn(f'RANGE INPUT for function {function_number} has an odd number of entries.\n'
                              f'Ignoring the last value: "{dropped_range_input}" from the range input.\n'
                              f'In line: "{modified_line}"')
            try:
                # Create pair-wise min-max tuples in a list
                input_range_iterator = iter([float(i) for i in split_range_input])
                input_range_list = list(zip(input_range_iterator, input_range_iterator))
            except ValueError:
                warnings.warn(f'ValueError at function {function_number}: could not convert string to float.')

        if nfo.check_token('RANGE', modified_line) and nfo.check_token('OUTPUT', modified_line):
            split_range_output = modified_line.split('OUTPUT')[1].split()
            if len(split_range_output) % 2 == 1:  # Should be an even number of entries
                # Remove the last entry, which is not a pair
                dropped_range_output = split_range_output.pop()
                warnings.warn(f'RANGE OUTPUT for function {function_number} has an odd number of entries.\n'
                              f'Ignoring the last value "{dropped_range_output}" from range output.\n'
                              f'In line: "{modified_line}"')
            try:
                # Create pair-wise min-max tuples in a list
                output_range_iterator = iter([float(i) for i in split_range_output])
                output_range_list = list(zip(output_range_iterator, output_range_iterator))
            except ValueError:
                warnings.warn(f'ValueError at function {function_number}: could not convert string to float.')

        if nfo.check_token('DRANGE', modified_line):
            warnings.warn(f'Function {function_number}: Function table entries will be excluded from summary df.')
            drange_list = [float(x) for x in words[1:]]
            function_type_enum = GridFunctionTypeEnum.FUNCTION_TABLE

        if nfo.check_token('ANALYT', modified_line):
            if words[1] == 'POLY':
                # POLY should just map to POLYN in the enum
                # This is an undocumented feature in the Nexus manual.
                function_type_enum = GridFunctionTypeEnum.POLYN
            else:
                function_type_enum = GridFunctionTypeEnum[words[1]]
            if len(words) > 2:
                # remove the first 2 words in line, and set the rest to coefficients
                function_coefficients0 = words[2:]
                # convert string coefficient values to numerical, if possible:
                try:
                    function_coefficients = [float(i) for i in function_coefficients0]
                except ValueError:
                    warnings.warn(f'ValueError at function {function_number}: could not convert string to float.')

        if len(output_line_headers) > 0:
            function_type_enum = GridFunctionTypeEnum.FUNCTION_TABLE
            function_table = nfo.read_table_to_df(array_function[li:], noheader=True)
            function_table.columns = output_line_headers
            output_line_headers = []

        if nfo.check_token('OUTPUT', modified_line) and not nfo.check_token('RANGE', modified_line):
            input_array_list = words[:words.index('OUTPUT')]
            output_array_list = words[words.index('OUTPUT') + 1:]
            output_line_headers = input_array_list + output_array_list

    # Create output NexusGridArrayFunction object
    new_grid_array_function = NexusGridArrayFunction(
        region_type=region_type,
        blocks=block_array,
        grid_name=grid_name,
        region_number=region_number_list,
        function_type=function_type_enum,
        input_array=input_array_list,
        output_array=output_array_list,
        function_values=function_coefficients,
        input_range=input_range_list,
        output_range=output_range_list,
        drange=drange_list,
        function_table=function_table,
        function_table_m=function_table_m,
        function_table_p_list=function_table_p_list
    )
    return new_grid_array_function
