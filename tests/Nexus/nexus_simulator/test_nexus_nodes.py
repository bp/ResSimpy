import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Surface.NexusNode import NexusNode
from ResSimpy.Nexus.Surface.load_nodes import load_nodes

def test_load_single_node():

@pytest.mark.parametrize('file_contents',[
('''WELLHEAD
WELL NAME DEPTH TYPE METHOD
R001	TH-R001	0	PIPE 	2
'''),
(
'''WELLHEAD
WELL NAME DEPTH TYPE METHOD
!RU415	TH-RU415	0	PIPE 	3	
R001	TH-R001	0	PIPE 	2	
R002	TH-R002	0	PIPE 	1	
R003	TH-R003	0	PIPE 	1	
ENDWELLHEAD
R005 TH-R005 0 PIPE 5'''),

],
ids=['basic', 'reaching endwellhead']

)
def test_load_nodes(mocker, file_contents):
    # Arrange
    # mock out a surface file:
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    node_1 = NexusNode(name='R001', )

    expected_result = []

    # Act

    result = load_nodes(surface_file)
    # Assert
    assert result == expected_result

