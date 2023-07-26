from abc import ABC
from dataclasses import field
from typing import Literal

from ResSimpy.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.WellConnection import WellConnection


class WellConnections(NetworkOperationsMixIn, ABC):
    __well_connections: list[WellConnection] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['well_connections']:
        return 'well_connections'
