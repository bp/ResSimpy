from dataclasses import dataclass

import pandas as pd
import pytest

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Utils import to_dict_generic
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
    expected_no_date_no_units = {'attr_1': 'hello', 'attr_2': 10, 'attr_3': 43020.2, }
    expected_nexus_style = {'ATTR_1': 'hello', 'ATTR_2': 10, 'ATTR_3': 43020.2, 'unit_system': 'METRIC',
                            'date': '01/01/2030'}
    # Act
    result = to_dict(class_inst, )
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

    expected_df = pd.DataFrame({'attr_1': ['hello', 'world'],
                                'attr_2': [10, 2],
                                'attr_3': [43020.2, 2.2],
                                'unit_system': ['METRIC', 'ENGLISH'],
                                'date': ['01/01/2030', '01/01/2033']
                                })
    # Act
    result = obj_to_dataframe(list_class)
    # Assert
    pd.testing.assert_frame_equal(result, expected_df, check_like=True)
