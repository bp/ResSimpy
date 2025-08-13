import pandas as pd
import pytest
from pytest_mock import MockerFixture

from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.nexus_grid_to_proc import GridToProc
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusReporting import NexusReporting
from ResSimpy.Nexus.DataModels.NexusReportingRequests import NexusOutputRequest, NexusOutputContents
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.multifile_mocker import mock_multiple_files

from tests.Nexus.nexus_simulator.test_nexus_simulator import mock_multiple_opens
from ResSimpy.Nexus.runcontrol_operations import SimControls
from tests.utility_for_tests import get_fake_nexus_simulator


@pytest.mark.parametrize(
    "date_format,expected_date_format,run_control_contents,include_file_contents,expected_times", [
        # USA date format, no times in run control
        ("MM/DD/YYYY", DateFormat.MM_DD_YYYY, "START 01/01/1980\nINCLUDE     path/to/include\nWELLS\nTIMES PERFS\n",
         "TIME 0.1\nTIME 10/15/1983\n "
         "invalidtime", ['0.1', '10/15/1983']),
        # Non-USA date format, times in run control and include files
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY,
         "START 01/01/1980\nINCLUDE  \n! Comment \n   path/to/include\nTIME 01/01/1981\nTIME 0.1",
         "TIME 0.3\nTIME 15/10/1983\nTIME 1503.1\nTIME 15/12/1996",
         ['0.1', '0.3', '01/01/1981', '15/10/1983', '1503.1', '15/12/1996']),
        # Non-USA date format, times in include file only
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE  !test comment\n   path/to/include",
         "TIME 0.1\nTIME 15/10/1983\n invalidtime\nTIME 1503.1\nTIME 15/12/2021",
         ['0.1', '15/10/1983', '1503.1', '15/12/2021']),
        # Non-USA date format, times in run control only, but include file declared
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY,
         "START 01/01/1980\nINCLUDE     path/to/include\nTIME 19/08/2025\nTIME 0.1\nTIME 50000",
         "",
         ['0.1', '19/08/2025', '50000']),
        # Non-USA date format, times with times as well as dates
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE  !test comment\n   path/to/include",
         "TIME 0.1\nTIME 15/10/1983(01:30:00)\n invalidtime\nTIME 15/10/1983(18:30:12)\nTIME 1503.1\n"
         "TIME 15/12/2021",
         ['0.1', '15/10/1983(01:30:00)', '15/10/1983(18:30:12)', '1503.1', '15/12/2021']),
        # Non-USA date format, times with times as well as dates
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE  !test comment\n   path/to/include",
         "TIME 0.1\nTIME 15/10/1983(01:30:00)\n invalidtime\nTIME 15/10/1983(18:30:12)\nTIME 15/10/1983(18:30:11)\n"
         "TIME 1503.1\nTIME 15/12/2021\nTIME 15/12/2021(00:00:01)",
         ['0.1', '15/10/1983(01:30:00)', '15/10/1983(18:30:11)', '15/10/1983(18:30:12)', '1503.1', '15/12/2021',
          '15/12/2021(00:00:01)']),
    ], ids=['USA date format', 'Non-USA date format', 'times in include', 'times in runcontrol only',
            'times and dates', 'times and dates 2'])
def test_load_run_control_file_times_in_include_file(mocker, date_format, expected_date_format,
                                                     run_control_contents, include_file_contents, expected_times):
    """Getting times from an external include file"""
    # Arrange
    fcs_file_name = 'testpath1/test.fcs'
    fcs_file = f"RUNCONTROL /path/run_control\nDATEFORMAT {date_format}\n"
    run_control_file = run_control_contents
    include_file = include_file_contents

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, run_control_file, include_file).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin=fcs_file_name)
    result_times = simulation._sim_controls.times

    # Assert
    assert result_times == expected_times
    assert simulation.date_format is expected_date_format


@pytest.mark.parametrize(
    "date_format,run_control_contents,include_file_contents", [
        ("MM/DD/YYYY", "START 01/01/1980\nINCLUDE     path/to/include", "TIME 0.1\nTIME 15/10/1983\ntime "
                                                                        "invalidtime"),
        ("DD/MM/YYYY", "START 01/14/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
         "TIME 0.3\nTIME 15/10/1983\ntime invalidtime\nTIME 1503.1\nTIME 15/12/1996"),
        ("DD/MM/YYYY", "START 01/01/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 15/10/1983\ntime invalidtime\nTIME 1503.1\nTIME 15/12e/2021"),
        ("DD/MM/YYYY", "START 01/01/1980\nINCLUDE     path/to/include\nTIME 19/08/2025\nTIME 0.1\nTIME 5p0000",
         ""),
    ])
def test_load_run_control_invalid_times(mocker, date_format, run_control_contents, include_file_contents):
    """Included files contain dates in invalid format, raise error when attempting to re-write them."""
    # Arrange
    fcs_file_name = 'testpath1/test.fcs'
    fcs_file = f"RUNCONTROL /path/run_control\nDATEFORMAT {date_format}\n"
    run_control_file = run_control_contents
    include_file = include_file_contents

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, run_control_file, include_file).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    with pytest.raises(ValueError):
        NexusSimulator(origin=fcs_file_name, write_times=True)


@pytest.mark.parametrize(
    "date_format,expected_date_format,run_control_contents,include_file_contents,new_times,operation,"
    "expected_times",
    [
        # USA date format, replace
        ("MM/DD/YYYY", DateFormat.MM_DD_YYYY, "START 01/01/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 10/15/1983\n ",
         ['01/01/2001', '12/15/2000', '08/08/2008', '0.1', '08/07/2008'], 'REPLACE',
         ['0.1', '12/15/2000', '01/01/2001', '08/07/2008', '08/08/2008']),
        # Non-USA date format, merge
        (
                "DD/MM/YYYY", DateFormat.DD_MM_YYYY,
                "START 01/01/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
                "TIME 0.3\nTIME 15/10/1983\n invalidtime\nTIME 1503.1\nTIME 15/12/1998",
                ['01/01/2001', '15/12/2000', '08/08/1998',
                 '0.1', '08/07/2008', '01/02/1981'], 'merge',
                ['0.1', '0.3', '01/01/1981', '01/02/1981', '15/10/1983', '1503.1', '08/08/1998', '15/12/1998',
                 '15/12/2000',
                 '01/01/2001', '08/07/2008']),
        # Non-USA date format, replace
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 15/10/1983\ntimeer invalidtime\nTIME 1503.1\nTIME 15/12/2021",
         ['01/01/2001', '15/12/2000', '08/08/1998', '0.1',
          '08/07/2025', '01/02/1981'], 'replace',
         ['0.1', '01/02/1981', '08/08/1998', '15/12/2000', '01/01/2001', '08/07/2025']),
        # Non-USA date format, reset
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 15/10/1983\ntimer invalidtime\nTIME 1503.1\nTIME 15/12/2021",
         ['01/01/2001', '15/12/2000', '08/08/1998',
          '0.1', '08/07/2025', '01/02/1981'], 'reset',
         []),
        # Non-USA date format, remove
        (
                "DD/MM/YYYY", DateFormat.DD_MM_YYYY,
                "START 01/01/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
                "TIME 0.3\nTIME 15/10/1983\nytime invalidtime\nTIME 1503.1\nTIME 15/12/1996\nTIME 01/01/2000\nSTOP\n",
                ['0.3', '01/01/1981', '01/01/2000', '08/05/2015'], 'REMOVE',
                ['15/10/1983', '1503.1', '15/12/1996']),
        # Non-USA date format, replace, duplicate in run control
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include",
         "TIME 01/01/1980\nTIME 15/10/1983\nxtime invalidtime\nTIME 1503.1\nTIME 15/12/2021",
         ['01/01/2001', '15/12/2000', '08/08/1998', '0.1',
          '08/07/2025', '01/02/1981'], 'replace',
         ['0.1', '01/02/1981', '08/08/1998', '15/12/2000', '01/01/2001', '08/07/2025']),
    ])
def test_modify_times(mocker, date_format, expected_date_format,
                      run_control_contents, include_file_contents, new_times, operation, expected_times):
    """Testing the modify times code. Checks that the code correctly orders times and removes duplicates (checks both
    US and Rest of the world dates) """
    # Arrange
    fcs_file_name = 'testpath1/test.fcs'
    fcs_file = f"RUNCONTROL /path/run_control\nDATEFORMAT {date_format}\n"
    run_control_file = run_control_contents
    include_file = include_file_contents

    run_control_mock = mocker.mock_open(read_data=run_control_contents)
    include_file_mock = mocker.mock_open(read_data=include_file_contents)

    # OperationEnum parameter required here to handle all calls to open
    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(mocker, filename, fcs_file, run_control_file, include_file,
                                        run_control_mock, include_file_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(
        origin=fcs_file_name, destination="test_new_destination", write_times=True)
    simulation.modify(section="RUNCONTROL", keyword="TIME",
                      content=new_times, operation=operation)
    result_times = simulation.get_content(section="RUNCONTROL", keyword="TIME")

    # Assert
    assert result_times == expected_times
    assert simulation.date_format is expected_date_format

    # Check that the include file has been cleared
    include_string = str(include_file_mock().write.call_args_list[0])
    assert 'TIME' not in include_string

    # Check the resulting Run control contains all the expected times and no others
    file_string = str(run_control_mock().write.call_args_list[1])
    assert (file_string.endswith("STOP\\n')"))
    for time in expected_times:
        expected_string = f"TIME {time}"
        assert expected_string in file_string
        file_string = file_string.replace(expected_string, "", 1)

    assert ('TIME' not in file_string)
    run_control_mock().write.assert_called()


@pytest.mark.parametrize(
    "date_format,expected_date_format,run_control_contents,include_file_contents,new_times,operation,"
    "expected_times",
    [
        # USA date format, replace
        ("MM/DD/YYYY", DateFormat.MM_DD_YYYY, "START 12/01/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 10/15/1983\ntimee ",
         ['01/01/2001', '12/15/2000', '08/08/2008', '0.1',
          '01/12/1980', '08/07/2008'], 'REPLACE',
         ['0.1', '10/15/1983']),
        # Non-USA date format, merge
        (
                "DD/MM/YYYY", DateFormat.DD_MM_YYYY,
                "START 01/01/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
                "TIME 0.3\nTIME 15/10/1983\n invalidtime\nTIME 1503.1\nTIME 15/12/1998",
                ['01/01/2001', '15/12/2000', '08/08/1998',
                 '0.1', '08/07/2008', '01/02/1979'], 'merge',
                ['0.1', '0.3', '01/01/1981', '15/10/1983', '1503.1', '15/12/1998']),
        # Non-USA date format, replace
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 15/10/1983\ntimee invalidtime\nTIME 1503.1\nTIME 15/12/2021",
         ['01/01/2001', '15/12/2000', '08/08/1998', '0.1',
          '08/07/1970', '01/02/1981'], 'replace',
         ['0.1', '15/10/1983', '1503.1', '15/12/2021']),
        # Non-USA date format, reset
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/12/1980\nINCLUDE     path/to/include",
         "TIME 0.1\nTIME 15/10/1983\nttime invalidtime\nTIME 1503.1\nTIME 15/12/2021\nSTOP\n",
         ['01/01/2001', '15/12/2000', '08/08/1998',
          '0.1', '12/01/1980', '01/02/1981'], 'reset',
         ['0.1', '15/10/1983', '1503.1', '15/12/2021']),
        # Non-USA date format, remove
        (
                "DD/MM/YYYY", DateFormat.DD_MM_YYYY,
                "START 01/01/1985\nINCLUDE     path/to/include\nTIME 01/01/1986\nTIME 0.1",
                "TIME 0.3\nTIME 15/10/1993\n invalidtime\nTIME 1503.1\nTIME 15/12/1996\nTIME 01/01/2000",
                ['0.3', '01/01/1981', '01/01/2000', '08/08/1981'], 'REMOVE',
                ['0.1', '0.3', '01/01/1986', '1503.1', '15/10/1993', '15/12/1996', '01/01/2000']),
    ])
def test_modify_times_invalid_date(mocker, date_format, expected_date_format,
                                   run_control_contents, include_file_contents, new_times, operation, expected_times):
    """Checks that the code doesn't allow times to be entered before the start date, and leaves the times array
     unchanged.  Also Checks that the code outputs new times to the run control file correctly, and clears the include
     file """
    # Arrange
    fcs_file_name = 'testpath1/test.fcs'
    fcs_file = f"RUNCONTROL /path/run_control\nDATEFORMAT {date_format}\n"
    run_control_file = run_control_contents
    include_file = include_file_contents

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, run_control_file, include_file).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin=fcs_file_name, write_times=True)
    with pytest.raises(ValueError):
        simulation.modify(section="RUNCONTROL", keyword="TIME",
                          content=new_times, operation=operation)
    result_times = simulation.get_content(section="RUNCONTROL", keyword="TIME")

    # Assert
    assert result_times == expected_times
    assert simulation.date_format is expected_date_format


@pytest.mark.skip('Functionality for writing to runcontrols does not work and is currently not requested by the user.')
@pytest.mark.parametrize(
    "fcs_content, run_control_contents, inc_file_contents, expected_times, expected_output", [
        ("RUNCONTROL /path/run_control\nDATEFORMAT DD/MM/YYYY\n",
         "START 01/01/1980\nINCLUDE  \n! Comment \n   include.inc\n",
         "SPREADSHEET\n\tFIELD TIMES\n\tWELLSS TIMES\nENDSPREADSHEET\n"
         "OUTPUT TARGETS TIMES\n\tMAPS TIMES\nENDOUTPUT\nTIME 0.3\n",
         ['0.3'],
         "RUNCONTROL /path/run_control\nDATEFORMAT DD/MM/YYYY\n"
         "START 01/01/1980\nINCLUDE  \n! Comment \n   include.inc\n"
         "SPREADSHEET\n\tFIELD TIMES\n\tWELLSS TIMES\nENDSPREADSHEET\n"
         "OUTPUT TARGETS TIMES\n\tMAPS TIMES\nENDOUTPUT\nTIME 0.3\n\nSTOP\n"),

        ("RUNCONTROL /path/run_control\nDATEFORMAT DD/MM/YYYY\n",
         "START 01/01/1980\nINCLUDE  \n! Comment \n   include.inc\n",
         "SPREADSHEET\n\tFIELD TIMES\n\tWELLSS TIMES\nENDSPREADSHEET\n"
         "OUTPUT TARGETS TIMES\n\tMAPS TIMES\nENDOUTPUT\nTIME 0.3\n\nTIME 01/01/2001\n\tTIME 15/10/2020\n",
         ['0.3', '01/01/2001', '15/10/2020'],
         "RUNCONTROL /path/run_control\nDATEFORMAT DD/MM/YYYY\n"
         "START 01/01/1980\nINCLUDE  \n! Comment \n   include.inc\n"
         "SPREADSHEET\n\tFIELD TIMES\n\tWELLSS TIMES\nENDSPREADSHEET\n"
         "OUTPUT TARGETS TIMES\n\tMAPS TIMES\nENDOUTPUT\nTIME 0.3\n\nTIME 01/01/2001\n\nTIME 15/10/2020\n\nSTOP\n"),

    ])
def test_load_run_control_file_write_times_to_run_control(mocker, fcs_content, run_control_contents, inc_file_contents,
                                                          expected_times, expected_output):
    """Getting times from an external include file"""
    # Arrange
    fcs_file_name = 'testpath1/test.fcs'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename,
                                        potential_file_dict={'testpath1/test.fcs': fcs_content,
                                                             '/path/run_control': run_control_contents,
                                                             'include.inc': inc_file_contents}).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin=fcs_file_name, )
    result_times = simulation.get_content(section="RUNCONTROL", keyword="TIME")

    # Assert
    # TODO REASSERT THESE CALLS
    # .assert_any_call('/path/run_control', 'w')
    # .return_value.write.assert_any_call(expected_output)
    assert result_times == expected_times


def test_runcontrol_no_start_time(mocker):
    # Arrange
    fcs_data = '''RUN_UNITS     ENGLISH
    DEFAULT_UNITS ENGLISH
    DATEFORMAT    DD/MM/YYYY
    RUNCONTROL            runcontrol.dat     '''

    runcontrol_data = '''
    !
    OUTPUT MAPS TNEXT			
    ENDOUTPUT	
    TIME 01/01/2016																			
    TIME 01/02/2016												
    TIME 01/03/2016												!	
    STOP
    '''

    fcs_file_name = 'test.fcs'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename,
                                        potential_file_dict={'test.fcs': fcs_data,
                                                             r'runcontrol.dat': runcontrol_data,
                                                             }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    expected_result = '01/01/2016'
    # Act
    simulation = NexusSimulator(origin=fcs_file_name, )
    result = simulation.start_date

    # Assert
    assert result == expected_result


def test_load_grid_to_proc():
    # Arrange
    options_file_content = '''
    data to ignore
    another line
    15 15 MATRIX
    GRID
    1 1 1 
    GRIDTOPROC ! lp
GRID PROCESS PORTYPE
1 1 MATRIX
2 2 MATRIX
3 3 MATRIX
4 4 MATRIX
1 1 FRAC
2 2 FRAC
3 3 FRAC
4 4 FRAC
ENDGRIDTOPROC
! stuff to exclude:
5 5 FRAC
'''
    options_file_content = options_file_content.splitlines(keepends=True)
    expected_result = GridToProc(grid_to_proc_table=pd.DataFrame({
        'GRID': [1, 2, 3, 4, 1, 2, 3, 4],
        'PROCESS': [1, 2, 3, 4, 1, 2, 3, 4],
        'PORTYPE': ['MATRIX', 'MATRIX', 'MATRIX', 'MATRIX', 'FRAC', 'FRAC', 'FRAC', 'FRAC']}),
        auto_distribute=None)
    sim_controls = SimControls(model=None)
    expected_number_processors = 4
    # Act
    result = sim_controls._load_grid_to_procs(options_file_content)

    # Assert
    pd.testing.assert_frame_equal(result.grid_to_proc_table, expected_result.grid_to_proc_table)
    assert sim_controls.number_of_processors == expected_number_processors


def test_load_grid_to_proc_no_grid_to_proc(mocker):
    # Arrange
    options_file_content = '''
    data to ignore
    another line
    15 15 MATRIX
    GRID
    1 1 1 
'''
    options_file_content = options_file_content.splitlines(keepends=True)
    expected_result = GridToProc(grid_to_proc_table=None, auto_distribute=None)

    # mock out simulation
    model = mocker.Mock()
    model.model_files.options_file = NexusFile(location='options.dat', file_content_as_list=options_file_content)

    sim_controls = SimControls(model=model)
    expected_number_processors = 0

    # Act
    result = sim_controls._load_grid_to_procs(options_file_content)

    # Assert
    assert result == expected_result
    assert sim_controls.number_of_processors == expected_number_processors


def test_load_grid_to_proc_auto():
    # Arrange
    options_file_content = '''
    GRIDTOPROC
    AUTO GRIDBLOCKS
    ENDGRIDTOPROC
    '''
    options_file_content = options_file_content.splitlines(keepends=True)
    expected_result = GridToProc(grid_to_proc_table=None, auto_distribute='GRIDBLOCKS')
    sim_controls = SimControls(model=None)
    expected_number_processors = 0
    # Act
    result = sim_controls._load_grid_to_procs(options_file_content)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize('file_content', [
    # basic test
    ('''FIELD MONTHLY
      REGIONS TIMESTEP 1030
      WELLS FREQ 123
      NETWORK YEARLY'''),

    # test with comments
    ('''FIELD MONTHLY
      REGIONS TIMESTEP 1030
      ! comment
      
      WELLS FREQ 123
      NETWORK YEARLY

      ! comment
      ! comment
      '''),
], ids=['basic test', 'test with comments'])
def test_get_output_request(file_content: str, mocker: MockerFixture):
    date = '01/01/2020'
    output_type = OutputType.ARRAY
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    # Act
    result = NexusReporting._get_output_request(table_file_as_list=file_content.splitlines(keepends=True),
                                                date=date, output_type=output_type)
    expected_result = [NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/2020', output='FIELD',
                                          output_frequency=FrequencyEnum.MONTHLY, output_frequency_number=None),
                       NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/2020', output='REGIONS',
                                          output_frequency=FrequencyEnum.TIMESTEP, output_frequency_number=1030),
                       NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/2020', output='WELLS',
                                          output_frequency=FrequencyEnum.FREQ, output_frequency_number=123),
                       NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/2020', output='NETWORK',
                                          output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None)]
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('file_content, expected_result', [
    # basic test
    ("""
WELLS DATE TSNUM QOP QWP COP CWP QWI CWI WCUT WPAVE CGP   QGP  QLP  GOR  BHP SAL 
! comment
FIELD DATE TSNUM COP CGP CWP CWI QOP QGP QWP QLP QWI WCUT OREC PAVT PAVH

REGIONS DATE TSNUM COP CGP CWP CWI QOP QGP QWP QWI STOIP ROP RWP RWI CROP CRWP CRWI PDATUMT PDATUMHC COFLUX CWFLUX AQFLUX RVO RVPVH """,
     [NexusOutputContents(output_type=OutputType.SPREADSHEET, output='WELLS', date='01/01/2020',
                          output_contents=['DATE', 'TSNUM', 'QOP', 'QWP', 'COP', 'CWP', 'QWI', 'CWI', 'WCUT', 'WPAVE',
                                           'CGP', 'QGP', 'QLP',
                                           'GOR', 'BHP', 'SAL']),
      NexusOutputContents(output_type=OutputType.SPREADSHEET, output='FIELD', date='01/01/2020',
                          output_contents=['DATE', 'TSNUM', 'COP', 'CGP', 'CWP', 'CWI', 'QOP', 'QGP', 'QWP', 'QLP',
                                           'QWI', 'WCUT', 'OREC',
                                           'PAVT', 'PAVH']),
      NexusOutputContents(output_type=OutputType.SPREADSHEET, output='REGIONS', date='01/01/2020',
                          output_contents=['DATE', 'TSNUM', 'COP', 'CGP', 'CWP', 'CWI', 'QOP', 'QGP', 'QWP', 'QWI',
                                           'STOIP', 'ROP', 'RWP',
                                           'RWI', 'CROP', 'CRWP', 'CRWI', 'PDATUMT', 'PDATUMHC', 'COFLUX', 'CWFLUX',
                                           'AQFLUX', 'RVO',
                                           'RVPVH'])
      ]),

    # Advanced
    ("""WELLS DATE TSNUM QOP QWP COP CWP QWI CWI ! comment at end of line
! comment
FIELD DATE TSNUM COP CGP 
     """, [NexusOutputContents(output_type=OutputType.SPREADSHEET, output='WELLS', date='01/01/2020',
                               output_contents=['DATE', 'TSNUM', 'QOP', 'QWP', 'COP', 'CWP', 'QWI', 'CWI']),
           NexusOutputContents(output_type=OutputType.SPREADSHEET, output='FIELD', date='01/01/2020',
                               output_contents=['DATE', 'TSNUM', 'COP', 'CGP'])
           ]),
],
                         ids=['basic test', 'advanced'])
def test_get_output_contents(file_content, expected_result):
    # Act
    result = NexusReporting._get_output_contents(table_file_as_list=file_content.splitlines(keepends=True),
                                                 output_type=OutputType.SPREADSHEET, date='01/01/2020')
    # Assert
    assert result == expected_result


def test_load_output_requests(mocker):
    # Arrange
    file_content = '''START 01/01/1950
    MAPOUT
   P
   PV
   SAT OIL GAS WATER
   KR OIL WATER
   PC OIL WATER
   SAL
ENDMAPOUT
SPREADSHEET
      FIELD MONTHLY
      REGIONS	FREQ 21
      WELLS YEARLY
      NETWORK YEARLY
ENDSPREADSHEET
    SSOUT
WELLS DATE TSNUM QOP QWP COP CWP QWI CWI WCUT WPAVE CGP   QGP  QLP  GOR  BHP SAL 
FIELD DATE TSNUM COP CGP CWP CWI QOP QGP QWP QLP QWI WCUT OREC PAVT PAVH
REGIONS DATE TSNUM COP CGP CWP CWI QOP QGP QWP QWI STOIP ROP RWP RWI CROP CRWP CRWI PDATUMT PDATUMHC COFLUX CWFLUX AQFLUX RVO RVPVH 
ENDSSOUT
TIME 01/01/1951
OUTPUT 
    FIELD MONTHLY
    WELLS YEARLY
    MAPS FREQ 120
    RFT     MONTHLY
    RFTFILE ON
ENDOUTPUT


TIME 01/01/1952

TIME 01/10/1953
SSOUT
WELLS DATE TSNUM QOP QWP COP
ENDSSOUT
OUTPUT
    FIELD YEARLY
    WELLS TIMES
    MAPS FREQ 120
    RFTFILE TNEXT
ENDOUTPUT
TIME 24/01/1999
    '''
    file_content_as_list = file_content.splitlines(keepends=True)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    expected_ss_output_requests = [
        NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/01/1950', output='FIELD',
                           output_frequency=FrequencyEnum.MONTHLY, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/01/1950', output='REGIONS',
                           output_frequency=FrequencyEnum.FREQ, output_frequency_number=21),
        NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/01/1950', output='WELLS',
                           output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/01/1950', output='NETWORK',
                           output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None),
    ]
    expected_array_output_requests = [
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/1951', output='FIELD',
                           output_frequency=FrequencyEnum.MONTHLY, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/1951', output='WELLS',
                           output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/1951', output='MAPS',
                           output_frequency=FrequencyEnum.FREQ, output_frequency_number=120),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/1951', output='RFT',
                           output_frequency=FrequencyEnum.MONTHLY, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/01/1951', output='RFTFILE',
                           output_frequency=FrequencyEnum.ON, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/10/1953', output='FIELD',
                           output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/10/1953', output='WELLS',
                           output_frequency=FrequencyEnum.TIMES, output_frequency_number=None),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/10/1953', output='MAPS',
                           output_frequency=FrequencyEnum.FREQ, output_frequency_number=120),
        NexusOutputRequest(output_type=OutputType.ARRAY, date='01/10/1953', output='RFTFILE',
                           output_frequency=FrequencyEnum.TNEXT, output_frequency_number=None)
    ]

    expected_ss_output_contents = [
        NexusOutputContents(output_type=OutputType.SPREADSHEET, output='WELLS', date='01/01/1950',
                            output_contents=['DATE', 'TSNUM', 'QOP', 'QWP', 'COP', 'CWP', 'QWI', 'CWI', 'WCUT',
                                             'WPAVE', 'CGP', 'QGP', 'QLP', 'GOR', 'BHP', 'SAL']),
        NexusOutputContents(output_type=OutputType.SPREADSHEET, output='FIELD', date='01/01/1950',
                            output_contents=['DATE', 'TSNUM', 'COP', 'CGP', 'CWP', 'CWI', 'QOP', 'QGP', 'QWP', 'QLP',
                                             'QWI', 'WCUT', 'OREC', 'PAVT', 'PAVH']),
        NexusOutputContents(output_type=OutputType.SPREADSHEET, output='REGIONS', date='01/01/1950',
                            output_contents=['DATE', 'TSNUM', 'COP', 'CGP', 'CWP', 'CWI', 'QOP', 'QGP', 'QWP', 'QWI',
                                             'STOIP', 'ROP', 'RWP', 'RWI', 'CROP', 'CRWP', 'CRWI', 'PDATUMT',
                                             'PDATUMHC', 'COFLUX', 'CWFLUX', 'AQFLUX', 'RVO', 'RVPVH']),
        NexusOutputContents(output_type=OutputType.SPREADSHEET, output='WELLS', date='01/10/1953',
                            output_contents=['DATE', 'TSNUM', 'QOP', 'QWP', 'COP'])
    ]

    expected_array_output_contents = [
        NexusOutputContents(output_type=OutputType.ARRAY, output='P', date='01/01/1950',
                            output_contents=[]),
        NexusOutputContents(output_type=OutputType.ARRAY, output='PV', date='01/01/1950',
                            output_contents=[]),
        NexusOutputContents(output_type=OutputType.ARRAY, output='SAT', date='01/01/1950',
                            output_contents=['OIL', 'GAS', 'WATER']),
        NexusOutputContents(output_type=OutputType.ARRAY, output='KR', date='01/01/1950',
                            output_contents=['OIL', 'WATER']),
        NexusOutputContents(output_type=OutputType.ARRAY, output='PC', date='01/01/1950',
                            output_contents=['OIL', 'WATER']),
        NexusOutputContents(output_type=OutputType.ARRAY, output='SAL', date='01/01/1950',
                            output_contents=[])
    ]

    # fake model
    model = get_fake_nexus_simulator(mocker)
    model._start_date = '01/01/1950'
    nexus_reporting = NexusReporting(model=model)
    model.model_files.runcontrol_file = NexusFile(location='runcontrol.dat', file_content_as_list=file_content_as_list)
    # Act
    nexus_reporting.load_output_requests()

    # Assert
    assert nexus_reporting.ss_output_requests == expected_ss_output_requests
    assert nexus_reporting.array_output_requests == expected_array_output_requests
    assert nexus_reporting.ss_output_contents == expected_ss_output_contents
    assert nexus_reporting.array_output_contents == expected_array_output_contents


@pytest.mark.parametrize('new_rft_date, expected_result', [
    # basic test - at existing time stamp
    ('01/02/1951', '''START 01/01/1950
                    TIME 01/01/1951
                    TIME 01/02/1951

OUTPUT
RFT TNEXT
ENDOUTPUT

                    TIME 01/05/1951
                    OUTPUT 
                        FIELD MONTHLY
                    ENDOUTPUT
                    TIME 01/01/1952
                    STOP
                    '''),
    # at a new timestamp
    ('01/03/1951', '''START 01/01/1950
                    TIME 01/01/1951
                    TIME 01/02/1951

TIME 01/03/1951
OUTPUT
RFT TNEXT
ENDOUTPUT

                    TIME 01/05/1951
                    OUTPUT 
                        FIELD MONTHLY
                    ENDOUTPUT
                    TIME 01/01/1952
                    STOP
                    '''),
    # at an existing timestep with an OUTPUT field defined already
    ('01/05/1951', '''START 01/01/1950
                    TIME 01/01/1951
                    TIME 01/02/1951
                    TIME 01/05/1951
                    OUTPUT 
                        FIELD MONTHLY
RFT TNEXT
                    ENDOUTPUT
                    TIME 01/01/1952
                    STOP
                    '''),
    # At the end of the file
    ('01/01/1953', '''START 01/01/1950
                    TIME 01/01/1951
                    TIME 01/02/1951
                    TIME 01/05/1951
                    OUTPUT 
                        FIELD MONTHLY
                    ENDOUTPUT
                    TIME 01/01/1952

TIME 01/01/1953
OUTPUT
RFT TNEXT
ENDOUTPUT

                    STOP
                    '''),

], ids=['basic test - at existing time stamp', 'at a new timestamp', 'existing timestep with an OUTPUT',
        'At the end of the file'])
def test_add_array_output_request(mocker, new_rft_date, expected_result):
    # Arrange
    runcontrol_content = '''START 01/01/1950
                    TIME 01/01/1951
                    TIME 01/02/1951
                    TIME 01/05/1951
                    OUTPUT 
                        FIELD MONTHLY
                    ENDOUTPUT
                    TIME 01/01/1952
                    STOP
                    '''

    expected_result = expected_result.splitlines(keepends=True)
    # fake model
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_content}
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    model = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    nexus_reporting = NexusReporting(model=model)

    nexus_reporting.load_output_requests()
    new_output_request = NexusOutputRequest(date=new_rft_date, output='RFT', output_type=OutputType.ARRAY,
                                            output_frequency=FrequencyEnum.TNEXT, output_frequency_number=None)

    # Act
    nexus_reporting.add_array_output_request(new_output_request)
    result = model.model_files.runcontrol_file.file_content_as_list

    # Assert
    assert result == expected_result
    assert nexus_reporting.array_output_requests[-1] == new_output_request


def test_output_request_to_table_line():
    # Arrange
    output_req = NexusOutputRequest(date='01/02/1951', output='RFT', output_type=OutputType.ARRAY,
                                    output_frequency=FrequencyEnum.TNEXT, output_frequency_number=None)
    expected_result = 'RFT TNEXT\n'
    # Act
    result = output_req.to_table_line(headers=[])

    # Assert
    assert result == expected_result


def test_get_times_run_control():
    # Arrange
    run_control_content = """
TIME 01/01/2023
TIME 01/01/2024
TIME 01/01/2025
    
STOP
TIME 01/01/2026
"""
    options_file_content = run_control_content.splitlines(keepends=True)
    expected_result = ['01/01/2023', '01/01/2024', '01/01/2025']
    sim_controls = SimControls(model=None)

    # Act
    result = sim_controls.get_times(options_file_content)

    # Assert
    assert result == expected_result


def test_modify_times_run_control(mocker: MockerFixture):
    # Arrange

    nex_model = get_fake_nexus_simulator(mocker=mocker)
    nex_model._start_date = '01/01/2023'
    sim_controls = SimControls(model=nex_model)
    time_content = ['01/01/2025', '01/01/2026']
    sim_controls._SimControls__times = ['01/01/2023', '01/01/2024']

    sim_controls.modify_times(content=time_content, operation='MERGE')

    # Assert
    assert sim_controls.times == ['01/01/2023', '01/01/2024'] + time_content


def test_modify_times_run_control_with_get_times(mocker: MockerFixture):
    # Arrange
    run_control_content = """
TIME 01/01/2023
TIME 01/01/2024
TIME 01/01/2025

STOP
TIME 01/01/2028
"""
    run_file_content = run_control_content.splitlines(keepends=True)

    nex_model = get_fake_nexus_simulator(mocker=mocker)
    nex_model._start_date = '01/01/2023'
    sim_controls = SimControls(model=nex_model)

    time_content = ['01/01/2026', '01/01/2027']
    sim_controls._SimControls__times = sim_controls.get_times(run_file_content)

    sim_controls.modify_times(content=time_content, operation='MERGE')

    # Assert
    assert sim_controls.times == ['01/01/2023', '01/01/2024', '01/01/2025'] + time_content
