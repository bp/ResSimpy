import pytest

from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod, NexusWaterParams
from ResSimpy.Nexus.NexusEnums.UnitsEnum import SUnits, UnitSystem, TemperatureUnits

@pytest.mark.parametrize("file_contents, expected_water_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! This is a comment
    DENW 62.4 CW 3.4 VISW 0.7 BW 1.04 PREF 3600 CVW 1e-3
    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                                      'and this is second line of description'],
            'TEMP': [None], 'SALINITY': [None],
            'DENW': [62.4], 'CW': [3.4], 'VISW': [0.7], 'CVW': [0.001], 'BW': [1.04], 'PREF': 3600}
      ),
      ("""
    DESC This is first line of description
    DESC and this is second line of description

    SUNITS PPM

    ! This is a comment
    SALINITY 100000
        DENW 62.4 CW 3.4 
        VISW 0.7 BW 1.04
        PREF 3600

    SALINITY 200000
        DENW 65.4 CW 4.4 
        VISW 0.8 BW 1.05 

    SALINITY 300000
        DENW 68.4 CW 5.4 
        VISW 0.9 BW 1.06 
    """, {'SUNITS': SUnits.PPM, 'DESC': ['This is first line of description',
                                         'and this is second line of description'],
            'TEMP': [None, None, None], 'SALINITY': [100000, 200000, 300000],
            'DENW': [62.4, 65.4, 68.4], 'CW': [3.4, 4.4, 5.4], 'CVW': [None, None, None],
            'VISW': [0.7, 0.8, 0.9], 'BW': [1.04, 1.05, 1.06], 'PREF': 3600}
      ),
      ("""
    DESC This is first line of description
    DESC and this is second line of description

    FAHR

    ! This is a comment
    TEMP 250
        DENW 62.4 CW 3.4 
        VISW 0.7 BW 1.04
        PREF 3600

    TEMP 260
        DENW 62.4 CW 4.4 
        VISW 0.8 BW 1.05 

    TEMP 270
        DENW 62.4 CW 5.4 
        VISW 0.9 BW 1.06 
    """, {'TEMP_UNIT': TemperatureUnits.FAHR, 'DESC': ['This is first line of description',
                                         'and this is second line of description'],
            'TEMP': [250, 260, 270], 'SALINITY': [None, None, None],
            'DENW': [62.4, 62.4, 62.4], 'CW': [3.4, 4.4, 5.4], 'CVW': [None, None, None],
            'VISW': [0.7, 0.8, 0.9], 'BW': [1.04, 1.05, 1.06], 'PREF': 3600}
      ),
      ("""
    DESC This is first line of description
    DESC and this is second line of description

    SUNITS PPM
    KELVIN

    ! This is a comment
    TEMP 394.3
        SALINITY 100000
            DENW 62.4 CW 3.4 
            VISW 0.7 BW 1.04
            PREF 3600

        SALINITY 200000
            DENW 65.4 CW 4.4 
            VISW 0.8 BW 1.05 

    TEMP 399.8
        SALINITY 100000
            DENW 62.4 CW 3.5 
            VISW 0.8 BW 1.05
            PREF 3600

        SALINITY 200000
            DENW 65.4 CW 4.5 
            VISW 0.9 BW 1.06
    """, {'SUNITS': SUnits.PPM, 
          'TEMP_UNIT': TemperatureUnits.KELVIN,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'TEMP': [394.3, 394.3, 399.8, 399.8], 'SALINITY': [100000, 200000, 100000, 200000],
          'DENW': [62.4, 65.4, 62.4, 65.4], 'CW': [3.4, 4.4, 3.5, 4.5], 'CVW': [None, None, None, None],
          'VISW': [0.7, 0.8, 0.8, 0.9], 'BW': [1.04, 1.05, 1.05, 1.06], 'PREF': 3600}
      ),
      ("""
    DESC This is first line of description
    DESC and this is second line of description

    SUNITS PPM
    KELVIN

    ! This is a comment
    TEMP 394.3
        SALINITY 100000
            DENW 62.4 CW 3.4 
            VISW 0.7 BW 1.04
            PREF 3600

        SALINITY 200000
            DENW 65.4 CW 4.4 
            VISW 0.8 BW 1.05 

    """, {'SUNITS': SUnits.PPM, 
          'TEMP_UNIT': TemperatureUnits.KELVIN,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'TEMP': [394.3, 394.3], 'SALINITY': [100000, 200000],
          'DENW': [62.4, 65.4], 'CW': [3.4, 4.4], 'CVW': [None, None],
          'VISW': [0.7, 0.8], 'BW': [1.04, 1.05], 'PREF': 3600}
      )
      ], ids=['basic water props', 'salinity_only', 'temp_only', 'temp_sal_case', 'one_temp_multi_sal']
)
def test_read_water_properties_from_file(mocker, file_contents, expected_water_properties):
    # Arrange
    wat_obj = NexusWaterMethod(file_path='test/file/water.dat', input_number=1)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    wat_obj.read_properties()
    props = wat_obj.properties
    params = wat_obj.parameters

    # Assert
    for key in ['UNIT_SYSTEM', 'SUNITS', 'TEMP_UNIT', 'DESC']:
        if key in expected_water_properties.keys():
            assert props[key] == expected_water_properties[key]
    assert wat_obj.reference_pressure == expected_water_properties['PREF']

    for i in range(len(expected_water_properties['TEMP'])):
        assert params[i].temperature == expected_water_properties['TEMP'][i]
        assert params[i].salinity == expected_water_properties['SALINITY'][i]
        assert params[i].density == expected_water_properties['DENW'][i]
        assert params[i].compressibility == expected_water_properties['CW'][i]
        assert params[i].viscosity_compressibility == expected_water_properties['CVW'][i]
        assert params[i].viscosity == expected_water_properties['VISW'][i]
        assert params[i].formation_volume_factor == expected_water_properties['BW'][i]


def test_nexus_water_repr():
    # Arrange
    water_obj = NexusWaterMethod(file_path='test/file/water.dat', input_number=1)
    water_obj.properties = {'SUNITS': SUnits.PPM, 'TEMP_UNIT': TemperatureUnits.KELVIN}
    water_obj.reference_pressure = 3600.0
    water_params1 = NexusWaterParams(temperature=394.3, salinity=100000.0,
                                     density=62.4, compressibility=3.4,
                                     formation_volume_factor=1.04, viscosity=0.7, 
                                     viscosity_compressibility=None
                                     )
    water_params2 = NexusWaterParams(temperature=394.3, salinity=200000.0,
                                     density=65.4, compressibility=4.4,
                                     formation_volume_factor=1.05, viscosity=0.8, 
                                     viscosity_compressibility=None
                                     )
    water_obj.parameters = [water_params1, water_params2]
    expected_output = """
FILE_PATH: test/file/water.dat
PREF: 3600.0
SUNITS: PPM
TEMP_UNIT: KELVIN
TEMP: 394.3
    SALINITY: 100000.0
        DENW: 62.4
        CW: 3.4
        BW: 1.04
        VISW: 0.7
    SALINITY: 200000.0
        DENW: 65.4
        CW: 4.4
        BW: 1.05
        VISW: 0.8
"""

    # Act
    result = water_obj.__repr__()

    # Assert
    assert result == expected_output
