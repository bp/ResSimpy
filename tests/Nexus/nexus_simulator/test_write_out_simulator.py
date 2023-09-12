import os

import pytest

from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator

class TestWriteOutSimulator:
    fcs_file_contents = '''
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            RECURRENT_FILES
            RUNCONTROL /nexus_data/runcontrol.dat
            SURFACE Network 1  /surface_file_01.dat'''

    runcontrol_contents = '''START 01/01/2019'''

    def test_write_out_new_simulator(self, mocker, fixture_for_osstat_pathlib):
        # Arrange
        expected_runcontrol_path = os.path.join('nexus_includes', 'runcontrol.dat')
        expected_surface_path = os.path.join('nexus_includes', 'surface_file_01.dat')
        expected_fcs_file_contents = (
            '\n'
            '            RUN_UNITS ENGLISH\n'
            '            DATEFORMAT DD/MM/YYYY\n'
            '            RECURRENT_FILES\n'
            f'            RUNCONTROL {expected_runcontrol_path}\n'
            f'            SURFACE Network 1  {expected_surface_path}')

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': self.fcs_file_contents,
                '/surface_file_01.dat': '',
                '/nexus_data/runcontrol.dat': self.runcontrol_contents}
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
        assert list_of_writes[0].args[0] == self.runcontrol_contents
        assert list_of_writes[1].args[0] == ''

        # assert we are writing to the correct file
        assert writing_mock_open.call_args_list[-1][0][0] == '/new_path/new_fcs_file.fcs'
        assert writing_mock_open.call_args_list[0][0][0] == expected_runcontrol_path
        assert writing_mock_open.call_args_list[1][0][0] == expected_surface_path


    def test_update_simulator_files(self, mocker, fixture_for_osstat_pathlib):
        # Arrange
        expected_surface_path = os.path.join('/path', 'fcs_file_surface_method_1.dat')

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': self.fcs_file_contents,
                '/surface_file_01.dat': 'surface_file_content',
                '/nexus_data/runcontrol.dat': self.runcontrol_contents}
                                            ).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        # make a mock for the write operation
        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)
        nexus_sim.model_files.surface_files[1]._file_modified_set(True)
        # Act
        nexus_sim.update_simulator_files()

        # Assert
        # Get all the calls to write() and check that the contents are what we expect
        list_of_writes = [call for call in writing_mock_open.mock_calls if 'call().write' in str(call)]
        assert len(list_of_writes) == 2
        assert list_of_writes[1].args[0] == self.fcs_file_contents
        assert list_of_writes[0].args[0] == 'surface_file_content'

        # assert we are writing to the correct file
        assert writing_mock_open.call_args_list[-1][0][0] == '/path/fcs_file.fcs'
        assert writing_mock_open.call_args_list[0][0][0] == '/surface_file_01.dat'


    def test_write_out_new_simulator_new_location(self, mocker, fixture_for_osstat_pathlib):
        # test the case where we have both a new file location and overwrite file and overwrite file and
        # preserve_file_names false
        # Arrange
        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': self.fcs_file_contents,
                '/surface_file_01.dat': 'surface_file_content',
                '/nexus_data/runcontrol.dat': self.runcontrol_contents}
                                            ).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        # make a mock for the write operation
        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)
        # pretend a file has been modified
        nexus_sim.model_files.surface_files[1]._file_modified_set(True)
        # Act
        nexus_sim.model_files.update_fcs_file(new_file_path='new_file_name.fcs', new_include_file_location=None,
                                              write_out_all_files=False, preserve_file_names=False,
                                              overwrite_include_files=True)
        # assert
        assert writing_mock_open.call_args_list[0][0][0] == '/surface_file_01.dat'
        assert writing_mock_open.call_args_list[1][0][0] == 'new_file_name.fcs'
