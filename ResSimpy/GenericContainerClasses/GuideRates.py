from abc import ABC
from dataclasses import dataclass, field
from typing import Literal, Sequence

from ResSimpy.DataModelBaseClasses.GuideRate import GuideRate
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class GuideRates(NetworkOperationsMixIn, ABC):
    _guide_rates: Sequence[GuideRate] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['guide_rates']:
        return 'guide_rates'
