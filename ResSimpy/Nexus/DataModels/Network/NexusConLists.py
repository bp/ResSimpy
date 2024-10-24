"""Contains a class for representing a set of ConList objects for the Nexus model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Sequence

from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList
from ResSimpy.GenericContainerClasses.NetworkLists import NetworkLists
from ResSimpy.Nexus.DataModels.Network.NexusConList import NexusConList

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusConLists(NetworkLists):
    """Class for representing a set of conList objects for the Nexus model."""

    _lists: list[NexusConList] = field(default_factory=list)
    __parent_network: NexusNetwork

    def __init__(self, parent_network: NexusNetwork, con_lists: None | list[NexusConList] = None) -> None:
        """Initialises the NexusConLists class. Supports ADD and REMOVE operations on the conlist.
        Currently, this does not handle the keywords: NODEIN, NODEOUT, NODEPRODWH, NODEPRODBH, NODEINJWH or NODEINJBH.

        Args:
            parent_network (NexusNetwork): The network that the con lists are a part of.
            con_lists (list[NexusConList]): The list of con lists to be added to the NexusConLists object
        """
        self._lists = con_lists if con_lists is not None else []
        super().__init__(parent_network=parent_network)

    def get_all(self) -> list[NexusConList]:
        """Returns all conList names."""
        self.__parent_network.get_load_status()
        return self._lists

    @property
    def conlists(self) -> list[NexusConList]:
        """Returns list of all conList objects."""
        self.__parent_network.get_load_status()
        return self._lists

    @staticmethod
    def table_header() -> Literal['CONLIST']:
        """Start of the Node definition table."""
        return 'CONLIST'

    @staticmethod
    def table_footer() -> Literal['ENDCONLIST']:
        """End of the Node definition table."""
        return 'ENDCONLIST'

    @property
    def _network_element_name(self) -> Literal['conlists']:
        return 'conlists'

    def _add_to_memory(self, additional_list: None | Sequence[NetworkList]) -> None:
        """Extends the conlist stored in memory by a list of conlist provided to it."""
        if additional_list is None:
            return
        if not isinstance(additional_list, list):
            additional_list = list(additional_list)
        only_conlist = [x for x in additional_list if isinstance(x, NexusConList)]
        self._lists.extend(only_conlist)
