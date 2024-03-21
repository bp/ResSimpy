"""Handling the mapping between ResSimpy attributes and the unit type of the attribute."""
from abc import ABC
from typing import Mapping

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.Units import UnitDimension


class BaseUnitMapping(ABC):
    """Base class for handling the mapping between ResSimpy attributes and the unit type of the attribute."""
    attribute_map: Mapping[str, UnitDimension]

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the BaseUnitMapping class.

        Args:
            unit_system (None | UnitSystem): The unit system to use for the unit mapping.
        """
        self.unit_system = unit_system

    def get_unit_for_attribute(self, attribute_name: str, uppercase: bool = False) -> str:
        """Returns the unit variable for the given unit system.

        Args:
            attribute_name (str): name of the attribute to get the unit for
            uppercase (bool): if True returns the unit in uppercase
        """
        unit_dimension = self.attribute_map.get(attribute_name, None)
        if unit_dimension is None:
            raise AttributeError(f'Attribute {attribute_name} not recognised and does not have a unit definition')
        if self.unit_system is None:
            raise AttributeError('Unit system not defined')
        unit = unit_dimension.unit_system_enum_to_variable(unit_system=self.unit_system)
        if uppercase:
            unit = unit.upper()
        return unit

    def get_unit_for_keyword(self, keyword: str,
                             keyword_mapping: dict[str, tuple[str, type]],
                             uppercase: bool = False) -> str:
        """Given a simulator keyword, return the appropriate unit string.

        Args:
            keyword (str): Simulator keyword
            keyword_mapping (dict[str, tuple[str, type]]): Mapping of simulator keywords to attribute definitions
            uppercase (bool): if True returns the unit in uppercase

        Returns:
            str: unit string
        """
        attribute_name = keyword_mapping[keyword][0]  # Extract ResSimpy attribute name from provided keyword mapping
        return self.get_unit_for_attribute(attribute_name, uppercase)
