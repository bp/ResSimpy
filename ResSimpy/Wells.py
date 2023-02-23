from dataclasses import dataclass
from abc import ABC

import pandas as pd

from ResSimpy import Well


@dataclass(kw_only=True)
class Wells(ABC):
    def get_wells(self) -> list[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
