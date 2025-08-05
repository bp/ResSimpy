import os
from unittest.mock import MagicMock

import pytest

from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator

class TestWriteOutSimulator:
    fcs_file_contents = '''
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            RECURRENT_FILES
            RUNCONTROL /nexus_data/runcontrol.dat
            SURFACE Network 1  /surface_file_01.dat
            HYD Method 1 hyd_method.dat
            '''

    runcontrol_contents = '''START 01/01/2019'''

    def test_write_out_case(self, mocker):
        # Arrange
        expected_runcontrol_path = os.path.join('include_files', 'runcontrol_case_1.dat')
        expected_surface_path = os.path.join('include_files', 'surface_file_01_case_1.dat')
        expected_hyd_path = os.path.join('/path', 'hyd_method.dat')
        expected_fcs_file_contents = (
            '\n'
            '            RUN_UNITS ENGLISH\n'
            '            DATEFORMAT DD/MM/YYYY\n'
            '            RECURRENT_FILES\n'
            f'            RUNCONTROL {expected_runcontrol_path}\n'
            f'            SURFACE Network 1  {expected_surface_path}\n'
            f'            HYD Method 1 {expected_hyd_path}\n'
            '            ')

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': self.fcs_file_contents,
                '/surface_file_01.dat': '',
                '/nexus_data/runcontrol.dat': self.runcontrol_contents,
                os.path.join('/path', 'hyd_method.dat'): ''}
                                            ).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        # make a mock for the write operation
        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)

        # change all but the hydraulics file
        nexus_sim.model_files.surface_files[1]._file_modified_set(True)
        nexus_sim.model_files.runcontrol_file._file_modified_set(True)

        # Mock out the file exists
        file_exists_mock = MagicMock(side_effect=lambda x: False)
        mocker.patch('os.path.exists', file_exists_mock)

        # mock out makedirs
        makedirs_mock = MagicMock()
        mocker.patch('os.makedirs', makedirs_mock)

        # Act
        nexus_sim.write_out_case(new_file_path='/new_path/new_fcs_file.fcs', case_suffix='case_1')

        # Assert
        # Get all the calls to write() and check that the contents are what we expect
        list_of_writes = [call for call in writing_mock_open.mock_calls if 'call().write' in str(call)]
        assert list_of_writes[-1].args[0] == expected_fcs_file_contents
        assert list_of_writes[0].args[0] == self.runcontrol_contents
        assert list_of_writes[1].args[0] == ''
        assert len(list_of_writes) == 3

        # assert we are writing to the correct file
        assert writing_mock_open.call_args_list[2][0][0] == '/new_path/new_fcs_file.fcs'
        assert writing_mock_open.call_args_list[0][0][0] == expected_runcontrol_path
        assert writing_mock_open.call_args_list[1][0][0] == expected_surface_path


    def test_update_simulator_files(self, mocker):
        # Arrange
        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': self.fcs_file_contents,
                '/surface_file_01.dat': 'surface_file_content',
                '/nexus_data/runcontrol.dat': self.runcontrol_contents,
                os.path.join('/path', 'hyd_method.dat'): ''}
                                            ).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        # make a mock for the write operation
        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)
        nexus_sim.model_files.surface_files[1]._file_modified_set(True)
        nexus_sim.model_files.runcontrol_file._file_modified_set(True)

        # Act
        nexus_sim.update_simulator_files()

        # Assert
        # Get all the calls to write() and check that the contents are what we expect
        list_of_writes = [call for call in writing_mock_open.mock_calls if 'call().write' in str(call)]
        assert len(list_of_writes) == 2
        assert list_of_writes[1].args[0] == 'surface_file_content'
        assert list_of_writes[0].args[0] == self.runcontrol_contents

        # assert we are writing to the correct file
        assert writing_mock_open.call_args_list[0][0][0] == '/nexus_data/runcontrol.dat'
        assert writing_mock_open.call_args_list[1][0][0] == '/surface_file_01.dat'
