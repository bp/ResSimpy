# from ResSimpy.Nexus.NexusSimulator import NexusSimulator
# import ResSimpy.Nexus.nexus_file_operations as nfo
# from ResSimpy.Nexus.NexusKeywords.grid_function_keywords import INTEGER_ARRAYS
import pandas as pd
from typing import Union, List


def collect_function_block_lines(file_as_list: list[str], str_to_search: str = 'OUTPUT',
                                 str_to_avoid: str = 'RANGE') -> list:
    """ Collects all lines until the line that contains str_to_search, but not str_to_avoid.
        Uses recursion.
     Args:
         file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                    --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
         str_to_search (str): string to search in the file. Defaults to 'OUTPUT'.
     Raises:
         ValueError: #TODO
     Returns:
         list[str]: function block lines as a list of strings
     """
    # Return empty list if list is empty - probably unnecessary # TODO: Raise error??
    if not file_as_list:
        return []

    # Filter the empty strings from file:
    # file_as_list = list(filter(None, file_as_list))

    # If str_to_search is in first item of list, return the first item only.
    # TODO: raise error if str_to_search is the last item in file_as_list
    if (str_to_search in file_as_list[0].upper()) and (str_to_avoid not in file_as_list[0].upper()):
        return [file_as_list[0]]

    # Recursion time!!! get the first item, search for str_to_search in the rest of the lines, and repeat.
    return [file_as_list[0]] + collect_function_block_lines(file_as_list[1:])


def collect_all_function_blocks(file_as_list: list[str]) -> list[list[str]]:
    """ Collects all the function blocks within a grid file.
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                     --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
          str_to_search (str): string to search in the file. Defaults to 'OUTPUT'.
      Returns:
          list[list[str]]: list of function block lines as a list of strings
      """
    function_list = []

    for i, line in enumerate(file_as_list):

        if line.upper().startswith('FUNCTION'):
            # fetch the rest of the items until finding the line that contains 'OUTPUT', but not 'RANGE':
            function_body = collect_function_block_lines(file_as_list[i:])
            function_list.append(function_body)

    return function_list


def create_function_parameters_df(file_as_list: list[str]):
    """ Creates a dataframe to hold all the function properties and parameters:
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                     --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
      Returns:
          pandas.DataFrame: a dataframe holding each function's parameters in a row.
      """

    functions_df = pd.DataFrame(
        columns=['FUNCTION #', 'i1', 'i2', 'j1', 'j2', 'k1', 'k2', 'region_type', 'region_numbers',
                 'analyt_func_type', 'func_coeff', 'grid', 'range_input', 'range_output', 'drange',
                 'input_arrays', 'output_arrays'])

    # Collect all the function blocks in a grid file:
    function_list_to_parse = collect_all_function_blocks(file_as_list)

    for b, block in enumerate(function_list_to_parse):
        #print(f'reading function block number: {b}')

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
            if 'FUNCTION' in line:
                if len(words) == 1:
                    continue
                if len(words) == 2:  # TODO: deal with tabular function option keywords
                    region_type = words[1]
                    region_number_list = block[li + 1].split()
                if len(words) > 2:  # TODO: deal with tabular function option keywords
                    print('Detected Max number of func table entries. This method does not collect function tables.')
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
                print('DRANGE: This method only works with analytical functions, not with function tables.')
                words.pop(0)
                drange_list = words
            if 'OUTPUT' in line and 'RANGE' not in line:
                input_array_list = words[:words.index('OUTPUT')]
                output_array_list = words[words.index('OUTPUT') + 1:]
        # TODO: find a safer way to create the new function row
        function_row = [b + 1, i1, i2, j1, j2, k1, k2, region_type, region_number_list, function_type,
                        function_coefficients,
                        grid_name, input_arrays_min_max_list, output_arrays_min_max_list, drange_list, input_array_list,
                        output_array_list]
        functions_df.loc[len(functions_df)] = function_row
    return functions_df


def summarize_model_functions(file_as_list: list[str]):
    """ Extracts all function parameters into a df, with an added column of human-readable notations for each function:
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                     --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
      Raises:
          AttributeError: if no functions have been found # TODO
      Returns:
          pandas.DataFrame: a dataframe holding each function's translation/summary in a row.
      """

    # get the df from create_function_parameters_df, add a new column, and populate based on ANALYT function type:

    function_summary_df = create_function_parameters_df(file_as_list)
    function_summary_df['notation'] = ''

    for index, row in function_summary_df.iterrows():

        formula = row['output_arrays'][0] + ' = '

        # ANALYT POLYN
        if row['analyt_func_type'].upper() == 'POLYN':
            n = len(row['func_coeff'])

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

        if row['analyt_func_type'].upper() == 'ABS':
            formula += f"| {row['input_arrays'][0]} |"

        # ANALYT EXP
        if row['analyt_func_type'].upper() == 'EXP':
            formula += f"e^{row['input_arrays'][0]}"

        # ANALYT EXP10
        if row['analyt_func_type'].upper() == 'EXP10':
            formula += f"10^{row['input_arrays'][0]}"

        # ANALYT LOG
        if row['analyt_func_type'].upper() == 'LOG':
            formula += f"ln|{row['input_arrays'][0]}|"

        # ANALYT LOG10
        if row['analyt_func_type'].upper() == 'LOG10':
            # formula += f"log\u2081\u2080|{row['input_arrays'][0]}|"
            formula += f"log10|{row['input_arrays'][0]}|"

        # ANALYT SQRT
        if row['analyt_func_type'].upper() == 'SQRT':
            formula += f"SQRT|{row['input_arrays'][0]}|"

        # ANALYT GE
        if row['analyt_func_type'].upper() == 'GE':
            formula += f"({row['input_arrays'][0]} if {row['input_arrays'][0]} >= {row['func_coeff'][0]}; " \
                       f"{row['func_coeff'][1]} otherwise)"

        # ANALYT LE
        if row['analyt_func_type'].upper() == 'LE':
            formula += f"({row['input_arrays'][0]} if {row['input_arrays'][0]} <= {row['func_coeff'][0]}; " \
                       f"{row['func_coeff'][1]} otherwise)"

        # ANALYT ADD
        if row['analyt_func_type'].upper() == 'ADD':
            formula += f"{row['input_arrays'][0]} + {row['input_arrays'][1]}"

        # ANALYT SUBT
        if row['analyt_func_type'].upper() == 'SUBT':
            formula += f"{row['input_arrays'][0]} - {row['input_arrays'][1]}"

        # ANALYT DIV
        if row['analyt_func_type'].upper() == 'DIV':
            formula += f"({row['input_arrays'][0]} / {row['input_arrays'][1]} if {row['input_arrays'][1]} != 0; " \
                       f"{row['input_arrays'][0]} otherwise)"

        # ANALYT MULT
        if row['analyt_func_type'].upper() == 'MULT':
            formula += f"{row['input_arrays'][0]} * {row['input_arrays'][1]}"

        # ANALYT MIN
        if row['analyt_func_type'].upper() == 'MIN':
            formula += f"min({row['input_arrays'][0]}, {row['input_arrays'][1]})"

        # ANALYT MAX
        if row['analyt_func_type'].upper() == 'MAX':
            formula += f"max({row['input_arrays'][0]}, {row['input_arrays'][1]})"

        # fill in the notation value for the row
        function_summary_df.loc[index, 'notation'] = formula

    return function_summary_df
