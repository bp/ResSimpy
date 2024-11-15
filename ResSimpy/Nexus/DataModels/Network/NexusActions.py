from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, TYPE_CHECKING

from ResSimpy.Nexus.DataModels.Network.NexusAction import NexusAction

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusActions:
    """A class representing a list of nexus action objects."""
    __actions: list[NexusAction] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusActions class.

        Args:
            parent_network (NexusNetwork): The network that the actions are a part of.
            actions (list[NexusAction]): A list of nexus action objects.
        """
        self.__parent_network: NexusNetwork = parent_network
        self.__actions = []

    def get_all(self) -> Sequence[NexusAction]:
        """Returns a list of actions loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__actions

    def _add_to_memory(self, actions_to_add: list[NexusAction]) -> None:
        """Adds the list of Nexus Action objects to memory."""
        self.__actions.extend(actions_to_add)
