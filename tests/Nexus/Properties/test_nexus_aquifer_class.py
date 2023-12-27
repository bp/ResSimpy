import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits
from ResSimpy.Nexus.NexusAquiferMethods import NexusAquiferMethods

@pytest.mark.parametrize("file_contents, expected_aquifer_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    CARTER_TRACY
    LABEL SOUTH_FLANK
    BAQ 20
    TC 100
    PAQI 4800
    DAQI 9600
    TRACER
    NAME CONCENTRATION
    c1 0.2
    c2 0.05
    ENDTRACER
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'CARTER_TRACY': '', 'LABEL': 'SOUTH_FLANK', 'BAQ': 20, 'TC': 100, 'PAQI': 4800, 'DAQI': 9600,
          'TRACER': pd.DataFrame({'NAME': ['c1', 'c2'],
                                  'CONCENTRATION': [0.2, 0.05]
                                  })
          }  # Need to handle 'LABEL': "SOUTH FLANK" case
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    CARTER_TRACY
    CT 1E-6
    H 50
    RO 5000
    S 0.3333
    TC 400
    ! User Supplied Table
    TDPD
    TD PD
    0.0 0.0
    0.01 0.115
    0.10 0.350
    0.20 0.472
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'CARTER_TRACY': '', 'CT': 1e-6, 'H': 50, 'RO': 5000, 'S': 0.3333, 'TC': 400,
          'TDPD': pd.DataFrame({'TD': [0., 0.01, 0.1, 0.2],
                                'PD': [0., 0.115, 0.35, 0.472]
                                })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    CARTER_TRACY
    LABEL LINEAR_AQ1
    BAQ 20
    TC 1.1
    LINEAR
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'CARTER_TRACY': '', 'LABEL': 'LINEAR_AQ1', 'BAQ': 20, 'TC': 1.1}
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! This is a comment
    FETKOVICH
    LABEL FETTY_V
    RADIAL
    H 50
    VISC 1.1
    S 0.3333
    RO 5000
    RE 10000
    NOFLOW

    LINFAC 2.5

    CT 1E-6
    WAQI 5e8
    PAQI 4800
    DAQI 9600

    TRACER
    NAME CONCENTRATION
    c1 0.2
    c2 0.05
    ENDTRACER

    SUNITS PPM
    IWATER 2
    SALINITY 300000
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM, 'IWATER': 2, 'SALINITY': 300000, 'LINFAC': 2.5,
          'FETKOVICH': '', 'LABEL': 'FETTY_V', 'RADIAL': '', 'VISC': 1.1, 'CT': 1e-6, 'H': 50, 'RO': 5000,
          'S': 0.3333, 'RE': 10000, 'NOFLOW': '', 'WAQI': 5e8, 'PAQI': 4800, 'DAQI': 9600,
          'TRACER': pd.DataFrame({'NAME': ['c1', 'c2'],
                                  'CONCENTRATION': [0.2, 0.05]
                                  })
          }
    ),
    ], ids=['baq_carter_tracy', 'tdpd_carter_tracy', 'linear_carter_tracy', 'fetkovich']
)
def test_read_aquifer_properties_from_file(mocker, file_contents, expected_aquifer_properties):
    # Arrange
    aq_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    aquifer_obj = NexusAquiferMethod(file=aq_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    aquifer_obj.read_properties()
    props = aquifer_obj.properties

    # Assert
    for key in expected_aquifer_properties:
        if isinstance(expected_aquifer_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_aquifer_properties[key], props[key])
        else:
            assert props[key] == expected_aquifer_properties[key]


def test_nexus_aquifer_repr():
    # Arrange
    aq_file = NexusFile(location='test/file/aquifer.dat')
    aquifer_obj = NexusAquiferMethod(file=aq_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    aquifer_obj.properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                              'FETKOVICH': '', 'LABEL': 'FETTY_V',
                              'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM, 'IWATER': 2, 'SALINITY': 300000,
                              'LINFAC': 2.5, 'RADIAL': '', 'VISC': 1.1, 'CT': 1e-6, 'H': 50, 'RO': 5000,
                              'S': 0.3333, 'RE': 10000, 'NOFLOW': '', 'WAQI': 5e8, 'PAQI': 4800, 'DAQI': 9600
          }
    expected_output = """
FILE_PATH: test/file/aquifer.dat

DESC This is first line of description
DESC and this is second line of description
FETKOVICH
LABEL FETTY_V
ENGLISH
SUNITS PPM
IWATER 2
SALINITY 300000
LINFAC 2.5
RADIAL
VISC 1.1
CT 1e-06
H 50
RO 5000
S 0.3333
RE 10000
NOFLOW
WAQI 500000000.0
PAQI 4800
DAQI 9600

"""

    # Act
    result = aquifer_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_aquifer_methods_repr():
    # Arrange
    aq_file = NexusFile(location='test/file/aquifer.dat')
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                              'FETKOVICH': '', 'LABEL': 'FETTY_V',
                              'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM, 'IWATER': 2, 'SALINITY': 300000,
                              'LINFAC': 2.5, 'RADIAL': '', 'VISC': 1.1, 'CT': 1e-6, 'H': 50, 'RO': 5000,
                              'S': 0.3333, 'RE': 10000, 'NOFLOW': '', 'WAQI': 5e8, 'PAQI': 4800, 'DAQI': 9600
          }
    aquifer_obj = NexusAquiferMethod(file=aq_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                     properties=properties)
    aquifer_methods_obj = NexusAquiferMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: aquifer_obj,
                                                                                            2: aquifer_obj})
    expected_output = """
--------------------------------
AQUIFER method 1
--------------------------------

FILE_PATH: test/file/aquifer.dat

DESC This is first line of description
DESC and this is second line of description
FETKOVICH
LABEL FETTY_V
ENGLISH
SUNITS PPM
IWATER 2
SALINITY 300000
LINFAC 2.5
RADIAL
VISC 1.1
CT 1e-06
H 50
RO 5000
S 0.3333
RE 10000
NOFLOW
WAQI 500000000.0
PAQI 4800
DAQI 9600



--------------------------------
AQUIFER method 2
--------------------------------

FILE_PATH: test/file/aquifer.dat

DESC This is first line of description
DESC and this is second line of description
FETKOVICH
LABEL FETTY_V
ENGLISH
SUNITS PPM
IWATER 2
SALINITY 300000
LINFAC 2.5
RADIAL
VISC 1.1
CT 1e-06
H 50
RO 5000
S 0.3333
RE 10000
NOFLOW
WAQI 500000000.0
PAQI 4800
DAQI 9600


"""

    # Act
    result = aquifer_methods_obj.__repr__()

    # Assert
    assert result == expected_output
