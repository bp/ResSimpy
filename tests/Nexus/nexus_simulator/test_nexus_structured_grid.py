import os
import pandas as pd
import pytest
from ResSimpy.Grid import GridArrayDefinition
from ResSimpy.Nexus.DataModels.StructuredGrid import NexusGrid
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

    #include_file_contents = '0.425 0.255 3*0.662 0.376 0.000 3*0.453 4*0.884 0.412 0.788 12*0.000'
    #include_file_location = os.path.join('testpath1', r'includes/netgrs_01.inc')

    # set up dataframe
    i1 = [68]*6 + [56]
    i2 = [68]*6 + [56]
    j1 = [34]*6 + [36]
    j2 = [34]*6 + [36]
    k1 = [1, 2, 8, 11, 15, 16, 1]
    k2 = [1, 2, 10, 14, 15, 16, 1]
    v = ['=0.34', '=0.2', '=0.69', '=0.85', '=0.52', '=0.79', '=0.67']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
                                        {'testpath1/nexus_run.fcs': fcs_file_contents,
                                         '/run_control/path': '',
                                         structured_grid_name: structured_grid_file_contents,
                                         #include_file_location: include_file_contents
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
"""  # ends structured_grid_file_contents

    #include_file_contents = '0.425 0.255 3*0.662 0.376 0.000 3*0.453 4*0.884 0.412 0.788 12*0.000'
    #include_file_location = os.path.join('testpath1', r'includes/netgrs_01.inc')

    # set up dataframe
    i1 = [68]*2
    i2 = [68]*2
    j1 = [34]*2
    j2 = [34]*2
    k1 = [1, 2]
    k2 = [1, 2]
    v = ['=0.34', '=0.2']
    expected_df = pd.DataFrame({'i1': i1, 'i2': i2, 'j1': j1, 'j2': j2, 'k1': k1, 'k2': k2, '#v': v})

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
                                        {'testpath1/nexus_run.fcs': fcs_file_contents,
                                         '/run_control/path': '',
                                         structured_grid_name: structured_grid_file_contents,
                                         #include_file_location: include_file_contents
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
                                         #include_file_location: include_file_contents
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
IRELPERM CON
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
                              "\nother text\n\nNETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \nINCLUDE path/to/porosity.inc",
                              "/path_to_netgrs_file/net_to_gross.inc", "path/to/porosity.inc", "VALUE", "VALUE", 1, 2,
                              3),
                             ("! Grid dimensions\nNX NY NZ\n111 123 321\ntest string\nPOROSITY VALUE\n!random text\n"
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
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs' )
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
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc "

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
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs' )
    result = simulation.get_structured_grid_dict()

    # Assert
    assert result['sw'].modifier == expected_water_saturation_modifier
    assert result['sw'].value == expected_water_saturation_value


@pytest.mark.parametrize("structured_grid_file_contents, expected_kx_value,expected_kx_modifier, expected_ky_value, "
                         "expected_ky_modifier, expected_kz_value, expected_kz_modifier",
                         [
                             ("KX VALUE\n INCLUDE /path/to/kx.inc\nKY MULT\n12 KX\n KZ VALUE\n\n\n INCLUDE kz.inc", "/path/to/kx.inc",
                              "VALUE", "12 KX", "MULT", "kz.inc", "VALUE"),
                             ("KX VALUE\n INCLUDE /path/to/kx.inc\nKY VALUE\n\tINCLUDE /path/to/kx.inc\n KZ MULT\n\n\n\t0.1 KX",
                              "/path/to/kx.inc",
                              "VALUE", "/path/to/kx.inc", "VALUE", "0.1 KX", "MULT"),
                             ("KX VALUE\n!Comment \n INCLUDE kx.inc\nKY MULT\n\t1 KX\n KZ MULT\n\n!3 KX\n 1 KX",
                              "kx.inc", "VALUE", "1 KX", "MULT", "1 KX", "MULT"),
                             ("KX MULT\n0.000001 KY\nKY VALUE\n\tINCLUDE ky.inc\n KZ VALUE\n!COMMENT test\n\n INCLUDE /path/to/kz.inc",
                              "0.000001 KY", "MULT", "ky.inc", "VALUE", "/path/to/kz.inc", "VALUE"),
                             ("KX MULT\n 0.1 KY\nKY VALUE\n\t INCLUDE ky.inc\n KZ VALUE\n!COMMENT test\n\n INCLUDE /path/to/kz.inc",
                              "0.1 KY", "MULT", "ky.inc", "VALUE", "/path/to/kz.inc", "VALUE"),
                             ("KX VALUE\n INCLUDE /path/to/kx.inc\nKY VALUE\n\tINCLUDE /path/to/kx.inc\n KZ MULT\n\n\n\t\n\t 0.1\tKX",
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
                             ("!KX VALUE\nKX VALUE\n INCLUDE /path/to/kx.inc\nKY MULT\n12 KX\n KZ VALUE\n\n\n INCLUDE kz.inc", "/path/to/kx.inc",
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
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc "

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
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs' )
    result = simulation.grid

    # Assert
    assert result.kx.modifier == expected_kx_modifier
    assert result.kx.value == expected_kx_value
    assert result.ky.modifier == expected_ky_modifier
    assert result.ky.value == expected_ky_value
    assert result.kz.modifier == expected_kz_modifier
    assert result.kz.value == expected_kz_value


@pytest.mark.parametrize("new_porosity, new_sw, new_netgrs, new_kx, new_ky, new_kz",
                         [
                             (GridArrayDefinition("VALUE", "porosity_2.inc"), GridArrayDefinition("CON", "0.33"),
                              GridArrayDefinition(
                                  "VALUE", "/new/netgrs_2.inc"), GridArrayDefinition("VALUE", "KX.INC"),
                              GridArrayDefinition("MULT", "0.1 KX"), GridArrayDefinition("VALUE", "path/to/kz.inc")),

                             (GridArrayDefinition("VALUE", "porosity_2.inc"), GridArrayDefinition("CON", "0.33"),
                              GridArrayDefinition(
                                  "VALUE", "/new/netgrs_2.inc"), GridArrayDefinition("VALUE", "KX.INC"),
                              GridArrayDefinition("CON", "1.111113"), GridArrayDefinition("VALUE", "path/to/kz.inc")),

                             (GridArrayDefinition("VALUE", "/path/porosity_2.inc"), GridArrayDefinition("VALUE", "sw_file.inc"),
                              GridArrayDefinition(
                                  "VALUE", "/new/netgrs_2.inc"), GridArrayDefinition("CON", "123"),
                              GridArrayDefinition("CON", "1.111113"), GridArrayDefinition("MULT", "1 KX")),

                             (GridArrayDefinition("CON", "123456"), GridArrayDefinition("CON", "0.000041"),
                              GridArrayDefinition("CON", "1.1"), GridArrayDefinition(
                                  "MULT", "0.1 KY"),
                              GridArrayDefinition("CON", "1.111113"), GridArrayDefinition("MULT", "10 KX")),

                             (GridArrayDefinition("VALUE", "/path/porosity/file.inc"), GridArrayDefinition("VALUE", "sw_file2.inc"),
                              GridArrayDefinition("VALUE", "netgrs_3.inc"), GridArrayDefinition(
                                  "VALUE", "path/to/kx.inc"),
                              GridArrayDefinition("VALUE", "path/to/ky.inc"), GridArrayDefinition("VALUE", "path/to/KZ.inc")),
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

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs' )
    mocker.patch("builtins.open", structured_grid_mock)

    # Act
    NexusGrid.NexusGrid.update_structured_grid_file(new_structured_grid_dictionary, simulation)
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
    result = NexusSimulator(origin='testpath1/nexus_run.fcs' )

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
