import pytest
from ResSimpy.Utils.Test_Utils.utility_for_tests import get_fake_stat_pathlib_time


@pytest.fixture(scope="function", autouse=True)
def simulation(mocker):
    # Create a basic listdir mock to help mock out a file system

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)
    # Create an override for isfile checks
    mocker.patch("os.path.isfile", lambda x: True)

@pytest.fixture
def fixture_for_osstat_pathlib(mocker):
    get_fake_stat_pathlib_time(mocker)


