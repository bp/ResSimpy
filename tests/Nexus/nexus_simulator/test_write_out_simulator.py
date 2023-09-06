import os

from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


def test_write_out_new_simulator(mocker, fixture_for_osstat_pathlib):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat'''

    runcontrol_contents = '''START 01/01/2019'''
    expected_runcontrol_path = os.path.join('nexus_includes', 'runcontrol.dat')
    expected_surface_path = os.path.join('nexus_includes', 'surface_file_01.dat')
    expected_fcs_file_contents = (
        '\n'
        '        RUN_UNITS ENGLISH\n'
        '        DATEFORMAT DD/MM/YYYY\n'
        '        RECURRENT_FILES\n'
        f'        RUNCONTROL {expected_runcontrol_path}\n'
        f'        SURFACE Network 1  {expected_surface_path}')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': '',
            '/nexus_data/runcontrol.dat': runcontrol_contents}
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    nexus_sim.write_out_new_simulator(new_file_path='/new_path/new_fcs_file.fcs',
                                      new_include_file_location='nexus_includes')

    # Assert
    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [call for call in writing_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == 3
    assert list_of_writes[-1].args[0] == expected_fcs_file_contents
    assert list_of_writes[0].args[0] == runcontrol_contents
    assert list_of_writes[1].args[0] == ''
