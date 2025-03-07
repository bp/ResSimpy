import os

import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusTOver import NexusTOver
from tests.multifile_mocker import mock_multiple_files


@pytest.mark.parametrize('structured_grid_file_contents, expected_result', [
    ("""ARRAYS ROOT
! grid
NX  NY  NZ
10  25  10

NETGRS VALUE
INCLUDE NTG.inc

TOVER TX+
1 10 1 15 1 3 MULT
INCLUDE ../../tover_1.inc
1 10 1 25 4 6 MULT
INCLUDE ../../tover_2.inc
""",
     [NexusTOver(i1=1, i2=10, j1=1, j2=15, k1=1, k2=3, operator='MULT', array='TX+',
                 grid='ROOT', include_file='../../tover_1.inc', value=0),
      NexusTOver(i1=1, i2=10, j1=1, j2=25, k1=4, k2=6, operator='MULT', array='TX+',
                 grid='ROOT', include_file='../../tover_2.inc', value=0)]

     ),
    ("""ARRAYS ROOT
    NX  NY  NZ
    10  25  10
    NETGRS VALUE
    INCLUDE NTG.inc
    
    TOVER TX-
    
    1 10 1 15 1 3 EQ  ! COMMENT
    
    INCLUDE tover_1.inc


    TOvER TY-
    1 10 1 15 1 3 DIV  ! COMMENT
    include tover2.inc
    
    KX CON
    2
    
    TOVER TXF+
    1 2 3 4 5 6 EQ
    INCLUDE txf.inc ! comment
    """,
        [NexusTOver(i1=1, i2=10, j1=1, j2=15, k1=1, k2=3, operator='EQ', array='TX-',
                    grid='ROOT', include_file='tover_1.inc', value=0),
        NexusTOver(i1=1, i2=10, j1=1, j2=15, k1=1, k2=3, operator='DIV', array='TY-',
                    grid='ROOT', include_file='tover2.inc', value=0),
        NexusTOver(i1=1, i2=2, j1=3, j2=4, k1=5, k2=6, operator='EQ', array='TXF+',
                    grid='ROOT', include_file='txf.inc', value=0)]
    
        ),
    ("""ARRAYS ROOT
    NX  NY  NZ
    10  25  10
    NETGRS VALUE
    INCLUDE NTG.inc
    
    TOVER TX-
    1 1 1 1 1 3 EQ ! Comment
    0.3 0.4 0.5 
    
    TOVER TX+
    1 1 1 1 1 1 MULT
    include tover1.inc
    
    TOVER TXF+
    1 1 1 1 1 1 MULT
    1.2
    """,
     [NexusTOver(i1=1, i2=1, j1=1, j2=1, k1=1, k2=3, operator='EQ', array='TX-', array_values=[0.3, 0.4, 0.5], value=0,
                 include_file=None, grid='ROOT'),
      NexusTOver(i1=1, i2=1, j1=1, j2=1, k1=1, k2=1, operator='MULT', array='TX+', include_file='tover1.inc', value=0,
                 array_values=None, grid='ROOT'),
      NexusTOver(i1=1, i2=1, j1=1, j2=1, k1=1, k2=1, operator='MULT', array='TXF+', array_values=[1.2], value=0, 
                 include_file=None, grid='ROOT')
      ]),
], ids=['basic', 'multiple reads', 'direct from array'])
def test_load_tover(mocker, structured_grid_file_contents, expected_result):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

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
    result = simulation.grid.tovers

    # assert
    assert result == expected_result
