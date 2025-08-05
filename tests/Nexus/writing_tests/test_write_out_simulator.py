import os
from unittest.mock import MagicMock

import pytest

from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator, check_file_read_write_is_correct
from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Enums.UnitsEnum import UnitSystem
import numpy as np
import pandas as pd


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
    
    def test_write_new_simulator(self, mocker):
        # Arrange
        model = NexusSimulator('new_model.fcs', assume_loaded=True, start_date='01/01/2019')

        new_hydraulics_props = {'DESC': ['Hydraulics Data'],
                                'UNIT_SYSTEM': UnitSystem.ENGLISH,
                                'QOIL': np.array([1.0, 1000., 3000.]),
                                'GOR': np.array([0.0, 0.5]),
                                'WCUT': np.array([0.0]),
                                'THP': np.array([100., 500.]),
                                'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 2, 2, 2],
                                                           'IWCUT': [1, 1, 1, 1, 1, 1],
                                                           'IQOIL': [1, 2, 3, 1, 2, 3],
                                                           'BHP0': [2470., 2478., 2493., 1860., 1881., 1947.],
                                                           'BHP1': [2545., 2548., 2569., 1990., 2002., 2039.0]
                                                           })
                                }
        new_hydraulics = NexusHydraulicsMethod(file=None, input_number=1, model_unit_system=model.default_units,
                                               properties=new_hydraulics_props)
        model.hydraulics.inputs[1] = new_hydraulics

        new_constraint = NexusConstraint(unit_system=model.default_units, date='01/01/2020', name='well1',
                                         max_surface_oil_rate=10240)

        model.network.constraints._add_to_memory({'well1': [new_constraint]})
        
        expected_hydraulics_path = os.path.join('/new_path/', 'nexus_files', 'new_model_hyd_1.dat')
        expected_surface_path = os.path.join('/new_path/', 'nexus_files', 'new_model_surface.dat')
        expected_fcs_path = os.path.join('/new_path/', 'new_model.fcs')
        
        expected_fcs_contents = f'''DESC Model created with ResSimpy
RUN_UNITS ENGLISH
DEFAULT_UNITS ENGLISH
DATEFORMAT MM/DD/YYYY

GRID_FILES

INITIALIZATION_FILES

ROCK_FILES

PVT_FILES

RECURRENT_FILES
    SURFACE NETWORK 1 {expected_surface_path}

NET_METHOD_FILES
    HYD METHOD 1 {expected_hydraulics_path}
'''

        expected_hydraulics_file_content = '''DESC Hydraulics Data
ENGLISH
QOIL 1.0 1000.0 3000.0
GOR 0.0 0.5
WCUT 0.0
THP 100.0 500.0
 IGOR  IWCUT  IQOIL   BHP0   BHP1
    1      1      1 2470.0 2545.0
    1      1      2 2478.0 2548.0
    1      1      3 2493.0 2569.0
    2      1      1 1860.0 1990.0
    2      1      2 1881.0 2002.0
    2      1      3 1947.0 2039.0


'''
        expected_surface_file_content = '''BLACKOIL

TIME 01/01/2020
CONSTRAINTS
well1 QOSMAX 10240
ENDCONSTRAINTS

'''
        expected_writes = [(expected_surface_path, expected_surface_file_content),
                           (expected_hydraulics_path, expected_hydraulics_file_content),
                           (expected_fcs_path, expected_fcs_contents),
                           ]
        
        # Mock out the file exists
        file_exists_mock = MagicMock(side_effect=lambda x: False)
        mocker.patch('os.path.exists', file_exists_mock)
        mocker.patch('os.makedirs', MagicMock())  # ensures no dirs are created

        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)
        
        # Act
        model.write_out_new_model(new_location='/new_path/', new_model_name='new_model', 
                                  new_include_file_location='nexus_files')
        
        # Assert
        # Check that the hydraulics file was written correctly
        check_file_read_write_is_correct(expected_file_writes=expected_writes, modifying_mock_open=writing_mock_open)
