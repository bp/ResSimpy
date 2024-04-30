from unittest.mock import Mock

from ResSimpy import NexusSimulator
from ResSimpy import NexusSimulator as Simulator


def test_top_level_imports(mocker):
    # Arrange
    open_mock = mocker.mock_open(read_data='')
    mocker.patch("builtins.open", open_mock)
    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)
    # Act
    result = NexusSimulator('/path/fcs_file.fcs')

    result_2 = Simulator('/path/fcs_file.fcs')

    # Assert
    assert result is not None
    assert result_2 is not None
