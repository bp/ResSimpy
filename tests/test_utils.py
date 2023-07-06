from dataclasses import dataclass
from typing import Optional

import pandas as pd
import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr
from ResSimpy.Utils.invert_nexus_map import invert_nexus_map, attribute_name_to_nexus_keyword, \
    nexus_keyword_to_attribute_name
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
from ResSimpy.Utils.to_dict_generic import to_dict


def test_to_dict():
    # Arrange
    @dataclass
    class GenericTest:
        attr_1: str
        attr_2: int
        attr_3: float
        unit_system: UnitSystem
        date: str

        @staticmethod
        def get_nexus_mapping():
            mapping_dict = {
                'ATTR_1': ('attr_1', str),
                'ATTR_2': ('attr_2', int),
                'ATTR_3': ('attr_3', float),
            }
            return mapping_dict

    class_inst = GenericTest(attr_1='hello', attr_2=10, attr_3=43020.2, unit_system=UnitSystem.METRIC,
                             date='01/01/2030')
    expected = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, 'unit_system': 'METRIC', 'date': '01/01/2030'}
    expected_no_date_no_units = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2 }
    expected_nexus_style = {
        'ATTR_1': 'hello', 'ATTR_2': 10, 'ATTR_3': 43020.2, 'unit_system': 'METRIC',
        'date': '01/01/2030'
    }
    # Act
    result = to_dict(class_inst )
    result_no_date_no_units = to_dict(class_inst, add_units=False, add_date=False)
    result_nexus_style = to_dict(class_inst, keys_in_nexus_style=True)

    # Assert
    assert result == expected
    assert result_no_date_no_units == expected_no_date_no_units
    assert result_nexus_style == expected_nexus_style


def test_obj_to_dataframe():
    # Arrange
    @dataclass
    class GenericTest:
        attr_1: str
        attr_2: int
        attr_3: float
        unit_system: UnitSystem
        date: str

        @staticmethod
        def get_nexus_mapping():
            mapping_dict = {
                'ATTR_1': ('attr_1', str),
                'ATTR_2': ('attr_2', int),
                'ATTR_3': ('attr_3', float),
            }
            return mapping_dict

        def to_dict(self):
            return to_dict_generic.to_dict(self, add_date=True, add_units=True)

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


def test_generic_repr():
    @dataclass
    class MyClass:
        well: str
        depth: float
        x_pos: Optional[float]
        y_pos: Optional[float]
        temp: Optional[float]

        def __repr__(self) -> str:
            return generic_repr(self)

    obj = MyClass(
        well="my_well",
        depth=100,
        x_pos=50.0,
        y_pos=75.0,
        temp=None
    )
    expected = "MyClass(well='my_well', depth=100, x_pos=50.0, y_pos=75.0)"
    assert repr(obj) == expected


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
        attribute_name_to_nexus_keyword(nexus_map, 'also fails')

