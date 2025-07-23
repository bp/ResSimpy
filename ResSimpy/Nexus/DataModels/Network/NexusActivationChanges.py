from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, TYPE_CHECKING, Optional

from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Time.ISODateTime import ISODateTime

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusActivationChanges:
    """A class representing a list of nexus action objects."""
    __activationChanges: list[NexusActivationChange] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusActivationChanges class.

        Args:
            parent_network (NexusNetwork): The network that the actions are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self.__activationChanges = []

    def get_all(self) -> Sequence[NexusActivationChange]:
        """Ensures the surface network file has been loaded."""
        self.__parent_network.get_load_status()
        return self.__activationChanges

    def _add_to_memory(self, activations_to_add: Optional[list[NexusActivationChange]]) -> None:
        """Adds the list of NexusActivationChange objects to memory."""
        if activations_to_add is None:
            return

        self.__activationChanges.extend(activations_to_add)

    def to_string_for_date(self, date: ISODateTime) -> str:
        """Outputs the activation changes for a specific date."""
        output_str = ''
        activations_for_date = [x for x in self.__activationChanges if x.iso_date == date and
                                x.change == ActivationChangeEnum.ACTIVATE]
        deactivations_for_date = [x for x in self.__activationChanges if x.iso_date == date and
                                  x.change == ActivationChangeEnum.DEACTIVATE]

        if activations_for_date:
            output_str += "ACTIVATE\nCONNECTION\n"
        for activation in activations_for_date:
            output_str += f"{activation.name}\n"
        if activations_for_date:
            output_str += "ENDACTIVATE\n"

        if deactivations_for_date:
            output_str += "DEACTIVATE\nCONNECTION\n"
        for deactivation in deactivations_for_date:
            output_str += f"{deactivation.name}\n"
        if deactivations_for_date:
            output_str += "ENDDEACTIVATE\n"

        return output_str
