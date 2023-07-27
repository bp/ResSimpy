from dataclasses import dataclass, field
from abc import ABC
from typing import Literal

from ResSimpy.Node import Node
from ResSimpy.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class Nodes(NetworkOperationsMixIn, ABC):
    __nodes: list[Node] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['nodes']:
        return 'nodes'
