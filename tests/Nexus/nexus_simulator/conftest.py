import pytest


@pytest.fixture(scope="function", autouse=True)
def simulation(mocker):
    # Create a basic listdir mock to help mock out a file system

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)
    # Create an override for isfile checks
    mocker.patch("os.path.isfile", lambda x: True)

@pytest.fixture(scope="function", autouse=True)
def globalFixture(mocker):
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = None
    path_mock.return_value.group.return_value = None
    

    os_mock = mocker.MagicMock()
    mocker.patch('os.stat',os_mock)
    os_mock.return_value.st_mtime.return_value = None
    

    ts_mock = mocker.MagicMock()
    mocker.patch('datetime.datetime',ts_mock)
    ts_mock.return_value.fromtimestamp.return_value = None


