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
    nexus_sim.network.nodes.remove_node(node_to_remove)
    result_nodes = nexus_sim.network.nodes.get_nodes()

    # Assert
    assert result_nodes == expected_nodes
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)
    check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='/surface_file_01.dat',
                                     number_of_writes=expected_number_writes)
