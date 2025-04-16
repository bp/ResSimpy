import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from ResSimpy import NexusSimulator
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange
from ResSimpy.Nexus.DataModels.Network.NexusProc import NexusProc
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Time.ISODateTime import ISODateTime
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnections import NexusWellConnections
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellbores import NexusWellbores
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.Network.NexusWellheads import NexusWellheads
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusWells import NexusWells
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


@pytest.mark.parametrize('file_contents, node1_props, node2_props', [
    ('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH}
     ),
    ('''NODES
  NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
 ! Riser Nodes
  node1         NA        NA    60.5    100.5 300.5   1     station
  node_2        WELLHEAD     1167.3 #  10.21085 3524.23 2   station2 ! COMMENT 
  ENDNODES
  content outside of the node statement
  node1         NA        NA    60.5    10.5 3.5   1     station_null
  ''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
      'station': 'station', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23,
      'number': 2,
      'station': 'station2', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH}
     ),
    ('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  ENDNODES
  TIME 01/02/2023
  NODES
    NAME                           TYPE       DEPTH   TEMP

  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/02/2023',
      'unit_system': UnitSystem.ENGLISH}
     ),
    ('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  ENDNODES
  METRIC
  TIME 01/02/2023
  NODES
    NAME                           TYPE       DEPTH   TEMP

  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/02/2023',
      'unit_system': UnitSystem.METRIC}
     ),
    ('''NODES
  NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
 ! Riser Nodes
  node1         NA        NA    60.5    100.5 300.5   1     station
  ENDNODES
  NODES
    NAME       TYPE       DEPTH   TemP       NUMBER  StatiON    
node_2        WELLHEAD     1167.3 #  2   station2 
ENDNODES
  content outside of the node statement
  node1         NA        NA    60.5    10.5 3.5   1     station_null
  ''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
      'station': 'station', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': None, 'y_pos': None, 'number': 2,
      'station': 'station2', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH}
     ),

    ('''TIME 01/01/2023
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
     {'name': 'test_node2', 'type': 'WELL', 'temp': 100, 'date': '01/01/2024', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'test_node3', 'type': 'WELLHEAD', 'depth': 1167.3, 'x_pos': 100, 'y_pos': 100, 'date': '01/01/2025',
      'unit_system': UnitSystem.ENGLISH},
     )
],
                         ids=['basic', 'all columns', 'times', 'units', 'two tables', 'keyword in column']
                         )
def test_load_nexus_nodes(mocker: MockerFixture, file_contents, node1_props, node2_props):
    # Arrange
    # mock out a surface file:
    start_date = '01/01/2023'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    node_1 = NexusNode(properties_dict=node1_props, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    node_2 = NexusNode(properties_dict=node2_props, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.MM_DD_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    expected_result = [node_1, node_2]
    # get the second node only
    second_node_name = node2_props['name']
    # Act

    nexus_nodes = NexusNodes(mock_nexus_network)
    nexus_nodes.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_nodes.get_all()
    single_node_result = nexus_nodes.get_by_name(second_node_name)

    # Assert
    assert result == expected_result
    assert single_node_result == node_2
    if single_node_result.depth is not None:
        assert single_node_result.depth / 2 == 1167.3 / 2


@pytest.mark.parametrize('file_contents, node1_props, node2_props', [
    ('''NODES
  NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
 ! Riser Nodes
  node1         NA        NA    60.5    100.5 300.5   1     station
  node_2        WELLHEAD     1167.3 #  10.21085 3524.23 2   station2 ! COMMENT 
  ENDNODES
  content outside of the node statement
  node1         NA        NA    60.5    10.5 3.5   1     station_null
  ''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
      'station': 'station', 'date': '01/01/2023', 'unit_system': 'ENGLISH'},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23,
      'number': 2,
      'station': 'station2', 'date': '01/01/2023', 'unit_system': 'ENGLISH'}
     )], )
def test_get_node_df(mocker, file_contents, node1_props, node2_props):
    # Arrange
    start_date = '01/01/2023'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_nodes = NexusNodes(mock_nexus_network)
    nexus_nodes.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)

    node1_props['iso_date'] = ISODateTime.convert_to_iso(date=node1_props['date'], date_format=DateFormat.DD_MM_YYYY)
    node2_props['iso_date'] = ISODateTime.convert_to_iso(date=node2_props['date'], date_format=DateFormat.DD_MM_YYYY)

    expected_df = pd.DataFrame([node1_props, node2_props])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')
    # Act
    result = nexus_nodes.get_df()

    # Assert
    pd.testing.assert_frame_equal(result, expected_df, check_like=True)


@pytest.mark.parametrize('file_contents, connection1_props, connection2_props', [
    ('''NODECON
	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
	CP01            CP01      wh_cp01       PIPE        2          7002.67
	cp01_gaslift    GAS       CP01          GASLIFT     NONE        NA ! Checked NODECON 13/05/2020 
	ENDNODECON
	''',
     {'name': 'CP01', 'node_in': 'CP01', 'node_out': 'wh_cp01', 'con_type': 'PIPE', 'hyd_method': '2',
      'delta_depth': 7002.67, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'cp01_gaslift', 'node_in': 'GAS', 'node_out': 'CP01', 'con_type': 'GASLIFT', 'hyd_method': None,
      'delta_depth': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},),
    ('''NODES
  NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
 ! Riser Nodes
  node1         NA        NA    60.5    100.5 300.5   1     station
  node_2        WELLHEAD     1167.3 #  10.21085 3524.23 2   station2 ! COMMENT 
  ENDNODES
  NODECON
	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH    DPADD
	CP01            CP01      wh_cp01       PIPE        2          7002.67  20486
	cp01_gaslift    GAS       CP01          GASLIFT     NONE        NA    1000.23! Checked NODECON 13/05/2020 
	ENDNODECON''',
     {'name': 'CP01', 'node_in': 'CP01', 'node_out': 'wh_cp01', 'con_type': 'PIPE', 'hyd_method': '2',
      'delta_depth': 7002.67, 'dp_add': 20486, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'cp01_gaslift', 'node_in': 'GAS', 'node_out': 'CP01', 'con_type': 'GASLIFT', 'hyd_method': None,
      'delta_depth': None, 'dp_add': 1000.23, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},),
    (''' TIME 01/02/2023
  NODECON
	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
	CP01            CP01      wh_cp01       PIPE        2          7002.67
	ENDNODECON
	TIME 01/03/2023
	NODECON
		NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
	cp01_gaslift    GAS       CP01          GASLIFT     NONE        NA ! Checked NODECON 13/05/2020 
	ENDNODECON''',
     {'name': 'CP01', 'node_in': 'CP01', 'node_out': 'wh_cp01', 'con_type': 'PIPE', 'hyd_method': '2',
      'delta_depth': 7002.67, 'date': '01/02/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'cp01_gaslift', 'node_in': 'GAS', 'node_out': 'CP01', 'con_type': 'GASLIFT', 'hyd_method': None,
      'delta_depth': None, 'date': '01/03/2023', 'unit_system': UnitSystem.ENGLISH},),
    ('''NODECON
  NAME    NODEIN        NODEOUT       TYPE      METHOD    IPVT  ELEVPR   MDIN     MDOUT DIAM  ROUGHNESS    HTC  TEMPPR    TEMPIN  TEMPOUT
  CP01   dccfr1        pseudo_prd_1  PIPE      HAG_BEG     NA  R0302E04 NA        NA   9.500    0.0476  8.000  prtempr    100.3     300
  prd_2   pseudo_prd_1  pseudo_prd_2  PIPE      HAG_BEG     NA  R0308E03 NA        NA   9.130    0.0018  8.000  prtempr   100     10.3
!prd_3   prd_3         prd_3         PIPE      HAG_BEG     NA  R0308E03 NA        NA   9.130    0.0018  8.000  prtempr    200     NA
  ENDNODECON''',
     {'name': 'CP01', 'node_in': 'dccfr1', 'node_out': 'pseudo_prd_1', 'con_type': 'PIPE', 'hyd_method': 'HAG_BEG',
      'elevation_profile': 'R0302E04', 'diameter': 9.500, 'roughness': 0.0476, 'heat_transfer_coeff': 8.000,
      'temperature_profile': 'prtempr', 'temperature_in': 100.3, 'temperature_out': 300, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'prd_2', 'node_in': 'pseudo_prd_1', 'node_out': 'pseudo_prd_2', 'con_type': 'PIPE',
      'hyd_method': 'HAG_BEG',
      'elevation_profile': 'R0308E03', 'diameter': 9.130, 'roughness': 0.0018, 'heat_transfer_coeff': 8.000,
      'temperature_profile': 'prtempr', 'temperature_in': 100, 'temperature_out': 10.3, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},),
    ('''NODECON
        NAME             NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
        CP01             CP01      wh_cp01       PIPEGRAD        2          7002.67
        another_pipegrad  X         CP01         PIPEGRAD      0.0        NA
        ENDNODECON
        ''',
     {'name': 'CP01', 'node_in': 'CP01', 'node_out': 'wh_cp01', 'con_type': 'PIPEGRAD', 'hyd_method': None,
      'delta_depth': 7002.67, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'another_pipegrad', 'node_in': 'X', 'node_out': 'CP01', 'con_type': 'PIPEGRAD', 'hyd_method': None,
      'delta_depth': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH}
     )

], ids=['basic', 'other_tables', 'time changes two tables', 'More Columns', 'pipegrad'])
def test_load_connections(mocker: MockerFixture, file_contents, connection1_props, connection2_props):
    # Arrange
    start_date = '01/01/2023'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    # set up objects from the dictionaries
    con1 = NexusNodeConnection(connection1_props, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    con2 = NexusNodeConnection(connection2_props, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [con1, con2]

    # add expected iso dates for the dataframe comparison
    connection1_props['iso_date'] = ISODateTime.convert_to_iso(date=connection1_props['date'],
                                                               date_format=DateFormat.DD_MM_YYYY)
    connection2_props['iso_date'] = ISODateTime.convert_to_iso(date=connection2_props['date'],
                                                               date_format=DateFormat.DD_MM_YYYY)

    # create the dataframe output
    expected_df = pd.DataFrame([connection1_props, connection2_props])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_cons = NexusNodeConnections(mock_nexus_network)
    # Act
    nexus_cons.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_cons.get_all()
    single_connection_result = nexus_cons.get_by_name('CP01')
    result_df = nexus_cons.get_df()
    # Assert
    assert result == expected_result
    assert single_connection_result == con1
    # check for correct float types
    if single_connection_result.depth is not None:
        assert single_connection_result.depth / 2 == 7002.67 / 2
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


@pytest.mark.parametrize('file_contents, well_connection_props1, well_connection_props2', [
    (''' TIME 02/10/2032
METRIC
WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  prod   PRODUCER   94     4039.3     ON        CELLGRAD
  inj   WATER      95     4039.3     OFF        CALC
  bad_data
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossflow': 'ON',
      'crossshut': 'CELLGRAD',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossflow': 'OFF', 'crossshut': 'CALC',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),

    # Pipegrad
    (''' TIME 02/10/2032
METRIC
WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT  METHOD   TYPE
  prod   PRODUCER   94     4039.3     ON        CELLGRAD     1       PIPE
  inj   WATER      95     4039.3     OFF        CALC         0.0     PIPEGRAD
  bad_data
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossflow': 'ON',
      'crossshut': 'CELLGRAD',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC, 'hyd_method': '1', 'con_type': 'PIPE'},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossflow': 'OFF', 'crossshut': 'CALC',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC, 'hyd_method': None, 'con_type': 'PIPEGRAD'},
     ),

    # Default Crossflow
    (''' TIME 02/10/2032
METRIC

CROSSFLOW ON

WELLS
  NAME    STREAM   NUMBER   DATUM 
  prod   PRODUCER   94     4039.3 
  inj   WATER      95     4039.3 
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossflow': 'ON',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossflow': 'ON',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),


    # Override Default Crossflow
    (''' TIME 02/10/2032
METRIC

CROSSFLOW ON

WELLS
  NAME    STREAM   NUMBER   DATUM CROSSFLOW
  prod   PRODUCER   94     4039.3 OFF
  inj   WATER      95     4039.3  OFF
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossflow': 'OFF',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossflow': 'OFF',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),

    # Default Shutin on
    (''' TIME 02/10/2032
METRIC

SHUTINON

WELLS
  NAME    STREAM   NUMBER   DATUM 
  prod   PRODUCER   94     4039.3 
  inj   WATER      95     4039.3 
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossshut': 'ON',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossshut': 'ON',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),

    # Default Shutin off
    (''' TIME 02/10/2032
METRIC

SHUTINOFF

WELLS
  NAME    STREAM   NUMBER   DATUM 
  prod   PRODUCER   94     4039.3 
  inj   WATER      95     4039.3 
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossshut': 'OFF',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossshut': 'OFF',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),

    # Default shutin Cellgrad
    (''' TIME 02/10/2032
METRIC

SHUTIN_CELLGRAD

WELLS
  NAME    STREAM   NUMBER   DATUM 
  prod   PRODUCER   94     4039.3 
  inj   WATER      95     4039.3 
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossshut': 'CELLGRAD',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossshut': 'CELLGRAD',
      'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),

    # Override default crossflow and shutin
    (''' TIME 02/10/2032
METRIC

CROSSFLOW OFF
SHUTINOFF

WELLS
  NAME    STREAM   NUMBER   DATUM CROSS_SHUT CROSSFLOW
  prod   PRODUCER   94     4039.3   CELLGRAD  OFF
  inj   WATER      95     4039.3  ON   ON
    ENDWELLS
''',
     {'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossshut': 'CELLGRAD',
      'crossflow': 'OFF', 'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     {'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossshut': 'ON',
      'crossflow': 'ON', 'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
     ),
], ids=['Normal', 'Pipegrad', 'Default Crossflow', 'Crossflow override', 'Default shutin on', 'Default shutin off',
        'Default shutin cellgrad', 'override both'])
def test_load_well_connections(mocker, file_contents, well_connection_props1, well_connection_props2, ):
    # Arrange
    start_date = '01/01/2023'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellcon1 = NexusWellConnection(well_connection_props1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellcon2 = NexusWellConnection(well_connection_props2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [wellcon1, wellcon2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_well_cons = NexusWellConnections(mock_nexus_network)

    well_connection_props1['iso_date'] = ISODateTime.convert_to_iso(date=well_connection_props1['date'],
                                                                    date_format=DateFormat.DD_MM_YYYY,
                                                                    start_date=start_date)
    well_connection_props2['iso_date'] = ISODateTime.convert_to_iso(date=well_connection_props2['date'],
                                                                    date_format=DateFormat.DD_MM_YYYY,
                                                                    start_date=start_date)

    expected_df = pd.DataFrame([well_connection_props1, well_connection_props2])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')

    # Act
    nexus_well_cons.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_well_cons.get_all()
    single_connection_result = nexus_well_cons.get_by_name('prod')
    result_df = nexus_well_cons.get_df()

    # Assert
    assert len(result) == 2
    assert result[0] == wellcon1
    assert result[1] == wellcon2
    assert result == expected_result
    assert single_connection_result == wellcon1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


def test_load_gaswell_connections(mocker):
    # Arrange
    file_contents = """ TIME 01/01/2019
METRIC

TIME 01/01/2020
WELLS
NAME     	STREAM    NUMBER  DATUM DATGRAD	CROSSFLOW CROSS_SHUT
P01	  	PRODUCER     1    14000 MOBGRAD	    OFF        OFF
P02	  	PRODUCER     2    14000 MOBGRAD	    OFF        OFF
I01     WATER       95    15000 MOBGRAD     OFF        CALC
ENDWELLS


GASWELLS
NAME 		D 		DPERF GASMOB
P01		1.123e-5	INVKH	CB
ENDGASWELLS

TIME 01/01/2021

GASWELLS
NAME 		D 		DPERF GASMOB
P02		2.345e-5	random	#
ENDGASWELLS

"""
    well_connection_props1 = {'name': 'P01', 'stream': 'PRODUCER', 'number': 1, 'datum_depth': 14000,
                              'gradient_calc': 'MOBGRAD', 'crossflow': 'OFF', 'crossshut': 'OFF',
                              'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    well_connection_props2 = {'name': 'P02', 'stream': 'PRODUCER', 'number': 2, 'datum_depth': 14000,
                              'gradient_calc': 'MOBGRAD', 'crossflow': 'OFF', 'crossshut': 'OFF',
                              'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    well_connection_props3 = {'name': 'I01', 'stream': 'WATER', 'number': 95, 'datum_depth': 15000,
                              'gradient_calc': 'MOBGRAD', 'crossflow': 'OFF', 'crossshut': 'CALC',
                              'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    well_connection_props4 = {'name': 'P01', 'd_factor': 1.123e-5, 'non_darcy_flow_method': 'INVKH',
                              'gas_mobility': 'CB', 'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    well_connection_props5 = {'name': 'P02', 'd_factor': 2.345e-5, 'non_darcy_flow_method': 'random',
                              'gas_mobility': None, 'date': '01/01/2021', 'unit_system': UnitSystem.METRIC}
    start_date = '01/01/2019'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellcon1 = NexusWellConnection(well_connection_props1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellcon2 = NexusWellConnection(well_connection_props2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellcon3 = NexusWellConnection(well_connection_props3, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellcon4 = NexusWellConnection(well_connection_props4, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellcon5 = NexusWellConnection(well_connection_props5, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [wellcon1, wellcon2, wellcon3, wellcon4, wellcon5]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_well_cons = NexusWellConnections(mock_nexus_network)

    # Act
    nexus_well_cons.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_well_cons.get_all()

    # Assert
    assert result == expected_result


def test_load_sim_wells_well_type(mocker):
    """Checks that we retrieve the well type from the surface files correctly."""

    # Arrange
    surface_file_contents = """TIME 02/10/2032
METRIC
WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  well_prod_1   PRODUCER   94     4039.3     ON        CELLGRAD
  well_inj_wat   WATER      95     4039.3     OFF        CALC
  well_inj_oil      OIL 389 20339 ON CALC
    well_inj_gas      GAS 389 20339 ON CALC
        well_prod_other      OTHER_VALUE 389 20339 ON CALC
    ENDWELLS    
"""

    wellspec_file_contents = """
    TIME 02/10/2032
WELLSPEC well_prod_1
    IW JW L RADW
    1  2  3  4.5  
    
WELLSPEC well_inj_wat
      IW JW L RADW
    5 6 7 8
    
WELLSPEC well_inj_oil
IW JW L RADW
9 10 11 12.1

WELLSPEC well_prod_2
IW JW L RADW
13 14 15 16

WELLSPEC well_inj_gas
IW JW L RADW
13 14 15 16

WELLSPEC well_prod_other
IW JW L RADW
13 14 15 16
"""

    wellspec_2_contents = """TIME 02/10/2035
WELLSPEC well_inj_wat
      IW JW L RADW
    5 6 7 10
"""
    fcs_file_contents = """
DATEFORMAT DD/MM/YYYY    
RECURRENT_FILES
	 WELLS Set 1        wells.dat
	 WELLS Set 2     wells_2.dat
	 SURFACE Network 1  surface.dat
	 RUNCONTROL runcontrol.dat
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'model.fcs': fcs_file_contents,
            'wells.dat': wellspec_file_contents,
            'wells_2.dat': wellspec_2_contents,
            'surface.dat': surface_file_contents,
            'runcontrol.dat': 'START 01/01/2018'
        }).return_value
        return mock_open

    start_date = '01/01/2018'
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)

    parent_wells_instance = NexusWells(model=model)
    model._wells = parent_wells_instance

    expected_completion_1 = NexusCompletion(date='02/10/2032', i=1, j=2, k=3, well_radius=4.5,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_well_1 = NexusWell(well_name='well_prod_1', completions=[expected_completion_1],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.PRODUCER, parent_wells_instance=parent_wells_instance)
    expected_completion_2_1 = NexusCompletion(date='02/10/2032', i=5, j=6, k=7, well_radius=8.0,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_completion_2_2 = NexusCompletion(date='02/10/2035', i=5, j=6, k=7, well_radius=10.0,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_well_2 = NexusWell(well_name='well_inj_wat', completions=[expected_completion_2_1, expected_completion_2_2],
                                unit_system=UnitSystem.ENGLISH, well_type=WellType.WATER_INJECTOR, 
                                parent_wells_instance=parent_wells_instance)
    expected_completion_3 = NexusCompletion(date='02/10/2032', i=9, j=10, k=11, well_radius=12.1,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_well_3 = NexusWell(well_name='well_inj_oil', completions=[expected_completion_3],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.OIL_INJECTOR, parent_wells_instance=parent_wells_instance)
    expected_completion_4 = NexusCompletion(date='02/10/2032', i=13, j=14, k=15, well_radius=16.0,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_well_4 = NexusWell(well_name='well_prod_2', completions=[expected_completion_4],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.PRODUCER, parent_wells_instance=parent_wells_instance)
    expected_well_5 = NexusWell(well_name='well_inj_gas', completions=[expected_completion_4],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.GAS_INJECTOR, parent_wells_instance=parent_wells_instance)
    expected_well_6 = NexusWell(well_name='well_prod_other', completions=[expected_completion_4],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.PRODUCER, parent_wells_instance=parent_wells_instance)

    expected_wells = [expected_well_1, expected_well_2, expected_well_3, expected_well_4, expected_well_5,
                      expected_well_6]

    # Act
    result = model.wells.wells

    # Assert
    assert result[1].well_type == WellType.WATER_INJECTOR
    assert result == expected_wells


@pytest.mark.parametrize('file_contents, wellhead_props_1, wellhead_props_2', [
    (''' TIME 01/03/2019
WELLHEAD
WELL NAME DEPTH TYPE METHOD
!ru	TH-ru	100	PIPE 	3	
R001	tubing	50.2	PIPE 	2	!ENDWELLHEAD
R-0_02	TH-03	0	PIPE 	1! comment
	ENDWELLHEAD''',
     {'well': 'R001', 'name': 'tubing', 'depth': 50.2, 'wellhead_type': 'PIPE', 'hyd_method': 2, 'date': '01/03/2019',
      'unit_system': UnitSystem.ENGLISH},
     {'well': 'R-0_02', 'name': 'TH-03', 'depth': 0, 'wellhead_type': 'PIPE', 'hyd_method': 1, 'date': '01/03/2019',
      'unit_system': UnitSystem.ENGLISH},)

])
def test_load_wellhead(mocker, file_contents, wellhead_props_1, wellhead_props_2):
    # Arrange
    start_date = '01/01/2018'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellhead1 = NexusWellhead(wellhead_props_1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellhead2 = NexusWellhead(wellhead_props_2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [wellhead1, wellhead2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_wellheads = NexusWellheads(mock_nexus_network)

    # add expected iso dates for the dataframe comparison
    wellhead_props_1['iso_date'] = ISODateTime.convert_to_iso(date=wellhead_props_1['date'],
                                                              date_format=DateFormat.DD_MM_YYYY)
    wellhead_props_2['iso_date'] = ISODateTime.convert_to_iso(date=wellhead_props_2['date'],
                                                              date_format=DateFormat.DD_MM_YYYY)

    expected_df = pd.DataFrame([wellhead_props_1, wellhead_props_2])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')

    # Act
    nexus_wellheads.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_wellheads.get_all()
    single_wellhead = nexus_wellheads.get_by_name('tubing')
    result_df = nexus_wellheads.get_df()

    # Assert
    assert result == expected_result
    assert single_wellhead == wellhead1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


@pytest.mark.parametrize('file_contents, wellboreprops1, wellboreprops2', [
    (''' TIME 01/03/2019
WELLBORE
WELL METHOD DIAM TYPE
well1 BEGGS 3.5 PIPE
ENDWELLBORE
WELLBORE
WELL METHOD DIAM FLOWSECT ROUGHNESS
well2 BRILL 3.25 2      0.2002
ENDWELLBORE
	''',
     {'name': 'well1', 'bore_type': 'PIPE', 'hyd_method': "BEGGS", 'diameter': 3.5, 'date': '01/03/2019',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'well2', 'hyd_method': "BRILL", 'diameter': 3.25, 'flowsect': 2, 'roughness': 0.2002,
      'date': '01/03/2019', 'unit_system': UnitSystem.ENGLISH},)
])
def test_load_wellbore(mocker, file_contents, wellboreprops1, wellboreprops2):
    # Arrange
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellbore2 = NexusWellbore(wellboreprops2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexuswellbore = NexusWellbores(mock_nexus_network)

    # add expected iso dates for the dataframe comparison
    wellboreprops1['iso_date'] = ISODateTime.convert_to_iso(date=wellboreprops1['date'],
                                                            date_format=DateFormat.DD_MM_YYYY)
    wellboreprops2['iso_date'] = ISODateTime.convert_to_iso(date=wellboreprops2['date'],
                                                            date_format=DateFormat.DD_MM_YYYY)

    expected_df = pd.DataFrame([wellboreprops1, wellboreprops2])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')

    # Act
    nexuswellbore.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexuswellbore.get_all()
    single_wellbore = nexuswellbore.get_by_name('well1')
    result_df = nexuswellbore.get_df()

    # Assert
    assert result == expected_result
    assert single_wellbore == wellbore1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


@pytest.mark.parametrize('file_contents, wellboreprops1, wellboreprops2', [
    (''' TIME 01/03/2019
TIME PLUS 4
WELLBORE
WELL METHOD DIAM TYPE
well1 BEGGS 3.5 PIPE
ENDWELLBORE
WELLBORE
WELL METHOD DIAM FLOWSECT ROUGHNESS
well2 BRILL 3.25 2      0.2002
ENDWELLBORE
    ''',
     {'name': 'well1', 'bore_type': 'PIPE', 'hyd_method': "BEGGS", 'diameter': 3.5, 'date': '05/03/2019',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'well2', 'hyd_method': "BRILL", 'diameter': 3.25, 'flowsect': 2, 'roughness': 0.2002,
      'date': '05/03/2019', 'unit_system': UnitSystem.ENGLISH},),
    (''' TIME 25/08/2019
TIME PLUS 2.9
WELLBORE
WELL METHOD DIAM TYPE
well1 BEGGS 3.5 PIPE
ENDWELLBORE
WELLBORE
WELL METHOD DIAM FLOWSECT ROUGHNESS
well2 BRILL 3.25 2      0.2002
ENDWELLBORE
    ''',
     {'name': 'well1', 'bore_type': 'PIPE', 'hyd_method': "BEGGS", 'diameter': 3.5, 'date': '27/08/2019(21:36:00)',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'well2', 'hyd_method': "BRILL", 'diameter': 3.25, 'flowsect': 2, 'roughness': 0.2002,
      'date': '27/08/2019(21:36:00)', 'unit_system': UnitSystem.ENGLISH},)
])
def test_load_wellbore_time_plus(mocker, file_contents, wellboreprops1, wellboreprops2):
    # Arrange
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellbore2 = NexusWellbore(wellboreprops2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexuswellbore = NexusWellbores(mock_nexus_network)

    # add expected iso dates for the dataframe comparison
    wellboreprops1['iso_date'] = ISODateTime.convert_to_iso(date=wellboreprops1['date'],
                                                            date_format=DateFormat.DD_MM_YYYY)
    wellboreprops2['iso_date'] = ISODateTime.convert_to_iso(date=wellboreprops2['date'],
                                                            date_format=DateFormat.DD_MM_YYYY)

    expected_df = pd.DataFrame([wellboreprops1, wellboreprops2])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')

    # Act
    nexuswellbore.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexuswellbore.get_all()
    single_wellbore = nexuswellbore.get_by_name('well1')
    result_df = nexuswellbore.get_df()

    # Assert
    assert result == expected_result
    assert single_wellbore == wellbore1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


@pytest.mark.parametrize('file_contents, wellboreprops1, wellboreprops2', [
    (''' TIME 12/28/2019
TIME PLUS 6
WELLBORE
WELL METHOD DIAM TYPE
well1 BEGGS 3.5 PIPE
ENDWELLBORE
WELLBORE
WELL METHOD DIAM FLOWSECT ROUGHNESS
well2 BRILL 3.25 2      0.2002
ENDWELLBORE
    ''',
     {'name': 'well1', 'bore_type': 'PIPE', 'hyd_method': "BEGGS", 'diameter': 3.5, 'date': '01/03/2020',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'well2', 'hyd_method': "BRILL", 'diameter': 3.25, 'flowsect': 2, 'roughness': 0.2002,
      'date': '01/03/2020', 'unit_system': UnitSystem.ENGLISH},),
    (''' TIME 05/11/2019
TIME PLUS 1.1
WELLBORE
WELL METHOD DIAM TYPE
well1 BEGGS 3.5 PIPE
ENDWELLBORE
WELLBORE
WELL METHOD DIAM FLOWSECT ROUGHNESS
well2 BRILL 3.25 2      0.2002
ENDWELLBORE
    ''',
     {'name': 'well1', 'bore_type': 'PIPE', 'hyd_method': "BEGGS", 'diameter': 3.5, 'date': '05/12/2019(02:24:00)',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'well2', 'hyd_method': "BRILL", 'diameter': 3.25, 'flowsect': 2, 'roughness': 0.2002,
      'date': '05/12/2019(02:24:00)', 'unit_system': UnitSystem.ENGLISH},)
])
def test_load_wellbore_time_plus_mmddyy(mocker, file_contents, wellboreprops1, wellboreprops2):
    # Arrange
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    wellbore2 = NexusWellbore(wellboreprops2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.MM_DD_YYYY
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexuswellbore = NexusWellbores(mock_nexus_network)

    # add expected iso dates for the dataframe comparison
    wellboreprops1['iso_date'] = ISODateTime.convert_to_iso(date=wellboreprops1['date'],
                                                            date_format=DateFormat.MM_DD_YYYY)
    wellboreprops2['iso_date'] = ISODateTime.convert_to_iso(date=wellboreprops2['date'],
                                                            date_format=DateFormat.MM_DD_YYYY)

    expected_df = pd.DataFrame([wellboreprops1, wellboreprops2])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')

    # Act
    nexuswellbore.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexuswellbore.get_all()
    single_wellbore = nexuswellbore.get_by_name('well1')
    result_df = nexuswellbore.get_df()

    # Assert
    assert result == expected_result
    assert single_wellbore == wellbore1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


def test_wells_table_expands_out_wildcards(mocker: MockerFixture):
    """Checks that wildcard names in a WELLS table apply the property to all names that match the wildcard."""

    # Arrange
    wellspec_file_contents = """
        TIME 12/06/2024
    WELLSPEC well_aa
        IW JW L RADW
        1  2  3  4.5  

    WELLSPEC well_ab
          IW JW L RADW
        5 6 7 8

    WELLSPEC well_c
    IW JW L RADW
    9 10 11 12.1
    """

    surface_file_contents = """TIME 12/06/2024
    WELLS
        NAME      STREAM      DATUM
        well_aa   PRODUCER    1234
        well_ab   PRODUCER    5678
        well_c    PRODUCER    9123
    ENDWELLS
    
    NODECON
    NAME	 	NODEIN		NODEOUT  	TYPE METHOD   LENGTH
    well_bc     well_bc    OTH_3R       PIPE 4  NA
    ENDNODECON
    
    TIME 09/07/2024
        WELLS
        NAME      STREAM      DATUM
        well_dd  PRODUCER    1234
    ENDWELLS
    WELLS
      NAME    ONTIME
      wel*_a* 0.85
    ENDWELLS
    
    TIME 14/07/2024
    
    WELLS
      NAME    DATUM
      well_* 4321
    ENDWELLS     
    """

    fcs_file_contents = """
    DATEFORMAT DD/MM/YYYY    
    RECURRENT_FILES
    	 WELLS Set 1        wells.dat
    	 SURFACE Network 1  surface.dat
    	 RUNCONTROL runcontrol.dat
    """

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'model.fcs': fcs_file_contents,
            'wells.dat': wellspec_file_contents,
            'surface.dat': surface_file_contents,
            'runcontrol.dat': 'START 01/01/2018 DATEFORMAT DD/MM/YYYY'
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)

    parent_wells_instance = NexusWells(model=model)
    model._wells = parent_wells_instance

    # Act
    result = model.network.well_connections.well_connections

    # Assert
    connections_for_12th_june = [x for x in result if x.date == '12/06/2024']

    connections_for_aa_june = [x for x in connections_for_12th_june if x.name == 'well_aa']
    assert connections_for_aa_june[0].on_time is None
    assert connections_for_aa_june[0].datum_depth == 1234

    connections_for_ab_june = [x for x in connections_for_12th_june if x.name == 'well_ab']
    assert connections_for_ab_june[0].on_time is None
    assert connections_for_ab_june[0].datum_depth == 5678

    connections_for_c_june = [x for x in connections_for_12th_june if x.name == 'well_c']
    assert connections_for_c_june[0].on_time is None
    assert connections_for_c_june[0].datum_depth == 9123

    connections_on_9th_july = [x for x in result if x.date == '09/07/2024']
    assert len(connections_on_9th_july) == 3

    connections_for_aa_july = [x for x in connections_on_9th_july if x.name == 'well_aa']
    assert connections_for_aa_july[0].on_time == 0.85

    connections_for_ab_july = [x for x in connections_on_9th_july if x.name == 'well_ab']
    assert connections_for_ab_july[0].on_time == 0.85

    connections_on_14th_july = [x for x in result if x.date == '14/07/2024']
    assert len(connections_on_14th_july) == 4

    connections_for_aa_14th_july = [x for x in connections_on_14th_july if x.name == 'well_aa']
    assert connections_for_aa_14th_july[0].datum_depth == 4321

    connections_for_ab_14th_july = [x for x in connections_on_14th_july if x.name == 'well_ab']
    assert connections_for_ab_14th_july[0].datum_depth == 4321

    connections_for_c_14th_july = [x for x in connections_on_14th_july if x.name == 'well_c']
    assert connections_for_c_14th_july[0].datum_depth == 4321


def test_load_surface_file_activate_deactivate(mocker):
    # Arrange
    # Mock out the surface and fcs file
    fcs_file_contents = 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc'

    surface_file_content = """
        TIME 01/02/2024
          WELLS
         NAME   STREAM DATUM 
         WELCON_1 PRODUCER 1234 
         welcon_2 PRODUCER 5678 
         welcon_1_2 PRODUCER 9.87
         gaswelcon_1 PRODUCER 1.234
         gaswelcon_2 PRODUCER 5.678
         ENDWELLS

         GASWELLS
        NAME 		D 		DPERF 
        gaswelcon_1		1.123e-5	INVKH
        gaswelcon_2		123.4	ABCD
        ENDGASWELLS

         NODECON
         NAME      NODEIN    NODEOUT    TYPE
         N1_n2     N1        N2         PIPE
         ENDNODECON

        DEACTIVATE
         CONNECTION
         welcon_1*
         gaswelcon_2
         !** test
         N1_N2
        ENDDEACTIVATE

        TIME 09/07/2024

        ACTIVATE
        CONNECTION
        welcon_1*
        ENDACTIVATE

        TIME 14/07/2024
        GASWELLS
        NAME 		D 
        gaswelcon_1		4321	
        gaswelcon_2		9876	
        ENDGASWELLS

        TIME 23/08/2024

        ACTIVATE
        CONNECTION
        gaswelcon_2
        N1_N2
        ENDACTIVATE

        DEACTIVATE
         CONNECTION
         gaswelcon_1
        ENDDEACTIVATE
    """

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            'nexus_data/surface.inc': surface_file_content,
            'run_control.inc': 'START 01/01/2023',
        }).return_value
        return mock_open

    start_date = '01/01/2023'
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    fcs_file_path = 'fcs_file.fcs'
    nexus_sim = NexusSimulator(fcs_file_path)
    welcon_props_1 = {'name': 'WELCON_1', 'stream': 'PRODUCER', 'datum_depth': 1234.0, 'date': '01/02/2024',
                      'unit_system': UnitSystem.ENGLISH}
    welcon_props_2 = {'name': 'welcon_2', 'stream': 'PRODUCER', 'datum_depth': 5678.0, 'date': '01/02/2024',
                      'unit_system': UnitSystem.ENGLISH}
    welcon_props_1_2_1 = {'name': 'welcon_1_2', 'stream': 'PRODUCER', 'datum_depth': 9.87, 'date': '01/02/2024',
                          'unit_system': UnitSystem.ENGLISH}

    original_gas_welcon_props_1 = {'name': 'gaswelcon_1', 'stream': 'PRODUCER', 'datum_depth': 1.234,
                                   'date': '01/02/2024',
                                   'unit_system': UnitSystem.ENGLISH}
    original_gas_welcon_props_2 = {'name': 'gaswelcon_2', 'stream': 'PRODUCER', 'datum_depth': 5.678,
                                   'date': '01/02/2024',
                                   'unit_system': UnitSystem.ENGLISH}

    gas_welcon_props_1 = {'name': 'gaswelcon_1', 'd_factor': 1.123e-5, 'non_darcy_flow_method': 'INVKH',
                          'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH}
    gas_welcon_props_2 = {'name': 'gaswelcon_2', 'd_factor': 123.4, 'non_darcy_flow_method': 'ABCD',
                          'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH}
    node_con_prop_n1_n2 = {'name': 'N1_n2', 'node_in': 'N1', 'node_out': 'N2', 'con_type': 'PIPE',
                           'date': '01/02/2024', 'unit_system': UnitSystem.ENGLISH}

    gas_welcon_props_3 = {'name': 'gaswelcon_1', 'date': '14/07/2024', 'unit_system': UnitSystem.ENGLISH,
                          'd_factor': 4321}
    gas_welcon_props_4 = {'name': 'gaswelcon_2', 'date': '14/07/2024', 'unit_system': UnitSystem.ENGLISH,
                          'd_factor': 9876, }

    welcon_1 = NexusWellConnection(welcon_props_1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    welcon_2 = NexusWellConnection(welcon_props_2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    welcon_1_2 = NexusWellConnection(welcon_props_1_2_1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)

    original_gas_welcon_1 = NexusWellConnection(original_gas_welcon_props_1, date_format=DateFormat.DD_MM_YYYY,
                                                start_date=start_date)
    original_gas_welcon_2 = NexusWellConnection(original_gas_welcon_props_2, date_format=DateFormat.DD_MM_YYYY,
                                                start_date=start_date)
    gas_welcon_1 = NexusWellConnection(gas_welcon_props_1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    gas_welcon_2 = NexusWellConnection(gas_welcon_props_2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    gas_welcon_3 = NexusWellConnection(gas_welcon_props_3, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    gas_welcon_4 = NexusWellConnection(gas_welcon_props_4, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    node_n1_n2 = NexusNodeConnection(node_con_prop_n1_n2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)

    activation_change_1 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE,
                                                date_format=DateFormat.DD_MM_YYYY,
                                                date='01/02/2024', name='WELCON_1', start_date='01/01/2023')
    activation_change_2 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE,
                                                date_format=DateFormat.DD_MM_YYYY,
                                                date='01/02/2024', name='welcon_1_2', start_date='01/01/2023')
    activation_change_3 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE,
                                                date_format=DateFormat.DD_MM_YYYY,
                                                date='01/02/2024', name='gaswelcon_2', start_date='01/01/2023')
    activation_change_4 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE,
                                                date_format=DateFormat.DD_MM_YYYY,
                                                date='01/02/2024', name='N1_N2', start_date='01/01/2023')

    activation_change_5 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, date_format=DateFormat.DD_MM_YYYY,
                                                date='09/07/2024', name='WELCON_1', start_date='01/01/2023')
    activation_change_6 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, date_format=DateFormat.DD_MM_YYYY,
                                                date='09/07/2024', name='welcon_1_2', start_date='01/01/2023')

    activation_change_7 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, date_format=DateFormat.DD_MM_YYYY,
                                                date='23/08/2024', name='gaswelcon_2', start_date='01/01/2023')
    activation_change_8 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, date_format=DateFormat.DD_MM_YYYY,
                                                date='23/08/2024', name='N1_N2', start_date='01/01/2023')

    activation_change_9 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE,
                                                date_format=DateFormat.DD_MM_YYYY,
                                                date='23/08/2024', name='gaswelcon_1', start_date='01/01/2023')

    # Create the expected objects
    expected_wellcons = [welcon_1, welcon_2, welcon_1_2, original_gas_welcon_1, original_gas_welcon_2, gas_welcon_1,
                         gas_welcon_2, gas_welcon_3, gas_welcon_4]
    expected_node_cons = [node_n1_n2]
    expected_activation_changes = [activation_change_1, activation_change_2, activation_change_3, activation_change_4,
                                   activation_change_5, activation_change_6, activation_change_7, activation_change_8,
                                   activation_change_9]

    # Act
    result_wellcons = nexus_sim.network.well_connections.get_all()
    result_nodecons = nexus_sim.network.connections.get_all()
    result_activation_changes = nexus_sim.network.activation_changes.get_all()

    # Assert
    assert sorted(result_activation_changes, key=lambda x: (x.iso_date)) == expected_activation_changes
    assert result_wellcons[0] == welcon_1
    assert sorted(result_wellcons, key=lambda x: (x.iso_date)) == expected_wellcons
    assert sorted(result_nodecons, key=lambda x: (x.iso_date)) == expected_node_cons


def test_load_surface_file_activate_deactivate_basic(mocker):
    # Arrange
    # Mock out the surface and fcs file
    fcs_file_contents = 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc'

    surface_file_content = """
        WELLS
 NAME     	STREAM    NUMBER  DATUM 	CROSSFLOW CROSS_SHUT  
 well1	  	PRODUCER    1       123.4    OFF        OFF
ENDWELLS

TIME 09/07/2024
CONSTRAINTS
    well1	 QOSMAX 	5432
ENDCONSTRAINTS

TIME 23/08/2024
DEACTIVATE
    CONNECTION
    well1
ENDDEACTIVATE

TIME 10/09/2024
ACTIVATE
    CONNECTION
    well1
ENDACTIVATE
    """

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            'nexus_data/surface.inc': surface_file_content,
            'run_control.inc': 'START 01/01/2023',
        }).return_value
        return mock_open

    start_date = '01/01/2023'
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    fcs_file_path = 'fcs_file.fcs'
    nexus_sim = NexusSimulator(fcs_file_path)

    # Create the expected objects
    welcon_0 = NexusWellConnection(date_format=DateFormat.DD_MM_YYYY,
                                   start_date=start_date, date='01/01/2023', name='well1', datum_depth=123.4,
                                   crossflow='OFF', crossshut='OFF', number=1, stream='PRODUCER')

    expected_wellcons = [welcon_0]
    activation_change_1 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE, name='well1', date='23/08/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    activation_change_2 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, name='well1', date='10/09/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_activation_changes = [activation_change_1, activation_change_2]

    # Act
    result_wellcons = nexus_sim.network.well_connections.get_all()
    result_activation_changes = nexus_sim.network.activation_changes.get_all()

    # Assert
    assert result_wellcons == expected_wellcons
    assert result_activation_changes == expected_activation_changes


def test_load_surface_file_activate_deactivate_constraints_as_well(mocker):
    # Arrange
    # Mock out the surface and fcs file
    fcs_file_contents = 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc'

    surface_file_content = """
        WELLS
 NAME     	STREAM    NUMBER  DATUM 	CROSSFLOW CROSS_SHUT  
 well1	  	PRODUCER    1       123.4    OFF        OFF
ENDWELLS

TIME 09/07/2024
CONSTRAINTS
    well1	 QOSMAX 	5432
ENDCONSTRAINTS

TIME 23/08/2024
ACTIVATE
    CONNECTION
    well1
ENDACTIVATE

TIME 10/09/2024
CONSTRAINTS
well1 DEACTIVATE
ENDCONSTRAINTS

TIME 15/01/2025
ACTIVATE
    CONNECTION
    well1
ENDACTIVATE
    """

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            'nexus_data/surface.inc': surface_file_content,
            'run_control.inc': 'START 01/01/2023',
        }).return_value
        return mock_open

    start_date = '01/01/2023'
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    fcs_file_path = 'fcs_file.fcs'
    nexus_sim = NexusSimulator(fcs_file_path)

    # Create the expected objects
    welcon_0 = NexusWellConnection(date_format=DateFormat.DD_MM_YYYY,
                                   start_date=start_date, date='01/01/2023', name='well1', datum_depth=123.4,
                                   crossflow='OFF', crossshut='OFF', number=1, stream='PRODUCER')

    expected_wellcons = [welcon_0]
    activation_change_1 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, name='well1', date='23/08/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    activation_change_2 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE, name='well1', date='10/09/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date,
                                                is_constraint_change=True)
    activation_change_3 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, name='well1', date='15/01/2025',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_activation_changes = [activation_change_1, activation_change_2, activation_change_3]

    # Act
    result_wellcons = nexus_sim.network.well_connections.get_all()
    result_activation_changes = sorted(nexus_sim.network.activation_changes.get_all(), key=lambda x: x.iso_date)

    # Assert
    assert result_wellcons == expected_wellcons
    assert result_activation_changes == expected_activation_changes

def test_load_surface_file_activate_deactivate_multiple_on_same_line(mocker):
    # Arrange
    # Mock out the surface and fcs file
    fcs_file_contents = 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc'

    surface_file_content = """
        WELLS
 NAME     	STREAM    NUMBER  DATUM 	CROSSFLOW CROSS_SHUT  
 well1	  	PRODUCER    1       123.4    OFF        OFF
  Well2	  	PRODUCER    1       123.4    OFF        OFF
ENDWELLS

TIME 09/07/2024
CONSTRAINTS
    well1	 QOSMAX 	5432
ENDCONSTRAINTS

TIME 23/08/2024
DEACTIVATE
    CONNECTION
    well1 Well2
ENDDEACTIVATE

TIME 10/09/2024
ACTIVATE
    CONNECTION
    well1  ! comment
ENDACTIVATE
    """

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            'nexus_data/surface.inc': surface_file_content,
            'run_control.inc': 'START 01/01/2023',
        }).return_value
        return mock_open

    start_date = '01/01/2023'
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    fcs_file_path = 'fcs_file.fcs'
    nexus_sim = NexusSimulator(fcs_file_path)

    # Create the expected objects
    welcon_0 = NexusWellConnection(date_format=DateFormat.DD_MM_YYYY,
                                   start_date=start_date, date='01/01/2023', name='well1', datum_depth=123.4,
                                   crossflow='OFF', crossshut='OFF', number=1, stream='PRODUCER')
    welcon_1 = NexusWellConnection(date_format=DateFormat.DD_MM_YYYY,
                                   start_date=start_date, date='01/01/2023', name='Well2', datum_depth=123.4,
                                   crossflow='OFF', crossshut='OFF', number=1, stream='PRODUCER')

    expected_wellcons = [welcon_0, welcon_1]

    activation_change_1 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE, name='well1', date='23/08/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    activation_change_2 = NexusActivationChange(change=ActivationChangeEnum.DEACTIVATE, name='Well2', date='23/08/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    activation_change_3 = NexusActivationChange(change=ActivationChangeEnum.ACTIVATE, name='well1', date='10/09/2024',
                                                date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_activation_changes = [activation_change_1, activation_change_2, activation_change_3]

    # Act
    result_wellcons = nexus_sim.network.well_connections.get_all()
    result_activation_changes = nexus_sim.network.activation_changes.get_all()

    # Assert
    assert result_wellcons == expected_wellcons
    assert result_activation_changes == expected_activation_changes


def test_load_between_procs(mocker):
    fcs_file_contents = 'RUNCONTROL run_control.inc\nDATEFORMAT DD/MM/YYYY\nSURFACE NETWORK 1 	nexus_data/surface.inc'
    surface_file_content = '''TIME 01/01/2023
    
PROCS NAME TUNING
REAL_1D     list
REAL  t_last = 0
IF (t_last == 0 THEN
t_last = TIME
ENDIF
ENDPROCS
    
    NODECON
    	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
    	CP01            CP01      wh_cp01       PIPE        2          7002.67
    	cp01_gaslift    GAS       CP01          GASLIFT     NONE        NA ! Checked NODECON 13/05/2020 
    	ENDNODECON
    	'''
    expected_nodecons = [NexusNodeConnection(name='CP01', node_in='CP01', node_out='wh_cp01', con_type='PIPE',
                                             hyd_method='2', delta_depth=7002.67, date='01/01/2023',
                                             unit_system=UnitSystem.ENGLISH, properties_dict={}, 
                                             date_format=DateFormat.DD_MM_YYYY, start_date='01/01/2023'),
                         NexusNodeConnection(name='cp01_gaslift', node_in='GAS', node_out='CP01', con_type='GASLIFT',
                                             hyd_method=None, delta_depth=None, date='01/01/2023',
                                             unit_system=UnitSystem.ENGLISH, properties_dict={},
                                             date_format=DateFormat.DD_MM_YYYY, start_date='01/01/2023')]
    
    expected_proc = NexusProc(date='01/01/2023', name='TUNING', 
                              contents=['REAL_1D     list\n', 'REAL  t_last = 0\n', 'IF (t_last == 0 THEN\n', 
                                        't_last = TIME\n', 'ENDIF\n'],)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            'nexus_data/surface.inc': surface_file_content,
            'run_control.inc': 'START 01/01/2023',
        }).return_value
        return mock_open

    start_date = '01/01/2023'
    mocker.patch("builtins.open", mock_open_wrapper)

    fcs_file_path = 'fcs_file.fcs'
    nexus_sim = NexusSimulator(fcs_file_path)

    # Act
    result_nodecons = nexus_sim.network.connections.get_all()
    result_procs = nexus_sim.network.procs.get_all()[0]

    # Assert
    assert result_nodecons == expected_nodecons
    assert result_procs.contents == expected_proc.contents
    assert result_procs.date == expected_proc.date
    assert result_procs.name == expected_proc.name
