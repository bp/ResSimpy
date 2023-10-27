import uuid
import pytest
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
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
'unit_system': UnitSystem.ENGLISH, 'dp_add': 100},
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

    expected_cons = [NexusNodeConnection(node) for node in expected_connections]
    expected_cons.sort(key=lambda x: x.name)

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
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

        expected_connection = [NexusNodeConnection(node) for node in expected_connection]

        mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
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
    'date': '01/01/2023', 'temperature_profile': 'tempprof', 'unit_system': UnitSystem.ENGLISH},
    {'name': 'test_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out', 'roughness': 376,
    'con_type': 'PIPE', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
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

    expected_objs = [NexusNodeConnection(node) for node in expected_objs]
    expected_objs.sort(key=lambda x: x.name)

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
    # Act
    nexus_sim.network.connections.modify(obj_to_modify, modified_properties)
    # compare sets as order doesn't matter
    result_nodes = nexus_sim.network.connections.get_all()
    result_nodes.sort(key=lambda x: x.name)
    # Assert
    assert result_nodes == expected_objs
    assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)
