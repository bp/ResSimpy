import os
import pytest

from ResSimpy import NexusSimulator
from tests.multifile_mocker import mock_multiple_files


def test_load_drsdt_limit(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    run_control_file_contents = "DRSDT LIMIT 0.0 2PHASE\n"
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': run_control_file_contents,
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None

    assert simulation.sim_controls.drsdt_limit == 0.0
    assert simulation.sim_controls.drsdt_two_phases is True


def test_load_drsdt_without_two_phase(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    run_control_file_contents = "DRSDT LIMIT 0.1\n"
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': run_control_file_contents,
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None

    assert simulation.sim_controls.drsdt_limit == 0.1
    assert simulation.sim_controls.drsdt_two_phases is False


# Minimal test: covers the parser branch for an incomplete DRSDT line
def test_load_drsdt_incomplete_line_warns(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    run_control_file_contents = "DRSDT LIMIT\n"
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': run_control_file_contents,
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    with pytest.warns(UserWarning, match=r'Unable to parse DRSDT line'):
        simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    assert simulation.sim_controls.drsdt_limit is None


def test_load_drsdt_selector_with_non_numeric_value_skips(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    run_control_file_contents = "DRSDT LIMIT NOT_A_NUMBER\n"
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': run_control_file_contents,
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    # parsing should skip setting a numeric limit when value is invalid
    assert simulation.sim_controls.drsdt_limit is None


def test_load_drsdt_unrecognized_keyword_warns(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    run_control_file_contents = "DRSDT SOMETHING\n"
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': run_control_file_contents,
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    with pytest.warns(UserWarning, match=r'Unable to parse DRSDT line'):
        simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    _ = simulation.sim_controls.drsdt_limit