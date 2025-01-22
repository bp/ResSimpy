import os

import numpy as np
import pandas as pd
import pytest
from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGR import NexusLGR
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.Nexus.nexus_simulator.test_nexus_simulator import mock_multiple_opens
from tests.multifile_mocker import mock_multiple_files


@pytest.mark.parametrize("structured_grid_file_contents, expected_corp, expected_iequil",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nCORP VALUE\n "
                              "INCLUDE /XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor\n "
                              "IEQUIL CON\n"
                              "1\n!ANOTHER COMMENT \n",  # end structured_grid_file_contents
                              "/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor",
                              1),
                         ])
def test_load_structured_grid_file_iequil_corp(mocker, structured_grid_file_contents, expected_corp, expected_iequil):
    """Read in Structured Grid File"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):  # for some reason mode arg is needed even though not used
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         structured_grid_name: structured_grid_file_contents,
         '/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor': ''}).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    sim_obj = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = sim_obj.grid

    # Assert
    # note that iequil is a nexus specific grid array and is an integer
    assert result.iequil.modifier == 'CON'
    assert result.iequil.value == '1'
    assert result.corp.modifier == 'VALUE'
    assert result.corp.value == '/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor'


@pytest.mark.parametrize('structured_grid_file_contents, include_file_contents',
                         [
                             ("""ARRAYS ROOT
! grid
INCLUDE /XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor
LIST""",  # end structured grid_file_contents and begin include_file_contents
                              """C ---------------------------
C  File-name: xx.cor
C  Created: 08-MAR-2005 14:41:27
C
C
C
C
C
CORP VALUE"""
                              ),
                             ("""ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10
INCLUDE /XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor
LIST""",  # ends structured_grid_file_contents
                              """C ---------------------------
C  File-name: xx.cor
C  Created: 08-MAR-2005 14:41:27
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
CORP VALUE
C This is a comment that comes after the keyword."""

                              ),
                             ("""ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10
INCLUDE /XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor
LIST""",  # ends structured grid_file_contents
                              """CORP VALUE
C GRID BLOCK: I =   1 , J =   1 , K =   1  
2265.261168 18412.34172 6006.48864 2697.769032 18432.059328 6010.983336
2879.984664 17767.1724 5972.663592 2456.761464 17751.621408 5976.206856
2265.261168 18412.34172 6104.91264 2697.769032 18432.059328 6109.407336
2879.984664 17767.1724 6071.087592 2456.761464 17751.621408 6074.630856"""
                              )

                         ])
def test_grid_arr_in_include_file(mocker, structured_grid_file_contents, include_file_contents):
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    include_file_location = '/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    sim_obj = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = sim_obj.grid

    # Assert
    assert result.corp.keyword_in_include_file is True
    assert result.corp.value == '/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.cor'


@pytest.mark.parametrize('structured_grid_file_contents, include_file_contents',
                         [
                             ("""ARRAYS ROOT
! grid
INCLUDE /XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.ireg.inc
LIST""",  # end structured grid_file_contents and begin include_file_contents
                              """C ---------------------------
C  File-name: xx.ireg.inc
C  Created: 08-MAR-2005 14:41:27
C
C
C
C
C
IREGION VALUE"""
                              ),
                         ])
def test_grid_arr_in_include_file_ireg(mocker, structured_grid_file_contents, include_file_contents):
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    include_file_location = '/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.ireg.inc'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    sim_obj = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = sim_obj.grid

    # Assert
    assert result.iregion['IREG1'].keyword_in_include_file is True
    assert result.iregion['IREG1'].value == '/XXX/XXX/XXX/Testing/XXX/XXX/Includes/xxx.ireg.inc'


def test_load_structured_grid_file_multiple_mods(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10

NETGRS ZVAR
NOLIST
INCLUDE path/netgrs_01.inc
MOD
68  68 34 34  1  1 =0.34
68  68 34 34  2  2 =0.2
MOD
68  68 34 34  8 10 =0.69
MOD
68  68 34 34 11 14 =0.85
68  68 34 34 15 15 =0.52
MOD
68  68 34 34 16 16 =0.79
56  56 36 36  1  1 =0.67
LIST
"""  # ends structured_grid_file_contents

    # include_file_contents = '0.425 0.255 3*0.662 0.376 0.000 3*0.453 4*0.884 0.412 0.788 12*0.000'
    # include_file_location = os.path.join('testpath1', r'includes/netgrs_01.inc')

    # set up dataframe
    i1 = [68] * 6 + [56]
    i2 = [68] * 6 + [56]
    j1 = [34] * 6 + [36]
    j2 = [34] * 6 + [36]
    k1 = [1, 2, 8, 11, 15, 16, 1]
    k2 = [1, 2, 10, 14, 15, 16, 1]
    v = ['=0.34', '=0.2', '=0.69', '=0.85', '=0.52', '=0.79', '=0.67']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         # include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.netgrs.keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.netgrs.mods['MOD'], expected_df)
    assert result.netgrs.modifier == 'ZVAR'
    assert result.netgrs.value == 'path/netgrs_01.inc'


def test_load_structured_grid_file_mod_with_space(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10

NETGRS ZVAR
INCLUDE path/netgrs_01.inc
MOD
68  68 34 34  1  1 = 0.34
68  68 34 34  2  2 = 0.2

IREGION ZVAR
3*1
3*2
4*3

IRELPM XVAR
3*1
3*2
4*3
"""  # ends structured_grid_file_contents

    # include_file_contents = '0.425 0.255 3*0.662 0.376 0.000 3*0.453 4*0.884 0.412 0.788 12*0.000'
    # include_file_location = os.path.join('testpath1', r'includes/netgrs_01.inc')

    # set up dataframe
    i1 = [68] * 2
    i2 = [68] * 2
    j1 = [34] * 2
    j2 = [34] * 2
    k1 = [1, 2]
    k2 = [1, 2]
    v = ['=0.34', '=0.2']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         # include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.netgrs.keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.netgrs.mods['MOD'], expected_df)
    assert result.netgrs.modifier == 'ZVAR'
    assert result.netgrs.value == 'path/netgrs_01.inc'
    assert result.iregion['IREG1'].modifier == 'ZVAR'
    assert result.iregion['IREG1'].value == '3*1\n3*2\n4*3'
    assert result.irelpm.modifier == 'XVAR'
    assert result.irelpm.value == '3*1\n3*2\n4*3'


def test_load_structured_grid_file_corp_modx_mody_modz(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10

CORP VALUE
INCLUDE path/corp_01.inc
MODX
1 298   1 216   1 120 +1421587
MODY
1 298   1 216   1 120 +1421587
MODZ
1 298   1 216   1 120 +1421587
LIST"""  # ends structured_grid_file_contents

    include_file_contents = '0.425 0.255 3*0.662 0.376 0.000 3*0.453 4*0.884 0.412 0.788 12*0.000'
    include_file_location = os.path.join('testpath1', r'includes/corp_01.inc')

    # set up dataframe
    i1 = [1]
    i2 = [298]
    j1 = [1]
    j2 = [216]
    k1 = [1]
    k2 = [120]
    v = [1421587]
    expected_modx_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         # include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.corp.keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.corp.mods['MODX'], expected_modx_df)
    pd.testing.assert_frame_equal(result.corp.mods['MODY'], expected_modx_df)
    pd.testing.assert_frame_equal(result.corp.mods['MODZ'], expected_modx_df)
    assert result.corp.modifier == 'VALUE'
    assert result.corp.value == 'path/corp_01.inc'


def test_load_structured_grid_file_iregion(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10
WORKA1 CON
1
WORKA2 CON
1
WORKA3 CON
1
WORKA4 CON
1
WORKA5 CON
1
WORKA6 CON
1
WORKA7 CON
1
WORKA8 CON
1
WORKA9 CON
1
IPVT CON
1
IROCK CON
1
ITRAN CON
1
IRELPM CON
1
PVMULT CON
1
LIVECELL CON
1
IWATER CON
1
IREGION CON
2  
MOD
30 38  1  30  1  1  =1   
C 13 20  1 30  1  1  =1     
25 32  1 30  1  1  =1      
LIST"""  # ends structured_grid_file_contents

    # set up dataframe
    i1 = [30, 25]
    i2 = [38, 32]
    j1 = [1, 1]
    j2 = [30, 30]
    k1 = [1, 1]
    k2 = [1, 1]
    v = ['=1', '=1']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    # note that iregion is a dict
    assert result.iregion['IREG1'].keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.iregion['IREG1'].mods['MOD'], expected_df)
    assert result.iregion['IREG1'].modifier == 'CON'
    assert result.iregion['IREG1'].value == '2'
    assert result.worka1.value == '1'
    assert result.worka2.value == '1'
    assert result.worka3.value == '1'
    assert result.worka4.value == '1'
    assert result.worka5.value == '1'
    assert result.worka6.value == '1'
    assert result.worka7.value == '1'
    assert result.worka8.value == '1'
    assert result.worka9.value == '1'
    assert result.ipvt.value == '1'
    assert result.iwater.value == '1'
    assert result.irock.value == '1'
    assert result.pvmult.value == '1'
    assert result.itran.value == '1'
    assert result.livecell.value == '1'
    assert result.irelpm.value == '1'


def test_load_structured_grid_file_iregion_multiple(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10
IREGION VALUE
INCLUDE /path/to/file.inc 
MOD
30 38  1  30  1  1  = 1       
IREGION inj_02 CON
3
MOD
30 38  1  30  1  1  = 1
MOD
31 39  1  30  1  1  = 1
IREGION inj_03 CON
4
IREGION inj_04 MULT
1 IEQUIL
LIST"""  # ends structured_grid_file_contents

    # set up dataframe
    i1 = [30, 31]
    i2 = [38, 39]
    j1 = [1, 1]
    j2 = [30, 30]
    k1 = [1, 1]
    k2 = [1, 1]
    v = ['=1', '=1']
    ireg1_expected_df = (
        pd.DataFrame({'i1': [30], 'i2': [38], 'j1': [1], 'j2': [30], 'k1': [1], 'k2': [1], '#v': ['=1']}))
    ireg2_expected_df = (
        pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v}))

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    # note that iregion is a dict
    assert result.iregion['IREG1'].keyword_in_include_file is False
    assert result.iregion['inj_02'].keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.iregion['IREG1'].mods['MOD'], ireg1_expected_df)
    pd.testing.assert_frame_equal(result.iregion['inj_02'].mods['MOD'], ireg2_expected_df)
    assert result.iregion['IREG1'].modifier == 'VALUE'
    assert result.iregion['inj_02'].modifier == 'CON'
    assert result.iregion['IREG1'].value == '/path/to/file.inc'
    assert result.iregion['IREG1'].absolute_path == '/path/to/file.inc'
    assert result.iregion['inj_02'].value == '3'
    assert result.iregion['inj_03'].value == '4'
    assert result.iregion['inj_03'].modifier == 'CON'
    assert result.iregion['inj_04'].value == '1 IEQUIL'
    assert result.iregion['inj_04'].modifier == 'MULT'


@pytest.mark.parametrize("structured_grid_file_contents, expected_net_to_gross, expected_porosity, expected_range_x,"
                         "expected_range_y, expected_range_z",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS VALUE\n INCLUDE /path_to_netgrs_file/include_net_to_gross.inc\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \nINCLUDE path/to/porosity.inc",
                              "/path_to_netgrs_file/include_net_to_gross.inc", "path/to/porosity.inc", 1, 2, 3),
                             ("! Grid dimensions\nNX NY NZ\n111 123 321\ntest string\nPOROSITY VALUE\n!random text\n"
                              "INCLUDE porosity_file.inc\nNETGRS VALUE\n!Comment Line 1\n\n!Comment Line 2\nINCLUDE   "
                              "/path/to/netgrs_file\nother text\n\n",
                              "/path/to/netgrs_file", "porosity_file.inc", 111, 123, 321)
                         ])
def test_load_structured_grid_file_basic_properties(mocker, structured_grid_file_contents,
                                                    expected_net_to_gross, expected_porosity, expected_range_x,
                                                    expected_range_y, expected_range_z):
    """Read in Structured Grid File"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.netgrs.value == expected_net_to_gross
    assert result.porosity.value == expected_porosity
    assert result.range_x == expected_range_x
    assert result.range_y == expected_range_y
    assert result.range_z == expected_range_z


def test_load_structured_grid_file_basic_properties_nested_includes(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
INCLUDE includes/Another_structured_grid_01.inc"""
    included_file_contents = """POROSITY CON\n 0.3\n ! Grid dimensions\nNX NY NZ\n3  4 5\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS VALUE\n 14 616 8371 81367136  \n 
                              !Should have stopped reading by this point \n POROSITY "
                              "CON 0.5\n"""
    included_file_location = os.path.join('testpath1', r'includes/Another_structured_grid_01.inc')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         included_file_location: included_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.porosity.value == '0.3'
    assert result.range_x == 3
    assert result.range_y == 4
    assert result.range_z == 5


@pytest.mark.parametrize("structured_grid_file_contents, expected_net_to_gross, expected_porosity,  "
                         "expected_ntg_modifier, expected_porosity_modifier, expected_range_x, expected_range_y, "
                         "expected_range_z",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS VALUE\n NOLIST\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\nLIST\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \nINCLUDE path/to/porosity.inc",
                              "/path_to_netgrs_file/net_to_gross.inc", "path/to/porosity.inc", "VALUE", "VALUE", 1, 2,
                              3),
                             ("! Grid dimensions\nNX NY NZ\n111 123 321\ntest string\nPOR VALUE\n!random text\n"
                              "INCLUDE porosity_file.inc\nNETGRS VALUE\n!Comment Line 1\n\n!Comment Line 2\nINCLUDE   "
                              "/path/to/netgrs_file\nother text\n\n",
                              "/path/to/netgrs_file", "porosity_file.inc", "VALUE", "VALUE", 111, 123, 321),
                             ("! Grid dimensions\nNX NY NZ\n999 9 9\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS CON\n 0.55\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \nINCLUDE path/to/porosity2.inc",
                              "0.55", "path/to/porosity2.inc", "CON", "VALUE", 999, 9, 9),
                             ("! Grid dimensions\nNX NY NZ\n8 5 \t6\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS VALUE\n\t INCLUDE ntg_file.dat\n POROSITY CON\n!ANOTHER COMMENT \n3",
                              "ntg_file.dat", "3", "VALUE", "CON", 8, 5, 6),
                             ("! Grid dimensions\nNX   NY   NZ\n69   30    1\ntest string\nDUMMY VALUE\n!ioeheih\ntext"
                              "\nother text\n\nNETGRS VALUE\n\t INCLUDE ntg_file.dat\n POROSITY CON\n!ANOTHER COMMENT \n3",
                              "ntg_file.dat", "3", "VALUE", "CON", 69, 30, 1),
                         ])
def test_load_structured_grid_file_dict_basic_properties(mocker, structured_grid_file_contents,
                                                         expected_net_to_gross, expected_porosity,
                                                         expected_ntg_modifier,
                                                         expected_porosity_modifier, expected_range_x, expected_range_y,
                                                         expected_range_z):
    """Read in Structured Grid File and return a dict object"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.get_structured_grid_dict()

    # Assert
    assert result['netgrs'].value == expected_net_to_gross
    assert result['netgrs'].modifier == expected_ntg_modifier
    assert result['porosity'].value == expected_porosity
    assert result['porosity'].modifier == expected_porosity_modifier
    assert result['range_x'] == expected_range_x
    assert result['range_y'] == expected_range_y
    assert result['range_z'] == expected_range_z


@pytest.mark.skip("Raising this error may no longer be required")
def test_load_structured_grid_file_fails(mocker):
    """Check that an error is raised if loading the structured grid file fails"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"

    structured_grid_mock = mocker.mock_open(read_data="")

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_multiple_opens(mocker, filename, fcs_file, "", "",
                                        structured_grid_mock=structured_grid_mock).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    with pytest.raises(ValueError):
        simulation = NexusSimulator(
            origin='testpath1/nexus_run.fcs', destination="new_destination")


@pytest.mark.parametrize("structured_grid_file_contents, expected_water_saturation_modifier, "
                         "expected_water_saturation_value",
                         [
                             ("SW VALUE\n INCLUDE /path/to/SW.inc",
                              "VALUE", "/path/to/SW.inc"),
                             ("SW CON\n0.6", "CON", "0.6"),
                             ("Random VALUE\nSW CON\n 0.33\nOTHER VALUE", "CON", "0.33"),
                             ("CON VALUE\nSW VALUE\t\nINCLUDE SW_FILE.inc",
                              "VALUE", "SW_FILE.inc"),
                         ])
def test_load_structured_grid_file_sw(mocker, structured_grid_file_contents,
                                      expected_water_saturation_modifier,
                                      expected_water_saturation_value):
    """Read in Structured Grid File"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    base_structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                                "\nother text\n\n,NETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc \n"

    structured_grid_file = base_structured_grid_file + structured_grid_file_contents
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.get_structured_grid_dict()

    # Assert
    assert result['sw'].modifier == expected_water_saturation_modifier
    assert result['sw'].value == expected_water_saturation_value


@pytest.mark.parametrize("structured_grid_file_contents, expected_kx_value,expected_kx_modifier, expected_ky_value, "
                         "expected_ky_modifier, expected_kz_value, expected_kz_modifier",
                         [
                             ("KX VALUE\n INCLUDE /path/to/kx.inc\nKY MULT\n12 KX\n KZ VALUE\n\n\n INCLUDE kz.inc",
                              "/path/to/kx.inc",
                              "VALUE", "12 KX", "MULT", "kz.inc", "VALUE"),
                             (
                                     "KX VALUE\n INCLUDE /path/to/kx.inc\nKY VALUE\n\tINCLUDE /path/to/kx.inc\n KZ MULT\n\n\n\t0.1 KX",
                                     "/path/to/kx.inc",
                                     "VALUE", "/path/to/kx.inc", "VALUE", "0.1 KX", "MULT"),
                             ("KX VALUE\n!Comment \n INCLUDE kx.inc\nKY MULT\n\t1 KX\n KZ MULT\n\n!3 KX\n 1 KX",
                              "kx.inc", "VALUE", "1 KX", "MULT", "1 KX", "MULT"),
                             (
                                     "KX MULT\n0.000001 KY\nKY VALUE\n\tINCLUDE ky.inc\n KZ VALUE\n!COMMENT test\n\n INCLUDE /path/to/kz.inc",
                                     "0.000001 KY", "MULT", "ky.inc", "VALUE", "/path/to/kz.inc", "VALUE"),
                             (
                                     "KX MULT\n 0.1 KY\nKY VALUE\n\t INCLUDE ky.inc\n KZ VALUE\n!COMMENT test\n\n INCLUDE /path/to/kz.inc",
                                     "0.1 KY", "MULT", "ky.inc", "VALUE", "/path/to/kz.inc", "VALUE"),
                             (
                                     "KX VALUE\n INCLUDE /path/to/kx.inc\nKY VALUE\n\tINCLUDE /path/to/kx.inc\n KZ MULT\n\n\n\t\n\t 0.1\tKX",
                                     "/path/to/kx.inc", "VALUE", "/path/to/kx.inc", "VALUE", "0.1 KX", "MULT"),
                             ("KX VALUE\n INCLUDE kx.inc\nKY MULT\n1 KX\n KZ MULT\n12 Ky",
                              "kx.inc", "VALUE", "1 KX", "MULT", "12 Ky", "MULT"),
                             ("KX CON\n 0.11333\nKY MULT\n1 KX\n KZ MULT\n12 Ky",
                              "0.11333", "CON", "1 KX", "MULT", "12 Ky", "MULT"),
                             ("PERMX CON\n 0.11333\nPERMY MULT\n1 PERMX\n PERMZ MULT\n12 PERMY",
                              "0.11333", "CON", "1 PERMX", "MULT", "12 PERMY", "MULT"),
                             ("PERMI CON\n 0.11333\nPERMJ MULT\n1 PERMI\n PERMK MULT\n12 PERMJ",
                              "0.11333", "CON", "1 PERMI", "MULT", "12 PERMJ", "MULT"),
                             ("KI CON\n 0.11333\nKJ MULT\n1 KI\n KK MULT\n12 KI",
                              "0.11333", "CON", "1 KI", "MULT", "12 KI", "MULT"),
                             (
                                     "!KX VALUE\nKX VALUE\n INCLUDE /path/to/kx.inc\nKY MULT\n12 KX\n KZ VALUE\n\n\n INCLUDE kz.inc",
                                     "/path/to/kx.inc",
                                     "VALUE", "12 KX", "MULT", "kz.inc", "VALUE"),
                         ])
def test_load_structured_grid_file_k_values(mocker, structured_grid_file_contents, expected_kx_value,
                                            expected_kx_modifier, expected_ky_value, expected_ky_modifier,
                                            expected_kz_value, expected_kz_modifier):
    """Read in Structured Grid File"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    base_structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                                "\nother text\n\n,NETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc \n"

    structured_grid_file = base_structured_grid_file + structured_grid_file_contents
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         "/path/to/kz.inc": '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.kx.modifier == expected_kx_modifier
    assert result.kx.value == expected_kx_value
    assert result.ky.modifier == expected_ky_modifier
    assert result.ky.value == expected_ky_value
    assert result.kz.modifier == expected_kz_modifier
    assert result.kz.value == expected_kz_value


def test_load_structured_grid_file_keff_values(mocker):
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    base_structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                                "\nother text\n\n,NETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc \n"

    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file = (base_structured_grid_file +
                            "KXEFF VALUE\n INCLUDE /path/to/kxeff.inc\n KYEFF CON \n2 \n KZEFF VALUE \nINCLUDE\n kzeff.inc")

    expected_value_kxeff = "/path/to/kxeff.inc"
    expected_value_kyeff = "2"
    expected_value_kzeff = "kzeff.inc"
    expected_modifier_kxeff = "VALUE"
    expected_modifier_kyeff = "CON"
    expected_modifier_kzeff = "VALUE"

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         "/path/to/kz.inc": '',
         '/path/to/kxeff.inc': '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.kxeff.value == expected_value_kxeff
    assert result.kxeff.modifier == expected_modifier_kxeff
    assert result.kyeff.value == expected_value_kyeff
    assert result.kyeff.modifier == expected_modifier_kyeff
    assert result.kzeff.value == expected_value_kzeff
    assert result.kzeff.modifier == expected_modifier_kzeff


@pytest.mark.parametrize("new_porosity, new_sw, new_netgrs, new_kx, new_ky, new_kz",
                         [
                             (GridArrayDefinition("VALUE", "porosity_2.inc"),
                              GridArrayDefinition("CON", "0.33"),
                              GridArrayDefinition("VALUE", "/new/netgrs_2.inc"),
                              GridArrayDefinition("VALUE", "KX.INC"),
                              GridArrayDefinition("MULT", "0.1 KX"),
                              GridArrayDefinition("VALUE", "path/to/kz.inc")),

                             (GridArrayDefinition("VALUE", "porosity_2.inc"),
                              GridArrayDefinition("CON", "0.33"),
                              GridArrayDefinition("VALUE", "/new/netgrs_2.inc"),
                              GridArrayDefinition("VALUE", "KX.INC"),
                              GridArrayDefinition("CON", "1.111113"),
                              GridArrayDefinition("VALUE", "path/to/kz.inc")),

                             (GridArrayDefinition("VALUE", "/path/porosity_2.inc"),
                              GridArrayDefinition("VALUE", "sw_file.inc"),
                              GridArrayDefinition("VALUE", "/new/netgrs_2.inc"),
                              GridArrayDefinition("CON", "123"),
                              GridArrayDefinition("CON", "1.111113"),
                              GridArrayDefinition("MULT", "1 KX")),

                             (GridArrayDefinition("CON", "123456"),
                              GridArrayDefinition("CON", "0.000041"),
                              GridArrayDefinition("CON", "1.1"),
                              GridArrayDefinition("MULT", "0.1 KY"),
                              GridArrayDefinition("CON", "1.111113"),
                              GridArrayDefinition("MULT", "10 KX")),

                             (GridArrayDefinition("VALUE", "/path/porosity/file.inc"),
                              GridArrayDefinition("VALUE", "sw_file2.inc"),
                              GridArrayDefinition("VALUE", "netgrs_3.inc"),
                              GridArrayDefinition("VALUE", "path/to/kx.inc"),
                              GridArrayDefinition("VALUE", "path/to/ky.inc"),
                              GridArrayDefinition("VALUE", "path/to/KZ.inc")),
                         ])
def test_save_structured_grid_values(mocker, new_porosity, new_sw, new_netgrs, new_kx, new_ky, new_kz):
    """Test saving values passed from the front end to the structured grid file and update the class"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"

    structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                           "\nother text\n\n NETGRS VALUE\n\n!C\n\n  INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                           "VALUE\n !ANOTHER COMMENT \n\tINCLUDE path/to/porosity.inc\nKX MULT\n 0.1 KY\nKY VALUE\n\t INCLUDE ky.inc\n " \
                           "KZ VALUE\n!COMMENT test\n\n INCLUDE /path/to/kz.inc !Comment\n\t SW VALUE\n INCLUDE sw_file.inc"

    new_structured_grid_dictionary = {"porosity": new_porosity, "sw": new_sw, "netgrs": new_netgrs, "kx": new_kx,
                                      "ky": new_ky, "kz": new_kz}

    expected_output_file = f"! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                           f"\nother text\n\n NETGRS {new_netgrs.modifier}\n\n!C\n\n" \
                           f"  {'INCLUDE ' if new_netgrs.modifier == 'VALUE' else ''} {new_netgrs.value}\n POROSITY " \
                           f"{new_porosity.modifier}\n !ANOTHER COMMENT \n" \
                           f"\t{'INCLUDE ' if new_porosity.modifier == 'VALUE' else ''}{new_porosity.value}" \
                           f"\nKX {new_kx.modifier}\n {'INCLUDE ' if new_kx.modifier == 'VALUE' else ''}{new_kx.value}\n" \
                           f"KY {new_ky.modifier}\n\t {'INCLUDE ' if new_ky.modifier == 'VALUE' else ''}" \
                           f"{new_ky.value}\n KZ {new_kz.modifier}\n!COMMENT test\n\n" \
                           f" {'INCLUDE ' if new_kz.modifier == 'VALUE' else ''}{new_kz.value} !Comment\n\t SW {new_sw.modifier}\n" \
                           f"{' INCLUDE' if new_sw.modifier == 'VALUE' else ''} {new_sw.value}"

    structured_grid_mock = mocker.mock_open(read_data=structured_grid_file)
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         "/path/to/kz.inc": '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    mocker.patch("builtins.open", structured_grid_mock)

    # Act
    NexusGrid.update_structured_grid_file(new_structured_grid_dictionary, simulation)
    result = simulation.grid

    # Assert

    # Check the newly written file is as expected
    structured_grid_mock.assert_called_with(structured_grid_name, 'w')
    structured_grid_mock.return_value.write.assert_called_with(
        expected_output_file)

    # Check that the class properties have been updated
    assert result.porosity == new_porosity
    assert result.netgrs == new_netgrs
    assert result.sw == new_sw
    assert result.kx == new_kx
    assert result.ky == new_ky
    assert result.kz == new_kz


@pytest.mark.parametrize("structured_grid_file_contents, expected_text",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n "
                              "POROSITY VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc",
                              "dummy text\nother text\n\nNETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc"
                              "\n POROSITY VALUE\n"),
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS CON\n 1.11111\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \nINCLUDE path/to/porosity.inc",
                              "dummy text\nother text\n\nNETGRS CON\n 1.11111\n POROSITY VALUE\n"),
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\tNETGRS VALUE\n INCLUDE NETGRS_FILE.inc !Inline Comment\n !Comment "
                              "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc",
                              "!ioeheih\ndummy text\nother text\n\tNETGRS VALUE\n INCLUDE NETGRS_FILE.inc !Inline Comment"
                              "\n !Comment VALUE\n"),
                         ])
def test_view_command(mocker, structured_grid_file_contents, expected_text):
    """Test the View Command functionality"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_name_quotes = os.path.join('testpath1', '\"test_structured_grid.dat\"')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         structured_grid_name_quotes: structured_grid_file_contents,
         '/path_to_netgrs_file/include_net_to_gross.inc': '',
         'path/to/porosity.inc': '',
         "/path/to/kz.inc": '',
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    result = NexusSimulator(origin='testpath1/nexus_run.fcs')

    # Assert
    value = result._structured_grid_operations.view_command(field='netgrs')
    assert value == expected_text


@pytest.mark.parametrize("fcs_file, expected_root, expected_extracted_path",
                         [
                             (
                                     'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID\n /path/to/structured/grid.dat',
                                     '', '/path/to/structured/grid.dat'),
                             (
                                     'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID\n path/to/other_structured/grid.dat',
                                     'testpath1', 'path/to/other_structured/grid.dat'),
                             (
                                     'RUNControl run_control.inc\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_grid\n structured/grid.dat',
                                     'testpath1', 'structured/grid.dat'),
                             (
                                     'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nStructured_GRID\n path/to/include_locations/grid.dat',
                                     'testpath1', 'path/to/include_locations/grid.dat'),
                             (
                                     'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nstructured_grid\n path/to/include_locations/grid.dat',
                                     'testpath1', 'path/to/include_locations/grid.dat'),
                         ])
def test_get_abs_structured_grid_path(mocker, fcs_file, expected_root, expected_extracted_path):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_result = os.path.join(expected_root, expected_extracted_path)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')
    result = simulation.get_abs_structured_grid_path('grid.dat')

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("structured_grid_file_contents, expected_results",
                         [
                             ("""

      KX VALUE
      INCLUDE BLAH/BLAH

      MULT TX ALL PLUS MULT
       FNAME F1
       1 5 2 2 1 10 1.0
       6 9 2 2 1 10 0.1

      MULT TY ALL PLUS MULT
       FNAME F1
       1 1 2 5 1 10 1.0
       1 1 6 9 1 10 0.0

      MULT TX ALL MINUS MULT
       FNAME F2
       1 5 4 4 1 10 1.0
       6 9 4 4 1 10 1.0

      MULT TY ALL PLUS MULT
       FNAME F2
       3 3 2 5 1 10 1.0
       3 3 6 9 1 10 1.0

    """, pd.DataFrame({'I1': [1, 6, 1, 1, 1, 6, 3, 3],
                       'I2': [5, 9, 1, 1, 5, 9, 3, 3],
                       'J1': [2, 2, 2, 6, 4, 4, 2, 6],
                       'J2': [2, 2, 5, 9, 4, 4, 5, 9],
                       'K1': [1, 1, 1, 1, 1, 1, 1, 1],
                       'K2': [10, 10, 10, 10, 10, 10, 10, 10],
                       'MULT': [1.0, 0.1, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0],
                       'GRID': ['ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT'],
                       'NAME': ['F1', 'F1', 'F1', 'F1', 'F2', 'F2', 'F2', 'F2'],
                       'FACE': ['I', 'I', 'J', 'J', 'I-', 'I-', 'J', 'J']}
                      )
                              ),
                             ("""

      KX VALUE
      INCLUDE BLAH/BLAH

    """, None
                              ),
                             ("""

      KX VALUE
      INCLUDE BLAH/BLAH

      MULT TX ALL PLUS MULT
       FNAME F1
       1 5 2 2 1 10 1.0
       6 9 2 2 1 10 0.1

      MULT TY ALL PLUS MULT
       FNAME F1
       1 1 2 5 1 10 1.0
       1 1 6 9 1 10 0.0

      MULT TX ALL MINUS MULT
       FNAME F2
       1 5 4 4 1 10 1.0
       6 9 4 4 1 10 1.0

      MULT TY ALL PLUS MULT
       FNAME F2
       3 3 2 5 1 10 1.0
       3 3 6 9 1 10 1.0

      MULTFL F1 0.0

      MULTFL F2 0.1

      MULTFL F2 0.2

    """, pd.DataFrame({'I1': [1, 6, 1, 1, 1, 6, 3, 3],
                       'I2': [5, 9, 1, 1, 5, 9, 3, 3],
                       'J1': [2, 2, 2, 6, 4, 4, 2, 6],
                       'J2': [2, 2, 5, 9, 4, 4, 5, 9],
                       'K1': [1, 1, 1, 1, 1, 1, 1, 1],
                       'K2': [10, 10, 10, 10, 10, 10, 10, 10],
                       'MULT': [0.0, 0.0, 0.0, 0.0, 0.02, 0.02, 0.02, 0.02],
                       'GRID': ['ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT'],
                       'NAME': ['F1', 'F1', 'F1', 'F1', 'F2', 'F2', 'F2', 'F2'],
                       'FACE': ['I', 'I', 'J', 'J', 'I-', 'I-', 'J', 'J']}
                      )
                              )
                         ], ids=['basic_nomultfl', 'no_faults', 'basic_w_multfl']
                         )
def test_load_faults(mocker, structured_grid_file_contents, expected_results):
    """Read in Structured Grid File and test extraction of fault information"""
    # Arrange
    fcs_path = 'testpath1/nexus_run.fcs'
    fcs_file = "DESC test fcs file\nDATEFORMAT MM/DD/YYYY\nGRID_FILES\n\tSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_path = os.path.join('testpath1', 'test_structured_grid.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {fcs_path: fcs_file,
         structured_grid_path: structured_grid_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # explicitly set datatype to int32
    if expected_results is not None:
        expected_results = expected_results.astype({'I1': 'int32', 'I2': 'int32', 'J1': 'int32', 'J2': 'int32',
                                                    'K1': 'int32', 'K2': 'int32'})

    # Act
    simulation = NexusSimulator(origin=fcs_path)
    faults_df = simulation.grid.get_faults_df()

    if faults_df is not None:
        faults_df = faults_df.astype({'I1': 'int32', 'I2': 'int32', 'J1': 'int32', 'J2': 'int32',
                                      'K1': 'int32', 'K2': 'int32'})
    # Assert
    if expected_results is None:
        assert expected_results == faults_df
    else:
        pd.testing.assert_frame_equal(expected_results, faults_df)


def test_included_fault_tables(mocker):
    # Arrange
    fcs_path = 'testpath1/nexus_run.fcs'
    fcs_file = "DESC test fcs file\nDATEFORMAT MM/DD/YYYY\nGRID_FILES\n\tSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_path = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = '''KX VALUE
        INCLUDE kx_file.dat
        
        MULT TX ALL PLUS MULT
       FNAME F1
       1 5 2 2 1 10 1.0
       6 9 2 2 1 10 0.1
       
       INCLUDE faults_inc.inc
       !something else 
         
    '''
    kx_file_content = '0 1 0 2 0 3 0 4 100 1200\n 102023 9014 109 1293 2727'
    kx_path = os.path.join('testpath1', 'kx_file.dat')
    include_file_path = os.path.join('testpath1', 'faults_inc.inc')
    include_file = '''     MULT TY ALL PLUS MULT
       FNAME F1
       1 1 2 5 1 10 1.0
       1 1 6 9 1 10 0.0

      MULT TX ALL MINUS MULT
       FNAME F2
       1 5 4 4 1 10 1.0
       6 9 4 4 1 10 1.0

      MULT TY ALL PLUS MULT
       FNAME F2
       3 3 2 5 1 10 1.0
       3 3 6 9 1 10 1.0

      MULTFL F1 0.0

      MULTFL F2 0.1

      MULTFL F2 0.2'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {fcs_path: fcs_file,
         structured_grid_path: structured_grid_file_contents,
         include_file_path: include_file,
         kx_path: kx_file_content,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_df = pd.DataFrame({
        'I1': [1, 6, 1, 1, 1, 6, 3, 3],
        'I2': [5, 9, 1, 1, 5, 9, 3, 3],
        'J1': [2, 2, 2, 6, 4, 4, 2, 6],
        'J2': [2, 2, 5, 9, 4, 4, 5, 9],
        'K1': [1, 1, 1, 1, 1, 1, 1, 1],
        'K2': [10, 10, 10, 10, 10, 10, 10, 10],
        'MULT': [0.0, 0.0, 0.0, 0.0, 0.02, 0.02, 0.02, 0.02],
        'GRID': ['ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT'],
        'NAME': ['F1', 'F1', 'F1', 'F1', 'F2', 'F2', 'F2', 'F2'],
        'FACE': ['I', 'I', 'J', 'J', 'I-', 'I-', 'J', 'J']}
    )

    comparison_types = {'I1': 'int32', 'I2': 'int32', 'J1': 'int32', 'J2': 'int32',
                        'K1': 'int32', 'K2': 'int32'}

    expected_df = expected_df.astype(comparison_types)
    # Act
    simulation = NexusSimulator(origin=fcs_path)
    faults_df = simulation.grid.get_faults_df()
    faults_df = faults_df.astype(comparison_types)
    # Assert
    pd.testing.assert_frame_equal(expected_df, faults_df)


def test_load_structured_grid_file_nocorp(mocker):
    """Read in Structured Grid File where properties are in a nested include file"""
    # Arrange
    fcs_file_contents = "RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
 5   5   3

DX VALUE
75*100

DY CON
100

DZ CON
10

DZNET CON
9

DEPTH LAYER
25*5000

MDEPTH LAYER
25*5005

SG ZVAR
1.
2*0

SW ZVAR
2*0
1.

P ZVAR
1000
1100
1200

TEMP ZVAR
100
101
102

COMPR CON
3e-6

ICOARS CON
1

IALPHAF CON
1

IPOLYMER CON
1

IADSORPTION CON
1

ISECTOR CON
1
MOD
30 38  1  30  1  1  =1
C 13 20  1 30  1  1  =1
25 32  1 30  1  1  =1

ITRACER CON
1

IGRID CON
1

SWL CON
0.

SWR CON
0.1

SWU CON
1

SGL CON
0

SGR CON
0.01

SGU CON
1.0

SWRO CON
0.9

SWRO_LS CON
0.95

SGRO CON
0.8

SGRW CON
0.8

KRW_SWRO CON
1

KRWS_LS CON
1

KRW_SWU CON
1

KRG_SGRO CON
1

KRG_SGU CON
1

KRG_SGRW CON
1

KRO_SWL CON
1

KRO_SWR CON
0.9

KRO_SGL CON
1

KRO_SGR CON
1

KRW_SGL CON
1

KRW_SGL CON
1

KRW_SGR CON
0.9

SGTR CON
.2

SOTR CON
0.1

SWLPC CON
0.2

SGLPC CON
0.1

PCW_SWL CON
5

PCG_SGU CON
6

CHLORIDE CON
0.3

CALCIUM CON
0.03

SALINITY CON
1.1

API CON
20

TMX CON
1

TMY CON
1

TMZ CON
1

MULTBV CON
1

PV CON
20000

LIST"""  # ends structured_grid_file_contents

    # set up dataframe
    i1 = [30, 25]
    i2 = [38, 32]
    j1 = [1, 1]
    j2 = [30, 30]
    k1 = [1, 1]
    k2 = [1, 1]
    v = ['=1', '=1']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'testpath1/nexus_run.fcs': fcs_file_contents, '/run_control/path': '',
            structured_grid_name: structured_grid_file_contents}).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    # note that iregion is a dict
    assert result.isector.keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.isector.mods['MOD'], expected_df)
    assert result.dx.modifier == 'VALUE'
    assert result.dx.value == '75*100'
    assert result.dy.value == '100'
    assert result.dz.value == '10'
    assert result.dznet.value == '9'
    assert result.depth.modifier == 'LAYER'
    assert result.depth.value == '25*5000'
    assert result.mdepth.value == '25*5005'
    assert result.sg.modifier == 'ZVAR'
    assert result.sg.value == '1.\n2*0'
    assert result.sw.value == '2*0\n1.'
    assert result.pressure.value == '1000\n1100\n1200'
    assert result.temperature.value == '100\n101\n102'
    assert result.compr.value == '3e-6'
    assert result.icoars.value == '1'
    assert result.ialphaf.value == '1'
    assert result.ipolymer.value == '1'
    assert result.iadsorption.value == '1'
    assert result.itracer.value == '1'
    assert result.igrid.value == '1'
    assert result.swl.value == '0.'
    assert result.swr.value == '0.1'
    assert result.swu.value == '1'
    assert result.sgl.value == '0'
    assert result.sgr.value == '0.01'
    assert result.sgu.value == '1.0'
    assert result.swro.value == '0.9'
    assert result.swro_ls.value == '0.95'
    assert result.sgro.value == '0.8'
    assert result.sgrw.value == '0.8'
    assert result.krw_swro.value == '1'
    assert result.krws_ls.value == '1'
    assert result.krw_swu.value == '1'
    assert result.krg_sgro.value == '1'
    assert result.krg_sgu.value == '1'
    assert result.krg_sgrw.value == '1'
    assert result.kro_swl.value == '1'
    assert result.kro_swr.value == '0.9'
    assert result.kro_sgl.value == '1'
    assert result.kro_sgr.value == '1'
    assert result.krw_sgl.value == '1'
    assert result.krw_sgr.value == '0.9'
    assert result.sgtr.value == '.2'
    assert result.sotr.value == '0.1'
    assert result.swlpc.value == '0.2'
    assert result.sglpc.value == '0.1'
    assert result.pcw_swl.value == '5'
    assert result.pcg_sgu.value == '6'
    assert result.chloride.value == '0.3'
    assert result.calcium.value == '0.03'
    assert result.salinity.value == '1.1'
    assert result.api.value == '20'
    assert result.tmx.value == '1'
    assert result.tmy.value == '1'
    assert result.tmz.value == '1'
    assert result.multbv.value == '1'
    assert result.pv.value == '20000'


def test_nested_includes_with_grid_array_keywords(mocker):
    # Arrange

    structured_grid_path = '/nexus_files/test_structured_grid.dat'
    fcs_file_contents = (f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID "
                         f"{structured_grid_path}")
    structured_grid_file_contents = '''! Array data
    KX VALUE
    INCLUDE /inc_file_kx.inc
    
    INCLUDE grid/inc_file1.inc'''

    include_file_location = os.path.join('/nexus_files', 'grid/inc_file1.inc')
    include_file_location_2 = os.path.join('/nexus_files/grid', 'inc_file2.inc')
    include_file_location_kx = '/inc_file_kx.inc'

    include_file_contents = ('''KY VALUE 
                                INCLUDE inc_file2.inc
                                ''')
    include_file_contents_2 = 'some content\n that should\n be skipped'
    include_file_contents_kx = 'some content that should be skipped'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_path: structured_grid_file_contents,
         include_file_location: include_file_contents,
         include_file_location_2: include_file_contents_2,
         include_file_location_kx: include_file_contents_kx
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    sim_obj = NexusSimulator(origin='/nexus_run.fcs')

    expected_kx_result = GridArrayDefinition(modifier='VALUE', value='/inc_file_kx.inc', mods=None,
                                             absolute_path='/inc_file_kx.inc')
    expected_ky_result = GridArrayDefinition(modifier='VALUE', value='inc_file2.inc', mods=None,
                                             absolute_path=os.path.join('/nexus_files', 'grid', 'inc_file2.inc'))

    # Act
    result_kx = sim_obj.grid.kx
    result_ky = sim_obj.grid.ky

    # Assert
    assert result_kx == expected_kx_result
    assert result_ky == expected_ky_result


@pytest.mark.parametrize('structured_grid_file_contents, modifier, full_file_path, expected_value', [
    ('''! Array data
    KX VALUE
    INCLUDE inc_file_kx.inc''', 'VALUE', os.path.join('/root', 'nexus_files/grid', 'inc_file_kx.inc'),
     'inc_file_kx.inc'),
    ('''! Array data
     KX ZVAR
     INCLUDE inc_file_kx.inc''', 'ZVAR', os.path.join('/root', 'nexus_files/grid', 'inc_file_kx.inc'),
     'inc_file_kx.inc'),
    ('''! Array data
    KX YVAR
    INCLUDE inc_file_kx.inc''', 'YVAR', os.path.join('/root', 'nexus_files/grid', 'inc_file_kx.inc'),
     'inc_file_kx.inc'),
    # Value directly in grid file
    ('''! Array data
    KX VALUE
    1 2 3 4''', 'VALUE', None, '1 2 3 4'),
])
def test_grid_array_definitions_abs_path(mocker, structured_grid_file_contents, modifier,
                                         full_file_path, expected_value):
    # Arrange
    fcs_path = '/root/nexus_run.fcs'
    structured_grid_path = 'nexus_files/grid/test_structured_grid.dat'
    fcs_file_contents = (f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID "
                         f"{structured_grid_path}")

    full_structured_grid_path = os.path.join('/root', structured_grid_path)
    include_file_contents_kx = 'some content that should be skipped'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {fcs_path: fcs_file_contents,
         '/run_control/path': '',
         full_structured_grid_path: structured_grid_file_contents,
         full_file_path: include_file_contents_kx,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    sim_obj = NexusSimulator(origin=fcs_path)

    expected_kx_result = GridArrayDefinition(modifier=modifier, value=expected_value, mods=None,
                                             absolute_path=full_file_path)

    # Act
    result_kx = sim_obj.grid.kx

    # Assert
    assert result_kx == expected_kx_result


def test_load_structured_grid_file_excludes_skip_section(mocker):
    """Read in Structured Grid File, excluding the section marked with SKIP / NOSKIP"""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """
! grid
NX  NY  NZ
! 4 5   6
1   2   3

SKIP ! Start excluding these values
DY CON
100

DZ CON
10

NX  NY  NZ  !change in values should be ignored
7   8     9

NOSKIP ! Stop excluding and take the remaining values
DZNET CON
9

"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.range_x == 1
    assert result.range_y == 2
    assert result.range_z == 3
    assert result.dznet.value == '9'
    assert result.dx.value is None
    assert result.dy.value is None
    assert result.dz.value is None


def test_load_arrays_with_different_grid_names_to_lgr_class(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """NX  NY  NZ
 80  86  84

CARTREF lgr_01                         
  14  20   29  29  1  10  ! comment
  
  6*5  1*7 6*5
  9   ! comment
  
  10*1
ENDREF 
ENDLGR


ARRAYS

KX CON
100

KY CON
10

ARRAYS lgr_01

KX  ZVAR 
INCLUDE  KX_file.dat

KY CON
1
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_lgr = NexusLGR(parent_grid='ROOT', name='lgr_01', i1=14, i2=20, j1=29, j2=29, k1=1, k2=10,
                            nx=[5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 5],
                            ny=[9],
                            nz=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                            )
    expected_lgr._kx = GridArrayDefinition(modifier='ZVAR', value='KX_file.dat',
                                           absolute_path=os.path.join('testpath1', 'KX_file.dat'))
    expected_lgr._ky = GridArrayDefinition(modifier='CON', value='1')
    expected_root_kx = GridArrayDefinition(modifier='CON', value='100')
    expected_root_ky = GridArrayDefinition(modifier='CON', value='10')

    model = NexusSimulator('testpath1/nexus_run.fcs')
    # Act
    result = model.grid
    result_lgr = result.lgrs.lgrs[0]

    # assert
    assert result.kx == expected_root_kx
    assert result.ky == expected_root_ky
    assert result_lgr == expected_lgr
    assert result_lgr.kx == expected_lgr._kx
    assert result_lgr.ky == expected_lgr._ky
    assert len(result.lgrs.lgrs) == 1


def test_load_lgrs(mocker):
    input_run_control = "START 01/07/2023"
    input_nexus_fcs_file = """DATEFORMAT DD/MM/YYYY
        GRID_FILES
            STRUCTURED_GRID    /path/to/grid/file.dat

        RECURRENT_FILES
            RUNCONTROL /path/to/run_control.dat

        SURFACE Network 1  /surface_file_01.dat

        """
    input_grid_file = """

    NX NY NZ
    69 30  1

    KX VALUE
    INCLUDE BLAH/BLAH

    KY CON
    200.50

    LGR
    CARTREF lgr_01                         
      14  20   29  29  1  1
      6*5  1*7 6*5
      9
      10*1
    ENDREF 
    ENDLGR

    ARRAYS lgr_01
    KX VALUE
    INCLUDE permx_array.dat

    """

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/to/nexus/fcsfile.dat': input_nexus_fcs_file,
            '/path/to/run_control.dat': input_run_control,
            '/path/to/grid/file.dat': input_grid_file,
            '/surface_file_01.dat': ''
        }
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)

    def mock_isfile(filename):
        if '_filtered' in filename:
            return False
        return True

    mocker.patch("os.path.isfile", mock_isfile)
    mocker.patch("os.path.exists", mock_isfile)
    expected_output_file_name = os.path.join('/path/to/new/test/location', 'MY_NEW_MODEL.DATA')
    # Act
    nexus_model = NexusSimulator(origin='/path/to/nexus/fcsfile.dat')
    kx_array = nexus_model.grid.kx
    lgr_kx_array = nexus_model.grid.lgrs.lgrs[0].kx

    # Assert
    assert kx_array.modifier == 'VALUE'
    assert kx_array.value == 'BLAH/BLAH'
    assert lgr_kx_array.modifier == 'VALUE'
    assert lgr_kx_array.value == 'permx_array.dat'


def test_load_grid_new_bug(mocker):
    # Arrange
    input_run_control = "START 01/07/2023"
    input_nexus_fcs_file = """DATEFORMAT DD/MM/YYYY
            GRID_FILES
                STRUCTURED_GRID    /path/to/grid/file.dat

            RECURRENT_FILES
                RUNCONTROL /path/to/run_control.dat

            SURFACE Network 1  /surface_file_01.dat

            """
    input_grid_file = """
! GRID DEFINITION   
MAPOUT ALL

NX NY NZ
 57  57  82

LGR
CARTREF lgr1                         
  14  44   29  29  1  82
  15*5  1*5 15*5
  9
  82*1
ENDREF 
ENDLGR


DECOMP
ROOT      4   4  3
lgr1    16  1  3
ENDDEC

ARRAYS 

DX  CON                          
116.0                                                                                                                                                             
DY  CON                                                                                                                                                            
116.0

POROSITY ZVAR
INCLUDE PORO.dat

KX  ZVAR 
INCLUDE  KX.dat
MOD
      1   57    1    57    1   82 *1.10  

KY  ZVAR
INCLUDE  KX.dat
MOD
      1   57    1    57    1   82 *1.10 
	  
KZ  ZVAR  
INCLUDE  KX.dat
MOD
      1   57    1    57    1   82 *1.10 
	  
NETGRS  CON                                                                                                                                                            
1.0

SW  ZVAR  
INCLUDE  SW.dat

"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/to/nexus/fcsfile.dat': input_nexus_fcs_file,
            '/path/to/run_control.dat': input_run_control,
            '/path/to/grid/file.dat': input_grid_file,
            '/surface_file_01.dat': ''
        }
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)

    def mock_isfile(filename):
        if '_filtered' in filename:
            return False
        return True

    mocker.patch("os.path.isfile", mock_isfile)
    mocker.patch("os.path.exists", mock_isfile)

    expected_sw = GridArrayDefinition(modifier='ZVAR', value='SW.dat',
                                      absolute_path=os.path.join('/path/to/grid', 'SW.dat'))
    expected_kz = GridArrayDefinition(modifier='ZVAR', value='KX.dat',
                                      absolute_path=os.path.join('/path/to/grid', 'KX.dat'),
                                      mods={'MOD': pd.DataFrame({'i1': [1], 'i2': [57], 'j1': [1], 'j2': [57],
                                                                 'k1': [1], 'k2': [82], '#v': ['*1.10']})})
    expected_kx = GridArrayDefinition(modifier='ZVAR', value='KX.dat',
                                      absolute_path=os.path.join('/path/to/grid', 'KX.dat'),
                                      mods={'MOD': pd.DataFrame({'i1': [1], 'i2': [57], 'j1': [1], 'j2': [57],
                                                                 'k1': [1], 'k2': [82], '#v': ['*1.10']})})

    nexus_model = NexusSimulator(origin='/path/to/nexus/fcsfile.dat')

    # Act
    result_sw = nexus_model.grid.sw
    result_kz = nexus_model.grid.kz
    result_kx = nexus_model.grid.kx

    # Assert
    assert nexus_model.grid.ky.absolute_path is not None
    assert result_sw == expected_sw

    assert result_kz.value == expected_kz.value
    assert result_kz.modifier == expected_kz.modifier
    assert result_kz.absolute_path == expected_kz.absolute_path
    pd.testing.assert_frame_equal(result_kz.mods['MOD'], expected_kz.mods['MOD'])

    assert result_kx.value == expected_kx.value
    assert result_kx.modifier == expected_kx.modifier
    assert result_kx.absolute_path == expected_kx.absolute_path
    pd.testing.assert_frame_equal(nexus_model.grid.kx.mods['MOD'], expected_kx.mods['MOD'])


def test_load_arrays_with_different_grid_names_to_lgr_class_none_keyword(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """NX  NY  NZ
 80  86  84

CARTREF LGR_01                         
  14  44   29  29  1  82
  15*5  1*5 15*5
  9
  82*1
ENDREF 
ENDLGR

ARRAYS LGR_01

KX  NONE
MOD 
    1   155    5    5      1   82 =1000.00  

IREGION NONE
MOD
1 10  1  10 1  1  =1
11 20  1  10 2  2  =2

"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_lgr = NexusLGR(parent_grid='ROOT', name='LGR_01', i1=14, i2=44, j1=29, j2=29, k1=1, k2=82,
                            nx=[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                                5, 5],
                            ny=[9],
                            nz=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    # set up dataframe
    i1 = [1]
    i2 = [155]
    j1 = [5]
    j2 = [5]
    k1 = [1]
    k2 = [82]
    v = ['=1000.00']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    expected_lgr._kx = GridArrayDefinition(modifier=None, value=None, mods={'MOD': expected_df},
                                           keyword_in_include_file=False, absolute_path=None, array=None)
    expected_lgr._iregion = {'IREG1': GridArrayDefinition(modifier=None, value=None, mods={'MOD': pd.DataFrame(
        {'i1': [1, 11], 'i2': [10, 20], 'j1': [1, 1], 'j2': [10, 10], 'k1': [1, 2], 'k2': [1, 2], '#v': ['=1', '=2']})},
                                                          keyword_in_include_file=False, absolute_path=None,
                                                          array=None)}

    model = NexusSimulator('testpath1/nexus_run.fcs')
    # Act
    result = model.grid
    result_lgr = result.lgrs.lgrs[0]
    result_iregion = result_lgr.iregion['IREG1']

    # Assert
    pd.testing.assert_frame_equal(result_lgr.kx.mods['MOD'], expected_lgr.kx.mods['MOD'])
    assert result_lgr.kx.value == expected_lgr.kx.value
    assert result_lgr.kx.modifier == expected_lgr.kx.modifier
    assert len(result.lgrs.lgrs) == 1
    assert result_iregion.value == expected_lgr._iregion['IREG1'].value
    assert result_iregion.modifier == expected_lgr._iregion['IREG1'].modifier
    pd.testing.assert_frame_equal(result_iregion.mods['MOD'], expected_lgr._iregion['IREG1'].mods['MOD'])


def test_load_arrays_with_mods_in_include_files(mocker):
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """NX  NY  NZ
 80  86  84

CARTREF LGR_01                         
  14  44   29  29  1  82
  15*5  1*5 15*5
  9
  82*1
ENDREF 
ENDLGR

ARRAYS LGR_01

KX  NONE
MOD 
!20 2 02 50 2 02 =1000.00
INCLUDE kx_mod.mod

IREGION NONE
MOD
! 1 1 1 2 2 2 *10
INCLUDE iregion_mod.mod

"""
    kx_mod_path = os.path.join('testpath1', 'kx_mod.mod')
    kx_mod_content = '''79          79           5           5           8           8 =   1.89576540E-02 ! A comment
           77          77           5           5           8           8 =   1.89576540E-02
           78          78           5           5           8           8 =  0.240092114    
           79          79           5           5           9           9 =   977.063721  
           77          77           5           5           9           9 =   977.063721
           80          80           5           5           9           9 =   915.068970
'''
    iregion_mod_path = os.path.join('testpath1', 'iregion_mod.mod')
    iregion_mod_content = '''1           10           1           10           1           1 =  1
              11           20           1           10           2           2 =  2
              '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         kx_mod_path: kx_mod_content,
         iregion_mod_path: iregion_mod_content,
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_lgr = NexusLGR(parent_grid='ROOT', name='LGR_01', i1=14, i2=44, j1=29, j2=29, k1=1, k2=82,
                            nx=[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                                5, 5],
                            ny=[9],
                            nz=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    # set up dataframe
    i1 = [79, 77, 78, 79, 77, 80]
    i2 = [79, 77, 78, 79, 77, 80]
    j1 = [5, 5, 5, 5, 5, 5]
    j2 = [5, 5, 5, 5, 5, 5]
    k1 = [8, 8, 8, 9, 9, 9]
    k2 = [8, 8, 8, 9, 9, 9]
    v = ['=0.018957654', '=0.018957654', '=0.240092114', '=977.063721', '=977.063721', '=915.06897']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})
    expected_lgr._kx = GridArrayDefinition(modifier=None, value=None, mods={'MOD': expected_df},
                                           keyword_in_include_file=False, absolute_path=None, array=None)
    # set up iregion dataframe
    expected_lgr._iregion = {'IREG1': GridArrayDefinition(modifier=None, value=None, mods={'MOD': pd.DataFrame(
        {'i1': [1, 11], 'i2': [10, 20], 'j1': [1, 1], 'j2': [10, 10], 'k1': [1, 2], 'k2': [1, 2], '#v': ['=1', '=2']})},
                                                          keyword_in_include_file=False, absolute_path=None,
                                                          array=None)}

    model = NexusSimulator('testpath1/nexus_run.fcs')
    # Act
    result = model.grid
    result_lgr = result.lgrs.lgrs[0]
    result_iregion = result_lgr.iregion['IREG1']

    # Assert
    pd.testing.assert_frame_equal(result_lgr.kx.mods['MOD'], expected_lgr.kx.mods['MOD'])
    assert result_lgr.kx.value == expected_lgr.kx.value
    assert result_lgr.kx.modifier == expected_lgr.kx.modifier
    assert len(result.lgrs.lgrs) == 1
    assert result_iregion.value == expected_lgr._iregion['IREG1'].value
    assert result_iregion.modifier == expected_lgr._iregion['IREG1'].modifier
    pd.testing.assert_frame_equal(result_iregion.mods['MOD'], expected_lgr._iregion['IREG1'].mods['MOD'])


@pytest.mark.parametrize("input_grid_file, expected_ipvt_mod", [
    ("""IPVT CON
1
MOD 
1 5 1 2 1 1 = 2\t! A comment
1 5 3 4 1 1 =3 ! A comment

SG ZVAR
5*0.8
5*0.2
""",
     pd.DataFrame({'i1': [1, 1], 'i2': [5, 5], 'j1': [1, 3], 'j2': [2, 4],
                   'k1': [1, 1], 'k2': [1, 1], '#v': ['=2', '=3']})
     ),
    ("""IPVT CON
1
MOD
1 5 1 2 1 1 = 2\t! A comment
1 5 3 4 1 1 =3 ! A comment
SKIP
MOD 
12 55 11 21 11 11 = 12050\t! A comment
12 55 31 41 11 11 =330303 ! A comment
NOSKIP

SG ZVAR
5*0.8
5*0.2
""",
     pd.DataFrame({'i1': [1, 1], 'i2': [5, 5], 'j1': [1, 3], 'j2': [2, 4],
                   'k1': [1, 1], 'k2': [1, 1], '#v': ['=2', '=3']})
     ),
    ("""IPVT CON
1
MOD
1 5 1 2 1 1 = 2\t! A comment
SKIP
MOD 
12 55 11 21 11 11 = 12050\t! A comment
12 55 31 41 11 11 =330303 ! A comment
NOSKIP
1 5 3 4 1 1 =3 ! A comment

SG ZVAR
5*0.8
5*0.2
""",
     pd.DataFrame({'i1': [1, 1], 'i2': [5, 5], 'j1': [1, 3], 'j2': [2, 4],
                   'k1': [1, 1], 'k2': [1, 1], '#v': ['=2', '=3']})
     ),
    ("""IPVT CON
1
SKIP
MOD
1 5 1 2 1 1 = 2\t! A comment
12 55 11 21 11 11 = 12050\t! A comment
12 55 31 41 11 11 =330303 ! A comment
NOSKIP

SG ZVAR
5*0.8
5*0.2
""",
     None),
])
def test_read_mods(mocker, input_grid_file, expected_ipvt_mod, ):
    # Arrange
    input_run_control = "START 01/07/2023"
    input_nexus_fcs_file = """DATEFORMAT DD/MM/YYYY
        GRID_FILES
            STRUCTURED_GRID    /path/to/grid/file.dat

        RECURRENT_FILES
            RUNCONTROL /path/to/run_control.dat

        SURFACE Network 1  /surface_file_01.dat

        """
    
    base_grid_file = """
    
NX NY NZ
69 30  1

KX VALUE
INCLUDE kx_array.inc

KY CON
200.50

LGR
CARTREF lgr_01                         
  14  20   29  29  1  10
  6*5  1*7
  9
  10*1
ENDREF 
ENDLGR

ARRAYS lgr_01
KX VALUE
INCLUDE permx_array.dat
"""
    input_grid_file = base_grid_file + input_grid_file
    
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/to/nexus/fcsfile.dat': input_nexus_fcs_file,
            '/path/to/run_control.dat': input_run_control,
            '/path/to/grid/file.dat': input_grid_file,
            '/surface_file_01.dat': ''
        }
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)

    def mock_isfile(filename):
        if '_filtered' in filename:
            return False
        return True

    mocker.patch("os.path.isfile", mock_isfile)
    mocker.patch("os.path.exists", mock_isfile)

    # Act
    nexus_model = NexusSimulator(origin='/path/to/nexus/fcsfile.dat')

    # Assert
    _ = nexus_model.grid.kx
    ipvt_mods = nexus_model.grid.lgrs.lgrs[0].ipvt.mods
    ipvt_mods = ipvt_mods['MOD'] if ipvt_mods is not None else None
    if expected_ipvt_mod is not None:
        pd.testing.assert_frame_equal(ipvt_mods, expected_ipvt_mod)
    else:
        assert ipvt_mods is None


def test_load_structured_grid_file_vmod(mocker):
    """Read in VMOD keyword with include file after."""
    # Arrange
    fcs_file_contents = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"
    structured_grid_name = os.path.join('testpath1', 'test_structured_grid.dat')
    structured_grid_file_contents = """ARRAYS ROOT
! grid
NX  NY  NZ
10  10  10

NETGRS VALUE
INCLUDE NTG.inc
VMOD
1 10 1 10  1 5 EQ  ! comment
INCluDE vmod_1.inc ! comment
VMOD
1 10 1 10  6 10 EQ

INCLUDE vmod_2.inc

"""  # ends structured_grid_file_contents
    # set up dataframe
    i1 = [1, 1]
    i2 = [10, 10]
    j1 = [1, 1]
    j2 = [10, 10]
    k1 = [1, 6]
    k2 = [5, 10]
    operation = ['EQ', 'EQ']
    include_file = ['vmod_1.inc', 'vmod_2.inc']
    expected_vmod = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, 'operation': operation,
                                  'include_file': include_file})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
        {'testpath1/nexus_run.fcs': fcs_file_contents,
         '/run_control/path': '',
         structured_grid_name: structured_grid_file_contents,
         # include_file_location: include_file_contents
         }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs')
    result = simulation.grid

    # Assert
    assert result.netgrs.keyword_in_include_file is False
    pd.testing.assert_frame_equal(result.netgrs.mods['VMOD'], expected_vmod)
    assert result.netgrs.modifier == 'VALUE'
    assert result.netgrs.value == 'NTG.inc'