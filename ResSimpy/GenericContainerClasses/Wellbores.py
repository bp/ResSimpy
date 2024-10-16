from abc import ABC
from dataclasses import dataclass, field
from typing import Literal
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.DataModelBaseClasses.Wellbore import Wellbore


@dataclass(kw_only=True, repr=False)
class Wellbores(NetworkOperationsMixIn, ABC):
    __connections: list[Wellbore] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['wellbores']:
        return 'wellbores'
