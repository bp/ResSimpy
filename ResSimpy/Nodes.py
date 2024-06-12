from dataclasses import dataclass, field
from abc import ABC
from typing import Literal, Sequence

from ResSimpy.Node import Node
from ResSimpy.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class Nodes(NetworkOperationsMixIn, ABC):
    _nodes: Sequence[Node] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['nodes']:
        return 'nodes'
