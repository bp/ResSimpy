import pytest
import pathlib
# from tests.utility_for_tests import get_fake_stat_pathlib_time


@pytest.fixture(scope='function', autouse=True)
def mock_out_file_datetime_operations(mocker, request):
    """ mocks pathlibpath and os.stat"""

    # Mock out pathlib and stat libraries
    owner_mock = mocker.MagicMock(return_value=None)
    group_mock = mocker.MagicMock(return_value=None)
    mocker.patch.object(pathlib.Path, 'owner', owner_mock)
    mocker.patch.object(pathlib.Path, 'group', group_mock)

    os_mock = mocker.MagicMock()
    mocker.patch('os.stat', os_mock)
    os_mock.return_value.st_mtime = None
