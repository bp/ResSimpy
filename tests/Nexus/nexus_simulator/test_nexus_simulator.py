import os
import pytest
import pandas as pd
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusPVT import NexusPVT
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
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


@pytest.mark.parametrize(
    "run_control_path,expected_root,expected_run_control_path,date_format,expected_use_american_date_format", [
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


@pytest.mark.parametrize(
    "run_control_path,expected_root,expected_run_control_path,date_format,expected_use_american_date_format", [
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
    result = simulation.get_default_units()

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
    result = simulation.get_run_units()

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
    simulation.Reporting.add_map_properties_to_start_of_grid_file()

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


@pytest.mark.parametrize("fcs_file_contents", [
    ("""
       PVT method 1 my/pvt/file1.dat

       pvt Method 2 my/pvt/file2.dat
       Pvt METHOD 3 my/pvt/file3.dat
    """)
], ids=['basic case'])
def test_get_pvt(mocker: MockerFixture, fcs_file_contents: str):
    """Testing the functionality to retrieve pvt methods from Nexus fcs file"""
    # Arrange
    fcs_file_open = mocker.mock_open(read_data=fcs_file_contents)
    mocker.patch("builtins.open", fcs_file_open)

    loaded_pvt = {1: NexusPVT(file_path=os.path.join('path', 'my/pvt/file1.dat')),
                  2: NexusPVT(file_path=os.path.join('path', 'my/pvt/file2.dat')),
                  3: NexusPVT(file_path=os.path.join('path', 'my/pvt/file3.dat')),
                  }

    simulation = NexusSimulator(origin='path/nexus_run.fcs')

    # Act
    result = simulation.pvt_methods

    # Assert
    assert result == loaded_pvt


@pytest.mark.parametrize("fcs_file_contents, surface_file_content, node1_props, node2_props, \
connection1_props, connection2_props, wellconprops1, wellconprops2",
     [(
         'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc',
         '''NODECON
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
          ''',
            {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
                'station': 'station', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23, 'number': 2,
                'station': 'station2', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'CP01', 'node_in': 'CP01', 'node_out': 'wh_cp01', 'con_type': 'PIPE', 'hyd_method': '2',
            'delta_depth': 7002.67, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'cp01_gaslift', 'node_in': 'GAS', 'node_out': 'CP01', 'con_type': 'GASLIFT', 'hyd_method': None,
            'delta_depth': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'R001', 'stream': 'PRODUCER', 'datum_depth': 10350.0, 'crossflow': 'OFF', 'crossshut_method': 'OFF',
            'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'R002', 'stream': 'PRODUCER', 'datum_depth': 10350.0, 'crossflow': 'ON', 'crossshut_method': 'OFF',
             'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH}
         ),
     ])
def test_load_surface_file(mocker, fcs_file_contents, surface_file_content, node1_props, node2_props,
    connection1_props, connection2_props, wellconprops1, wellconprops2):
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
    node_1 = NexusNode(node1_props)
    node_2 = NexusNode(node2_props)
    expected_nodes = [node_1, node_2]
    con1 = NexusNodeConnection(connection1_props)
    con2 = NexusNodeConnection(connection2_props)
    expected_cons = [con1, con2]

    well_con1 = NexusWellConnection(wellconprops1)
    well_con2 = NexusWellConnection(wellconprops2)
    expected_wellcons = [well_con1, well_con2]

    # create a mocker spy to check the network loader gets called once
    spy = mocker.spy(nexus_sim.Network, 'load')

    # Act
    result_nodes = nexus_sim.Network.Nodes.get_nodes()
    result_cons = nexus_sim.Network.Connections.get_connections()
    result_wellcons = nexus_sim.Network.WellConnections.get_well_connections()
    # Assert
    assert result_nodes == expected_nodes
    assert result_cons == expected_cons
    assert result_wellcons == expected_wellcons

    spy.assert_called_once()
