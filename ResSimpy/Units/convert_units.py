from typing import Callable, Optional, Protocol, TypeVar

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import UnitDimension


# Set up typing and generics for the convert_units function
class UnitConvertableObject(Protocol):
    """Protocol for objects that can be converted between unit systems.
    Implements _unit_system and units properties.
    """
    _unit_system: UnitSystem

    @property
    def units(self) -> BaseUnitMapping: ...

    @property
    def unit_system(self) -> UnitSystem: ...


T = TypeVar('T', bound=UnitConvertableObject)


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


def convert_object_units(obj: T, to_unit: UnitSystem) -> T:
    """Inplace conversion of all attributes on the provided object to the new unit system.

    Args:
        obj (UnitConvertableObject): The object to convert attributes of.
        to_unit (UnitSystem): The unit system to convert to.
    """
    for attr, value in obj.__dict__.items():
        # TODO: use the typing in the dict rather than checking if it is a float
        if isinstance(value, float):

            attribute_unit_dims = obj.units.attribute_map.get(attr, None)
            if attribute_unit_dims is None:
                continue
            converted_value = convert_units(obj.unit_system,
                                            to_unit,
                                            attribute_unit_dims,
                                            value)
            setattr(obj, attr, converted_value)
    obj._unit_system = to_unit
    return obj
