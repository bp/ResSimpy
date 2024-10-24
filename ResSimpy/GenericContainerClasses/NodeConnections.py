from abc import ABC
from dataclasses import dataclass, field
from typing import Literal, Sequence

from ResSimpy.DataModelBaseClasses.NodeConnection import NodeConnection
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class NodeConnections(NetworkOperationsMixIn, ABC):
    _connections: Sequence[NodeConnection] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['connections']:
        return 'connections'
