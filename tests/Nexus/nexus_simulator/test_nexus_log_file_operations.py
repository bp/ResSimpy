import pytest

from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.Nexus.nexus_simulator.test_nexus_simulator import mock_multiple_opens


@pytest.mark.parametrize("log_file_contents, times, expected_progress",
                         [
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n50.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1",
                              ["50", "100"], 50.0),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n1.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n2.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1",
                              ["1", "2", "3"], 66.7),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n368 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n1097 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n2740 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1",
                              ["02/01/2001", "03/07/2007", "01/01/2003", "01/01/2010"], 75.0),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n368 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n1097 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n2740 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n3654 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1",
                              ["02/01/2001", "03/07/2007", "01/01/2003", "01/01/2010"], 100.0),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n368 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n1097 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n2740 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n2780 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n3010 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n4405 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1\n\n"
                              f" Case Name = nexus_run        \nTIME  TS NWT   OIL     GAS    WATER    OIL     GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n4769 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n5230 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n5560 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1\n\n",
                              ["02/01/2001", "03/07/2007", "01/01/2003",
                               "01/01/2010", "23/03/2015", "05/06/2016"],
                              92.7),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nCOL1 COL2 TIME  TS NWT   OIL     GAS    WATER  OIL GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n1 2 1.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n3 4 2.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1",
                              ["1", "2", "10"], 20.0),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n\n"
                              f" Case Name = nexus_run        \nCOL1 COL2 TIME  TS NWT   OIL     GAS    WATER  OIL GAS"
                              f"WATER\n   DAYS  RP ITN   C.P.    C.I.    C.I.    P.R.    P.R.    P.R.    I.R.    I.R."
                              f"\n1 2 2.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1"
                              f"\n3 4 4.00 0   1 81961.8     0.0 347997. 2495.18 883.375 30000.3     0.0 34278.1\n"
                              "Errors            0     Warnings           65"
                              ""
                              "Run terminated at stop time"
                              "0",
                              ["2", "4", "10"], 40.0),
                         ])
def test_get_simulation_progress(mocker, log_file_contents, times, expected_progress):
    """Getting an estimate for how far through the simulation is"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\n"
    run_control_file = "START 01/01/2000"

    log_file_mock = mocker.mock_open(read_data=log_file_contents)

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(mocker, filename, fcs_file, run_control_file, "",
                                        log_file_mock=log_file_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.MagicMock(return_value=['nexus_run.log', ''])
    mocker.patch("os.listdir", listdir_mock)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="basic-model")
    simulation.modify(section="RUNCONTROL", keyword="TIME",
                      content=times, operation='REPLACE')
    mocker.patch("builtins.open", log_file_mock)

    # Act
    result = simulation.get_simulation_progress()

    # Assert
    listdir_mock.assert_called_with('basic-model')
    assert result == expected_progress


@pytest.mark.skip("Re-enable once the run code has been established")
def test_get_status_running(mocker):
    """Getting a simulation status for a running simulation"""
    # Arrange
    fcs_file = f"RUNCONTROL /run/control/path\nDATEFORMAT DD/MM/YYYY\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    listdir_mock = mocker.MagicMock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)

    # Act
    simulation = NexusSimulator(
        origin='testpath1/Path.fcs', destination="test_new_destination")
    result = simulation.get_simulation_status()

    # Assert
    assert result == "Nexsub status called, Job ID is: 456"


@pytest.mark.parametrize("log_file_contents,errors,warnings",
                         [
                             ("Nexus finished\nerrors 0 warnings 0", "0", "0"),
                             ("errors 1242452 warnings 37856\ntest\n other status\nNexus finished\n", "1242452",
                              "37856"),
                             ("test\n other status\nNexus\nNexus finished\nerrors 12 warnings 34", "12", "34"),
                         ])
def test_get_status_finished(mocker, log_file_contents, errors, warnings):
    """Getting a simulation status for a completed simulation - checking the log file"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\n"

    listdir_mock = mocker.MagicMock(return_value=['nexus_run.log', ''])
    mocker.patch("os.listdir", listdir_mock)

    log_file_mock = mocker.mock_open(read_data=log_file_contents)

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, "", "", log_file_mock=log_file_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="new_destination")

    mocker.patch("builtins.open", log_file_mock)

    expected_result = f"Simulation complete - Errors: {errors} and Warnings: {warnings}"

    # Act
    result = simulation.get_simulation_status()

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("log_file_contents, run_time",
                         [
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:13:19 CDT 2020\n \
                            not running cleanup, slots= 8 tot_cpus= 24\nNexus finished\nerrors 0 warnings 3"
                              f"\nend generic pdsh   epilog  with cleanup on  hpchw0101 Wed Sep 2 05:13:19 CDT 2020",
                              "0 Days, 2 Hours, 0 Minutes 0 Seconds"),

                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CDT 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\nNexus finished\nerrors 0 warnings 3"
                              f"\nend generic pdsh   epilog  with cleanup on  hpchw0101 Fri Sep 18 09:25:19 CDT 2020",
                              "16 Days, 6 Hours, 5 Minutes 0 Seconds"),

                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:20:19 CST 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\nNexus finished\nerrors 0 warnings 3"
                              f"\nend generic pdsh   epilog  with cleanup on  hpchw0101 Fri Sep 18 09:25:19 CST 2020",
                              "16 Days, 6 Hours, 5 Minutes 0 Seconds"),
                             # Different timezones (e.g. when the clocks change)
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 00:00:00 CDT 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\nNexus finished\nerrors 0 warnings 3"
                              f"\nend generic pdsh   epilog  with cleanup on  hpchw0101 Thu Oct 15 01:02:03 CST 2020",
                              "43 Days, 2 Hours, 2 Minutes 3 Seconds"),
                             # Across year boundary
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Thu Oct 15 01:02:03 CST 2020\n \
                            not running cleanup, slots= 8 tot_cpus= 24\nNexus finished\nerrors 0 warnings 3"
                              f"\nend generic pdsh   epilog  with cleanup on  hpchw0101 Sun Jan 24 10:12:14 CDT 2021",
                              "101 Days, 8 Hours, 10 Minutes 11 Seconds"),
                             # No previous run
                             (f"generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:13:19 CDT 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\nNexus finished\nerrors 0 warnings 3"
                              f"\ngeneric pdsh   epilog  with cleanup on  hpchw0101 Wed Sep 2 05:13:19 CDT 2020",
                              "-"),
                         ])
def test_get_base_case_run_time(mocker, log_file_contents, run_time):
    """Test the 'retrieve previous time for run' functionality"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\n"
    log_file_mock = mocker.mock_open(read_data=log_file_contents)

    # Returns the contents of a completed run when looking at the 'original' model
    def open_file_mock(filename, operation=None):
        if filename == 'testpath1/nexus_run.log':
            return log_file_mock.return_value
        return mocker.mock_open(read_data=fcs_file).return_value

    mocker.patch("builtins.open", open_file_mock)

    initial_listdir_mock = mocker.Mock(return_value=['nexus_run.log', ''])
    rename_mock = mocker.Mock()
    mocker.patch("os.rename", rename_mock)
    mocker.patch("os.listdir", initial_listdir_mock)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs', destination="/test/new_destination",
                                root_name="new_case")

    final_listdir_mock = mocker.Mock(return_value=['new_case.log', ''])
    mocker.patch("os.listdir", final_listdir_mock)

    new_open_mock = mocker.mock_open(read_data='Nexus finished\n')
    mocker.patch("builtins.open", new_open_mock)

    # Act
    result = simulation.logging.get_base_case_run_time()

    # Assert
    initial_listdir_mock.assert_called_once_with('testpath1')
    # final_listdir_mock.assert_called_once_with('/test/new_destination')
    assert result == run_time


@pytest.mark.parametrize("log_file_contents, start_time",
                         [
                             (
                                     f"start generic pdsh   prolog  with cleanup on  hpchw0103 Wed Aug 26 06:56:06 CDT 2020\n\n",
                                     "Wed Aug 26 06:56:06 CDT 2020"),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:13:19 CDT 2020\n \
                            not running cleanup, slots= 8 tot_cpus= 24\n"
                              f"\nend generic pdsh prolog  with cleanup  Wed Sep 2 03:13:22 CDT 2020",
                              "Wed Sep 2 03:13:19 CDT 2020"),

                         ])
def test_get_simulation_start_time(mocker, log_file_contents, start_time):
    """Test the get start time functionality"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\n"

    log_file_mock = mocker.mock_open(read_data=log_file_contents)

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, "", "", log_file_mock=log_file_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.MagicMock(return_value=['nexus_run.log', ''])
    mocker.patch("os.listdir", listdir_mock)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="new_destination")
    mocker.patch("builtins.open", log_file_mock)

    # Act
    result = simulation.logging.get_simulation_start_time()

    # Assert
    assert result == start_time


@pytest.mark.parametrize("log_file_contents, end_time",
                         [
                             (f"end generic pdsh   epilog  with cleanup on  hpchw0101 Wed Aug 26 08:15:02 CDT 2020\n\n",
                              "Wed Aug 26 08:15:02 CDT 2020"),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:13:19 CDT 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\n"
                              f"\nend generic pdsh prolog  with cleanup  Wed Sep 2 03:13:22 CDT 2020",
                              "-"),
                         ])
def test_get_simulation_end_time(mocker, log_file_contents, end_time):
    """Test the get end time functionality"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\n"

    log_file_mock = mocker.mock_open(read_data=log_file_contents)

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, "", "", log_file_mock=log_file_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.MagicMock(return_value=['nexus_run.log', ''])
    mocker.patch("os.listdir", listdir_mock)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="new_destination")
    mocker.patch("builtins.open", log_file_mock)

    # Act
    result = simulation.logging.get_simulation_end_time()

    # Assert
    assert result == end_time


@pytest.mark.parametrize("log_file_contents, expected_start_time, expected_end_time",
                         [
                             (f"start generic pdsh   prolog  with cleanup on  hpchw0103 Wed Aug 30 09:56:06 CDT 2020\n"
                              f"end generic pdsh   epilog  with cleanup on  hpchw0101 Wed Aug 26 08:15:02 CDT 2020\n\n",
                              "Wed Aug 30 09:56:06 CDT 2020", "Wed Aug 26 08:15:02 CDT 2020"),
                             (f"start generic pdsh   prolog  with cleanup on  hpchw1104 Wed Sep 2 03:13:19 CDT 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\n"
                              f"\nend generic pdsh prolog  with cleanup  Wed Sep 2 03:13:22 CDT 2020",
                              "Wed Sep 2 03:13:19 CDT 2020", "-"),
                             (f"start generic pdsh   test  with cleanup on  hpchw1104 Wed Sep 2 03:13:19 CDT 2020\n \
                                not running cleanup, slots= 8 tot_cpus= 24\n"
                              f"\nend generic pdsh test  with cleanup  Wed Sep 2 03:13:22 CDT 2020",
                              "-", "-"),
                             (f"start generic pdsh   epilog  with cleanup on  hpchw0103 Wed Aug 30 09:56:06 CDT 2020\n"
                              f"end generic pdsh   prolog  with cleanup on  hpchw0101 Wed Aug 26 08:15:02 CDT 2020\n\n",
                              "-", "-"),
                         ])
def test_get_simulation_start_end_time(mocker, log_file_contents, expected_start_time, expected_end_time):
    """Test the get end time functionality"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\n"

    log_file_mock = mocker.mock_open(read_data=log_file_contents)

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(
            mocker, filename, fcs_file, "", "", log_file_mock=log_file_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.MagicMock(return_value=['nexus_run.log', ''])
    mocker.patch("os.listdir", listdir_mock)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="new_destination")
    mocker.patch("builtins.open", log_file_mock)

    # Act
    result_start_time = simulation.logging.get_simulation_start_time()
    result_end_time = simulation.logging.get_simulation_end_time()

    # Assert
    assert result_start_time == expected_start_time
    assert result_end_time == expected_end_time
