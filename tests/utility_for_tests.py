import pathlib
from unittest.mock import Mock

from pytest_mock import MockerFixture

from ResSimpy.Nexus.NexusSimulator import NexusSimulator


def check_file_read_write_is_correct(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture, write_file_name: str, number_of_writes=1):
    assert len(modifying_mock_open.call_args_list) == number_of_writes
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(write_file_name, 'w')
    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == number_of_writes
    assert list_of_writes[-1].args[0] == expected_file_contents

def get_fake_nexus_simulator(mocker: MockerFixture, fcs_file_path: str = '/path/fcs_file.fcs',
                             mock_open: bool = True) -> NexusSimulator:
    """Returns a set up NexusSimulator object that can then be used for testing. Note that if mock_open is set to True,
    it mocks out the builtin open method, which may then have to be overwritten by the calling code."""
    if mock_open:
        open_mock = mocker.mock_open(read_data='')
        mocker.patch("builtins.open", open_mock)
    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    fake_nexus_sim = NexusSimulator(fcs_file_path)

    return fake_nexus_sim

def get_fake_stat_pathlib_time(mocker):
    """ mocks pathlibpath, os.stat and datetime"""
    
    dt_mock = mocker.MagicMock()
    mocker.patch('datetime.datetime',dt_mock)
    dt_mock.fromtimestamp.return_value = None

    owner_mock = mocker.MagicMock(return_value=None)
    group_mock = mocker.MagicMock(return_value=None)
    mocker.patch.object(pathlib.Path, 'owner', owner_mock)
    mocker.patch.object(pathlib.Path, 'group', group_mock)

    os_mock = mocker.MagicMock()
    mocker.patch('os.stat',os_mock)
    os_mock.return_value.st_mtime = None

