from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Sequence

from ResSimpy.NetworkList import NetworkList


@dataclass(kw_only=True)
class NetworkLists(ABC):
    """Base class for representing different list types for the model."""
    _lists: Sequence[NetworkList]

    def __init__(self) -> None:
        """Initialises the ConLists class."""
        self._lists = []

    @property
    @abstractmethod
    def _network_element_name(self) -> Literal['conlists']:
        raise NotImplementedError('This method must be implemented in the derived class.')

    @property
    def lists(self) -> Sequence[NetworkList]:
        """Returns all ConList instances."""
        return self._lists

    @property
    def unique_names(self) -> list[str]:
        """Returns all ConList names."""
        return list({x.name for x in self.lists if x.name is not None})

    def get_all_by_name(self, list_name: str) -> Sequence[NetworkList]:
        """Returns a list of list objects that match by name.

        Args:
            list_name (str): The name of the NetworkList.

        Returns:
            list[NetworkList]: list of NetworkList that match by name.
        """
        return [x for x in self.lists if x.name == list_name]

    @staticmethod
    @abstractmethod
    def table_header() -> str:
        """Start of the table."""
        raise NotImplementedError('This method must be implemented in the derived class.')

    @staticmethod
    @abstractmethod
    def table_footer() -> str:
        """End of the table."""
        raise NotImplementedError('This method must be implemented in the derived class.')

