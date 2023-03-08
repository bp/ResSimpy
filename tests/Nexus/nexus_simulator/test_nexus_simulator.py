import os
import pytest
import pandas as pd
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.StructuredGridFile import VariableEntry
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from pytest_mock import MockerFixture
from unittest.mock import Mock

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from tests.multifile_mocker import mock_multiple_files


def mock_multiple_opens(mocker, filename, fcs_file_contents, run_control_contents, include_contents,
                        run_control_mock=None, include_file_mock=None, log_file_mock=None, structured_grid_mock=None,
                        surface_1_mock=None, surface_2_mock=None):
    """Mock method that returns different test file contents depending upon the file name"""
    if "fcs" in filename:
        file_contents = fcs_file_contents
    elif "run_control" in filename:
        if run_control_mock is not None:
            return run_control_mock
        else:
            file_contents = run_control_contents
    elif "include" in filename:
        if include_file_mock is not None:
            return include_file_mock
        else:
            file_contents = include_contents
    elif "log" in filename:
        return log_file_mock
    elif "structured_grid" in filename:
        return structured_grid_mock
    else:
        raise FileNotFoundError(filename)
    open_mock = mocker.mock_open(read_data=file_contents)
    return open_mock


def mock_different_model_opens(mocker, filename, fcs_file_contents_1, fcs_file_contents_2, surface_file_contents_1,
                               surface_file_contents_2):
    """Mock method that returns different test file contents depending upon the model"""
    if "model1" in filename:
        file_contents = fcs_file_contents_1
    elif "model2" in filename:
        file_contents = fcs_file_contents_2
    elif "surface_1" in filename:
        file_contents = surface_file_contents_1
    elif "surface_2" in filename:
        file_contents = surface_file_contents_2
    else:
        raise FileNotFoundError(filename)
    open_mock = mocker.mock_open(read_data=file_contents)
    return open_mock


def check_file_read_write_is_correct(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture):
    assert len(modifying_mock_open.call_args_list) == 2
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(
        '/my/file/path', 'r')
    assert modifying_mock_open.call_args_list[1] == mocker_fixture.call(
        '/my/file/path', 'w')

    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [
        call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == 1
    assert list_of_writes[0].args[0] == expected_file_contents


@pytest.mark.parametrize("run_control_path,expected_root,expected_run_control_path,date_format,expected_use_american_date_format", [
    # Providing an absolute path to the fcs file + USA date format
    ("/run/control/path", "", "/run/control/path", "MM/DD/YYYY", True),
    # Providing a relative path to the fcs file + Non-USA date format
    ("run/control/path", "testpath1", "run/control/path", "DD/MM/YYYY", False)
])
def test_load_fcs_file_no_output_no_include_file(mocker, run_control_path, expected_root, expected_run_control_path,
                                                 date_format, expected_use_american_date_format):
    # Arrange
    fcs_file = f"RUNCONTROL {run_control_path}\nDATEFORMAT {date_format}\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_full_path = os.path.join(expected_root, expected_run_control_path)
    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.run_control_file_path == expected_full_path
    assert simulation.use_american_date_format == expected_use_american_date_format
    open_mock.assert_called_with(expected_full_path, 'r')


@pytest.mark.parametrize("run_control_path,expected_root,expected_run_control_path,date_format,expected_use_american_date_format", [
    # Providing an absolute path to the fcs file + USA date format
    ("/run/control/path", "", "/run/control/path", "MM/DD/YYYY", True),
    # Providing a relative path to the fcs file + Non-USA date format
    ("run/control/path", "testpath1", "run/control/path", "DD/MM/YYYY", False)
])
def test_load_fcs_space_in_filename(mocker, run_control_path, expected_root, expected_run_control_path,
                                    date_format, expected_use_american_date_format):
    # Arrange
    fcs_file = f"RUNCONTROL {run_control_path}\nDATEFORMAT {date_format}\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_full_path = os.path.join(expected_root, expected_run_control_path)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.run_control_file_path == expected_full_path
    assert simulation.use_american_date_format == expected_use_american_date_format
    open_mock.assert_called_with(expected_full_path, 'r')


def test_load_fcs_file_comment_after_declaration(mocker):
    """Check that the code ignores lines with comments that contain tokens"""
    # Arrange
    fcs_file = "!RUNCONTROL run_control_1\n RUNCONTROL run_control_2.inc\nDATEFORMAT DD/MM/YY\n!DATEFORMAT MM/DD/YY"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_file_path = os.path.join('testpath1', 'run_control_2.inc')
    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.run_control_file_path == expected_file_path
    assert simulation.use_american_date_format is False
    open_mock.assert_called_with(expected_file_path, 'r')


@pytest.mark.skip("Code changed to not throw an error in this scenario now")
@pytest.mark.parametrize("run_control_path,expected_run_control_path,date_format,expected_use_american_date_format", [
    # Providing an absolute path to the fcs file + USA date format
    ("/run/control/path", "/run/control/path", "MM/DD/YYYY", True),
    # Providing a relative path to the fcs file + Non-USA date format
    ("run/control/path", "original_output_path/run/control/path", "DD/MM/YYYY", False)
])
def test_output_destination_missing(mocker, run_control_path, expected_run_control_path, date_format,
                                    expected_use_american_date_format):
    """Check that an exception is raised if the user attempts to modify files without a specified output directory"""
    # Arrange
    fcs_file = f"RUNCONTROL {run_control_path}\nDATEFORMAT {date_format}"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(
        origin='test/Path.fcs', destination='original_output_path')
    with pytest.raises(ValueError):
        simulation.set_output_path(None)

    # Assert
    assert simulation.run_control_file_path == expected_run_control_path
    assert simulation.use_american_date_format == expected_use_american_date_format


@pytest.mark.parametrize("run_control_path,expected_run_control_path,date_format,expected_use_american_date_format",
                         [
                             ("/run/control/path",
                              "/run/control/path", "MM/DD/YYYY", True),
                             # Providing an absolute path to the fcs file + USA date format
                             ("run/control/path", "original_output_path/run/control/path",
                              "DD/MM/YYYY", False)
                             # Providing a relative path to the fcs file + Non-USA date format
                         ])
def test_origin_missing(mocker, run_control_path, expected_run_control_path, date_format,
                        expected_use_american_date_format):
    """Check that an exception is raised if the user attempts to initialise the class without an fcs file declared"""
    # Arrange
    fcs_file = f"RUNCONTROL {run_control_path}\nDATEFORMAT {date_format}"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    with pytest.raises(ValueError):
        NexusSimulator()


@pytest.mark.skip("re-enable once model moving has been implemented")
def test_output_to_existing_directory(mocker):
    """Testing output to directory with existing files"""
    # Arrange
    fcs_file = "RUNCONTROL path/to/run/control\nDATEFORMAT DD/MM/YYYYY"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    exists_mock = mocker.Mock(return_value=True)
    mocker.patch("os.path.exists", exists_mock)

    # Act + Assert
    with pytest.raises(FileExistsError):
        NexusSimulator(origin='test/Path.fcs',
                       destination='original_output_path')


@pytest.mark.parametrize("structured_grid_file_contents, expected_net_to_gross, expected_porosity, expected_range_x,"
                         "expected_range_y, expected_range_z",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\n,NETGRS VALUE\n INCLUDE /path_to_netgrs_file/include_net_to_gross.inc\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc",
                              "/path_to_netgrs_file/include_net_to_gross.inc", "path/to/porosity.inc", 1, 2, 3),
                             ("! Grid dimensions\nNX NY NZ\n111 123 321\ntest string\nPOROSITY VALUE\n!random text\n"
                              "porosity_file.inc\nNETGRS VALUE\n!Comment Line 1\n\n!Comment Line 2\nINCLUDE   "
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
    result = simulation.get_structured_grid()

    # Assert
    assert result.netgrs.value == expected_net_to_gross
    assert result.porosity.value == expected_porosity
    assert result.range_x == expected_range_x
    assert result.range_y == expected_range_y
    assert result.range_z == expected_range_z


@pytest.mark.parametrize("structured_grid_file_contents, expected_net_to_gross, expected_porosity,  "
                         "expected_ntg_modifier, expected_porosity_modifier, expected_range_x, expected_range_y, "
                         "expected_range_z",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\n,NETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc",
                              "/path_to_netgrs_file/net_to_gross.inc", "path/to/porosity.inc", "VALUE", "VALUE", 1, 2,
                              3),
                             ("! Grid dimensions\nNX NY NZ\n111 123 321\ntest string\nPOROSITY VALUE\n!random text\n"
                              "porosity_file.inc\nNETGRS VALUE\n!Comment Line 1\n\n!Comment Line 2\nINCLUDE   "
                              "/path/to/netgrs_file\nother text\n\n",
                              "/path/to/netgrs_file", "porosity_file.inc", "VALUE", "VALUE", 111, 123, 321),
                             ("! Grid dimensions\nNX NY NZ\n999 9 9\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\n,NETGRS CON\n 0.55\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \npath/to/porosity2.inc",
                              "0.55", "path/to/porosity2.inc", "CON", "VALUE", 999, 9, 9),
                             ("! Grid dimensions\nNX NY NZ\n8 5 \t6\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\n,NETGRS VALUE\n\t ntg_file.dat\n POROSITY CON\n!ANOTHER COMMENT \n3",
                              "ntg_file.dat", "3", "VALUE", "CON", 8, 5, 6),
                             ("! Grid dimensions\nNX   NY   NZ\n69   30    1\ntest string\nDUMMY VALUE\n!ioeheih\ntext"
                              "\nother text\n\n,NETGRS VALUE\n\t ntg_file.dat\n POROSITY CON\n!ANOTHER COMMENT \n3",
                              "ntg_file.dat", "3", "VALUE", "CON", 69, 30, 1),
                         ])
def test_load_structured_grid_file_dict_basic_properties(mocker, structured_grid_file_contents,
                                                         expected_net_to_gross, expected_porosity,
                                                         expected_ntg_modifier,
                                                         expected_porosity_modifier, expected_range_x, expected_range_y,
                                                         expected_range_z):
    """Read in Structured Grid File and return a dict object"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID \"test_structured_grid.dat\""
    structured_grid_name = os.path.join('testpath1', '\"test_structured_grid.dat\"')
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
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs', )
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
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID \"test_structured_grid.dat\""

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
                             ("SW VALUE\n /path/to/SW.inc",
                              "VALUE", "/path/to/SW.inc"),
                             ("SW CON\n0.6", "CON", "0.6"),
                             ("Random VALUE\nSW CON 0.33\nOTHER VALUE", "CON", "0.33"),
                             ("CON VALUE\nSW VALUE\tSW_FILE.inc",
                              "VALUE", "SW_FILE.inc"),
                         ])
def test_load_structured_grid_file_sw(mocker, structured_grid_file_contents,
                                      expected_water_saturation_modifier,
                                      expected_water_saturation_value):
    """Read in Structured Grid File"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID \"test_structured_grid.dat\""
    base_structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                                "\nother text\n\n,NETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc"

    structured_grid_file = base_structured_grid_file + structured_grid_file_contents
    structured_grid_name = os.path.join('testpath1', '\"test_structured_grid.dat\"')
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
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs', )
    result = simulation.get_structured_grid_dict()

    # Assert
    assert result['sw'].modifier == expected_water_saturation_modifier
    assert result['sw'].value == expected_water_saturation_value


@pytest.mark.parametrize("structured_grid_file_contents, expected_kx_value,expected_kx_modifier, expected_ky_value, "
                         "expected_ky_modifier, expected_kz_value, expected_kz_modifier",
                         [
                             ("KX VALUE\n /path/to/kx.inc\nKY MULT\n12 KX\n KZ VALUE\n\n\n kz.inc", "/path/to/kx.inc",
                              "VALUE", "12 KX", "MULT", "kz.inc", "VALUE"),
                             ("KX VALUE\n /path/to/kx.inc\nKY VALUE\n\t/path/to/kx.inc\n KZ MULT\n\n\n\t0.1 KX",
                              "/path/to/kx.inc",
                              "VALUE", "/path/to/kx.inc", "VALUE", "0.1 KX", "MULT"),
                             ("KX VALUE\n!Comment \n kx.inc\nKY MULT\n\t1 KX\n KZ MULT\n\n!3 KX\n 1 KX",
                              "kx.inc", "VALUE", "1 KX", "MULT", "1 KX", "MULT"),
                             ("KX MULT\n0.000001 KY\nKY VALUE\n\tky.inc\n KZ VALUE\n!COMMENT test\n\n /path/to/kz.inc",
                              "0.000001 KY", "MULT", "ky.inc", "VALUE", "/path/to/kz.inc", "VALUE"),
                             ("KX MULT\n 0.1 KY\nKY VALUE\n\t ky.inc\n KZ VALUE\n!COMMENT test\n\n /path/to/kz.inc",
                              "0.1 KY", "MULT", "ky.inc", "VALUE", "/path/to/kz.inc", "VALUE"),
                             ("KX VALUE\n /path/to/kx.inc\nKY VALUE\n\t/path/to/kx.inc\n KZ MULT\n\n\n\t\n\t 0.1\tKX",
                              "/path/to/kx.inc", "VALUE", "/path/to/kx.inc", "VALUE", "0.1 KX", "MULT"),
                             ("KX VALUE\n kx.inc\nKY MULT\n1 KX\n KZ MULT\n12 Ky",
                              "kx.inc", "VALUE", "1 KX", "MULT", "12 Ky", "MULT"),
                             ("KX CON\n 0.11333\nKY MULT\n1 KX\n KZ MULT\n12 Ky",
                              "0.11333", "CON", "1 KX", "MULT", "12 Ky", "MULT"),
                             ("PERMX CON\n 0.11333\nPERMY MULT\n1 PERMX\n PERMZ MULT\n12 PERMY",
                              "0.11333", "CON", "1 PERMX", "MULT", "12 PERMY", "MULT"),
                             ("PERMI CON\n 0.11333\nPERMJ MULT\n1 PERMI\n PERMK MULT\n12 PERMJ",
                              "0.11333", "CON", "1 PERMI", "MULT", "12 PERMJ", "MULT"),
                             ("KI CON\n 0.11333\nKJ MULT\n1 KI\n KK MULT\n12 KI",
                              "0.11333", "CON", "1 KI", "MULT", "12 KI", "MULT"),
                         ])
def test_load_structured_grid_file_k_values(mocker, structured_grid_file_contents, expected_kx_value,
                                            expected_kx_modifier, expected_ky_value, expected_ky_modifier,
                                            expected_kz_value, expected_kz_modifier):
    """Read in Structured Grid File"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID \"test_structured_grid.dat\""
    base_structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                                "\nother text\n\n,NETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                                "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc"

    structured_grid_file = base_structured_grid_file + structured_grid_file_contents
    structured_grid_name = os.path.join('testpath1', '\"test_structured_grid.dat\"')
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
    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs', )
    result = simulation.get_structured_grid()

    # Assert
    assert result.kx.modifier == expected_kx_modifier
    assert result.kx.value == expected_kx_value
    assert result.ky.modifier == expected_ky_modifier
    assert result.ky.value == expected_ky_value
    assert result.kz.modifier == expected_kz_modifier
    assert result.kz.value == expected_kz_value


@pytest.mark.parametrize("new_porosity, new_sw, new_netgrs, new_kx, new_ky, new_kz",
                         [
                             (VariableEntry("VALUE", "porosity_2.inc"), VariableEntry("CON", "0.33"),
                              VariableEntry(
                                  "VALUE", "/new/netgrs_2.inc"), VariableEntry("VALUE", "KX.INC"),
                              VariableEntry("MULT", "0.1 KX"), VariableEntry("VALUE", "path/to/kz.inc")),

                             (VariableEntry("VALUE", "porosity_2.inc"), VariableEntry("CON", "0.33"),
                              VariableEntry(
                                  "VALUE", "/new/netgrs_2.inc"), VariableEntry("VALUE", "KX.INC"),
                              VariableEntry("CON", "1.111113"), VariableEntry("VALUE", "path/to/kz.inc")),

                             (VariableEntry("VALUE", "/path/porosity_2.inc"), VariableEntry("VALUE", "sw_file.inc"),
                              VariableEntry(
                                  "VALUE", "/new/netgrs_2.inc"), VariableEntry("CON", "123"),
                              VariableEntry("CON", "1.111113"), VariableEntry("MULT", "1 KX")),

                             (VariableEntry("CON", "123456"), VariableEntry("CON", "0.000041"),
                              VariableEntry("CON", "1.1"), VariableEntry(
                                  "MULT", "0.1 KY"),
                              VariableEntry("CON", "1.111113"), VariableEntry("MULT", "10 KX")),

                             (VariableEntry("VALUE", "/path/porosity/file.inc"), VariableEntry("VALUE", "sw_file2.inc"),
                              VariableEntry("VALUE", "netgrs_3.inc"), VariableEntry(
                                  "VALUE", "path/to/kx.inc"),
                              VariableEntry("VALUE", "path/to/ky.inc"), VariableEntry("VALUE", "path/to/KZ.inc")),
                         ])
def test_save_structured_grid_values(mocker, new_porosity, new_sw, new_netgrs, new_kx, new_ky, new_kz):
    """Test saving values passed from the front end to the structured grid file and update the class"""
    # Arrange
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID test_structured_grid.dat"

    structured_grid_file = "! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text " \
                           "\nother text\n\n NETGRS VALUE\n\n!C\n\n  INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n POROSITY " \
                           "VALUE\n !ANOTHER COMMENT \n\tINCLUDE path/to/porosity.inc\nKX MULT\n 0.1 KY\nKY VALUE\n\t ky.inc\n " \
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

    simulation = NexusSimulator(origin='testpath1/nexus_run.fcs', )
    mocker.patch("builtins.open", structured_grid_mock)

    # Act
    simulation.update_structured_grid_file(new_structured_grid_dictionary)
    result = simulation.get_structured_grid()

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


@pytest.mark.parametrize("structured_grid_file_contents, expected_text",
                         [
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc\n "
                              "POROSITY VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc",
                              "dummy text\nother text\n\nNETGRS VALUE\n INCLUDE  /path_to_netgrs_file/net_to_gross.inc"
                              "\n POROSITY VALUE\n"),
                             ("! Grid dimensions\nNX NY NZ\n1 2 3\ntest string\nDUMMY VALUE\n!ioeheih\ndummy text"
                              "\nother text\n\nNETGRS CON\n 1.11111\n POROSITY "
                              "VALUE\n!ANOTHER COMMENT \npath/to/porosity.inc",
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
    fcs_file = f"RUNCONTROL /run_control/path\nDATEFORMAT DD/MM/YYYY\nSTRUCTURED_GRID \"test_structured_grid.dat\""
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
    result = NexusSimulator(origin='testpath1/nexus_run.fcs', )

    # Assert
    value = result.view_command(field='netgrs')
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
                                 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nStructured_GRID\n path/to/includes/grid.dat',
                                 'testpath1', 'path/to/includes/grid.dat'),
                             (
                                 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nstructured_grid\n path/to/includes/grid.dat',
                                 'testpath1', 'path/to/includes/grid.dat'),
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


@pytest.mark.parametrize("fcs_file, expected_default_unit_value",
                         [('DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.ENGLISH),
                          ('DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS \n LAB\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.LAB),
                          ('DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS METKG/CM2\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.METKGCM2),
                          ('DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_units    METRIC\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.METRIC),
                          ('DESC Test model\n\nRUN_UNITS ENGLISH\n\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.ENGLISH),
                          ('DESC Test model\n\nRUN_UNITS ENGLISH\n\ndefault_Units Metbar\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.METBAR),
                          ])
def test_load_fcs_file_populates_default_units(mocker, fcs_file, expected_default_unit_value):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')
    result = simulation.get_default_units()

    # Assert
    assert result == expected_default_unit_value


@pytest.mark.parametrize("fcs_file",
                         ['DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS NOTVALID\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                         'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS \nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat'
                          ])
def test_load_fcs_file_raises_error_for_undefined_default_units(mocker, fcs_file):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    with pytest.raises(ValueError):
        NexusSimulator(origin='testpath1/Path.fcs')


@pytest.mark.parametrize("fcs_file, expected_run_unit_value",
                         [('DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.ENGLISH),
                          ('DESC Test model\n\nRUN_UNITS  \n lab  \n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.LAB),
                          ('DESC Test model\n\nRun_UNITS MetBar\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.METBAR),
                          ('DESC Test model\n\nRun_UNITS METKG/CM2\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.METKGCM2),
                          ('DESC Test model\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                           UnitSystem.ENGLISH)
                          ])
def test_load_fcs_file_populates_run_units(mocker, fcs_file, expected_run_unit_value):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')
    result = simulation.get_run_units()

    # Assert
    assert result == expected_run_unit_value


@pytest.mark.parametrize("fcs_file",
                         ['DESC Test model\n\nRUN_UNITS BLAH\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                          'DESC Test model\n\nRUN_UNITs \nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat'
                          'DESC Test model\n\nRUN_UNITs 1\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat'
                          ])
def test_load_fcs_file_raises_error_for_undefined_run_units(mocker, fcs_file):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    with pytest.raises(ValueError):
        NexusSimulator(origin='testpath1/Path.fcs')


@pytest.mark.parametrize("fcs_file, expected_root, expected_extracted_path",
                         [(
                             'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/Includes/nexus_data/surface_simplified_06082018.inc',
                             'testpath1', 'nexus_data/Includes/nexus_data/surface_simplified_06082018.inc'),
                             (
                             'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE Network 1 	file/path/location/surface.inc',
                             'testpath1', 'file/path/location/surface.inc'),
                             (
                             'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nsurface network 1 	file/path/location/surface.inc',
                             'testpath1', 'file/path/location/surface.inc'),
                          ])
def test_get_abs_surface_file_path(mocker, fcs_file, expected_root, expected_extracted_path):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_result = os.path.join(expected_root, expected_extracted_path)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')
    result = simulation.get_surface_file_path()

    # Assert
    assert result == expected_result


@pytest.mark.skip("Re-enable once the run code has been established")
def test_run_simulator(mocker):
    """Testing the Simulator run code"""
    # Arrange
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator
    fcs_file = f"RUNCONTROL /run/control/path\nDATEFORMAT DD/MM/YYYY\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(
        origin='testpath1/Path.fcs', destination="test_new_destination")
    result = simulation.run_simulation()

    # Assert
    assert result == 'Job running, job number: 456'

def test_get_check_oil_gas_types_for_models_different_types(mocker):
    # Checks that a Value error is raised if the surface files contain different oil / gas types
    # Arrange
    models = ['path/to/model1.fcs', 'path/to/another/model2.fcs']

    fcs_file_contents_1 = "Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat"
    fcs_file_contents_2 = "SURFACE Network 1	Includes/nexus_data/surface_2.dat"
    surface_file_contents_1 = "line 1\nline 2\nGASWATER"
    surface_file_contents_2 = "line 1\nBLACKOIL"

    def mock_open_wrapper(filename, mode):
        mock_open = mock_different_model_opens(mocker, filename, fcs_file_contents_1, fcs_file_contents_2,
                                               surface_file_contents_1, surface_file_contents_2).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act / Assert
    with pytest.raises(ValueError):
        NexusSimulator.get_check_oil_gas_types_for_models(models)


@pytest.mark.parametrize("fcs_file_contents_1, fcs_file_contents_2, surface_file_contents_1, surface_file_contents_2,"
                         " expected_type",
                         [
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nline 2\nBLACKOIL",
                              "line 1\nBLACKOIL",
                              "BLACKOIL"
                              ),
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nline 2\nWATEROIL",
                              "line 1\nWATEROIL",
                              "WATEROIL"
                              ),
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nline 2\nGASWATER",
                              "line 1\nGASWATER",
                              "GASWATER"
                              )
                         ])
def test_get_check_oil_gas_types_for_models_same_types(mocker, fcs_file_contents_1, fcs_file_contents_2,
                                                       surface_file_contents_1, surface_file_contents_2, expected_type):
    # Checks that the correct oil / gas type is returned.
    # Arrange
    models = ['path/to/model1.fcs', 'path/to/another/model2.fcs']

    def mock_open_wrapper(filename, mode):
        mock_open = mock_different_model_opens(mocker, filename, fcs_file_contents_1, fcs_file_contents_2,
                                               surface_file_contents_1, surface_file_contents_2).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    result = NexusSimulator.get_check_oil_gas_types_for_models(models)

    # Assert
    assert result == expected_type


@pytest.mark.parametrize("fcs_file_contents_1, fcs_file_contents_2, surface_file_contents_1, surface_file_contents_2,"
                         " expected_type",
                         [
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nline 2\nBLAKOIL",
                              "line 1\nBLACKOIL",
                              ""
                              ),
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nline 2\nWATEROIL",
                              "line 1\nWATER",
                              ""
                              ),
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nline 2\nGASWATER",
                              "line 1\nGAWATER",
                              ""
                              )
                         ])
def test_get_check_oil_gas_types_for_models_no_type_found(mocker, fcs_file_contents_1, fcs_file_contents_2,
                                                          surface_file_contents_1, surface_file_contents_2,
                                                          expected_type):
    # Checks that the correct oil / gas type is returned.
    # Arrange
    models = ['path/to/model1.fcs', 'path/to/another/model2.fcs']

    def mock_open_wrapper(filename, mode):
        mock_open = mock_different_model_opens(mocker, filename, fcs_file_contents_1, fcs_file_contents_2,
                                               surface_file_contents_1, surface_file_contents_2).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act / Assert
    with pytest.raises(ValueError):
        NexusSimulator.get_check_oil_gas_types_for_models(models)


@pytest.mark.parametrize("original_file_contents, expected_file_contents, token, new_value, add_to_start",
                         [("test 3", "test ABC3", "TEST", "ABC3", False),
                          ("""!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults""",

                           """!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 50.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults""",
                           "NeTtEMp", "50.",
                           False),
                          ("""!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults""",

                           """MYTOKEN new value
!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults""",
                           "MYTOKEN", "new value",
                           True),
                          ("""!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults""",

                           """!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults
MYTOKEN new value""",
                           "MYTOKEN", "new value",
                           False),
                          ("""!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults""",

                           """!     Fluid model for network
BLACKOIL
!     Network default temperature
NETTEMP 100.  !Comment after value

!     lumped wellbore default to better match vip wellbore behaviour
!     Connection defaults
TOKENNOVALUE """,
                           "TOKENNOVALUE", "",
                           False)
                          ],
                         ids=["basic case", "standard value change", "token not present (add to start)",
                              "token not present (add to end)",
                              "token not present and has no value"])
def test_update_token_file_value(mocker, original_file_contents, expected_file_contents, token, new_value,
                                 add_to_start):
    """Test the update token value functionality"""
    # Arrange

    mock_original_opens = mocker.mock_open()
    mocker.patch("builtins.open", mock_original_opens)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="new_destination")

    modifying_mock_open = mocker.mock_open(read_data=original_file_contents)
    mocker.patch("builtins.open", modifying_mock_open)

    # Act
    simulation.update_file_value(
        file_path='/my/file/path', token=token, new_value=new_value, add_to_start=add_to_start)

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=modifying_mock_open,
                                     mocker_fixture=mocker)


@pytest.mark.parametrize("original_file_contents, expected_file_contents, token",
                         [
                             ("test 3", "! test 3", "TEST"),
                             ("""START 11/01/1992

!     Timestepping method
METHOD IMPLICIT
!     Current optimized default for facilities
SOLVER FACILITIES EXTENDED
GRIDSOLVER IMPLICIT_COUPLING NONE

!     Use vip units for output to vdb
VIPUNITS""",

                              """START 11/01/1992

!     Timestepping method
! METHOD IMPLICIT
!     Current optimized default for facilities
SOLVER FACILITIES EXTENDED
GRIDSOLVER IMPLICIT_COUPLING NONE

!     Use vip units for output to vdb
VIPUNITS""",
                              "METHOD")
                         ], ids=["standard comment out", "Larger file"])
def test_comment_out_file_value(mocker, original_file_contents, expected_file_contents, token):
    """Testing the functionality to comment out a line containing a specific token"""
    # Arrange
    mock_original_opens = mocker.mock_open()
    mocker.patch("builtins.open", mock_original_opens)

    simulation = NexusSimulator(
        origin='testpath1/nexus_run.fcs', destination="new_destination")

    modifying_mock_open = mocker.mock_open(read_data=original_file_contents)
    mocker.patch("builtins.open", modifying_mock_open)

    # Act
    simulation.comment_out_file_value(file_path='/my/file/path', token=token)

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=modifying_mock_open,
                                     mocker_fixture=mocker)


def test_add_map_statements(mocker):
    """Testing the functionality to comment out a line containing a specific token"""
    # Arrange

    original_file_contents = """START 11/01/1992

!     Timestepping method
METHOD IMPLICIT
!     Current optimized default for facilities
SOLVER FACILITIES EXTENDED
GRIDSOLVER IMPLICIT_COUPLING NONE

!     Use vip units for output to vdb
VIPUNITS

MAPBINARY
PLOTBINARY    
    """

    expected_file_contents = """MAPVDB
MAPOUT ALL
START 11/01/1992

!     Timestepping method
METHOD IMPLICIT
!     Current optimized default for facilities
SOLVER FACILITIES EXTENDED
GRIDSOLVER IMPLICIT_COUPLING NONE

!     Use vip units for output to vdb
VIPUNITS

MAPBINARY
PLOTBINARY    
    """

    mock_original_opens = mocker.mock_open(
        read_data="STRUCTURED_GRID /my/file/path")
    mocker.patch("builtins.open", mock_original_opens)

    simulation = NexusSimulator(origin='nexus_run.fcs')

    modifying_mock_open = mocker.mock_open(read_data=original_file_contents)
    mocker.patch("builtins.open", modifying_mock_open)

    # Act
    simulation.add_map_properties_to_start_of_grid_file()

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=modifying_mock_open,
                                     mocker_fixture=mocker)


# TODO: move these methods to a separate WELLS test file
@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WelLS sEt 1 my/wellspec/file.dat
    """)
], ids=['path_after_set'])
def test_get_wells(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to load in and retrieve a set of wells"""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid=None, skin=None,
                                          angle_v=None)
    loaded_completion_2 = NexusCompletion(
        i=6, j=7, k=8, well_radius=9.11, date='01/01/2023')
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              units=UnitSystem.ENGLISH)]

    # mock out the load_wells function as that is tested elsewhere
    mock_load_wells = mocker.Mock(return_value=loaded_wells)
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.Wells.get_wells()

    expected_well_spec_file_path = os.path.join('path', 'my/wellspec/file.dat')
    # Assert
    assert result == loaded_wells
    mock_load_wells.assert_called_once_with(wellspec_file_path=expected_well_spec_file_path,
                                            default_units=UnitSystem.ENGLISH,
                                            start_date='')


def test_get_wells_df(mocker: MockerFixture):
    # Arrange
    fcs_file_contents = """
       WelLS sEt 1 my/wellspec/file.dat
    """
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid=None, skin=None,
                                          angle_v=None)
    loaded_completion_2 = NexusCompletion(
        i=6, j=7, k=8, well_radius=9.11, date='01/01/2023')
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              units=UnitSystem.ENGLISH)]
    # create the expected dataframe
    loaded_wells_txt = ['WELL1, ENGLISH, 4.5, 01/01/2023, 1, 2, 3',
                        'WELL1, ENGLISH, 9.11, 01/01/2023, 6, 7, 8', ]
    loaded_wells_txt = [x.split(', ') for x in loaded_wells_txt]
    loaded_wells_df = pd.DataFrame(loaded_wells_txt,
                                   columns=['well_name', 'units', 'well_radius', 'date', 'i', 'j', 'k', ])
    loaded_wells_df = loaded_wells_df.astype(
        {'well_radius': 'float64', 'i': 'int64', 'j': 'int64', 'k': 'int64'})

    mock_load_wells = mocker.Mock(return_value=loaded_wells)
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)
    simulation = NexusSimulator(origin='nexus_run.fcs')
    # Act
    result = simulation.Wells.get_wells_df()
    # Assert

    pd.testing.assert_frame_equal(result, loaded_wells_df)

@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WelLS set 1 my/wellspec/file.dat
    """)
], ids=['basic case'])
def test_get_well(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to load in and retrieve a single wells"""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid=None, skin=None,
                                          angle_v=None)
    loaded_completion_2 = NexusCompletion(
        i=6, j=7, k=8, well_radius=9.11, date='01/01/2023')
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              units=UnitSystem.ENGLISH),
                    NexusWell(well_name='WELL2', completions=[loaded_completion_1, loaded_completion_2],
                              units=UnitSystem.ENGLISH)
                    ]

    # mock out the load_wells function as that is tested elsewhere
    mock_load_wells = mocker.Mock(return_value=loaded_wells)
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.Wells.get_well(well_name='WELL2')

    expected_well_spec_file_path = os.path.join('path', 'my/wellspec/file.dat')
    # Assert
    assert result == loaded_wells[1]
    mock_load_wells.assert_called_once_with(wellspec_file_path=expected_well_spec_file_path,
                                            default_units=UnitSystem.ENGLISH,
                                            start_date='')
