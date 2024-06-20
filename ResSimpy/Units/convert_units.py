from typing import Callable, Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.Units import UnitDimension


def get_map(from_unit: UnitSystem, to_unit: UnitSystem, unit_dim: UnitDimension) -> Optional[Callable]:
    mapping = {'ENGLISH_METBAR': 'english_to_metbar',
               'METBAR_ENGLISH': 'metbar_to_english',
               }

    function_name = mapping[from_unit.value + '_' + to_unit.value]

    function_call = getattr(unit_dim, function_name, None)
    if function_call is None:
        return None
    return function_call


def convert_units(from_unit: UnitSystem, to_unit: UnitSystem, unit_dim: UnitDimension, value: float) -> float:
    unit_mapping_function = get_map(from_unit, to_unit, unit_dim)
    if unit_mapping_function is None:
        return value
    return unit_mapping_function(value)


def convert_object(obj: object, to_unit: UnitSystem) -> object:
    for attr in obj.__dict__:
        # TODO: use the typing in the dict rather than checking if it is a float
        if isinstance(obj.__dict__[attr], float):
            obj.__dict__[attr] = convert_units(obj.__dict__[attr].unit_system,
                                               to_unit,
                                               obj.__dict__[attr],
                                               obj.__dict__[attr].value)
    return obj
