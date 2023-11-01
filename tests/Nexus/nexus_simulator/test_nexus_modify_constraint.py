import uuid
import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import check_file_read_write_is_correct, get_fake_nexus_simulator, uuid_side_effect


def test_find_constraint(mocker):
    # Arrange
    mock_nexus_sim = get_fake_nexus_simulator(mocker)
    mock_nexus_network = NexusNetwork(mock_nexus_sim)
    mock_nexus_network.__setattr__('_NexusNetwork__has_been_loaded', True)

    constraints = NexusConstraints(mock_nexus_network, mock_nexus_sim)
    well1_constraint_props = ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
                              'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
                              {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': None, 'max_wor': 95.0,
                              'unit_system': UnitSystem.ENGLISH},
                              {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0, 'max_surface_oil_rate': 1.8,
                              'unit_system': UnitSystem.ENGLISH},
                              )
    well2_constraint_props = ({'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 1.8, 'max_pressure': 10000.2,
                               'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True},
                              {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True})

    existing_constraints = {'well1': [NexusConstraint(x) for x in well1_constraint_props],
                            'well2': [NexusConstraint(x) for x in well2_constraint_props]}

    constraints.__setattr__('_NexusConstraints__constraints', existing_constraints)
    mock_nexus_network.constraints = constraints
    expected_constraint = NexusConstraint(well1_constraint_props[2])
    find_constraint_dict = {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0}
    # Act
    result = constraints.find_by_properties('well1', find_constraint_dict)

    # Assert
    assert result == expected_constraint


def test_find_constraint_too_many_too_few_constraints_found(mocker):
    # Arrange
    mock_nexus_sim = get_fake_nexus_simulator(mocker)
    mock_nexus_network = NexusNetwork(mock_nexus_sim)
    mock_nexus_network.__setattr__('_NexusNetwork__has_been_loaded', True)

    constraints = NexusConstraints(mock_nexus_network, mock_nexus_sim)
    well1_constraint_props = ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
                               'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
                              {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': None, 'max_wor': 95.0,
                               'unit_system': UnitSystem.ENGLISH},
                              {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0, 'max_surface_oil_rate': 1.8,
                               'unit_system': UnitSystem.ENGLISH},
                              )
    well2_constraint_props = ({'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 1.8, 'max_pressure': 10000.2,
                               'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True},
                              {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True})

    existing_constraints = {'well1': [NexusConstraint(x) for x in well1_constraint_props],
                            'well2': [NexusConstraint(x) for x in well2_constraint_props]}

    constraints.__setattr__('_NexusConstraints__constraints', existing_constraints)
    mock_nexus_network.constraints = constraints

    find_constraint_dict = {'name': 'well1', 'max_wor': 95.0}
    no_matching_constraints_dict = {'name': 'well1', 'max_wor': 100000}
    too_many_constraints = {'name': 'well1', 'max_wor': 95.0, 'max_surface_liquid_rate': 1000, 'date': '01/01/2019',
                            'max_pressure': 10}

    # Act
    with pytest.raises(ValueError) as ve:
        constraints.find_by_properties('well1', find_constraint_dict)
    assert "Instead found: 3 matching constraints" in str(ve.value)

    with pytest.raises(ValueError) as ve:
        constraints.find_by_properties('well1', no_matching_constraints_dict)
    assert "Instead found: 0 matching constraints" in str(ve.value)

    with pytest.raises(ValueError) as ve:
        constraints.find_by_properties('well1', too_many_constraints)
    assert "Instead found: 0 matching constraints" in str(ve.value)


@pytest.mark.parametrize("file_contents, expected_result_file, constraint_to_remove, expected_constraints, expected_number_writes", [
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
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0,
                         'max_reverse_surface_liquid_rate': 10000.0,
                         'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
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
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0,
                         'max_reverse_surface_liquid_rate': 10000.0,
                         'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
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
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0,
                         'max_reverse_surface_liquid_rate': 10000.0,
                         'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
    [{'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/02/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000, 'max_surface_water_rate': 10,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/02/2019', 'name': 'well2', 'max_surface_liquid_rate': 10000.0, 'max_surface_water_rate': 0,
           'max_wor': 15.5, 'unit_system': UnitSystem.ENGLISH}
    ], 2),

    (''' TIME 01/01/2019
    CONSTRAINT
    NAME    QLIQSMAX    QWSMAX  QLIQSMAX-
    well1	3884.0   	0       NA
    well2   15.5        0       10000
    ENDCONSTRAINT
    ''',
    ''' TIME 01/01/2019
    CONSTRAINT
    NAME    QLIQSMAX    QWSMAX  QLIQSMAX-
    well1	3884.0   	0       NA
    ENDCONSTRAINT
    ''',
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0,
                         'max_reverse_surface_liquid_rate': 10000.0,
                         'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
    [{'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH},
    ], 1),

    (''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	MULT  QOSMAX 	MULT
    well2	 QALLRMAX 	0
    ENDCONSTRAINTS
    QMULT
    WELL QOIL QGAS QWATER
    well1 121.0 53.6 2.5
    well2 211.0 102.4 35.7
    ENDQMULT
    ''',
''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	MULT  QOSMAX 	MULT
    ENDCONSTRAINTS
    QMULT
    WELL QOIL QGAS QWATER
    well1 121.0 53.6 2.5
    ENDQMULT
    ''',
    {'date': '01/01/2019', 'name': 'well2', 'max_qmult_total_reservoir_rate': 0.0, 'unit_system': UnitSystem.ENGLISH,
     'qmult_oil_rate': 211.0, 'qmult_gas_rate': 102.4, 'qmult_water_rate': 35.7, 'well_name':'well2'},
    [{'date': '01/01/2019', 'name': 'well1', 'use_qmult_qoilqwat_surface_rate': True, 'use_qmult_qoil_surface_rate': True,
    'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 121.0, 'qmult_gas_rate': 53.6, 'qmult_water_rate': 2.5, 'well_name':'well1'}
    ], 2),


    ], ids=['basic_test', 'over multiple lines', 'multiple_dates', 'constraint_table','qmult_table'])
def test_remove_constraint(mocker, file_contents, expected_result_file,
                           constraint_to_remove, expected_constraints, expected_number_writes):
    # Arrange
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
    nexus_sim.network.constraints.get_all()
    nexus_sim.network.constraints.remove(constraint_to_remove)
    result = nexus_sim.network.constraints.get_all()

    # Assert
    assert result == expected_constraint_dict
    assert result['well1'] == expected_constraint_dict['well1']
    assert result['well2'] == expected_constraint_dict['well2']
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_result_file.splitlines(keepends=True)

@pytest.mark.parametrize("file_contents, expected_file_contents, new_constraint, expected_number_writes, expected_uuid", [
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
well3 QOSMAX 100 ! test user comments
        ENDCONSTRAINTS''',
    {'name': 'well3', 'max_surface_oil_rate': 100, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH},
    1,
    {'uuid1': [2, 4], 'uuid2': [3],'uuid3': [5]}
    ),

    # add new table
    ('''TIME 01/01/2019

''',
    '''TIME 01/01/2019
CONSTRAINTS ! test user comments
well3 QOSMAX 100
ENDCONSTRAINTS

''',
    {'name': 'well3', 'max_surface_oil_rate': 100, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH},
    1,
    {'uuid1': [2]}
    ),

# add new table
    ('''TIME 01/01/2019
    TIME 01/02/2019

    TIME 01/03/2019
    TIME 01/01/2020
    TIME 01/02/2020
''',
    '''TIME 01/01/2019
    TIME 01/02/2019

    TIME 01/03/2019
TIME 01/04/2019 ! test user comments
CONSTRAINTS
well3 QOSMAX 100
ENDCONSTRAINTS
    TIME 01/01/2020
    TIME 01/02/2020
''',
    {'name': 'well3', 'max_surface_oil_rate': 100, 'date': '01/04/2019', 'unit_system': UnitSystem.ENGLISH},
    1,
    {'uuid1': [6]}
    ),

# add QMULT table
    ('''TIME 01/01/2019

''',
    '''TIME 01/01/2019
CONSTRAINTS ! test user comments
node#2 QLIQSMAX MULT
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER
node#2 200.0 NA 4052.12
ENDQMULT

''',
    {'name': 'node#2', 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH,
                'use_qmult_qoilqwat_surface_rate': True, 'qmult_oil_rate': 200.0, 'qmult_water_rate': 4052.12},
    1,
    {'uuid1': [2, 6]}
    ),

# add QMULT table to existing QMULT
    ('''TIME 01/01/2019
CONSTRAINTS
node#2 QLIQSMAX MULT
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER
node#2 200.0 NA 4052.12
ENDQMULT
''',
    '''TIME 01/01/2019
CONSTRAINTS
node#2 QLIQSMAX MULT
new_well QLIQSMAX MULT ! test user comments
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER
node#2 200.0 NA 4052.12
new_well 3.14 50.2 420.232
ENDQMULT
''',
{'name': 'new_well', 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH,
 'use_qmult_qoilqwat_surface_rate': True, 'qmult_oil_rate': 3.14, 'qmult_gas_rate': 50.2,
 'qmult_water_rate': 420.232},
2,
{'uuid1': [2, 7], 'uuid2': [3, 8]}
),

# more time cards with qmult
    ('''TIME 01/01/2019
CONSTRAINTS
well1 QOSMAX 1025 
ENDCONSTRAINTS
    QMULT
WELL QOIL QGAS QWATER
well1 10 20 30
ENDQMULT
    TIME 01/01/2020
CONSTRAINTS
node#2 QLIQSMAX MULT
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER  ! Comment
node#2 200.0 NA 4052.12 ! Comment
ENDQMULT
TIME 01/02/2020
!comment
TIME 01/03/2020
''',
    '''TIME 01/01/2019
CONSTRAINTS
well1 QOSMAX 1025 
ENDCONSTRAINTS
    QMULT
WELL QOIL QGAS QWATER
well1 10 20 30
ENDQMULT
    TIME 01/01/2020
CONSTRAINTS
node#2 QLIQSMAX MULT
new_well QLIQSMAX MULT ! test user comments
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER  ! Comment
node#2 200.0 NA 4052.12 ! Comment
new_well 3.14 50.2 420.232
ENDQMULT
TIME 01/02/2020
!comment
TIME 01/03/2020
''',
    {'name': 'new_well', 'date': '01/01/2020', 'unit_system': UnitSystem.ENGLISH,
     'use_qmult_qoilqwat_surface_rate': True, 'qmult_oil_rate': 3.14, 'qmult_gas_rate': 50.2,
     'qmult_water_rate': 420.232},
    2,
    {'uuid1': [2, 6], 'uuid2': [10, 15], 'uuid3': [11, 16]}
    ),

], ids=['basic_test', 'add new table', 'add to new date', 'add QMULT table', 'add QMULT table to existing QMULT',
        'more time cards with qmult'])
def test_add_constraint(mocker, file_contents, expected_file_contents, new_constraint, expected_number_writes,
                        expected_uuid):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
            ).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # patch in uuids for the constraints
    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3',
                                                    'uuid4', 'uuid5', 'uuid6'])
    # Act
    nexus_sim.network.constraints.add(new_constraint, comments='test user comments')
    # Assert
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)
    assert nexus_sim.model_files.surface_files[1].object_locations == expected_uuid


@pytest.mark.parametrize("constraint, expected_string", [
# basic_test
({'name': 'well3', 'max_surface_oil_rate': 100, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH},
'well3 QOSMAX 100\n'
),
# more columns
({'name': 'well_2933', 'max_reservoir_liquid_rate': 100.14, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH,
'min_reservoir_oil_rate': 150.27, 'max_gor': 21020, 'max_reservoir_total_fluids_rate': 123.13},
'well_2933 GORMAX 21020 QLIQMAX 100.14 QALLMAX 123.13 QOMIN 150.27\n'
),

# Activate
({'name': 'well_2933', 'max_reservoir_liquid_rate': 100.14, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH,
'active_node': True},
'well_2933 QLIQMAX 100.14 ACTIVATE\n'
),

# deactivate
({'name': 'well_2933', 'max_reservoir_liquid_rate': 100.14, 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH,
'active_node': False},
'well_2933 QLIQMAX 100.14 DEACTIVATE\n'
),

# clear and special keywords
({'name': 'node#2', 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH, 'clear_p': True,
'convert_qmult_to_reservoir_barrels': True,
},
'node#2 QALLRMAX MULT CLEARP\n'
),
], ids=['basic_test', 'more columns', 'Activate', 'Deactivate', 'clear and special keywords'])
def test_constraint_to_string(constraint, expected_string):
    # Arrange
    new_constraint = NexusConstraint(constraint)
    # Act
    constraint_string = new_constraint.to_table_line([])
    # Assert
    assert constraint_string == expected_string


def test_write_qmult_table():
    # Arrange
    constraint_props = {'name': 'node#2', 'date': '01/01/2019', 'unit_system': UnitSystem.ENGLISH,
        'use_qmult_qoilqwat_surface_rate': True, 'qmult_oil_rate': 200.0, 'qmult_water_rate': 4052.12}
    constraint = NexusConstraint(constraint_props)
    expected_qmult_table = ['QMULT\n',
                            'WELL QOIL QGAS QWATER\n',
                            'node#2 200.0 NA 4052.12\n',
                            'ENDQMULT\n'
    ]
    # Act
    result_qmult_table = constraint.write_qmult_table()
    # Assert
    assert result_qmult_table == expected_qmult_table

@pytest.mark.parametrize("file_contents, expected_file_contents, current_constraint, new_constraint, expected_number_writes, expected_uuid", [
    # basic_test
    ('''TIME 01/01/2019
        CONSTRAINTS
        well2    QLIQSMAX- 10000.0 QLIQSMAX 15.5
        well1	 QLIQSMAX 	3884.0  QWSMAX 	0
        ENDCONSTRAINTS''',
    '''TIME 01/01/2019
        CONSTRAINTS
        well2    QLIQSMAX- 10000.0 QLIQSMAX 15.5
well1 QWSMAX 1000.0 QLIQSMAX 3884.0
        ENDCONSTRAINTS''',
    {'name': 'well1', 'date': '01/01/2019', 'max_surface_water_rate': 0},
    {'name': 'well1', 'date': '01/01/2019', 'max_surface_water_rate': 1000.0},
    2,
    {'uuid0': [2], 'uuid2': [3]}
    ),
   # qmult_test
    ('''TIME 01/01/2019
        CONSTRAINTS
well1 QLIQSMAX MULT
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER
well1 200.0 NA 4052.12
ENDQMULT
''',
'''TIME 01/01/2019
        CONSTRAINTS
well1 QLIQSMAX MULT
ENDCONSTRAINTS
QMULT
WELL QOIL QGAS QWATER
well1 1000.0 10 1.31
ENDQMULT
''',
    {'name': 'well1', 'date': '01/01/2019'},
    {'name': 'well1', 'date': '01/01/2019', 'qmult_oil_rate': 1000.0, 'qmult_water_rate': 1.31, 'qmult_gas_rate': 10},
    4,
    {'uuid1': [2, 6]}
    )
    ],ids=['basic_test', 'qmult_test'])
def test_modify_constraints(mocker, file_contents, expected_file_contents, current_constraint, new_constraint,
                            expected_number_writes, expected_uuid):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
            ).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # patch in uuids for the constraints
    mocker.patch.object(uuid, 'uuid4', side_effect=uuid_side_effect())
    # Act
    nexus_sim.network.constraints.modify('well1', current_constraint, new_constraint)
    # Assert
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)
    assert nexus_sim.model_files.surface_files[1].object_locations == expected_uuid

@pytest.mark.parametrize('current_constraint, new_constraint, error_msg',[
# well name not found
({'name': 'well1', 'date': '01/01/2019', 'max_surface_oil_rate': 10},
{'name': 'well1', 'date': '01/01/2019', 'max_surface_oil_rate': 1000.0},
 "No constraints found with name='well1'"),

# constraint not matching
({'name': 'well_not_found', 'date': '01/01/2019', 'max_surface_oil_rate': 10},
{'name': 'well_not_found', 'date': '01/01/2019', 'max_surface_oil_rate': 1000.0},
 'No unique matching constraints with the properties provided.Instead found: 0 matching constraints.'
 ),

], ids=['well name not', 'constraint not matching']
)
def test_modify_constraint_no_constraint_found(mocker, current_constraint, new_constraint,
                                               error_msg):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''
    surface_file = '''
    TIME 01/01/2019
    CONSTRAINTS
    well_not_found QOSMAX 100
    ENDCONSTRAINTS'''
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': surface_file,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
            ).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
    # make a mock for the write operation
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # patch in uuids for the constraints
    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3',
                                                    'uuid4', 'uuid5', 'uuid6', 'uuid7'])
    # Act
    with pytest.raises(ValueError) as ve:
        nexus_sim.network.constraints.modify(current_constraint['name'], current_constraint, new_constraint)
    assert str(ve.value) == error_msg

def test_add_constraint_no_name_given(mocker):
    # Arrange
    model = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    constraints = NexusConstraints(mock_nexus_network, model)

    empty_constraint = NexusConstraint({})

    # Act and Assert
    with pytest.raises(ValueError) as ve:
        constraints.add(constraint_to_add={'max_surface_oil_rate': 10},)
    assert str(ve.value) == 'Input arguments or constraint_to_add dictionary must contain a name for the node.'
    with pytest.raises(ValueError) as ve:
        constraints.add(constraint_to_add=empty_constraint)
    assert str(ve.value) == 'No name found in the provided constraint object.'