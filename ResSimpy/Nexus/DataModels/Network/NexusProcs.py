from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, TYPE_CHECKING

from ResSimpy.Nexus.DataModels.Network.NexusProc import NexusProc

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusProcs:
    """Class for handling procedures in the Nexus Network.

    This class is used to store and collect information about certain procedures written in the Nexus surface file.
    """
    # need field function to make a new unique empty list
    __procs: list[NexusProc] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusProcs class.

        Args:
            parent_network (NexusNetwork): The network that the procedures are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self.__procs = []

    def get_all(self) -> Sequence[NexusProc]:
        """Returns a list of procs loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__procs

    def _add_to_memory(self, procs_to_add: list[NexusProc]) -> None:
        """Adds the list of Nexus procedure objects to memory."""
        self.__procs.extend(procs_to_add)
