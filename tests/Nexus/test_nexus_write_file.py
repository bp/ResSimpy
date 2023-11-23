from unittest.mock import Mock, MagicMock
import pytest
import numpy as np
import pandas as pd
from ResSimpy.Enums.UnitsEnum import SUnits, TemperatureUnits, UnitSystem


from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.Nexus.DataModels.NexusEquilMethod import NexusEquilMethod
from ResSimpy.Nexus.DataModels.NexusGasliftMethod import NexusGasliftMethod
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.Nexus.DataModels.NexusRockMethod import NexusRockMethod
from ResSimpy.Nexus.DataModels.NexusSeparatorMethod import NexusSeparatorMethod
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod, NexusWaterParams
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.utility_for_tests import check_file_read_write_is_correct
from tests.multifile_mocker import mock_multiple_files


@pytest.mark.parametrize('fcs_file_contents, wells_file, expected_result', [
('''DATEFORMAT DD/MM/YYYY
WelLS sEt 1 /my/wellspec/file.dat''',

''' ! wells file:
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
''' ! wells file:
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
''')

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
    mock_nexus_sim.start_date = start_date
    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.5, 'date_format': DateFormat.DD_MM_YYYY}

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    mock_nexus_sim._wells.add_completion(well_name='well1', completion_properties=add_perf_dict,
                                        preserve_previous_completions=True)
    mock_nexus_sim.model_files.well_files[1].write_to_file(overwrite_file=True)
    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat')


@pytest.mark.parametrize('fcs_file_contents, wells_file, expected_result, expected_removed_completion_line, '
'expected_obj_locations', [
('''DATEFORMAT DD/MM/YYYY
WelLS sEt 1 /my/wellspec/file.dat''',

''' ! wells file:
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
''' ! wells file:
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
10, [[4], [9], [14]]),


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
9, [[4], [10]]),
], ids=['basic_test', 'only 1 completion to remove'] )
def test_remove_completion_write_to_file(mocker, fcs_file_contents, wells_file, expected_result,
        expected_removed_completion_line, expected_obj_locations, ):
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
    mock_nexus_sim._wells._load() # Manually call load_wells to simulate loading in wells before we change the open mock.
    mock_nexus_sim.start_date = start_date
    remove_perf_dict = {'date': remove_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 4.2}
    well_files = mock_nexus_sim.model_files.well_files[1]
    object_locations = well_files.object_locations
    object_locations_minus_completion = {k: v for k, v in object_locations.items() if v !=
                                         [expected_removed_completion_line]}
    object_locations_minus_completion = dict(zip(object_locations_minus_completion, expected_obj_locations))

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    mock_nexus_sim._wells.remove_completion(well_name='well1', completion_properties=remove_perf_dict)
    result_object_ids = mock_nexus_sim.model_files.well_files[1].object_locations
    mock_nexus_sim.model_files.well_files[1].write_to_file(overwrite_file=True)
    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat',
                                     number_of_writes=1)

    assert result_object_ids == object_locations_minus_completion

@pytest.mark.parametrize('fcs_file_contents, wells_file, expected_result', [
('''DATEFORMAT DD/MM/YYYY
WelLS sEt 1 /my/wellspec/file.dat''',

''' ! wells file:
TIME 01/01/2020
WELLSPEC well1Dev
iw jw l radw
1  2  3 4.5

TIME 01/03/2020
WELLSPEC well1Dev
iw jw l radw
1  2  3 4.5
4  5  6 4.2

TIME 01/05/2020
WELLSPEC well1>
Dev
iw jw l radw
1  2  >
3 4.5
''',
''' ! wells file:
TIME 01/01/2020
WELLSPEC well1Dev
iw jw l radw
1  2  3 4.5

TIME 01/03/2020
WELLSPEC well1Dev
iw jw l radw
1  2  3 4.5
4 8 6 10.2

TIME 01/05/2020
WELLSPEC well1Dev
iw jw l radw
1  2  3 4.5
''')

])
def test_modify_completion_write_to_file(mocker, fcs_file_contents, wells_file, expected_result):
    # Arrange
    start_date = '01/01/2020'
    modify_perf_date = '01/03/2020'
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
    mock_nexus_sim.start_date = start_date
    modify_perf_target = {'date': modify_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 4.2, 'date_format': DateFormat.DD_MM_YYYY}
    modify_perf_new_properties = {'date': modify_perf_date, 'j': 8, 'well_radius': 10.2, 'date_format': DateFormat.DD_MM_YYYY}

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    mock_nexus_sim._wells.modify_completion(well_name='well1Dev', properties_to_modify=modify_perf_new_properties,
                                           completion_to_change=modify_perf_target )
    mock_nexus_sim.model_files.well_files[1].write_to_file(overwrite_file=True)
    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat',
                                     number_of_writes=1,
                                     )

@pytest.mark.parametrize('folder_exists, expected_number_calls', [
    (True, 0),
    (False, 1)], ids=['folder_exists', 'folder_does_not_exist'])
def test_write_file_makedirs(mocker, folder_exists, expected_number_calls, ):
    # Arrange
    file_contents = 'Contents of the file to write'
    file_location = '/path/to/file.dat'
    new_file_location = '/new/path/to/file.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_location: file_contents,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    file = NexusFile(file_location, file_content_as_list=[file_contents])
    file._file_modified_set(True)
    # mock out the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # mock out folder exists
    folder_exists_mock = MagicMock(side_effect=lambda x: folder_exists)
    mocker.patch('os.path.exists', folder_exists_mock)

    # mock out the makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)

    # Act
    file.write_to_file(new_file_location, overwrite_file=True)

    # Assert
    # check we are writing to the correct file
    # check we are creating the correct folder
    assert len(makedirs_mock.call_args_list) == expected_number_calls
    if expected_number_calls == 1:
        assert makedirs_mock.call_args_list[0][0][0] == '/new/path/to'
    assert writing_mock_open.call_args_list[0][0][0] == new_file_location


def test_nexus_pvt_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'API': 30.0, 'SPECG': 0.6, 'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                                                                         'and this is second line of description']}
    dataobj = NexusPVTMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH, pvt_type='BLACKOIL',
                             properties=properties)
    expected_result = '''DESC This is first line of description
DESC and this is second line of description
BLACKOIL API 30.0 SPECG 0.6
ENGLISH
'''

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_aquifer_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                  'FETKOVICH': '', 'LABEL': 'FETTY_V',
                  'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM, 'IWATER': 2, 'SALINITY': 300000,
                  'LINFAC': 2.5, 'RADIAL': '', 'VISC': 1.1, 'CT': 1e-6, 'H': 50, 'RO': 5000,
                  'S': 0.3333, 'RE': 10000, 'NOFLOW': '', 'WAQI': 5e8, 'PAQI': 4800, 'DAQI': 9600
                  }
    dataobj = NexusAquiferMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                 properties=properties)
    expected_result = '''DESC This is first line of description
DESC and this is second line of description
FETKOVICH
LABEL FETTY_V
ENGLISH
SUNITS PPM
IWATER 2
SALINITY 300000
LINFAC 2.5
RADIAL
VISC 1.1
CT 1e-06
H 50
RO 5000
S 0.3333
RE 10000
NOFLOW
WAQI 500000000.0
PAQI 4800
DAQI 9600

'''

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_equil_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600
                  }
    dataobj = NexusEquilMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                               properties=properties)
    expected_result = '''DESC This is first line of description
DESC and this is second line of description
ENGLISH
PINIT 3600
DINIT 9035
GOC 8800
WOC 9950
PSAT 3600

'''

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_gaslift_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['Optimal Gaslift Data'],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'WCUT': '0.0 0.2 0.4',
                  'QLIQ': '1000 3500',
                  'PRESSURE': '2500 4500',
                  'GL_TABLE': pd.DataFrame({'IPRES': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                            'IWCUT': [1, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, 3],
                                            'IQLIQ': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                                            'GLR': [0.8, 0.7, 0.9, 0.8, 1,   0.9,
                                                    0.5, 0.4, 0.6, 0.5, 0.7, 0.6]
                                            })}
    dataobj = NexusGasliftMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                 properties=properties)
    expected_result = """DESC Optimal Gaslift Data
ENGLISH
WCUT 0.0 0.2 0.4
QLIQ 1000 3500
PRESSURE 2500 4500
""" + properties['GL_TABLE'].to_string(na_rep='', index=False) + '\n\n'

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_hydraulics_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['Hydraulics Data'],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'QOIL': '1.0 1000. 3000.',
                  'GOR': '0.0 0.5',
                  'WCUT': '0.0',
                  'ALQ': '0.0 50.0',
                  'ALQ_PARAM': 'GASRATE',
                  'THP': '100. 500. 900. 1400. 2000.',
                  'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                             'IWCUT': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                             'IALQ': [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
                                             'IQOIL': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                                             'BHP0': [2470., 2478., 2493., 2535., 2541., 2555.,
                                                      1860., 1881., 1947., 1990., 2004., 2033.],
                                             'BHP1': [2545., 2548., 2569., 2600., 2608., 2631.,
                                                      1990., 2002., 2039., 2100., 2109., 2130.],
                                             'BHP2': [2600., 2613., 2638., 2650., 2673., 2703.,
                                                      2090., 2101., 2131., 2190., 2206., 2224.],
                                             'BHP3': [2820., 2824., 2870., 2852., 2884., 2931.,
                                                      2435., 2438., 2448., 2530., 2537., 2548.],
                                             'BHP4': [3070., 3081., 3138., 3130., 3141., 3197.,
                                                      2830., 2836., 2848., 2916., 2926., 2946.]
                                            }),
                  'DATGRAD': 'GRAD',
                  'WATINJ': {'GRAD': 0.433, 'VISC': 0.7, 'LENGTH': 9000,
                             'ROUGHNESS': 1e-5, 'DZ': 8000, 'DIAM': 7},
                  'NOCHK': ''}
    dataobj = NexusHydraulicsMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                    properties=properties)
    expected_result = """DESC Hydraulics Data
ENGLISH
QOIL 1.0 1000. 3000.
GOR 0.0 0.5
WCUT 0.0
ALQ GASRATE 0.0 50.0
THP 100. 500. 900. 1400. 2000.
""" + properties['HYD_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
DATGRAD GRAD
WATINJ
    GRAD 0.433
    VISC 0.7
    LENGTH 9000
    ROUGHNESS 1e-05
    DZ 8000
    DIAM 7
NOCHK

"""

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_valve_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                  'DP_RATE': 'QALL',
                  'VALVE': pd.DataFrame({'SETTING': [1, 2, 3, 4, 5],
                                         'VC': ['NOFLOW', '5.4', '0.8', '0.3', '0.01']
                                         })}
    dataobj = NexusValveMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                               properties=properties)
    expected_result = """DESC This is first line of description
DESC and this is second line of description
VALVE QALL
""" + properties['VALVE'].to_string(na_rep='', index=False) + \
"""
ENDVALVE

"""

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_relperm_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    hysteresis_params = {'KRG': {'LINEAR': {'MAXTRAP': 0.2, 'NOMOD': ''}},
                         'KRW': 'USER',
                         'KROW': {'KILLOUGH': {'MAXTRAP': 0.2, 'EXP': 1.1}},
                         'PCWO': {'MAXSW': 0.8, 'ETA': 0.15, 'TRAPSCALE': ''},
                         'PCGO': {},
                         'WAG': {'LAND': 1.1, 'NOOILHYS': ''},
                         'TOLREV': 0.05, 'NOCHK_HYS': ''
                         }
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                  'WOTABLE': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                           'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                           'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                           'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                           }),
                  'GOTABLE': pd.DataFrame({'SG': [0, 0.05, 0.2, 0.4, 0.55, 0.65, 0.8],
                                           'KROG': [1, 0.729, 0.216, 0.008, 0, 0, 0],
                                           'KRG': [0, 0.0039, 0.0625, 0.25, 0.4727, 0.6602, 1],
                                           'PCGO': [0., np.nan, np.nan, 1., np.nan, np.nan, 5.0]
                                           }),
                  'WOTABLE_IMB': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                               'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                               'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                               'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                               }),
                  'PRSTAB': pd.DataFrame({'SWL': [0.1, 0.15],
                                          'SWR': [0.2, 0.25],
                                          'SWRO': [0.6, 0.7],
                                          'SWU': [1., 0.9],
                                          'KRO_SWL': [0.55, 0.65]
                                          }),
                  'STONE1': '', 'SOMOPT2': 0.05, 'STONE2_WAT': '', 'LOW_SAL': '', 'SCALING': 'TWOPOINT', 'VEGO_PC': '',
                  'VEWO': '', 'DRELPM': 0.9, 'IFT': '', 'TENTHR': 0.005, 'XEX': 0.3, 'TENI': 0.005,
                  'FREEZE_PCGO': '', 'FREEZE_PCWO': '', 'DERIVATIVES': 'NUMERICAL',
                  'NONDARCY_GAS': {},
                  'NONDARCY_OIL': {'BETA0': 0.001, 'BETA1': -0.5, 'BETA2': -5, 'BETA3': -0.5, 'BETA4': -3, 'BETA5': 4.4},
                  'RECONSTRUCT': {'NSGDIM': 101, 'NSWDIM': 101}, 'VIP_RELPM': ''
                  }
    dataobj = NexusRelPermMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                 properties=properties, hysteresis_params=hysteresis_params)
    expected_result = """DESC This is first line of description
DESC and this is second line of description
WOTABLE LOW_SAL
""" + properties['WOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
GOTABLE
""" + properties['GOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WOTABLE_IMB
""" + properties['WOTABLE_IMB'].to_string(na_rep='', index=False) + '\n' + \
"""
PRSTAB
""" + properties['PRSTAB'].to_string(na_rep='', index=False) + '\n' + \
"""
STONE1 SOMOPT2 0.05
STONE2_WAT
SCALING TWOPOINT
VEGO_PC
VEWO
DRELPM 0.9
IFT
TENTHR 0.005
XEX 0.3
TENI 0.005
FREEZE_PCGO
FREEZE_PCWO
DERIVATIVES NUMERICAL
NONDARCY_GAS
ENDNONDARCY_GAS
NONDARCY_OIL
    BETA0 0.001
    BETA1 -0.5
    BETA2 -5
    BETA3 -0.5
    BETA4 -3
    BETA5 4.4
ENDNONDARCY_OIL
RECONSTRUCT
    NSGDIM 101
    NSWDIM 101
VIP_RELPM
HYSTERESIS KRG LINEAR MAXTRAP 0.2 NOMOD
           KRW USER
           KROW KILLOUGH MAXTRAP 0.2 EXP 1.1
           PCWO MAXSW 0.8 ETA 0.15 TRAPSCALE
           PCGO
           WAG LAND 1.1 NOOILHYS
           TOLREV 0.05
           NOCHK_HYS
"""

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_rock_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'UNIT_SYSTEM': UnitSystem.ENGLISH, 
                  'CMT': pd.DataFrame({'P': [1500, 2000, 3500],
                                       'PVMULT': [0.76, 0.81, 0.85]
                                       }),
                  'REVERSIBLE': 'CMTONLY', 'TOLREV_P': 2.5,
                  'WIRCT': {'0.10': pd.DataFrame({'DSW': [0.0, 0.02, 0.12, 0.22, 0.32, 0.42],
                                                  'PVMULT': [1., 1., 0.94, 0.88, 0.82, 0.76],
                                                  'TAMULT': [1., 1., 0.40, 0.25, 0.09, 0.09]
                                                  }),
                            '0.50': pd.DataFrame({'DSW': [0.02, 0.12, 0.35],
                                                  'TAMULT': [1., 0.9, 0.8]
                                                  })
                            },
                  'IRREVERSIBLE': 'WIRCTONLY', 'TOLREV_SW': 0.01
                  }
    dataobj = NexusRockMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                              properties=properties)
    expected_result = """ENGLISH
CMT
""" + properties['CMT'].to_string(na_rep='', index=False) + '\n' + \
"""
REVERSIBLE CMTONLY
TOLREV_P 2.5
WIRCT
SWINIT 0.10
""" + properties['WIRCT']['0.10'].to_string(na_rep='', index=False) + '\n' + \
"""
SWINIT 0.50
""" + properties['WIRCT']['0.50'].to_string(na_rep='', index=False) + '\n' + \
"""
IRREVERSIBLE WIRCTONLY
TOLREV_SW 0.01
"""

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_separator_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['This is first line of description',
                           'and this is second line of description'
                           ],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'TEMP_UNIT': TemperatureUnits.FAHR,
                  'SEPARATOR_TABLE': pd.DataFrame({'STAGE': [1, 2],
                                                   'METHOD': [1, 2],
                                                   'PRES': [500.0, 14.7],
                                                   'TEMP': [150.0, 60.0],
                                                   'IDL1': ['2', 'OIL'],
                                                   'IDL2': [np.nan, np.nan],  
                                                   'IDV1': ['GAS', 'VENT'],
                                                   'IDV2': [np.nan, np.nan],
                                                   'FDL1': [1., 1.],
                                                   'FDV1': [1., 1.]
                                                   }),
                  'WATERMETHOD': 1}
    dataobj = NexusSeparatorMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                   properties=properties, separator_type='EOS')
    expected_result = """DESC This is first line of description
DESC and this is second line of description
ENGLISH
FAHR
""" + properties['SEPARATOR_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WATERMETHOD 1
"""

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')


def test_nexus_water_write_to_file(mocker):
    # Arrange
    pfile = NexusFile(location='/my/orig_prop/file.dat')
    properties = {'DESC': ['This is first line of description',
                           'and this is second line of description'],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH}
    water_params1 = NexusWaterParams(water_density=62.4, water_compressibility=3.4,
                                     water_formation_volume_factor=1.04, water_viscosity=0.7,
                                     water_viscosity_compressibility=1e-3
                                     )
    dataobj = NexusWaterMethod(file=pfile, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                               properties=properties, reference_pressure=3600.0,
                               parameters=[water_params1]
                               )
    expected_result = """DESC This is first line of description
DESC and this is second line of description
PREF 3600.0
ENGLISH
DENW 62.4
CW 3.4
BW 1.04
VISW 0.7
CVW 0.001
"""

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    dataobj.write_to_file(new_file_location='/my/prop/file.dat')

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/prop/file.dat')
