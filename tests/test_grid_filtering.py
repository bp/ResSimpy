# tests for filtering the grid file to ensure it is only numeric values
import numpy as np
import pytest
from ResSimpy.File import File
from ResSimpy.GridArrayDefinition import GridArrayDefinition
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.grid_filtering_functions import grid_filter_file_as_list, filter_grid_array_definition

from tests.utility_for_tests import mock_multiple_files


@pytest.mark.parametrize("file_as_list, expected_filtered_file_as_list", [

    # basic test
    (['1 2 \t 3 4 5\n', '6 7 8 9 10\n'], ['1 2 3 4 5\n', '6 7 8 9 10\n']),

    # with a comment
    (['-- comment\n', '1 2 3 4 5\n'], ['1 2 3 4 5\n']),
    # with a comment at the end
    (['1 2 3 4 5 -- comment\n'], ['1 2 3 4 5\n']),
    # with keywords in the file
    (['KEYWORD\n', '1 2 3 4 5\n'], ['\n', '1 2 3 4 5\n']),
    # with keywords in the file at the end
    (['1 2 3 4 5 keyword\n', 'KEYWORD\n'], ['1 2 3 4 5\n', '\n']),
],
    ids=['basic', 'comment', 'comment_end', 'keyword', 'keyword_end'])
def test_grid_filter_file_as_list(file_as_list, expected_filtered_file_as_list):
    # Arrange
    # Act
    result = grid_filter_file_as_list(file_as_list)
    # Assert
    assert result == expected_filtered_file_as_list


def test_filter_grid_file(mocker):
    # Arrange
    # mock out the open file
    file_contents = '''-- comment
    ! Nexus Comment
    1 2 3 4 5 ! comment
    6 7 8 9 10
    ! comment
    11 12
    '''
    file_path = '/my/grid/file.dat'
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_contents,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    expected_filtered_file_as_list = ['\n', '1 2 3 4 5\n', '6 7 8 9 10\n', '\n', '11 12\n', '\n']
    expected_file = File(location='/my/grid/file_filtered.dat', file_loading_skipped=False,
                         file_content_as_list=expected_filtered_file_as_list, create_as_modified=True)
    grid_array_definition = GridArrayDefinition(modifier='VALUE', value=file_path, keyword_in_include_file=False)

    # Act
    result = filter_grid_array_definition(grid_array_definition)
    result_from_array_def = grid_array_definition.filtered_grid_array_def_as_file()
    # Assert
    assert result == expected_file
    assert result_from_array_def == expected_file


def test_grid_to_numpy_array(mocker):
    # Arrange
    file_contents = '''! Comment 345 52
    1 2 3 4 5
    6 7 8 9 10 ! comment
    -- comment?
    11 12'''
    expected_array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    file_path = '/my/grid/file.dat'
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_contents,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    grid = NexusGrid(assume_loaded=True)
    grid._porosity = GridArrayDefinition(modifier='VALUE', value=file_path, keyword_in_include_file=False,
                                         absolute_path=file_path)
    grid._range_x = 2
    grid._range_y = 3
    grid._range_z = 2
    # Act
    result = grid.grid_array_definition_to_numpy_array(grid_array_definition=grid.porosity)
    result_from_grid_array = grid.porosity.get_array_from_file()
    # Assert
    assert np.array_equal(expected_array, result)
    assert np.array_equal(expected_array, result_from_grid_array)
