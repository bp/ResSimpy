import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import check_file_read_write_is_correct, get_fake_nexus_simulator


def test_find_constraint(mocker):
    # Arrange
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    mock_nexus_sim = get_fake_nexus_simulator(mocker)

    constraints = NexusConstraints(mock_nexus_network, mock_nexus_sim)
    well1_constraint_props = ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
                    'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
            {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': None, 'max_wor': 95.0,
                'unit_system': UnitSystem.ENGLISH},
            {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0, 'max_surface_oil_rate': 1.8,
                'unit_system': UnitSystem.ENGLISH},
            )
    well2_constraint_props = ({'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 1.8, 'max_pressure': 10000.2,
                                'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},
    {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},)

    existing_constraints = {'well1': [NexusConstraint(x) for x in well1_constraint_props],
                            'well2': [NexusConstraint(x) for x in well2_constraint_props]}

    constraints.__setattr__('_NexusConstraints__constraints', existing_constraints)
    expected_constraint = NexusConstraint(well1_constraint_props[2])
    find_constraint_dict = {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0,}
    # Act
    result = constraints.find_constraint('well1', find_constraint_dict)

    # Assert
    assert result == expected_constraint


def test_find_constraint_too_many_too_few_constraints_found(mocker):
    # Arrange
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    mock_nexus_sim = get_fake_nexus_simulator(mocker)

    constraints = NexusConstraints(mock_nexus_network, mock_nexus_sim)
    well1_constraint_props = ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
                    'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
            {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': None, 'max_wor': 95.0,
                'unit_system': UnitSystem.ENGLISH},
            {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0, 'max_surface_oil_rate': 1.8,
                'unit_system': UnitSystem.ENGLISH},
            )
    well2_constraint_props = ({'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 1.8, 'max_pressure': 10000.2,
                                'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},
    {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},)

    existing_constraints = {'well1': [NexusConstraint(x) for x in well1_constraint_props],
                            'well2': [NexusConstraint(x) for x in well2_constraint_props]}

    constraints.__setattr__('_NexusConstraints__constraints', existing_constraints)
    find_constraint_dict = {'name': 'well1', 'max_wor': 95.0}
    no_matching_constraints_dict = {'name': 'well1', 'max_wor': 100000}
    too_many_constraints = {'name': 'well1', 'max_wor': 95.0, 'max_surface_liquid_rate': 1000, 'date': '01/01/2019',
                            'max_pressure': 10}

    # Act
    with pytest.raises(ValueError) as ve:
        constraints.find_constraint('well1', find_constraint_dict)
        assert "Instead found: 3 matching constraints" in str(ve.value)

    with pytest.raises(ValueError) as ve:
        constraints.find_constraint('well1', no_matching_constraints_dict)
        assert "Instead found: 0 matching constraints" in str(ve.value)

    with pytest.raises(ValueError) as ve:
        constraints.find_constraint('well1', too_many_constraints)
        assert "Instead found: 0 matching constraints" in str(ve.value)


@pytest.mark.parametrize("file_contents, expected_result_file, expected_constraints, expected_number_writes",[
    (''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    ''',
    ''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    ENDCONSTRAINTS
    ''',
    [{'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH}
    ], 1),


    (''' TIME 01/01/2019
    CONSTRAINTS
    well2    QLIQSMAX- 10000.0 QLIQSMAX 15.5
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0
    ENDCONSTRAINTS
    ''',
    ''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    ENDCONSTRAINTS
    ''',
    [{'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH}], 2),

    (''' TIME 01/01/2019
    CONSTRAINTS
    well2    QLIQSMAX- 10000.0 QLIQSMAX 15.5
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0
    ENDCONSTRAINTS
    TIME 01/02/2019
    CONSTRAINTS
    well2    QLIQSMAX 10000.0 WORMAX 15.5
    well1	 QLIQSMAX 	1000  QWSMAX 	10
    well2	 QWSMAX 	0.0
    ENDCONSTRAINTS
    ''',
    ''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    ENDCONSTRAINTS
    TIME 01/02/2019
    CONSTRAINTS
    well2    QLIQSMAX 10000.0 WORMAX 15.5
    well1	 QLIQSMAX 	1000  QWSMAX 	10
    well2	 QWSMAX 	0.0
    ENDCONSTRAINTS
    ''',
    [{'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/02/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000, 'max_surface_water_rate': 10,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/02/2019', 'name': 'well2', 'max_surface_liquid_rate': 10000.0, 'max_surface_water_rate': 0,
           'max_wor': 15.5, 'unit_system': UnitSystem.ENGLISH}
    ], 2),

    ], ids=['basic_test', 'over multiple lines', 'multiple_dates'])
def test_remove_constraint(mocker, file_contents, expected_result_file, expected_constraints, expected_number_writes):
    # Arrange
    remove_constraint = {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH}

    fcs_file_contents = '''RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    RECURRENT_FILES
    RUNCONTROL nexus_data/runcontrol.dat
    SURFACE Network 1  /surface_file_01.dat'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    expected_constraint_dict = {'well1': [], 'well2': []}
    for constraint_dict in expected_constraints:
        node_name = constraint_dict['name']
        if node_name not in expected_constraint_dict.keys():
            expected_constraint_dict[node_name] = [NexusConstraint(constraint_dict)]
        else:
            expected_constraint_dict[node_name].append(NexusConstraint(constraint_dict))

    # Act
    constraints = nexus_sim.network.Constraints.get_constraints()
    nexus_sim.network.Constraints.remove_constraint(remove_constraint)
    result = nexus_sim.network.Constraints.get_constraints()

    # Assert
    assert result == expected_constraint_dict
    assert result['well1'] == expected_constraint_dict['well1']
    assert result['well2'] == expected_constraint_dict['well2']
    check_file_read_write_is_correct(expected_file_contents=expected_result_file,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/surface_file_01.dat',
                                     number_of_writes=expected_number_writes)

@pytest.mark.parametrize("file_contents, expected_file_contents, new_constraint, expected_number_writes", [
    # basic_test
    ('''TIME 01/01/2019
        CONSTRAINTS
        well2    QLIQSMAX- 10000.0 QLIQSMAX 15.5
        well1	 QLIQSMAX 	3884.0  QWSMAX 	0
        well2	 QWSMAX 	0.0
        ENDCONSTRAINTS''',
    '''TIME 01/01/2019
        CONSTRAINTS
        well2    QLIQSMAX- 10000.0 QLIQSMAX 15.5
        well1	 QLIQSMAX 	3884.0  QWSMAX 	0
        well2	 QWSMAX 	0.0
        well3    QOSMAX     100.0
        ENDCONSTRAINTS''',
    {'name': 'well3', 'max_surface_oil_rate': 100, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH},
    1
    ),
], ids=['basic_test'])
def test_add_constraint(mocker, file_contents, expected_file_contents, new_constraint, expected_number_writes):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    # Act
    nexus_sim.network.Constraints.add_constraints(new_constraint)
    # Assert
    check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/surface_file_01.dat',
                                     number_of_writes=expected_number_writes)