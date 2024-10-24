import pytest

from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from tests.multifile_mocker import mock_multiple_files


@pytest.mark.parametrize('modifier, value', [
    ('VALUE', '/some/path/to/file.dat'),
    ('CON', 25),
])
def test_grid_array_definition_max_min(mocker, modifier, value):
    # Arrange
    grid_array_definition = GridArrayDefinition(modifier=modifier, value=value, keyword_in_include_file=False)
    # mock open the file
    data = '1 2 3 4 5\n6 7 8 9 10\n11 12\n13 14 15 16 17\n18 19 20 21 22\n23 24 25\n'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            value: data,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    expected_max = 25
    expected_min = 1 if modifier == 'VALUE' else 25
    # Act
    result_max = grid_array_definition.max()
    result_min = grid_array_definition.min()

    # Assert
    assert result_max == expected_max
    assert result_min == expected_min
