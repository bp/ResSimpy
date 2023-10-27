import pytest
import pathlib
# from tests.utility_for_tests import get_fake_stat_pathlib_time


@pytest.fixture(scope='function', autouse=True)
def mock_out_file_datetime_operations(mocker, request):
    """ mocks pathlibpath, os.stat and datetime"""

    # Avoid mocking datetime if the test setup relies upon it
    if not request.node.get_closest_marker('maintain_datetime_behaviour'):
        dt_mock = mocker.MagicMock()
        mocker.patch('datetime.datetime', dt_mock)
        dt_mock.fromtimestamp.return_value = None

    owner_mock = mocker.MagicMock(return_value=None)
    group_mock = mocker.MagicMock(return_value=None)
    mocker.patch.object(pathlib.Path, 'owner', owner_mock)
    mocker.patch.object(pathlib.Path, 'group', group_mock)

    os_mock = mocker.MagicMock()
    mocker.patch('os.stat', os_mock)
    os_mock.return_value.st_mtime = None
