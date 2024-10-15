from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Sequence, TYPE_CHECKING, Optional

from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList
if TYPE_CHECKING:
    from ResSimpy.DataModelBaseClasses.Network import Network


@dataclass(kw_only=True)
class NetworkLists(ABC):
    """Base class for representing different list types for the model."""
    _lists: Sequence[NetworkList]
    __parent_network: Network

    def __init__(self, parent_network: Network) -> None:
        """Initialises the ConLists class."""
        self.__parent_network: Network = parent_network

    @property
    @abstractmethod
    def _network_element_name(self) -> Literal['conlists', 'welllists', 'node_lists']:
        raise NotImplementedError('This method must be implemented in the derived class.')

    @property
    def lists(self) -> Sequence[NetworkList]:
        """Returns all ConList instances."""
        return self._lists

    @property
    def unique_names(self) -> list[str]:
        """Returns all ConList names."""
        return list({x.name for x in self.lists if x.name is not None})

    @staticmethod
    @abstractmethod
    def table_header() -> Literal['WELLLIST', 'CONLIST']:
        """Start of the table."""
        raise NotImplementedError('This method must be implemented in the derived class.')

    @staticmethod
    @abstractmethod
    def table_footer() -> Literal['ENDWELLLIST', 'ENDCONLIST']:
        """End of the table."""
        raise NotImplementedError('This method must be implemented in the derived class.')

    def get_all_by_name(self, list_name: str) -> Sequence[NetworkList]:
        """Returns a list of NetworkLists which match the provided name loaded from the simulator.

        Args:
        ----
            list_name (str): name of the requested ConList

        Returns:
        -------
            list[NexusConList]: the requested list of filtered lists with the same name
        """
        self.__parent_network.get_load_status()
        return [x for x in self._lists if x.name == list_name]

    @abstractmethod
    def _add_to_memory(self, additional_list: Optional[Sequence[NetworkList]]) -> None:
        """Adds additional lists to the current list."""
        raise NotImplementedError('This method must be implemented in the derived class.')
