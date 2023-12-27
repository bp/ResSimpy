import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusHydraulicsMethods import NexusHydraulicsMethods

@pytest.mark.parametrize("file_contents, expected_hydraulics_properties",
    [(
    """
    DESC Hydraulics Data

    ENGLISH

    ! Comment
    QOIL 1.0 1000. 3000. ! GOR
    GOR 0.0 0.5     !  comment ! Gas oil ratio
    ! Another comment
    WCUT 0.0
    THP 100. 500.
    IGOR IWCUT IQOIL BHP(ITHP)
       1     1     1  2470. 2545.
       1     1     2  2478. 2548.
       1     1     3  2493. 2569.
       2     1     1  1860. 1990.
       2     1     2  1881. 2002.
       2     1     3  1947. 2039.
    """, {'DESC': ['Hydraulics Data'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'QOIL': '1.0 1000. 3000.',
          'GOR': '0.0 0.5',
          'WCUT': '0.0',
          'THP': '100. 500.',
          'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 2, 2, 2],
                                     'IWCUT': [1, 1, 1, 1, 1, 1],
                                     'IQOIL': [1, 2, 3, 1, 2, 3],
                                     'BHP0': [2470., 2478., 2493., 1860., 1881., 1947.],
                                     'BHP1': [2545., 2548., 2569., 1990., 2002., 2039.0]
                                     })
          }
    ),
    (
    """
    DESC Hydraulics Data

    ENGLISH

    ! Comment
    QLIQ 1.0 1000. 3000.
    GLR 0.0 0.5     !  comment ! Gas oil ratio
    ! Another comment
    WCUT 0.0
    POUT 100. 500.

    LENGTH 10000
    DATUM 8000

    IGLR IWCUT IQLIQ
       1     1     1  2470. 2545.
       1     1     2  2478. 2548.
       1     1     3  2493. 2569.
       2     1     1  1860. 1990.
       2     1     2  1881. 2002.
       2     1     3  1947. 2039.

    NOCHK

    WATINJ GRAD 0.433
           VISC 0.7
           LENGTH 9000
           ROUGHNESS 1e-5
           DZ 8000
           DIAM 7

    LIMITS
    VARIABLE MIN MAX
    QLIQ 0.0 5000.0
    GLR 0.0 1.0
    ENDLIMITS

    DATGRAD GRAD
    """, {'DESC': ['Hydraulics Data'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'QLIQ': '1.0 1000. 3000.',
          'GLR': '0.0 0.5',
          'WCUT': '0.0',
          'POUT': '100. 500.',
          'LENGTH': 10000., 'DATUM': 8000., 'NOCHK': '', 'DATGRAD': 'GRAD',
          'WATINJ': {'GRAD': 0.433, 'VISC': 0.7, 'LENGTH': 9000,
                     'ROUGHNESS': 1e-5, 'DZ': 8000, 'DIAM': 7},
          'HYD_TABLE': pd.DataFrame({'IGLR': [1, 1, 1, 2, 2, 2],
                                     'IWCUT': [1, 1, 1, 1, 1, 1],
                                     'IQLIQ': [1, 2, 3, 1, 2, 3],
                                     'PIN0': [2470., 2478., 2493., 1860., 1881., 1947.],
                                     'PIN1': [2545., 2548., 2569., 1990., 2002., 2039.0]
                                     }),
          'LIMITS': pd.DataFrame({'VARIABLE': ['QLIQ', 'GLR'],
                                  'MIN': [0., 0.],
                                  'MAX': [5000., 1.]
                                  })
          }
    ),
    (
    """
    DESC Hydraulics Data

    ENGLISH

    ! Comment
    QOIL 1.0 1000. 3000.
    GOR 0.0 0.5     !  comment ! Gas oil ratio
    ! Another comment
    WCUT 0.0
    ALQ  0.0 50.0
    THP 100. 500. 900. 1400. 2000.
    IGOR IWCUT  IALQ  IQOIL  BHP(ITHP)
       1     1     1      1  2470. 2545. 2600. 2820. 3070.
       1     1     1      2  2478. 2548. 2613. 2824. 3081.
       1     1     1      3  2493. 2569. 2638. 2870. 3138.
       1     1     2      1  2535. 2600. 2650. 2852. 3130.
       1     1     2      2  2541. 2608. 2673. 2884. 3141.
       1     1     2      3  2555. 2631. 2703. 2931. 3197.
       2     1     1      1  1860. 1990. 2090. 2435. 2830.
       2     1     1      2  1881. 2002. 2101. 2438. 2836.
       2     1     1      3  1947. 2039. 2131. 2448. 2848.
       2     1     2      1  1990. 2100. 2190. 2530. 2916.
       2     1     2      2  2004. 2109. 2206. 2537. 2926.
       2     1     2      3  2033. 2130. 2224. 2548. 2946.
    """, {'DESC': ['Hydraulics Data'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'QOIL': '1.0 1000. 3000.',
          'GOR': '0.0 0.5',
          'WCUT': '0.0',
          'ALQ': '0.0 50.0',
          'THP': '100. 500. 900. 1400. 2000.',
          'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                     'IWCUT': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                     'IALQ': [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
                                     'IQOIL': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                                     'BHP0': [2470., 2478., 2493., 2535., 2541., 2555.,
                                              1860., 1881., 1947., 1990., 2004., 2033.],
                                     'BHP1': [2545., 2548., 2569., 2600., 2608., 2631.,
                                              1990., 2002., 2039., 2100., 2109., 2130.],
                                     'BHP2': [2600., 2613., 2638., 2650., 2673., 2703.,
                                              2090., 2101., 2131., 2190., 2206., 2224.],
                                     'BHP3': [2820., 2824., 2870., 2852., 2884., 2931.,
                                              2435., 2438., 2448., 2530., 2537., 2548.],
                                     'BHP4': [3070., 3081., 3138., 3130., 3141., 3197.,
                                              2830., 2836., 2848., 2916., 2926., 2946.]
                                     })
          }
    ),
    (
    """
    DESC Hydraulics Data

    ENGLISH

    ! Comment
    QOIL 1.0 1000. 3000.
    GOR 0.0 0.5     !  comment ! Gas oil ratio
    ! Another comment
    WCUT 0.0
    ALQ     GASRATE     0.0     50.0
    THP 100. 500. 900. 1400. 2000.
    IGOR IWCUT  IALQ  IQOIL  >
    BHP(ITHP)
       1     1     1      1  2470. 2545. >
                             2600. 2820. >
                             3070.
       1     1     1      2  2478. 2548. >
                             2613. 2824. >
                             3081.
       1     1     1      3  2493. 2569. 2638. 2870. 3138.
       1     1     2      1  2535. 2600. 2650. 2852. 3130.
       1     1     2      2  2541. 2608. 2673. 2884. 3141.
       1     1     2      3  2555. 2631. 2703. 2931. 3197.
       2     1     1      1  1860. 1990. 2090. 2435. 2830.
       2     1     1      2  1881. 2002. 2101. 2438. 2836.
       2     1     1      3  1947. 2039. 2131. 2448. 2848.
       2     1     2      1  1990. 2100. 2190. 2530. 2916.
       2     1     2      2  2004. 2109. >
                             2206. 2537. >
                             2926.
       2     1     2      3  2033. 2130. >
                             2224. 2548. >
                             2946.
    """, {'DESC': ['Hydraulics Data'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'QOIL': '1.0 1000. 3000.',
          'GOR': '0.0 0.5',
          'WCUT': '0.0',
          'ALQ': '0.0 50.0',
          'ALQ_PARAM': 'GASRATE',
          'THP': '100. 500. 900. 1400. 2000.',
          'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                     'IWCUT': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                     'IALQ': [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
                                     'IQOIL': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                                     'BHP0': [2470., 2478., 2493., 2535., 2541., 2555.,
                                              1860., 1881., 1947., 1990., 2004., 2033.],
                                     'BHP1': [2545., 2548., 2569., 2600., 2608., 2631.,
                                              1990., 2002., 2039., 2100., 2109., 2130.],
                                     'BHP2': [2600., 2613., 2638., 2650., 2673., 2703.,
                                              2090., 2101., 2131., 2190., 2206., 2224.],
                                     'BHP3': [2820., 2824., 2870., 2852., 2884., 2931.,
                                              2435., 2438., 2448., 2530., 2537., 2548.],
                                     'BHP4': [3070., 3081., 3138., 3130., 3141., 3197.,
                                              2830., 2836., 2848., 2916., 2926., 2946.]
                                     })
          }
    )
    ], ids=['basic_hyd', 'complex_hyd', 'with_alq', 'alq_gr_and_line_continuation']
)
def test_read_hydraulics_properties_from_file(mocker, file_contents, expected_hydraulics_properties):
    # Arrange
    hyd_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    hydraulics_obj = NexusHydraulicsMethod(file=hyd_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    hydraulics_obj.read_properties()
    props = hydraulics_obj.properties

    # Assert
    for key in expected_hydraulics_properties:
        if isinstance(expected_hydraulics_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_hydraulics_properties[key], props[key])
        elif isinstance(expected_hydraulics_properties[key], dict):
            for subkey in expected_hydraulics_properties[key].keys():
                if isinstance(expected_hydraulics_properties[key][subkey], pd.DataFrame):
                    pd.testing.assert_frame_equal(expected_hydraulics_properties[key][subkey], props[key][subkey])
                else:
                    assert props[key][subkey] == expected_hydraulics_properties[key][subkey]
        else:
            assert props[key] == expected_hydraulics_properties[key]


def test_nexus_hydraulics_repr():
    # Arrange
    hyd_file = NexusFile(location='test/file/hyd.dat')
    hyd_obj = NexusHydraulicsMethod(file=hyd_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    hyd_obj.properties = {'DESC': ['Hydraulics Data'],
                          'UNIT_SYSTEM': UnitSystem.ENGLISH,
                          'QOIL': '1.0 1000. 3000.',
                          'GOR': '0.0 0.5',
                          'WCUT': '0.0',
                          'ALQ': '0.0 50.0',
                          'ALQ_PARAM': 'GASRATE',
                          'THP': '100. 500. 900. 1400. 2000.',
                          'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                                     'IWCUT': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                                     'IALQ': [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
                                                     'IQOIL': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                                                     'BHP0': [2470., 2478., 2493., 2535., 2541., 2555.,
                                                              1860., 1881., 1947., 1990., 2004., 2033.],
                                                     'BHP1': [2545., 2548., 2569., 2600., 2608., 2631.,
                                                             1990., 2002., 2039., 2100., 2109., 2130.],
                                                     'BHP2': [2600., 2613., 2638., 2650., 2673., 2703.,
                                                             2090., 2101., 2131., 2190., 2206., 2224.],
                                                     'BHP3': [2820., 2824., 2870., 2852., 2884., 2931.,
                                                             2435., 2438., 2448., 2530., 2537., 2548.],
                                                     'BHP4': [3070., 3081., 3138., 3130., 3141., 3197.,
                                                             2830., 2836., 2848., 2916., 2926., 2946.]
                                                     }),
                          'DATGRAD': 'GRAD',
                          'WATINJ': {'GRAD': 0.433, 'VISC': 0.7, 'LENGTH': 9000,
                                     'ROUGHNESS': 1e-5, 'DZ': 8000, 'DIAM': 7},
                          'NOCHK': ''}
    expected_output = """
FILE_PATH: test/file/hyd.dat

DESC Hydraulics Data
ENGLISH
QOIL 1.0 1000. 3000.
GOR 0.0 0.5
WCUT 0.0
ALQ GASRATE 0.0 50.0
THP 100. 500. 900. 1400. 2000.
""" + hyd_obj.properties['HYD_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
DATGRAD GRAD
WATINJ
    GRAD 0.433
    VISC 0.7
    LENGTH 9000
    ROUGHNESS 1e-05
    DZ 8000
    DIAM 7
NOCHK

"""

    # Act
    result = hyd_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_hydraulics_methods_repr():
    # Arrange
    hyd_file = NexusFile(location='test/file/hyd.dat')
    properties = {'DESC': ['Hydraulics Data'],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'QOIL': '1.0 1000. 3000.',
                  'GOR': '0.0 0.5',
                  'WCUT': '0.0',
                  'ALQ': '0.0 50.0',
                  'ALQ_PARAM': 'GASRATE',
                  'THP': '100. 500. 900. 1400. 2000.',
                  'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                             'IWCUT': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                             'IALQ': [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
                                             'IQOIL': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                                             'BHP0': [2470., 2478., 2493., 2535., 2541., 2555.,
                                                      1860., 1881., 1947., 1990., 2004., 2033.],
                                             'BHP1': [2545., 2548., 2569., 2600., 2608., 2631.,
                                                      1990., 2002., 2039., 2100., 2109., 2130.],
                                             'BHP2': [2600., 2613., 2638., 2650., 2673., 2703.,
                                                      2090., 2101., 2131., 2190., 2206., 2224.],
                                             'BHP3': [2820., 2824., 2870., 2852., 2884., 2931.,
                                                      2435., 2438., 2448., 2530., 2537., 2548.],
                                             'BHP4': [3070., 3081., 3138., 3130., 3141., 3197.,
                                                      2830., 2836., 2848., 2916., 2926., 2946.]
                                            }),
                  'DATGRAD': 'GRAD',
                  'WATINJ': {'GRAD': 0.433, 'VISC': 0.7, 'LENGTH': 9000,
                             'ROUGHNESS': 1e-5, 'DZ': 8000, 'DIAM': 7},
                  'NOCHK': ''}
    hyd_obj = NexusHydraulicsMethod(file=hyd_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                    properties=properties)
    hyd_methods_obj = NexusHydraulicsMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: hyd_obj, 2: hyd_obj})
    expected_output = """
--------------------------------
HYD method 1
--------------------------------

FILE_PATH: test/file/hyd.dat

DESC Hydraulics Data
ENGLISH
QOIL 1.0 1000. 3000.
GOR 0.0 0.5
WCUT 0.0
ALQ GASRATE 0.0 50.0
THP 100. 500. 900. 1400. 2000.
""" + hyd_obj.properties['HYD_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
DATGRAD GRAD
WATINJ
    GRAD 0.433
    VISC 0.7
    LENGTH 9000
    ROUGHNESS 1e-05
    DZ 8000
    DIAM 7
NOCHK



--------------------------------
HYD method 2
--------------------------------

FILE_PATH: test/file/hyd.dat

DESC Hydraulics Data
ENGLISH
QOIL 1.0 1000. 3000.
GOR 0.0 0.5
WCUT 0.0
ALQ GASRATE 0.0 50.0
THP 100. 500. 900. 1400. 2000.
""" + hyd_obj.properties['HYD_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
DATGRAD GRAD
WATINJ
    GRAD 0.433
    VISC 0.7
    LENGTH 9000
    ROUGHNESS 1e-05
    DZ 8000
    DIAM 7
NOCHK


"""

    # Act
    result = hyd_methods_obj.__repr__()

    # Assert
    assert result == expected_output
