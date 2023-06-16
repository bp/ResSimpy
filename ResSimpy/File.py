from abc import ABC
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class File(ABC):
    """The abstract base class for simulator files.

    Attributes:
        location (str): Full path to file location
        file_content_as_list (list[str]): List of lines in the file
    """

    location: Optional[str] = None
    file_content_as_list: Optional[list[str]] = field(default=None, repr=False)

    def __init__(self, location: Optional[str] = None,
                 file_content_as_list: Optional[list[str]] = None) -> None:

        self.location = location
        if file_content_as_list is None:
            self.file_content_as_list = []
        else:
            self.file_content_as_list = file_content_as_list

    def write_to_file(self) -> None:
        """Writes back to the original file location of the nexusfile."""
        if self.location is None:
            raise ValueError(f'No file path to write to, instead found {self.location}')
        if self.file_content_as_list is None:
            raise ValueError(f'No file data to write out, instead found {self.file_content_as_list}')
        file_str = ''.join(self.file_content_as_list)
        with open(self.location, 'w') as fi:
            fi.write(file_str)
