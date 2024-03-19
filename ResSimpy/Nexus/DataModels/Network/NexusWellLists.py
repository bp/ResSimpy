"""Contains a class for representing a set of WellList objects for the Nexus model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork

from ResSimpy.WellLists import WellLists


@dataclass(kw_only=True)
class NexusWellLists(WellLists):
    """Class for representing a set of WellList objects for the Nexus model."""
    __well_lists: list[NexusWellList] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusWellLists class.

        Args:
            parent_network (NexusNetwork): The network that the well lists are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self.__well_lists: list[NexusWellList] = []

    def get_all(self) -> list[NexusWellList]:
        """Returns all WellList names."""
        self.__parent_network.get_load_status()
        return self.__well_lists

    @property
    def welllists(self) -> list[NexusWellList]:
        """Returns all WellList names."""
        self.__parent_network.get_load_status()
        return self.__well_lists

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
        return [x for x in self.__well_lists if x.name == well_list_name]

    def _add_to_memory(self, additional_list: None | list[NexusWellList]) -> None:
        if additional_list is None:
            return
        only_welllist_objects = [x for x in additional_list if isinstance(x, NexusWellList)]
        self.__well_lists.extend(only_welllist_objects)
