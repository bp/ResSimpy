import uuid
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.general_utilities import expand_string_list_of_numbers, convert_to_number, is_number
from ResSimpy.Utils.generic_repr import generic_repr, generic_str
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map, attribute_name_to_nexus_keyword, \
    nexus_keyword_to_attribute_name
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
from ResSimpy.Utils.obj_to_table_string import to_table_line, get_column_headers_required
from ResSimpy.Utils.to_dict_generic import to_dict


@dataclass
class GenericTest:
    attr_1: str
    attr_2: int
    attr_3: float
    unit_system: UnitSystem
    date: str
    attr_4: Optional[str] = None
    attr_5: Optional[str] = 'asdj'
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False, repr=False)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        mapping_dict = {
            'ATTR_1': ('attr_1', str),
            'ATTR_2': ('attr_2', int),
            'ATTR_3': ('attr_3', float),
            'ATTR_4': ('attr_4', str),
            'ATTR_5': ('attr_5', str)
        }
        return mapping_dict

    def to_dict(self, include_nones=True, add_iso_date=True):
        return to_dict_generic.to_dict(self, add_date=True, add_units=True, include_nones=include_nones,
                                       add_iso_date=add_iso_date)

    def __repr__(self):
        return generic_repr(self, exclude_attributes=['attr_5'])

    def __str__(self):
        return generic_str(self)


def test_to_dict():
    # Arrange
    class_inst = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC,
                             date='01/01/2030')
    expected = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'attr_4': None, 'unit_system': 'METRIC',
                'date': '01/01/2030', 'attr_5': 'asdj', }
    expected_no_date_no_units = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'attr_4': None, 'attr_5': 'asdj', }
    expected_nexus_style = {
        'ATTR_1': 'hello', 'ATTR_2': 10, 'ATTR_3': 43020.2, 'unit_system': 'METRIC',
        'date': '01/01/2030', 'ATTR_4': None, 'ATTR_5': 'asdj',
    }
    expected_without_nones = {
        'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'unit_system': 'METRIC',
        'date': '01/01/2030', 'attr_5': 'asdj',
    }
    # Act
    result = to_dict(class_inst)
    result_no_date_no_units = to_dict(class_inst, add_units=False, add_date=False)
    result_nexus_style = to_dict(class_inst, keys_in_nexus_style=True)
    result_no_nuns_none = class_inst.to_dict(include_nones=False)

    # Assert
    assert result == expected
    assert result_no_date_no_units == expected_no_date_no_units
    assert result_nexus_style == expected_nexus_style
    assert result_no_nuns_none == expected_without_nones


def test_obj_to_dataframe():
    # Arrange
    class_inst_1 = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC,
                               date='01/01/2030',
                               )
    class_inst_2 = GenericTest(attr_1='world', attr_2=2, attr_3=2.2, unit_system=UnitSystem.ENGLISH,
                               date='01/01/2033')
    list_class = [class_inst_1, class_inst_2]

    expected_df = pd.DataFrame({
        'attr_1': ['hello', 'world'],
        'attr_2': [10, 2],
        'attr_3': [43020.2, 2.2],
        'attr_5': ['asdj', 'asdj'],
        'unit_system': ['METRIC', 'ENGLISH'],
        'date': ['01/01/2030', '01/01/2033'],
    })
    # Act
    result = obj_to_dataframe(list_class)
    # Assert
    pd.testing.assert_frame_equal(result, expected_df, check_like=True)


def test_generic_repr_str(mocker):
    # Arrange
    mocker.patch('uuid.uuid4', return_value='uuid1')
    class_inst = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC,
                             date='01/01/2030',
                             attr_4='world')
    # mock out id

    expected_repr = (
        "GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=<UnitSystem.METRIC: 'METRIC'>, "
        "date='01/01/2030', attr_4='world', GenericTest__id='uuid1')")

    expected_str = ("GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=<UnitSystem.METRIC: 'METRIC'>, "
                    "date='01/01/2030', attr_4='world', attr_5='asdj')")
    # Act Assert
    assert repr(class_inst) == expected_repr
    assert str(class_inst) == expected_str


def test_invert_nexus_map():
    # Arrange
    @dataclass
    class NexusClass:
        date: str
        depth: float
        x_pos: Optional[float]

        def nexus_mapping(self):
            nexus_mapping = {
                'DEPTH': ('depth', float),
                'X': ('x_pos', float)
            }
            return nexus_mapping

    nex_class = NexusClass(date='01/01/2020', depth=10, x_pos=1.5)
    nexus_map = nex_class.nexus_mapping()
    expected_result = {'depth': 'DEPTH', 'x_pos': 'X'}

    # Act
    result = invert_nexus_map(nexus_map)

    # Assert
    assert result == expected_result


def test_nexus_keyword_to_attribute_name():
    # Arrange
    @dataclass
    class NexusClass:
        date: str
        depth: float
        x_pos: Optional[float]
        y_pos: Optional[float]
        rand: Optional[str]

        def nexus_mapping(self):
            nexus_mapping = {
                'DEPTH': ('depth', float),
                'X': ('x_pos', float),
                'Y': ('y_pos', float),
                'RANDOM': ('rand', str),
            }
            return nexus_mapping

    nex_class = NexusClass(date='01/01/2020', depth=10, x_pos=1.5, y_pos=3.14, rand='hello')
    nexus_map = nex_class.nexus_mapping()

    expected_attr = 'x_pos'
    expected_nexus_keyword = 'RANDOM'

    # Act
    result_attr = nexus_keyword_to_attribute_name(nexus_map, 'X')
    result_nexus_keyword = attribute_name_to_nexus_keyword(nexus_map, 'rand')

    # Assert
    assert result_attr == expected_attr
    assert result_nexus_keyword == expected_nexus_keyword

    with pytest.raises(AttributeError):
        nexus_keyword_to_attribute_name(nexus_map, 'Failure')
    with pytest.raises(AttributeError):
        attribute_name_to_nexus_keyword(nexus_map, 'also fails')


@pytest.mark.parametrize('headers, expected_result', [
    # basic
    (['ATTR_1', 'ATTR_2', 'ATTR_3'],
     'name 10 3.14\n'),
    # repeated + No value to NA
    (['ATTR_1', 'ATTR_1', 'ATTR_1', 'ATTR_4'],
     'name name name NA\n'),
    # not in attributes
    (['ATTR_1', 'ATTR_NOT_VALID', 'ATTR_1', 'ATTR_4'],
     None),
], ids=['basic', 'repeated + No value to NA', 'not in attributes'])
def test_to_string_generic(mocker, headers, expected_result):
    # Arrange
    test_object = GenericTest(attr_1='name', attr_2=10, attr_3=3.14, attr_4=None, date='01/01/2020',
                              unit_system=UnitSystem.ENGLISH)

    # Act
    if expected_result is None:
        # for the failure case
        with pytest.raises(AttributeError) as ae:
            result_string = to_table_line(test_object, headers)
            assert 'No attribute found with name "ATTR_NOT_VALID"' in ae
        return
    result_string = to_table_line(test_object, headers)

    # Assert
    assert result_string == expected_result


@pytest.mark.parametrize('input_string, expected_result', [
    # string with repeats
    ("1 2 3 4*20 3*12.5 4 5 2*6.4e-5 1*7.2E+3 8",
     "1 2 3 20 20 20 20 12.5 12.5 12.5 4 5 6.4e-05 6.4e-05 7200.0 8"),
    # no repeats
    ('1 2 3 4 5',
     '1 2 3 4 5')
], ids=['string_with_repeats', 'no_repeats'])
def test_expand_string_list_of_numbers(input_string, expected_result):
    # Arrange

    # Act
    result = expand_string_list_of_numbers(input_string)

    # Assert
    assert result == expected_result


def test_convert_to_number_error():
    # Arrange
    err_input = '3abc'
    expected_error_msg = f'Provided string {err_input} is erroneous and needs to be either an integer or a float.'

    # Act
    with pytest.raises(ValueError) as error:
        convert_to_number(err_input)

    # Assert
    assert str(error.value) == expected_error_msg


@pytest.mark.parametrize('input_string, expected', [
    # string with scientific notation, floats and integers
    ('3', True),
    ('-3', True),
    ('-3.3', True),
    ('1e3', True),
    ('1E3', True),
    ('2E+4', True),
    ('-2e+4', True),
    ('1e-300', True),
    ('-0.0', True),

    # False cases
    ('--3.3', False),
    ('12..34', False),
    ('+-123.45', False),
    ('e123', False),
    ('abc', False),
    ('', False),
])
def test_is_number(input_string, expected):
    # Act
    result = is_number(input_string)

    # Assert
    assert result == expected


def test_get_column_headers_required():
    # Arrange
    class_inst_1 = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC,
                               date='01/01/2030')
    class_inst_2 = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, attr_5='hello', unit_system=UnitSystem.METRIC,
                               date='01/01/2030')
    
    expected_headers = ['ATTR_1', 'ATTR_2', 'ATTR_3', 'ATTR_5']
    
    objects_list = [class_inst_1, class_inst_2]
    
    # Act
    result_headers = get_column_headers_required(objects_list)

    # Assert
    assert result_headers == expected_headers
