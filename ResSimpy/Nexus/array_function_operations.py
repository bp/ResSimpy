"""A collection of functions for handling grid functions from Nexus."""
from __future__ import annotations
import ResSimpy.Nexus.nexus_file_operations as nfo
import pandas as pd
from typing import Union
import warnings
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS


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

    for i, line in enumerate(file_as_list):
        if nfo.check_token('FUNCTION', line):
            function_body = []
            reading_function = True
        if reading_function:
            # remove all comments following the first '!' in a line.
            modified_line = line.split('!', 1)[0]
            function_body.append(modified_line.strip())
            if nfo.check_token('OUTPUT', modified_line) and not nfo.check_token('RANGE', modified_line):
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
            if 'BLOCKS' in modified_line:
                i1 = words[1]
                i2 = words[2]
                j1 = words[3]
                j2 = words[4]
                k1 = words[5]
                k2 = words[6]
                blocks_list = words[1:7]
                blocks_list = [round(float(i)) for i in blocks_list]

            if 'FUNCTION' in modified_line:
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
            if 'ANALYT' in modified_line:
                function_type = words[1]
                if len(words) > 2:
                    # remove the first 2 words in line, and set the rest to coefficients
                    function_coefficients = words[2:]
                    # convert string coefficient values to numerical, if possible:
                    try:
                        function_coefficients = [float(i) for i in function_coefficients]
                    except ValueError:
                        warnings.warn(f'ValueError at function {b + 1}: could not convert string to float.')

            if 'GRID' in modified_line:
                grid_name = words[1]
            if 'RANGE' in modified_line and 'INPUT' in modified_line:
                input_arrays_min_max_list = words[2:]
                # convert string range_input values to numerical, if possible:
                try:
                    input_arrays_min_max_list = [float(i) for i in input_arrays_min_max_list]
                except ValueError:
                    warnings.warn(f'ValueError at function {b + 1}: could not convert string to float.')
            if 'RANGE' in modified_line and 'OUTPUT' in modified_line:
                output_arrays_min_max_list = words[2:]
                # convert string range_input values to numerical, if possible:
                try:
                    output_arrays_min_max_list = [float(i) for i in output_arrays_min_max_list]
                except ValueError:
                    warnings.warn(f'ValueError at function {b + 1}: could not convert string to float.')
            if 'DRANGE' in modified_line:
                warnings.warn(f'Function {b + 1}: Function table entries will be excluded from summary df.')
                drange_list = words[1:]
                function_type = 'function table'
            if 'OUTPUT' in modified_line and 'RANGE' not in modified_line:
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
