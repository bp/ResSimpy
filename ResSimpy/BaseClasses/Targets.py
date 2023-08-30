from dataclasses import dataclass, field
from abc import ABC
from typing import Literal

from ResSimpy.BaseClasses.Target import Target
from ResSimpy.BaseClasses.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class Targets(NetworkOperationsMixIn, ABC):
    __targets: list[Target] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['targets']:
        return 'targets'
