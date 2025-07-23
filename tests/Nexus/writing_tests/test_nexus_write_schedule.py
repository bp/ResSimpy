import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Enums.FluidTypeEnums import PvtType
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusTarget import NexusTarget
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_model_file_generator import NexusModelFileGenerator
from tests.utility_for_tests import get_fake_nexus_simulator

@pytest.mark.parametrize('pvt_type, eos_details, expected_pvt_string', [
    (PvtType.BLACKOIL, None, 'BLACKOIL'),
    (PvtType.EOS, ['NHC', '3', 'COMPONENTS', 'C1', 'C2', 'C3'], 'EOS NHC 3 COMPONENTS C1 C2 C3'),])
def test_write_surface_section(pvt_type, eos_details, expected_pvt_string):
    # Arrange
    start_date = '01/01/2019'
    model = NexusSimulator(origin='test_file', assume_loaded=True, start_date=start_date, 
                           date_format=DateFormat.DD_MM_YYYY, run_units=UnitSystem.METRIC, 
                           default_units=UnitSystem.METRIC, pvt_type=pvt_type,
                           eos_details=eos_details)

    model_file_generator = NexusModelFileGenerator(model=model, model_name='new_path.fcs')
    model.network._has_been_loaded = True

    wellcon1 = NexusWellConnection(name='P01', stream='PRODUCER', number=1, datum_depth=14000,
                                   gradient_calc='MOBGRAD', crossflow='OFF', crossshut='OFF',
                                   date='01/01/2020', unit_system=UnitSystem.METRIC, date_format=DateFormat.DD_MM_YYYY,
                                   start_date=start_date)
    wellcon2 = NexusWellConnection(name='P02', stream='PRODUCER', number=2, datum_depth=14000,
                                   gradient_calc='MOBGRAD', crossflow='OFF', crossshut='OFF',
                                   date='01/01/2020', unit_system=UnitSystem.METRIC, 
                                   date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    # these should be combined to give 1 entry
    wellcon2_additional_wellcon = NexusWellConnection(name='P02', gas_mobility='GASMETHOD', non_darcy_flow_model='ND',
                                                      crossflow='ON',
                                                      date='01/01/2020', unit_system=UnitSystem.METRIC,
                                                      date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    model.network.well_connections._add_to_memory([wellcon1, wellcon2, wellcon2_additional_wellcon])

    # add some constraints
    constraints = {'P01': [NexusConstraint(name='P01', max_gor=100000, max_pressure=234.223,
                                           date='01/01/2019', unit_system=UnitSystem.METRIC),
                           NexusConstraint(name='P01', max_surface_oil_rate=1000.23, max_pressure=234.223,
                                           date='01/01/2020', unit_system=UnitSystem.METRIC)],
                   'P02': [NexusConstraint(name='P02', max_surface_oil_rate=1500.45, max_pressure=300.123,
                                           date='01/01/2020', unit_system=UnitSystem.METRIC),
                           NexusConstraint(name='P02', max_surface_oil_rate=2000.67, max_pressure=400.456,
                                           date='01/01/2021', unit_system=UnitSystem.METRIC)]}
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
    
    model.network.activation_changes._add_to_memory([
        NexusActivationChange(name='P01', date='01/01/2021', date_format=DateFormat.DD_MM_YYYY,
                              change=ActivationChangeEnum.ACTIVATE),
        NexusActivationChange(name='P02', date='15/10/2021', date_format=DateFormat.DD_MM_YYYY,
                              change=ActivationChangeEnum.DEACTIVATE),
        NexusActivationChange(name='P01', date='15/10/2021', date_format=DateFormat.DD_MM_YYYY,
                              change=ActivationChangeEnum.DEACTIVATE),
        
    ])


    expected_result = f"""{expected_pvt_string}

CONSTRAINTS
P01 GORMAX 100000 PMAX 234.223
ENDCONSTRAINTS

TIME 01/01/2020
WELLS
NAME STREAM NUMBER DATUM DATGRAD CROSS_SHUT CROSSFLOW ND GASMOB
P01 PRODUCER 1 14000 MOBGRAD OFF OFF NA NA
P02 PRODUCER 2 14000 MOBGRAD OFF ON ND GASMETHOD
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

ACTIVATE
CONNECTION
P01
ENDACTIVATE

TIME 15/10/2021
DEACTIVATE
CONNECTION
P02
P01
ENDDEACTIVATE

"""

    # Act
    result = model_file_generator.output_surface_section()

    # Assert
    assert result == expected_result
