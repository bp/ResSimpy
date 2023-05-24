from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from ResSimpy.Nexus.NexusWells import NexusWells
from tests.multifile_mocker import mock_multiple_files


def check_file_read_write_is_correct(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture, write_file_name: str, number_of_writes=1):
    assert len(modifying_mock_open.call_args_list) == number_of_writes
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(
        write_file_name, 'w')

    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [
        call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == number_of_writes
    assert list_of_writes[-1].args[0] == expected_file_contents


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


@pytest.mark.parametrize('fcs_file_contents, wells_file, expected_result, expected_removed_completion_line, '
'expected_obj_locations, number_of_writes', [
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

TIME 01/05/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
''',
10, [4, 9, 14], 1),


('''DATEFORMAT DD/MM/YYYY
WelLS sEt 1 /my/wellspec/file.dat''',

'''
TIME 01/01/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5

TIME 01/03/2020
WELLSPEC well1
iw jw l radw
4  5      6 4.2

WELLSPEC well2
iw jw l radw
5 6 4 3.2
''',
'''
TIME 01/01/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5

TIME 01/03/2020

WELLSPEC well2
iw jw l radw
5 6 4 3.2
''',
9, [4, 10], 3),
], ids=['basic_test', 'only 1 completion to remove'] )
def test_remove_completion_write_to_file(mocker, fcs_file_contents, wells_file, expected_result,
        expected_removed_completion_line, expected_obj_locations, number_of_writes):
    # Arrange
    start_date = '01/01/2020'
    remove_perf_date = '01/03/2020'
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
    remove_perf_dict = {'date': remove_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 4.2}
    well_files = mock_nexus_sim.fcs_file.well_files[1]
    object_locations = well_files.object_locations
    object_locations_minus_completion = {k: v for k, v in object_locations.items() if v != expected_removed_completion_line}
    object_locations_minus_completion = {k: v for k, v in zip(object_locations_minus_completion, expected_obj_locations)}
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    mock_nexus_sim.Wells.remove_completion(well_name='well1', completion_properties=remove_perf_dict,
                                           )
    result_object_ids = mock_nexus_sim.fcs_file.well_files[1].object_locations
    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat',
                                     number_of_writes=number_of_writes)

    assert result_object_ids == object_locations_minus_completion

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
4 8 6 10.2

TIME 01/05/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
''',)

])
def test_modify_completion_write_to_file(mocker, fcs_file_contents, wells_file, expected_result,):
    # Arrange
    start_date = '01/01/2020'
    remove_perf_date = '01/03/2020'
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
    modify_perf_target = {'date': remove_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 4.2}
    modify_perf_new_properties = {'date': remove_perf_date, 'j': 8, 'well_radius': 10.2}

    well_files = mock_nexus_sim.fcs_file.well_files[1]
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    mock_nexus_sim.Wells.modify_completion(well_name='well1', properties_to_modify=modify_perf_new_properties,
                                           completion_to_change=modify_perf_target, )
    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat',
                                     number_of_writes=2,
                                     )
