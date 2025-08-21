import pandas as pd
import pytest

from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from tests.multifile_mocker import mock_multiple_files


@pytest.mark.parametrize('modifier, value', [
    ('VALUE', '/some/path/to/file.dat'),
    ('CON', 25),
], ids=['mod_value', 'mod_con'])
def test_grid_array_definition_max_min(mocker, modifier, value):
    # Arrange
    grid_array_definition = GridArrayDefinition(modifier=modifier, value=value, keyword_in_include_file=False)
    # mock open the file
    data = '1 2 3 4 5\n6 7 8 9 10\n11 12\n13 14 15 16 17\n18 19 20 21 22\n23 24 25\n'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            value: data,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    expected_max = 25
    expected_min = 1 if modifier == 'VALUE' else 25
    # Act
    result_max = grid_array_definition.max()
    result_min = grid_array_definition.min()

    # Assert
    assert result_max == expected_max
    assert result_min == expected_min


@pytest.mark.parametrize('name, region_name, modifier, value, mods, expected_result', [
    ('KX', '', 'VALUE', '/some/path/to/file.dat', None, 'KX VALUE\nINCLUDE /some/path/to/file.dat\n'),
    ('KX', '', 'VALUE', '100 200 300\n200 300 400\n300 400 500', None,
     'KX VALUE\n100 200 300\n200 300 400\n300 400 500\n'),
    ('KY', '', 'XVAR', '/some/path/to/file.dat', None, 'KY XVAR\nINCLUDE /some/path/to/file.dat\n'),
    ('KZ', '', 'MULT', '0.1 KX', None, 'KZ MULT\n0.1 KX\n'),
    ('ITRAN', '', 'ZVAR', '1\n2\n3\n4', None, 'ITRAN ZVAR\n1\n2\n3\n4\n'),
    ('ITRAN', '', 'YVAR', '1 2 3 4', None, 'ITRAN YVAR\n1 2 3 4\n'),
    ('porosity', '', 'CON', 25, None, 'POROSITY CON\n25\n'),
    ('DEPTH', '', 'DIP', '12000 0 0', None, 'DEPTH DIP\n12000 0 0\n'),
    ('DEPTH', '', 'LAYER', '12000\n13000\n14000', None, 'DEPTH LAYER\n12000\n13000\n14000\n'),
    ('TMX', '', 'NONE', None, None, 'TMX NONE\n'),
    ('IREGION', '', 'ZVAR', '1 2\n3 4', None, 'IREGION ZVAR\n1 2\n3 4\n'),
    ('IREGION', 'EX1', 'VALUE', '/some/path/to/file.dat', None, 'IREGION EX1 VALUE\nINCLUDE /some/path/to/file.dat\n'),
    ('IREGION', 'EX2', 'VALUE', '/some/path/to/file.dat',
     {'MOD': pd.DataFrame(columns=['i1', 'i2', 'j1', 'j2', 'k1', 'k2', '#v'],
                          data=[[1, 10, 1, 20, 1,  5, '=1'],
                                [1, 10, 1, 20, 6, 10, '=2']])},
     'IREGION EX2 VALUE\nINCLUDE /some/path/to/file.dat\nMOD\n1 10 1 20 1  5 =1\n1 10 1 20 6 10 =2\n'),
    ('CORP', '', 'VALUE', '/some/path/to/file.dat',
     {'MODX': pd.DataFrame(columns=['i1', 'i2', 'j1', 'j2', 'k1', 'k2', '#v'],
                           data=[[1, 10, 1, 20, 1, 5, 10203040]]),
      'MODY': pd.DataFrame(columns=['i1', 'i2', 'j1', 'j2', 'k1', 'k2', '#v'],
                           data=[[1, 10, 1, 20, 1, 5, 20304050]])
      },
     'CORP VALUE\nINCLUDE /some/path/to/file.dat\nMODX\n1 10 1 20 1 5 10203040\nMODY\n1 10 1 20 1 5 20304050\n')
], ids=['kx_value_file', 'kx_value_vals', 'ky_xvar', 'kz_mult', 'itran_zvar', 'itran_yvar',
        'porosity_con', 'depth_dip', 'depth_layer', 'tmx_none', 'iregion_zvar', 'iregion_value_file',
        'iregion_value_file_with_mods', 'corp_with_mods'])
def test_grid_array_definition_to_string(name, region_name, modifier, value, mods, expected_result):
    # Arrange
    grid_array_definition = GridArrayDefinition(name=name, region_name=region_name, modifier=modifier, value=value,
                                                mods=mods, keyword_in_include_file=False)
    # Act
    result = grid_array_definition.to_string()
    # Assert
    assert result == expected_result
