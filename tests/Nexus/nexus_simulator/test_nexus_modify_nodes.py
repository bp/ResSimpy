import uuid
import pytest
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator, check_file_read_write_is_correct

@pytest.mark.parametrize('file_contents, expected_file_contents, node_to_remove, expected_nodes, expected_number_writes',
[# basic_test
('''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
  node1                         NA            NA      #
  node_2        WELLHEAD     1167.3 #
  ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
  node_2        WELLHEAD     1167.3 #
  ENDNODES
''',
{'name': 'node1', 'type': None, 'depth': None,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023',
    'unit_system': UnitSystem.ENGLISH}],
1  # no. writes
),

# by ID
('''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
 ! another comment
  node1                         NA            NA      #  !comment
  ! comment 3
  node_2        WELLHEAD     1167.3 #  ! comment
  ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
 ! another comment
  ! comment 3
  node_2        WELLHEAD     1167.3 #  ! comment
  ENDNODES
''',
'uuid1',
[{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023',
    'unit_system': UnitSystem.ENGLISH}],
1  # no. writes
),

# more tables and timestamps
('''TIME 01/01/2022
NODES
  NAME        TYPE       DEPTH   TEMP
  node1       NA            NA      #  !comment
  node_2      WELLHEAD     1167.3 #  ! comment
  ENDNODES

  TIME 01/01/2023
NODES
  NAME        TYPE       DEPTH   TEMP
  node1       WELLBORE   1202      110
  node_2      WELLHEAD     1167.3 #  ! comment
  ENDNODES
  TIME 01/01/2024
NODES
  NAME        TYPE       DEPTH   TEMP
  node1       WELLBORE   1202      110
  node11     WELLBORE   1202      110
  ENDNODES
''',

'''TIME 01/01/2022
NODES
  NAME        TYPE       DEPTH   TEMP
  node1       NA            NA      #  !comment
  node_2      WELLHEAD     1167.3 #  ! comment
  ENDNODES

  TIME 01/01/2023
NODES
  NAME        TYPE       DEPTH   TEMP
  node_2      WELLHEAD     1167.3 #  ! comment
  ENDNODES
  TIME 01/01/2024
NODES
  NAME        TYPE       DEPTH   TEMP
  node1       WELLBORE   1202      110
  node11     WELLBORE   1202      110
  ENDNODES
''',
{'name': 'node1', 'type': 'WELLBORE', 'depth': 1202,  'temp': 110, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},

[{'name': 'node1', 'type': None, 'depth': None,  'temp': None, 'date': '01/01/2022', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2022', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node1', 'type': 'WELLBORE', 'depth': 1202, 'temp': 110, 'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node11', 'type': 'WELLBORE', 'depth': 1202, 'temp': 110, 'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH}],
1  # no. writes
),

# empty table
('''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
  node_2        WELLHEAD     1167.3 #
  ENDNODES
something after the table
''',
'''TIME 01/01/2023
something after the table
''',
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
[],
5  # no. writes
),

# empty table and table in the same date
('''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
  node_2        WELLHEAD     1167.3 #
  ENDNODES

NODES
  NAME                           TYPE       DEPTH   TEMP
  node3        WELL     1167.3  60
  ENDNODES

something after the table
''',
'''TIME 01/01/2023

NODES
  NAME                           TYPE       DEPTH   TEMP
  node3        WELL     1167.3  60
  ENDNODES

something after the table
''',
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'node3', 'type': 'WELL', 'depth': 1167.3,  'temp': 60, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
],
5  # no. writes
),

('''TIME 01/01/2022
NODES
  NAME  TYPE       DEPTH   TEMP
node3        WELL     1167.3  60
ENDNODES

TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
 ! comment
  node_2        WELLHEAD     1167.3 # 
  ENDNODES

TIME 01/01/2024
NODES
  NAME                           TYPE       DEPTH   TEMP
  node3        WELL     1167.3  60
  ENDNODES

something after the table
''',
'''TIME 01/01/2022
NODES
  NAME  TYPE       DEPTH   TEMP
node3        WELL     1167.3  60
ENDNODES

TIME 01/01/2023

TIME 01/01/2024
NODES
  NAME                           TYPE       DEPTH   TEMP
  node3        WELL     1167.3  60
  ENDNODES

something after the table
''',
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'node3', 'type': 'WELL', 'depth': 1167.3,  'temp': 60, 'date': '01/01/2022', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node3', 'type': 'WELL', 'depth': 1167.3,  'temp': 60, 'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
],
5  # no. writes
),
], ids=['basic_test', 'by ID', 'more tables and timestamps','empty table', 'empty table and table in the same date',
'empty table and different date'])
def test_remove_node(mocker, file_contents, expected_file_contents, node_to_remove, expected_nodes,
                     expected_number_writes):
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

    expected_nodes = [NexusNode(node) for node in expected_nodes]

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
    # Act
    nexus_sim.network.nodes.remove(node_to_remove)
    result_nodes = nexus_sim.network.nodes.get_all()

    # Assert
    assert result_nodes == expected_nodes
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)


@pytest.mark.parametrize('file_contents, expected_file_contents, node_to_add, expected_nodes, expected_number_writes', [
# basic_test
('''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
  node1                         NA            NA      #
  ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME                           TYPE       DEPTH   TEMP
  node1                         NA            NA      #
node_2 WELLHEAD 1167.3 NA
  ENDNODES
''',
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'node1', 'type': None, 'depth': None,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023',
    'unit_system': UnitSystem.ENGLISH}],
1  # no. writes
),

# additional headers
('''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP
  node1 WELLHEAD 100 100
  ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP STATION
  node1 WELLHEAD 100 100 NA
node_2 WELLHEAD 1167.3 NA station_1
  ENDNODES
''',
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'station': 'station_1',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'node1', 'type': 'WELLHEAD', 'depth': 100,  'temp': 100, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023', 'station': 'station_1',
    'unit_system': UnitSystem.ENGLISH}],
1  # no. writes
),

# more time cards
('''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP 
  test_node1 WELLHEAD 100 100 
ENDNODES
  
  TIME 01/01/2024
NODES
  NAME          TEMP    TYPE
  test_node2    100     WELL
ENDNODES
  
  TIME 01/01/2025
NODES
  NAME TYPE DEPTH  X Y  ! comment to test for keyword in comment ENDNODES
  test_node3 WELLHEAD 1167.3 100 100 ! NODES
ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP 
  test_node1 WELLHEAD 100 100 
ENDNODES
  
  TIME 01/01/2024
NODES
  NAME          TEMP    TYPE DEPTH STATION
  test_node2    100     WELL NA NA
new_node NA WELLHEAD 1167.3 station_1
ENDNODES
  
  TIME 01/01/2025
NODES
  NAME TYPE DEPTH  X Y  ! comment to test for keyword in comment ENDNODES
  test_node3 WELLHEAD 1167.3 100 100 ! NODES
ENDNODES
''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'test_node1', 'type': 'WELLHEAD', 'depth': 100,  'temp': 100, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'test_node2', 'type': 'WELL', 'temp': 100, 'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
{'name': 'test_node3', 'type': 'WELLHEAD', 'x_pos': 100, 'y_pos': 100, 'depth': 1167.3, 'date': '01/01/2025', 'unit_system': UnitSystem.ENGLISH},
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
],
1  # no. writes
),

# no existing time card for specified date (write out full nodes table)
('''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP 
  test_node1 WELLHEAD 100 100 
ENDNODES

  TIME 01/01/2025
NODES
  NAME TYPE DEPTH  X Y
  test_node3 WELLHEAD 1167.3 100 100 ! NODES
ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP 
  test_node1 WELLHEAD 100 100 
ENDNODES


TIME 01/01/2024
NODES
NAME TYPE DEPTH STATION
new_node WELLHEAD 1167.3 station_1
ENDNODES

  TIME 01/01/2025
NODES
  NAME TYPE DEPTH  X Y
  test_node3 WELLHEAD 1167.3 100 100 ! NODES
ENDNODES
''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'test_node1', 'type': 'WELLHEAD', 'depth': 100,  'temp': 100, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'test_node3', 'type': 'WELLHEAD', 'x_pos': 100, 'y_pos': 100, 'depth': 1167.3, 'date': '01/01/2025', 'unit_system': UnitSystem.ENGLISH},
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
],
1
),

# existing date card but no table
('''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP 
  test_node1 WELLHEAD 100 100 
ENDNODES
TIME 01/01/2024
NODECONS
NAME X Y LENGTH
test_con 1.254 12.0 10.2
ENDNODECONS
  TIME 01/01/2025
NODES
  NAME TYPE DEPTH  X Y
  test_node3 WELLHEAD 1167.3 100 100 ! NODES
ENDNODES
''',
'''TIME 01/01/2023
NODES
  NAME TYPE DEPTH TEMP 
  test_node1 WELLHEAD 100 100 
ENDNODES
TIME 01/01/2024
NODECONS
NAME X Y LENGTH
test_con 1.254 12.0 10.2
ENDNODECONS

NODES
NAME TYPE DEPTH STATION
new_node WELLHEAD 1167.3 station_1
ENDNODES

  TIME 01/01/2025
NODES
  NAME TYPE DEPTH  X Y
  test_node3 WELLHEAD 1167.3 100 100 ! NODES
ENDNODES
''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'test_node1', 'type': 'WELLHEAD', 'depth': 100,  'temp': 100, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'test_node3', 'type': 'WELLHEAD', 'x_pos': 100, 'y_pos': 100, 'depth': 1167.3, 'date': '01/01/2025', 'unit_system': UnitSystem.ENGLISH},
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
],
1
),
# reaching end of file
('''TIME 01/01/2023
''',
'''TIME 01/01/2023

TIME 01/01/2024
NODES
NAME TYPE DEPTH STATION
new_node WELLHEAD 1167.3 station_1
ENDNODES

''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
[{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},],
1  # no. writes
),
], ids=['basic_test', 'additional headers', 'more time cards', 'no existing time card', 'existing date card but no table',
'hitting end of file'])
def test_add_node(mocker, file_contents, expected_file_contents, node_to_add, expected_nodes,
                  expected_number_writes):
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

    expected_nodes = [NexusNode(node) for node in expected_nodes]
    expected_nodes.sort(key=lambda x: x.name)

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
    # Act
    nexus_sim.network.nodes.add(node_to_add)
    # compare sets as order doesn't matter
    result_nodes = nexus_sim.network.nodes.get_all()
    result_nodes.sort(key=lambda x: x.name)
    # Assert
    assert result_nodes == expected_nodes
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)


@pytest.mark.parametrize('file_contents, expected_file_contents, node_to_modify, modified_properties, expected_nodes,'
                         'expected_number_writes', [
# basic_test
('''TIME 01/01/2023
NODES
NAME TYPE DEPTH STATION
new_node WELLHEAD 1167.3 station_1
keep_node WELL 1020 staTION2
ENDNODES
TIME 01/01/2024
''',
'''TIME 01/01/2023
NODES
NAME TYPE DEPTH STATION
keep_node WELL 1020 staTION2
new_node WELLHEAD 10 station_2
ENDNODES
TIME 01/01/2024
''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'depth': 10, 'station': 'station_2'},
[{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 10, 'station': 'station_2',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'keep_node', 'type': 'WELL', 'depth': 1020, 'station': 'staTION2',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
],
2  # no. writes
),

# replace nones
('''TIME 01/01/2023
NODES
NAME TYPE DEPTH STATION
new_node WELLHEAD 1167.3 station_1
keep_node WELL 1020 staTION2
ENDNODES
TIME 01/01/2024
''',
'''TIME 01/01/2023
NODES
NAME TYPE DEPTH STATION
keep_node WELL 1020 staTION2
new_node WELLHEAD NA station_2
ENDNODES
TIME 01/01/2024
''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'depth': None, 'station': 'station_2'},
[{'name': 'new_node', 'type': 'WELLHEAD', 'depth': None, 'station': 'station_2',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'keep_node', 'type': 'WELL', 'depth': 1020, 'station': 'staTION2',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
],
2  # no. writes
),


# changes to non-pre-existing columns
('''TIME 01/01/2023
NODES
NAME TYPE DEPTH STATION
new_node WELLHEAD 1167.3 station_1
keep_node WELL 1020 staTION2
ENDNODES
TIME 01/01/2024
''',
'''TIME 01/01/2023
NODES
NAME TYPE DEPTH STATION TEMP
keep_node WELL 1020 staTION2 NA
new_node WELLHEAD 1167.3 station_2 100
ENDNODES
TIME 01/01/2024
''',
{'name': 'new_node', 'type': 'WELLHEAD', 'depth': 1167.3, 'station': 'station_1',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'temp': 100, 'station': 'station_2'},
[{'name': 'new_node', 'type': 'WELLHEAD', 'temp': 100, 'depth': 1167.3, 'station': 'station_2',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
{'name': 'keep_node', 'type': 'WELL', 'depth': 1020, 'station': 'staTION2',
'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
],
2  # no. writes
),


], ids=['basic_test', 'replace nones', 'changes to non-pre-existing columns'])
def test_modify_node(mocker, file_contents, expected_file_contents, node_to_modify, modified_properties, expected_nodes,
                     expected_number_writes):
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

    expected_nodes = [NexusNode(node) for node in expected_nodes]
    expected_nodes.sort(key=lambda x: x.name)

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
    # Act
    nexus_sim.network.nodes.modify(node_to_modify, modified_properties)
    # compare sets as order doesn't matter
    result_nodes = nexus_sim.network.nodes.get_all()
    result_nodes.sort(key=lambda x: x.name)
    # Assert
    assert result_nodes == expected_nodes
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)
