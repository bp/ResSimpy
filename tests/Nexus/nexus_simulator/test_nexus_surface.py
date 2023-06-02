import uuid
from unittest.mock import Mock
import numpy as np
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnections import NexusWellConnections
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellbores import NexusWellbores
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.Network.NexusWellheads import NexusWellheads
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.multifile_mocker import mock_multiple_files


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
],
ids=['basic', 'all columns', 'times', 'units', 'two tables']
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
    nexus_nodes.load_nodes(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_nodes.get_nodes()
    single_node_result = nexus_nodes.get_node(second_node_name)

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
    nexus_nodes.load_nodes(surface_file, start_date, default_units=UnitSystem.ENGLISH)

    expected_df = pd.DataFrame([node1_props, node2_props])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')
    # Act
    result = nexus_nodes.get_node_df()

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
  NAME    NODEIN        NODEOUT       TYPE      METHOD    IPVT  ELEVPR   MDIN     MDOUT DIAM  ROUGHNESS    HTC  TEMPPR
  CP01   dccfr1        pseudo_prd_1  PIPE      HAG_BEG     NA  R0302E04 NA        NA   9.500    0.0476  8.000  prtempr
  prd_2   pseudo_prd_1  pseudo_prd_2  PIPE      HAG_BEG     NA  R0308E03 NA        NA   9.130    0.0018  8.000  prtempr
!prd_3   prd_3         prd_3         PIPE      HAG_BEG     NA  R0308E03 NA        NA   9.130    0.0018  8.000  prtempr
  ENDNODECON''',
    {'name': 'CP01', 'node_in': 'dccfr1', 'node_out': 'pseudo_prd_1', 'con_type': 'PIPE', 'hyd_method': 'HAG_BEG',
    'elevation_profile': 'R0302E04','diameter': 9.500, 'roughness':0.0476, 'heat_transfer_coeff': 8.000,
    'temperature_profile': 'prtempr', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
    {'name': 'prd_2', 'node_in': 'pseudo_prd_1', 'node_out': 'pseudo_prd_2', 'con_type': 'PIPE', 'hyd_method': 'HAG_BEG',
    'elevation_profile': 'R0308E03', 'diameter': 9.130, 'roughness':0.0018, 'heat_transfer_coeff':8.000,
    'temperature_profile': 'prtempr', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},),

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
    nexus_cons.load_connections(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_cons.get_connections()
    single_connection_result = nexus_cons.get_connection('CP01')
    result_df = nexus_cons.get_connection_df()
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
{'name': 'prod', 'stream': 'PRODUCER', 'number': 94, 'datum_depth': 4039.3, 'crossflow': 'ON', 'crossshut_method': 'CELLGRAD',
'date': '02/10/2032', 'unit_system': UnitSystem.METRIC},
{'name': 'inj', 'stream': 'WATER', 'number': 95, 'datum_depth': 4039.3, 'crossflow': 'OFF', 'crossshut_method': 'CALC',
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
    nexus_well_cons.load_well_connections(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_well_cons.get_well_connections()
    single_connection_result = nexus_well_cons.get_well_connection('prod')
    result_df = nexus_well_cons.get_well_connections_df()

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
    nexus_wellheads.load_wellheads(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_wellheads.get_wellheads()
    single_wellhead = nexus_wellheads.get_wellhead('tubing')
    result_df = nexus_wellheads.get_wellheads_df()

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
    nexuswellbore.load_wellbores(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexuswellbore.get_wellbores()
    single_wellbore = nexuswellbore.get_wellbore('well1')
    result_df = nexuswellbore.get_wellbores_df()

    # Assert
    assert result == expected_result
    assert single_wellbore == wellbore1
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)


@pytest.mark.parametrize("file_contents, expected_content",[
    (''' CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    ''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH})),

    ('''CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    TIME 01/01/2020
    CONSTRAINTS
    well1	 QLIQSMAX 	5000
    well2	 QWSMAX 	0.0  QLIQSMAX 20.5
    ENDCONSTRAINTS''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2020', 'name': 'well1', 'max_surface_liquid_rate': 5000.0, 'max_surface_water_rate': 0, 'unit_system': UnitSystem.ENGLISH},
   {'date': '01/01/2020', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
   'max_surface_liquid_rate': 20.5, 'unit_system': UnitSystem.ENGLISH}
     )),

     ('''CONSTRAINTS
    well1	 QHCMAX- 	3884.0  PMIN 	0
    well2	 PMAX 	0.0  QLIQMIN 10000.0 QLIQMIN- 15.5 WORPLUGPLUS 85 CWLIM 155554
    ENDCONSTRAINTS''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_reverse_reservoir_hc_rate': 3884.0, 'min_pressure': 0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/01/2019', 'name': 'well2', 'max_pressure': 0, 'min_reservoir_liquid_rate': 10000.0,
    'min_reverse_reservoir_liquid_rate': 15.5, 'max_wor_plug_plus': 85, 'max_cum_water_prod': 155554,
    'unit_system': UnitSystem.ENGLISH})),

    ('''CONSTRAINT
    NAME    QLIQSMAX    QWSMAX 
    well1	  	3884.0   	0
    well2   0.0         10000
    ENDCONSTRAINT
    TIME 01/12/2023
    CONSTRAINTS
    well1	 QLIQSMAX 	1000.0
    ENDCONSTRAINTS
    ''', ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0.0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 0.0, 'max_surface_water_rate': 10000,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': 1000.0, 'max_surface_water_rate': 0.0,
            'unit_system': UnitSystem.ENGLISH},
    )),

    ('''CONSTRAINTS
    well1	 QLIQSMAX 	1000.0
    well1   pmin    1700
    well1   thp     2000    ! comment
    ENDCONSTRAINTS''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0, 'min_pressure': 1700.0,
    'tubing_head_pressure': 2000.0, 'unit_system': UnitSystem.ENGLISH},)
    ),

('''
    CONSTRAINTS
    well1	 QLIQSMAX 	1000.0    WORMAX 95
    ENDCONSTRAINTS
    TIME 01/12/2023
    CONSTRAINT
    NAME    QLIQSMAX    QWSMAX 
    well1	  	3884.0   	0
    well2   0.0         10000
    ENDCONSTRAINT
    
    ''', ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
            'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
    {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0.0,
    'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
    {'date': '01/12/2023', 'name': 'well2', 'max_surface_liquid_rate': 0.0, 'max_surface_water_rate': 10000,
    'unit_system': UnitSystem.ENGLISH},
    )),
(''' CONSTRAINTS
    well1	 QLIQSMAX 	MULT  QOSMAX 	MULT
    well2	 QALLRMAX 	0
    well3   QALLRMAX        MULT 
    ENDCONSTRAINTS
    QMULT
    WELL QOIL QGAS QWATER
    well1 121.0 53.6 2.5
    well2 211.0 102.4 35.7
    well3  10.2 123   203
    ENDQMULT
    ''',
    ({'date': '01/01/2019', 'name': 'well1', 'use_qmult_qoilqwat_surface_rate': True, 'use_qmult_qoil_surface_rate': True,
    'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 121.0, 'qmult_gas_rate': 53.6, 'qmult_water_rate': 2.5, 'well_name':'well1'},
     {'date': '01/01/2019', 'name': 'well2', 'max_qmult_total_reservoir_rate': 0.0, 'unit_system': UnitSystem.ENGLISH,
     'qmult_oil_rate': 211.0, 'qmult_gas_rate': 102.4, 'qmult_water_rate': 35.7, 'well_name':'well2'},
    {'date': '01/01/2019', 'name': 'well3', 'convert_qmult_to_reservoir_barrels': True,
    'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 10.2, 'qmult_gas_rate': 123, 'qmult_water_rate': 203, 'well_name':'well3'},
      )),
      ('''
    CONSTRAINTS
    well1	 QLIQSMAX 	1000.0    WORMAX 95
    well2  QLIQSMAX 1.8 PMAX    10000.2 QOSMAX MULT
    ENDCONSTRAINTS
    
    TIME 01/12/2023
    CONSTRAINTS
    well1 CLEARQ
    well2 CLEAR
    ENDCONSTRAINTS
    
    TIME 01/01/2024
    CONSTRAINTS
    well1  QOSMAX 1.8
    ENDCONSTRAINTS
    
    ''', ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
            'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 1.8, 'max_pressure': 10000.2,
        'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},
    {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': None, 'max_wor': 95.0,
        'unit_system': UnitSystem.ENGLISH},
    {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},
    {'date': '01/01/2024', 'name': 'well1', 'max_wor': 95.0, 'max_surface_oil_rate': 1.8,
        'unit_system': UnitSystem.ENGLISH},
    )),
    (''' 
        CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  ACTIVATE
    well2	 QWSMAX 	0.0  DEACTIVATE QLIQSMAX 15.5
    ENDCONSTRAINTS
    CONSTRAINTS
    ENDCONSTRAINTS
    WELLLIST RFTWELL
    CONSTRAINTS 
    well1 QLIQSMAX 0 DEACTIVATE
    ENDCONSTRAINTS
    ''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 0.0, 'active_node': False,
    'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'active_node': False,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
      )),
(''' 
          CONSTRAINTS
      well1	 DPBHAVG 1024.2  DPBHMX OFF  GORLIM NONE EXPONENT 9999
      ENDCONSTRAINTS
      ''',
      ({'date': '01/01/2019', 'name': 'well1', 'max_avg_comp_dp': 1024.2, 'gor_limit_exponent': 9999.0, 'unit_system': UnitSystem.ENGLISH},
        )),
    ], ids=['basic_test', 'Change in Time', 'more Keywords', 'constraint table', 'multiple constraints on same well',
    'inline before table', 'QMULT', 'Clearing Constraints', 'activate keyword', 'GORLIM_drawdowncards'])
def test_load_constraints(mocker, file_contents, expected_content):
    # Arrange
    start_date = '01/01/2019'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    expected_constraints = {}
    for constraint in expected_content:
        well_name = constraint['name']
        if expected_constraints.get(well_name, None) is not None:
            expected_constraints[well_name].append(NexusConstraint(constraint))
        else:
            expected_constraints[well_name] = [NexusConstraint(constraint)]
    expected_date_filtered_constraints = {}
    for constraint in expected_content:
        if constraint['date'] == '01/01/2019':
            well_name = constraint['name']
            if expected_date_filtered_constraints.get(well_name, None) is not None:
                expected_date_filtered_constraints[well_name].append(NexusConstraint(constraint))
            else:
                expected_date_filtered_constraints[well_name] = [NexusConstraint(constraint)]
    expected_single_name_constraint = {'well1': expected_constraints['well1']}
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    expected_df = pd.DataFrame(expected_content)
    # Act
    constraints = NexusConstraints(mock_nexus_network)
    constraints.load_constraints(surface_file, start_date, UnitSystem.ENGLISH)
    result = constraints.get_constraints()
    result_single = constraints.get_constraints(object_name='well1')
    result_df = constraints.get_constraint_df()
    result_date_filtered = constraints.get_constraints(date='01/01/2019')
    # sort the dates for comparing dataframes (order normally wouldn't matter)
    result_df['date'] = pd.to_datetime(result_df['date'])
    result_df = result_df.sort_values('date').reset_index(drop=True)

    expected_df['date'] = pd.to_datetime(expected_df['date'])
    expected_df = expected_df.sort_values('date').reset_index(drop=True)
    # Assert
    assert result == expected_constraints
    assert result_single == expected_single_name_constraint
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)
    assert result_date_filtered == expected_date_filtered_constraints

@pytest.mark.parametrize('file_contents, object_locations',[
        ('''CONSTRAINTS
        ! comment
            well1	 QLIQSMAX 	3884.0  QWSMAX 	0

            well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
        ''',
        {'uuid1': [2],
         'uuid2': [4]}
        ),

('''CONSTRAINTS
        ! comment
            well1	 QLIQSMAX 	3884.0  QWSMAX 	0

            well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    
    CONSTRAINTS
            ! comment
            well3	 QLIQSMAX 	3884.0  QWSMAX 	0

            well4	 QWSMAX 	0.0  QLIQSMAX- 10000.0
    ENDCONSTRAINTS
        ''',
        {'uuid1': [2],
         'uuid2': [4],
         'uuid3': [9],
         'uuid4': [11]}
        ),

('''CONSTRAINTS
        ! comment
            well1	 QLIQSMAX 	3884.0  QWSMAX 	0

            well1	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS

    CONSTRAINTS
            ! comment
            well1	 QOSMAX 	1234  QWSMAX 	0

            well1	 QWSMAX 	12334  QLIQSMAX- 10000.0
    ENDCONSTRAINTS
        ''',
        {'uuid1': [2, 4, 9, 11],
 }
        ),
        ], ids=['basic_test', 'two tables', 'several constraints for one well'])
def test_constraint_ids(mocker, file_contents, object_locations):
    # Arrange
    fcs_file_data = '''RUN_UNITS ENGLISH

    DATEFORMAT DD/MM/YYYY

    RECURRENT_FILES
    RUNCONTROL ref_runcontrol.dat
    SURFACE Network 1 surface.dat'''
    runcontrol_data = 'START 01/01/2020'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.dat': fcs_file_data,
            'surface.dat': file_contents,
            'ref_runcontrol.dat': runcontrol_data,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)
    model = NexusSimulator('fcs_file.dat')

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3',
                                                    'uuid4', 'uuid5', 'uuid6', 'uuid7'])
    # Act
    model.Network.Constraints.get_constraints()

    result = model.fcs_file.surface_files[1].object_locations
    # Assert
    assert result == object_locations
