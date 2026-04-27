import os

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
    result = simulation.grid.tolpv

    # assert
    assert result == structured_grid_file_contents
