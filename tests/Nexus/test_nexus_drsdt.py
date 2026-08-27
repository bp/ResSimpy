import os
import pytest

from ResSimpy import NexusSimulator
from tests.multifile_mocker import mock_multiple_files


def test_load_drsdt_limit(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT LIMIT 0.0 2PHASE
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None

    assert simulation.grid.drsdt_limit == 0.0
    assert simulation.grid.drsdt_two_phases is True
    assert simulation.grid.drsdt_grid_name is None


def test_load_drsdt_without_two_phase(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT LIMIT 0.1
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None

    assert simulation.grid.drsdt_limit == 0.1
    assert simulation.grid.drsdt_two_phases is False
    assert simulation.grid.drsdt_grid_name is None


def test_load_drsdt_with_grid_name_warns_and_stores(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT LIMIT LGR1 0.25 2PHASE
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    with pytest.warns(UserWarning, match=r'DRSDT in Nexus was applied to grid LGR1'):
        result = simulation.grid.drsdt_limit

    assert result == 0.25
    assert simulation.grid.drsdt_two_phases is True
    assert simulation.grid.drsdt_grid_name == 'LGR1'


def test_load_drsdt_with_all_keyword_warns_and_stores(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT LIMIT ALL 0.5
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    with pytest.warns(UserWarning, match=r'DRSDT in Nexus was applied to grid ALL'):
        result = simulation.grid.drsdt_limit

    assert result == 0.5
    assert simulation.grid.drsdt_two_phases is False
    assert simulation.grid.drsdt_grid_name == 'ALL'


# Minimal test: covers the parser branch for an incomplete DRSDT line
def test_load_drsdt_incomplete_line_warns(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT LIMIT
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    with pytest.warns(UserWarning, match=r'Unable to parse DRSDT line'):
        assert simulation.grid.drsdt_limit is None


def test_load_drsdt_selector_with_non_numeric_value_skips(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    # selector present but following value is non-numeric -> should be skipped
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT LIMIT LGR1 NOT_A_NUMBER
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    # parsing should skip setting a numeric limit when value is invalid
    assert simulation.grid.drsdt_limit is None
    assert simulation.grid.drsdt_grid_name is None


def test_load_drsdt_unrecognized_keyword_warns(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
DRSDT SOMETHING
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    with pytest.warns(UserWarning, match=r'Unable to parse DRSDT line'):
        _ = simulation.grid.drsdt_limit