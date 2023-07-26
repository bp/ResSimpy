from abc import ABC
from dataclasses import dataclass, field
from typing import Literal

from ResSimpy.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.Wellhead import Wellhead


@dataclass(kw_only=True)
class Wellheads(NetworkOperationsMixIn, ABC):
    __wellheads: list[Wellhead] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['wellheads']:
        return 'wellheads'
