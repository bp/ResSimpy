from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from ResSimpy.Nexus.NexusWells import NexusWells
from tests.multifile_mocker import mock_multiple_files


def check_file_read_write_is_correct(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture, write_file_name: str):
    assert len(modifying_mock_open.call_args_list) == 1
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(
        write_file_name, 'w')

    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [
        call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == 1
    assert list_of_writes[0].args[0] == expected_file_contents


@pytest.mark.parametrize('fcs_file_contents, wells_file, expected_result', [
('''DATEFORMAT DD/MM/YYYY
WelLS sEt 1 /my/wellspec/file.dat''',

''' ! Wells file:
TIME 01/01/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5

TIME 01/03/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
4  5  6 4.2

TIME 01/05/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
''',
''' ! Wells file:
TIME 01/01/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5

TIME 01/03/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
4  5  6 4.2
4 5 6 7.5

TIME 01/05/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
''',)

])
def test_write_to_file(mocker, fcs_file_contents, wells_file, expected_result):
    # Arrange
    start_date = '01/01/2020'
    add_perf_date = '01/03/2020'
    fcs_file_path = 'fcs_file.fcs'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            '/my/wellspec/file.dat': wells_file,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    mock_nexus_sim = NexusSimulator('fcs_file.fcs')
    mock_nexus_sim.start_date_set(start_date)
    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.5}

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)


    # Act
    mock_nexus_sim.Wells.add_completion(well_name='well1', completion_properties=add_perf_dict,
                                        preserve_previous_completions=True)

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat')
