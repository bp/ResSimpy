import pytest

from tests.Nexus.conftest import mock_out_file_datetime_operations # This import allows us to run tests individually
# (forces it to check the 'parent' conftest as well).

@pytest.fixture(scope="function", autouse=True)
def simulation(mocker):
    # Create a basic listdir mock to help mock out a file system

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)
    # Create an override for isfile checks
    mocker.patch("os.path.isfile", lambda x: True)