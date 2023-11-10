"""Base class for handling any dynamic property simulator inputs, for use in inputs such as PVT, relperm, etc."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.File import File
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


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

    @property
    def units(self) -> BaseUnitMapping:
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

    def write_to_file(self, new_file_path: Optional[str] = None, overwrite_file: bool = False) -> None:
        """Write dynamic property data to file."""
        printable_str = self.to_string()
        new_file_contents = printable_str.splitlines(keepends=True)
        if overwrite_file is True and new_file_path is not None:
            raise ValueError('Please specify only one of either overwrite_existing or new_file_location.')

        if new_file_path is not None:
            new_file = File(file_content_as_list=new_file_contents, location=new_file_path)
            new_file.write_to_file(new_file_path=new_file_path, overwrite_file=True)
            return
        elif overwrite_file is False:
            raise ValueError('Please specify either overwrite_file as True or provide new_file_location.')

        # Overwriting existing file contents
        if overwrite_file is True:
            self.file.file_content_as_list = new_file_contents
            self.file.write_to_file(overwrite_file=overwrite_file)
