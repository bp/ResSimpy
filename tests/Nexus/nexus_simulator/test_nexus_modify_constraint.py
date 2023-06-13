import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from tests.utility_for_tests import check_file_read_write_is_correct


@pytest.mark.parametrize("file_contents, expected_result_file, expected_constraints",[
    (''' CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    ''',
    ''' CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    ENDCONSTRAINTS
    '''
    ,
    [{'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH}
    ]),


    ], ids=['basic_test']
)
def test_remove_constraint(mocker, file_contents, expected_result_file, expected_constraints):
    # Arrange
    remove_constraint = {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH}
    NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    constraints = NexusConstraints(mock_nexus_network)
    expected_nexus_constraints = [NexusConstraint(x) for x in expected_constraints]
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    # Act
    constraints.remove_constraint(remove_constraint)
    result = constraints.get_constraints()

    # Assert
    assert result == expected_nexus_constraints
    check_file_read_write_is_correct(expected_file_contents=expected_result_file,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/my/wellspec/file.dat',
                                     number_of_writes=1)
