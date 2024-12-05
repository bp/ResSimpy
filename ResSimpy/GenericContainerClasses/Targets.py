from dataclasses import dataclass, field
from abc import ABC
from typing import Literal, Sequence

from ResSimpy.DataModelBaseClasses.Target import Target
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class Targets(NetworkOperationsMixIn, ABC):
    _targets: Sequence[Target] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['targets']:
        return 'targets'
