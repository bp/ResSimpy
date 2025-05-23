import uuid
import pytest
from pytest_mock import MockerFixture

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator, check_file_read_write_is_correct


@pytest.mark.parametrize('file_contents, expected_file_contents, connection_to_add, expected_connections, expected_number_writes', [
# basic_test
('''TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
ENDNODECON
''',
'''TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR DPADD
test_name_1 test_node test_node_out PIPE 3.2        tempprof NA
tests_name_2 test_node test_node_out PIPE NA NA 100
ENDNODECON
''',
{'name': 'tests_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out', 'con_type': 'PIPE', 'date': '01/01/2023',
'unit_system': UnitSystem.ENGLISH, 'dp_add': 100, 'start_date': '01/01/2019'},
[
    {'name': 'test_name_1', 'node_in': 'test_node', 'node_out': 'test_node_out', 'con_type': 'PIPE', 'roughness': 3.2,
    'date': '01/01/2023', 'temperature_profile': 'tempprof', 'unit_system': UnitSystem.ENGLISH},
    {'name': 'tests_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out', 'dp_add': 100,
    'con_type': 'PIPE', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
    ],
1  # no. writes
),
], ids=['basic_test'])
def test_add_connection(mocker, file_contents, expected_file_contents, connection_to_add, expected_connections, expected_number_writes):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    start_date = '01/01/2019'
    runcontrol_contents = f'''START {start_date}'''

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

    expected_cons = [NexusNodeConnection(node, date_format=DateFormat.DD_MM_YYYY, 
                                         start_date=start_date) for node in expected_connections]
    expected_cons.sort(key=lambda x: x.name)

    expected_cons[0]._DataObjectMixin__id = 'uuid_1'
    expected_cons[1]._DataObjectMixin__id = 'uuid_2'

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=['uuid_1', 'uuid_2', 'uuid_3', 'uuid_4', 'uuid_5',
                                                                'uuid_6', 'uuid_7'])
    # Act
    nexus_sim.network.connections.add(connection_to_add)
    # compare sets as order doesn't matter
    result_connections = nexus_sim.network.connections.get_all()
    result_connections.sort(key=lambda x: x.name)

    # Assert
    assert result_connections == expected_cons
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)


@pytest.mark.parametrize('file_contents, expected_file_contents, connection_to_remove, expected_connection, expected_number_writes', [
# basic_test
('''TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
tests_name_2 test_node test_node_out PIPE 100  NA
ENDNODECON
''',
'''TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
tests_name_2 test_node test_node_out PIPE 100  NA
ENDNODECON
''',
{'name': 'test_name_1', 'date': '01/01/2023'},
[{'name': 'tests_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out', 'roughness': 100,
    'con_type': 'PIPE', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
    ],
1  # no. writes
),
], ids=['basic_test',])
def test_remove_connection(mocker, file_contents, expected_file_contents, connection_to_remove, expected_connection,
                         expected_number_writes):
        # Arrange
        fcs_file_contents = '''
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            RECURRENT_FILES
            RUNCONTROL /nexus_data/runcontrol.dat
            SURFACE Network 1  /surface_file_01.dat
            '''
        start_date = '01/01/2019'
        runcontrol_contents = '''START 01/01/2019'''

        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=['uuid_1', 'uuid_2', 'uuid_3', 'uuid_4', 'uuid_5',
                                                                    'uuid_6', 'uuid_7'])

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

        expected_connection = [NexusNodeConnection(node, date_format=DateFormat.DD_MM_YYYY,
                                                   start_date=start_date) for node in expected_connection]
        expected_connection[0]._DataObjectMixin__id = 'uuid_3'

        # Act
        nexus_sim.network.connections.remove(connection_to_remove)
        result_nodes = nexus_sim.network.connections.get_all()

        # Assert
        assert result_nodes == expected_connection
        assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)


@pytest.mark.parametrize('file_contents, expected_file_contents, obj_to_modify, modified_properties, expected_objs,'
                         'expected_number_writes', [
# basic_test
('''TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
test_name_2 test_node test_node_out PIPE 100  NA
ENDNODECON
TIME 01/01/2024
''',
'''TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
test_name_2 test_node test_node_out PIPE 376 NA
ENDNODECON
TIME 01/01/2024
''',
{'name':'test_name_2', 'date': '01/01/2023'},
{'name': 'test_name_2', 'roughness': 376,},
[
    {'name': 'test_name_1', 'node_in': 'test_node', 'node_out': 'test_node_out', 'con_type': 'PIPE', 'roughness': 3.2,
    'date': '01/01/2023', 'temperature_profile': 'tempprof', 'unit_system': UnitSystem.ENGLISH, 'start_date': '01/01/2019'},
    {'name': 'test_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out', 'roughness': 376,
    'con_type': 'PIPE', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH, 'start_date': '01/01/2019'},
    ],
2  # no. writes
),


], ids=['basic_test'])
def test_modify_connections(mocker, file_contents, expected_file_contents, obj_to_modify, modified_properties, expected_objs,
                     expected_number_writes):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    start_date = '01/01/2019'
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

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=['uuid_1', 'uuid_3'])

    expected_objs = [NexusNodeConnection(node, date_format=DateFormat.DD_MM_YYYY,
                                         start_date=start_date) for node in expected_objs]
    expected_objs.sort(key=lambda x: x.name)

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=['uuid_1', 'uuid_2', 'uuid_3', 'uuid_4', 'uuid_5',
                                                                'uuid_6', 'uuid_7'])
    # Act
    nexus_sim.network.connections.modify(obj_to_modify, modified_properties)
    # compare sets as order doesn't matter
    result_nodes = nexus_sim.network.connections.get_all()
    result_nodes.sort(key=lambda x: x.name)
    # Assert
    assert result_nodes == expected_objs
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)


@pytest.mark.parametrize('connections, obj_to_check, expected_connected_objects', [
    # One after
    ([NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_wh', properties_dict={},
                                       date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
                   NexusNodeConnection(name='well_1_wh', node_in='well_1', node_out='SINK', properties_dict={},
                                       date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)],

    'well_1',
    ([],
     [NexusNodeConnection(name='well_1_wh', node_in='well_1', node_out='SINK',
                                                      properties_dict={}, date='25/07/2026',
                                        date_format=DateFormat.DD_MM_YYYY)])),

     # One before
        ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1', properties_dict={},
                              date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
             NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_wh', properties_dict={},
                              date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)],

         'well_1',
         ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1',
                               properties_dict={}, date='25/07/2026',
                               date_format=DateFormat.DD_MM_YYYY)],
         [])),

     # No connected nodes
        ([NexusNodeConnection(name='well_1', node_in='well_1', node_out='SINK', properties_dict={},
                              date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)],

         'well_1',
         ([],
          [])),

    # Multiple before + after
    ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1_pipe_in', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_in', node_in='well_1_gl', node_out='well_1', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_pipe_out', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_out', node_in='well_1', node_out='well_1_wh', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe_out', node_out='SINK', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)
      ],

     'well_1',

     ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1_pipe_in', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_in', node_in='well_1_gl', node_out='well_1', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),],
      [NexusNodeConnection(name='well_1_pipe_out', node_in='well_1', node_out='well_1_wh', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe_out', node_out='SINK', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)])),

    # Non well object
    ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1_pipe_in', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_in', node_in='well_1_gl', node_out='well_1', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_pipe_out', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_out', node_in='well_1', node_out='well_1_wh', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe_out', node_out='SINK', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)
      ],

     'well_1_pipe_out',

     ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1_pipe_in', properties_dict={},
                           date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
       NexusNodeConnection(name='well_1_pipe_in', node_in='well_1_gl', node_out='well_1', properties_dict={},
                           date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
       NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_pipe_out', properties_dict={},
                           date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)],

      [NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe_out', node_out='SINK', properties_dict={},
                           date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)])),

    # Non well object higher up
    ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1_pipe_in', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_in', node_in='well_1_gl', node_out='well_1', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_pipe_out', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe_out', node_in='well_1', node_out='well_1_wh', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe_out', node_out='SINK', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)
      ],

     'well_1_pipe_in',

     ([NexusNodeConnection(name='well_1_gl', node_in='GAS', node_out='well_1_pipe_in', properties_dict={},
                           date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)],

    [NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1_pipe_out', properties_dict={},
                         date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
     NexusNodeConnection(name='well_1_pipe_out', node_in='well_1', node_out='well_1_wh', properties_dict={},
                         date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe_out', node_out='SINK', properties_dict={},
                       date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)])),

    # Info from other node
    ([NexusNodeConnection(name='well_1', node_in='well_1', node_out='well_1', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_pipe', node_in='well_1', node_out='well_1_pipe', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe', node_out='SINK', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)
      ],

     'well_1',
     ([],
      [NexusNodeConnection(name='well_1_pipe', node_in='well_1', node_out='well_1_pipe', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY),
      NexusNodeConnection(name='well_1_wh', node_in='well_1_pipe', node_out='SINK', properties_dict={},
                          date='25/07/2026', date_format=DateFormat.DD_MM_YYYY)
       ])),

], ids=['One after', 'One before', 'No connected nodes', 'Multiple before + after', 'Non well object',
        'Non well object different location', 'info from other node'])
def test_get_connected_objects(mocker: MockerFixture, connections, obj_to_check, expected_connected_objects):
    # Arrange

    dummy_model = get_fake_nexus_simulator(mocker=mocker)
    network_obj = NexusNetwork(assume_loaded=True, model=dummy_model)
    node_connections_obj = NexusNodeConnections(parent_network=network_obj)
    node_connections_obj._connections = connections
    network_obj.connections = node_connections_obj

    # Act
    result = network_obj.get_connected_objects(connection_name=obj_to_check)

    # Assert
    assert result == expected_connected_objects

def test_print_connected_objects(mocker):
        # Arrange
        fcs_file_contents = '''
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            RECURRENT_FILES
            RUNCONTROL /nexus_data/runcontrol.dat
            SURFACE Network 1  /surface_file_01.dat
            '''

        runcontrol_contents = '''START 01/01/2019'''

        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=['uuid_1', 'uuid_2', 'uuid_3', 'uuid_4', 'uuid_5',
                                                                    'uuid_6', 'uuid_7'])

        surface_file_contents = """ NODECON
NAME        NODEIN     NODEOUT      TYPE  DPADD
well_1_gl   GAS well_1_pipe_in  GASLIFT  NA
well_1_pipe_in   well_1_gl well_1  PIPE  NA
well_1  well_1  well_1_pipe_out   PIPE    -35.8
well_1_pipe_out   well_1 well_1_wh  PIPE  NA
well_1_wh   well_1_wh   SINK    NA  NA 
well_2  well_2  well_2_wh   NA NA 
ENDNODECON
"""

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': fcs_file_contents,
                '/surface_file_01.dat': surface_file_contents,
                '/nexus_data/runcontrol.dat': runcontrol_contents}
                ).return_value
            return mock_open
        mocker.patch("builtins.open", mock_open_wrapper)
        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        # make a mock for the write operation
        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)

        expected_output = \
"""NAME            TYPE
-----------------------
well_1_gl       GASLIFT
well_1_pipe_in  PIPE

well_1          PIPE - Requested Node

well_1_pipe_out PIPE
well_1_wh       None
"""

        # Act
        result = nexus_sim.network.print_connected_objects(connection_name='well_1')

        # Assert
        assert result == expected_output
