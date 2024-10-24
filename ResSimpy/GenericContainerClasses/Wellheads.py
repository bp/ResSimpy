from abc import ABC
from dataclasses import dataclass, field
from typing import Literal, Sequence

from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.DataModelBaseClasses.Wellhead import Wellhead


@dataclass(kw_only=True)
class Wellheads(NetworkOperationsMixIn, ABC):
    _wellheads: Sequence[Wellhead] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['wellheads']:
        return 'wellheads'
