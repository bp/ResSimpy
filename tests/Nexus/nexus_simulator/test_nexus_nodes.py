import numpy as np
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
from ResSimpy.Nexus.NexusNetwork import NexusNetwork


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
],
ids=['basic', 'all columns', 'times', 'units']
)
def test_load_nexus_nodes(mocker, file_contents, node1_props, node2_props):
    # Arrange
    # mock out a surface file:
    start_date = '01/01/2023'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    node_1 = NexusNode(node1_props)
    node_2 = NexusNode(node2_props)

    expected_result = [node_1, node_2]
    # get the second node only
    second_node_name = node2_props['name']
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
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
