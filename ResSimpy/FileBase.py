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
        raise NotImplementedError("Implement this in the derived class")

    @property
    @abstractmethod
    def get_flat_list_str_file(self) -> list[str]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add_object_locations(self, obj_uuid: UUID, line_indices: list[int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @staticmethod
    @abstractmethod
    def insert_comments(additional_content: list[str], comments) -> list[str]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_object_locations_for_id(self, obj_id: UUID) -> list[int]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_object_from_file_as_list(self, objects_to_remove: list[UUID]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add_to_file_as_list(self, additional_content: list[str], index: int,
                            additional_objects: Optional[dict[UUID, list[int]]] = None,
                            comments: Optional[str] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_from_file_as_list(self, index: int, objects_to_remove: Optional[list[UUID]] = None,
                                 string_to_remove: Optional[str] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
