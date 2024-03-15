from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Literal, Optional, TYPE_CHECKING

from ResSimpy.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.WellConnection import WellConnection
if TYPE_CHECKING:
    from ResSimpy.Network import Network


@dataclass(kw_only=True)
class WellConnections(NetworkOperationsMixIn, ABC):
    _well_connections: list[WellConnection]

    def __init__(self, parent_network: Network, well_connections: Optional[list[WellConnection]] = None) -> None:
        super().__init__(parent_network)
        self.__parent_network: Network = parent_network
        self._well_connections: list[WellConnection] = well_connections if well_connections is not None else []

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
        self._well_connections.extend(additional_list)
