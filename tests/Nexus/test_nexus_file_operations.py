import ResSimpy.Nexus.nexus_file_operations as nexus_file_operations
import pytest


@pytest.mark.parametrize("file_contents, expected_result", [
    ("""GWTABLE
        SW KRW KRWG
        0.2 0.0 1.4""",
     {'single_fluid': [(0.2, 0.0)], 'combined_fluids': [(0.2, 1.4)]}),
    ("""GWTABLE
    SW KRW KRWG
    0.2 0.0 1.4
    0.8 3.6 4.7""",
     {'single_fluid': [(0.2, 0.0), (0.8, 3.6)], 'combined_fluids': [(0.2, 1.4), (0.8, 4.7)]}),
    ("""! This is a test comment

WOTABLE 
          SW         KRW        KROW        PCWO
0.1250000  0.000E+00  1.000E+00  0.000E+00 
0.1512400  7.871E-05  9.863E-01  0.000E+00
\t\t0.2038501  1.286E-03  9.001E-01  0.000E+00 """,
     {'single_fluid': [(0.125, 0.000E+00), (0.15124, 7.871E-05), (0.2038501, 1.286E-03)],
      'combined_fluids': [(0.125, 1.000E+00), (0.15124, 9.863E-01), (0.2038501, 0.9001)]}),

    ("""GOTABLE 
          SG         KRG        KROG        PCGO
     0.000000     0.000000     1.000000     0.000000
     0.085260     0.011210     0.681265     0.000000
     ! Test comment in the middle of the table
     0.100598     0.014109     0.625140     0.000000""",
     {'single_fluid': [(0, 0), (0.085260, 0.011210)],
      'combined_fluids': [(0, 1.000E+00), (0.085260, 0.681265)]}),

    ("""GOTABLE 
    KROG   SG         KRG              PCGO
        1 2       3 4
        5 6 7 8
        9 10 11 12
 
 0.100598     0.014109     0.625140     0.000000""",
     {'single_fluid': [(2, 3), (6, 7), (10, 11)],
      'combined_fluids': [(2, 1), (6, 5), (10, 9)]}),
])
def test_load_nexus_relperm_table(mocker, file_contents, expected_result):
    # Arrange
    relperm_file_path = '/test/file/path1.dat'
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result = nexus_file_operations.load_nexus_relperm_table(relperm_file_path)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("line_contents, file_contents, expected_result", [
    ("MYTESTTOKEN 3", "MYTESTTOKEN 3\n ANOTHER_TOKEN 8", '3'),
    ("MYTESTTOKEN 123",
     """GOTABLE 
               SG         KRG        KROG        PCGO
          0.000000     0.000000     1.000000     0.000000
          0.085260     0.011210     0.681265     0.000000
          ! Test comment in the middle of the table          
          0.100598     0.014109     0.625140     0.000000
          ANOTHERTOKEN 6
        MYTESTTOKEN 123
          TOKENCONTAINING_MYTESTTOKEN 8
          FINALTOKEN 90

          """,
     '123'),
    ("MYTESTTOKEN",
     """GOTABLE 
       SG         KRG        KROG        PCGO
  0.000000     0.000000     1.000000     0.000000
  0.085260     0.011210     0.681265     0.000000
  ! Test comment in the middle of the table          
  0.100598     0.014109     0.625140     0.000000
  ANOTHERTOKEN 6
MYTESTTOKEN 
7
  TOKENCONTAINING_MYTESTTOKEN 8
  FINALTOKEN 90

  """,
     '7'),
], ids=['basic case', 'multiple lines', 'value on next line'])
def test_get_token_value(mocker, line_contents, file_contents, expected_result):
    # Arrange
    dummy_file_as_list = [y for y in (x.strip() for x in file_contents.splitlines()) if y]
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result = nexus_file_operations.get_token_value(token='MYTESTTOKEN', token_line=line_contents,
                                                   file_list=dummy_file_as_list)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("line_string, token, expected_result",
                         [("Line contains TOKEN 124", "ToKEN", True),
                          ("TokeN 323 and other text", "TOKEN", True),
                          ("other text and TokEN", "TOKEN", True),
                          ("No T0k3N here", "TOKEN", False),
                          ("!TOKEN", "TOKEN", False),
                          ("THISTOKEN etc", "TOKEN", False),
                          ("TOKENLONGERWORD etc", "TOKEN", False),
                          ("TOKEN!comment", "TOKEN", True),
                          ("TOKEN  value", "TOKEN", True),
                          ("TOKEN\n", "TOKEN", True),
                          ("T", "T", True),
                          ], ids=["standard case", "token at start", "token at end", "no token", "token commented out",
                                  "token only part of longer word 1", "token only part of longer word 2",
                                  "token before comment", "token then tab", "token then newline", "single character"])
def test_check_token(line_string, token, expected_result):
    # Act
    result = nexus_file_operations.check_token(token=token, line=line_string)

    # Assert
    assert result == expected_result
