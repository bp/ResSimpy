from dataclasses import dataclass
from abc import ABC

import pandas as pd

from ResSimpy.Well import Well
from typing import Sequence, Optional


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
