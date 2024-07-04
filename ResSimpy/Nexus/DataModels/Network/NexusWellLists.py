"""Contains a class for representing a set of WellList objects for the Nexus model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Sequence

from ResSimpy.NetworkList import NetworkList
from ResSimpy.NetworkLists import NetworkLists
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusWellLists(NetworkLists):
    """Class for representing a set of WellList objects for the Nexus model."""

    _lists: list[NexusWellList] = field(default_factory=list)
    __parent_network: NexusNetwork

    def __init__(self, parent_network: NexusNetwork, well_lists: None | list[NexusWellList] = None) -> None:
        """Initialises the NexusWellLists class.

        Args:
            parent_network (NexusNetwork): The network that the well lists are a part of.
            well_lists (list[NexusWellList]): The well lists found in the network.
        """
        self._lists = well_lists if well_lists is not None else []
        self.__parent_network = parent_network
        super().__init__(parent_network)

    @property
    def _network_element_name(self) -> Literal['welllists']:
        return 'welllists'

    def get_all(self) -> list[NexusWellList]:
        """Returns all WellList names."""
        self.__parent_network.get_load_status()
        return self._lists

    @property
    def welllists(self) -> list[NexusWellList]:
        """Returns list of all WellList objects."""
        self.__parent_network.get_load_status()
        return self._lists

    @property
    def table_header(self) -> str:
        """Start of the Node definition table."""
        return 'WELLLISTS'

    @property
    def table_footer(self) -> str:
        """End of the Node definition table."""
        return 'ENDWELLLISTS'

    def get_all_by_name(self, well_list_name: str) -> list[NexusWellList]:
        """Returns a list of WellLists which match the provided name loaded from the simulator.

        Args:
        ----
            well_list_name (str): name of the requested WellList

        Returns:
        -------
            list[NexusWellList]: the requested list of filtered welllists with the same name
        """
        self.__parent_network.get_load_status()
        return [x for x in self._lists if x.name == well_list_name]

    def _add_to_memory(self, additional_list: None | Sequence[NetworkList]) -> None:
        """Extends the welllists stored in memory by a list of welllist provided to it."""
        if additional_list is None:
            return
        only_welllist_objects = [x for x in additional_list if isinstance(x, NexusWellList)]
        self._lists.extend(only_welllist_objects)
