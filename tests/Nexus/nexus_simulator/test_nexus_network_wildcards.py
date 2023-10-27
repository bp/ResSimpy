import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator

@pytest.mark.parametrize("file_contents, expected_constraints ", [
    # basic_test
    ('''TIME 01/01/2019
    WELLS
    NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
    well_prod   PRODUCER   94     4039.3     ON        CELLGRAD
    well_inj   WATER      95     4039.3     OFF        CALC
    ENDWELLS
    CONSTRAINTS
    well_*   QWSMAX 100
    ENDCONSTRAINTS''',
    [{'name': 'well_prod', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'unit_system': UnitSystem.ENGLISH},
    {'name': 'well_inj', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'unit_system': UnitSystem.ENGLISH}],
    ),

    # with extra nodes

    ('''TIME 01/01/2019
    WELLS
    NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
    well_prod   PRODUCER   94     4039.3     ON        CELLGRAD
    well_inj   WATER      95     4039.3     OFF        CALC
    dont_add_to_well PRODUCER 96 3000.2     OFF     CELlgrad
    ENDWELLS
    CONSTRAINTS
    well_*   QWSMAX 100
    ENDCONSTRAINTS''',
    [{'name': 'well_prod', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'unit_system': UnitSystem.ENGLISH},
    {'name': 'well_inj', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'unit_system': UnitSystem.ENGLISH}],
    ),

    # with extra constraints
    ('''TIME 01/01/2019
    WELLS
    NAME    STREAM   NUMBER   DATUM   CROSSFLOW   CROSS_SHUT
    well_prod   PRODUCER   94     4039.3     ON        CELLGRAD
    well_inj   WATER      95     4039.3     OFF        CALC
    dont_add_to_well PRODUCER 96 3000.2     OFF     CELlgrad
    ENDWELLS
    CONSTRAINTS
    well_*   QWSMAX 100
    well_prod   QOSMAX 102.2
    ENDCONSTRAINTS''',
    [{'name': 'well_prod', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'max_surface_oil_rate': 102.2,
      'unit_system': UnitSystem.ENGLISH},
    {'name': 'well_inj', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'unit_system': UnitSystem.ENGLISH}],
    ),

    # wildcard in the middle + case sensitivity
    ('''TIME 01/01/2019
    NODECON
	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
	CP01            CP01      wh_cp01       PIPE        2          2060.7
	cp01_gaslift    GAS       CP01          GASLIFT     NONE        NA ! Checked NODECON 13/05/2020
	CP-234          GAS       CP-234          GASLIFT     NONE        NA
	ENDNODECON
    CONSTRAINTS
    C*1  QWSMAX 100 QOSMAX 2.02
    ENDCONSTRAINTS''',
    [{'name': 'CP01', 'date': '01/01/2019', 'max_surface_water_rate': 100.0, 'max_surface_oil_rate': 2.02,
      'unit_system': UnitSystem.ENGLISH},
    ],
    ),

    # previous time card
    ('''TIME 01/01/2019
    NODECON
	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
    node_1            node_1      wh_node_1       PIPE        2          7334
    node_2            node_2      wh_node_2       PIPE        2          555
    well_1          well_1        wh_well_2     PIPE          2     23040.2
	ENDNODECON
	TIME 01/01/2020
    CONSTRAINTS
    node*  QWSMAX 100 QOSMAX 2.02
    ENDCONSTRAINTS
    TIME 01/02/2020
    NODECON
	NAME            NODEIN    NODEOUT       TYPE        METHOD    DDEPTH
    node_3            node_3      wh_node_3      PIPE        2          7334
	ENDNODECON

    CONSTRAINTS
    node* QWSMAX 200 QOSMAX 300
    ENDCONSTRAINTS
    ''',
    [{'name': 'node_1', 'date': '01/01/2020', 'max_surface_water_rate': 100.0, 'max_surface_oil_rate': 2.02,
      'unit_system': UnitSystem.ENGLISH},
    {'name': 'node_2', 'date': '01/01/2020', 'max_surface_water_rate': 100.0, 'max_surface_oil_rate': 2.02,
      'unit_system': UnitSystem.ENGLISH},

    {'name': 'node_1', 'date': '01/02/2020', 'max_surface_water_rate': 200.0, 'max_surface_oil_rate': 300.0,
      'unit_system': UnitSystem.ENGLISH},
    {'name': 'node_2', 'date': '01/02/2020', 'max_surface_water_rate': 200.0, 'max_surface_oil_rate': 300.0,
      'unit_system': UnitSystem.ENGLISH},
    {'name': 'node_3', 'date': '01/02/2020', 'max_surface_water_rate': 200.0, 'max_surface_oil_rate': 300.0,
      'unit_system': UnitSystem.ENGLISH},
    ],
    ),
    ], ids=['basic_test', 'with extra nodes', 'with extra constraints', 'wildcard in the middle + case sensitivity',
            'previous time card'])
def test_read_wildcard(mocker, file_contents, expected_constraints):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''

    # set up expected constraint dict
    expected_result = {}
    for constraint in expected_constraints:
        well_name = constraint['name']
        if expected_result.get(well_name, None) is not None:
            expected_result[well_name].append(NexusConstraint(constraint))
        else:
            expected_result[well_name] = [NexusConstraint(constraint)]

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
            ).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    # Act
    result = nexus_sim.network.constraints.get_all()
    # Assert
    assert result == expected_result

def test_add_remove_wildcard_well(mocker):
    # Arrange
    model = get_fake_nexus_simulator(mocker)
    parent_network = NexusNetwork(model)
    parent_network.__setattr__('_NexusNetwork__has_been_loaded', True)
    constraints = NexusConstraints(parent_network, model)
    constraint_props = {'name': 'P*', 'date': '01/01/2020', 'max_surface_oil_rate': 100.2}
    # Act Assert
    with pytest.raises(NotImplementedError) as error_msg:
        constraints.add(constraint_to_add=constraint_props)
    assert 'unsupported' in str(error_msg.value)

    with pytest.raises(NotImplementedError) as error_msg:
        constraints.remove(constraint_dict=constraint_props)
    assert 'unsupported' in str(error_msg.value)

