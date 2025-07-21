from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusTarget import NexusTarget
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_model_file_generator import NexusModelFileGenerator
from utility_for_tests import get_fake_nexus_simulator


def test_write_surface_section(mocker):
    # Arrange
    model = get_fake_nexus_simulator(mocker)
    start_date = '01/01/2019'
    model_file_generator = NexusModelFileGenerator(model=model, model_name='new_path.fcs')
    well_connection_props1 = {'name': 'P01', 'stream': 'PRODUCER', 'number': 1, 'datum_depth': 14000,
                              'gradient_calc': 'MOBGRAD', 'crossflow': 'OFF', 'crossshut': 'OFF',
                              'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    well_connection_props2 = {'name': 'P02', 'stream': 'PRODUCER', 'number': 2, 'datum_depth': 14000,
                              'gradient_calc': 'MOBGRAD', 'crossflow': 'OFF', 'crossshut': 'OFF',
                              'date': '01/01/2020', 'unit_system': UnitSystem.METRIC}
    wellcon1 = NexusWellConnection(well_connection_props1, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    wellcon2 = NexusWellConnection(well_connection_props2, date_format=DateFormat.DD_MM_YYYY, start_date=start_date)

    # add some constraints

    constraints = {'P01': [NexusConstraint(name='P01', max_surface_oil_rate=1000.23, max_pressure=234.223,
                                           date='01/01/2020', unit_system=UnitSystem.METRIC)],
                   'P02': [NexusConstraint(name='P02', max_surface_oil_rate=1500.45, max_pressure=300.123,
                                           date='01/01/2020', unit_system=UnitSystem.METRIC),
                           NexusConstraint(name='P02', max_surface_oil_rate=2000.67, max_pressure=400.456,
                                           date='01/01/2021', unit_system=UnitSystem.METRIC)]}
    
    model.network._has_been_loaded = True
    model.network.well_connections._add_to_memory([wellcon1, wellcon2])
    model.network.constraints._add_to_memory(constraints)
    model.network.nodes._add_to_memory([
        NexusNode(name='NODE1', date='01/01/2020', unit_system=UnitSystem.METRIC, type='test', 
                  date_format=DateFormat.DD_MM_YYYY),
        NexusNode(name='NODE2', date='01/01/2020', unit_system=UnitSystem.METRIC, type='WELLHEAD', depth=2052.2,
                  date_format=DateFormat.DD_MM_YYYY),
    ])

    model.network.connections._add_to_memory([
        NexusNodeConnection(name='Nodecon_test', node_in='NODE1', node_out='NODE2', date='01/01/2020',
                            unit_system=UnitSystem.METRIC, hyd_method=23, date_format=DateFormat.DD_MM_YYYY)
    ])
    
    model.network.welllists._add_to_memory([
        NexusWellList(name='welllist1', date='01/01/2021', elements_in_the_list=['P01', 'P02'], 
                      date_format=DateFormat.DD_MM_YYYY)
    ])
    model.network.targets._add_to_memory([
        NexusTarget(name='TARGET1', date='01/01/2021', unit_system=UnitSystem.METRIC,
                    date_format=DateFormat.DD_MM_YYYY, control_quantity='control1', value=2592.3, 
                    control_connections='welllist1', control_conditions='SURFACE')
    ])


    expected_result = """TIME 01/01/2020
WELLS
NAME STREAM NUMBER DATUM DATGRAD CROSS_SHUT CROSSFLOW
P01 PRODUCER 1 14000 MOBGRAD OFF OFF
P02 PRODUCER 2 14000 MOBGRAD OFF OFF
ENDWELLS

NODES
NAME TYPE DEPTH
NODE1 test NA
NODE2 WELLHEAD 2052.2
ENDNODES

NODECON
NAME NODEIN NODEOUT METHOD
Nodecon_test NODE1 NODE2 23
ENDNODECON

CONSTRAINTS
P01 PMAX 234.223 QOSMAX 1000.23
P02 PMAX 300.123 QOSMAX 1500.45
ENDCONSTRAINTS

TIME 01/01/2021
WELLLIST welllist1
CLEAR
ADD
P01 P02
ENDWELLLIST

CONSTRAINTS
P02 PMAX 400.456 QOSMAX 2000.67
ENDCONSTRAINTS

TARGET
NAME CTRL CTRLCOND CTRLCONS VALUE
TARGET1 control1 SURFACE welllist1 2592.3
ENDTARGET

"""

    # Act
    result = model_file_generator.output_surface_section()

    # Assert
    assert result == expected_result
