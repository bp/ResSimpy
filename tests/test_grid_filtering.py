# tests for filtering the grid file to ensure it is only numeric values
import numpy as np
import pytest
from ResSimpy.File import File
from ResSimpy.Grid import GridArrayDefinition, Grid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid

from tests.utility_for_tests import mock_multiple_files


@pytest.mark.parametrize("file_as_list, expected_filtered_file_as_list", [

    # basic test
    (['1 2 \t 3 4 5', '6 7 8 9 10'], ['1 2 3 4 5', '6 7 8 9 10']),

    # with a comment
    (['-- comment', '1 2 3 4 5'], ['1 2 3 4 5']),
    # with a comment at the end
    (['1 2 3 4 5 -- comment'], ['1 2 3 4 5']),
    # with keywords in the file
    (['KEYWORD', '1 2 3 4 5'], ['', '1 2 3 4 5']),
    # with keywords in the file at the end
    (['1 2 3 4 5 keyword', 'KEYWORD'], ['1 2 3 4 5', '']),
],
    ids=['basic', 'comment', 'comment_end', 'keyword', 'keyword_end'])
def test_grid_filter_file_as_list(file_as_list, expected_filtered_file_as_list):
    # Arrange
    # Act
    result = Grid.grid_filter_file_as_list(file_as_list)
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

    expected_filtered_file_as_list = ['', '1 2 3 4 5', '6 7 8 9 10', '', '11 12', '']
    expected_file = File(location='/my/grid/file_filtered.dat', file_loading_skipped=False,
                         file_content_as_list=expected_filtered_file_as_list, create_as_modified=True)
    grid_array_definition = GridArrayDefinition(modifier='VALUE', value=file_path, keyword_in_include_file=False)

    # Act
    result = Grid.filter_grid_array_definition(grid_array_definition)
    # Assert
    assert result == expected_file


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
    result_from_grid_array = grid.porosity.get_array()
    # Assert
    assert np.array_equal(expected_array, result)
    assert np.array_equal(expected_array, result_from_grid_array)
