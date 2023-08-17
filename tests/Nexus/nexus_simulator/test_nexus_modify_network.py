import uuid
import pytest
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator, check_file_read_write_is_correct


class TestNetworkModify:
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''
    file_contents = '''TIME 01/01/2019
    ! comment
    TIME 01/01/2020
    Something here!
    TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
test_name_2 test_node test_node_out PIPE 100  NA
ENDNODECON

WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  testwell   PRODUCER   94     2020     ON        CELLGRAD
  inj   WATER      95     2020     OFF        CALC
  bad_data
    ENDWELLS

WELLHEAD
WELL NAME DEPTH X Y\t IPVT\t IWAT
testwell testwell_wellhead 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
ENDWELLBORE

TIME 01/01/2024
'''

    def multiple_file_open_wrapper(self, filename, mode, mocker):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': self.fcs_file_contents,
            '/surface_file_01.dat': self.file_contents,
            '/nexus_data/runcontrol.dat': self.runcontrol_contents}
            ).return_value
        return mock_open

    def patch_simulator(self, mocker):
        def outer_mock_wrapper(filename, mode):
            return self.multiple_file_open_wrapper(filename, mode, mocker)

        mocker.patch("builtins.open", outer_mock_wrapper)
        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        # make a mock for the write operation
        writing_mock_open = mocker.mock_open()
        mocker.patch("builtins.open", writing_mock_open)
        return nexus_sim, writing_mock_open


    @pytest.mark.parametrize('expected_file_contents, obj_to_modify, modified_properties, expected_objs,'
                             'expected_number_writes', [
    # basic_test
    ('''TIME 01/01/2019
    ! comment
    TIME 01/01/2020
    Something here!
    TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
test_name_2 test_node test_node_out PIPE 376 NA
ENDNODECON

WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  testwell   PRODUCER   94     2020     ON        CELLGRAD
  inj   WATER      95     2020     OFF        CALC
  bad_data
    ENDWELLS

WELLHEAD
WELL NAME DEPTH X Y\t IPVT\t IWAT
testwell testwell_wellhead 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
ENDWELLBORE

TIME 01/01/2024
''',
{'name':'test_name_2', 'date': '01/01/2023'},
    {'name': 'test_name_2', 'roughness': 376},
    [
        {'name': 'test_name_1', 'node_in': 'test_node', 'node_out': 'test_node_out', 'con_type': 'PIPE', 'roughness': 3.2,
        'date': '01/01/2023', 'temperature_profile': 'tempprof', 'unit_system': UnitSystem.ENGLISH},
        {'name': 'test_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out', 'roughness': 376,
        'con_type': 'PIPE', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
        ],
    2  # no. writes
    ),
    ], ids=['basic_test'])
    def test_modify_connections(self, mocker, fixture_for_osstat_pathlib, expected_file_contents, obj_to_modify,
                                modified_properties, expected_objs, expected_number_writes):
        # Arrange
        nexus_sim, writing_mock_open = self.patch_simulator(mocker)
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
        check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                         modifying_mock_open=writing_mock_open,
                                         mocker_fixture=mocker, write_file_name='/surface_file_01.dat',
                                         number_of_writes=expected_number_writes)

    @pytest.mark.parametrize('expected_file_contents, obj_to_modify, modified_properties, expected_objs,'
                             'expected_number_writes', [
        # basic_test
    ('''TIME 01/01/2019
    ! comment
    TIME 01/01/2020
    Something here!
    TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
test_name_2 test_node test_node_out PIPE 100  NA
ENDNODECON

WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  inj   WATER      95     2020     OFF        CALC
  bad_data
testwell PRODUCER 94 2020.0 OFF CELLGRAD
    ENDWELLS

WELLHEAD
WELL NAME DEPTH X Y\t IPVT\t IWAT
testwell testwell_wellhead 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
ENDWELLBORE

TIME 01/01/2024
''',
    {'name':'testwell', 'date': '01/01/2023'},
        {'name': 'testwell', 'crossflow': 'OFF'},
        [
            {'name': 'testwell', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 2020, 'crossflow': 'OFF', 'crossshut_method': 'CELLGRAD',
            'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 2020, 'crossflow': 'OFF', 'crossshut_method': 'CALC',
            'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            ],
        2  # no. writes
        ),
        ], ids=['basic_test'])
    def test_modify_wellcons(self, mocker, fixture_for_osstat_pathlib, expected_file_contents, obj_to_modify,
                          modified_properties, expected_objs, expected_number_writes):
        # Arrange
        #TODO abstract NexusWellConnections
        nexus_sim, writing_mock_open = self.patch_simulator(mocker)
        expected_objs = [NexusWellConnection(obj) for obj in expected_objs]
        expected_objs.sort(key=lambda x: x.name)

        mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
        # Act
        nexus_sim.network.well_connections.modify(obj_to_modify, modified_properties)
        # compare sets as order doesn't matter
        result_nodes = nexus_sim.network.well_connections.get_all()
        result_nodes.sort(key=lambda x: x.name)

        # Assert
        assert result_nodes == expected_objs
        assert nexus_sim.model_files.surface_files[1].file_content_as_list == \
            expected_file_contents.splitlines(keepends=True)
        check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                         modifying_mock_open=writing_mock_open,
                                         mocker_fixture=mocker, write_file_name='/surface_file_01.dat',
                                         number_of_writes=expected_number_writes)

    @pytest.mark.parametrize('expected_file_contents, obj_to_modify, modified_properties, expected_objs,'
                             'expected_number_writes', [
        # basic_test
    ('''TIME 01/01/2019
    ! comment
    TIME 01/01/2020
    Something here!
    TIME 01/01/2023
NODECON
NAME        NODEIN     NODEOUT      TYPE ROUGHNESS  TEMPPR
test_name_1 test_node test_node_out PIPE 3.2        tempprof
test_name_2 test_node test_node_out PIPE 100  NA
ENDNODECON

WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  testwell   PRODUCER   94     2020     ON        CELLGRAD
  inj   WATER      95     2020     OFF        CALC
  bad_data
    ENDWELLS

WELLHEAD
WELL NAME DEPTH X Y\t IPVT\t IWAT
testwell testwell_wellhead 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM METHOD
testwell textdata 10.2 NEW_METHOD
ENDWELLBORE

TIME 01/01/2024
''',
    {'name': 'testwell', 'date': '01/01/2023'},
        {'name': 'testwell', 'METHOD': 'NEW_METHOD'},
        [
            {'name': 'testwell', 'temperature_profile': 'textdata', 'diameter': 10.2, 'hyd_method': 'NEW_METHOD',
            'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            ],
        2  # no. writes
        ),
        ], ids=['basic_test'])
    def test_modify_wellbores(self, mocker, fixture_for_osstat_pathlib, expected_file_contents, obj_to_modify,
                          modified_properties, expected_objs, expected_number_writes):
        # Arrange
        nexus_sim, writing_mock_open = self.patch_simulator(mocker)
        expected_objs = [NexusWellbore(obj) for obj in expected_objs]
        expected_objs.sort(key=lambda x: x.name)

        mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6'])
        # Act
        nexus_sim.network.wellbores.modify(obj_to_modify, modified_properties)
        # compare sets as order doesn't matter
        result_nodes = nexus_sim.network.wellbores.get_all()
        result_nodes.sort(key=lambda x: x.name)

        # Assert
        assert result_nodes == expected_objs
        assert nexus_sim.model_files.surface_files[1].file_content_as_list == expected_file_contents.splitlines(keepends=True)
        check_file_read_write_is_correct(expected_file_contents=expected_file_contents,
                                         modifying_mock_open=writing_mock_open,
                                         mocker_fixture=mocker, write_file_name='/surface_file_01.dat',
                                         number_of_writes=expected_number_writes)

    def test_modify_wellhead(self):
        pass