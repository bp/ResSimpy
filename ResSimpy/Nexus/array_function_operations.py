import ResSimpy.Nexus.nexus_file_operations as nfo
import pandas as pd
from typing import Union, List
import warnings
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS


def collect_all_function_blocks(file_as_list: list[str]) -> list[list[str]]:
    """ Collects all the function blocks within a grid file.
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
      Returns:
          list[list[str]]: list of function block lines as a list of strings
      """
    function_list = []
    function_body: list[str] = []
    reading_function = False
    for i, line in enumerate(file_as_list):
        if nfo.check_token('FUNCTION', line):
            function_body = []
            reading_function = True
        if reading_function:
            function_body.append(line.strip())
            if nfo.check_token('OUTPUT', line) and not nfo.check_token('RANGE', line):
                function_list.append(function_body)
                reading_function = False

    return function_list


def create_function_parameters_df(function_list_to_parse: list[list[str]]) -> pd.DataFrame:
    """ Creates a dataframe to hold all the function properties and parameters:
      Args:
          function_list_to_parse (list[list[str]]): list of functions extracted as list of lines.
      Returns:
          pandas.DataFrame: a dataframe holding each function's parameters in a row.
      """

    functions_df = pd.DataFrame(
        columns=['FUNCTION #', 'blocks [i1,i2,j1,j2,k1,k2]', 'i1', 'i2', 'j1', 'j2', 'k1', 'k2', 'region_type', 'region_numbers',
                 'func_type', 'func_coeff', 'grid', 'range_input', 'range_output', 'drange',
                 'input_arrays', 'output_arrays'])

    for b, block in enumerate(function_list_to_parse):

        # set the empty default values for the parameters,
        # so if they don't exist in dataframe they won't appear as NaN or give error,
        # or repeat the last value for each row.
        i1 = i2 = j1 = j2 = k1 = k2 = region_type = function_type = grid_name = ''
        # set the lists as empty strings as well, otherwise they show up as [] on the dataframe.
        region_number_list: Union[str, List[str]] = ''
        function_coefficients: Union[str, List[str]] = ''
        input_arrays_min_max_list: Union[str, List[str]] = ''
        output_arrays_min_max_list: Union[str, List[str]] = ''
        input_array_list: Union[str, List[str]] = ''
        output_array_list: Union[str, List[str]] = ''
        drange_list: Union[str, List[str]] = ''
        blocks_list: Union[str, List[str]] = ''

        for li, line in enumerate(block):
            line = line.upper()
            words = line.split()
            if 'BLOCKS' in line:
                i1 = words[1]
                i2 = words[2]
                j1 = words[3]
                j2 = words[4]
                k1 = words[5]
                k2 = words[6]
                blocks_list = words[1:7]
                blocks_list = [round(float(i)) for i in blocks_list]

            if 'FUNCTION' in line:
                if len(words) == 1:
                    continue
                if len(words) == 2:
                    if words[1] not in GRID_ARRAY_KEYWORDS:
                        warnings.warn(
                            f'Function {b + 1}:  Function table entries will be excluded from summary df.')
                        function_type = 'function table'
                    else:
                        region_type = words[1]
                        region_number_list = block[li + 1].split()
                if len(words) > 2:  # TODO: deal with tabular function option keywords
                    warnings.warn(f'Function {b+1}:  Function table entries will be excluded from summary df.')
                    function_type = 'function table'
            if 'ANALYT' in line:
                function_type = words[1]
                if len(words) > 2:
                    # remove the first 2 words in line, and set the rest to coefficients
                    words.pop(0)
                    words.pop(0)
                    function_coefficients = words
            if 'GRID' in line:
                grid_name = words[1]
            if 'RANGE' in line and 'INPUT' in line:
                words.pop(0)
                words.pop(0)
                input_arrays_min_max_list = words
            if 'RANGE' in line and 'OUTPUT' in line:
                words.pop(0)
                words.pop(0)
                output_arrays_min_max_list = words
            if 'DRANGE' in line:
                warnings.warn(f'Function {b+1}: Function table entries will be excluded from summary df.')
                words.pop(0)
                drange_list = words
                function_type = 'function table'
            if 'OUTPUT' in line and 'RANGE' not in line:
                input_array_list = words[:words.index('OUTPUT')]
                output_array_list = words[words.index('OUTPUT') + 1:]
        # TODO: find a safer way to create the new function row
        function_row = [b + 1, blocks_list, i1, i2, j1, j2, k1, k2, region_type, region_number_list, function_type,
                        function_coefficients,
                        grid_name, input_arrays_min_max_list, output_arrays_min_max_list, drange_list, input_array_list,
                        output_array_list]
        functions_df.loc[len(functions_df)] = function_row
    return functions_df


def summarize_model_functions(function_list_to_parse: List[List[str]]) -> pd.DataFrame:
    """ Extracts all function parameters into a df, with an added column of human-readable notations for each function:
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

        # ANALYT POLYN
        if row['func_type'].upper() == 'POLYN':
            n = len(row['func_coeff'])
            # TODO: deal with negative coefficient notations
            for x in range(n):
                c = row['func_coeff'][x]
                p = n - x - 1
                arr = row['input_arrays'][0]
                if p == 0:
                    f_portion = f'{c}'
                elif p == 1:
                    f_portion = f'{c}*{arr} + '
                else:
                    f_portion = f'{c}*({arr}^{p}) + '
                formula += f_portion

        # ANALYT ABS
        # TODO: test nexus with multiple input and output arrays

        if row['func_type'].upper() == 'ABS':
            formula += f"| {row['input_arrays'][0]} |"

        # ANALYT EXP
        if row['func_type'].upper() == 'EXP':
            formula += f"e^{row['input_arrays'][0]}"

        # ANALYT EXP10
        if row['func_type'].upper() == 'EXP10':
            formula += f"10^{row['input_arrays'][0]}"

        # ANALYT LOG
        if row['func_type'].upper() == 'LOG':
            formula += f"ln|{row['input_arrays'][0]}|"

        # ANALYT LOG10
        if row['func_type'].upper() == 'LOG10':
            formula += f"log10|{row['input_arrays'][0]}|"

        # ANALYT SQRT
        if row['func_type'].upper() == 'SQRT':
            formula += f"SQRT|{row['input_arrays'][0]}|"

        # ANALYT GE
        if row['func_type'].upper() == 'GE':
            formula += f"({row['input_arrays'][0]} if {row['input_arrays'][0]} >= {row['func_coeff'][0]}; " \
                       f"{row['func_coeff'][1]} otherwise)"

        # ANALYT LE
        if row['func_type'].upper() == 'LE':
            formula += f"({row['input_arrays'][0]} if {row['input_arrays'][0]} <= {row['func_coeff'][0]}; " \
                       f"{row['func_coeff'][1]} otherwise)"

        # ANALYT ADD
        if row['func_type'].upper() == 'ADD':
            formula += f"{row['input_arrays'][0]} + {row['input_arrays'][1]}"

        # ANALYT SUBT
        if row['func_type'].upper() == 'SUBT':
            formula += f"{row['input_arrays'][0]} - {row['input_arrays'][1]}"

        # ANALYT DIV
        if row['func_type'].upper() == 'DIV':
            formula += f"({row['input_arrays'][0]} / {row['input_arrays'][1]} if {row['input_arrays'][1]} != 0; " \
                       f"{row['input_arrays'][0]} otherwise)"

        # ANALYT MULT
        if row['func_type'].upper() == 'MULT':
            formula += f"{row['input_arrays'][0]} * {row['input_arrays'][1]}"

        # ANALYT MIN
        if row['func_type'].upper() == 'MIN':
            formula += f"min({row['input_arrays'][0]}, {row['input_arrays'][1]})"

        # ANALYT MAX
        if row['func_type'].upper() == 'MAX':
            formula += f"max({row['input_arrays'][0]}, {row['input_arrays'][1]})"

        # fill in the notation value for the row
        function_summary_df.loc[index, 'notation'] = formula

    # move notation column to the beginning of table:
    second_column = function_summary_df.pop('notation')
    function_summary_df.insert(1, 'notation', second_column)

    # set FUNCTION number as the index colum:
    function_summary_df.set_index('FUNCTION #', inplace=True)


    return function_summary_df
