from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.File import File
from ResSimpy.Units.AttributeMapping import AttributeMapBase
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitAttributeMapping import PVTUnits


@dataclass
class DynamicProperty(ABC):
    """The abstract base class for dynamic property simulator inputs, for use in inputs such as PVT, relperm, etc.

    Attributes:
        input_number (int): Method, table or input number, in order as entered in the simulation input deck.
    """

    input_number: int
    file: File

    def __init__(self, input_number: int, file: File) -> None:
        self.input_number: int = input_number
        self.file: File = file
        # self.attribute_map: AttributeMapBase

    @property
    def attribute_to_unit_map(self) -> AttributeMapBase:
        """Returns the attribute to unit map for the constraint."""
        raise NotImplementedError('Implement in the derived class.')

    def __repr__(self) -> str:
        """Pretty printing dynamic property data."""
        printable_str = f'\nFILE_PATH: {self.file.location}\n\n'
        printable_str += self.to_string()
        return printable_str

    def to_string(self) -> str:
        """Write dynamic property data to string."""
        raise NotImplementedError('Implement in the derived class.')

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

    def write_to_file(self, overwrite_existing: bool = False, new_file_location: Optional[str] = None) -> None:
        """Write dynamic property data to file."""
        printable_str = self.to_string()
        new_file_contents = printable_str.splitlines(keepends=True)
        if overwrite_existing is True and new_file_location is not None:
            raise ValueError('Please specify only one of either overwrite_existing or new_file_location.')

        if new_file_location is not None:
            new_file = File(file_content_as_list=new_file_contents, location=new_file_location)
            new_file.write_to_file()
            return
        elif overwrite_existing is False:
            raise ValueError('Please specify either overwrite_existing as True or provide new_file_location.')

        # Overwriting existing file contents
        if overwrite_existing is True:
            self.file.file_content_as_list = new_file_contents
            self.file.write_to_file()
