from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusWellMod import NexusWellMod
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.load_wells import load_wells
import pytest

class TestNexusWellMod:
    start_date = '01/01/2020'
    date_format = DateFormat.DD_MM_YYYY
    unit_system = UnitSystem.ENGLISH

    @pytest.mark.parametrize('wellfile_content, expected_wellmod_dict', [
        # simple_wellmod
        ('''TIME 01/01/2020
        WELLSPEC test_well
        JW IW L RADW
        2  1  3  4.5
        7 6 8   9.11
        WELLMOD test_well PPERF	CON	0.25''',
        {'well_name': 'test_well', 'date': '01/01/2020', 'unit_system': UnitSystem.ENGLISH, 'partial_perf': 0.25}),

        # wellmod_with_different_date
        ("""WELLSPEC test_well
        ! RADW radw
        JW iw l radw
        2  1  3  4.5
        7 6 8   9.11
        TIME 01/01/2021
        TIME 01/01/2023
        WELLMOD test_well KHMULT CON 0.4 RADW CON 4.102""",
         {'well_name': 'test_well', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH, 'perm_thickness_mult': 0.4,
          'well_radius': 4.102}),
    ], ids=['simple_wellmod', 'wellmod_with_different_date', ])
    def test_load_nexus_wellmod(self, mocker, wellfile_content, expected_wellmod_dict):
        # Arrange
        expected_wellmods = [NexusWellMod(expected_wellmod_dict)]

        expected_completion_1 = NexusCompletion(date=self.start_date, i=1, j=2, k=3, skin=None, well_radius=4.5,
                                                angle_v=None,
                                                grid=None, date_format=self.date_format, unit_system=self.unit_system)
        expected_completion_2 = NexusCompletion(date=self.start_date, i=6, j=7, k=8, well_radius=9.11,
                                                date_format=self.date_format,
                                                unit_system=self.unit_system)
        expected_wells = [NexusWell(well_name='test_well',
                                    completions=[expected_completion_1, expected_completion_2],
                                    wellmods=expected_wellmods,
                                    unit_system=self.unit_system)]
        open_mock = mocker.mock_open(read_data=wellfile_content)
        mocker.patch("builtins.open", open_mock)
        wells_file = NexusFile.generate_file_include_structure('test_well_file.dat')

        # Act
        result_wells = load_wells(wells_file, start_date=self.start_date, model_date_format=self.date_format,
                                  default_units=self.unit_system)[0]
        # Assert
        assert result_wells == expected_wells

