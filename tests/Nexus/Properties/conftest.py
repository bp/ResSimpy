
import pytest

@pytest.fixture
def globalFixture(mocker,request):
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = None
    path_mock.return_value.group.return_value = None

    os_mock = mocker.MagicMock()
    mocker.patch('os.stat',os_mock)
    os_mock.return_value.st_mtime = None

    def sideeffect(timestamp=None):
        return None
    ts_mock = mocker.MagicMock()
    mocker.patch('datetime.datetime',ts_mock)
    ts_mock.return_value.fromtimestamp.side_effect = sideeffect

    
  