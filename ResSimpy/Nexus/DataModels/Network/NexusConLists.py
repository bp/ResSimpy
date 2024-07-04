"""Contains a class for representing a set of ConList objects for the Nexus model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from ResSimpy.NetworkLists import NetworkLists
from ResSimpy.Nexus.DataModels.Network.NexusConList import NexusConList

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusConLists(NetworkLists):
    """Class for representing a set of conList objects for the Nexus model."""

    _con_lists: list[NexusConList] = field(default_factory=list)
    __parent_network: NexusNetwork

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusconLists class.

        Args:
            parent_network (NexusNetwork): The network that the con lists are a part of.
        """
        super().__init__()
        self.__parent_network: NexusNetwork = parent_network

    def get_all(self) -> list[NexusConList]:
        """Returns all conList names."""
        self.__parent_network.get_load_status()
        return self._con_lists

    @property
    def conlists(self) -> list[NexusConList]:
        """Returns list of all conList objects."""
        self.__parent_network.get_load_status()
        return self._con_lists

    @property
    def table_header(self) -> str:
        """Start of the Node definition table."""
        return 'CONLIST'

    @property
    def table_footer(self) -> str:
        """End of the Node definition table."""
        return 'ENDCONLIST'

    def get_all_by_name(self, con_list_name: str) -> list[NexusConList]:
        """Returns a list of ConLists which match the provided name loaded from the simulator.

        Args:
        ----
            con_list_name (str): name of the requested ConList

        Returns:
        -------
            list[NexusConList]: the requested list of filtered conlists with the same name
        """
        self.__parent_network.get_load_status()
        return [x for x in self._con_lists if x.name == con_list_name]

    def _add_to_memory(self, additional_list: None | list[NexusConList]) -> None:
        if additional_list is None:
            return
        only_conlist_objects = [x for x in additional_list if isinstance(x, NexusConList)]
        self._con_lists.extend(only_conlist_objects)

    @property
    def _network_element_name(self) -> Literal['conlists']:
        return 'conlists'
