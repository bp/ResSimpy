import os
import pytest

from ResSimpy import NexusSimulator
from tests.multifile_mocker import mock_multiple_files


def test_load_tolpv(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
TOLPV 5000.5
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         # include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    mocker.patch("os.path.isfile", lambda x: True)
    mocker.patch("os.path.exists", lambda x: True)
    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    result = simulation.grid.tolpv

    # assert
    assert isinstance(result, float)
    assert result == 5000.5
    assert simulation.grid.tolpv_grid_name is None


def test_load_tolpv_from_cortol(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
CORTOL 0.1 0.2 7000.25
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
    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    result = simulation.grid.tolpv

    # assert
    assert isinstance(result, float)
    assert result == 7000.25
    assert simulation.grid.tolpv_grid_name is None


def test_load_tolpv_with_grid_name_warns_and_stores(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
TOLPV LGR1 5000.5
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
    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    with pytest.warns(UserWarning, match=r'TOLPV in Nexus was applied to grid LGR1'):
        result = simulation.grid.tolpv

    # assert
    assert isinstance(result, float)
    assert result == 5000.5
    assert simulation.grid.tolpv_grid_name == 'LGR1'


def test_load_tolpv_with_all_keyword_warns_and_stores(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
TOLPV ALL 5000.5
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
    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    assert simulation.grid is not None
    with pytest.warns(UserWarning, match=r'TOLPV in Nexus was applied to grid ALL'):
        result = simulation.grid.tolpv

    # assert
    assert isinstance(result, float)
    assert result == 5000.5
    assert simulation.grid.tolpv_grid_name == 'ALL'


def test_load_tolpv_with_comment_after_value(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
TOLPV 5000.5 ! this is a tolpv line
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
    result = simulation.grid.tolpv

    assert isinstance(result, float)
    assert result == 5000.5
    assert simulation.grid.tolpv_grid_name is None


def test_load_tolpv_value_on_next_line(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
TOLPV ALL
5000.5
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
    with pytest.warns(UserWarning, match=r'TOLPV in Nexus was applied to grid ALL'):
        result = simulation.grid.tolpv

    assert isinstance(result, float)
    assert result == 5000.5
    assert simulation.grid.tolpv_grid_name == 'ALL'


def test_load_tolpv_warns_when_value_missing(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
    NX NY NZ
    10 10 3
TOLPV
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
    with pytest.warns(UserWarning, match=r'Unable to parse TOLPV line: TOLPV'):
        result = simulation.grid.tolpv

    assert result is None
    assert simulation.grid.tolpv_grid_name is None


