from __future__ import annotations
import os

from ResSimpy.FileOperations.File import File
from ResSimpy.FileOperations import file_operations as fo
from ResSimpy.Utils.general_utilities import check_if_string_is_float
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition


def filter_grid_array_definition(grid_array_definition: GridArrayDefinition) -> File:
    """Checks array files for only float values and returns a new file with only float values."""
    file_path = grid_array_definition.absolute_path
    if file_path is None and grid_array_definition.value is not None:
        file_path = grid_array_definition.value
    elif file_path is None:
        raise FileNotFoundError('No file path found in the grid array definition')
    file_as_list = fo.load_file_as_list(file_path)

    new_file_as_list = grid_filter_file_as_list(file_as_list)

    # create a new file with the filtered list
    new_file_path = (os.path.splitext(file_path)[0] + '_filtered' +
                     os.path.splitext(file_path)[1])
    new_grid_file = File(location=new_file_path,
                         file_content_as_list=new_file_as_list,
                         create_as_modified=True,
                         )

    return new_grid_file


def grid_filter_file_as_list(file_as_list: list[str], comment_characters: list[str] | None = None) -> list[str]:
    """Checks array files for only float values and returns a new file with only float values.

    This works for grid arrays only. It does not work well with extremely large files.

    Args:
        file_as_list (list[str]): The file as a list of strings.
        comment_characters (Optional[list[str]]): The comment characters to filter out. Defaults to None.
    """
    if comment_characters is None:
        comment_characters = ['--', '!', 'C']
    if fo.value_in_file('INCLUDE', file_as_list):
        raise NotImplementedError('Nested includes for grid files currently not implemented')
    file_as_list = fo.strip_file_of_comments(file_as_list, comment_characters=comment_characters)
    # remove non float values
    file_as_list = [' '.join([x for x in line.split()
                              if check_if_string_is_float(x)]) + '\n' for line in file_as_list]
    return file_as_list
