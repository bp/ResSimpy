import uuid
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr, generic_str
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map, attribute_name_to_nexus_keyword, \
    nexus_keyword_to_attribute_name
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
from ResSimpy.Utils.obj_to_table_string import to_table_line
from ResSimpy.Utils.to_dict_generic import to_dict


@dataclass
class GenericTest:
    attr_1: str
    attr_2: int
    attr_3: float
    unit_system: UnitSystem
    date: str
    attr_4: Optional[str] = None
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False, repr=False)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        mapping_dict = {
            'ATTR_1': ('attr_1', str),
            'ATTR_2': ('attr_2', int),
            'ATTR_3': ('attr_3', float),
            'ATTR_4': ('attr_4', str),
            }
        return mapping_dict

    def to_dict(self, include_nones=True):
        return to_dict_generic.to_dict(self, add_date=True, add_units=True, include_nones=include_nones)

    def __repr__(self):
        return generic_repr(self)

    def __str__(self):
        return generic_str(self)

def test_to_dict():
    # Arrange
    class_inst = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC,
                             date='01/01/2030')
    expected = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'attr_4': None, 'unit_system': 'METRIC',
                'date': '01/01/2030'}
    expected_no_date_no_units = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'attr_4': None, }
    expected_nexus_style = {
        'ATTR_1': 'hello', 'ATTR_2': 10, 'ATTR_3': 43020.2, 'unit_system': 'METRIC',
        'date': '01/01/2030', 'ATTR_4': None
    }
    expected_without_nones = {
        'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'unit_system': 'METRIC',
        'date': '01/01/2030'
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
                               date='01/01/2030')
    class_inst_2 = GenericTest(attr_1='world', attr_2=2, attr_3=2.2, unit_system=UnitSystem.ENGLISH,
                               date='01/01/2033')
    list_class = [class_inst_1, class_inst_2]

    expected_df = pd.DataFrame({
        'attr_1': ['hello', 'world'],
        'attr_2': [10, 2],
        'attr_3': [43020.2, 2.2],
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
    class_inst = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC, date='01/01/2030',
                             attr_4='world')
    # mock out id

    expected_repr = ("GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=<UnitSystem.METRIC: 'METRIC'>, "
                     "date='01/01/2030', attr_4='world', _GenericTest__id='uuid1')")
    expected_str = ("GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=<UnitSystem.METRIC: 'METRIC'>, "
                     "date='01/01/2030', attr_4='world')")
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
    test_object = GenericTest(attr_1='name', attr_2=10, attr_3=3.14, attr_4=None, date='01/01/2020', unit_system=UnitSystem.ENGLISH)

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
