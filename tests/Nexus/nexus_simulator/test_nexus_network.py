
import numpy as np
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnections import NexusWellConnections
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellbores import NexusWellbores
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.Network.NexusWellheads import NexusWellheads
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes


@pytest.mark.parametrize('file_contents, node1_props, node2_props',[
('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
{'name': 'node1', 'type': None, 'depth': None,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
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
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23, 'number': 2,
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
{'name': 'node1', 'type': None, 'depth': None,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
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
{'name': 'node1', 'type': None, 'depth': None,  'temp': None, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
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
{'name': 'test_node3', 'type': 'WELLHEAD', 'depth': 1167.3, 'x_pos': 100, 'y_pos': 100, 'date': '01/01/2025', 'unit_system': UnitSystem.ENGLISH},
)
],
ids=['basic', 'all columns', 'times', 'units', 'two tables', 'keyword in column']
)
def test_load_nexus_nodes(mocker, file_contents, node1_props, node2_props):
    # Arrange
    # mock out a surface file:
    start_date = '01/01/2023'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    node_1 = NexusNode(node1_props)
    node_2 = NexusNode(node2_props)

    mock_nexus_network = mocker.MagicMock()
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


@pytest.mark.parametrize('file_contents, node1_props, node2_props',[
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
{'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23, 'number': 2,
    'station': 'station2', 'date': '01/01/2023', 'unit_system': 'ENGLISH'}
  )],)
def test_get_node_df(mocker, file_contents, node1_props, node2_props):
    # Arrange
    start_date = '01/01/2023'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_nodes = NexusNodes(mock_nexus_network)
    nexus_nodes.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)

    expected_df = pd.DataFrame([node1_props, node2_props])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')
    # Act
    result = nexus_nodes.get_df()

    # Assert
    pd.testing.assert_frame_equal(result, expected_df,)

@pytest.mark.parametrize('file_contents, connection1_props, connection2_props',[
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
(	'''NODES
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
(	''' TIME 01/02/2023
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
    'elevation_profile': 'R0302E04','diameter': 9.500, 'roughness':0.0476, 'heat_transfer_coeff': 8.000,
    'temperature_profile': 'prtempr', 'temperature_in': 100.3, 'temperature_out': 300, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
    {'name': 'prd_2', 'node_in': 'pseudo_prd_1', 'node_out': 'pseudo_prd_2', 'con_type': 'PIPE', 'hyd_method': 'HAG_BEG',
    'elevation_profile': 'R0308E03', 'diameter': 9.130, 'roughness':0.0018, 'heat_transfer_coeff':8.000,
    'temperature_profile': 'prtempr', 'temperature_in': 100, 'temperature_out': 10.3, 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},),

	], ids=['basic', 'other_tables', 'time changes two tables', 'More Columns'])
def test_load_connections(mocker, file_contents, connection1_props, connection2_props):
    # Arrange
    start_date = '01/01/2023'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    # set up objects from the dictionaries
    con1 = NexusNodeConnection(connection1_props)
    con2 = NexusNodeConnection(connection2_props)
    expected_result = [con1, con2]
    # create the dataframe output
    expected_df = pd.DataFrame([connection1_props, connection2_props])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')
    mock_nexus_network = mocker.MagicMock()
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
    pd.testing.assert_frame_equal(result_df, expected_df,)

@pytest.mark.parametrize('file_contents, well_connection_props1, well_connection_props2',[
(''' TIME 02/10/2032
METRIC
WELLS
  NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
  prod   PRODUCER   94     4039.3     ON        CELLGRAD
  inj   WATER      95     4039.3     OFF        CALC
  bad_data
    ENDWELLS
''',
{'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossflow': 'ON', 'crossshut': 'CELLGRAD',
'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
{'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossflow': 'OFF', 'crossshut': 'CALC',
'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
)
])
def test_load_well_connections(mocker, file_contents, well_connection_props1, well_connection_props2,):
    # Arrange
    start_date = '01/01/2023'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellcon1 = NexusWellConnection(well_connection_props1)
    wellcon2 = NexusWellConnection(well_connection_props2)
    expected_result = [wellcon1, wellcon2]
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_well_cons = NexusWellConnections(mock_nexus_network)
    expected_df = pd.DataFrame([well_connection_props1, well_connection_props2])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')


    # Act
    nexus_well_cons.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_well_cons.get_all()
    single_connection_result = nexus_well_cons.get_by_name('prod')
    result_df = nexus_well_cons.get_df()

    # Assert
    assert result == expected_result
    assert single_connection_result == wellcon1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


@pytest.mark.parametrize('file_contents, wellhead_props_1, wellhead_props_2', [
(''' TIME 01/03/2019
WELLHEAD
WELL NAME DEPTH TYPE METHOD
!ru	TH-ru	100	PIPE 	3	
R001	tubing	50.2	PIPE 	2	!ENDWELLHEAD
R-0_02	TH-03	0	PIPE 	1! comment
	ENDWELLHEAD''',
{'well': 'R001', 'name': 'tubing', 'depth': 50.2, 'wellhead_type': 'PIPE', 'hyd_method': 2, 'date': '01/03/2019', 'unit_system': UnitSystem.ENGLISH},
{'well': 'R-0_02', 'name': 'TH-03', 'depth': 0, 'wellhead_type': 'PIPE', 'hyd_method': 1, 'date': '01/03/2019', 'unit_system': UnitSystem.ENGLISH},)

])
def test_load_wellhead(mocker, file_contents, wellhead_props_1, wellhead_props_2):
    # Arrange
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellhead1 = NexusWellhead(wellhead_props_1)
    wellhead2 = NexusWellhead(wellhead_props_2)
    expected_result = [wellhead1, wellhead2]
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexus_wellheads = NexusWellheads(mock_nexus_network)
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
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1)
    wellbore2 = NexusWellbore(wellboreprops2)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    nexuswellbore = NexusWellbores(mock_nexus_network)
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
