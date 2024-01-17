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
    well_file_content = '''TIME 01/01/2020
        WELLSPEC test_well
        ! RADW radw
        JW iw l radw
        2  1  3  4.5
        7 6 8   9.11
        '''
    expected_completion_1 = NexusCompletion(date=start_date, i=1, j=2, k=3, well_radius=4.5,
                                            date_format=date_format, unit_system=unit_system)
    expected_completion_2 = NexusCompletion(date=start_date, i=6, j=7, k=8, well_radius=9.11,
                                            date_format=date_format,
                                            unit_system=unit_system)

    @pytest.mark.parametrize('wellfile_content, expected_wellmod_dict', [
        # simple_wellmod
        ('''WELLMOD test_well PPERF	CON	0.25''',
        {'well_name': 'test_well', 'date': '01/01/2020', 'unit_system': UnitSystem.ENGLISH, 'partial_perf': 0.25}),

        # wellmod_with_different_date
        ("""TIME 01/01/2021
        TIME 01/01/2023
        WELLMOD test_well KHMULT CON 0.4 RADW CON 4.102""",
         {'well_name': 'test_well', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH, 'perm_thickness_mult': 0.4,
          'well_radius': 4.102}),
    ], ids=['simple_wellmod', 'wellmod_with_different_date', ])
    def test_load_nexus_wellmod(self, mocker, wellfile_content, expected_wellmod_dict):
        # Arrange
        wellfile_content = self.well_file_content + wellfile_content
        expected_wellmods = [NexusWellMod(expected_wellmod_dict)]

        expected_wells = [NexusWell(well_name='test_well',
                                    completions=[self.expected_completion_1, self.expected_completion_2],
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

    def test_load_nexus_wellmod_multiple_wells(self, mocker):
        # Arrange
        extra_content = """WELLSPEC test_well_2
        JW iw l radw
        1  1  1  4.5
        2 2 2 5.5
        WEllMOd test_well_2    SKIN	CON	0.25 !!! WI CON 2
        WELLMod test_well   KHMULT    CON 1234.2
        TIME 01/01/2021
        WELLMOD test_well_2 PPERF	CON	0.25
        """
        well_file_content = self.well_file_content + extra_content
        expected_wellmod_1 = NexusWellMod({'well_name': 'test_well_2', 'date': '01/01/2020',
                                                'unit_system': self.unit_system, 'skin': 0.25})
        expected_wellmod_2 = NexusWellMod({'well_name': 'test_well', 'date': '01/01/2020',
                                             'unit_system': self.unit_system, 'perm_thickness_mult': 1234.2})
        expected_wellmod_3 = NexusWellMod({'well_name': 'test_well_2', 'date': '01/01/2021',
                                                'unit_system': self.unit_system, 'partial_perf': 0.25})

        expected_completion_test_well_2_1 = NexusCompletion(date=self.start_date, i=1, j=1, k=1, skin=None,
                                                            well_radius=4.5, date_format=self.date_format,
                                                            unit_system=self.unit_system)
        expected_completion_test_well_2_2 = NexusCompletion(date=self.start_date, i=2, j=2, k=2,
                                                            skin=None, well_radius=5.5,
                                                            date_format=self.date_format, unit_system=self.unit_system)

        expected_well_1 = NexusWell(well_name='test_well',
                                    completions=[self.expected_completion_1, self.expected_completion_2],
                                    wellmods=[expected_wellmod_2],
                                    unit_system=self.unit_system)
        expected_well_2 = NexusWell(well_name='test_well_2',
                                    completions=[expected_completion_test_well_2_1, expected_completion_test_well_2_2],
                                    wellmods=[expected_wellmod_1, expected_wellmod_3],
                                    unit_system=self.unit_system)
        expected_wells = [expected_well_1, expected_well_2]

        open_mock = mocker.mock_open(read_data=well_file_content)
        mocker.patch("builtins.open", open_mock)
        wells_file = NexusFile.generate_file_include_structure('test_well_file.dat')

        # Act
        result_wells = load_wells(wells_file, start_date=self.start_date, model_date_format=self.date_format,
                                  default_units=self.unit_system)[0]

        # Assert
        assert result_wells == expected_wells

    def test_load_wellmod_var(self, mocker):
        # Arrange
        extra_well_file_content = "WELLMod test_well SKIN VAR 1.2  55  KHMULT    CON 1234.2  DKRW  VAr 10 2 "
        expected_wellmod = NexusWellMod({'well_name': 'test_well', 'date': '01/01/2020',
                                         'unit_system': self.unit_system, 'skin': [1.2, 55],
                                         'perm_thickness_mult': 1234.2, 'delta_krw': [10, 2]})
        expected_wells = [NexusWell(well_name='test_well',
                                    completions=[self.expected_completion_1, self.expected_completion_2],
                                    wellmods=[expected_wellmod],
                                    unit_system=self.unit_system)]
        open_mock = mocker.mock_open(read_data=self.well_file_content + extra_well_file_content)
        mocker.patch("builtins.open", open_mock)

        wells_file = NexusFile.generate_file_include_structure('test_well_file.dat')

        # Act
        result_wells = load_wells(wells_file, start_date=self.start_date, model_date_format=self.date_format,
                                  default_units=self.unit_system)[0]
        # Assert
        assert result_wells == expected_wells

    def test_load_wellmod_var_multiple_dates(self, mocker):
        # Arrange
        extra_well_file_content = """
        TIME 01/01/2021
        WELLSPEC test_well
        JW iw l radw
        1  1  1  4.5
        1  1  2  4.6
        1  1  3  4.7
        TIME 01/01/2022
        WELLSPEC test_well2
        JW iw l skin
        2 2 3 4
        WELLMod test_well SKIN VAR 1.2  55  66  KHMULT    CON 1234.2  DKRW  VAr 10 2 3
        TIME 01/01/2023
        WELLSPEC test_well
        JW iw l radw
        1  1  1  4.5
        WELLMOD test_well SKIN VAR 0.5 KHMULT    CON 1234.2  DKRW  VAr 1.1
        WELLMOD test_well2 SKIN CON 2
        """
        expected_wellmod_1 = NexusWellMod({'well_name': 'test_well', 'date': '01/01/2022',
                                           'unit_system': self.unit_system, 'skin': [1.2, 55, 66],
                                           'perm_thickness_mult': 1234.2, 'delta_krw': [10, 2, 3]})
        expected_wellmod_2 = NexusWellMod({'well_name': 'test_well', 'date': '01/01/2023',
                                             'unit_system': self.unit_system, 'skin': [0.5],
                                             'perm_thickness_mult': 1234.2, 'delta_krw': [1.1]})

        extra_expected_completion_1 = NexusCompletion(date='01/01/2021', i=1, j=1, k=1, well_radius=4.5,
                                                      date_format=self.date_format, unit_system=self.unit_system)
        extra_expected_completion_2 = NexusCompletion(date='01/01/2021', i=1, j=1, k=2, well_radius=4.6,
                                                      date_format=self.date_format, unit_system=self.unit_system)
        extra_expected_completion_3 = NexusCompletion(date='01/01/2021', i=1, j=1, k=3, well_radius=4.7,
                                                        date_format=self.date_format, unit_system=self.unit_system)
        extra_expected_completion_4 = NexusCompletion(date='01/01/2023', i=1, j=1, k=1, well_radius=4.5,
                                                      date_format=self.date_format, unit_system=self.unit_system)

        expected_wells = [NexusWell(well_name='test_well',
                                    completions=[self.expected_completion_1, self.expected_completion_2,
                                                 extra_expected_completion_1, extra_expected_completion_2,
                                                 extra_expected_completion_3, extra_expected_completion_4],
                                    wellmods=[expected_wellmod_1, expected_wellmod_2],
                                    unit_system=self.unit_system),
                          NexusWell(well_name='test_well2',
                                    completions=[NexusCompletion(date='01/01/2022', i=2, j=2, k=3, skin=4,
                                                                 date_format=self.date_format,
                                                                 unit_system=self.unit_system)],
                                    wellmods=[NexusWellMod({'well_name': 'test_well2', 'date': '01/01/2023',
                                                            'unit_system': self.unit_system, 'skin': 2})],
                                    unit_system=self.unit_system)]
        open_mock = mocker.mock_open(read_data=self.well_file_content + extra_well_file_content)
        mocker.patch("builtins.open", open_mock)

        wells_file = NexusFile.generate_file_include_structure('test_well_file.dat')

        # Act
        result_wells = load_wells(wells_file, start_date=self.start_date, model_date_format=self.date_format,
                                  default_units=self.unit_system)[0]
        # Assert
        assert result_wells == expected_wells
