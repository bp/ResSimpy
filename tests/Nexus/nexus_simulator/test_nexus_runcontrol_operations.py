

import pytest

from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.multifile_mocker import mock_multiple_files

from tests.Nexus.nexus_simulator.test_nexus_simulator import mock_multiple_opens


@pytest.mark.parametrize(
    "date_format,expected_date_format,run_control_contents,include_file_contents,expected_times", [
        # USA date format, no times in run control
        ("MM/DD/YYYY", DateFormat.MM_DD_YYYY, "START 01/01/1980\nINCLUDE     path/to/include\nWELLS\nTIMES PERFS\n",
         "TIME 0.1\nTIME 10/15/1983\n "
         "invalidtime", ['0.1', '10/15/1983']),
        # Non-USA date format, times in run control and include files
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE  \n! Comment \n   path/to/include\nTIME 01/01/1981\nTIME 0.1",
         "TIME 0.3\nTIME 15/10/1983\nTIME 1503.1\nTIME 15/12/1996",
         ['0.1', '0.3', '01/01/1981', '15/10/1983', '1503.1', '15/12/1996']),
        # Non-USA date format, times in include file only
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE  !test comment\n   path/to/include",
         "TIME 0.1\nTIME 15/10/1983\n invalidtime\nTIME 1503.1\nTIME 15/12/2021",
         ['0.1', '15/10/1983', '1503.1', '15/12/2021']),
        # Non-USA date format, times in run control only, but include file declared
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include\nTIME 19/08/2025\nTIME 0.1\nTIME 50000",
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
        ("MM/DD/YYYY", DateFormat.MM_DD_YYYY, "START 01/01/1980\nINCLUDE     path/to/include", "TIME 0.1\nTIME 10/15/1983\n ",
         ['01/01/2001', '12/15/2000', '08/08/2008', '0.1', '08/07/2008'], 'REPLACE',
         ['0.1', '12/15/2000', '01/01/2001', '08/07/2008', '08/08/2008']),
        # Non-USA date format, merge
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
         "TIME 0.3\nTIME 15/10/1983\n invalidtime\nTIME 1503.1\nTIME 15/12/1998",
         ['01/01/2001', '15/12/2000', '08/08/1998',
             '0.1', '08/07/2008', '01/02/1981'], 'merge',
         ['0.1', '0.3', '01/01/1981', '01/02/1981', '15/10/1983', '1503.1', '08/08/1998', '15/12/1998', '15/12/2000',
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
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
         "TIME 0.3\nTIME 15/10/1983\nytime invalidtime\nTIME 1503.1\nTIME 15/12/1996\nTIME 01/01/2000\nSTOP\n",
         ['0.3', '01/01/1981', '01/01/2000', '08/05/2015'], 'REMOVE',
         ['0.1', '15/10/1983', '1503.1', '15/12/1996']),
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
        ("MM/DD/YYYY", DateFormat.MM_DD_YYYY, "START 12/01/1980\nINCLUDE     path/to/include", "TIME 0.1\nTIME 10/15/1983\ntimee ",
         ['01/01/2001', '12/15/2000', '08/08/2008', '0.1',
             '01/12/1980', '08/07/2008'], 'REPLACE',
         ['0.1', '10/15/1983']),
        # Non-USA date format, merge
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1980\nINCLUDE     path/to/include\nTIME 01/01/1981\nTIME 0.1",
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
        ("DD/MM/YYYY", DateFormat.DD_MM_YYYY, "START 01/01/1985\nINCLUDE     path/to/include\nTIME 01/01/1986\nTIME 0.1",
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
    fcs_data ='''RUN_UNITS     ENGLISH
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
