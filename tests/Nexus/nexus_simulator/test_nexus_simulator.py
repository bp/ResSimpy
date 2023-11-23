import os
from typing import Optional
import uuid
import pytest
import pandas as pd
from datetime import datetime, timezone
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod
from ResSimpy.Nexus.DataModels.NexusSeparatorMethod import NexusSeparatorMethod
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod
from ResSimpy.Nexus.DataModels.NexusEquilMethod import NexusEquilMethod
from ResSimpy.Nexus.DataModels.NexusRockMethod import NexusRockMethod
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Nexus.DataModels.NexusGasliftMethod import NexusGasliftMethod
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from pytest_mock import MockerFixture
from unittest.mock import Mock
from ResSimpy.Enums.UnitsEnum import UnitSystem
from tests.multifile_mocker import mock_multiple_files


def mock_multiple_opens(mocker, filename, fcs_file_contents, run_control_contents, include_contents,
                        run_control_mock=None, include_file_mock=None, log_file_mock=None, structured_grid_mock=None,
                        surface_1_mock=None, surface_2_mock=None, wellspec_mock=None):
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
    elif "wellspec" in filename:
        return wellspec_mock
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


def check_file_read_write_is_correct_for_windows(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture):
    assert len(modifying_mock_open.call_args_list) == 2
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(
        "\my\file\path", 'r')
    assert modifying_mock_open.call_args_list[1] == mocker_fixture.call(
        "\my\file\path", 'w')

    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [
        call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == 1
    assert list_of_writes[0].args[0] == expected_file_contents

@pytest.mark.parametrize(
    "run_control_path, expected_root, expected_run_control_path, date_format, expected_date_format", [
        # Providing an absolute path to the fcs file + USA date format
        ("/run/control/path", "", "/run/control/path", "MM/DD/YYYY", DateFormat.MM_DD_YYYY),
        # Providing a relative path to the fcs file + Non-USA date format
        ("run/control/path", "testpath1", "run/control/path", "DD/MM/YYYY", DateFormat.DD_MM_YYYY)
    ])
def test_load_fcs_file_no_output_no_include_file(mocker, run_control_path, expected_root, expected_run_control_path,
                                                 date_format, expected_date_format):
    # Arrange
    fcs_file = f"RUNCONTROL {run_control_path}\nDATEFORMAT {date_format}\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_full_path = os.path.join(expected_root, expected_run_control_path)
    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.run_control_file_path == expected_full_path
    assert simulation.date_format is expected_date_format
    open_mock.assert_called_with(expected_full_path, 'r')

@pytest.mark.parametrize(
    "run_control_path, expected_root, expected_run_control_path, date_format, expected_date_format", [
        # Providing an absolute path to the fcs file + USA date format
        ("/run/control/path", "", "/run/control/path", "MM/DD/YYYY", DateFormat.MM_DD_YYYY),
        # Providing a relative path to the fcs file + Non-USA date format
        ("run/control/path", "testpath1", "run/control/path", "DD/MM/YYYY", DateFormat.DD_MM_YYYY)
    ])
def test_load_fcs_space_in_filename(mocker, run_control_path, expected_root, expected_run_control_path,
                                    date_format, expected_date_format):
    # Arrange
    fcs_file = f"RUNCONTROL {run_control_path}\nDATEFORMAT {date_format}\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_full_path = os.path.join(expected_root, expected_run_control_path)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.run_control_file_path == expected_full_path
    assert simulation.date_format is expected_date_format
    open_mock.assert_called_with(expected_full_path, 'r')
@pytest.mark.parametrize(
    "fcs_file_contents, expected_date_format", [
        ("RUNCONTROL /path/to/run/control\n  DATE_FORMAT MM/DD/YYYY", DateFormat.MM_DD_YYYY),
        ("RUNCONTROL /path/to/run/control\n  DATE_FORMAT DD/MM/YYYY", DateFormat.DD_MM_YYYY),
        ("RUNCONTROL /path/to/run/control\n", DateFormat.MM_DD_YYYY),
        ("RUNCONTROL c:\path\to\run\control\n  DATE_FORMAT MM/DD/YYYY", DateFormat.MM_DD_YYYY),
        ("RUNCONTROL c:\path\to\run\control\n  DATE_FORMAT DD/MM/YYYY", DateFormat.DD_MM_YYYY),
        ("RUNCONTROL c:\path\to\run\control\n", DateFormat.MM_DD_YYYY),
    ], ids=['US date format', 'non-us date format', 'default (us format)', 'Win US Date Format', 'Win non-us date format', 'Win default (us format)', ])
def test_load_fcs_date_format(mocker, fcs_file_contents, expected_date_format):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.date_format is expected_date_format

def test_get_users_linked_with_files(mocker):
    # Arrange 
    fcs_file = "RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    modified_time=datetime(2018, 6, 30, 8, 18, 10,tzinfo=timezone.utc)
    dt_mock = mocker.MagicMock()
    mocker.patch('datetime.datetime',dt_mock)
    dt_mock.fromtimestamp.return_value = modified_time
    
    mocker.patch("builtins.open", open_mock)
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = "Mock-User"
    path_mock.return_value.group.return_value = "Mock-Group"
    
    os_mock = mocker.MagicMock()
    mocker.patch('os.stat',os_mock)
    os_mock.return_value.st_mtime = 1530346690
  
    simulation = NexusSimulator(origin="Path.fcs")
    
    expected_result = [("Path.fcs","Mock-User:Mock-Group",modified_time),("run_control.inc","Mock-User:Mock-Group",modified_time)]
    # Act
    
    result = simulation.get_users_linked_with_files()
    mocker.stopall()
    assert result == expected_result


def test_get_users_linked_with_files_error_raised(mocker):
    # Arrange
    fcs_file = "RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\n"
    open_mock = mocker.mock_open(read_data=fcs_file)
    modified_time = datetime(2018, 6, 30, 8, 18, 10, tzinfo=timezone.utc)
    dt_mock = mocker.MagicMock()
    mocker.patch('datetime.datetime', dt_mock)
    dt_mock.fromtimestamp.return_value = modified_time

    mocker.patch("builtins.open", open_mock)
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = "mock_User"
    path_mock.return_value.group.side_effect = NotImplementedError("Not implemented on this system")

    os_mock = mocker.MagicMock()
    mocker.patch('os.stat', os_mock)
    os_mock.return_value.st_mtime = 1530346690

    simulation = NexusSimulator(origin="Path.fcs")

    expected_result = [("Path.fcs", "mock_User:", modified_time),
                       ("run_control.inc", "mock_User:", modified_time)]
    # Act

    result = simulation.get_users_linked_with_files()
    mocker.stopall()

    # Assert
    assert result == expected_result

def test_get_users_with_files_for_multiple_files(mocker):
    
    fcs_file = 'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat'     
     
     
    open_mock = mocker.mock_open(read_data=fcs_file)
    modified_time=datetime(2018, 6, 30, 8, 18, 10,tzinfo=timezone.utc)
    dt_mock = mocker.MagicMock()
    mocker.patch('datetime.datetime',dt_mock)
    dt_mock.fromtimestamp.return_value = modified_time
    
    mocker.patch("builtins.open", open_mock)
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = "Mock-User"
    path_mock.return_value.group.return_value = "Mock-Group"
    
    os_mock = mocker.MagicMock()
    mocker.patch('os.stat',os_mock)
    os_mock.return_value.st_mtime = 1530346690
  
    simulation = NexusSimulator(origin="Path.fcs")
    
    expected_result = [("Path.fcs","Mock-User:Mock-Group",modified_time),
                       ("Includes/grid_data/main_grid.dat","Mock-User:Mock-Group",modified_time)]
    # Act
    
    result = simulation.get_users_linked_with_files()
    mocker.stopall()
    assert result == expected_result


def test_load_fcs_file_comment_after_declaration(mocker):
    """Check that the code ignores lines with comments that contain tokens"""
    # Arrange
    fcs_file = "!RUNCONTROL run_control_1\n RUNCONTROL run_control_2.inc\nDATEFORMAT DD/MM/YYYY\n!DATEFORMAT MM/DD/YYYY"
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)
    expected_file_path = os.path.join('testpath1', 'run_control_2.inc')
    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')

    # Assert
    assert simulation.run_control_file_path == expected_file_path
    assert simulation.date_format is DateFormat.DD_MM_YYYY
    open_mock.assert_called_with(expected_file_path, 'r')


@pytest.mark.skip("Code changed to not throw an error in this scenario now")
@pytest.mark.parametrize("run_control_path, expected_run_control_path, date_format, expected_date_format", [
    # Providing an absolute path to the fcs file + USA date format
    ("/run/control/path", "/run/control/path", "MM/DD/YYYY", True),
    # Providing a relative path to the fcs file + Non-USA date format
    ("run/control/path", "original_output_path/run/control/path", "DD/MM/YYYY", DateFormat.DD_MM_YYYY),
    # Providing an absolute path to the fcs file + USA date format Windows
    ("C:\run\control\path", "C:\run\control\path", "MM/DD/YYYY", True),
    # Providing a relative path to the fcs file + Non-USA date format Windows
    ("\run\control\path", "original_output_path\run\control\path", "DD/MM/YYYY", DateFormat.DD_MM_YYYY)
])
def test_output_destination_missing(mocker, run_control_path, expected_run_control_path, date_format,
                                    expected_date_format):
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
    assert simulation.date_format is expected_date_format


@pytest.mark.parametrize("run_control_path,expected_run_control_path,date_format,expected_use_american_date_format",
                         [
                             ("/run/control/path",
                              "/run/control/path", "MM/DD/YYYY", True),
                             # Providing an absolute path to the fcs file + USA date format
                             ("run/control/path", "original_output_path/run/control/path",
                              "DD/MM/YYYY", False),
                             # Providing a relative path to the fcs file + Non-USA date format
                             ("c:\run\control\path",
                              "c:\run\control\path", "MM/DD/YYYY", True),
                             # Providing an absolute path to the fcs file + USA date format
                             ("run\control\path", "original_output_path\run\control\path",
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
    # Arrange for windows
    fcs_file_win = "RUNCONTROL path\to\run\control\nDATEFORMAT DD/MM/YYYYY"
    open_mock_win = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock_win)

    exists_mock = mocker.Mock(return_value=True)
    mocker.patch("os.path.exists", exists_mock)

    # Act + Assert
    with pytest.raises(FileExistsError):
        NexusSimulator(origin='test\Path.fcs',
                       destination='original_output_path')


@pytest.mark.parametrize("fcs_file, expected_default_unit_value",
                         [(
                                 'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                 UnitSystem.ENGLISH),
                             (
                                     'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS \n LAB\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.LAB),
                             (
                                     'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS METKG/CM2\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.METKGCM2),
                             (
                                     'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_units    METRIC\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.METRIC),
                             (
                                     'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.ENGLISH),
                             (
                                     'DESC Test model\n\nRUN_UNITS ENGLISH\n\ndefault_Units Metbar\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.METBAR),
                         ])
def test_load_fcs_file_populates_default_units(mocker, fcs_file, expected_default_unit_value):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')
    result = simulation.default_units

    # Assert
    assert result == expected_default_unit_value


@pytest.mark.parametrize("fcs_file",
                         [
                             'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS NOTVALID\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
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
                         [(
                                 'DESC Test model\n\nRUN_UNITS ENGLISH\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                 UnitSystem.ENGLISH),
                             (
                                     'DESC Test model\n\nRUN_UNITS  \n lab  \n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.LAB),
                             (
                                     'DESC Test model\n\nRun_UNITS MetBar\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.METBAR),
                             (
                                     'DESC Test model\n\nRun_UNITS METKG/CM2\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.METKGCM2),
                             (
                                     'DESC Test model\n\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
                                     UnitSystem.ENGLISH)
                         ])
def test_load_fcs_file_populates_run_units(mocker, fcs_file, expected_run_unit_value):
    # Arrange
    open_mock = mocker.mock_open(read_data=fcs_file)
    mocker.patch("builtins.open", open_mock)

    # Act
    simulation = NexusSimulator(origin='testpath1/Path.fcs')
    result = simulation.run_units

    # Assert
    assert result == expected_run_unit_value


@pytest.mark.parametrize("fcs_file",
                         [
                             'DESC Test model\n\nRUN_UNITS BLAH\nDEFAULT_UNITS ENGLISH\nDATEFORMAT MM/DD/YYYY\n\nGRID_FILES\n\tSTRUCTURED_GRID\tIncludes/grid_data/main_grid.dat',
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
                             (
                                 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data\\Includes\\nexus_data\\surface_simplified_06082018.inc',
                                 'testpath1', 'nexus_data\\Includes\\nexus_data\\surface_simplified_06082018.inc')
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
                              ),
                             ("Line 1\nAnother LIne\nSURFACE Network 1	Includes/nexus_data/surface_1.dat",
                              "SURFACE Network 1	Includes/nexus_data/surface_2.dat",
                              "line 1\nAPI",
                                "line 1\nAPI",
                                "API"
                              ),

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
        origin='testpath1\nexus_run.fcs', destination="new_destination")

    modifying_mock_open = mocker.mock_open(read_data=original_file_contents)
    mocker.patch("builtins.open", modifying_mock_open)

    # Act
    simulation.update_file_value(
        file_path='\my\file\path', token=token, new_value=new_value, add_to_start=add_to_start)

    # Assert
    check_file_read_write_is_correct_for_windows(expected_file_contents=expected_file_contents,
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
        origin='testpath1\nexus_run.fcs', destination="new_destination")

    modifying_mock_open = mocker.mock_open(read_data=original_file_contents)
    mocker.patch("builtins.open", modifying_mock_open)

    # Act
    simulation.comment_out_file_value(file_path='\my\file\path', token=token)

    # Assert
    check_file_read_write_is_correct_for_windows(expected_file_contents=expected_file_contents,
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
    simulation.reporting.add_map_properties_to_start_of_grid_file()

    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=modifying_mock_open,
                                     mocker_fixture=mocker)

def test_add_map_statements_windows(mocker):
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
        read_data="STRUCTURED_GRID \my\file\path")
    mocker.patch("builtins.open", mock_original_opens)

    simulation = NexusSimulator(origin='nexus_run.fcs')

    modifying_mock_open = mocker.mock_open(read_data=original_file_contents)
    mocker.patch("builtins.open", modifying_mock_open)

    # Act
    simulation.reporting.add_map_properties_to_start_of_grid_file()

    # Assert
    check_file_read_write_is_correct_for_windows(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=modifying_mock_open,
                                     mocker_fixture=mocker)

# TODO: move these methods to a separate WELLS test file
@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WelLS sEt 1 my/wellspec/file.dat
    """)
], ids=['path_after_set'])
def test_get_all(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to load in and retrieve a set of wells"""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                          grid=None, date_format=DateFormat.DD_MM_YYYY)
    loaded_completion_2 = NexusCompletion(date='01/01/2023', i=6, j=7, k=8, well_radius=9.11,
                                          date_format=DateFormat.DD_MM_YYYY)
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH)]

    # mock out the load_wells function as that is tested elsewhere
    mock_load_wells = mocker.Mock(return_value=(loaded_wells, ''))
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)

    # NB file_content_as_list needs to be set as below due to the mocker open re-reading fcs contents
    expected_well_file = NexusFile(location='my/wellspec/file.dat',
                                   include_locations=[], origin='path/nexus_run.fcs', file_content_as_list=
                                   ['\n', '       WelLS sEt 1 my/wellspec/file.dat\n', '    '])

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.wells.get_all()

    # Assert
    assert result == loaded_wells
    mock_load_wells.assert_called_once_with(nexus_file=expected_well_file,
                                            default_units=UnitSystem.ENGLISH,
                                            start_date='', model_date_format=DateFormat.MM_DD_YYYY)

@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WelLS sEt 1 my\wellspec\file.dat
    """)
], ids=['path_after_set'])
def test_get_wells_windows(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to load in and retrieve a set of wells"""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                          grid=None, date_format=DateFormat.DD_MM_YYYY)
    loaded_completion_2 = NexusCompletion(date='01/01/2023', i=6, j=7, k=8, well_radius=9.11,
                                          date_format=DateFormat.DD_MM_YYYY)
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH)]

    # mock out the load_wells function as that is tested elsewhere
    mock_load_wells = mocker.Mock(return_value=(loaded_wells, ''))
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)

    # NB file_content_as_list needs to be set as below due to the mocker open re-reading fcs contents
    expected_well_file = NexusFile(location='my\wellspec\file.dat',
                                   include_locations=[], origin='path\nexus_run.fcs', file_content_as_list=
                                   ['\n', '       WelLS sEt 1 my\wellspec\file.dat\n', '    '])

    simulation = NexusSimulator(origin='path\nexus_run.fcs')

    # Act
    result = simulation.wells.get_all()

    # Assert
    assert result == loaded_wells
    mock_load_wells.assert_called_once_with(nexus_file=expected_well_file,
                                            default_units=UnitSystem.ENGLISH,
                                            start_date='', model_date_format = DateFormat.MM_DD_YYYY)


def test_get_df(mocker: MockerFixture):
    # Arrange
    fcs_file_contents = """
       WelLS sEt 1 my/wellspec/file.dat
    """
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                          grid=None, date_format=DateFormat.DD_MM_YYYY)
    loaded_completion_2 = NexusCompletion(date='01/01/2023', i=6, j=7, k=8, well_radius=9.11,
                                          date_format=DateFormat.DD_MM_YYYY)
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH)]
    # create the expected dataframe
    loaded_wells_txt = ['WELL1, ENGLISH, 4.5, 01/01/2023, 1, 2, 3',
                        'WELL1, ENGLISH, 9.11, 01/01/2023, 6, 7, 8', ]
    loaded_wells_txt = [x.split(', ') for x in loaded_wells_txt]
    loaded_wells_df = pd.DataFrame(loaded_wells_txt,
                                   columns=['well_name', 'units', 'well_radius', 'date', 'i', 'j', 'k', ])
    loaded_wells_df = loaded_wells_df.astype(
        {'well_radius': 'float64', 'i': 'int64', 'j': 'int64', 'k': 'int64'})

    mock_load_wells = mocker.Mock(return_value=(loaded_wells, ''))
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)
    simulation = NexusSimulator(origin='nexus_run.fcs')
    # Act
    result = simulation.wells.get_df()
    # Assert

    pd.testing.assert_frame_equal(result, loaded_wells_df, check_like=True)


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WelLS set 1 my/wellspec/file.dat
    """)
], ids=['basic case'])
def test_get(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to load in and retrieve a single wells."""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                          grid=None, date_format=DateFormat.DD_MM_YYYY)
    loaded_completion_2 = NexusCompletion(date='01/01/2023', i=6, j=7, k=8, well_radius=9.11,
                                          date_format=DateFormat.DD_MM_YYYY)
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH),
                    NexusWell(well_name='WELL2', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH)
                    ]

    # mock out the load_wells function as that is tested elsewhere
    mock_load_wells = mocker.Mock(return_value=(loaded_wells, ''))
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)

    # NB file_content_as_list needs to be set as below due to the mocker open re-reading fcs contents
    expected_well_file = NexusFile(location='my/wellspec/file.dat',
                                   include_locations=[], origin='path/nexus_run.fcs', file_content_as_list=
                                   ['\n', '       WelLS set 1 my/wellspec/file.dat\n', '    '])

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.wells.get(well_name='WELL2')

    # Assert
    assert result == loaded_wells[1]
    mock_load_wells.assert_called_once_with(nexus_file=expected_well_file,
                                            default_units=UnitSystem.ENGLISH,
                                            start_date='', model_date_format = DateFormat.MM_DD_YYYY)
@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WelLS set 1 my\\wellspec\\file.dat
    """)
], ids=['basic case'])
def test_get_well_windows(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to load in and retrieve a single wells."""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_completion_1 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                          grid=None, date_format=DateFormat.DD_MM_YYYY)
    loaded_completion_2 = NexusCompletion(date='01/01/2023', i=6, j=7, k=8, well_radius=9.11,
                                          date_format=DateFormat.DD_MM_YYYY)
    loaded_wells = [NexusWell(well_name='WELL1', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH),
                    NexusWell(well_name='WELL2', completions=[loaded_completion_1, loaded_completion_2],
                              unit_system=UnitSystem.ENGLISH)
                    ]

    # mock out the load_wells function as that is tested elsewhere
    mock_load_wells = mocker.Mock(return_value=(loaded_wells, ''))
    mocker.patch('ResSimpy.Nexus.NexusWells.load_wells', mock_load_wells)

    # NB file_content_as_list needs to be set as below due to the mocker open re-reading fcs contents
    expected_well_file = NexusFile(location='my\\wellspec\\file.dat',
                                   include_locations=[], origin='path\\nexus_run.fcs', file_content_as_list=
                                   ['\n', '       WelLS set 1 my\\wellspec\\file.dat\n', '    '])

    simulation = NexusSimulator(origin='path\\nexus_run.fcs')

    # Act
    result = simulation.wells.get(well_name='WELL2')

    # Assert
    assert result == loaded_wells[1]
    mock_load_wells.assert_called_once_with(nexus_file=expected_well_file,
                                            default_units=UnitSystem.ENGLISH,
                                            start_date='', model_date_format = DateFormat.MM_DD_YYYY)


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       PVT method 1 my/pvt/file1.dat

       pvt Method 2 my/pvt/file2.dat
       Pvt METHOD 3 my/pvt/file3.dat
    """)
], ids=['basic case'])
def test_get_pvt(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve pvt methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/pvt/file1.dat'): '',
            os.path.join('path', 'my/pvt/file2.dat'): '',
            os.path.join('path', 'my/pvt/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    pvt_files = []
    for i in range(3):
        pvt_file = NexusFile(location=f'my/pvt/file{i+1}.dat', origin='path/nexus_run.fcs')
        pvt_file.line_locations = [(0, uuid.uuid4())]
        pvt_files.append(pvt_file)

    loaded_pvt = {1: NexusPVTMethod(file=pvt_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                  2: NexusPVTMethod(file=pvt_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                  3: NexusPVTMethod(file=pvt_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH),
                  }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.pvt.inputs

    # Assert
    assert result == loaded_pvt

@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       SEPARATOR method 1 my/separator/file1.dat

       separator Method 2 my/separator/file2.dat
       Separator METHOD 3 my/separator/file3.dat
    """)
], ids=['basic case'])
def test_get_separator(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve separator methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/separator/file1.dat'): '',
            os.path.join('path', 'my/separator/file2.dat'): '',
            os.path.join('path', 'my/separator/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    sep_files = []
    for i in range(3):
        sep_file = NexusFile(location=f'my/separator/file{i+1}.dat', origin='path/nexus_run.fcs')
        sep_file.line_locations = [(0, uuid.uuid4())]
        sep_files.append(sep_file)

    loaded_sep = {1: NexusSeparatorMethod(file=sep_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                  2: NexusSeparatorMethod(file=sep_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                  3: NexusSeparatorMethod(file=sep_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH),
                  }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.separator.inputs

    # Assert
    assert result == loaded_sep


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       WATER method 1 my/water/file1.dat

       water Method 2 my/water/file2.dat
       Water METHOD 3 my/water/file3.dat
    """)
], ids=['basic case'])
def test_get_water(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve water methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/water/file1.dat'): '',
            os.path.join('path', 'my/water/file2.dat'): '',
            os.path.join('path', 'my/water/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    wat_files = []
    for i in range(3):
        wat_file = NexusFile(location=f'my/water/file{i+1}.dat', origin='path/nexus_run.fcs')
        wat_file.line_locations = [(0, uuid.uuid4())]
        wat_files.append(wat_file)

    loaded_wat = {1: NexusWaterMethod(file=wat_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                  2: NexusWaterMethod(file=wat_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                  3: NexusWaterMethod(file=wat_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH),
                  }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.water.inputs

    # Assert
    assert result == loaded_wat




@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       EQUIL method 1 my/equil/file1.dat

       equil Method 2 my/equil/file2.dat
       Equil METHOD 3 my/equil/file3.dat
    """)
], ids=['basic case'])
def test_get_equil(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve equilibration methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/equil/file1.dat'): '',
            os.path.join('path', 'my/equil/file2.dat'): '',
            os.path.join('path', 'my/equil/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    eq_files = []
    for i in range(3):
        eq_file = NexusFile(location=f'my/equil/file{i+1}.dat', origin='path/nexus_run.fcs')
        eq_file.line_locations = [(0, uuid.uuid4())]
        eq_files.append(eq_file)

    loaded_equil = {1: NexusEquilMethod(file=eq_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                    2: NexusEquilMethod(file=eq_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                    3: NexusEquilMethod(file=eq_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH)
                    }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.equil.inputs

    # Assert
    assert result == loaded_equil


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       ROCK method 1 my/rock/file1.dat

       rock Method 2 my/rock/file2.dat
       Rock METHOD 3 my/rock/file3.dat
    """)
], ids=['basic case'])
def test_get_rock(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve rock properties methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/rock/file1.dat'): '',
            os.path.join('path', 'my/rock/file2.dat'): '',
            os.path.join('path', 'my/rock/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    rock_files = []
    for i in range(3):
        rock_file = NexusFile(location=f'my/rock/file{i+1}.dat', origin='path/nexus_run.fcs')
        rock_file.line_locations = [(0, uuid.uuid4())]
        rock_files.append(rock_file)

    loaded_rocks = {1: NexusRockMethod(file=rock_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                    2: NexusRockMethod(file=rock_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                    3: NexusRockMethod(file=rock_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH),
                    }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.rock.inputs

    # Assert
    assert result == loaded_rocks


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       RELPM method 1 my/relpm/file1.dat

       relpm Method 2 my/relpm/file2.dat
       RelPm METHOD 3 my/relpm/file3.dat
    """)
], ids=['basic case'])
def test_get_relperm(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve relative permeability and
    capillary pressure methods from Nexus fcs file.
    """
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/relpm/file1.dat'): '',
            os.path.join('path', 'my/relpm/file2.dat'): '',
            os.path.join('path', 'my/relpm/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    relpm_files = []
    for i in range(3):
        relpm_file = NexusFile(location=f'my/relpm/file{i+1}.dat', origin='path/nexus_run.fcs')
        relpm_file.line_locations = [(0, uuid.uuid4())]
        relpm_files.append(relpm_file)

    loaded_relperms = {1: NexusRelPermMethod(file=relpm_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                       2: NexusRelPermMethod(file=relpm_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                       3: NexusRelPermMethod(file=relpm_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH),
                       }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.relperm.inputs

    # Assert
    assert result == loaded_relperms


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       VALVE method 1 my/valve/file1.dat

       valve Method 2 my/valve/file2.dat
       Valve METHOD 3 my/valve/file3.dat
    """)
], ids=['basic case'])
def test_get_valve(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve valve methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/valve/file1.dat'): '',
            os.path.join('path', 'my/valve/file2.dat'): '',
            os.path.join('path', 'my/valve/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    valve_files = []
    for i in range(3):
        valve_file = NexusFile(location=f'my/valve/file{i+1}.dat', origin='path/nexus_run.fcs')
        valve_file.line_locations = [(0, uuid.uuid4())]
        valve_files.append(valve_file)

    loaded_valves = {1: NexusValveMethod(file=valve_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                     2: NexusValveMethod(file=valve_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                     3: NexusValveMethod(file=valve_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH),
                     }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.valve.inputs

    # Assert
    assert result == loaded_valves


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       AQUIFER method 1 my/aquifer/file1.dat
       aquifer Method 2 my/aquifer/file2.dat
       Aquifer METHOD 3 my/aquifer/file3.dat
    """)
], ids=['basic case'])
def test_get_aquifer(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve aquifer methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/aquifer/file1.dat'): '',
            os.path.join('path', 'my/aquifer/file2.dat'): '',
            os.path.join('path', 'my/aquifer/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    aq_files = []
    for i in range(3):
        aq_file = NexusFile(location=f'my/aquifer/file{i+1}.dat', origin='path/nexus_run.fcs')
        aq_file.line_locations = [(0, uuid.uuid4())]
        aq_files.append(aq_file)

    loaded_aquifers = {1: NexusAquiferMethod(file=aq_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                       2: NexusAquiferMethod(file=aq_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                       3: NexusAquiferMethod(file=aq_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH)
                       }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.aquifer.inputs

    # Assert
    assert result == loaded_aquifers


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       HYD method 1 my/hyd/file1.dat
       hyd Method 2 my/hyd/file2.dat
       Hyd METHOD 3 my/hyd/file3.dat
    """)
], ids=['basic case'])
def test_get_hydraulics(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve hydraulics methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/hyd/file1.dat'): '',
            os.path.join('path', 'my/hyd/file2.dat'): '',
            os.path.join('path', 'my/hyd/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    hyd_files = []
    for i in range(3):
        hyd_file = NexusFile(location=f'my/hyd/file{i+1}.dat', origin='path/nexus_run.fcs')
        hyd_file.line_locations = [(0, uuid.uuid4())]
        hyd_files.append(hyd_file)

    loaded_hyds = {1: NexusHydraulicsMethod(file=hyd_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                   2: NexusHydraulicsMethod(file=hyd_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                   3: NexusHydraulicsMethod(file=hyd_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH)
                   }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.hydraulics.inputs

    # Assert
    assert result == loaded_hyds

@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       GASLIFT method 1 my/gaslift/file1.dat
       gaslift Method 2 my/gaslift/file2.dat
       Gaslift METHOD 3 my/gaslift/file3.dat
    """)
], ids=['basic case'])
def test_get_gaslift(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve gaslift methods from Nexus fcs file."""
    # Arrange
    mocker.patch.object(uuid, 'uuid4', return_value='uuid')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            os.path.join('path', 'my/gaslift/file1.dat'): '',
            os.path.join('path', 'my/gaslift/file2.dat'): '',
            os.path.join('path', 'my/gaslift/file3.dat'): '',
            'path/nexus_run.fcs': fcs_file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    gl_files = []
    for i in range(3):
        gl_file = NexusFile(location=f'my/gaslift/file{i+1}.dat', origin='path/nexus_run.fcs')
        gl_file.line_locations = [(0, uuid.uuid4())]
        gl_files.append(gl_file)

    loaded_gaslift = {1: NexusGasliftMethod(file=gl_files[0], input_number=1, model_unit_system=UnitSystem.ENGLISH),
                      2: NexusGasliftMethod(file=gl_files[1], input_number=2, model_unit_system=UnitSystem.ENGLISH),
                      3: NexusGasliftMethod(file=gl_files[2], input_number=3, model_unit_system=UnitSystem.ENGLISH)
                      }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.gaslift.inputs

    # Assert
    assert result == loaded_gaslift


@pytest.mark.parametrize("fcs_file_contents, surface_file_content, node1_props, node2_props, \
connection1_props, connection2_props, wellconprops1, wellconprops2, wellheadprops1, wellheadprops2, wellboreprops1, \
wellboreprops2, constraint_props1, constraint_props2",
     [(
         'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc',
         '''
         CONDEFAULTS
        CONTYPE   TYPE  METHOD
        WELLBORE LUMPED CELLAVG
        ENDCONDEFAULTS
        WELLCONTROL WELLHEAD

         NODECON
C          node1         NA        NA    80    100.5 200.8   1     station         (commented out using C) 
            NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
            CP01            CP01      wh_cp01       PIPE        2          7002.67
            cp01_gaslift    GAS       CP01          GASLIFT     NONE        NA ! Checked NODECON 13/05/2020 
            ENDNODECON
            NODES
          NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
         ! Riser Nodes
          node1         NA        NA    60.5    100.5 300.5   1     station
          node_2        WELLHEAD     1167.3 #  10.21085 3524.23 2   station2 ! COMMENT 
          ENDNODES
          content outside of the node statement
          node1         NA        NA    60.5    10.5 3.5   1     station_null
          TIME 01/02/2024
          WELLS
         NAME   STREAM DATUM CROSSFLOW CROSS_SHUT
         R001 PRODUCER 10350       OFF        OFF
         R002 PRODUCER 10350       ON        OFF
         ENDWELLS
         TIME 01/03/2025
        WELLHEAD
        WELL NAME DEPTH TYPE METHOD
        !ru	TH-ru	100	PIPE 	3	
        R001	tubing	50.2	PIPE 	2	!ENDWELLHEAD
        R-0_02	TH-03	0	PIPE 	1! comment
        ENDWELLHEAD
        WELLBORE
        WELL METHOD DIAM TYPE
        well1 BEGGS 3.5 PIPE
        ENDWELLBORE
        WELLBORE
        WELL METHOD DIAM FLOWSECT ROUGHNESS
        well2 BRILL 3.25 2      0.2002
        ENDWELLBORE
        METBAR
        QMULT
        WELL		QOIL	QGAS	QWATER
        GUN_P	128.528	13776.669	0
        ENDQMULT
        
        CONSTRAINTS
        GUN_P	ACTIVATE
        GUN_P	PMIN 5 QALLRMAX MULT
        ENDCONSTRAINTS
          ''',
            {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
                'station': 'station', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23, 'number': 2,
                'station': 'station2', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'CP01', 'node_in': 'CP01', 'node_out': 'wh_cp01', 'con_type': 'PIPE', 'hyd_method': '2',
            'delta_depth': 7002.67, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'cp01_gaslift', 'node_in': 'GAS', 'node_out': 'CP01', 'con_type': 'GASLIFT', 'hyd_method': None,
            'delta_depth': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'R001', 'stream': 'PRODUCER', 'datum_depth': 10350.0, 'crossflow': 'OFF', 'crossshut': 'OFF',
            'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'R002', 'stream': 'PRODUCER', 'datum_depth': 10350.0, 'crossflow': 'ON', 'crossshut': 'OFF',
             'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH},
{'well': 'R001', 'name': 'tubing', 'depth': 50.2, 'wellhead_type': 'PIPE', 'hyd_method': 2, 'date': '01/03/2025', 'unit_system': UnitSystem.ENGLISH},
{'well': 'R-0_02', 'name': 'TH-03', 'depth': 0, 'wellhead_type': 'PIPE', 'hyd_method': 1, 'date': '01/03/2025', 'unit_system': UnitSystem.ENGLISH},

{'name': 'well1', 'bore_type': 'PIPE', 'hyd_method': "BEGGS", 'diameter': 3.5, 'date': '01/03/2025',
 'unit_system': UnitSystem.ENGLISH},
{'name': 'well2', 'hyd_method': "BRILL", 'diameter': 3.25, 'flowsect': 2, 'roughness': 0.2002,
 'date': '01/03/2025', 'unit_system': UnitSystem.ENGLISH},
 {'name': 'GUN_P', 'qmult_oil_rate': 128.528, 'qmult_gas_rate': 13776.669, 'qmult_water_rate': 0.0, 'date': '01/03/2025',
 'unit_system': UnitSystem.METBAR, 'well_name':'GUN_P'},
{'name': 'GUN_P', 'qmult_oil_rate': 128.528, 'qmult_gas_rate': 13776.669, 'qmult_water_rate': 0.0, 'date': '01/03/2025',
'unit_system': UnitSystem.METBAR, 'active_node':True, 'min_pressure': 5.0, 'convert_qmult_to_reservoir_barrels': True,
'well_name':'GUN_P'},
         ),
     ])
def test_load_surface_file(mocker, fcs_file_contents, surface_file_content, node1_props, node2_props,
    connection1_props, connection2_props, wellconprops1, wellconprops2, wellheadprops1, wellheadprops2,
    wellboreprops1, wellboreprops2, constraint_props1, constraint_props2):
    # Arrange
    # Mock out the surface and fcs file
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            'nexus_data/surface.inc': surface_file_content,
            'run_control.inc': 'START 01/01/2023',
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    fcs_file_path = 'fcs_file.fcs'
    nexus_sim = NexusSimulator(fcs_file_path)

    # Create the expected objects
    expected_nodes = [NexusNode(node1_props), NexusNode(node2_props)]
    expected_cons = [NexusNodeConnection(connection1_props), NexusNodeConnection(connection2_props)]
    expected_wellcons = [NexusWellConnection(wellconprops1), NexusWellConnection(wellconprops2)]
    expected_wellheads = [NexusWellhead(wellheadprops1), NexusWellhead(wellheadprops2)]
    expected_wellbores = [NexusWellbore(wellboreprops1), NexusWellbore(wellboreprops2)]
    expected_constraints = {constraint_props1['name']: [NexusConstraint(constraint_props2)]}
    # create a mocker spy to check the network loader gets called once
    spy = mocker.spy(nexus_sim._network, 'load')

    # Act
    result_nodes = nexus_sim.network.nodes.get_all()
    result_cons = nexus_sim.network.connections.get_all()
    result_wellcons = nexus_sim.network.well_connections.get_all()
    result_wellheads = nexus_sim.network.wellheads.get_all()
    result_wellbores = nexus_sim.network.wellbores.get_all()
    result_constraints = nexus_sim.network.constraints.get_all()
    # Assert
    assert result_nodes == expected_nodes
    assert result_cons == expected_cons
    assert result_wellcons == expected_wellcons
    assert result_wellheads == expected_wellheads
    assert result_wellbores == expected_wellbores
    assert result_constraints == expected_constraints
    spy.assert_called_once()
