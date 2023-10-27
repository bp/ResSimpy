import uuid
import pytest
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator, check_file_read_write_is_correct, uuid_side_effect


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
testwell2 testwell_wellhead2 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
testwell2 temppr NA
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


    @pytest.mark.parametrize('object_type, network_component, expected_file_contents, '
        'obj_to_modify, modified_properties, expected_objs,', [
        # NexusWellhead test
        (NexusWellhead, 'wellheads',
        '''TIME 01/01/2019
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
testwell2 testwell_wellhead2 1000 102 302 2 3
testwell testwell_wellhead 1000.0 1 302.0 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
testwell2 temppr NA
ENDWELLBORE

TIME 01/01/2024
''',
    {'well': 'testwell', 'name': 'testwell_wellhead', 'date': '01/01/2023', 'depth': 1000},
    {'name': 'testwell_wellhead', 'x_pos': 1},
        [
            {'well': 'testwell', 'name': 'testwell_wellhead', 'date': '01/01/2023', 'depth': 1000, 'x_pos': 1,
            'y_pos': 302, 'pvt_method': 2, 'water_method': 3, 'unit_system': UnitSystem.ENGLISH},
            {'well': 'testwell2', 'name': 'testwell_wellhead2', 'date': '01/01/2023', 'depth': 1000, 'x_pos': 102,
                'y_pos': 302, 'pvt_method': 2, 'water_method': 3, 'unit_system': UnitSystem.ENGLISH},
            ],
        ),

    # NexusWellbore TEST
    (NexusWellbore, 'wellbores',
    '''TIME 01/01/2019
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
testwell2 testwell_wellhead2 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM METHOD
testwell2 temppr NA NA
testwell textdata 10.2 NEW_METHOD
ENDWELLBORE

TIME 01/01/2024
''',
    {'name': 'testwell', 'date': '01/01/2023'},
        {'name': 'testwell', 'hyd_method': 'NEW_METHOD'},
        [
            {'name': 'testwell', 'temperature_profile': 'textdata', 'diameter': 10.2, 'hyd_method': 'NEW_METHOD',
            'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'testwell2', 'temperature_profile': 'temppr',
                'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            ],
    ),

# WELLCONNECTIONS TEST
    (NexusWellConnection, 'well_connections',
    '''TIME 01/01/2019
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
testwell2 testwell_wellhead2 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
testwell2 temppr NA
ENDWELLBORE

TIME 01/01/2024
''',
    {'name':'testwell', 'date': '01/01/2023'},
        {'name': 'testwell', 'crossflow': 'OFF'},
        [
            {'name': 'testwell', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 2020, 'crossflow': 'OFF',
             'crossshut': 'CELLGRAD', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 2020, 'crossflow': 'OFF',
             'crossshut': 'CALC', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
            ],
    ),

    # NexusNodeConnection test
    (NexusNodeConnection, 'connections',
    '''TIME 01/01/2019
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
testwell2 testwell_wellhead2 1000 102 302 2 3
ENDWELLHEAD

WELLBORE
WELL TEMPPR DIAM
testwell textdata 10.2
testwell2 temppr NA
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
        ),
        ], ids=['wellhead', 'wellbore', 'wellconnection', 'nodeconnections'])
    def test_modify_network_component(self, mocker, object_type, network_component,
                                      expected_file_contents, obj_to_modify,
                                      modified_properties, expected_objs):
        # Arrange
        mocker.patch.object(uuid, 'uuid4', side_effect=uuid_side_effect)

        nexus_sim, writing_mock_open = self.patch_simulator(mocker)
        expected_objs = [object_type(obj) for obj in expected_objs]
        expected_objs.sort(key=lambda x: x.name)

        # Act
        network_objects = getattr(nexus_sim.network, network_component)
        network_objects.modify(obj_to_modify, modified_properties)
        # reorder to ensure direct comparison on named objects
        result_nodes = network_objects.get_all()
        result_nodes.sort(key=lambda x: x.name)

        # Assert
        assert result_nodes == expected_objs
        assert nexus_sim.model_files.surface_files[1].file_content_as_list == \
            expected_file_contents.splitlines(keepends=True)
