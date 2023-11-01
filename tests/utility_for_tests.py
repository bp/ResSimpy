import pathlib
from unittest.mock import Mock

from pytest_mock import MockerFixture
from tests.multifile_mocker import mock_multiple_files

from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.NexusSimulator import NexusSimulator


def check_file_read_write_is_correct(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture, write_file_name: str, number_of_writes=1,
                                     expected_write_method='w'):
    assert len(modifying_mock_open.call_args_list) == number_of_writes
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(write_file_name, expected_write_method)
    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == number_of_writes
    assert list_of_writes[-1].args[0] == expected_file_contents


def check_sequential_write_is_correct(expected_file_contents: list[str], modifying_mock_open: Mock,
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

def uuid_side_effect():
    """Generates an infinite sequence of overwrites for uuid calls."""
    num = 0
    while True:
        yield 'uuid' + str(num)
        num += 1


def generic_fcs(mocker):

    fcs_path = 'test_fcs.fcs'

    fcs_content = '''DESC reservoir1
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        INITIALIZATION_FILES
    	 EQUIL Method 1 nexus_data/nexus_data/equil_01.dat
    	 EQUIL Method 2 nexus_data/nexus_data/equil_02.dat
        STRUCTURED_GRID nexus_data/structured_grid_1_reg_update.dat
    	 OPTIONS nexus_data/nexus_data/ref_options_reg_update.dat
    	 
    	ROCK_FILES
	        ROCK Method 1 nexus_data/nexus_data/rock.dat
	        RELPM Method 1 nexus_data/relpm.dat
    	 NET_METHOD_FILES
         HYD METHOd 3 hyd.dat
        
        RECURRENT_FILES
            RUNCONTROL nexus_data/nexus_data/runcontrol.dat
            WELLS Set 1 nexus_data/nexus_data/wells.dat
            SURFACE Network 1 nexus_data/nexus_data/surface.dat
         '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)
    fcs = FcsNexusFile.generate_fcs_structure(fcs_path)
    return fcs
