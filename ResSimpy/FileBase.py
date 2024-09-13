from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass
class FileBase(ABC):
    """The abstract base class for simulator files.

    Attributes:
        location (str): Full path to file location
        file_content_as_list (list[str]): List of lines in the file
    """

    location: str
    file_content_as_list: Optional[list[str]] = field(default=None, repr=False)
    __file_modified: bool = False

    @abstractmethod
    def write_to_file(self) -> None:
        """Writes to file specified in self.location the strings contained in the list self.file_content_as_list."""
        raise NotImplementedError("Implement this in the derived class")

    @property
    @abstractmethod
    def get_flat_list_str_file(self) -> list[str]:
        """Returns flat list of string from file."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add_object_locations(self, obj_uuid: UUID, line_indices: list[int]) -> None:
        """Adds a uuid to the object_locations dictionary."""
        raise NotImplementedError("Implement this in the derived class")

    @staticmethod
    @abstractmethod
    def insert_comments(additional_content: list[str], comments: str) -> list[str]:
        """Adds comments alongside additional content."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_object_locations_for_id(self, obj_id: UUID) -> list[int]:
        """Gets the number of object locations for a specified id."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_object_from_file_as_list(self, objects_to_remove: list[UUID]) -> None:
        """Remove objects identified by UUID from file."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add_to_file_as_list(self, additional_content: list[str], index: int,
                            additional_objects: Optional[dict[UUID, list[int]]] = None,
                            comments: Optional[str] = None) -> None:
        """Adds a UUID to the object_location dictionary."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_from_file_as_list(self, index: int, objects_to_remove: Optional[list[UUID]] = None,
                                 string_to_remove: Optional[str] = None) -> None:
        """Removes an entry from the file as list."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
