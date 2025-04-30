from abc import ABC
from dataclasses import dataclass, field
from typing import Literal, Sequence

from ResSimpy.DataModelBaseClasses.DrillSite import DrillSite
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn


@dataclass(kw_only=True)
class DrillSites(NetworkOperationsMixIn, ABC):
    _drillsites: Sequence[DrillSite] = field(default_factory=list)

    @property
    def _network_element_name(self) -> Literal['drill_sites']:
        return 'drill_sites'
