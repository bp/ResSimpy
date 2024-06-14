import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from ResSimpy.Enums.WellTypeEnum import WellType
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
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    node_1 = NexusNode(properties_dict=node1_props, date_format=DateFormat.MM_DD_YYYY)
    node_2 = NexusNode(properties_dict=node2_props, date_format=DateFormat.MM_DD_YYYY)

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

    expected_df = pd.DataFrame([node1_props, node2_props])
    expected_df = expected_df.fillna(value=np.nan).dropna(axis=1, how='all')
    # Act
    result = nexus_nodes.get_df()

    # Assert
    pd.testing.assert_frame_equal(result, expected_df, )


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

], ids=['basic', 'other_tables', 'time changes two tables', 'More Columns'])
def test_load_connections(mocker: MockerFixture, file_contents, connection1_props, connection2_props):
    # Arrange
    start_date = '01/01/2023'
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    # set up objects from the dictionaries
    con1 = NexusNodeConnection(connection1_props, date_format=DateFormat.DD_MM_YYYY)
    con2 = NexusNodeConnection(connection2_props, date_format=DateFormat.DD_MM_YYYY)
    expected_result = [con1, con2]
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
    pd.testing.assert_frame_equal(result_df, expected_df, )


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
     )
])
def test_load_well_connections(mocker, file_contents, well_connection_props1, well_connection_props2, ):
    # Arrange
    start_date = '01/01/2023'
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellcon1 = NexusWellConnection(well_connection_props1, date_format=DateFormat.DD_MM_YYYY)
    wellcon2 = NexusWellConnection(well_connection_props2, date_format=DateFormat.DD_MM_YYYY)
    expected_result = [wellcon1, wellcon2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
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
P01		1.123e-5	INVKH	#
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
                              'gas_mobility': None, 'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    well_connection_props5 = {'name': 'P02', 'd_factor': 2.345e-5, 'non_darcy_flow_method': 'random',
                              'gas_mobility': None, 'date': '01/01/2021', 'unit_system': UnitSystem.METRIC}
    start_date = '01/01/2019'
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellcon1 = NexusWellConnection(well_connection_props1, date_format=DateFormat.DD_MM_YYYY)
    wellcon2 = NexusWellConnection(well_connection_props2, date_format=DateFormat.DD_MM_YYYY)
    wellcon3 = NexusWellConnection(well_connection_props3, date_format=DateFormat.DD_MM_YYYY)
    wellcon4 = NexusWellConnection(well_connection_props4, date_format=DateFormat.DD_MM_YYYY)
    wellcon5 = NexusWellConnection(well_connection_props5, date_format=DateFormat.DD_MM_YYYY)
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
            'runcontrol.dat': 'START 01/01/2018'
        }).return_value
        return mock_open

    start_date = '01/01/2018'
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)

    parent_wells_instance = NexusWells(model=model)
    model._wells = parent_wells_instance

    expected_completion_1 = NexusCompletion(date='02/10/2032', i=1, j=2, k=3, well_radius=4.5,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_well_1 = NexusWell(well_name='well_prod_1', completions=[expected_completion_1],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.PRODUCER, parent_wells_instance=parent_wells_instance)
    expected_completion_2 = NexusCompletion(date='02/10/2032', i=5, j=6, k=7, well_radius=8.0,
                                            date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                            start_date=start_date)
    expected_well_2 = NexusWell(well_name='well_inj_wat', completions=[expected_completion_2],
                                unit_system=UnitSystem.ENGLISH,
                                well_type=WellType.WATER_INJECTOR, parent_wells_instance=parent_wells_instance)
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
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellhead1 = NexusWellhead(wellhead_props_1, date_format=DateFormat.DD_MM_YYYY)
    wellhead2 = NexusWellhead(wellhead_props_2, date_format=DateFormat.DD_MM_YYYY)
    expected_result = [wellhead1, wellhead2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
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
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1, date_format=DateFormat.DD_MM_YYYY)
    wellbore2 = NexusWellbore(wellboreprops2, date_format=DateFormat.DD_MM_YYYY)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
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
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1, date_format=DateFormat.DD_MM_YYYY)
    wellbore2 = NexusWellbore(wellboreprops2, date_format=DateFormat.DD_MM_YYYY)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.DD_MM_YYYY
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
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
    start_date = '01/01/2018'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    wellbore1 = NexusWellbore(wellboreprops1, date_format=DateFormat.MM_DD_YYYY)
    wellbore2 = NexusWellbore(wellboreprops2, date_format=DateFormat.MM_DD_YYYY)
    expected_result = [wellbore1, wellbore2]
    mock_nexus_network = mocker.MagicMock()
    mock_nexus_network.model.date_format = DateFormat.MM_DD_YYYY
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
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')

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
    assert len(connections_on_9th_july) == 2

    connections_for_aa_july = [x for x in connections_on_9th_july if x.name == 'well_aa']
    assert connections_for_aa_july[0].on_time == 0.85

    connections_for_ab_july = [x for x in connections_on_9th_july if x.name == 'well_ab']
    assert connections_for_ab_july[0].on_time == 0.85

    connections_on_14th_july = [x for x in result if x.date == '14/07/2024']
    assert len(connections_on_14th_july) == 3

    connections_for_aa_14th_july = [x for x in connections_on_14th_july if x.name == 'well_aa']
    assert connections_for_aa_14th_july[0].datum_depth == 4321

    connections_for_ab_14th_july = [x for x in connections_on_14th_july if x.name == 'well_ab']
    assert connections_for_ab_14th_july[0].datum_depth == 4321

    connections_for_c_14th_july = [x for x in connections_on_14th_july if x.name == 'well_c']
    assert connections_for_c_14th_july[0].datum_depth == 4321
