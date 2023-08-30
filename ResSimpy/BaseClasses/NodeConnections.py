from abc import ABC
from dataclasses import dataclass, field
from typing import Literal

from ResSimpy.BaseClasses.NodeConnection import NodeConnection
from ResSimpy.BaseClasses.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class NodeConnections(NetworkOperationsMixIn, ABC):
    __connections: list[NodeConnection] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['connections']:
        return 'connections'
