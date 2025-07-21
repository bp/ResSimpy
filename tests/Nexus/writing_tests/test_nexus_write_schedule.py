from ResSimpy import NexusSimulator
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
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
    model.network._has_been_loaded = True
    model.network.well_connections._add_to_memory([wellcon1, wellcon2])
    
    expected_result = """TIME 01/01/2020
WELLS
NAME STREAM NUMBER DATUM DATGRAD CROSS_SHUT CROSSFLOW
P01 PRODUCER 1 14000 MOBGRAD OFF OFF
P02 PRODUCER 2 14000 MOBGRAD OFF OFF
ENDWELLS

"""

    # Act
    result = model_file_generator.output_surface_section()
    
    # Assert
    assert result == expected_result
