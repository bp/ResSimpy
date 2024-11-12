from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, TYPE_CHECKING

from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusActivationChanges:
    """A class representing a list of nexus action objects."""
    __activationChanges: list[NexusActivationChange] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusProcs class.

        Args:
            parent_network (NexusNetwork): The network that the actions are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self.__activationChanges = []

    def get_all(self) -> Sequence[NexusActivationChange]:
        """Returns a list of actions loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__activationChanges

    def _add_to_memory(self, activations_to_add: list[NexusActivationChange]) -> None:
        """Adds the list of Nexus Action objects to memory."""
        self.__activationChanges.extend(activations_to_add)