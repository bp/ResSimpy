from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC

import pandas as pd

from ResSimpy.Well import Well
from typing import Sequence, Optional


@dataclass(kw_only=True)
class Wells(ABC):
    __wells: list[Well] = field(default_factory=list)

    @property
    def wells(self):
        return self.__wells

    @wells.setter
    def wells(self, value):
        self.__wells = value

    def get_all(self) -> Sequence[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get(self, well_name: str) -> Optional[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
    
    def modify(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
    
    def add_completion(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    def remove_completion(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
    
    def modify_completion(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_header(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_footer(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
