from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Sequence, TYPE_CHECKING, Optional

from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList
from ResSimpy.Time.ISODateTime import ISODateTime

if TYPE_CHECKING:
    from ResSimpy.DataModelBaseClasses.Network import Network


@dataclass(kw_only=True)
class NetworkLists(ABC):
    """Base class for representing different list types for the model."""
    _lists: Sequence[NetworkList]
    __parent_network: Network

    def __init__(self, parent_network: Network) -> None:
        """Initialises the NetworkList ABC."""
        self.__parent_network: Network = parent_network

    @property
    @abstractmethod
    def _network_element_name(self) -> Literal['conlists', 'welllists', 'nodelists']:
        raise NotImplementedError('This method must be implemented in the derived class.')

    @property
    def lists(self) -> Sequence[NetworkList]:
        """Returns all NetworkList instances."""
        return self._lists

    @property
    def unique_names(self) -> list[str]:
        """Returns all NetworkList names."""
        return list({x.name for x in self.lists if x.name is not None})

    @staticmethod
    @abstractmethod
    def table_header() -> Literal['WELLLIST', 'CONLIST', 'NODELIST']:
        """Start of the table."""
        raise NotImplementedError('This method must be implemented in the derived class.')

    @staticmethod
    @abstractmethod
    def table_footer() -> Literal['ENDWELLLIST', 'ENDCONLIST', 'ENDNODELIST']:
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

    def to_string_for_date(self, date: ISODateTime) -> str:
        """Returns a string representation of the lists for a specific date."""
        lists_for_date = [x for x in self._lists if x.iso_date == date]
        if not lists_for_date:
            return ''
        printable_string = ''
        for list_item in lists_for_date:
            printable_string += f'{self.table_header()} {list_item.name}\n'
            # remove all the previous wells and reinitialise the list
            printable_string += 'CLEAR\nADD\n'
            printable_string += ' '.join(list_item.elements_in_the_list) + '\n'
            printable_string += self.table_footer() + '\n'
        return printable_string
