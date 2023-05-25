from dataclasses import dataclass
from abc import ABC

import pandas as pd

from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Well import Well
from typing import Sequence, Optional, MutableMapping, Dict, Type


@dataclass(kw_only=True)
class Wells(ABC):
    def get_wells(self) -> Sequence[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get_well(self, well_name: str) -> Optional[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def test_property(self) -> Well:

        raise NotImplementedError("test")
