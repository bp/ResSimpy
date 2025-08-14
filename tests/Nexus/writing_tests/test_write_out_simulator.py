import os
from unittest.mock import MagicMock

import pytest

from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Nexus.DataModels.NexusOptions import NexusOptions
from ResSimpy.Nexus.DataModels.NexusReportingRequests import NexusOutputContents, NexusOutputRequest
from ResSimpy.Nexus.DataModels.nexus_grid_to_proc import GridToProc
from ResSimpy.Nexus.NexusReporting import NexusReporting
from ResSimpy.Nexus.runcontrol_operations import SimControls
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
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

        opts_obj = NexusOptions(file=None, model_unit_system=UnitSystem.ENGLISH)
        opts_obj.properties = {'DESC': ['Simulation Options'],
                               'UNIT_SYSTEM': UnitSystem.ENGLISH,
                               'PSTD': 14.7,
                               'TSTD': 60.0,
                               'RES_TEMP': 200.0,
                               'REGDATA': {
                                   'Injection_regions': pd.DataFrame({'NAME': ['Reg1', 'Reg2'],
                                                                      'NUMBER': [1, 2],
                                                                      'IBAT': [2, 2]
                                                                      }),
                                   'Fruit_regions': pd.DataFrame({'NUMBER': [10, 22, 33, 44],
                                                                  'NAME': ['Apple', 'Grape', 'Orange', 'Reg1']
                                                                  })}
                               }
        model.set_options(opts_obj)

        grid_to_proc = GridToProc(grid_to_proc_table=None, auto_distribute='GRIDBLOCKS')
        
        sim_controls = SimControls(model=model)
        sim_controls.set_grid_to_proc(grid_to_proc)
        times = ['01/05/2019', '01/04/2020', '01/12/2021', '01/10/2022']
        sim_controls.modify_times(content=times, operation='replace')

        model.set_sim_controls(sim_controls)

        # set the runcontrol
        new_nexus_reporting = NexusReporting(model=model, assume_loaded=True)
        new_nexus_reporting.add_array_output_request_to_memory(
            NexusOutputRequest(date='01/02/2020', output='RFT', output_type=OutputType.ARRAY,
                               output_frequency=FrequencyEnum.TNEXT, output_frequency_number=None))
        new_nexus_reporting.add_array_output_request_to_memory(
            NexusOutputRequest(date='01/02/2020', output='WELLS', output_type=OutputType.ARRAY,
                               output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None))
                
        new_nexus_reporting.add_array_output_contents_to_memory(
            NexusOutputContents(output_type=OutputType.SPREADSHEET, output='WELLS', date='01/01/2019',
                            output_contents=['DATE', 'TSNUM', 'QOP', 'QWP', 'COP', 'CWP', 'QWI', 'CWI', 'WCUT',
                                             'WPAVE', 'CGP', 'QGP', 'QLP', 'GOR', 'BHP', 'SAL']))
        
        new_nexus_reporting.add_array_output_contents_to_memory(
            NexusOutputContents(output_type=OutputType.SPREADSHEET, output='FIELD', date='01/01/2019',
                                           output_contents=['DATE', 'TSNUM', 'COP', 'CGP', 'CWP', 'CWI', 'QOP', 'QGP',
                                                            'QWP', 'QLP',
                                                            'QWI', 'WCUT', 'OREC', 'PAVT', 'PAVH']),)
        model.set_reporting_controls(new_nexus_reporting)

        
        # set the wells
        completions = [NexusCompletion(date='01/01/2020', i=20, j=30, k=40, well_radius=0.34, skin=2),
                       NexusCompletion(date='01/01/2020', i=21, j=31, k=41, well_radius=0.34, skin=2)]
        model.wells.add_well(name='well1', units=model.default_units, completions=completions, add_to_file=False)

        expected_hydraulics_path = os.path.join('/new_path/', 'nexus_files', 'new_model_hyd_1.dat')
        expected_surface_path = os.path.join('/new_path/', 'nexus_files', 'new_model_surface.dat')
        expected_options_path = os.path.join('/new_path/', 'nexus_files', 'new_model_options.dat')
        expected_runcontrol_path = os.path.join('/new_path/', 'nexus_files', 'new_model_runcontrol.dat')
        expected_wells_path = os.path.join('/new_path/', 'nexus_files', 'new_model_wells.dat')
        expected_fcs_path = os.path.join('/new_path/', 'new_model.fcs')
        
        expected_fcs_contents = f'''DESC Model created with ResSimpy
RUN_UNITS ENGLISH
DEFAULT_UNITS ENGLISH
DATEFORMAT MM/DD/YYYY

GRID_FILES
    OPTIONS {expected_options_path}

INITIALIZATION_FILES

ROCK_FILES

PVT_FILES

RECURRENT_FILES
    RUNCONTROL {expected_runcontrol_path}
    WELLS SET 1 {expected_wells_path}
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
        expected_options_content = """DESC Simulation Options
ENGLISH
PSTD 14.7
TSTD 60.0
RES_TEMP 200.0

REGDATA Injection_regions
NAME  NUMBER  IBAT
Reg1       1     2
Reg2       2     2
ENDREGDATA

REGDATA Fruit_regions
 NUMBER   NAME
     10  Apple
     22  Grape
     33 Orange
     44   Reg1
ENDREGDATA


GRIDTOPROC
AUTO GRIDBLOCKS
ENDGRIDTOPROC
"""

        expected_runcontrol_contents = """START 01/01/2019

SSOUT
    WELLS DATE TSNUM QOP QWP COP CWP QWI CWI WCUT WPAVE CGP QGP QLP GOR BHP SAL
    FIELD DATE TSNUM COP CGP CWP CWI QOP QGP QWP QLP QWI WCUT OREC PAVT PAVH
ENDSSOUT

TIME 01/05/2019

TIME 01/02/2020
OUTPUT
    RFT TNEXT
    WELLS YEARLY
ENDOUTPUT

TIME 01/04/2020

TIME 01/12/2021

TIME 01/10/2022
"""

        expected_wells_content = '''TIME 01/01/2020
WELLSPEC well1
IW JW L SKIN RADW
20 30 40 2 0.34
21 31 41 2 0.34

'''
        
        expected_writes = [(expected_surface_path, expected_surface_file_content),
                           (expected_hydraulics_path, expected_hydraulics_file_content),
                           (expected_options_path, expected_options_content),
                           (expected_runcontrol_path, expected_runcontrol_contents),
                           (expected_wells_path, expected_wells_content),
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
