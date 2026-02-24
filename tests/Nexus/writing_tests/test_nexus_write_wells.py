from ResSimpy import NexusSimulator
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWellMod import NexusWellMod
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_model_file_generator import NexusModelFileGenerator


def test_wellmod_to_string():
    # Arrange
    wellmod = NexusWellMod({'well_name': 'test_well', 'date': '01/01/2020',
                                         'unit_system': UnitSystem.ENGLISH, 'skin': [1, 1.5, 1.5],
                                         'perm_thickness_mult': 1234.2, 'delta_krw': [3, 3, 10.4]},
                                                            start_date='01/01/2019', date='01/01/2020',
                                                            date_format=DateFormat.DD_MM_YYYY)
    expected_output = """WELLMOD test_well
SKIN VAR 1 1.5 1.5
DKRW VAR 3 3 10.4
KHMULT CON 1234.2
"""
    # Act
    result = wellmod.to_string()
    # Assert
    assert result == expected_output

def test_write_wells_section():
    # Arrange
    start_date = '01/01/2019'
    model = NexusSimulator(origin='test_file', assume_loaded=True, start_date=start_date, 
                           date_format=DateFormat.DD_MM_YYYY, run_units=UnitSystem.METRIC, 
                           default_units=UnitSystem.METRIC)

    model_file_generator = NexusModelFileGenerator(model=model, model_name='new_path.fcs')
    model.wells._wells_loaded = True
    
    # Add some wells
    completions_to_add = [NexusCompletion(i= 1, j=2, k=3, well_radius=0.4, date='01/01/2019'),
                            NexusCompletion(i=4, j=5, k=6, well_radius=0.5, date='01/01/2019'),
                            NexusCompletion(i=7, j=8, k=9, well_radius=0.6, date='01/01/2020'),
                            NexusCompletion(i=10, j=11, k=12, well_radius=0.7, skin=2, date='01/01/2020')]
    
    wellmods_to_add = [NexusWellMod({'well_name': 'well1', 'date': '01/01/2020',
                                     'unit_system': model.default_units, 'skin': [1, 1.5, 1.5],
                                     'perm_thickness_mult': 1234.2, 'delta_krw': [3, 3, 10.4]},
                                    start_date=start_date, date='01/01/2020', date_format=model.date_format),
                       NexusWellMod({'well_name': 'well1', 'date': '01/01/2021',
                                     'unit_system': model.default_units, 'perm_thickness_mult': 0.0, 'skin': 25 },
                                    start_date=start_date, date='01/01/2021', date_format=model.date_format)]
    
    model.wells.add_well(name='well1', units=model.default_units, completions=completions_to_add,
                         add_to_file=False, wellmods=wellmods_to_add)
    
    completions_second_well = [NexusCompletion(i=11, j=22, k=33, well_radius=0.44, date='01/01/2019'),
                               NexusCompletion(i=44, j=55, k=66, well_radius=0.55, date='01/01/2019'),
                               NexusCompletion(i=77, j=88, k=99, well_radius=0.66, date='01/01/2021'),
                               NexusCompletion(i=100, j=111, k=122, well_radius=0.77, skin=2, date='01/01/2021')]
    
    model.wells.add_well(name='well2', units=model.default_units, completions=completions_second_well,
                         add_to_file=False)
    
    expected_output = """WELLSPEC well1
IW JW L RADW
1 2 3 0.4
4 5 6 0.5

WELLSPEC well2
IW JW L RADW
11 22 33 0.44
44 55 66 0.55

TIME 01/01/2020
WELLSPEC well1
IW JW L SKIN RADW
7 8 9 NA 0.6
10 11 12 2 0.7
WELLMOD well1
SKIN VAR 1 1.5 1.5
DKRW VAR 3 3 10.4
KHMULT CON 1234.2

TIME 01/01/2021
WELLMOD well1
SKIN CON 25
KHMULT CON 0.0

WELLSPEC well2
IW JW L SKIN RADW
77 88 99 NA 0.66
100 111 122 2 0.77

"""
    # Act
    result = model_file_generator.output_wells_section()
    # Assert
    assert result == expected_output
