from ResSimpy import NexusSimulator
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_model_file_generator import NexusModelFileGenerator


def test_write_wells_section():
    # Arrange
    start_date = '01/01/2019'
    model = NexusSimulator(origin='test_file', assume_loaded=True, start_date=start_date, 
                           date_format=DateFormat.DD_MM_YYYY, run_units=UnitSystem.METRIC, 
                           default_units=UnitSystem.METRIC)

    model_file_generator = NexusModelFileGenerator(model=model, model_name='new_path.fcs')
    model.network._has_been_loaded = True
    model.wells._wells_loaded = True
    
    # Add some wells
    well1 = model.wells.add_completion()