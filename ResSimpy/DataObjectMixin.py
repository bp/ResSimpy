"""Base class representing a data object in ResSimpy."""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMapping import AttributeMapBase
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr
from ResSimpy.Utils.obj_to_table_string import to_table_line


@dataclass(repr=False)
class DataObjectMixin(ABC):
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    def __init__(self, properties_dict: dict[str, None | int | str | float]) -> None:
        # properties dict is a parameter to make the call signature equivalent to subclasses.
        self.__id = uuid.uuid4()
        if properties_dict:
            raise ValueError('No properties should be passed to the DataObjectMixin')

    def to_dict(self, keys_in_keyword_style: bool = False, add_date: bool = True, add_units: bool = True,
                include_nones: bool = True) -> dict[str, None | str | int | float]:
        """Returns a dictionary of the attributes of the object.

        Args:
            include_nones (bool):
            keys_in_keyword_style (bool): if True returns the key values as simulator keywords, otherwise returns the \
                attribute name as stored by ressimpy.

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_keyword_style, add_date=add_date, add_units=add_units,
                                              include_nones=include_nones)
        return result_dict

    def to_table_line(self, headers: list[str]) -> str:
        """Takes a generic Nexus object and returns the attribute values as a string in the order of headers provided.
        Requires an implemented to_dict method and get_keyword_mapping() method.

        Args:
            headers (list[str]): list of header values in keyword format

        Returns:
            string of the values in the order of the headers provided.

        """
        return to_table_line(self, headers)

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each object."""
        return self.__id

    @staticmethod
    @abstractmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of keywords to attribute definitions."""
        raise NotImplementedError("Implement this in the derived class")

    def __repr__(self) -> str:
        return generic_repr(self)

    @property
    def attribute_to_unit_map(self) -> AttributeMapBase:
        """Returns the attribute to unit map for the data object."""
        raise NotImplementedError("Implement this in the derived class")

    def get_unit_for_attribute(self, attribute_name: str, unit_system: UnitSystem, uppercase: bool = False) -> str:
        """Returns the unit variable for the given unit system.

        Args:
            attribute_name (str): name of the attribute to get the unit for
            unit_system (UnitSystem): unit system to get the unit for
            uppercase (bool): if True returns the unit in uppercase
        """
        unit_dimension = self.attribute_to_unit_map.attribute_map.get(attribute_name, None)
        if unit_dimension is None:
            raise AttributeError(f'Attribute {attribute_name} not recognised and does not have a unit definition')
        unit = unit_dimension.unit_system_enum_to_variable(unit_system=unit_system)
        if uppercase:
            unit = unit.upper()
        return unit
