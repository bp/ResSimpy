"""Contains a class for representing a set of NodeList objects for the Nexus model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Sequence

from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList
from ResSimpy.GenericContainerClasses.NetworkLists import NetworkLists
from ResSimpy.Nexus.DataModels.Network.NexusNodeList import NexusNodeList

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusNodeLists(NetworkLists):
    """Class for representing a set of NodeList objects for the Nexus model."""

    _lists: list[NexusNodeList] = field(default_factory=list)
    __parent_network: NexusNetwork

    def __init__(
        self,
        parent_network: NexusNetwork,
        node_lists: None | list[NexusNodeList] = None,
    ) -> None:
        """Initialises the NexusNodeLists class. Supports CLEAR, ADD and REMOVE operations on the NodeList.

        Args:
            parent_network (NexusNetwork): The network that the node lists are a part of.
            node_lists (list[NexusNodeList]): The list of node lists to be added to the NexusNodeLists object.
        """
        self._lists = node_lists if node_lists is not None else []
        self.__parent_network = parent_network
        super().__init__(parent_network=parent_network)

    def get_all(self) -> list[NexusNodeList]:
        """Returns all NodeList names."""
        self.__parent_network.get_load_status()
        return self._lists

    @property
    def nodelists(self) -> list[NexusNodeList]:
        """Returns list of all NodeList objects."""
        self.__parent_network.get_load_status()
        return self._lists

    @staticmethod
    def table_header() -> Literal["NODELIST"]:
        """Start of the Node definition table."""
        return "NODELIST"

    @staticmethod
    def table_footer() -> Literal["ENDNODELIST"]:
        """End of the Node definition table."""
        return "ENDNODELIST"

    @property
    def _network_element_name(self) -> Literal["nodelists"]:
        return "nodelists"

    def _add_to_memory(self, additional_list: None | Sequence[NetworkList]) -> None:
        """Extends the nodelist stored in memory by a list of nodelist provided to it."""
        if additional_list is None:
            return
        if not isinstance(additional_list, list):
            additional_list = list(additional_list)
        only_nodelist = [x for x in additional_list if isinstance(x, NexusNodeList)]
        self._lists.extend(only_nodelist)
