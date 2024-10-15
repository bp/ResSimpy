"""Abstract base class for holding the well connections data for holding all components of the production networks."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Literal, Optional, TYPE_CHECKING, Sequence

from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.DataModelBaseClasses.WellConnection import WellConnection
if TYPE_CHECKING:
    from ResSimpy.DataModelBaseClasses.Network import Network


@dataclass(kw_only=True)
class WellConnections(NetworkOperationsMixIn, ABC):
    """Abstract base class for holding the well connections data for holding all components of the production
    networks.
    """
    _well_connections: Sequence[WellConnection] = field(default_factory=list)

    def __init__(self, parent_network: Network) -> None:
        """Abstract base class for holding the well connections data for holding all components of the \
        production networks.

        Args:
            parent_network (Network): The parent network object that the well connections belong to.
        """
        super().__init__(parent_network)
        self.__parent_network: Network = parent_network
        self._well_connections = []

    @property
    def _network_element_name(self) -> Literal['well_connections']:
        return 'well_connections'

    def _add_to_memory(self, additional_list: Optional[list[WellConnection]]) -> None:
        """Extends the nodes object by a list of connections provided to it.

        Args:
            additional_list (Sequence[NexusWellConnection]): list of nexus connections to add to the nodes list.
        """
        if additional_list is None:
            return
        if not isinstance(additional_list, list):
            additional_list = list(additional_list)
        if not isinstance(self._well_connections, list):
            self._well_connections = list(self._well_connections)

        self._well_connections.extend(additional_list)
