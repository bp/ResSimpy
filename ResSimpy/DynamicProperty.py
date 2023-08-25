from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from ResSimpy.File import File


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

    def __repr__(self) -> str:
        """Pretty printing dynamic property data."""
        printable_str = f'\nFILE_PATH: {self.file.location}\n\n'
        printable_str += self.to_string()
        return printable_str

    def to_string(self) -> str:
        """Write dynamic property data to string."""
        raise NotImplementedError('Implement in the derived class.')

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
