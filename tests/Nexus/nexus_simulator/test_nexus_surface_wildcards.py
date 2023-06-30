import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator

@pytest.mark.parametrize("file_contents, expected_constraints ", [
    # basic_test
    ('''TIME 01/01/2019
    WELLS
    NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
    well_prod   PRODUCER   94     4039.3     ON        CELLGRAD
    well_inj   WATER      95     4039.3     OFF        CALC
    ENDWELLS
    CONSTRAINTS
    well_*   QWSMAX 100
    ENDCONSTRAINTS''',
    [{'name': 'well_prod', 'date': '01/01/2019', 'max_surface_water_rate': 100, 'UnitSystem': 'ENGLISH'},
    {'name': 'well_inj', 'date': '01/01/2019', 'max_surface_water_rate': 100, 'UnitSystem': 'ENGLISH'}],
    ),

    # with extra constraints

    ], ids=['basic_test'])
def test_read_wildcard(mocker, file_contents, expected_constraints):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''

    expected_result = [NexusConstraint(x) for x in expected_constraints]

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
            ).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    # Act
    result = nexus_sim.network.Constraints.get_constraints()
    # Assert
    assert result == expected_result

