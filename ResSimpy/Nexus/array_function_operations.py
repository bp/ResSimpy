#from ResSimpy.Nexus.NexusSimulator import NexusSimulator
#import ResSimpy.Nexus.nexus_file_operations as nfo
#from ResSimpy.Nexus.NexusKeywords.grid_function_keywords import INTEGER_ARRAYS
import pandas as pd


def collect_function_block_lines(file_as_list: list[str], str_to_search: str = 'OUTPUT',
                                 str_to_avoid: str = 'RANGE') -> list:
    """ Collects all lines until the line that contains str_to_search.
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

    # Filter the empty strings from file: # TODO: incorporate this into nfo.load_file_as_list()
    file_as_list = list(filter(None, file_as_list))

    # If str_to_search is in first item of list, return the first item only.
    # TODO: raise error if str_to_search is the last item in file_as_list
    if (str_to_search in file_as_list[0]) and (str_to_avoid not in file_as_list[0]):
        return [file_as_list[0]]

    # Recursion time!!! get the first item, search for str_to_search in the rest of the lines, and repeat.
    return [file_as_list[0]] + collect_function_block_lines(file_as_list[1:])


# Find the FUNCTION keywords in str_file_words_as_list
# Walk str_file_lines one by one and collect the keywords from referenced files
# Returns list[list[function lines]]
def collect_all_function_blocks(file_as_list: list[str]) -> list[list[str]]:
    """ Collects all the function blocks within a grid file.
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                     --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
          str_to_search (str): string to search in the file. Defaults to 'OUTPUT'.
      Raises:
          ValueError: #TODO
      Returns:
          list[str]: function block lines as a list of strings
      """
    function_list = []

    for i, line in enumerate(file_as_list):

        if line.startswith('FUNCTION'):
            # fetch the rest of the items until finding the line that contains 'OUTPUT'
            function_body = collect_function_block_lines(file_as_list[i:])
            function_list.append(function_body)

    return function_list


def create_function_parameters_df(file_as_list: list[str]):
    """ Creates a dataframe to hold all the function properties and parameters:
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                     --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
      Raises:
          ValueError: #TODO
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
        print(f'reading function block number: {b}')

        # set the default values for the parameters,
        # so if they don't exist in dataframe they won't appear as NaN or give error.
        i1 = i2 = j1 = j2 = k1 = k2 = region_type = region_number_list = function_type = function_coefficients = \
        grid_name = input_arrays_min_max_list = output_arrays_min_max_list = drange_list = input_array_list = output_array_list = ''

        for l, line in enumerate(block):
            words = line.split()
            # print(f'reading line number: {l}')
            if 'BLOCKS' in line:
                i1 = words[1]
                i2 = words[2]
                j1 = words[3]
                j2 = words[4]
                k1 = words[5]
                k2 = words[6]
                print (f'blocks {i1,i2,j1, j2, k1, k2}')
            if 'FUNCTION' in line:
                if len(words) == 1:
                    continue
                if len(words) == 2:  # TODO: deal with tabular function option keywords
                    region_type = words[1]
                    # print(f'reg_type: {reg_type}')
                    region_number_list = block[l + 1].split()
                    # print(f'reg_numbers: {reg_numbers}')
                if len(words) > 2:  # TODO: deal with tabular function option keywords
                    print(
                        'Detected Max number of func table entries. This method only works with analytical functions, not with function tables.')
            if 'ANALYT' in line:
                function_type = words[1]
                # print(function_type)
                if len(words) > 2:
                    # remove the first 2 words in line, and set the rest to coefficients
                    words.pop(0)
                    words.pop(0)
                    function_coefficients = words
                    # print(function_coefficients)
            if 'GRID' in line:
                grid_name = words[1]
            if 'RANGE' in line and 'INPUT' in line:
                words.pop(0)
                words.pop(0)
                input_arrays_min_max_list = words
                # print(f'input arrays ranges: {input_arrays_min_max_list}')
            if 'RANGE' in line and 'OUTPUT' in line:
                words.pop(0)
                words.pop(0)
                output_arrays_min_max_list = words
                # print(f'output arrays ranges: {output_arrays_min_max_list}')
            if 'DRANGE' in line:
                print('DRANGE: This method only works with analytical functions, not with function tables.')
                words.pop(0)
                drange_list = words
                # print (drange_list)
            if 'OUTPUT' in line and 'RANGE' not in line:
                input_array_list = words[:words.index('OUTPUT')]
                output_array_list = words[words.index('OUTPUT') + 1:]
                # print(input_array_list)
                # print(output_array_list)
        # TODO: find a safer way to create the new function row
        function_row = [b + 1, i1, i2, j1, j2, k1, k2, region_type, region_number_list, function_type,
                        function_coefficients,
                        grid_name, input_arrays_min_max_list, output_arrays_min_max_list, drange_list, input_array_list,
                        output_array_list]
        functions_df.loc[len(functions_df)] = function_row
    return functions_df


# now create a column, that will turn the function to a human readable mathematical notation
# function_properties['func_meaning'] = pd.concat(function_properties['input_arrays'], function_properties['drange'])
# function_properties

# my_functions_df = create_function_parameters_df(my_str_file_lines)
# print(my_functions_df)
# my_functions_df.to_csv('C:\\Users\\dirii0\\OneDrive - BP\\Documents\\ResSimPy\\notebooks\\test_output_functions_df.csv')


def summarize_model_functions(file_as_list: list[str]):
    """ Translates and summarizes the model functions in a non-maddening, human-readable form:
      Args:
          file_as_list (list[str] | NexusFile): a list of strings containing each line of the file as an item,
                     --->file_as_list = nfo.load_file_as_list(str_grid_file_path, strip_comments=True, strip_str=True)
      Raises:
          ValueError: #TODO
      Returns:
          pandas.DataFrame: a dataframe holding each function's translation/summary in a row.
      """

    # create a new dataframe that will hold the summary of all the functions
    function_summary_df = pd.DataFrame(columns=['function#', 'output_array', 'where', 'function'])
    return function_summary_df