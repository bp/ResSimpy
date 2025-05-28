import uuid
import pytest

from ResSimpy.Enums.FluidTypeEnums import PhaseType
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusDrill import NexusDrill
from ResSimpy.Nexus.DataModels.Network.NexusDrillSite import NexusDrillSite
from ResSimpy.Nexus.DataModels.Network.NexusGuideRate import NexusGuideRate
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
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
    start_date = '01/01/2019'
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

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL

GUIDERATE
TARGET    DTMIN   PHASE   A B C D E F INCREASE DAMP
targ_1     12.1      GAS     1 0 2.1 3 8 4 YES  1.15      
ENDGUIDERATE

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
                             'obj_to_modify, modified_properties, expected_objs, expected_ids', [
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

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL

GUIDERATE
TARGET    DTMIN   PHASE   A B C D E F INCREASE DAMP
targ_1     12.1      GAS     1 0 2.1 3 8 4 YES  1.15      
ENDGUIDERATE

TIME 01/01/2024
''',
                                  {'well': 'testwell', 'name': 'testwell_wellhead', 'date': '01/01/2023',
                                   'depth': 1000},
                                  {'name': 'testwell_wellhead', 'x_pos': 1},
                                  [
                                      {'well': 'testwell', 'name': 'testwell_wellhead', 'date': '01/01/2023',
                                       'depth': 1000, 'x_pos': 1,
                                       'y_pos': 302, 'pvt_method': 2, 'water_method': 3,
                                       'unit_system': UnitSystem.ENGLISH, 'date_format': DateFormat.DD_MM_YYYY},
                                      {'well': 'testwell2', 'name': 'testwell_wellhead2', 'date': '01/01/2023',
                                       'depth': 1000, 'x_pos': 102,
                                       'y_pos': 302, 'pvt_method': 2, 'water_method': 3,
                                       'unit_system': UnitSystem.ENGLISH, 'date_format': DateFormat.DD_MM_YYYY},
                                  ],
                                  ['uuid_9', 'uuid_6']
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

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL

GUIDERATE
TARGET    DTMIN   PHASE   A B C D E F INCREASE DAMP
targ_1     12.1      GAS     1 0 2.1 3 8 4 YES  1.15      
ENDGUIDERATE

TIME 01/01/2024
''',
                                  {'name': 'testwell', 'date': '01/01/2023'},
                                  {'name': 'testwell', 'hyd_method': 'NEW_METHOD'},
                                  [
                                      {'name': 'testwell', 'temperature_profile': 'textdata', 'diameter': 10.2,
                                       'hyd_method': 'NEW_METHOD',
                                       'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH,
                                       'date_format': DateFormat.DD_MM_YYYY},
                                      {'name': 'testwell2', 'temperature_profile': 'temppr',
                                       'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH,
                                       'date_format': DateFormat.DD_MM_YYYY},
                                  ],
                                  ['uuid_9', 'uuid_8']
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

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL

GUIDERATE
TARGET    DTMIN   PHASE   A B C D E F INCREASE DAMP
targ_1     12.1      GAS     1 0 2.1 3 8 4 YES  1.15      
ENDGUIDERATE

TIME 01/01/2024
''',
                                  {'name': 'testwell', 'date': '01/01/2023'},
                                  {'name': 'testwell', 'crossflow': 'OFF'},
                                  [
                                      {'name': 'testwell', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 2020,
                                       'crossflow': 'OFF',
                                       'crossshut': 'CELLGRAD', 'date': '01/01/2023',
                                       'unit_system': UnitSystem.ENGLISH, 'date_format': DateFormat.DD_MM_YYYY},
                                      {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 2020,
                                       'crossflow': 'OFF',
                                       'crossshut': 'CALC', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH,
                                       'date_format': DateFormat.DD_MM_YYYY},
                                  ],
                                  ['uuid_9', 'uuid_4']
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

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL

GUIDERATE
TARGET    DTMIN   PHASE   A B C D E F INCREASE DAMP
targ_1     12.1      GAS     1 0 2.1 3 8 4 YES  1.15      
ENDGUIDERATE

TIME 01/01/2024
''',
                                  {'name': 'test_name_2', 'date': '01/01/2023'},
                                  {'name': 'test_name_2', 'roughness': 376},
                                  [
                                      {'name': 'test_name_1', 'node_in': 'test_node', 'node_out': 'test_node_out',
                                       'con_type': 'PIPE', 'roughness': 3.2,
                                       'date': '01/01/2023', 'temperature_profile': 'tempprof',
                                       'unit_system': UnitSystem.ENGLISH, 'date_format': DateFormat.DD_MM_YYYY},
                                      {'name': 'test_name_2', 'node_in': 'test_node', 'node_out': 'test_node_out',
                                       'roughness': 376,
                                       'con_type': 'PIPE', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH,
                                       'date_format': DateFormat.DD_MM_YYYY},
                                  ],
                                  ['uuid_1', 'uuid_9']
                                  ),
        # NexusDrill
        (NexusDrill, 'drills',
         """TIME 01/01/2019
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

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE



DRILL
WELL DRILLSITE DRILLTIME CMPLTIME WORKTIME RIGS
well_1 site_1 123 0 0 ALL
ENDDRILL

TIME 01/01/2024
""",
         {'name': 'well_1', 'drill_time': 654.1, 'date': '01/01/2023', 'date_format': DateFormat.DD_MM_YYYY},
         {'name': 'well_1', 'drill_time': 123},
         [{'name': 'well_1', 'drill_time': 123, 'date': '01/01/2023', 'date_format': DateFormat.DD_MM_YYYY,
           'drill_site': 'site_1'}],
         ['uuid_10']
         ),

        # NexusDrillSite
        (NexusDrillSite, 'drill_sites',
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
WELL TEMPPR DIAM
testwell textdata 10.2
testwell2 temppr NA
ENDWELLBORE

DRILLSITE
NAME    MAXRIGS
site_2  1
site_1 4
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL

TIME 01/01/2024
''',
         {'name': 'site_1', 'max_rigs': 5, 'date': '01/01/2023', 'date_format': DateFormat.DD_MM_YYYY},
         {'name': 'site_1', 'max_rigs': 4},
         [{'name': 'site_1', 'max_rigs': 4, 'date': '01/01/2023', 'date_format': DateFormat.DD_MM_YYYY},
          {'name': 'site_2', 'max_rigs': 1, 'date': '01/01/2023', 'date_format': DateFormat.DD_MM_YYYY},],
         ['uuid_11', 'uuid_12']
         ),

        # NexusGuideRate
        (NexusGuideRate, 'guide_rates',
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
WELL TEMPPR DIAM
testwell textdata 10.2
testwell2 temppr NA
ENDWELLBORE

DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL



GUIDERATE
TARGET DTMIN PHASE A B C D E F INCREASE DAMP
targ_1 10.1 GAS 1.0 4.0 2.1 3.0 8.0 4.0 YES 1.15
ENDGUIDERATE

TIME 01/01/2024
''',
         {'name': 'targ_1', 'time_interval': 12.1, 'phase': PhaseType.GAS, 'date_format': DateFormat.DD_MM_YYYY,
          'date': '01/01/2023'},
         {'time_interval': 10.1, 'b': 4.0},
         [{'name': 'targ_1', 'time_interval': 10.1, 'phase': PhaseType.GAS, 'date_format': DateFormat.DD_MM_YYYY,
           'date': '01/01/2023', 'a': 1, 'b': 4, 'c': 2.1, 'd': 3, 'e': 8, 'f': 4, 'increase_permitted': True,
           'damping_factor': 1.15}],
         ['uuid_13']
         )

         ], ids=['wellhead', 'wellbore', 'wellconnection', 'nodeconnections', 'NexusDrill', 'NexusDrillSite',
                 'NexusGuideRate'])
    def test_modify_network_component(self, mocker, object_type, network_component,
                                      expected_file_contents, obj_to_modify,
                                      modified_properties, expected_objs, expected_ids):

        # Arrange
        nexus_sim, writing_mock_open = self.patch_simulator(mocker)
        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=expected_ids)

        expected_objects = [object_type(properties_dict=obj, start_date=self.start_date) for obj in expected_objs]
        expected_objects.sort(key=lambda x: x.name)

        # Reset the ID allocation
        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', side_effect=['uuid_1', 'uuid_2', 'uuid_3', 'uuid_4', 'uuid_5',
                                                                    'uuid_6', 'uuid_7', 'uuid_8', 'uuid_9', 'uuid_10',
                                                                    'uuid_11', 'uuid_12', 'uuid_13'])

        # Act
        network_objects = getattr(nexus_sim.network, network_component)
        network_objects.modify(obj_to_modify, modified_properties)
        # reorder to ensure direct comparison on named objects
        result_nodes = network_objects.get_all()
        result_nodes.sort(key=lambda x: x.name)

        # Assert
        assert result_nodes == expected_objects
        assert nexus_sim.model_files.surface_files[1].file_content_as_list == \
               expected_file_contents.splitlines(keepends=True)
